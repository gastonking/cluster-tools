# OpenShift & ROSA Operational Scripts 🚀

Este repositorio contiene una colección de scripts en Bash diseñados para la gestión, auditoría y optimización de recursos en clústeres de **Red Hat OpenShift (OCP On-Premises y ROSA en AWS)**.

Su objetivo es brindar visibilidad rápida a los equipos de **SRE, Infraestructura y Owners de Aplicaciones** sobre el estado de los recursos, la distribución de Pods y las desviaciones de consumo de memoria.

---

## 🛠️ Requisitos Previos

1. **OpenShift CLI (`oc`)** instalado.
2. Estar autenticado en el clúster deseado (`oc login`) antes de ejecutar cualquier script.
3. Permisos de lectura a nivel de clúster (por ejemplo, rol `cluster-reader` o `dedicated-admin`).

---

## 📂 Descripción de los Scripts

### 1. `Reporte-Rosa-ocp.sh` — Inventory of Namespaces & Pods
* **¿Qué hace?**: Genera un reporte ordenado en texto plano que enumera todos los Namespaces (Proyectos) del clúster y los Pods contenidos en cada uno.
* **Información que incluye**: Nombre del Pod, Estado (`STATUS`), Reintentos (`RESTARTS`) y el Nodo Worker en el que se ejecuta (`NODE`).
* **Casos de uso**: Auditorías de densidad, troubleshooting rápido y detección de pods en nodos específicos.
* **Uso**:
  ```bash
  bash Reporte-Rosa-ocp.sh
  ```

---

### 2. `Reporte-Sinceramiento.sh` — Capacidad & Right-Sizing
* **¿Qué hace?**: Compara la configuración estática de recursos (Requests y Limits de memoria) contra el consumo real en tiempo real de los Pods.
* **Salida**: Archivo `.csv` (`Plan_Normalizacion_Cluster.csv`).
* **Casos de uso**: Genera automáticamente una recomendación de ajuste de memoria (consumo real + 20% de margen) para enviar a los *Application Owners* y evitar desperdicio o sobre-asignación de recursos.
* **Uso**:
  ```bash
  ./Reporte-Sinceramiento.sh
  ```

---

### 3. `Reporte-Rapido.sh` / `Reporte-Owners-Final.sh` — Auditoría de Desvíos
* **¿Qué hace?**: Filtra los namespaces del sistema/infraestructura y busca aplicaciones de usuario que tengan desvíos críticos.
* **Alertas principales**:
  * 🔴 **`SIN_RESERVA`**: Pods corriendo sin memory request configurado (invisibles para el scheduler).
  * ⚠️ **`DESVÍO`**: Pods cuyo consumo real supera la reserva configurada por más de 100MB/200MB.
* **Casos de uso**: Detección rápida en terminal de aplicaciones con riesgo de caer por `OOMKilled` o que estén saturando nodos.
* **Uso**:
  ```bash
  ./Reporte-Rapido.sh
  ```

---

### 4. `Generar-CSV-Owners.sh` — Reporte Exportable para Negocio/SRE
* **¿Qué hace?**: Extrae de forma masiva y ultrarrápida el consumo y reserva de aplicaciones de negocio y lo exporta a formato CSV delimitado por `;`.
* **Salida**: Archivo `.csv` listo para abrir en Excel o compartir por mail.
* **Casos de uso**: Reporte ejecutivo para compartir con líderes técnicos o gerencias de desarrollo.
* **Uso**:
  ```bash
  ./Generar-CSV-Owners.sh
  ```

---

### 5. `Auditoria-Owners-Limpio.sh` — Chequeo de Configuración de Deployments
* **¿Qué hace?**: Analiza las definiciones estáticas de los Deployments de usuario clasificando su nivel de criticidad según su configuración de memoria.
* **Clasificación**:
  * 🔴 **CRÍTICO**: Sin `requests.memory`.
  * ⚠️ **RIESGO**: Sin `limits.memory`.
  * ✅ **CONFIGURADO**: Definiciones completas.
* **Uso**:
  ```bash
  ./Auditoria-Owners-Limpio.sh
  ```

---

## ⚡ Flujo de Trabajo Recomendado

1. Iniciá sesión en el clúster deseado desde la terminal (`oc login ...`).
2. Ejecutá el script correspondiente al análisis que quieras realizar.
3. Todos los reportes generarán archivos con marcas de tiempo (`timestamp`) y el nombre del clúster en su nombre para evitar sobreescrituras.