import { useQuery } from "@tanstack/react-query";
import { fetchClusterList } from "../services/clusterService";
import { I_get_cluster_list_response } from "../models/clusters";

export const useClusterListResponse = (token: string) => {

    return useQuery({
        queryKey: ["clusterList",token],
        queryFn: () => {
            return fetchClusterList<I_get_cluster_list_response>(token);
        },
    });


}
