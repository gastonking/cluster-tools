# Dashboard TUI en Python para OpenShift, Zabbix, Clima y Dólar

Esta interfaz interactiva basada en terminal (TUI) utiliza Python y la librería `curses` para organizar la información en una cuadrícula de 4 secciones:
1. **Clima y Dólar**: Consulta el clima actual en Argentina y cotizaciones de divisas.
2. **Nodos OpenShift**: Monitoreo directo del estado de los nodos del clúster OCP vía API HTTP (refrescado automático cada 10 minutos).
3. **Alertas Zabbix**: Integración con la API JSON-RPC de Zabbix para extraer problemas y triggers activos en tiempo real.
4. **Controles**: Temporizador de actualización y opciones de control (`r` para actualizar manual, `q` para salir).

## Requisitos
- Python 3
- Librería `requests`:
  ```bash
  pip install requests
  ```
*(Nota: En sistemas Linux/macOS `curses` viene integrado de forma nativa).*

## Ejecución
```bash
python dashboard.py
```
