#!/bin/bash

# Exit on error
set -e

# Define cluster names
SERVICE_CLUSTER="api-cluster"
HOST_CLUSTER="host-cluster"

# Define credentials
MONGODB_USERNAME="berrybytes"
MONGODB_PASSWORD="password"
MONGODB_DATABASE="cloud"

RABBITMQ_USERNAME="berrybytes"
RABBITMQ_PASSWORD="password"

# Get the host IP from the internal network
HOST_IP=$(hostname -I | awk '{print $1}')

# Create clusters using Kind
function create_clusters() {
    echo "Creating $HOST_CLUSTER and $SERVICE_CLUSTER clusters..."

    # Add host entry to /etc/hosts
    echo "$HOST_IP hostcluster.example.com" | sudo tee -a /etc/hosts > /dev/null
    echo "Added '$HOST_IP hostcluster.example.com' to /etc/hosts"

    # Define Kind configuration for host cluster (with certSANs and public endpoint)
    cat <<EOF | kind create cluster --name $HOST_CLUSTER --config -
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: host-cluster
nodes:
- role: control-plane
  kubeadmConfigPatches:
  - |
    kind: ClusterConfiguration
    apiServer:
      certSANs:
      - "hostcluster.example.com"
      - "127.0.0.1"
      - "$HOST_IP"
    controlPlaneEndpoint: "hostcluster.example.com:7443"
  extraPortMappings:
  - containerPort: 6443
    hostPort: 7443
    protocol: TCP
EOF

    # Create service cluster
    kind create cluster --name $SERVICE_CLUSTER

    echo "$HOST_CLUSTER and $SERVICE_CLUSTER created successfully."

    # Generate separate kubeconfigs
    kind get kubeconfig --name $HOST_CLUSTER > $HOST_CLUSTER-kubeconfig
    kind get kubeconfig --name $SERVICE_CLUSTER > $SERVICE_CLUSTER-kubeconfig

    # Update host cluster kubeconfig to include additional SANs
    sed -i "s/https:\/\/0.0.0.0:7443/https:\/\/hostcluster.example.com:7443/g" $HOST_CLUSTER-kubeconfig
}

# Set up Dapr in service cluster
function setup_dapr() {
    echo "Setting up Dapr in $SERVICE_CLUSTER..."
    KUBECONFIG=$SERVICE_CLUSTER-kubeconfig kubectl config use-context kind-$SERVICE_CLUSTER --kubeconfig=$SERVICE_CLUSTER-kubeconfig
    #kubectl config use-context kind-$SERVICE_CLUSTER --kubeconfig=$SERVICE_CLUSTER-kubeconfig
    helm repo add dapr https://dapr.github.io/helm-charts
    helm install dapr dapr/dapr -n dapr-system --create-namespace
}

# Set up Keycloak in service cluster
function setup_keycloak() {
    echo "Setting up Dapr in $SERVICE_CLUSTER..."
    KUBECONFIG=$SERVICE_CLUSTER-kubeconfig kubectl config use-context kind-$SERVICE_CLUSTER
    # Define the Google Drive File ID and destination
    GOOGLE_DRIVE_FILE_ID="1McJObDuBtqyHniT4pRZVoqZX-AzIxqx3"
    DOWNLOAD_FILE="realm.json"

    # Download the file from Google Drive
    echo "Downloading realm configuration file from Google Drive..."

    # Step 1: Get the confirmation token (if required)
    confirm_token=$(curl -s -L "https://drive.google.com/uc?export=download&id=${GOOGLE_DRIVE_FILE_ID}" | grep -o 'confirm=[^&]*' | sed 's/confirm=//')

    # Step 2: Download the file with or without confirmation token
    if [ -z "$confirm_token" ]; then
        wget --no-check-certificate "https://drive.google.com/uc?export=download&id=${GOOGLE_DRIVE_FILE_ID}" -O "${DOWNLOAD_FILE}"
    else
        wget --no-check-certificate "https://drive.google.com/uc?export=download&confirm=${confirm_token}&id=${GOOGLE_DRIVE_FILE_ID}" -O "${DOWNLOAD_FILE}"
    fi

    # Create the values.yaml file
    cat > keycloak-values.yml << 'EOF'
extraEnvVars:
  - name: KEYCLOAK_EXTRA_ARGS
    value: --import-realm

extraVolumes:
  - name: realm-secret
    secret:
      secretName: realm-secret

extraVolumeMounts:
  - name: realm-secret
    mountPath: "/opt/bitnami/keycloak/data/import"
    readOnly: true
EOF

    # Create the secret directly from the file
    echo "Creating Kubernetes Secret..."
    kubectl create secret generic realm-secret --from-file=realm.json

    # Install Keycloak using the values file
    echo "Installing Keycloak with Helm chart..."
    helm install keycloak bitnami/keycloak \
        --create-namespace \
        -f keycloak-values.yml \
        --version 15.1.8

    echo "Keycloak setup completed successfully."

}

# Set up RabbitMQ in service cluster
function setup_rabbitmq() {
    echo "Setting up RabbitMQ in $SERVICE_CLUSTER..."
    KUBECONFIG=$SERVICE_CLUSTER-kubeconfig kubectl config use-context kind-$SERVICE_CLUSTER

    helm install rabbitmq bitnami/rabbitmq \
        --namespace rabbitmq \
        --create-namespace \
        --set auth.username=$RABBITMQ_USERNAME \
        --set auth.password=$RABBITMQ_PASSWORD \
        --set auth.vhost=$RABBITMQ_VHOST \
        --set resources.requests.cpu=100m \
        --set resources.requests.memory=256Mi \
        --set resources.limits.cpu=500m \
        --set resources.limits.memory=512Mi \
        --set service.ports.management=15672
}

