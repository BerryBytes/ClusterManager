# 🌟 Cluster Pod Status Controller

## 🛠️ Prerequisites

- **Kubernetes Cluster** 🚀

## 🚀 Quick Installation Guide

### 🛠️ Apply the Deployment
To deploy the Cluster Pod Status Controller, run the following command:

```bash
bash ./deployment/apply.sh
```

### 🧹 Clean Up or Destroy
To remove the Cluster Pod Status Controller and clean up resources, execute:

```bash
bash ./deployment/destroy.sh
```

## 📖 Detailed Installation Guide

### 1. 📝 Create Service Account
First, create the necessary service account:

```bash
kubectl apply -f ./deployment/service-account.yml
```

### 2. 🔑 Create Cluster Role
Next, apply the Cluster Role:

```bash
kubectl apply -f ./deployment/cluster-role.yml
```

### 3. 🔗 Create Cluster Role Binding
Bind the Cluster Role to the Service Account:

```bash
kubectl apply -f ./deployment/cluster-role-binding.yml
```

### 4. 🚀 Apply Deployment
Finally, deploy the Cluster Pod Status Controller:

```bash
kubectl apply -f ./deployment/deployment.yml
```

## 🏃‍♂️ Running the Application

### 🖥️ Run Locally
To run the application locally, use the following commands:

```bash
go mod tidy
go run main.go
```

### 🔨 Build and Run
To build the application and run it:

```bash
go build -o main .
./main
```

## 📜 Summary

This guide provides a quick and detailed installation process for the **Cluster Pod Status Controller**. Whether you prefer a quick setup or a step-by-step approach, you can easily deploy and manage the controller in your Kubernetes cluster. 🌐

---

Feel free to reach out if you have any questions or need further assistance! 😊
