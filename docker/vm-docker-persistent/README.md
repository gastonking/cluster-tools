# Firefox Headless + noVNC Container (con Persistencia)

Esta versión incluye persistencia de datos mediante volúmenes de Docker para conservar el perfil y las configuraciones de Firefox.

## Archivos incluidos

- `Dockerfile`: Definición de la imagen basada en Debian Slim.
- `supervisord.conf`: Gestión de los procesos Xvfb, Fluxbox, x11vnc, noVNC y Firefox.
- `docker-compose.yml`: Orquestación con volumen asignado para guardar el perfil de Firefox (`firefox_profile_data`).
- `README.md`: Guía rápida de uso.

## Uso rápido

1. Descomprimir el archivo `.zip`:
   ```bash
   unzip firefox-novnc-persistent.zip
   cd firefox-novnc-persistent
   ```

2. Levantar el contenedor con Docker Compose:
   ```bash
   docker compose up -d --build
   ```

3. Abrir en el navegador:
   `http://localhost:6080/vnc.html`