# Set up MongoDB in service cluster
function setup_mongodb() {
    echo "Setting up MongoDB in $SERVICE_CLUSTER..."
    KUBECONFIG=$SERVICE_CLUSTER-kubeconfig kubectl config use-context kind-$SERVICE_CLUSTER

    helm install mongodb bitnami/mongodb \
        --namespace mongodb \
        --create-namespace \
        --set auth.rootUser=$MONGODB_USERNAME \
        --set auth.rootPassword=$MONGODB_PASSWORD \
        --set auth.usernames[0]=$MONGODB_USERNAME \
        --set auth.passwords[0]=$MONGODB_PASSWORD \
        --set auth.databases[0]=$MONGODB_DATABASE \
        --set resources.requests.cpu=100m \
        --set resources.requests.memory=256Mi \
        --set resources.limits.cpu=500m \
        --set resources.limits.memory=512Mi
}

# Set up Vault in service cluster
function setup_vault() {
    echo "Setting up Vault in $SERVICE_CLUSTER..."
    KUBECONFIG=$SERVICE_CLUSTER-kubeconfig kubectl config use-context kind-$SERVICE_CLUSTER

    helm repo add hashicorp https://helm.releases.hashicorp.com


    helm install vault hashicorp/vault \
        --namespace vault --create-namespace \
        --set "server.resources.requests.memory=256Mi" \
        --set "server.resources.requests.cpu=100m" \
        --set "server.resources.limits.memory=512Mi" \
        --set "server.resources.limits.cpu=500m"

    echo "Waiting for Vault pod to reach Running state..."
    until kubectl get pod -n vault -l "app.kubernetes.io/name=vault" -o jsonpath='{.items[0].status.phase}' | grep -q "Running"; do
        echo "Waiting for Vault pod to be in Running state..."
        sleep 5
    done

    echo "Initializing Vault..."
    kubectl exec -it vault-0 -n vault -- /bin/sh -c '
        vault operator init -key-shares=5 -key-threshold=3 | tee /tmp/vault-init.txt
        grep "Initial Root Token" /tmp/vault-init.txt | cut -d":" -f2 | tr -d " " > /tmp/vault-token.txt
        for i in $(seq 1 3); do
            UNSEAL_KEY=$(grep "Unseal Key $i" /tmp/vault-init.txt | cut -d":" -f2 | tr -d " ")
            vault operator unseal $UNSEAL_KEY
        done
    '

    # Get the token and keys
    kubectl cp vault-0:/tmp/vault-init.txt vault-keys.txt -n vault
    kubectl cp vault-0:/tmp/vault-token.txt vault-token.txt -n vault
    VAULT_TOKEN=$(cat vault-token.txt)

echo "Vault setup completed successfully!"
}

# Set up Cert-Manager in a cluster
function setup_cert_manager() {
    local cluster=$1
    echo "Setting up Cert-Manager in $cluster..."
    KUBECONFIG=$cluster-kubeconfig kubectl config use-context kind-$cluster

    # Check if cert-manager is already installed
    if ! helm list -n cert-manager --kubeconfig=$cluster-kubeconfig | grep -q cert-manager; then
        helm repo add jetstack https://charts.jetstack.io

        helm install cert-manager jetstack/cert-manager -n cert-manager --create-namespace \
          --set crds.enabled=true --kubeconfig=$cluster-kubeconfig
    else
        echo "Cert-Manager is already installed in $cluster, skipping installation."
    fi
}

# Set up Ingress-Nginx in a cluster
function setup_ingress_nginx() {
    local cluster=$1
    echo "Setting up Ingress-Nginx in $cluster..."
    KUBECONFIG=$cluster-kubeconfig kubectl config use-context kind-$cluster

    # Check if ingress-nginx is already installed
    if ! helm list -n ingress-nginx --kubeconfig=$cluster-kubeconfig | grep -q ingress-nginx; then
        helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
        helm install ingress-nginx ingress-nginx/ingress-nginx -n ingress-nginx --create-namespace \
            --set controller.extraArgs.enable-ssl-passthrough="" \
            --set controller.extraArgs."default-ssl-certificate=default/tls-secret" \
            --kubeconfig=$cluster-kubeconfig
    else
        echo "Ingress-Nginx is already installed in $cluster, skipping installation."
    fi
}

# Set up MetalLB in a cluster


