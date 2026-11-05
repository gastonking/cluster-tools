import os
import time
import json
import urllib3
import requests
import curses

# Deshabilitar advertencias de certificados autofirmados
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuración (puedes ajustar o usar variables de entorno)
OCP_API_URL = os.environ.get("OPENSHIFT_API_URL", "https://localhost:8443")
OCP_TOKEN = os.environ.get("OPENSHIFT_TOKEN", "")

ZABBIX_URL = os.environ.get("ZABBIX_URL", "http://tu-zabbix/api_jsonrpc.php")
ZABBIX_USER = os.environ.get("ZABBIX_USER", "Admin")
ZABBIX_PASS = os.environ.get("ZABBIX_PASS", "zabbix")

def fetch_weather():
    try:
        # Usamos wttr.in en formato texto plano y corto
        res = requests.get("https://wttr.in/BuenosAires?format=3", timeout=5)
        if res.status_code == 200:
            return res.text.strip()
    except Exception:
        pass
    return "Clima no disponible"

def fetch_dollar():
    try:
        # API pública de cotizaciones en Argentina
        res = requests.get("https://dolarapi.com/v1/dolares/blue", timeout=5)
        if res.status_code == 200:
            data = res.json()
            return f"Dolar Blue - Compra: ${data.get('compra')} | Venta: ${data.get('venta')}"
    except Exception:
        pass
    return "Cotización dólar no disponible"

def fetch_nodes():
    # Detectar token SA si corre dentro de OCP
    token = OCP_TOKEN
    api_url = OCP_API_URL
    sa_token_path = "/var/run/secrets/kubernetes.io/serviceaccount/token"
    if os.path.exists(sa_token_path):
        with open(sa_token_path, "r") as f:
            token = f.read().strip()
        host = os.environ.get("KUBERNETES_SERVICE_HOST", "kubernetes.default.svc")
        port = os.environ.get("KUBERNETES_SERVICE_PORT", "443")
        api_url = f"https://{host}:{port}"
    
    if not token:
        return ["Sin token o sesión OCP activa (configura OPENSHIFT_TOKEN)"]

    try:
        url = f"{api_url}/api/v1/nodes"
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
        # Si corre dentro de pod usar ca.crt, sino verify=False
        ca_path = "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"
        verify = ca_path if os.path.exists(ca_path) else False

        response = requests.get(url, headers=headers, verify=verify, timeout=5)
        if response.status_code == 200:
            items = response.json().get("items", [])
            node_lines = []
            for node in items:
                name = node.get("metadata", {}).get("name", "Desconocido")
                status = "Desconocido"
                for cond in node.get("status", {}).get("conditions", []):
                    if cond.get("type") == "Ready":
                        status = "Ready" if cond.get("status") == "True" else "NotReady"
                node_lines.append(f"{name[:25]:<25} -> {status}")
            return node_lines if node_lines else ["No se encontraron nodos"]
        else:
            return [f"Error API OCP: HTTP {response.status_code}"]
    except Exception as e:
        return [f"Error de conexión OCP: {str(e)[:30]}"]

def fetch_zabbix_alerts():
    # Consulta a la API JSON-RPC de Zabbix para obtener problemas activos (triggers en estado de alerta)
    try:
        payload = {
            "jsonrpc": "2.0",
            "method": "user.login",
            "params": {"user": ZABBIX_USER, "password": ZABBIX_PASS},
            "id": 1
        }
        res = requests.post(ZABBIX_URL, json=payload, timeout=3)
        auth_token = res.json().get("result")
        if not auth_token:
            return ["Zabbix: Error de autenticación"]

        trigger_payload = {
            "jsonrpc": "2.0",
            "method": "problem.get",
            "params": {
                "output": ["eventid", "objectid", "severity", "name", "clock"],
                "recent": "true",
                "sortfield": ["eventid"],
                "sortorder": "DESC",
                "limit": 5
            },
            "auth": auth_token,
            "id": 2
        }
        tr_res = requests.post(ZABBIX_URL, json=trigger_payload, timeout=3)
        problems = tr_res.json().get("result", [])
        
        if not problems:
            return ["No hay alertas activas en Zabbix."]
        
        alert_lines = []
        for p in problems:
            sev = p.get("severity", "0")
            name = p.get("name", "Alerta sin nombre")
            alert_lines.append(f"[Sev {sev}] {name[:35]}")
        return alert_lines
    except Exception:
        return ["Zabbix: No accesible / Sin configurar"]

