# OpenShift, Red Hat & Linux Automation Toolkit 🛠️🐧

Bienvenido a esta colección de utilidades, scripts y herramientas de automatización diseñadas para optimizar la administración de sistemas Linux/Unix y la gestión operativa de clústeres empresariales de **Red Hat OpenShift (OCP On-Premises y ROSA en AWS)**.

## 🎯 Objetivo del Repositorio

El propósito central de este proyecto es transformar operaciones complejas y tediosas en tareas simples, repetibles y altamente eficientes.

Basado en la filosofía **DevOps / SRE**, todo script y herramienta aquí presente busca:

* **Simplicidad Efectiva:** Lograr el resultado deseado con el menor overhead técnico posible.
* **Automatización como Estándar:** Diseñar soluciones listas para integrarse en pipelines o tareas programadas.
* **Visibilidad Operativa:** Facilitar el diagnóstico rápido, la auditoría de recursos y la toma de decisiones informadas sobre la infraestructura.

---

## 🧰 Tecnologías Principales

* **Red Hat OpenShift Container Platform (OCP)** & **ROSA (Red Hat OpenShift Service on AWS)**
* **Red Hat Enterprise Linux (RHEL)** & Entornos Unix/Linux
* **Bash Shell Scripting** & herramientas nativas (`jq`, `awk`, `sed`, `jsonpath`)
* **Kubernetes Orchestration & Management** (`oc` / `kubectl`)

---

## 📂 Colección de Scripts y Herramientas

### 🔹 Auditoría y Visibilidad de Clúster

1. **`Reporte-Rosa-ocp.sh` — Inventario de Namespaces y Pods**
   * **Propósito:** Genera un reporte jerárquico estructurado que detalla los Namespaces (Proyectos) y el estado, reinicios y ubicación de nodo de cada Pod.
   * **Uso típico:** Auditoría de densidad de Pods y análisis de salud rápida post-despliegue.

2. **`Reporte-Rapido.sh` / `Reporte-Owners-Final.sh` — Detección de Desvíos de Recursos**
   * **Propósito:** Filtra pods de infraestructura y detecta aplicaciones de usuarios sin reservas de memoria (`requests`) o con sobreconsumo crítico.
   * **Uso típico:** Identificación de riesgos de `OOMKilled` en tiempo real.

### 🔹 Optimización y Sinceramiento de Capacidad

3. **`Reporte-Sinceramiento.sh` — Right-Sizing de Recursos**
   * **Propósito:** Cruza métricas en tiempo real de consumo con definiciones estáticas para recomendar ajustes reales de memoria (+20% de margen).
   * **Salida:** `Plan_Normalizacion_Cluster.csv`

4. **`Generar-CSV-Owners.sh` / `Auditoria-Owners-Limpio.sh` — Reportes para Gestión**
   * **Propósito:** Exportación masiva de datos de consumo y criticidad de deployments en formato CSV para compartir con *Application Owners* o gerencias.

---

## 🚀 Guía Rápida de Uso

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/gastonking/cluster-tools.git
   cd cluster-tools
   ```

2. **Otorgar permisos de ejecución:**
   ```bash
   chmod +x *.sh
   ```

3. **Autenticarse en el clúster deseado e iniciar:**
   ```bash
   oc login --token=YOUR_TOKEN --server=https://api.your-cluster.com:6443
   ./Reporte-Rosa-ocp.sh
   ```

---

## 👨‍💻 Sobre el Autor

### **Jorge Gastón Rey**
*Especialista en Infraestructura Cloud, DevOps & SysOps*

Profesional orientado a la arquitectura, administración y optimización de plataformas de contenedores e infraestructura híbrida. Con foco continuo en la filosofía de **automatizar todo lo automatizable**, diseño e implemento soluciones escalables sobre ecosistemas Red Hat, OpenShift y AWS.

* 🌐 **GitHub:** [gastonking/cluster-tools](https://github.com/gastonking/cluster-tools.git)
* 💼 **LinkedIn:** [gastonrey79](https://www.linkedin.com/in/gastonrey79/)
* 📄 **Curriculum Vitae:** [Ver CV Completo](./CV_Jorge_Gaston_Rey.md)
* 💡 **Filosofía:** *"Si tenés que repetir un comando más de dos veces, automatizalo."*

---

## 📄 Licencia

Este proyecto está disponible bajo la licencia [MIT](LICENSE), lo que permite su libre uso, modificación y distribución en entornos profesionales y personales.