function setup_metallb_host() {
    local max_retries=5
    local retry_count=0
    local wait_time=60

    echo "Setting up MetalLB in $HOST_CLUSTER..."

    # Validate KUBECONFIG and context
    if [ ! -f "$HOST_CLUSTER-kubeconfig" ]; then
        echo "Error: Kubeconfig file $HOST_CLUSTER-kubeconfig not found"
        return 1
    fi

    export KUBECONFIG="$HOST_CLUSTER-kubeconfig"

    # Switch context and verify
    if ! kubectl config use-context "kind-$HOST_CLUSTER" --kubeconfig="$KUBECONFIG"; then
        echo "Error: Failed to switch kubectl context"
        return 1
    fi

    # Check if MetalLB is already installed
    if kubectl get namespace metallb-system --kubeconfig="$KUBECONFIG" >/dev/null 2>&1; then
        echo "MetalLB namespace already exists. Checking deployment status..."
        if kubectl get deployment -n metallb-system controller --kubeconfig="$KUBECONFIG" >/dev/null 2>&1; then
            echo "MetalLB controller deployment already exists."
            echo "Would you like to (r)einstall MetalLB, (c)ontinue with existing installation, or (a)bort? [r/c/a]: "
            read -r choice
            case "$choice" in
                r|R)
                    echo "Removing existing MetalLB installation..."
                    kubectl delete namespace metallb-system --kubeconfig="$KUBECONFIG" --grace-period=0 --force
                    echo "Waiting for namespace deletion..."
                    while kubectl get namespace metallb-system --kubeconfig="$KUBECONFIG" >/dev/null 2>&1; do
                        echo "Waiting for metallb-system namespace deletion..."
                        sleep 5
                    done
                    ;;
                c|C)
                    echo "Continuing with existing installation..."
                    ;;
                *)
                    echo "Aborting setup..."
                    return 1
                    ;;
            esac
        fi
    fi

    # Apply MetalLB manifests if not already installed
    if ! kubectl get namespace metallb-system --kubeconfig="$KUBECONFIG" >/dev/null 2>&1; then
        echo "Installing MetalLB..."
        if ! kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.13.5/config/manifests/metallb-native.yaml --kubeconfig="$KUBECONFIG"; then
            echo "Error: Failed to apply MetalLB manifests"
            return 1
        fi
    fi

    # Wait for namespace with timeout
    echo "Waiting for MetalLB namespace to be ready..."
    for i in {1..12}; do  # 2 minute timeout (10s * 12)
        if kubectl get namespace metallb-system --kubeconfig="$KUBECONFIG" >/dev/null 2>&1; then
            break
        fi
        if [ $i -eq 12 ]; then
            echo "Error: Timeout waiting for MetalLB namespace"
            return 1
        fi
        echo "Waiting for namespace... ($(( 12 - i )) attempts remaining)"
        sleep 10
    done

    # Wait for controller deployment
    echo "Waiting for MetalLB controller deployment to be ready..."
    while [ $retry_count -lt $max_retries ]; do
        if kubectl wait --for=condition=available --timeout="${wait_time}s" deployment/controller -n metallb-system --kubeconfig="$KUBECONFIG"; then
            break
        fi

        retry_count=$((retry_count + 1))
        if [ $retry_count -lt $max_retries ]; then
            echo "Attempt $retry_count of $max_retries failed. Collecting debug information..."

            echo "--- MetalLB Pod Status ---"
            kubectl get pods -n metallb-system --kubeconfig="$KUBECONFIG"
            echo "--- MetalLB Pod Logs ---"
            kubectl logs -n metallb-system -l component=controller --tail=50 --kubeconfig="$KUBECONFIG" || true
            echo "--- MetalLB Pod Events ---"
            kubectl get events -n metallb-system --sort-by=.metadata.creationTimestamp --kubeconfig="$KUBECONFIG"

            echo "Retrying in 30 seconds..."
            sleep 30
        else
            echo "Error: Maximum retry attempts reached. MetalLB controller failed to become ready."
            return 1
        fi
    done

    # Detect network configuration
    echo "Detecting network configuration..."
    local network=""
    local control_plane_id

    # First try: Get network from control plane container
    control_plane_id=$(docker ps -a | grep "kind-control-plane" | grep "$HOST_CLUSTER" | awk '{print $1}')
    if [ -n "$control_plane_id" ]; then
        network=$(docker inspect "$control_plane_id" | grep -oP '"Gateway": "\K[0-9]+\.[0-9]+' | head -1)
    fi

    # Second try: Get network from kind network directly
    if [ -z "$network" ]; then
        network=$(docker network inspect kind | grep -oP '"Gateway": "\K[0-9]+\.[0-9]+' | head -1)
    fi

    # Fallback to default if both methods fail
    if [ -z "$network" ]; then
        network="172.18"
        echo "Warning: Could not detect network. Using default: $network"
    fi

    echo "Using network: $network"
    local IP_START="$network.254.202"
    local IP_END="$network.254.250"

    # Configure IPAddressPool if not already configured
    if ! kubectl get ipaddresspool -n metallb-system example --kubeconfig="$KUBECONFIG" >/dev/null 2>&1; then
        echo "Creating IPAddressPool with range $IP_START-$IP_END..."

        # Apply IPAddressPool
        cat <<EOF | kubectl apply -f - --kubeconfig="$KUBECONFIG"
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: example
  namespace: metallb-system
spec:
  addresses:
  - $IP_START-$IP_END
EOF

        # Apply L2Advertisement separately
        cat <<EOF | kubectl apply -f - --kubeconfig="$KUBECONFIG"
apiVersion: metallb.io/v1beta1
kind: L2Advertisement
metadata:
  name: default
  namespace: metallb-system
spec:
  ipAddressPools:
  - example
EOF
    else
        echo "IPAddressPool 'example' already exists"
    fi

    # Verify configuration with timeout
    echo "Verifying MetalLB configuration..."
    local verify_timeout=30
    local verify_start=$SECONDS

    while true; do
        if kubectl get ipaddresspool -n metallb-system example --kubeconfig="$KUBECONFIG" >/dev/null 2>&1 && \
           kubectl get l2advertisement -n metallb-system default --kubeconfig="$KUBECONFIG" >/dev/null 2>&1; then
            break
        fi

        if (( SECONDS - verify_start >= verify_timeout )); then
            echo "Error: Timeout waiting for MetalLB configuration verification"
            return 1
        fi

        echo "Waiting for MetalLB configuration to be ready..."
        sleep 5
    done

    echo "MetalLB setup completed successfully."
    return 0
}

