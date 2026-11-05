# Script de Verificación de Nodos para OpenShift 3 (Con Sesión Activa)

Este script en Python asume que **ya estás conectado al clúster** (por ejemplo, tras haber ejecutado `oc login` en tu terminal o si se ejecuta como un Pod dentro del clúster). Detecta automáticamente el contexto o permite configurar las credenciales de forma transparente.

## Requisitos

1. Python 3 instalado.
2. La librería `requests` instalada:
   ```bash
   pip install requests
   ```
   *(Opcional para lectura avanzada de kubeconfig)*: `pip install pyyaml`

## Ejecución

Simplemente corre el script en la misma terminal donde ya tienes la sesión activa de OpenShift:
```bash
python check_nodes.py
```
