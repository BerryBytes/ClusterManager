import Axios, { AxiosResponse } from "axios";
import { Endpoints } from '../constants/endpoints';
import { getAuthHeaderConfig } from "./utils";
import { I_clusterversion } from "../models/clusters";

export const fetchClusterList = <T>(
    token: string
): Promise<AxiosResponse<T>> => {
    return Axios.get<T, AxiosResponse<T>>(
        Endpoints.CLUSTER.GET_CLUSTERS,
        getAuthHeaderConfig(token)
    );
};
export const fetchClusterById = <T>(
    id: string,
    token: string
): Promise<AxiosResponse<T>> => {
    return Axios.get<T, AxiosResponse<T>>(
        Endpoints.CLUSTER.GET_CLUSTER_BY_ID + id,
        getAuthHeaderConfig(token)
    );
};

export const generateKubeconfig = <T>(
    payload: any,
    token: string
): Promise<AxiosResponse<T>> => {
    return Axios.post<T, AxiosResponse<T>>(
        Endpoints.CLUSTER.DOWNLOAD_KUBECONFIG,
        payload,
        getAuthHeaderConfig(token)
    );
};

export const fetchSubscription = <T>(): Promise<AxiosResponse<T>> => {
    return Axios.get<T, AxiosResponse<T>>(
        Endpoints.SUBSCRIPTION.GET_SUBSCRIPTIONS,
        getAuthHeaderConfig()
    );
};

export const checkSubscription = <T>(token: string): Promise<AxiosResponse<T>> => {
    return Axios.get<T, AxiosResponse<T>>(
        Endpoints.SUBSCRIPTION.CHECK_SUBSCRIPTIONS,
        getAuthHeaderConfig(token)
    );
};

export const subsRequest = <T>(
    token: string
): Promise<AxiosResponse<T>> => {
    return Axios.post<T, AxiosResponse<T>>(
        Endpoints.SUBSCRIPTION.REQ_SUBSCRIPTIONS,
        null,
        getAuthHeaderConfig(token)
    );
};

export const deleteCluster = <T>(
    id: string,
    token: string
): Promise<AxiosResponse<T>> => {
    return Axios.delete<T, AxiosResponse<T>>(
        Endpoints.CLUSTER.DELETE_CLUSTER + `${id}`,
        getAuthHeaderConfig(token)
    );
};

export const startCluster = <T>(
    id: string,
    token: string
): Promise<AxiosResponse<T>> => {
    return Axios.patch<T, AxiosResponse<T>>(
        Endpoints.CLUSTER.START_CLUSTER + `${id}/start`,
        null,
        getAuthHeaderConfig(token)
    );
};

export const stopCluster = <T>(
    id: string,
    token: string
): Promise<AxiosResponse<T>> => {
    return Axios.patch<T, AxiosResponse<T>>(
        Endpoints.CLUSTER.STOP_CLUSTER + `${id}/stop`,
        null,
        getAuthHeaderConfig(token)
    );
};


export const createCluster = <T>(
    payload: any,
    token: string
): Promise<AxiosResponse<T>> => {
    return Axios.post<T, AxiosResponse<T>>(
        Endpoints.CLUSTER.CREATE_CLISTER,
        payload,
        getAuthHeaderConfig(token)
    );
};


export const fetchHostClusterList = <T>(
    token: string
): Promise<AxiosResponse<T>> => {
    return Axios.get<T, AxiosResponse<T>>(
        Endpoints.HOST_CLUSTER.GET_HOST_CLUSTER_LIST,
        getAuthHeaderConfig(token)
    );
};

export const fetchClusterVersions = <T>(
    token: string
): Promise<AxiosResponse<T>> => {
    return Axios.get<T, AxiosResponse<T>>(
        Endpoints.CLUSTER.GET_CLUSTER_VERSIONS,
        getAuthHeaderConfig(token)
    );
};

export const updateClusterVersion = <T>(
    id: string,
    payload: Pick< I_clusterversion, "kube_version">,
    token: string
): Promise<AxiosResponse<T>> => {
    return Axios.put<T, AxiosResponse<T>>(
        Endpoints.CLUSTER.UPDATE_CLUSTER_VERSION.replace(':id', id),
        payload,
        getAuthHeaderConfig(token)
    );
};
