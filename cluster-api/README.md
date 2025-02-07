# 📘 **Cluster API Documentation**

Welcome to the **Cluster API** project! This documentation provides a comprehensive guide to set up, run, and leverage the power of FastAPI integrated with Dapr for seamless microservice communication. Follow the steps below to get started and enable message broker functionality using Dapr sidecars.

---

## 🛠 **Prerequisites**

Ensure the following are installed and properly configured on your system:

- **Python**: Version `3.8.20`
- **Dapr CLI**: Installed and set up
- **Uvicorn**: ASGI server for running the FastAPI app
- **Message Broker**: (e.g., RabbitMQ, Kafka) for pub/sub capabilities

---

## 🚀 **Getting Started**

### **Step 1: Start the Server**

Run the following command to launch the FastAPI server with Dapr integration:

```bash
dapr run --app-id cluster-api --resources-path components/ -- python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8081
```

#### **Command Breakdown**:

1. **`dapr run`**: Starts the application with Dapr-enabled functionality.
2. **`--app-id cluster-api`**: Assigns an app ID for Dapr service discovery.
3. **`--resources-path components/`**: Specifies the directory containing Dapr configuration files.
4. **`python3 -m uvicorn main:app`**: Launches the FastAPI app using Uvicorn.
5. **`--reload`**: Enables hot-reloading during development.
6. **`--host 0.0.0.0 --port 8081`**: Sets the app to listen on all interfaces at port `8081`.

---

### **Step 2: Install Dependencies**

Install the necessary Python dependencies:

```bash
pip install -r requirements.txt
```

---

### **Step 3: Run the Application**

After installing dependencies, start the application using the `dapr run` command:

```bash
dapr run --app-id cluster-api --resources-path components/ -- python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8081
```

---

## 🔧 **Dapr Configuration for Message Broker**

To enable pub/sub functionality with a message broker, update the `components/pubsub.yaml` file with the following configuration:

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
      value: 40v9cPO6fSqnhAtYaie3bGNMhEX_6Jay
    - name: durable
      value: "true"
    - name: autoDelete
      value: "true"
```

### **Key Points**:

- Replace placeholders like `host`, `username`, and `password` with your broker credentials.
- No code modifications are required—simply update the Dapr configuration file.
- Dapr handles pub/sub interactions automatically for the application.

For additional details, visit the [Dapr Documentation](https://github.com/dapr/dapr).

---

## 🛡 **Dapr Annotations for Kubernetes**

When deploying the application in a Kubernetes environment, use the following annotations in your resource YAML to enable the Dapr sidecar:

```yaml
annotations:
  dapr.io/app-id: cluster-api
  dapr.io/app-port: "8081"
  dapr.io/enabled: "true"
  dapr.io/disable-builtin-k8s-secret-store: "true"
```

#### **Annotations Breakdown**:

1. **`dapr.io/app-id`**: Assigns the app ID for Dapr service identification.
2. **`dapr.io/app-port`**: Specifies the application's listening port.
3. **`dapr.io/enabled`**: Activates the Dapr sidecar for this service.

---

## 🌟 **Why Use Dapr?**

- **Decoupled Design**: Frees your application from dependencies on specific protocols or message brokers.
- **Scalability**: Easily scales in Kubernetes environments with sidecar architecture.
- **Flexibility**: Supports multiple brokers with minimal configuration changes.
- **Ease of Use**: Simplifies integration with built-in features for pub/sub, state management, and service invocation.

---

## 📖 **Additional Resources**

Explore more about Dapr by visiting the official [Dapr Documentation](https://github.com/dapr/dapr).

---

Seamlessly integrate microservices with **Cluster API** and unlock the full potential of Dapr! 🚀
