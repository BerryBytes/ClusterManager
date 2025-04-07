import {
  Paper,
  Typography,
  Box,
  Button,
  Menu,
  MenuItem,
  CircularProgress,
  Autocomplete,
  TextField,
} from "@mui/material";
import CommonDialog from "../../factoryComponents/commonDialog/commonDialog";
import DownloadDialog from "../../factoryComponents/downloadDialog/downloadDialog";
import RestartAltIcon from "@mui/icons-material/RestartAlt";
import StopCircleIcon from "@mui/icons-material/StopCircle";
import { StatusColorHelper } from "../../../helpers/commonHelper";
import CloudDownloadIcon from "@mui/icons-material/CloudDownload";
import DeleteIcon from "@mui/icons-material/Delete";
import { I_cluster } from "../../../models/clusters";
import { useEffect, useState } from "react";
import { useKeycloak } from "@react-keycloak/web";
import { useKubeConfigDownload } from "../../../hooks/useKubeConfigDownload";
import {
  useDeleteClusterResponse,
  useStartClusterResponse,
  useStopClusterResponse,
} from "../../../hooks/useClusterActions";
import { useClusterVersionList, useUpdateClusterVersion } from "../../../hooks/useClusterVersionList";
import { useSubscriptionCheck } from "../../../hooks/useSubscriptionsResponse";
import { I_clusterversion } from "../../../models/clusters";
import { useParams } from "react-router-dom";
import { WebsocketConnection } from "../../../container/WebsocketConnection";
interface I_props {
  clusterDetails: I_cluster;
}

