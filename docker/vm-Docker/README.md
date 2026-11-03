# Firefox Headless + noVNC Container

Este proyecto levanta una instancia de Firefox en un entorno gráfico virtual dentro de Docker, accesible vía navegador web gracias a noVNC.

## Archivos incluidos

- `Dockerfile`: Definición de la imagen basada en Debian Slim con Xvfb, Fluxbox, x11vnc, noVNC y Firefox.
- `supervisord.conf`: Configuración de Supervisor para orquestar los 5 procesos requeridos.
- `docker-compose.yml`: Archivo de orquestación para desplegar el servicio de forma simple.

## Uso rápido

1. Descomprimir el archivo `.zip`:
   ```bash
   unzip firefox-novnc-docker.zip
   cd firefox-novnc-docker
   ```

2. Levantar los contenedores con Docker Compose:
   ```bash
   docker compose up -d --build
   ```

3. Abrir en el navegador:
   `http://localhost:6080/vnc.html`
