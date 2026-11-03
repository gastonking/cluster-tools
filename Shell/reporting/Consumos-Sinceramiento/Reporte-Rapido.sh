#!/bin/bash
echo "Generando reporte de desvíos para aplicaciones de usuario... (Espere unos segundos)"
echo -e "PROYECTO\tAPLICACIÓN\tUSO_REAL\tRESERVA(Req)\tESTADO"
echo "--------------------------------------------------------------------------------"

# 1. Sacamos el uso real de una vez
oc adm top pods -A --no-headers > /tmp/usage_real.txt

# 2. Sacamos las reservaciones de una vez (esto ahorra tiempo)
oc get pods -A -o custom-columns=NS:.metadata.namespace,NAME:.metadata.name,REQ:.spec.containers[0].resources.requests.memory --no-headers > /tmp/reservas.txt

# 3. Cruzamos los datos en memoria
grep -vE "^(openshift|kube|default|dynatrace|redhat|aws)" /tmp/usage_real.txt | while read -r line; do
    ns=$(echo "$line" | awk '{print $1}')
    name=$(echo "$line" | awk '{print $2}')
    usage_raw=$(echo "$line" | awk '{print $4}' | sed 's/[^0-9]//g')
    
    # Buscamos la reserva en nuestro archivo temporal
    req_raw=$(grep "^$ns[[:space:]]*$name" /tmp/reservas.txt | awk '{print $3}' | sed 's/[^0-9]//g')

    if [ -z "$req_raw" ] || [ "$req_raw" -eq 0 ]; then
        echo -e "$ns\t$name\t${usage_raw}Mi\t<none>\t🔴 SIN_RESERVA"
    else
        # Si el uso real supera la reserva por más de 100MB (ajustado para detectar más rápido)
        if [ "$usage_raw" -gt "$((req_raw + 100))" ]; then
            echo -e "$ns\t$name\t${usage_raw}Mi\t${req_raw}Mi\t⚠️  DESVÍO"
        fi
    fi
done | column -t

# Limpieza
rm /tmp/usage_real.txt /tmp/usage_real.txt 2>/dev/null
