
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createCluster } from "../services/clusterService";
import { useSnackbar } from "notistack";

export const useCreateClusterResponse = () => {
  const queryClient = useQueryClient()
  const { enqueueSnackbar } = useSnackbar();

  return useMutation({
    mutationFn: (arg: { payload: any; token: string }) => {
      return createCluster(arg.payload, arg.token);
    },
    onSuccess: () => {
      queryClient.invalidateQueries([`clusterList`]);
      enqueueSnackbar("Cluster created successfully !", { variant: 'success' })
    },
    onError: (error:any) => {
      enqueueSnackbar(error.response.data.detail||"Cluster creation failed !", { variant: "error" })
    },
  });
}