function setup_metallb_service() {
    local max_retries=5
    local retry_count=0
    local wait_time=60

    echo "Setting up MetalLB in $SERVICE_CLUSTER..."

    # Validate KUBECONFIG and context
    if [ ! -f "$SERVICE_CLUSTER-kubeconfig" ]; then
        echo "Error: Kubeconfig file $SERVICE_CLUSTER-kubeconfig not found."
        return 1
    fi

    export KUBECONFIG="$SERVICE_CLUSTER-kubeconfig"

    # Switch context and verify
    if ! kubectl config use-context "kind-$SERVICE_CLUSTER" --kubeconfig="$KUBECONFIG"; then
        echo "Error: Failed to switch kubectl context."
        return 1
    fi

    # Check if MetalLB namespace already exists
    if kubectl get namespace metallb-system --kubeconfig="$KUBECONFIG" >/dev/null 2>&1; then
        echo "MetalLB namespace already exists. Checking deployment status..."
        if kubectl get deployment -n metallb-system controller --kubeconfig="$KUBECONFIG" >/dev/null 2>&1; then
            echo "MetalLB controller deployment already exists."
            echo "Would you like to (r)einstall MetalLB, (c)ontinue with existing installation, or (a)bort? [r/c/a]: "
            read -r choice
            case "$choice" in
                r|R)
                    echo "Removing existing MetalLB installation..."
                    kubectl delete namespace metallb-system --kubeconfig="$KUBECONFIG" --grace-period=0 --force
                    echo "Waiting for namespace deletion..."
                    while kubectl get namespace metallb-system --kubeconfig="$KUBECONFIG" >/dev/null 2>&1; do
                        sleep 5
                    done
                    ;;
                c|C)
                    echo "Continuing with existing installation..."
                    ;;
                *)
                    echo "Aborting setup..."
                    return 1
                    ;;
            esac
        fi
    fi

    # Apply MetalLB manifests if not already installed
    if ! kubectl get namespace metallb-system --kubeconfig="$KUBECONFIG" >/dev/null 2>&1; then
        echo "Installing MetalLB..."
        if ! kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.13.5/config/manifests/metallb-native.yaml --kubeconfig="$KUBECONFIG"; then
            echo "Error: Failed to apply MetalLB manifests."
            return 1
        fi
    fi

    echo "Waiting for MetalLB namespace and controller to be ready..."
    kubectl wait --for=condition=available --timeout=180s deployment/controller -n metallb-system --kubeconfig="$KUBECONFIG" || {
        echo "Error: MetalLB controller failed to become ready."
        return 1
    }

    # Detect network configuration
    echo "Detecting network configuration..."
    local network=""
    local control_plane_id

    # First try: Get network from control plane container
    control_plane_id=$(docker ps -a | grep "kind-control-plane" | grep "$SERVICE_CLUSTER" | awk '{print $1}')
    if [ -n "$control_plane_id" ]; then
        network=$(docker inspect "$control_plane_id" | grep -oP '"Gateway": "\K[0-9]+\.[0-9]+' | head -1)
    fi

    # Second try: Get network from kind network directly
    if [ -z "$network" ]; then
        network=$(docker network inspect kind | grep -oP '"Gateway": "\K[0-9]+\.[0-9]+' | head -1)
    fi

    # Fallback to default if both methods fail
    if [ -z "$network" ]; then
        network="172.18"
        echo "Warning: Could not detect network. Using default: $network"
    fi

    echo "Using network: $network"
    local IP_START="$network.254.200"
    local IP_END="$network.254.250"

    # Configure IPAddressPool if not already configured
    if ! kubectl get ipaddresspool -n metallb-system example --kubeconfig="$KUBECONFIG" >/dev/null 2>&1; then
        echo "Creating IPAddressPool with range $IP_START-$IP_END..."
        cat <<EOF | kubectl apply -f - --kubeconfig="$KUBECONFIG"
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: example
  namespace: metallb-system
spec:
  addresses:
  - $IP_START-$IP_END
EOF

        # Create L2Advertisement in a separate apply
        cat <<EOF | kubectl apply -f - --kubeconfig="$KUBECONFIG"
apiVersion: metallb.io/v1beta1
kind: L2Advertisement
metadata:
  name: default
  namespace: metallb-system
spec:
  ipAddressPools:
  - example
EOF
    else
        echo "IPAddressPool 'example' already exists."
    fi

    # Verify MetalLB configuration
    echo "Verifying MetalLB configuration..."
    kubectl get ipaddresspool -n metallb-system example --kubeconfig="$KUBECONFIG" || {
        echo "Error: Failed to configure IPAddressPool."
        return 1
    }
    kubectl get l2advertisement -n metallb-system default --kubeconfig="$KUBECONFIG" || {
        echo "Error: Failed to configure L2Advertisement."
        return 1
    }

    echo "MetalLB setup completed successfully."
    return 0
}




# Set up clusters
function setup_clusters() {
    echo "Setting up namespaces for $SERVICE_CLUSTER and $HOST_CLUSTER..."
    KUBECONFIG=$SERVICE_CLUSTER-kubeconfig kubectl config use-context kind-$SERVICE_CLUSTER
    kubectl create namespace $SERVICE_CLUSTER || echo "Namespace $SERVICE_CLUSTER already exists"
    KUBECONFIG=$HOST_CLUSTER-kubeconfig kubectl config use-context kind-$HOST_CLUSTER
    kubectl create namespace $HOST_CLUSTER || echo "Namespace $HOST_CLUSTER already exists"

    echo "Linking Service Cluster components to Host Cluster..."
    KUBECONFIG=$SERVICE_CLUSTER-kubeconfig kubectl config use-context kind-$SERVICE_CLUSTER
    kubectl label namespace $SERVICE_CLUSTER cluster-role=service
    KUBECONFIG=$HOST_CLUSTER-kubeconfig kubectl config use-context kind-$HOST_CLUSTER
    kubectl label namespace $HOST_CLUSTER cluster-role=host
}

