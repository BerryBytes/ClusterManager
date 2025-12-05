import { I_api_list_response, I_api_response } from "./response";

export interface I_cluster {
    id:           string;
    name:         string;
    status:       string;
    user:         I_user;
    subscription: I_subscription;
    hostCluster:  I_hostcluster;
    created: Date;
    kube_version: string
}


export interface I_hostcluster {
    _id:      string;
    name:     string;
    region:   string;
    provider: string;
    nodes:    number;
    active:   boolean;
    version:  string;
    user_id:  string;
    created:  Date;
    updated:  Date;
}

export interface I_subscription {
    _id:                    string;
    name:                   string;
    pods:                   number;
    service:                number;
    config_map:             number;
    persistance_vol_claims: number;
    replication_ctl:        number;
    secrets:                number;
    loadbalancer:           number;
    node_port:              number;
    created:                Date;
    updated:                Date;
}

export interface I_user {
    _id:      string;
    name:     string;
    email:    string;
    userName: string;
}

export interface I_clusterversion {
    name: string,
    kube_version: string,
    _id: string,
    active: boolean
}

export interface I_cluster_version_list_response extends I_api_list_response{
    data: I_clusterversion[]
}

export interface I_cluster_details_response extends I_api_response{
    data: I_cluster
}

export interface I_get_cluster_list_response extends I_api_list_response{
    data: I_cluster[]
}


export interface I_get_host_cluster_list_response extends I_api_list_response{
    data: I_hostcluster[]
}
