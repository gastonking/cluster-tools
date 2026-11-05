# Script de Verificación de Nodos para OpenShift 3 (Sin ADM)

Este script en Python utiliza peticiones HTTP directas (vía la librería `requests`) para conectarse a la API de OpenShift 3 y consultar el estado de todos los nodos del clúster sin depender de herramientas de administración (`adm`).

## Requisitos

1. Python 3 instalado.
2. La librería `requests` instalada:
   ```bash
   pip install requests
   ```

## Configuración

1. Abre el archivo `check_nodes.py`.
2. Modifica la variable `OPENSHIFT_API_URL` con la URL de la API Master de tu clúster OCP 3.
3. Modifica la variable `TOKEN` con tu token de autenticación (puedes obtenerlo ejecutando `oc whoami -t`).

## Ejecución

Ejecuta el script desde tu terminal:
```bash
python check_nodes.py
```
