NODO=$1
for pod in $(oc get pods -A -o wide --no-headers | grep "$NODO" | awk '{print $1"/"$2}'); do
    namespace=$(echo $pod | cut -d'/' -f1)
    name=$(echo $pod | cut -d'/' -f2)
    oc adm top pod $name -n $namespace --no-headers 2>/dev/null
done | sort -k3 -h -r | head -n 10
