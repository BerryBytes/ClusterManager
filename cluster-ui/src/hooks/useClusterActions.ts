import { useQueryClient, useMutation } from "@tanstack/react-query";
import { startCluster, deleteCluster, stopCluster } from "../services/clusterService";
import { useHistory } from "react-router-dom";
import { useSnackbar } from "notistack";

export const useStartClusterResponse = () => {
    const queryClient = useQueryClient()
    const { enqueueSnackbar } = useSnackbar();
    return useMutation({
        mutationFn: (arg: { id: string; token: string }) => {
            return startCluster(arg.id, arg.token || "");
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["clusterList"] });
            queryClient.invalidateQueries({ queryKey: ["clusterDetails"] });
            enqueueSnackbar("Start command sent !", { variant: 'success' })
        },
        onError: (error:any) => {
            enqueueSnackbar(error.response.data.detail||"Failed to start cluster !", { variant: 'error' })
        },
    });
}

export const useDeleteClusterResponse = () => {
    const history = useHistory()
    const { enqueueSnackbar } = useSnackbar();
    const queryClient = useQueryClient()
    return useMutation({
        mutationFn: (arg: { id: string; token: string }) => {
            return deleteCluster(arg.id, arg.token || "");
        },
        onSuccess: () => {
            history.push("/");
            queryClient.invalidateQueries({ queryKey: ["clusterList"] });
            enqueueSnackbar("Delete cluster command sent !", { variant: 'success' })
        },
        onError: (error:any) => {
            enqueueSnackbar(error.response.data.detail||"Failed to delete cluster !", { variant: 'error' })

        },
    });

}

export const useStopClusterResponse = () => {
    const queryClient = useQueryClient()
    const { enqueueSnackbar } = useSnackbar();

    return useMutation({
        mutationFn: (arg: { id: string; token: string }) => {
            return stopCluster(arg.id, arg.token || "");
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["clusterList"] });
            queryClient.invalidateQueries({ queryKey: ["clusterDetails"] });
            enqueueSnackbar("Stop command sent !", { variant: 'success' })
        },
        onError: (error:any) => {

            enqueueSnackbar(error.response.data.detail||"Failed to delete cluster !", { variant: 'error' })
        },
    });
}