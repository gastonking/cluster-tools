#!/bin/bash

REPORT_FILE="auditoria_recursos_$(date +%F).csv"

# Función para normalizar unidades a MB (Enteros)
to_mb() {
    val=$(echo "$1" | tr -d '"' | tr -d ' ' | tr -d 'm') # Limpiamos todo
    case "$val" in
        *Gi) echo "$val" | sed 's/Gi//' | awk '{print int($1 * 1024)}' ;;
        *G)  echo "$val" | sed 's/G//'  | awk '{print int($1 * 1024)}' ;;
        *Mi) echo "$val" | sed 's/Mi//' | awk '{print int($1)}' ;;
        *M)  echo "$val" | sed 's/M//'  | awk '{print int($1)}' ;;
        "null"|"") echo "0" ;;
        *)   # Si es solo número o algo raro, intentar extraer solo dígitos
             clean_val=$(echo "$val" | sed 's/[^0-9]//g')
             [ -z "$clean_val" ] && echo "0" || echo "$clean_val" ;;
    esac
}

echo "Namespace,Aplicacion,CPU_Req,CPU_Limit,CPU_Usage,MEM_Req,MEM_Limit,MEM_Usage,Analisis_SRE" > "$REPORT_FILE"

# Excluir namespaces de sistema
NAMESPACES=$(oc get ns -o jsonpath='{.items[*].metadata.name}' | tr ' ' '\n' | grep -vE "openshift|kube-|default|logging|monitoring")

for NS in $NAMESPACES; do
    echo "Analizando Namespace: $NS..."
    
    TOP_TMP="/tmp/top_${NS}.txt"
    oc adm top pods -n "$NS" --no-headers 2>/dev/null > "$TOP_TMP"

    oc get deployments -n "$NS" -o json | jq -r '.items[] | 
        .metadata.namespace as $ns | .metadata.name as $deploy | .spec.template.spec.containers[] | 
        [$ns, $deploy, .resources.requests.cpu, .resources.limits.cpu, .resources.requests.memory, .resources.limits.memory] | @csv' | while IFS=',' read -r r_ns r_deploy r_cpu_req r_cpu_lim r_mem_req r_mem_lim; do
        
        NS_CLEAN=$(echo "$r_ns" | tr -d '"')
        DEPLOY_CLEAN=$(echo "$r_deploy" | tr -d '"')
        
        # Obtener uso real (promedio) - Manejo de errores si awk falla
        USAGE_LINE=$(grep "$DEPLOY_CLEAN" "$TOP_TMP" | awk '{cpu+=$2; mem+=$3; n++} END {if (n>0) print int(cpu/n) "m," int(mem/n) "Mi"; else print "0m,0Mi"}')
        CPU_USE=$(echo "$USAGE_LINE" | cut -d',' -f1)
        MEM_USE=$(echo "$USAGE_LINE" | cut -d',' -f2)

        ANALISIS="✅ OK"
        
        # Sanitizamos los valores para la lógica matemática
        REQ_MB=$(to_mb "$r_mem_req")
        USE_MB=$(to_mb "$MEM_USE")

        # Lógica de Análisis
        if [ "$r_cpu_req" = "null" ] || [ "$r_mem_req" = "null" ] || [ "$r_cpu_req" = '""' ]; then
            ANALISIS="⚠️ SIN_CONFIGURACION"
        elif [ "$r_cpu_lim" = "null" ] || [ "$r_mem_lim" = "null" ]; then
            ANALISIS="⚠️ LIMITES_FALTANTES"
        elif [ "$REQ_MB" -gt 0 ] && [ "$USE_MB" -gt 0 ]; then
            # Solo si ambos son números válidos mayores a cero
            LIMIT_CHECK=$((REQ_MB / 4))
            if [ "$REQ_MB" -gt 500 ] && [ "$USE_MB" -lt "$LIMIT_CHECK" ]; then
                ANALISIS="💰 SOBREDIMENSIONADO (Uso < 25%)"
            fi
        fi

        echo "$NS_CLEAN,$DEPLOY_CLEAN,$r_cpu_req,$r_cpu_lim,$CPU_USE,$r_mem_req,$r_mem_lim,$MEM_USE,\"$ANALISIS\"" >> "$REPORT_FILE"
    done
    rm -f "$TOP_TMP"
done

echo "========================================================="
echo "✅ Reporte Finalizado: $REPORT_FILE"
echo "========================================================="