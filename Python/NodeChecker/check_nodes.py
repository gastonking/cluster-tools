import urllib3
import requests
import json

# Deshabilitar advertencias por certificados autofirmados (muy común en entornos OCP antiguos)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# CONFIGURACIÓN
# Reemplaza con la URL de la API Master de tu OpenShift 3 (ej. https://master.example.com:8443)
OPENSHIFT_API_URL = "https://<YOUR_OCP3_MASTER_IP_OR_DOMAIN>:8443"

# Token de autenticación Bearer (puedes obtenerlo ejecutando `oc whoami -t`)
TOKEN = "<YOUR_BEARER_TOKEN>"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/json"
}

def check_cluster_nodes():
    url = f"{OPENSHIFT_API_URL}/api/v1/nodes"
    print(f"[*] Conectando a OpenShift API en: {OPENSHIFT_API_URL}")
    
    try:
        response = requests.get(url, headers=headers, verify=False, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            items = data.get("items", [])
            print(f"[*] Total de nodos encontrados: {len(items)}\n")
            print("-" * 80)
            print(f"{'NOMBRE DEL NODO':<30} | {'ESTADO':<15} | {'ROLES / LABELS'}")
            print("-" * 80)
            
            for node in items:
                name = node.get("metadata", {}).get("name", "Desconocido")
                
                # Obtener el estado del nodo (Ready, NotReady, etc.)
                conditions = node.get("status", {}).get("conditions", [])
                node_status = "Desconocido"
                for cond in conditions:
                    if cond.get("type") == "Ready":
                        node_status = "Ready" if cond.get("status") == "True" else "NotReady"
                
                # Obtener roles o etiquetas de nodo
                labels = node.get("metadata", {}).get("labels", {})
                roles = [k.replace("node-role.kubernetes.io/", "") for k in labels.keys() if "node-role.kubernetes.io/" in k]
                role_str = ", ".join(roles) if roles else "worker/compute"
                
                print(f"{name:<30} | {node_status:<15} | {role_str}")
            print("-" * 80)
            
        else:
            print(f"[!] Error al consultar la API. Código de estado: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"[!] Ocurrió un error de conexión: {e}")

if __name__ == "__main__":
    check_cluster_nodes()
