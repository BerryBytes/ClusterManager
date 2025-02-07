import { useQuery } from "@tanstack/react-query";
import { checkSubscription, fetchSubscription, subsRequest } from "../services/clusterService";
import {I_get_subscriptions_response, I_subscription_check_response } from "../models/subscriptions";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useSnackbar } from "notistack";

export const useSubscriptionsResponse=()=>{
    return  useQuery({
        queryKey: ["subscriptions"],
        queryFn: fetchSubscription<I_get_subscriptions_response>,
      });
}

export const useSubscriptionCheck = (token: string) => {
  return  useQuery({
    queryKey: ["subscriptionCheck"],
    queryFn: () => {
      return checkSubscription<I_subscription_check_response>(token)
    }
  })
}

export const useSubscriptionReq = () => {
  const queryClient = useQueryClient()
  const { enqueueSnackbar } = useSnackbar();

  return useMutation({
    mutationFn: (arg: {token: string }) => {
      return subsRequest(arg.token);
    },
    onSuccess: () => {
      queryClient.invalidateQueries([`subscriptionCheck`]);
      enqueueSnackbar("Subscription requested successfully !", { variant: 'success' })
    },
    onError: (error:any) => {
      enqueueSnackbar(error.response.data.detail||"Subscription requested failed !", { variant: "error" })
    },
  });
}