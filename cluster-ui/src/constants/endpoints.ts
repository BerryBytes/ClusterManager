// const baseUrl = "http://localhost:8081/v1";

const baseUrl = (window as any).config.VITE_APP_RESTAPI_ENDPOINT;
const Endpoints = {
  CLUSTER: {
    CREATE_CLISTER: baseUrl + "/clusters",  // resource type
    GET_CLUSTER_BY_ID: baseUrl + "/clusters/", // resource type
    GET_CLUSTERS: baseUrl + "/clusters",  // collection type
    STOP_CLUSTER: baseUrl + "/clusters/",  // resource type
    START_CLUSTER: baseUrl + "/clusters/",  // resource type
    DOWNLOAD_KUBECONFIG: baseUrl + "/clusters/generate-config",  // resource type
    DELETE_CLUSTER: baseUrl + "/clusters/",  // resource type
    GET_CLUSTER_VERSIONS: baseUrl + "/kubeversion/", // collection type
    UPDATE_CLUSTER_VERSION: baseUrl + "/clusters/upgrade/:id", // resource type
  },
  SUBSCRIPTION: {
    GET_SUBSCRIPTIONS: baseUrl + "/public/subscriptions", // collection type
    CHECK_SUBSCRIPTIONS: baseUrl + "/users/subscription-check", // resource type
    REQ_SUBSCRIPTIONS: baseUrl + "/users/subscription-request",  // resource type
  },
  HOST_CLUSTER:{
    GET_HOST_CLUSTER_LIST: baseUrl+'/host-clusters/' // collection type
  }
};


export { Endpoints };
