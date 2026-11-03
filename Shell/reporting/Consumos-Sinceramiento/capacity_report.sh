#!/bin/bash
echo "=========================================================="
echo "   REPORTE DE CAPACIDAD Y SOBRECOMPROMISO - OPENSHIFT"
echo "   Generado el: $(date)"
echo "=========================================================="

echo -e "\n1. ESTADO FÍSICO DE LOS NODOS (Uso Real de RAM)"
echo "----------------------------------------------------------"
oc adm top nodes | grep -v "NAME" | awk '$5+0 > 85 {print $1 " está al " $5 " de uso REAL (CRÍTICO)"}'
oc adm top nodes

echo -e "\n2. ANÁLISIS DE SOBRECOMPROMISO (Limits vs Capacity)"
echo "----------------------------------------------------------"
echo -e "NODE_NAME\t\t\tLIMITS_MEM%\tREQUESTS_MEM%"
for node in $(oc get nodes -l node-role.kubernetes.io/worker --no-headers | awk '{print $1}'); do
    limits=$(oc describe node $node | grep "memory" | grep "%" | awk 'NR==2 {print $4}')
    requests=$(oc describe node $node | grep "memory" | grep "%" | awk 'NR==1 {print $4}')
    echo -e "$node\t$limits\t\t$requests"
done

echo -e "\n3. TOP 10 OFFENDERS (Pods con mayor consumo real)"
echo "----------------------------------------------------------"
oc adm top pods -A --sort-by=memory | head -n 11

echo -e "\n4. BRECHA DE VISIBILIDAD (Uso Real vs Requests)"
echo "----------------------------------------------------------"
echo -e "NAMESPACE\tPOD_NAME\t\tUSAGE\tREQUEST"
oc adm top pods -A --no-headers --sort-by=memory | head -n 10 | while read line; do
    ns=$(echo $line | awk '{print $1}')
    name=$(echo $line | awk '{print $2}')
    usage=$(echo $line | awk '{print $4}')
    req=$(oc get pod $name -n $ns -o jsonpath='{.spec.containers[*].resources.requests.memory}' 2>/dev/null)
    if [ -z "$req" ]; then req="<none>"; fi
    echo -e "$ns\t$name\t$usage\t$req"
done | column -t

echo -e "\n=========================================================="
echo "RESUMEN PARA EL MAIL:"
echo "----------------------------------------------------------"
echo "- Si LIMITS_MEM% supera el 300%, el riesgo de caída es inminente."
echo "- Si USAGE es mucho mayor que REQUEST, el Scheduler está ciego."
echo "- Se requiere 1 Nodo Worker adicional para absorber el desvío."
echo "=========================================================="
