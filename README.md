<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/assets/clustermanager-logo.png">
    <source media="(prefers-color-scheme: light)" srcset="docs/assets/clustermanager-logo.png">
    <img alt="ClusterManager Logo" title="ClusterManager" src="docs/assets/clustermanager-logo.png" width="400">
  </picture>
</p>

# 🖥️ ClusterManager

**ClusterManager** is a Kubernetes-designed application to simplify the creation and management of **fully managed virtual clusters**. It utilizes Kubernetes Custom Resource Definitions (CRDs) to extend the Kubernetes API, enabling seamless provisioning and configuration of virtual clusters tailored to your needs.

<p align="center">
  <a href="https://doc.clustermanager.io/clustermanager"><img alt="Docs" src="https://img.shields.io/badge/docs-current-brightgreen.svg"></a>
  <a href="https://github.com/clustermanager/clustermanager/blob/master/LICENSE.md"><img alt="License" src="https://img.shields.io/badge/license-MIT-blue.svg"></a>
</p>

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Maintainers](#maintainers)
- [Contributing](#contributing)
- [Credits](#credits)
- [License](#license)

---

## 🧐 Overview

**ClusterManager** is a Kubernetes operator designed to **simplify** the creation and management of **virtual clusters**.It manage the multiple main cluster by region. By leveraging Kubernetes Custom Resource Definitions (CRDs), it extends the Kubernetes API, providing an easy-to-use platform for provisioning and configuring virtual clusters.

### 🏗️ Architecture

<p align="center"> <picture> <source media="(prefers-color-scheme: dark)" srcset="docs/assets/clustermanager_arch.png"> <source media="(prefers-color-scheme: light)" srcset="docs/assets/clustermanager_arch.png"> <img alt="ClusterManager Architecture" title="ClusterManager Architecture" src="docs/assets/clustermanager_arch.png" width="600"> </picture> </p>

### 🚀 Key Benefits:

- **Isolation**: Strong isolation for multi-tenancy.
- **Simplified Management**: Easily manage resources and configurations.
- **Automated Provisioning**: Reduce administrative overhead with automated cluster provisioning.

---

## 🌟 Features

- **Virtual Cluster Automation**: Effortlessly create virtual clusters with custom configurations.
- **Integrated Ingress Configuration**: Automatically expose virtual cluster ingress through the host cluster.
- **Advanced Resource Management**: Set resource quotas, limit ranges, and other Kubernetes configurations to enhance governance.
- **Sleep Mode**: Suspend virtual clusters to optimize resource utilization.

---

## 📦 Prerequisites

Before installing ClusterManager, ensure that you have the following:

- A Kubernetes cluster (v1.24+).
- **Helm 3** installed.
- **Dapr** installed.
- **Keycloak** installed.
- **HashiCorp Vault** installed.
- [Clusterctl](https://cluster-api.sigs.k8s.io/user/quick-start.html#install-clusterctl) installed.
- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/) installed.
- Cluster administrator privileges.

---

## 🚀 Installation

### Setup primary cluster

#### 🔧 Using Helm

ClusterManager can be easily installed using Helm:

```bash
helm install dapr ./manifest/charts/dapr -f ./manifest/charts/dapr/values.yaml
```

```bash
helm install keycloak ./manifest/charts/keycloak/ -f ./manifest/charts/keycloak/values.yaml
```

```bash
helm install vault ./manifest/charts/vault/ -f ./manifest/charts/vault/values.yaml
```

```bash
helm install mongodb ./manifest/charts/mongodb/ -f ./manifest/charts/mongodb/values.yaml
```

```bash
helm install rabbitmq ./manifest/charts/rabbitmq/ -f ./manifest/charts/rabbitmq/values.yaml
```

```bash
kubectl apply -f ./manifest/primary-cluster/
```

---

### Setup Host Cluster.

#### 🛠️ Installing clusterctl

Install the vCluster provider:

```bash
clusterctl init --infrastructure vcluster
```

```bash
kubectl apply -f ./manifest/target-custer/
```

---

### 🔧 Setup Dapr Component

#### 🐇 RabbitMQ

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: messagebus
spec:
  type: pubsub.rabbitmq
  version: v1
  metadata:
    - name: host
      value: amqps://user:pass@puffin.rmq2.example.com/ioraopuk
    - name: port
      value: 5672
    - name: username
      value: user
    - name: password
      value: pass
    - name: durable
      value: "true"
    - name: autoDelete
      value: "true"
```

#### 🔐 HashiCorp Vault

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: vault
spec:
  metadata:
    - name: vaultAddr
      value: http://vault.vault.svc.cluster.local:8200
    - name: skipVerify
      value: true
    - name: vaultToken
      value: hvs.fake.token # Initial Root Token in Vault
    - name: vaultKVUsePrefix
      value: "false"
  type: secretstores.hashicorp.vault
  version: v1
```

#### How to create secret in Vault

- Step 1: Create a Key-Value (KV) Engine on Vault

- Step 2: Give a name "secret" and click on the create button

- Step 3: Create a "dapr" secret

- Step 4: Add the value of "host_id" as "dsfsdfdsfds" (created in a HostCluster using API Swagger)

- Step 5: Set the key-value pair: "host_id": "base64Encoded kubeconfig"

- Step 6: Finish

#### Setting up the Host Cluster Status Controller

You need to apply the status controller in the host cluster where you created a vcluster.

```bash
kubectl apply -f manifest/target-custer/status-controller.yaml
```

Update the cluster API endpoint in the status controller manifest:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: status-controller
  namespace: status-namespace
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
          image: your-image-repository/status-controller:latest
          env:
            - name: API_URL
              value: "https://cluster-api.staging.01cloud.dev/"
          ports:
            - containerPort: 8080
```
#### Spinning up the clusterManager in LOCAL CLUSTER using Script
Here is the script to setup the [clusterManager](docs/script/clusterManager_setup-local.sh) in local cluster.

## 👥 Maintainers

We embrace an open and inclusive community philosophy. Motivated contributors are encouraged to join the [maintainers' team](docs/content/contributing/maintainers.md).  
Learn more about pull request reviews and issue triaging in our [contributor guide](docs/content/contributing/contributor-guidelines.md).

---
## 👥 Community  

Join our vibrant [Discord community](https://discord.gg/g4a3P9af) to connect with contributors and maintainers. Engage in meaningful discussions, collaborate on ideas, and stay updated on the latest developments!  

---

Let me know if you'd like any further refinements! 😊

## 🤝 Contributing

Interested in contributing? Refer to our [contributing documentation](CONTRIBUTING.md).  
This project adheres to a [Code of Conduct](CODE_OF_CONDUCT.md), and participation requires compliance with its terms.

---

## 🎉 Credits

Special thanks to [Berrybytes](https://www.berrybytes.com) for bringing this project to life!

---

## 📜 License

ClusterManager is open-source software licensed under the [MIT License](LICENSE).

### Key Enhancements:

1. **Visually Engaging Structure**: We've used emojis to separate sections and make key areas stand out. This creates an easy-to-read, welcoming atmosphere.
2. **Readable Headers**: The use of headers like **Installation**, **Features**, **Prerequisites**, etc., makes the document easy to navigate.
3. **Clear Examples and Code Blocks**: Code snippets are formatted properly and separated for easier reading.
4. **Table of Contents**: The Table of Contents at the beginning allows users to quickly navigate the document to relevant sections.
5. **Improved Formatting**: Sections like **Installation** and **Prerequisites** are cleanly formatted, making the process easier to follow.

This revised README is more visually appealing and user-friendly while maintaining its clarity and professionalism.
