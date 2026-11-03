#!/bin/bash
echo -e "PROYECTO\tAPLICACIÓN\tUSO_REAL\tRESERVA(Req)\tESTADO"
echo "--------------------------------------------------------------------------------"
oc adm top pods -A --no-headers | grep -vE "^(openshift|kube|default|dynatrace|redhat|aws)" | while read -r line; do
    ns=$(echo "$line" | awk '{print $1}')
    name=$(echo "$line" | awk '{print $2}')
    usage_raw=$(echo "$line" | awk '{print $4}' | sed 's/[^0-9]//g')
    
    # Obtenemos la Request de memoria y limpiamos para que sea solo número
    req_raw=$(oc get pod "$name" -n "$ns" -o jsonpath='{.spec.containers[0].resources.requests.memory}' 2>/dev/null | sed 's/[^0-9]//g')
    
    # Si no tiene reserva
    if [ -z "$req_raw" ]; then
        echo -e "$ns\t$name\t${usage_raw}Mi\t<none>\t🔴 SIN_RESERVA"
    else
        # Si el uso real supera la reserva por más de 200MB
        if [ "$usage_raw" -gt "$((req_raw + 200))" ]; then
            echo -e "$ns\t$name\t${usage_raw}Mi\t${req_raw}Mi\t⚠️  DESVÍO_ALTO"
        fi
    fi
done | column -t