# Deploy the service manifest in the service cluster
function deploy_service_manifest() {
    echo "Deploying service manifest to $SERVICE_CLUSTER..."
    KUBECONFIG=$SERVICE_CLUSTER-kubeconfig kubectl config use-context kind-$SERVICE_CLUSTER

    cat <<EOF | kubectl apply -f - --kubeconfig=$SERVICE_CLUSTER-kubeconfig
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cluster-service-python
  labels:
    app.kubernetes.io/instance: cluster-service
    app.kubernetes.io/version: 1.16.0
    helm.sh/chart: python-0.0.1
    dapr.io/app-id: subscriber-dapr
    dapr.io/metrics-enabled: "true"
    dapr.io/sidecar-injected: "true"
  annotations:
    dapr.io/app-id: subscriber-dapr
    dapr.io/app-port: "8082"
    dapr.io/disable-builtin-k8s-secret-store: "true"
    dapr.io/enabled: "true"
    dapr.io/log-level: debug
spec:
  replicas: 1
  selector:
    matchLabels:
      app.kubernetes.io/name: python
  template:
    metadata:
      labels:
        app: subscriber-dapr
        app.kubernetes.io/name: python
        app.kubernetes.io/instance: cluster-service
      annotations:
        dapr.io/app-id: subscriber-dapr
        dapr.io/app-port: "8082"
        dapr.io/disable-builtin-k8s-secret-store: "true"
        dapr.io/enabled: "true"
        dapr.io/log-level: debug
    spec:
      containers:
        - name: python
          image: rajivgs/cm-service:v18
          imagePullPolicy: Always
          env:
            - name: HOST_NAME
              value: clustermanager.local
            - name: DAPR_HTTP_PORT
              value: "3500"
            - name: DAPR_GRPC_PORT
              value: "50001"
          ports:
            - containerPort: 8082
              name: http
              protocol: TCP
          livenessProbe:
            initialDelaySeconds: 30
            periodSeconds: 30
            tcpSocket:
              port: http
          readinessProbe:
            initialDelaySeconds: 30
            periodSeconds: 30
            tcpSocket:
              port: http
          resources:
            limits:
              cpu: "512m"
              memory: 512Mi
            requests:
              cpu: 20m
              memory: 20Mi
      dnsPolicy: ClusterFirst
      restartPolicy: Always
---
apiVersion: v1
kind: Service
metadata:
  name: cluster-service-python
  namespace: default
spec:
  ports:
    - name: http
      port: 80
      protocol: TCP
      targetPort: 8082
  selector:
    app.kubernetes.io/instance: cluster-service
    app.kubernetes.io/name: python
  type: ClusterIP
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: cluster-service-python
  namespace: default
spec:
  ingressClassName: nginx
  rules:
    - host: cluster-service-python.clustermanager.local
      http:
        paths:
          - backend:
              service:
                name: cluster-service-python
                port:
                  number: 80
            path: /
            pathType: ImplementationSpecific
  tls:
    - hosts:
        - cluster-service-python.clustermanager.local
---
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app.kubernetes.io/instance: cluster-api
    app.kubernetes.io/name: python
  name: cluster-api-python
  namespace: default
spec:
  selector:
    matchLabels:
      app.kubernetes.io/instance: cluster-api
      app.kubernetes.io/name: python
  template:
    metadata:
      annotations:
        dapr.io/app-id: publisher-dapr
        dapr.io/app-port: "8081"
        dapr.io/disable-builtin-k8s-secret-store: "true"
        dapr.io/enabled: "true"
      creationTimestamp: null
      labels:
        app: publisher-dapr
        app.kubernetes.io/instance: cluster-api
        app.kubernetes.io/name: python
        dapr.io/app-id: publisher-dapr
        dapr.io/disable-builtin-k8s-secret-store: "true"
        dapr.io/metrics-enabled: "true"
        dapr.io/sidecar-injected: "true"
    spec:
      containers:
      - env:
        - name: ENV
          value: local
        - name: ADMIN_CLIENT_ID
          value: admin-cli
        - name: ADMIN_CLIENT_SECRET
          value: nZAEUFy0he6sZPI58KqG9JvK5qOtHJtY
        - name: ATLAS_URI
          value: mongodb://berrybytes:password@mongodb.mongodb.svc.cluster.local:27017
        - name: DB_NAME
          value: cloud
        - name: PYTHONDEVMODE
          value: "True"
        - name: DEBUG
          value: "True"
        - name: KEYCLOAK_URL
          value: https://keycloak.clustermanager.local
        - name: REALM_NAME
          value: clusterManager
        - name: REQUEST_GROUP_NAME
          value: request-user
        - name: REQUESTS_CA_BUNDLE
          value: /etc/tls/ca-certificates/ca.crt
        - name: SERVICE_URL
          value: https://cluster-service-python.clustermanager.local
        - name: CLIENT_ID
          value: clustermanagerclient
        image: umesh1212/cluster-api:tag16
        imagePullPolicy: Always
        livenessProbe:
          failureThreshold: 3
          initialDelaySeconds: 30
          periodSeconds: 30
          successThreshold: 1
          tcpSocket:
            port: http
          timeoutSeconds: 1
        name: python
        ports:
        - containerPort: 8081
          name: http
          protocol: TCP
        readinessProbe:
          failureThreshold: 3
          initialDelaySeconds: 30
          periodSeconds: 30
          successThreshold: 1
          tcpSocket:
            port: http
          timeoutSeconds: 1
        resources:
          limits:
            cpu: "1"
            memory: 1Gi
          requests:
            cpu: 20m
            memory: 20Mi
        volumeMounts:
        - mountPath: /etc/tls/ca-certificates/
          name: mkcert-ca
      volumes:
      - configMap:
          defaultMode: 420
          name: mkcert-ca
        name: mkcert-ca
---
apiVersion: v1
kind: Service
metadata:
  labels:
    app.kubernetes.io/instance: cluster-api
    app.kubernetes.io/name: python
  name: cluster-api-python
  namespace: default
spec:
  ports:
    - name: http
      port: 80
      protocol: TCP
      targetPort: 8081
  selector:
    app.kubernetes.io/name: python
  sessionAffinity: None
  type: ClusterIP
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: cluster-api-python
  namespace: default
spec:
  ingressClassName: nginx
  rules:
    - host: cluster-api.clustermanager.local
      http:
        paths:
          - backend:
              service:
                name: cluster-api-python
                port:
                  number: 80
            path: /
            pathType: ImplementationSpecific
  tls:
    - hosts:
        - cluster-api.clustermanager.local
---
apiVersion: v1
data:
  config.js: |
    window.config = {
      VITE_APP_RESTAPI_ENDPOINT: "https://cluster-api.clustermanager.local/v1",
      VITE_APP_KEYCLOAK_URL: "https://keycloak.clustermanager.local",
      VITE_APP_REALM: "clusterManager",
      VITE_APP_CLIENT_ID: "clustermanagerclient",
    }
kind: ConfigMap
metadata:
  name: config
  namespace: default

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cluster-ui-node
  labels:
    app: node
spec:
  replicas: 1
  selector:
    matchLabels:
      app: node
  template:
    metadata:
      labels:
        app: node
        app.kubernetes.io/provider: zerone
    spec:
      containers:
      - image: rajivgs/cluster-ui:v20
        imagePullPolicy: IfNotPresent
        livenessProbe:
          failureThreshold: 60
          initialDelaySeconds: 30
          periodSeconds: 30
          successThreshold: 1
          tcpSocket:
            port: http
          timeoutSeconds: 5
        name: node
        ports:
        - containerPort: 4173
          name: http
          protocol: TCP
        readinessProbe:
          failureThreshold: 60
          initialDelaySeconds: 10
          periodSeconds: 30
          successThreshold: 1
          tcpSocket:
            port: http
          timeoutSeconds: 5
        resources:
          limits:
            cpu: 500m
            memory: 512Mi
          requests:
            cpu: 20m
            memory: 20Mi
        volumeMounts:
        - mountPath: /app/dist/config.js
          name: config
          subPath: config.js
      volumes:
      - configMap:
          defaultMode: 420
          name: config
        name: config
---
apiVersion: v1
kind: Service
metadata:
  name: cluster-ui-node-service
  namespace: default
spec:
  ports:
    - name: http
      port: 80
      protocol: TCP
      targetPort: 4173
  selector:
    app: node
    app.kubernetes.io/provider: zerone
  type: ClusterIP
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ui-service
  namespace: default
spec:
  ingressClassName: nginx
  rules:
    - host: clusterui.clustermanager.local
      http:
        paths:
          - backend:
              service:
                name: cluster-ui-node-service
                port:
                  number: 80
            path: /
            pathType: ImplementationSpecific
  tls:
    - hosts:
        - clusterui.clustermanager.local
---

EOF
    echo "Service manifest deployed successfully to $SERVICE_CLUSTER"
}

