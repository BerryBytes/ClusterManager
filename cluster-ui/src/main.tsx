import ReactDOM from "react-dom/client";
import { App } from "./app.tsx";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import "./index.css";

import { ReactKeycloakProvider } from "@react-keycloak/web";
import keycloak from "./services/keycloak.tsx";
import { ThemeProvider } from "@mui/material";
import { theme } from "./theme/index.tsx";
import { SnackbarProvider } from "notistack";
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false, // default: true
    },
  },
});

const rootElement = document.getElementById("root");

if (rootElement) {
  ReactDOM.createRoot(rootElement).render(
    <>
      <ReactKeycloakProvider authClient={keycloak}>
        <QueryClientProvider client={queryClient}>
          <ThemeProvider theme={theme}>
            <SnackbarProvider
              anchorOrigin={{
                vertical: "top",
                horizontal: "right",
              }}
            >
              <App />
            </SnackbarProvider>
          </ThemeProvider>
        </QueryClientProvider>
      </ReactKeycloakProvider>
    </>
  );
} else {
  console.error("Root element not found");
}
