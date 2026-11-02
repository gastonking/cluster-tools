# OpenShift 3.x Node Status Dashboard

Dashboard web ligero para consultar y visualizar el estado de salud de los nodos de un cluster OpenShift 3.x en tiempo real.

## Estructura del proyecto

```text
ocp3-node-dashboard/
├── .gitlab-ci.yml
├── Dockerfile
├── requirements.txt
├── app.py
├── README.md
└── templates/
    └── index.html
```

## Despliegue en OpenShift 3.x

```bash
oc new-project monitoring-dashboard
oc create sa dashboard-sa
oc adm policy add-cluster-role-to-user cluster-reader -z dashboard-sa
oc new-app https://gitlab.com/tu-usuario/ocp3-node-dashboard.git --name=ocp3-dashboard
oc patch dc/ocp3-dashboard -p '{"spec":{"template":{"spec":{"serviceAccountName":"dashboard-sa"}}}}'
oc expose svc/ocp3-dashboard
```