def draw_box(stdscr, start_y, start_x, height, width, title):
    stdscr.attron(curses.color_pair(1))
    stdscr.border()
    # Dibujar caja manualmente o con box()
    for y in range(start_y, start_y + height):
        for x in range(start_x, start_x + width):
            try:
                if y == start_y or y == start_y + height - 1:
                    stdscr.addch(y, x, ord('-'))
                elif x == start_x or x == start_x + width - 1:
                    stdscr.addch(y, x, ord('|'))
            except curses.error:
                pass
    try:
        stdscr.addstr(start_y, start_x + 2, f" {title} ")
    except curses.error:
        pass
    stdscr.attroff(curses.color_pair(1))

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)  # No bloquear en getch()
    stdscr.timeout(1000)  # Refrescar cada 1 segundo el bucle para control de tiempo
    
    # Inicializar colores si están disponibles
    if curses.has_colors():
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)

    last_fetch_time = 0
    refresh_interval = 600  # 10 minutos (600 segundos)

    weather_data = "Cargando clima..."
    dollar_data = "Cargando dólar..."
    nodes_data = ["Cargando nodos..."]
    zabbix_data = ["Cargando alertas Zabbix..."]

    def update_data():
        nonlocal weather_data, dollar_data, nodes_data, zabbix_data
        weather_data = fetch_weather()
        dollar_data = fetch_dollar()
        nodes_data = fetch_nodes()
        zabbix_data = fetch_zabbix_alerts()

    # Carga inicial
    update_data()
    last_fetch_time = time.time()

    while True:
        current_time = time.time()
        if current_time - last_fetch_time > refresh_interval:
            update_data()
            last_fetch_time = current_time

        stdscr.clear()
        max_y, max_x = stdscr.getmaxyx()

        # Dimensiones de la cuadrícula (2x2)
        half_y = max_y // 2
        half_x = max_x // 2

        if max_y < 20 or max_x < 60:
            stdscr.addstr(0, 0, "Terminal muy pequeña. Amplía la ventana.")
            stdscr.refresh()
            key = stdscr.getch()
            if key == ord('q'):
                break
            continue

        # --- Cuadrante 1: Clima y Dólar (Superior Izquierda) ---
        draw_box(stdscr, 0, 0, half_y, half_x, "ECONOMÍA Y CLIMA")
        try:
            stdscr.addstr(2, 2, f"Clima (Arg): {weather_data[:half_x-6]}")
            stdscr.addstr(4, 2, f"Dólar: {dollar_data[:half_x-6]}")
        except curses.error:
            pass

        # --- Cuadrante 2: Estado de Nodos OCP (Superior Derecha) ---
        draw_box(stdscr, 0, half_x, half_y, max_x - half_x, "NODOS OPENSHIFT (OCP 3)")
        for idx, line in enumerate(nodes_data[:half_y-4]):
            try:
                stdscr.addstr(2 + idx, half_x + 2, line[:(max_x - half_x - 4)])
            except curses.error:
                pass

        # --- Cuadrante 3: Alertas de Zabbix (Inferior Izquierda) ---
        draw_box(stdscr, half_y, 0, max_y - half_y, half_x, "ALERTAS ZABBIX")
        for idx, line in enumerate(zabbix_data[:(max_y - half_y - 4)]):
            try:
                stdscr.addstr(half_y + 2, 2, line[:half_x-4])
            except curses.error:
                pass

        # --- Cuadrante 4: Estado del Sistema / Controles (Inferior Derecha) ---
        draw_box(stdscr, half_y, half_x, max_y - half_y, max_x - half_x, "ESTADO Y CONTROLES")
        try:
            next_refresh = int(refresh_interval - (current_time - last_fetch_time))
            stdscr.addstr(half_y + 2, half_x + 2, f"Próximo refresco automático: {next_refresh}s")
            stdscr.addstr(half_y + 4, half_x + 2, "Presiona 'r' para forzar actualización.")
            stdscr.addstr(half_y + 6, half_x + 2, "Presiona 'q' para salir.")
        except curses.error:
            pass

        stdscr.refresh()

        key = stdscr.getch()
        if key == ord('q'):
            break
        elif key == ord('r'):
            update_data()
            last_fetch_time = time.time()

if __name__ == "__main__":
    curses.wrapper(main)
