# Contenedor Linux Headless con GUI, VNC y Web Browser (Firefox)

Esta solución permite ejecutar una aplicación gráfica (GUI), en este caso **Firefox**, dentro de un contenedor Docker Linux sin necesidad de un monitor físico ni servidor X11 local. Expone la interfaz visual del navegador directamente a través de un navegador web mediante **noVNC** (HTML5 + WebSockets).

---

## 🎯 ¿Para qué sirve?

1. **Firefox GUI en Navegador Web:** Permite acceder a una instancia completa de Firefox corriendo en el contenedor simplemente abriendo un puerto en el navegador local (`http://localhost:6080`).
2. **Entornos Headless / Automatización:** Ideal para pruebas de automatización web (Selenium/Playwright/Puppeteer), herramientas de scraping visual, o acceso remoto seguro en entornos donde no hay pantalla física.
3. **Imágenes Docker Livianas:** Construido sobre Debian Slim sin la sobrecarga de un entorno de escritorio pesado (Gnome/KDE).

---

## 🏗️ Arquitectura y Flujo de Funcionamiento

El tráfico visual y de interacción fluye a través de los siguientes componentes acoplados:

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
       [ Firefox ]           <-- Aplicación GUI objetivo
```

---

## 🛠️ Análisis Detallado de los Archivos

### 1. `Dockerfile`
Define cómo se construye la imagen del contenedor paso a paso.

```dockerfile
FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV DISPLAY=:1
ENV USER=appuser
ENV HOME=/home/appuser

# 1. Instalar dependencias necesarias (Xvfb, Fluxbox, VNC, noVNC, Supervisor)
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

# 2. Descargar e instalar Firefox Oficial de 64 bits
RUN wget -O /tmp/firefox.tar.xz \
    "https://download.mozilla.org/?product=firefox-latest&os=linux64&lang=en-US" \
    && tar -xJf /tmp/firefox.tar.xz -C /opt/ \
    && ln -s /opt/firefox/firefox /usr/local/bin/firefox \
    && rm /tmp/firefox.tar.xz

# 3. Crear usuario sin privilegios de root para ejecutar las apps
RUN useradd -m -s /bin/bash $USER

# 4. Copiar la configuración del gestor de procesos
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Exponer el puerto de noVNC
EXPOSE 6080

# Iniciar Supervisor como proceso principal (PID 1)
CMD ["/usr/bin/supervisord"]
```

#### Componentes clave del Dockerfile:
* **`Xvfb` (X Virtual Framebuffer):** Servidor gráfico en memoria que simula la pantalla sin requerir hardware de video.
* **`Fluxbox`:** Gestor de ventanas ultraliviano para manejar bordes, dimensiones y posicionamiento de Firefox.
* **`x11vnc`:** Servidor VNC que lee el display virtual de Xvfb (`:1`).
* **`novnc` + `websockify`:** Traduce las conexiones VNC nativas a protocolo WebSocket para ser consumidas por cualquier navegador sin plugins.
* **`supervisord`:** Orquestador de procesos dentro del contenedor (mantiene vivos todos los servicios simultáneamente).

---

### 2. `supervisord.conf`
Configura los 5 procesos que deben ejecutarse en paralelo dentro del contenedor para que la interfaz funcione.

```ini
[supervisord]
nodaemon=true

# 1. Pantalla Virtual (Resolución 1280x800, 24 bits de color)
[program:xvfb]
command=/usr/bin/Xvfb :1 -screen 0 1280x800x24
autorestart=true

# 2. Gestor de Ventanas (Window Manager)
[program:fluxbox]
command=/usr/bin/fluxbox
environment=DISPLAY=":1"
autorestart=true

# 3. Servidor VNC (Sin contraseña, persistente)
[program:x11vnc]
command=/usr/bin/x11vnc -display :1 -forever -nopw -shared
autorestart=true

# 4. Servidor Web / WebSockets para noVNC en puerto 6080
[program:novnc]
command=/usr/bin/websockify --web=/usr/share/novnc/ 6080 localhost:5900
autorestart=true

# 5. Aplicación Gráfica (Firefox ejecutado como appuser)
[program:firefox]
command=/usr/local/bin/firefox --no-sandbox --disable-gpu
user=appuser
environment=DISPLAY=":1",HOME="/home/appuser"
autorestart=true
```

---

## 🚀 Guía de Despliegue y Uso

### 1. Construir la imagen de Docker
```bash
docker build -t debian-firefox-novnc .
```

### 2. Ejecutar el contenedor
```bash
docker run -d \
  --name firefox-browser \
  -p 6080:6080 \
  debian-firefox-novnc
```

### 3. Acceder desde el navegador
Abrí tu navegador web e ingresá a:
```text
http://localhost:6080/vnc.html
```
Verás la ventana de Firefox ejecutándose dentro de la interfaz noVNC en tu pantalla.

---

## 💡 Alternativa con Script de Entrada (Entrypoint)
En el fragmento original tenías un script Bash equivalente:
```bash
#!/bin/bash
# Iniciar VNC
su - usuario -c "vncserver :1 -geometry 1280x800"

# Iniciar noVNC
websockify --web=/usr/share/novnc/ 6080 localhost:5901
```
*Nota: Se recomienda utilizar el enfoque de `supervisord.conf` sobre el script Bash para entornos productivos, ya que Supervisor gestiona mejor la caída o reinicio de subprocesos individuales (como Firefox o el Xvfb).*