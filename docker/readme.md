# Documentación de Proyectos: Firefox Headless con noVNC en Docker

Este documento detalla la arquitectura, archivos de configuración y pasos de despliegue para dos variantes de contenedores Debian con entorno gráfico Headless (Xvfb + Fluxbox + x11vnc + noVNC) y Firefox.

---

## 🏗️ Arquitectura General

Ambos proyectos comparten la misma infraestructura básica de servicios orquestados por **Supervisor**:

```text
[ Usuario (Navegador Web) ]
           │ (Puerto 6080 - HTML5 / WebSockets)
           ▼
     [ websockify / noVNC ]  <-- Convierte WebSockets a VNC directo
           │ (Puerto 5900)
           ▼
       [ x11vnc ]            <-- Servidor VNC que captura el Display :1
           │
           ▼
     [ Xvfb + Fluxbox ]      <-- Framebuffer en memoria (Display :1) + Window Manager
           │
           ▼
       [ Firefox ]           <-- Aplicación GUI ejecutada por 'appuser'
```

---

## 📦 Proyecto 1: Firefox noVNC (Efímero / Estándar)

Ideal para pruebas temporales, automatización o entornos donde no se requiere guardar historial, cookies ni descargas entre reinicios del contenedor.

### 1. `Dockerfile`
```dockerfile
FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV DISPLAY=:1
ENV USER=appuser
ENV HOME=/home/appuser

# Instalar dependencias necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    xvfb \
    fluxbox \
    x11vnc \
    novnc \
    websockify \
    supervisor \
    ca-certificates \
    wget \
    xz-utils \
    libgtk-3-0 \
    libdbus-glib-1-2 \
    libasound2 \
    libx11-xcb1 \
    libxt6 \
    fonts-dejavu \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Descargar e instalar Firefox Oficial de 64 bits
RUN wget -O /tmp/firefox.tar.xz \
    "https://download.mozilla.org/?product=firefox-latest&os=linux64&lang=en-US" \
    && tar -xJf /tmp/firefox.tar.xz -C /opt/ \
    && ln -s /opt/firefox/firefox /usr/local/bin/firefox \
    && rm /tmp/firefox.tar.xz

# Crear usuario sin privilegios de root
RUN useradd -m -s /bin/bash $USER \
    && mkdir -p /home/$USER/.vnc \
    && chown -R $USER:$USER /home/$USER

# Copiar configuración de Supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 6080

CMD ["/usr/bin/supervisord"]
```

### 2. `supervisord.conf`
```ini
[supervisord]
nodaemon=true

[program:xvfb]
command=/usr/bin/Xvfb :1 -screen 0 1280x800x24
autorestart=true

[program:fluxbox]
command=/usr/bin/fluxbox
environment=DISPLAY=":1"
autorestart=true

[program:x11vnc]
command=/usr/bin/x11vnc -display :1 -forever -nopw -shared
autorestart=true

[program:novnc]
command=/usr/bin/websockify --web=/usr/share/novnc/ 6080 localhost:5900
autorestart=true

[program:firefox]
command=/usr/local/bin/firefox --no-sandbox --disable-gpu
user=appuser
environment=DISPLAY=":1",HOME="/home/appuser"
autorestart=true
```

### 3. `docker-compose.yml`
```yaml
version: '3.8'

services:
  firefox-headless:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: firefox-browser
    ports:
      - "6080:6080"
    shm_size: '2gb'
    restart: unless-stopped
    environment:
      - DISPLAY=:1
```

---

## 💾 Proyecto 2: Firefox noVNC con Persistencia de Datos

Diseñado para uso continuo donde se requiere conservar cookies, marcadores, extensiones e historial de navegación entre reinicios o reconstrucciones de contenedores.

> **Nota:** El `Dockerfile` y el `supervisord.conf` son idénticos al Proyecto 1. La diferencia clave reside en la orquestación de volúmenes en el archivo `docker-compose.yml`.

### `docker-compose.yml` (Con Volumen Nombrado)
```yaml
version: '3.8'

services:
  firefox-browser:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: firefox-browser-persistent
    ports:
      - "6080:6080"
    shm_size: '2gb'
    restart: unless-stopped
    environment:
      - DISPLAY=:1
    volumes:
      # Persistencia de datos del perfil del navegador
      - firefox_profile_data:/home/appuser/.mozilla

volumes:
  firefox_profile_data:
```

---

## 🚀 Guía de Despliegue y Uso

### Pasos para iniciar el servicio:
1. Asegúrate de tener instalados Docker y Docker Compose.
2. Coloca los archivos del proyecto elegido (`Dockerfile`, `supervisord.conf` y `docker-compose.yml`) en un mismo directorio.
3. Ejecuta el comando para construir y levantar el contenedor en segundo plano:
   ```bash
   docker compose up -d --build
   ```

### Acceso web:
Abre tu navegador e ingresa a la dirección:
```text
http://localhost:6080/vnc.html
```
Haz clic en **Connect** para visualizar la pantalla y comenzar a interactuar con Firefox.

---

## 🛠️ Comandos de Mantenimiento

* **Ver estado de los servicios:**
  ```bash
  docker compose ps
  ```
* **Ver logs en tiempo real:**
  ```bash
  docker compose logs -f
  ```
* **Detener el contenedor:**
  ```bash
  docker compose down
  ```
* **Eliminar el volumen de datos (para reiniciar la sesión desde cero en el Proyecto 2):**
  ```bash
  docker volume rm <nombre_del_directorio>_firefox_profile_data
  ```