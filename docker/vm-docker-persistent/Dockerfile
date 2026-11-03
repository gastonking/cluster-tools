FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV DISPLAY=:1
ENV USER=appuser
ENV HOME=/home/appuser

# Instalar dependencias mínimas necesarias
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

# Descargar e instalar Firefox
RUN wget -O /tmp/firefox.tar.xz \
    "https://download.mozilla.org/?product=firefox-latest&os=linux64&lang=en-US" \
    && tar -xJf /tmp/firefox.tar.xz -C /opt/ \
    && ln -s /opt/firefox/firefox /usr/local/bin/firefox \
    && rm /tmp/firefox.tar.xz

# Crear usuario no-root appuser y asignar permisos
RUN useradd -m -s /bin/bash $USER \
    && mkdir -p /home/$USER/.vnc \
    && chown -R $USER:$USER /home/$USER

# Copiar la configuración del gestor de procesos
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 6080

CMD ["/usr/bin/supervisord"]
