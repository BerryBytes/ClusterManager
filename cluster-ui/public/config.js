window.config = {
    VITE_APP_RESTAPI_ENDPOINT: "https://domain_example.com/v1",
    VITE_APP_KEYCLOAK_URL: "https://sso.keycloak.com/",
    VITE_APP_REALM: "example",
    VITE_APP_CLIENT_ID: "exampleclient",
    O_AUTH_CLIENTS:{
        "01cloud":["https://console.example.io/loginsso/clustermanager","https://console.test.example.dev/loginsso/clustermanager","https://console.staging.example.dev/loginsso/clustermanager"]
    },
    VITE_APP_WEBSOCKET_CONNECTION_URL : "wss://example.com/v1/websocket"
}
