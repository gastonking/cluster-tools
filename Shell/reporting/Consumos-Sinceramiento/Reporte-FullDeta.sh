#!/bin/bash

echo "=========================================================================================="
echo "   REPORTE DE CAPACIDAD Y MOVILIDAD DE PODS - SWISS MEDICAL GROUP"
echo "   Fecha: $(date)"
echo "=========================================================================================="

# 1. Identificar nodos con uso de memoria > 85% (Bajamos el umbral para mayor visibilidad)
NODOS_SATURADOS=$(oc adm top nodes --no-headers | awk '{print $1 " " $5}' | sed 's/%//' | awk '$2 > 85 {print $1}')

if [ -z "$NODOS_SATURADOS" ]; then
    echo "✅ OPERACIÓN NORMAL: No hay nodos con uso de memoria superior al 85%."
    exit 0
fi

for NODO in $NODOS_SATURADOS; do
    USO_MEM=$(oc adm top nodes "$NODO" --no-headers | awk '{print $5}')
    echo ""
    echo "🔴 NODO CRÍTICO: $NODO (Uso de RAM: $USO_MEM)"
    echo "------------------------------------------------------------------------------------------"
    printf "%-30s %-45s %-12s %-15s\n" "NAMESPACE" "POD" "MEMORIA" "MOVILIDAD"
    echo "------------------------------------------------------------------------------------------"

    # Capturamos los pods del nodo
    for pod_info in $(oc get pods -A -o wide --no-headers | grep "$NODO" | grep -vE "openshift-|kube-|trendmicro" | awk '{print $1"/"$2}'); do
        ns=$(echo "$pod_info" | cut -d'/' -f1)
        name=$(echo "$pod_info" | cut -d'/' -f2)

        # Captura robusta de memoria: buscamos el valor que termina en 'Mi' o 'Gi'
        metrics=$(oc adm top pod "$name" -n "$ns" --no-headers 2>/dev/null)
        [ -z "$metrics" ] && mem_usage="N/A" || mem_usage=$(echo "$metrics" | awk '{for(i=1;i<=NF;i++) if($i ~ /Mi|Gi/) print $i}')

        # Lógica de movilidad
        kind=$(oc get pod "$name" -n "$ns" -o jsonpath='{.metadata.ownerReferences[0].kind}' 2>/dev/null)
        node_sel=$(oc get pod "$name" -n "$ns" -o jsonpath='{.spec.nodeSelector}' 2>/dev/null)

        if [ "$kind" = "DaemonSet" ]; then
            movilidad="❌ FIJO (DS)"
        elif echo "$node_sel" | grep -qE "kubernetes.io/hostname|$NODO"; then
            movilidad="⚠️ ATADO (NodeSel)"
        else
            movilidad="✅ MOVIBLE"
        fi

        printf "%-30s %-45s %-12s %-15s\n" "$ns" "$name" "$mem_usage" "$movilidad"
    done | sort -k3 -h -r | head -n 12
    
    echo "------------------------------------------------------------------------------------------"
done

echo ""
echo "GLOSARIO PARA MONITOREO / OT:"
echo "✅ MOVIBLE:  Pod de aplicación (Deployment). Se puede mover a nodos con baja carga."
echo "❌ FIJO (DS): DaemonSet de sistema. No se moverá de este nodo."
echo "⚠️  ATADO:    Posee restricciones de afinidad en el YAML."
echo "=========================================================================================="
