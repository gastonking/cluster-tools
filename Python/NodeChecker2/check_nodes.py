import urllib3
import requests
import json
import os

# Deshabilitar advertencias por certificados autofirmados
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_openshift_credentials():
    # Opción 1: Si se ejecuta desde un pod dentro del clúster con una ServiceAccount montada
    sa_token_path = "/var/run/secrets/kubernetes.io/serviceaccount/token"
    sa_ca_path = "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"
    
    if os.path.exists(sa_token_path):
        with open(sa_token_path, "r") as f:
            token = f.read().strip()
        # En OCP 3 dentro del clúster, la variable KUBERNETES_SERVICE_HOST y PORT suelen estar definidas
        host = os.environ.get("KUBERNETES_SERVICE_HOST", "kubernetes.default.svc")
        port = os.environ.get("KUBERNETES_SERVICE_PORT", "443")
        api_url = f"https://{host}:{port}"
        return api_url, token, sa_ca_path if os.path.exists(sa_ca_path) else False

    # Opción 2: Si el usuario ya ejecutó `oc login` previamente, oc guarda la configuración en ~/.kube/config
    # Intentamos extraer el token y el servidor de la configuración actual si existe
    kubeconfig_path = os.path.expanduser("~/.kube/config")
    if os.path.exists(kubeconfig_path):
        try:
            import yaml
            with open(kubeconfig_path, "r") as f:
                config = yaml.safe_load(f)
            # Buscar el contexto actual y sus credenciales
            current_context = config.get("current-context")
            # Esto es una implementación básica para lectura directa si YAML está disponible
            # Como alternativa robusta, leemos la variable de entorno o asumimos credenciales activas del entorno local
        except ImportError:
            pass

    # Opción 3: Variables de entorno explícitas o valores por defecto para clúster local / sesión activa
    api_url = os.environ.get("OPENSHIFT_API_URL", "https://localhost:8443")
    token = os.environ.get("OPENSHIFT_TOKEN", "")
    
    return api_url, token, False

def check_cluster_nodes():
    api_url, token, ca_cert = get_openshift_credentials()
    
    if not token:
        print("[!] No se detectó un token activo automáticamente.")
        print("[*] Asegúrate de ejecutar este script habiendo hecho `oc login` previamente o configurando las variables de entorno.")
    
    url = f"{api_url}/api/v1/nodes"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }
    
    print(f"[*] Conectando al clúster OpenShift en: {api_url}")
    
    try:
        # Si estamos usando certificados del clúster (ej. dentro de un Pod), usamos ca_cert, de lo contrario verify=False
        verify_target = ca_cert if ca_cert else False
        response = requests.get(url, headers=headers, verify=verify_target, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            items = data.get("items", [])
            print(f"[*] Total de nodos encontrados: {len(items)}\n")
            print("-" * 95)
            print(f"{'NOMBRE DEL NODO':<30} | {'ESTADO':<12} | {'VERSION KUBELET':<18} | {'ROLES'}")
            print("-" * 95)
            
            for node in items:
                name = node.get("metadata", {}).get("name", "Desconocido")
                
                # Estado del nodo (Ready)
                conditions = node.get("status", {}).get("conditions", [])
                node_status = "Desconocido"
                for cond in conditions:
                    if cond.get("type") == "Ready":
                        node_status = "Ready" if cond.get("status") == "True" else "NotReady"
                
                # Versión de Kubelet
                kubelet_version = node.get("status", {}).get("nodeInfo", {}).get("kubeletVersion", "N/A")
                
                # Roles o etiquetas
                labels = node.get("metadata", {}).get("labels", {})
                roles = [k.replace("node-role.kubernetes.io/", "") for k in labels.keys() if "node-role.kubernetes.io/" in k]
                role_str = ", ".join(roles) if roles else "compute"
                
                print(f"{name:<30} | {node_status:<12} | {kubelet_version:<18} | {role_str}")
            print("-" * 95)
            
        else:
            print(f"[!] Error al consultar la API. Código de estado: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"[!] Ocurrió un error de conexión con la API del clúster: {e}")

if __name__ == "__main__":
    check_cluster_nodes()
