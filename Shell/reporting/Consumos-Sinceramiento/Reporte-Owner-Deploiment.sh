cat << 'EOF' > Auditoria-Owners-Limpio.sh
#!/bin/bash
OUTPUT_FILE="Auditoria_Solo_Owners.csv"

echo "Filtrando Deployments de aplicaciones de usuario... (Excluyendo Infraestructura)"

# Cabecera del CSV
echo "PROYECTO;DEPLOYMENT;RESERVA_MEM_CONFIG;LIMITE_MEM_CONFIG;ESTADO_CRITICIDAD" > $OUTPUT_FILE

# Lista de exclusión: openshift, kube, harbor, dynatrace, airflow, redhat, aws, default
FILTER="openshift\|kube\|harbor\|dynatrace\|airflow\|redhat\|aws\|default\|palo-alto\|splunk"

# Obtenemos los datos
oc get deploy -A -o custom-columns=NS:.metadata.namespace,NAME:.metadata.name,REQ:.spec.template.spec.containers[0].resources.requests.memory,LIMIT:.spec.template.spec.containers[0].resources.limits.memory --no-headers | grep -v "$FILTER" | while read -r ns name req limit; do

    # Normalizamos el valor de <none>
    [ "$req" == "<none>" ] && req_status="SIN_RESERVA" || req_status="OK"
    [ "$limit" == "<none>" ] && limit_status="SIN_LIMITE" || limit_status="OK"

    # Clasificamos la gravedad
    if [ "$req_status" == "SIN_RESERVA" ]; then
        ESTADO="🔴 CRITICO (Invisible para el Cluster)"
    elif [ "$limit_status" == "SIN_LIMITE" ]; then
        ESTADO="⚠️ RIESGO (Puede saturar el Nodo)"
    else
        ESTADO="✅ CONFIGURADO"
    fi

    echo "$ns;$name;$req;$limit;$ESTADO" >> $OUTPUT_FILE
done

echo "----------------------------------------------------------"
echo "✅ Reporte filtrado generado: $OUTPUT_FILE"
echo "Proyectos incluidos: $(oc get ns --no-headers | grep -v "$FILTER" | wc -l) aplicaciones de negocio."
echo "----------------------------------------------------------"
EOF

chmod +x Auditoria-Owners-Limpio.sh
./Auditoria-Owners-Limpio.sh