export const ClusterActionArea = ({ clusterDetails }: I_props) => {
  const [clusterVersion, setClusterVersion] = useState<I_clusterversion | null>(null);
  const [openDownloadDialog, setOpenDownloadDialog] = useState(false);
  const { keycloak } = useKeycloak();
  const { clusterStatus } = WebsocketConnection();
  const { data: clusterVersionData } =
    useClusterVersionList(keycloak.token || "");
  const { data: subscriptionCheck } = useSubscriptionCheck(
    keycloak.token || ""
  )
  const userPermission =
    subscriptionCheck && subscriptionCheck.data && subscriptionCheck.data.data.user_groups.length > 0
      ? subscriptionCheck.data.data.user_groups[0].name
      : "";

  const { mutateAsync: startClusterAsync, isLoading: isStartLoading } =
    useStartClusterResponse();

  const { mutateAsync: deleteClusterAsync, isLoading: isDeleteLoading } =
    useDeleteClusterResponse();

  const { mutateAsync: stopClusterAsync, isLoading: isStopLoading } =
    useStopClusterResponse();

  const {
    mutateAsync: downloadConfigAsync,
    isLoading: isDownloadConfigLoading,
  } = useKubeConfigDownload();

  const { mutateAsync: updateClusterVersionAsync }=useUpdateClusterVersion();
  const params=useParams<{id:string}>();

  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    setOpen(Boolean(anchorEl));
  }, [anchorEl]);

  const handleActions = (e: React.MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(e.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
    setOpen(false);
  };


  const handleStartDialogSubmit = async () => {
    startClusterAsync({ id: clusterDetails.id, token: keycloak.token || "" });
  };

  const handleStopDialogSubmit = async () => {
    stopClusterAsync({ id: clusterDetails.id, token: keycloak.token || "" });
  };
  const handleDeleteDialogSubmit = async () => {
    deleteClusterAsync({ id: clusterDetails.id, token: keycloak.token || "" });
  };

  const handleClickOnDownloadConfig = async (expirationTime: string) => {
    const data = {
      expiryTime: expirationTime,
      clusterId: clusterDetails.id,
    };
    // Close the dialog
    await downloadConfigAsync({ data, token: keycloak.token || "" });
    setOpenDownloadDialog(false);
    // Make the API call using fetch
  };

  const handleCloseDownloadDialog = () => {
    setOpenDownloadDialog(false);
  };

  const handleDownloadKubeConfigDialogOpen = () => {
    handleClose();
    setOpenDownloadDialog(true);
  };

  const isActionLoading = () => {
    return isDeleteLoading || isStartLoading || isStopLoading;
  };

  const handleUpdateClusterVersion = async (clusterDetails:I_clusterversion) => {
    if(!clusterDetails || !params.id) return;

    try {
      await updateClusterVersionAsync({id:params.id,cluster:{kube_version:clusterDetails.kube_version}});
     
    } catch (error) {
      console.log(error);
      
    }

  }
  useEffect(() => {
    if (clusterVersionData && clusterVersionData.data) {
      const clusterVersion = clusterVersionData.data.data.find((cluster: I_clusterversion) => {
        return cluster.active && clusterDetails.kube_version === cluster.kube_version
      })

      if (!clusterVersion) return

      setClusterVersion(clusterVersion)
    }
  }, [clusterVersionData, clusterDetails]);

  console.log("cluster version", clusterVersion);

  const currentClusterStatus = clusterStatus.find(
    (statusObj) => statusObj.clusterId === clusterDetails.id
  )?.status || 'Pending';

  return (
    <>
      <Paper
        elevation={0}
        sx={{
          padding: "1.5em",
          display: "flex",
          background: "transparent",
          justifyContent: "space-between",
          flexWrap: "wrap",
          gap: 5,
        }}
      >
        <Box
          component="div"
          sx={{ display: "flex", alignItems: "center", gap: 5 }}
        >
          <Typography variant="h5" sx={{ color: "#0057fa" }}>
            {clusterDetails.name}
          </Typography>
          <Typography
            variant="h5"
            sx={{ color: StatusColorHelper(currentClusterStatus) }}
          >
            {currentClusterStatus}
          </Typography>
        </Box>
        <Box component={"p"}>
          {isDownloadConfigLoading ? (
            <Typography variant="subtitle1">
              Getting your download. Please be patient...
            </Typography>
          ) : null}{" "}
        </Box>

        <Box component="div" display={"flex"} gap={1} alignItems={"center"} flexWrap={"wrap"}>
          <Autocomplete
            disablePortal
            id="subscription-box-version"
            options={(clusterVersionData?.data.data || []).sort((a, b) => (a.kube_version.slice(1) > b.kube_version.slice(1) ? 1 : -1))}
            getOptionLabel={(option) => option.name}
            renderInput={(params) => (
              <TextField variant="outlined" {...params} label="Version" />
            )}
            getOptionDisabled={(option) => option.kube_version.slice(1) <= clusterDetails.kube_version.slice(1)}
            sx={{ width: 300 }}
            isOptionEqualToValue={(option, value) => (option.name === value.name)|| !option.active}
            value={clusterVersion}
            onChange={(_event, newValue) =>{
              if(!newValue) return
              setClusterVersion(newValue)
              handleUpdateClusterVersion(newValue)
            }

            }
            disabled={userPermission === "approved-user" ? false : true}
          />
          <Button
            sx={{
              paddingLeft: "2.5em",
              paddingRight: "2.5em",
              paddingTop: "1em",
              paddingBottom: "1em",
            }}
            disableElevation={true}
            variant="contained"
            disabled={isActionLoading()}
            onClick={handleActions}
          >
            {isActionLoading() ? (
              <CircularProgress size={20} sx={{ color: "#0057fa" }} />
            ) : (
              "Actions"
            )}
          </Button>
          <Menu
            id="basic-menu"
            anchorEl={anchorEl}
            open={open}
            onClose={handleClose}
            MenuListProps={{
              "aria-labelledby": "basic-button",
            }}
          >
            {clusterDetails &&
              currentClusterStatus.toLowerCase() === "stopped" ? (
              <CommonDialog
                icon={<RestartAltIcon />}
                buttonText="Start"
                title="Are you sure ?"
                action="start"
                contentText={clusterDetails.name}
                submitText="I UNDERSTAND, START THIS CLUSTER"
                onSubmit={handleStartDialogSubmit}
              />
            ) : null}

            {clusterDetails && currentClusterStatus === "Running" ? (
              <CommonDialog
                icon={<StopCircleIcon />}
                buttonText="Stop"
                title="Are you sure ?"
                action="stop"
                contentText={clusterDetails?.name}
                submitText="I UNDERSTAND, STOP THIS CLUSTER"
                onSubmit={handleStopDialogSubmit}
              />
            ) : null}

            {clusterDetails != null && clusterDetails.status === "Running" ? (
              <>
                <MenuItem onClick={handleDownloadKubeConfigDialogOpen}>
                  <Box sx={{ color: "#0057fa", mr: "1.25em" }} component="span">
                    <CloudDownloadIcon />
                  </Box>
                  <Typography variant="subtitle1" sx={{ color: "#0057fa" }}>
                    Download
                  </Typography>
                </MenuItem>
              </>
            ) : (
              <></>
            )}
            {/* CloudDownloadIcon */}
            <CommonDialog
              icon={<DeleteIcon />}
              buttonText="Delete"
              title="Are you sure ?"
              contentText={clusterDetails.name}
              action="delete"
              submitText="I UNDERSTAND, DELETE THIS CLUSTER"
              onSubmit={handleDeleteDialogSubmit}
            />
          </Menu>
          <DownloadDialog
            isConfigDownloading={isDownloadConfigLoading}
            open={openDownloadDialog}
            handleClose={handleCloseDownloadDialog}
            handleClickOnDownloadConfig={handleClickOnDownloadConfig}
          />
        </Box>
      </Paper>
    </>
  );
};
