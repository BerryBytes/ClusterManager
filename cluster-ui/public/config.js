window.config = {
    VITE_APP_RESTAPI_ENDPOINT: "https://zerone-4409-9534.01cloud.com/v1",
    VITE_APP_KEYCLOAK_URL: "https://sso.01cloud.dev",
    VITE_APP_REALM: "clusterManager",
    VITE_APP_CLIENT_ID: "clustermanagerclient",
    O_AUTH_CLIENTS:{
        "01cloud":["https://console.01cloud.io/loginsso/clustermanager","https://console.test.01cloud.dev/loginsso/clustermanager","https://console.staging.01cloud.dev/loginsso/clustermanager"]
    },
    VITE_APP_WEBSOCKET_CONNECTION_URL : "wss://zerone-4409-9534.01cloud.com/v1/websocket"
}