function setup_dapr_components() {
    echo "Deploying dapr components manifest to $SERVICE_CLUSTER..."
    KUBECONFIG=$SERVICE_CLUSTER-kubeconfig kubectl config use-context kind-$SERVICE_CLUSTER

    echo "Setting up Dapr components..."
    VAULT_TOKEN=$(cat vault-token.txt)

    cat <<EOF | kubectl apply -f -
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: messagebus
  namespace: default
spec:
  type: pubsub.rabbitmq
  version: v1
  metadata:
  - name: host
    value: amqp://$RABBITMQ_USERNAME:$RABBITMQ_PASSWORD@rabbitmq.rabbitmq.svc.cluster.local/
  - name: port
    value: 5672
  - name: username
    value: $RABBITMQ_USERNAME
  - name: password
    value: $RABBITMQ_PASSWORD
  - name: durable
    value: "true"
  - name: autoDelete
    value: "true"
---
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: vault
  namespace: default
spec:
  type: secretstores.hashicorp.vault
  version: v1
  metadata:
  - name: vaultAddr
    value: http://vault.vault.svc.cluster.local:8200
  - name: skipVerify
    value: true
  - name: vaultToken
    value: $VAULT_TOKEN
  - name: vaultKVUsePrefix
    value: "false"
---

EOF
}


function setup_ingress() {
    echo "Setting up  Ingress "

        cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  annotations:
    nginx.ingress.kubernetes.io/proxy-buffer-size: 128k
    nginx.ingress.kubernetes.io/proxy-buffers: 4 256k
  name: keycloak
spec:
  ingressClassName: nginx
  rules:
  - host: keycloak.clustermanager.local
    http:
      paths:
      - path: /
        pathType: ImplementationSpecific
        backend:
          service:
            name: keycloak
            port:
              number: 80
  tls:
  - hosts:
    - keycloak.clustermanager.local

EOF

    echo "TLS and Ingress setup completed."
}

# Deploy status-controller in the host-cluster
function deploy_status_controller() {
    echo "Deploying status-controller in $HOST_CLUSTER..."
    KUBECONFIG=$HOST_CLUSTER-kubeconfig kubectl config use-context kind-$HOST_CLUSTER

    cat <<EOF | kubectl apply -f - --kubeconfig=$HOST_CLUSTER-kubeconfig
apiVersion: v1
kind: Namespace
metadata:
  name: status-controller
  labels:
    name: status-controller
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: status-cluster-role-binding
roleRef:
  kind: ClusterRole
  name: status-cluster-role
  apiGroup: rbac.authorization.k8s.io
subjects:
  - kind: ServiceAccount
    name: default
    namespace: status-controller
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: status-cluster-role
rules:
  - apiGroups: [""]
    resources: ["nodes", "services", "pods", "endpoints"]
    verbs: ["get", "list", "watch"]
  - apiGroups: [""]
    resources: ["configmaps"]
    verbs: ["get"]
  - apiGroups: ["extensions"]
    resources: ["deployments"]
    verbs: ["get", "list", "watch"]
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: status-controller
  namespace: status-controller
spec:
  replicas: 1
  selector:
    matchLabels:
      app: status-controller
  template:
    metadata:
      labels:
        app: status-controller
    spec:
      containers:
        - name: status-controller
          image: rajivgs/cluster-status:v1
          imagePullPolicy: Always
          env:
            - name: API_URL
              value: "https://cluster-api.clustermanager.local"
---
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: clustermanager-cert
  namespace: default
spec:
  secretName: tls-secret
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
  commonName: clustermanager.local
  dnsNames:
    - clustermanager.local
    - "*.clustermanager.local"
---
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  selfSigned: {}

EOF
    echo "status-controller deployed successfully in $HOST_CLUSTER."
}

