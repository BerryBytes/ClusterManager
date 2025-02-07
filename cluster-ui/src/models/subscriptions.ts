
import {I_api_response} from "./response";
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

// Converts JSON strings to/from your types
// and asserts the results of JSON.parse at runtime

export interface I_subscriptioncheck {
    status: any;
    user_id: string;
    username: string;
    email: string,
    user_groups: [
      {
        id: string,
        name: string,
        path: string
      }
    ],
    realm_roles: any
}

export interface I_get_subscriptions_response  extends I_api_response{
  
  data:I_subscription[];


}
export interface I_subscription_check_response  extends I_api_response{
  
  data:I_subscriptioncheck;
}