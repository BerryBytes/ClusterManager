
import { useQuery } from "@tanstack/react-query";
import { fetchClusterById } from "../services/clusterService";
import {  I_cluster_details_response } from "../models/clusters";

export const useClusterDetailsResponse=(id:string,token:string)=>{
    return useQuery({
        queryKey: ["clusterDetails",id,token],
        queryFn: () => {
          return fetchClusterById<I_cluster_details_response>(id, token);
        },
      });
}