# Function to update /etc/hosts with ingress hostnames, grouped by external IP, avoiding duplicates
function update_hosts_file_with_ingress() {
    local cluster=$1
    echo "Updating /etc/hosts with ingress hostnames for $cluster..."

    KUBECONFIG=$cluster-kubeconfig kubectl config use-context kind-$cluster

    # Retrieve ingress hostnames and their corresponding external IPs
    ingress_info=$(kubectl get ingress --all-namespaces -o jsonpath='{range .items[*]}{.status.loadBalancer.ingress[*].ip}{" "}{.spec.rules[*].host}{"\n"}{end}')

    # Create an associative array to group hostnames by external IP
    declare -A ip_to_hostnames

    while read -r ip hostname; do
        if [[ -n "$ip" && -n "$hostname" ]]; then
            # Avoid duplicate hostnames for the same IP
            if [[ ! "${ip_to_hostnames["$ip"]}" =~ $hostname ]]; then
                ip_to_hostnames["$ip"]+="$hostname "
            fi
        fi
    done <<< "$ingress_info"

    # Backup /etc/hosts before modifying
    sudo cp /etc/hosts /etc/hosts.bak

    # Remove any existing entries for these IPs
    for ip in "${!ip_to_hostnames[@]}"; do
        sudo sed -i "/^$ip/d" /etc/hosts
    done

    # Add consolidated entries to /etc/hosts
    for ip in "${!ip_to_hostnames[@]}"; do
        entry="$ip ${ip_to_hostnames[$ip]}"
        echo "$entry" | sudo tee -a /etc/hosts > /dev/null
        echo "Added entry: $entry"
    done

    echo "/etc/hosts updated successfully with ingress entries for $cluster."
}

# Function to check and install clusterctl
function install_clusterctl() {
    echo "Checking for clusterctl installation..."

    # Check if clusterctl is already installed
    if command -v clusterctl &> /dev/null; then
        echo "clusterctl is already installed. Version: $(clusterctl version)"
        return 0
    fi

    echo "clusterctl is not installed. Installing now..."

    # Detect operating system and architecture
    OS=$(uname -s | tr '[:upper:]' '[:lower:]')
    ARCH=$(uname -m)

    # Determine the download URL based on OS and architecture
    case $OS in
        linux)
            if [[ $ARCH == "x86_64" ]]; then
                URL="https://github.com/kubernetes-sigs/cluster-api/releases/download/v1.9.3/clusterctl-linux-amd64"
            else
                echo "Unsupported architecture: $ARCH on Linux."
                exit 1
            fi
            ;;
        darwin)
            if [[ $ARCH == "x86_64" ]]; then
                URL="https://github.com/kubernetes-sigs/cluster-api/releases/download/v1.9.3/clusterctl-darwin-amd64"
            elif [[ $ARCH == "arm64" ]]; then
                URL="https://github.com/kubernetes-sigs/cluster-api/releases/download/v1.9.3/clusterctl-darwin-arm64"
            else
                echo "Unsupported architecture: $ARCH on macOS."
                exit 1
            fi
            ;;
        *)
            echo "Unsupported operating system: $OS."
            exit 1
            ;;
    esac

    # Download and install clusterctl
    echo "Downloading clusterctl from $URL..."
    curl -L $URL -o clusterctl
    chmod +x ./clusterctl
    sudo mv ./clusterctl /usr/local/bin/clusterctl

    # Verify installation
    if command -v clusterctl &> /dev/null; then
        echo "clusterctl installed successfully. Version: $(clusterctl version)"
    else
        echo "Failed to install clusterctl."
        exit 1
    fi
}

# Export HOST_CLUSTER and initialize clusterctl
function init_clusterctl() {
    echo "Exporting HOST_CLUSTER and initializing clusterctl..."

    export KUBECONFIG="$HOST_CLUSTER-kubeconfig"
    echo "KUBECONFIG exported: $KUBECONFIG"

    # Initialize clusterctl with vcluster infrastructure
    clusterctl init --infrastructure vcluster

    if [[ $? -eq 0 ]]; then
        echo "clusterctl initialized successfully with vcluster."
    else
        echo "Failed to initialize clusterctl with vcluster."
        exit 1
    fi
}

# Set up secrets in Vault
function setup_secretVault() {
    echo "Exporting SERVICE_CLUSTER and initializing secrets..."

    export KUBECONFIG="$SERVICE_CLUSTER-kubeconfig"
    echo "KUBECONFIG exported: $KUBECONFIG"

    echo "Fetching Vault token from local file..."
    if [[ ! -f vault-token.txt ]]; then
        echo "Error: vault-token.txt not found. Please ensure Vault is initialized and the token file is available."
        exit 1
    fi
    VAULT_TOKEN=$(cat vault-token.txt)

    echo "Ensuring secret/dapr path exists and configuring secrets..."
    HOST_CLUSTER_KUBECONFIG_BASE64=$(base64 -w 0 < "$HOST_CLUSTER-kubeconfig")

    kubectl exec -it vault-0 -n vault -- /bin/sh -c "
        export VAULT_TOKEN=$VAULT_TOKEN
        vault secrets enable -path=secret kv-v2 || true

        vault kv put secret/dapr \
            4d17f7f0-752b-4a5e-844b-915a55876b22='$HOST_CLUSTER_KUBECONFIG_BASE64'
    "

    if [[ $? -eq 0 ]]; then
        echo "Secrets successfully added to dapr/secret path."
    else
        echo "Failed to add secrets to dapr/secret path. Please check Vault configuration."
        exit 1
    fi
}


