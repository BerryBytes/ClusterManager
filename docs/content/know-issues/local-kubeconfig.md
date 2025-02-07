# Setting Up a KIND Cluster with Internal Network Access

This guide provides step-by-step instructions to create a Kubernetes cluster using KIND (Kubernetes IN Docker) on your localhost. The configuration ensures the kubeconfig is accessible within your internal network.

## Prerequisites

- Installed Docker
- Installed KIND
- Administrative privileges to modify `/etc/hosts`

---

## Steps to Create the Cluster

### 1. Get the Host IP of Your Internal Network

Run the following command to retrieve your internal network IP:

```bash
hostname -I | awk '{print $1}'
```

**Example Output:**

```
192.168.1.93
```

### 2. Add the Domain Name to `/etc/hosts`

Edit the `/etc/hosts` file to map your internal IP to a custom domain name:

```bash
sudo nano /etc/hosts
```

Add the following line:

```
192.168.1.93 cluster.example.com
```

Save and close the file.

### 3. Create a KIND Cluster Configuration File

Create a `config.yaml` file with the following content:

```yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: public-cluster-2
nodes:
  - role: control-plane
    kubeadmConfigPatches:
      - |
        kind: ClusterConfiguration
        apiServer:
          certSANs:
          - "cluster.example.com"
          - "127.0.0.1"
          - "192.168.1.93"
        controlPlaneEndpoint: "cluster.example.com:6443"
    extraPortMappings:
      - containerPort: 6443
        hostPort: 6443
        protocol: TCP
```

### 4. Create the KIND Cluster

Run the following command to create the cluster using your configuration:

```bash
kind create cluster --config config.yaml --kubeconfig /home/users/public-kindcluster/public-cluster.yaml
```

This will create a KIND cluster and save the kubeconfig file at `/home/users/public-kindcluster/public-cluster.yaml`.

---
