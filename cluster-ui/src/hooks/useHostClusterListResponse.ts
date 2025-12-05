import { useQuery } from "@tanstack/react-query";
import { fetchHostClusterList } from "../services/clusterService";
import { I_get_host_cluster_list_response} from "../models/clusters";
export const useHostClusterListResponse = (token: string) => {
    return useQuery({
        queryKey: ["hostClusterList",token],
        queryFn: () => {
            return fetchHostClusterList<I_get_host_cluster_list_response>(token);
        },
    });

}
