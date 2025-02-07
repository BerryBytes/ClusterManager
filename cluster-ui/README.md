# 🌐 **Cluster UI Documentation**

Welcome to the **Cluster UI**, the frontend application for managing clusters seamlessly. This guide provides detailed instructions to set up, configure, and deploy the application for local development or production environments.

---

## 📋 **Prerequisites**

Ensure the following tools and versions are installed:

- **Node.js**: `16` or above
- **React**: `18` or above
- **Vite**: `4.4.0`
- **TypeScript**: `5` or above

---

## 🚀 **Getting Started**

### **Step 1: Install Dependencies**

Install all required packages for the project using the command:

```bash
npm install --legacy-peer-deps
```

---

### **Step 2: Configure Application**

Create a `config.js` file and populate it with the required configurations:

```javascript
window.config = {
  VITE_APP_RESTAPI_ENDPOINT: "https://domain_example.com/v1", // Backend REST API endpoint
  VITE_APP_KEYCLOAK_URL: "https://sso.keycloak.com/", // Keycloak SSO URL
  VITE_APP_REALM: "clusterManager", // Keycloak authentication realm
  VITE_APP_CLIENT_ID: "clustermanagerclient", // Keycloak client ID
  O_AUTH_CLIENTS: {
    // OAuth client URLs for environments
    "01cloud": [
      "https://console.example.io/loginsso/clustermanager",
      "https://console.test.example.dev/loginsso/clustermanager",
      "https://console.staging.example.dev/loginsso/clustermanager",
    ],
  },
};
```

#### **Configuration Breakdown**:

- **`VITE_APP_RESTAPI_ENDPOINT`**: The base URL for the backend REST API.
- **`VITE_APP_KEYCLOAK_URL`**: URL for Keycloak Single Sign-On (SSO).
- **`VITE_APP_REALM`**: Specifies the realm for Keycloak authentication.
- **`VITE_APP_CLIENT_ID`**: Identifies the Keycloak client.
- **`O_AUTH_CLIENTS`**: Lists OAuth client redirect URLs for various environments.

---

### **Step 3: Run the Development Server**

Start the application in development mode for local testing and debugging:

```bash
npm run dev
```

The server will start with hot-reloading enabled, ensuring rapid feedback during development.

---

### **Step 4: Build for Production**

Create an optimized and minified build for production deployment:

```bash
npm run build
```

The static assets will be output to the `dist/` directory, ready for deployment.

---

### **Step 5: Containerize the Application**

You can deploy the application as a Docker container. Build the Docker image with:

```bash
docker build -t cluster-ui:latest /cluster-ui/
```

This creates a `cluster-ui:latest` image that can be deployed to any container orchestration platform.

---

## ✨ **Key Features**

1. **Development Mode**

   - Hot-reloading for quick local development and iteration.

2. **Production Build**

   - Minified static assets for fast loading and optimized performance.

3. **Dockerization**
   - Seamless containerization for streamlined deployment.

---

## 📖 **Additional Information**

- For troubleshooting, ensure your configurations in `config.js` are accurate and up-to-date.
- Ensure all environment variables and API URLs are accessible and valid in their respective environments.

---

Enjoy managing your clusters with the powerful and intuitive **Cluster UI**! 🚀
