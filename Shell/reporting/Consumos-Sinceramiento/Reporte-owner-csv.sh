cat << 'EOF' > Generar-CSV-Owners.sh
#!/bin/bash
OUTPUT_FILE="Reporte_Owners_SRE.csv"

echo "Extrayendo datos masivos del cluster... (esto será rápido)"

# 1. Capturamos Uso Real y Reservas en archivos temporales para cruzar datos en memoria
oc adm top pods -A --no-headers > /tmp/top_pods.txt
oc get pods -A -o custom-columns=NS:.metadata.namespace,NAME:.metadata.name,REQ:.spec.containers[0].resources.requests.memory --no-headers > /tmp/req_pods.txt

# 2. Creamos la cabecera del CSV
echo "PROYECTO;APLICACION;USO_REAL_MB;RESERVA_MB;DESVIO_MB;ESTADO" > $OUTPUT_FILE

# 3. Procesamos solo Namespaces de usuario
grep -vE "^(openshift|kube|default|dynatrace|redhat|aws|palo-alto|splun)" /tmp/top_pods.txt | while read -r line; do
    ns=$(echo "$line" | awk '{print $1}')
    name=$(echo "$line" | awk '{print $2}')
    usage_raw=$(echo "$line" | awk '{print $4}' | sed 's/[^0-9]//g')
    
    # Buscamos la reserva configurada
    req_raw=$(grep -w "^$ns" /tmp/req_pods.txt | grep -w "$name" | awk '{print $3}' | sed 's/[^0-9]//g')

    # Lógica de comparación
    if [ -z "$req_raw" ] || [ "$req_raw" -eq 0 ]; then
        echo "$ns;$name;$usage_raw;0;$usage_raw;SIN_RESERVA_CRITICO" >> $OUTPUT_FILE
    else
        diff=$((usage_raw - req_raw))
        if [ "$diff" -gt 150 ]; then
            echo "$ns;$name;$usage_raw;$req_raw;$diff;DESVIO_DETECTADO" >> $OUTPUT_FILE
        fi
    fi
done

echo "----------------------------------------------------------"
echo "✅ Reporte generado exitosamente: $OUTPUT_FILE"
echo "Ya puedes abrirlo con Excel o enviarlo por mail."
echo "----------------------------------------------------------"

# Limpieza de temporales
rm /tmp/top_pods.txt /tmp/req_pods.txt
EOF

chmod +x Generar-CSV-Owners.sh
./Generar-CSV-Owners.sh
