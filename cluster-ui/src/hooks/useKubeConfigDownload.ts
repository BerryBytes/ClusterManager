import { useMutation } from "@tanstack/react-query";
import { generateKubeconfig } from "../services/clusterService";
import { useSnackbar } from "notistack";
interface I_data {
  expiryTime: string;
  clusterId: string;
}
export const useKubeConfigDownload = () => {
  const { enqueueSnackbar } = useSnackbar()

  return useMutation({
    mutationFn: (arg: { data: I_data; token: string }) => {
      return generateKubeconfig(arg.data, arg.token || "");
    },
    onSuccess: (response: any) => {
      // Get the content from the response
      const fileContent = response.data; // Assuming the file content is in the "data" field of the response.

      // Create a Blob with the file content
      const blob = new Blob([fileContent], { type: "application/x-yaml" });

      // Create a URL for the Blob
      const fileURL = URL.createObjectURL(blob);

      // Create a temporary link and click it to trigger the download
      const downloadLink = document.createElement("a");
      downloadLink.href = fileURL;
      downloadLink.download = "kubeconfig.yaml"; // Set the desired file name
      downloadLink.click();

      // Clean up the URL and link
      URL.revokeObjectURL(fileURL);
      enqueueSnackbar("Config generated !",{variant:'success'})
    },
    onError: () => {
      enqueueSnackbar("Failed to generate config !", { variant: 'error' })
    },
  })

}