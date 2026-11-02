import os
import urllib3
import json
from flask import Flask, render_template, jsonify

# Deshabilitar advertencias de certificados auto-firmados de OCP
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# Configuración vía variables de entorno
OCP_API_URL = os.getenv("OCP_API_URL", "https://openshift.default.svc:443")
OCP_TOKEN_FILE = os.getenv("OCP_TOKEN_FILE", "/var/run/secrets/kubernetes.io/serviceaccount/token")
OCP_TOKEN = os.getenv("OCP_TOKEN", "")

def get_token():
    if OCP_TOKEN:
        return OCP_TOKEN
    if os.path.exists(OCP_TOKEN_FILE):
        with open(OCP_TOKEN_FILE, "r") as f:
            return f.read().strip()
    return ""

def fetch_nodes():
    token = get_token()
    if not token:
        return None, "No se encontró un Token de autenticación de OpenShift."

    http = urllib3.PoolManager(cert_reqs="CERT_NONE")
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    try:
        url = f"{OCP_API_URL.rstrip('/')}/api/v1/nodes"
        resp = http.request("GET", url, headers=headers, timeout=5.0)
        
        if resp.status != 200:
            return None, f"Error API OCP HTTP {resp.status}: {resp.data.decode('utf-8')}"
        
        return json.loads(resp.data.decode("utf-8")), None
    except Exception as e:
        return None, f"Error de conexión con OCP: {str(e)}"

def process_node_data(ocp_data):
    nodes_summary = []
    total_nodes = 0
    ready_nodes = 0

    items = ocp_data.get("items", [])
    total_nodes = len(items)

    for item in items:
        name = item.get("metadata", {}).get("name", "Unknown")
        labels = item.get("metadata", {}).get("labels", {})
        
        # Determinar rol del nodo (Master / Infra / Worker)
        role = "Worker"
        if labels.get("node-role.kubernetes.io/master") == "true" or labels.get("role") == "master":
            role = "Master"
        elif labels.get("node-role.kubernetes.io/infra") == "true" or labels.get("role") == "infra":
            role = "Infra"

        conditions = item.get("status", {}).get("conditions", [])
        is_ready = False
        unschedulable = item.get("spec", {}).get("unschedulable", False)
        
        issues = []
        for cond in conditions:
            c_type = cond.get("type")
            c_status = cond.get("status")

            if c_type == "Ready" and c_status == "True":
                is_ready = True
            elif c_type != "Ready" and c_status == "True":
                issues.append(c_type)

        if is_ready:
            ready_nodes += 1

        nodes_summary.append({
            "name": name,
            "role": role,
            "status": "Ready" if is_ready else "NotReady",
            "unschedulable": unschedulable,
            "issues": issues,
            "kubelet_version": item.get("status", {}).get("nodeInfo", {}).get("kubeletVersion", "N/A"),
            "os": item.get("status", {}).get("nodeInfo", {}).get("osImage", "N/A")
        })

    cluster_status = "HEALTHY"
    if ready_nodes == 0 and total_nodes > 0:
        cluster_status = "CRITICAL"
    elif ready_nodes < total_nodes:
        cluster_status = "WARNING"

    return {
        "cluster_status": cluster_status,
        "total_nodes": total_nodes,
        "ready_nodes": ready_nodes,
        "nodes": nodes_summary
    }

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/status")
def api_status():
    raw_data, error = fetch_nodes()
    if error:
        return jsonify({"error": error, "cluster_status": "UNKNOWN"}), 500
    
    summary = process_node_data(raw_data)
    return jsonify(summary)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
