cat << 'EOF' > Reporte-Acaparadores.sh
#!/bin/bash
OUTPUT_FILE="Reporte_Acaparadores_SRE.csv"

echo "Buscando aplicaciones con exceso de reserva... (Eficiencia de Costos)"

# 1. Capturamos datos masivos
oc adm top pods -A --no-headers > /tmp/top_pods.txt
oc get pods -A -o custom-columns=NS:.metadata.namespace,NAME:.metadata.name,REQ:.spec.containers[0].resources.requests.memory --no-headers > /tmp/req_pods.txt

# 2. Cabecera del reporte
echo "PROYECTO;APLICACION;RESERVA_MB;USO_REAL_MB;DESPERDICIO_MB;EFICIENCIA_%" > $OUTPUT_FILE

# 3. Procesamos Namespaces de usuario
grep -vE "^(openshift|kube|default|dynatrace|redhat|aws)" /tmp/top_pods.txt | while read -r line; do
    ns=$(echo "$line" | awk '{print $1}')
    name=$(echo "$line" | awk '{print $2}')
    usage_raw=$(echo "$line" | awk '{print $4}' | sed 's/[^0-9]//g')
    
    # Buscamos la reserva
    req_raw=$(grep -w "^$ns" /tmp/req_pods.txt | grep -w "$name" | awk '{print $3}' | sed 's/[^0-9]//g')

    if [ ! -z "$req_raw" ] && [ "$req_raw" -gt 0 ]; then
        # Solo reportamos si la reserva es mayor al uso real por más de 500MB
        if [ "$req_raw" -gt "$((usage_raw + 500))" ]; then
            desperdicio=$((req_raw - usage_raw))
            eficiencia=$(( (usage_raw * 100) / req_raw ))
            echo "$ns;$name;${req_raw}Mi;${usage_raw}Mi;${desperdicio}Mi;${eficiencia}%" >> $OUTPUT_FILE
        fi
    fi
done

echo "----------------------------------------------------------"
echo "✅ Reporte de Desperdicio generado: $OUTPUT_FILE"
echo "Ordena por la columna DESPERDICIO_MB para ver a los mayores."
echo "----------------------------------------------------------"

rm /tmp/top_pods.txt /tmp/req_pods.txt
EOF

chmod +x Reporte-Acaparadores.sh
./Reporte-Acaparadores.sh
