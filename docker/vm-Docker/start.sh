#!/bin/bash

# Iniciar VNC
su - usuario -c "vncserver :1 -geometry 1280x800"

# Iniciar noVNC
websockify --web=/usr/share/novnc/ 6080 localhost:5901
