import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { fetchClusterVersions, updateClusterVersion } from "../services/clusterService";
import { I_cluster_version_list_response, I_clusterversion } from "../models/clusters";
import { useKeycloak } from "@react-keycloak/web";
import { useSnackbar } from "notistack";

export const useClusterVersionList = (token: string) => {

    return useQuery({
        queryKey: ["clusterVersionList", token],
        queryFn: () => {
            return fetchClusterVersions<I_cluster_version_list_response>(token);
        },
    });


}

export const useUpdateClusterVersion = () => {
    const queryClient = useQueryClient();
    const { keycloak } = useKeycloak();
    const { enqueueSnackbar } = useSnackbar();
    return useMutation({
        mutationFn: (arg: {
            id: string;
            cluster: Pick<I_clusterversion, "kube_version">
        }) => {
            return updateClusterVersion<I_clusterversion[]>(arg.id, arg.cluster, keycloak.token || "");
        },
        onSuccess: () => {
            queryClient.invalidateQueries(["clusterDetails"]);
        },
        onError: (error: any) => {
            console.log(error);
            enqueueSnackbar(error.response.data.detail[0].msg || "Failed to update cluster !", { variant: 'error' })

        },
    });
}
