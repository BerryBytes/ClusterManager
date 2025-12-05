import { TableVirtuoso } from "react-virtuoso";
import { rowContent, fixedHeaderContent } from "./tableContents.utils";
import { createData } from "./table.utils";
import { Data } from "./table";
import { VirtuosoTableComponents } from "./tableContents.utils";
import { useKeycloak } from "@react-keycloak/web";
import { useEffect, useState } from "react";
import { I_cluster } from "../../../models/clusters";
import DownloadDialog from "../../factoryComponents/downloadDialog/downloadDialog";
import { CloudDownload } from "@mui/icons-material";
import { Button, Typography, Box } from "@mui/material";
import { useHistory } from "react-router-dom";
import { StatusColorHelper } from "../../../helpers/commonHelper";
import { formatDate } from "./table.utils";
import { useClusterListResponse } from "../../../hooks/useClusterListResponse";
import { useKubeConfigDownload } from "../../../hooks/useKubeConfigDownload";
import { useQueryClient } from "@tanstack/react-query";
import { useWebsocketConnection } from "../../../container/WebsocketConnection";

export const ClusterList = () => {
  const { keycloak } = useKeycloak();
  const queryClient = useQueryClient();
  const { clusterStatus } = useWebsocketConnection();
  const {
    isError: isClusterListError,
    data: clusterListData,
    ...rest
  } = useClusterListResponse(keycloak.token || "");

  const {
    mutateAsync: downloadConfigAsync,
    isLoading: isDownloadConfigLoading,
  } = useKubeConfigDownload();

  const [rows, setRows] = useState<Data[]>([]);
  const [openDownloadDialog, setOpenDownloadDialog] = useState(false);
  const [activeClusterId, setActiveClusterId] = useState("");

  const history = useHistory();
  const gotoClusterDetails = (id: string) => () => {
    history.push(`/cluster/${id}`);
  };

  useEffect(() => {
    if (clusterListData && clusterListData.data.data.length) {
      setRows(() => {
        const newRows = clusterListData.data.data.map(
          (cluster: I_cluster, clusterIndex: number) => {
            const currentClusterStatus = clusterStatus.find(
              (statusObj) => statusObj.clusterId === cluster.id
            )?.status || 'Pending';
            return createData(
              <Typography variant="subtitle1">{cluster.id}</Typography>,
              <Typography variant="subtitle1">{clusterIndex + 1}</Typography>,
              <Typography
                onClick={gotoClusterDetails(cluster.id)}
                variant="subtitle1"
                sx={{
                  fontWeight: "bold",
                  "&:hover": {
                    cursor: "pointer", // Change the cursor to pointer on hover
                  },
                }}
              >
                {cluster.name}
              </Typography>,
              <Typography variant="subtitle1">
                {formatDate(cluster.created.toString())}
              </Typography>,

              <Typography variant="subtitle1">
                {cluster.hostCluster.region}
              </Typography>,
              <Typography
                variant="subtitle1"
                sx={{ textTransform: "capitalize" }}
              >
                {cluster.subscription.name}
              </Typography>,
              <Typography
                sx={{ color: StatusColorHelper(currentClusterStatus) }}
                variant="subtitle1"
              >
                {currentClusterStatus}
              </Typography>,
              <Button variant="outlined">Actions</Button>,
              currentClusterStatus === "Running" ? (
                <CloudDownload
                  onClick={() => handleOpen(cluster)}
                  style={{ cursor: "pointer" }}
                  color="primary"
                />
              ) : (
                <></>
              )
            );
          }
        );

        return newRows;
      });
    }
  }, [clusterListData, clusterStatus]);

  const handleClickOnDownloadConfig = async (expirationTime: string) => {
    const data = {
      expiryTime: expirationTime,
      clusterId: activeClusterId,
    };
    // Close the dialog
    await downloadConfigAsync({ data, token: keycloak.token || "" });
    setOpenDownloadDialog(false);
    // Make the API call using fetch
  };

  const handleCloseDownloadDialog = () => {
    setOpenDownloadDialog(false);
  };

  const handleOpen = (cluster: I_cluster) => {
    setActiveClusterId(cluster.id);
    setOpenDownloadDialog(true);
  };

  const refreshClusterList = () => {
    queryClient.invalidateQueries({ queryKey: ["clusterList"] });
  };

  if (rest.fetchStatus === "fetching")
    return (
      <Box sx={{ height: 100, padding: 10 }}>
        <Typography variant="h5" align="center">
          Getting your data please wait...
        </Typography>
      </Box>
    );
  if (isClusterListError)
    return (
      <Box sx={{ height: 100, padding: 10 }}>
        <Typography variant="h5" align="center">
          Something went wrong. Plese retry...
        </Typography>
      </Box>
    );
  return (
    <Box component={'div'}>
      <Box sx={{ display: "flex", justifyContent: "space-between" }}>
        <Box component={"span"} sx={{ my: 2 }}>
          <Typography variant="h5">Your Clusters</Typography>
        </Box>
        <Button
          sx={{ my: 1 }}
          onClick={refreshClusterList}
          variant="contained"
          disableElevation={true}
        >
          Refresh
        </Button>
      </Box>

      <Box component={'div'} sx={{ width: "100%", height: 600 }}>
        <TableVirtuoso
          data={rows}
          components={VirtuosoTableComponents}
          fixedHeaderContent={fixedHeaderContent}
          itemContent={rowContent}
        />
        <DownloadDialog
        isConfigDownloading={isDownloadConfigLoading}
          open={openDownloadDialog}
          handleClose={handleCloseDownloadDialog}
          handleClickOnDownloadConfig={handleClickOnDownloadConfig}
        />

      </Box >
  </Box>
  );
};
