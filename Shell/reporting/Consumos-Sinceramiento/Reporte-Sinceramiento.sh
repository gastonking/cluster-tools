#!/bin/bash
OUTPUT_FILE="Plan_Normalizacion_Cluster.csv"

echo "Cruzando datos de configuración vs. consumo real... (Espere unos segundos)"

# 1. Capturamos datos masivos
oc adm top pods -A --no-headers > /tmp/uso_real.txt
oc get deploy -A -o custom-columns=NS:.metadata.namespace,NAME:.metadata.name,REQ:.spec.template.spec.containers[0].resources.requests.memory,LIM:.spec.template.spec.containers[0].resources.limits.memory --no-headers > /tmp/config_static.txt

# 2. Cabecera del CSV
echo "PROYECTO;DEPLOYMENT;RESERVA_ACTUAL;LIMITE_ACTUAL;USO_REAL_AVG;RECOMENDACION_SRE" > $OUTPUT_FILE

# 3. Filtramos infraestructura y procesamos
FILTER="openshift\|kube\|harbor\|dynatrace\|airflow\|redhat\|aws\|palo-alto\|splunk"

grep -v "$FILTER" /tmp/config_static.txt | while read -r ns deploy req lim; do
    # Buscamos el uso real promedio de los pods de ese deployment
    usage_raw=$(grep "^$ns" /tmp/uso_real.txt | grep "$deploy" | awk '{sum+=$4} END {if (NR>0) print sum/NR; else print 0}' | sed 's/[^0-9]//g')
    
    if [ -z "$usage_raw" ] || [ "$usage_raw" -eq 0 ]; then usage_raw=0; fi

    # Lógica de Recomendación (Uso Real + 20% de margen de maniobra)
    if [ "$usage_raw" -gt 0 ]; then
        rec_val=$((usage_raw + (usage_raw * 20 / 100)))
        RECOMENDACION="${rec_val}Mi"
    else
        RECOMENDACION="Analizar (Pod detenido o sin métricas)"
    fi

    echo "$ns;$deploy;$req;$lim;${usage_raw}Mi;$RECOMENDACION" >> $OUTPUT_FILE
done

echo "----------------------------------------------------------"
echo "✅ Reporte de Sinceramiento generado: $OUTPUT_FILE"
echo "La columna RECOMENDACION es el valor que el Owner debe aplicar."
echo "----------------------------------------------------------"

rm /tmp/uso_real.txt /tmp/config_static.txt
