# 🌟 **ClusterManager: Building & Testing Documentation**

Welcome to the **ClusterManager** guide! This document provides all the steps you need to build and test your very own **ClusterManager** binary from source code.

---

## 📖 **Overview**

The **ClusterManager** project enables you to compile and test the application, allowing customization to meet your specific requirements. Follow the steps below to set up the environment, build the microservices, and create your binaries with ease.

---

## 📋 **Prerequisites**

Before getting started, ensure you have the following tools installed:

- **[Docker](https://github.com/docker/docker)**: For containerization.
- **`make`**: A build automation tool.
- **[shellcheck](https://github.com/koalaman/shellcheck)**: For shell script analysis.
- **[Tailscale](https://tailscale.com/)**: Required if using Docker Desktop for networking.

---

## 🛠️ **Source Directory Setup**

It is recommended to clone the **ClusterManager** repository into the following directory:

```bash
~/ClusterManager
```

---

## 🚀 **Building ClusterManager Microservices**

Once your environment is set up, and the repository is cloned, you can proceed to build the microservices.

### **Build Commands**

Run the following commands to build the microservices:

```bash
# Build the ClusterManager API service
docker build -t cluster-api:latest ./cluster-api

# Build the ClusterManager UI service
docker build -t cluster-ui:latest ./cluster-ui

# Build the ClusterManager Service component
docker build -t cluster-service:latest ./cluster-service
```

---

#### Run the dapr in docker container in development server.

```bash
docker pull daprio/daprd
```

```bash
docker run -d \
  --name dapr-container \
  -p 3500:3500 \ # Dapr HTTP port
  -p 50001:50001 \ # Dapr gRPC port
  -e APP_ID=YOUR_APP_ID \
  daprio/daprd
```

YOUR_APP_ID could be "cluster-api", "cluster-service"

#### Run the application in development server

1. Cluster-api

```bash
dapr run --app-id cluster-api --resources-path components/ -- python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8081
```

2. Cluster-service

```bash
dapr run --app-id cluster-service --resources-path components/ --app-port 8082 -- python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8082
```

3. Cluster-ui

```bash
npm run dev
```

## 💡 **Pro Tips**

- Ensure your Go environment is properly configured before initiating the build.
- Use consistent tags (e.g., `latest`) to maintain clarity during deployment.
- Regularly check for typos in your code with **misspell**.
- Analyze shell scripts using **shellcheck** to prevent scripting errors.

---

## 📝 **Additional Resources**

- For further details, visit the official documentation on [Docker](https://github.com/docker/docker).
- Explore tools like [misspell](https://github.com/golangci/misspell) and [shellcheck](https://github.com/koalaman/shellcheck) to ensure code quality.

---

## 🎉 **Congratulations!**

You are now ready to compile and test your own **ClusterManager** . Customize the project as needed and enjoy seamless cluster management! 🚀
