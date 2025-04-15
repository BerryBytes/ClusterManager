# 📚 **Cluster Service Documentation**

Welcome to the **Cluster Service** project! This guide outlines everything you need to set up, run, and utilize the application, leveraging FastAPI and Dapr for seamless microservice communication. Follow these steps to integrate a message broker with Dapr sidecars effortlessly.

---

## 🛠 **Prerequisites**

Before getting started, ensure the following tools are installed and configured:

- **Python**: Version `3.8.20`
- **Dapr CLI**: Installed and configured
- **Uvicorn**: ASGI server to run the FastAPI app
- **Message Broker**: (e.g., RabbitMQ, Kafka) for pub/sub functionality

### **Set Up a Virtual Environment**

1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   ```

2. Activate the virtual environment:
   - On Linux/macOS:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     .\venv\Scripts\activate
     ```

3. Once activated, install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🚀 **Getting Started**

### **Step 1: Start the Server**

Use the following command to start the FastAPI server with Dapr integration:

```bash
dapr run --app-id cluster-service --resources-path components/ --app-port 8082 -- gunicorn -w 4 -b 0.0.0.0:8082 main:app
```

#### **Command Breakdown**:

- **`dapr run`**: Launches a Dapr-enabled application.
- **`--app-id cluster-service`**: Assigns an app ID for Dapr service discovery.
- **`--resources-path components/`**: Points to the directory containing Dapr components and configurations.
- **`python3 -m uvicorn main:app`**: Starts the FastAPI app using Uvicorn.
- **`--reload`**: Enables live reloading for development.
- **`--host 0.0.0.0 --port 8082`**: Configures the app to listen on all interfaces on port `8082`.

---

### **Step 2: Install Dependencies**

Install the required Python dependencies:

```bash
pip install -r requirements.txt
```

---

### **Step 3: Run the Application**

With dependencies installed, use the `dapr run` command again to start the application:

```bash
dapr run --app-id cluster-service --resources-path components/ --app-port 8082 -- python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8082
```

---

## 🔧 **Dapr Configuration for Message Broker**

To enable pub/sub with a message broker, configure Dapr in the `components/pubsub.yaml` file as follows:

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
      value: amqps://user:pass@puffin.rmq2.cluster.svc.local/ioraopuk
    - name: port
      value: 5672
    - name: username
      value: ioraopuk
    - name: password
      value: pass
    - name: durable
      value: "true"
    - name: autoDelete
      value: "true"
```

---

### **Vault Configuration**

For secure secrets management using HashiCorp Vault, update `components/vault.yaml`:

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: vault
spec:
  metadata:
    - name: vaultAddr
      value: https://vaultexample.hashi.com
    - name: skipVerify
      value: true
    - name: vaultToken
      value: hvs.fake.token
    - name: vaultKVUsePrefix
      value: "false"
  type: secretstores.hashicorp.vault
  version: v1
```

### **Key Points**:

- Replace sensitive values (`host`, `username`, `password`, `vaultAddr`, etc.) with your credentials.
- No application code changes are necessary—Dapr handles pub/sub logic seamlessly through configurations.

---

## 🛡 **Dapr Annotations for Kubernetes**

To deploy the application in Kubernetes with a Dapr sidecar, add the following annotations to your resource YAML file:

```yaml
annotations:
  dapr.io/app-id: cluster-service
  dapr.io/app-port: "8082"
  dapr.io/enabled: "true"
  dapr.io/disable-builtin-k8s-secret-store: "true"
```

#### **Annotations Breakdown**:

1. **`dapr.io/app-id`**: Assigns the app ID for Dapr service identification.
2. **`dapr.io/app-port`**: Specifies the application’s listening port.
3. **`dapr.io/enabled`**: Enables the Dapr sidecar for this service.

---

## 🌟 **Why Use Dapr?**

- **Simplified Communication**: Decouples application logic from specific protocols or brokers.
- **Flexibility**: Easily switch between message brokers with minimal changes.
- **Scalability**: Optimized for Kubernetes with built-in support for sidecars.
- **Extensibility**: Add new services without refactoring core application code.

---

## 📖 **Additional Resources**

For more details, explore the [Dapr Documentation](https://github.com/dapr/dapr).

---

Enjoy building seamless microservices with **Cluster Service** and Dapr! 🚀
