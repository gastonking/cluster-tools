#!/bin/bash

echo "========================================================="
echo "   REPORTE DE NODOS SATURADOS (>90% RAM) - SWISS MEDICAL"
echo "   Fecha: $(date)"
echo "========================================================="

# 1. Obtener nodos con uso de memoria > 90%
NODOS_SATURADOS=$(oc adm top nodes --no-headers | awk '{print $1 " " $5}' | sed 's/%//' | awk '$2 > 90 {print $1}')

if [ -z "$NODOS_SATURADOS" ]; then
    echo "✅ No hay nodos con uso de memoria superior al 90%."
    exit 0
fi

for NODO in $NODOS_SATURADOS; do
    USO=$(oc adm top nodes $NODO --no-headers | awk '{print $5}')
    echo -e "\n🔴 NODO CRÍTICO: $NODO (Uso: $USO)"
    echo "---------------------------------------------------------"
    echo -e "TOP 5 PODS DESALOJABLES (Candidatos a reubicación):"
    echo -e "NAMESPACE\t\tPOD\t\t\t\tCPU\tMEMORIA"
    
    # 2. Listar pods en ese nodo, filtrando componentes críticos de infraestructura
    # Excluimos namespaces de openshift y el daemonset de trendmicro (seguridad)
    for pod_info in $(oc get pods -A -o wide --no-headers | grep "$NODO" | grep -vE "openshift-|kube-|trendmicro" | awk '{print $1"/"$2}'); do
        ns=$(echo $pod_info | cut -d'/' -f1)
        name=$(echo $pod_info | cut -d'/' -f2)
        oc adm top pod $name -n $ns --no-headers 2>/dev/null
    done | sort -k3 -h -r | head -n 10 | awk '{printf "%-20s %-40s %-7s %-10s\n", $1, $2, $3, $4}'
    
    echo "---------------------------------------------------------"
done

echo -e "\n💡 Recomendación SRE: Para mover un pod, usa: 'oc delete pod <POD> -n <NAMESPACE>'"
echo "Si el nodo está acordonado, el pod se recreará en un nodo con menos carga."
