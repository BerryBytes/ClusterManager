import Keycloak from 'keycloak-js';
const config=(window as any).config
const keycloakConfig = {
  url: config.VITE_APP_KEYCLOAK_URL,
  realm: config.VITE_APP_REALM,
  clientId:config.VITE_APP_CLIENT_ID,
};

const keycloak = new Keycloak(keycloakConfig);

export default keycloak;
