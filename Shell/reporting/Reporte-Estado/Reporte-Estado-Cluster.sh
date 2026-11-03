#!/bin/bash

# Detectar el cluster actual basándose en la sesión activa
CLUSTER_URL=$(oc whoami --show-server 2>/dev/null)
CLUSTER_NAME=$(echo "$CLUSTER_URL" | awk -F'//|:' '{print $3}' | sed 's/api.//')

# Si por alguna razón no se puede leer la URL, usa un nombre genérico
if [ -z "$CLUSTER_NAME" ]; then CLUSTER_NAME="openshift_cluster"; fi

OUTPUT_FILE="reporte_pods_${CLUSTER_NAME}_$(date +%Y%m%d_%H%M%S).txt"

echo "=========================================================================="
echo " GENERANDO REPORTE DE NAMESPACES Y PODS"
echo " Contexto actual: $CLUSTER_NAME"
echo " Guardando en:    $OUTPUT_FILE"
echo "=========================================================================="

# Inicializar archivo con el encabezado
{
    echo "=========================================================================="
    echo " REPORT OF NAMESPACES AND PODS - OPENSHIFT"
    echo " Cluster: $CLUSTER_NAME ($CLUSTER_URL)"
    echo " Date:    $(date '+%Y-%m-%d %H:%M:%S')"
    echo "=========================================================================="
    echo ""
} > "$OUTPUT_FILE"

# Obtener todos los namespaces/projects ordenados
NAMESPACES=$(oc get projects -o jsonpath='{.items[*].metadata.name}' | tr ' ' '\n' | sort)

TOTAL_NAMESPACES=0
TOTAL_PODS=0

for NS in $NAMESPACES; do
    # Sintaxis compatible con sh/bash para incremento
    TOTAL_NAMESPACES=$(expr $TOTAL_NAMESPACES + 1)
    
    # Extraer Pods en formato plano: Nombre | Estado | Restarts | Nodo
    POD_DATA=$(oc get pods -n "$NS" -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.phase}{"\t"}{.status.containerStatuses[0].restartCount}{"\t"}{.spec.nodeName}{"\n"}{end}' 2>/dev/null)
    
    if [ -z "$POD_DATA" ]; then
        POD_COUNT=0
    else
        POD_COUNT=$(echo "$POD_DATA" | wc -l)
    fi
    
    # Sintaxis compatible con sh/bash para suma
    TOTAL_PODS=$(expr $TOTAL_PODS + $POD_COUNT)
    
    # Escribir bloque del Namespace
    {
        echo "--------------------------------------------------------------------------"
        echo " NAMESPACE: $NS ($POD_COUNT Pods)"
        echo "--------------------------------------------------------------------------"
    } >> "$OUTPUT_FILE"
    
    # Si hay pods, formatearlos en columnas limpias
    if [ "$POD_COUNT" -gt 0 ]; then
        echo "$POD_DATA" | awk -F'\t' 'BEGIN {printf "%-65s %-15s %-10s %-25s\n", "POD NAME", "STATUS", "RESTARTS", "NODE"}
        {printf "%-65s %-15s %-10s %-25s\n", $1, $2, ($3==""?0:$3), ($4==""?"N/A":$4)}' >> "$OUTPUT_FILE"
    else
        echo "  No se encontraron Pods en este Namespace." >> "$OUTPUT_FILE"
    fi
    echo "" >> "$OUTPUT_FILE"
done

# Resumen al final del reporte
{
    echo "=========================================================================="
    echo " SUMMARY"
    echo "=========================================================================="
    echo " Total Namespaces procesados: $TOTAL_NAMESPACES"
    echo " Total Pods activos en el cluster: $TOTAL_PODS"
    echo "=========================================================================="
} >> "$OUTPUT_FILE"

echo "✅ Reporte generado exitosamente en: $OUTPUT_FILE"