function install_mkcert() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if ! command -v brew &> /dev/null; then
            echo "Error: Homebrew is required for macOS installation"
            exit 1
        fi
        brew install mkcert
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        sudo apt update
        sudo apt install -y mkcert
    else
        echo "Error: Unsupported operating system"
        exit 1
    fi
}

function setup_certificates() {
    # Verify cluster variables are set
    if [ -z "$SERVICE_CLUSTER" ] || [ -z "$HOST_CLUSTER" ]; then
        echo "Error: SERVICE_CLUSTER and/or HOST_CLUSTER variables are not set"
        echo "Current values:"
        echo "SERVICE_CLUSTER: ${SERVICE_CLUSTER:-not set}"
        echo "HOST_CLUSTER: ${HOST_CLUSTER:-not set}"
        return 1
    fi

    # Verify kubeconfig files exist
    if [ ! -f "$HOST_CLUSTER-kubeconfig" ]; then
        echo "Error: $HOST_CLUSTER-kubeconfig file not found"
        return 1
    fi
    if [ ! -f "$SERVICE_CLUSTER-kubeconfig" ]; then
        echo "Error: $SERVICE_CLUSTER-kubeconfig file not found"
        return 1
    fi

    # Install mkcert if not present
    if ! command -v mkcert &> /dev/null; then
        echo "Installing mkcert..."
        install_mkcert
    fi
  # Get mkcert root CA location
    CAROOT=$(mkcert -CAROOT)
    ROOT_CA="${CAROOT}/rootCA.pem"

    # Generate certificates
    echo "Generating certificates for clustermanager.local..."
    mkcert -install
    mkcert clustermanager.local "*.clustermanager.local"

    # Apply certificates to both clusters
    for cluster in "$HOST_CLUSTER" "$SERVICE_CLUSTER"; do
        echo "Applying certificates to $cluster..."

        # Switch context to current cluster
        export KUBECONFIG="$cluster-kubeconfig"
        kubectl config use-context "kind-$cluster"

        # Create TLS secret from generated certificates
        echo "Creating TLS secret in $cluster..."
        kubectl create secret tls tls-secret \
            --cert=clustermanager.local+1.pem \
            --key=clustermanager.local+1-key.pem \
            -n default --dry-run=client -o yaml | kubectl apply -f -
 # Create ConfigMap with root CA certificate
        kubectl create configmap mkcert-ca \
            --from-file=ca.crt="${ROOT_CA}" \
            -n default --dry-run=client -o yaml | kubectl apply -f -
        # Apply cert-manager configurations
        echo "Applying cert-manager configurations to $cluster..."
    done

    echo "Certificate setup completed for both clusters"
}

apply_certificate_manifest() {
    echo "Exporting HOST_CLUSTER and initializing clusterctl..."

    export KUBECONFIG="$HOST_CLUSTER-kubeconfig"
    echo "KUBECONFIG exported: $KUBECONFIG"
  local manifest=$(cat <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  selfSigned: {}
---
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: clustermanager-cert
  namespace: default
spec:
  secretName: tls-secret
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
  commonName: clustermanager.local
  dnsNames:
  - clustermanager.local
  - "*.clustermanager.local"
EOF
)

  echo "$manifest" | kubectl apply -f -
  echo "Certificate setup completed"
}

sleep 10
# Install metrics server in host cluster
function setup_metrics_server() {
    echo "Installing metrics server in $HOST_CLUSTER..."
    export KUBECONFIG="$HOST_CLUSTER-kubeconfig"

    # Install metrics server components
    kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

    # Wait for metrics server deployment to be ready
    sleep 5

    # Patch metrics server to allow insecure TLS
    kubectl patch deployment metrics-server -n kube-system --type=json \
        -p='[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--kubelet-insecure-tls" }]'

    echo "Metrics server installed and configured successfully"
}


##  Main installation process
##
create_clusters
install_mkcert


setup_cert_manager $SERVICE_CLUSTER
setup_cert_manager $HOST_CLUSTER
setup_certificates
setup_ingress_nginx $HOST_CLUSTER
setup_ingress_nginx $SERVICE_CLUSTER
setup_keycloak
setup_rabbitmq
setup_mongodb
setup_dapr
setup_vault

setup_dapr_components
setup_ingress
deploy_status_controller
setup_clusters
deploy_service_manifest

#restore_mongodb
setup_metallb_service
setup_metallb_host
install_clusterctl
init_clusterctl
setup_secretVault
echo "Saving access information..."
echo "RabbitMQ Management URL: http://127.0.0.1:15672/"
echo "RabbitMQ Username: $RABBITMQ_USERNAME"
echo "RabbitMQ Password: $RABBITMQ_PASSWORD"
echo "MongoDB Connection: mongodb://$MONGODB_USERNAME:$MONGODB_PASSWORD@staging-mongodb.01cloud-staging.svc.cluster.local:27017"
echo "Vault Token saved in: vault-token.txt"
echo "Vault Keys saved in: vault-keys.json"
echo "https://clusterui.clustermanager.local -> username: test@test.com password: password"

echo "Cluster setup completed successfully!"
sleep 10
update_hosts_file_with_ingress $SERVICE_CLUSTER
update_hosts_file_with_ingress $HOST_CLUSTER
sleep 10
setup_metrics_server
