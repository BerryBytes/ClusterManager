import { useEffect } from "react";
import { makeStyles } from "@mui/styles";
import {
  Grid,
  Typography,
  TextField,
  Autocomplete,
  Button,
  CircularProgress,
  Alert,
  Stack,
} from "@mui/material";
import { I_subscription } from "../../../models/subscriptions";
import {  useState } from "react";
import { useKeycloak } from "@react-keycloak/web";
import {
  useSubscriptionCheck,
  useSubscriptionReq,
  useSubscriptionsResponse,
} from "../../../hooks/useSubscriptionsResponse";
import { useCreateClusterResponse } from "../../../hooks/useCreateClusterResponse";
import { useHostClusterListResponse } from "../../../hooks/useHostClusterListResponse";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";
import { useClusterVersionList } from "../../../hooks/useClusterVersionList";

const useStyles = makeStyles(() => ({
  root: {
    display: "flex",
    flexDirection: "column",
    gap: 10,
  },
  alert: {
    marginTop: 10,
    width: "50%",
  },
}));

const getSortedVersions = (versions: string[]): string[] => {
  return versions.sort((a, b) => (a > b ? -1 : 1));
};

export const CreateClusterSection = () => {
  const { keycloak } = useKeycloak();

  const [subscriptionPlan, setSubscriptionPlan] =
    useState<I_subscription | null>(null);

  const [subsCheck, setSubsCheck] = useState<any>(null);

  const [clusterRegion, setClusterRegion] = useState<{
    region: string;
  }>({ region: "" });
  const [clusterName, setClusterName] = useState<string>("");
  const [createError, setCreateError] = useState<string>("");
  const [openPopup, setOpenPopup] = useState<boolean>(false);
  const [clusterVersion, setClusterVersion] = useState<string | null>(null);
  const [clusterVersionList, setClusterVersionList] = useState<string[]>([])
const [userPermission, setUserPermission] = useState<string>("");
  const classes = useStyles();


  useEffect(() => {
 if(!subsCheck) return;
if(subsCheck.user_groups.length === 0) return
 setUserPermission(subsCheck.user_groups[0].name)
  }, [subsCheck]);

  // const userPermission =
  //   subsCheck && subsCheck.user_groups?.length > 0
  //     ? subsCheck.user_groups[0].name
  //     : "";

  // queries
  const { mutateAsync, isLoading } = useCreateClusterResponse();
  const { data: subscriptionCheck } = useSubscriptionCheck(
    keycloak.token || ""
  )

  const { mutateAsync: subsReqAsync } = useSubscriptionReq();

  const { data: subscriptionData, ...restOfSubscriptionResponse } =
    useSubscriptionsResponse();

  const { data: hostClustersData, ...restOfHostClusterResponse } =
    useHostClusterListResponse(keycloak.token || "");
  // store

  const { data: clusterVersionData, ...restOfClusterVersionResponse } =
    useClusterVersionList(keycloak.token || "");


  useEffect(() => {
    if (!subscriptionCheck) return;
    setSubsCheck(subscriptionCheck.data.data || []);
  }, [subscriptionCheck]);

  const handleCreateCluster = async () => {
    if (!validateClusterName(clusterName)) return;
    if (!subscriptionPlan || !clusterRegion) {
      setCreateError("Please fill in all required fields.");
      return;
    }
    if (!keycloak.authenticated) {
      keycloak.login();
      return;
    }
    setCreateError("");
    const clusterData = {
      name: clusterName,
      subscription_id: subscriptionPlan?._id || "",
      region: clusterRegion?.region || "",
      kube_version: clusterVersion || ""
    };
    if (!keycloak.token) return;
    await mutateAsync({ payload: clusterData, token: keycloak.token });
  };

  const handleReqSubscription = () => {
    setOpenPopup(true);
  };

  const handleClose = () => {
    setOpenPopup(false);
  };

  const handleApproveSubs = async () => {
    if (!keycloak.token) return;
    await subsReqAsync({ token: keycloak.token });
    handleClose();
  };

  const capitalize = (word: string) => {
    return word[0].toUpperCase() + word.slice(1);
  };

  const validateClusterName = (name: string) => {
    // Validation check for symbols and numeric values
    const symbolCheck = /[_&.@#*^%$!~]/;
    const numericStartCheck = /^[0-9]/;
    const hyphenStartCheck = /^-/;

    if (
      name &&
      !symbolCheck.test(name) &&
      !numericStartCheck.test(name) &&
      !hyphenStartCheck.test(name)
    ) {
      return true;
    }

    setCreateError("Cluster name is not valid.");
    return false;
  };

  const handleChange = (
    e: React.ChangeEvent<HTMLTextAreaElement | HTMLInputElement>
  ) => {
    if (createError) {
      setCreateError("");
    }
    setClusterName(e.target.value);
  };

  useEffect(() => {
    const isClusterVersion = clusterVersionData?.data.data.map((e) => e?.kube_version);
    const sortedClusters = getSortedVersions(isClusterVersion || []);
    if (sortedClusters) {
        setClusterVersionList(sortedClusters);
    }
  }, [clusterVersionData]);

  useEffect(() => {
    if (clusterVersionList.length > 0) {
      setClusterVersion(clusterVersionList[0]);
    }
  }, [clusterVersionList]);
  

  return (
    <div className={classes.root}>
      <section>
        <Grid
          container
          spacing={2}
          alignItems="center"
          sx={{ marginBottom: "40px" }}
        >
          <Grid item md={6}>
            <Typography variant="h5" gutterBottom>
              Create New Cluster
            </Typography>
          </Grid>
          {subsCheck !== null && userPermission !== "approved-user" && (
            <Grid item md={6}>
              <Stack sx={{ width: "100%" }} spacing={2}>
                <Alert
                  variant="outlined"
                  severity="warning"
                  action={
                    subsCheck && subsCheck.user_groups?.length === 0 &&
                    <Button
                      variant="contained"
                      color="primary"
                      onClick={handleReqSubscription}
                    >
                      Request
                    </Button>
                  }
                >
                  {subsCheck && subsCheck.user_groups?.length > 0
                    ? 
                    "Your request has been received, waiting for admin approval"
                    : 
                    "You are not authorized to create cluster request for cluster creation"
                    }
                </Alert>
              </Stack>
            </Grid>
          )}
        </Grid>

        <div>
          <Grid container spacing={1}>
            <Grid item xs={12} md={4}>
              <TextField
                id="cluster-name"
                label="Cluster Name"
                variant="outlined"
                autoFocus={true}
                fullWidth={true}
                value={clusterName}
                onChange={handleChange}
                disabled={userPermission === "approved-user" ? false : true}
              />
            </Grid>

            <Grid item xs={12} md={2}>
              <Autocomplete
                disablePortal
                id="subscription-box-plan"
                options={subscriptionData?.data.data || []}
                getOptionLabel={(option) => capitalize(option.name)}
                renderInput={(params) => <TextField {...params} label="Plan" />}
                value={subscriptionPlan}
                onChange={(_event, newValue) =>
                  setSubscriptionPlan(newValue as I_subscription)
                }
                disabled={userPermission === "approved-user" ? false : true}
              />
            </Grid>

            <Grid item xs={12} md={2}>
              <Autocomplete
                disablePortal
                id="combo-box-region"
                options={hostClustersData?.data.data || []}
                getOptionLabel={(option) => option.region}
                renderInput={(params) => (
                  <TextField {...params} label="Location" />
                )}
                value={clusterRegion}
                onChange={(_event, newValue) =>
                  setClusterRegion(
                    newValue as {
                      region: string;
                    }
                  )
                }
                disabled={userPermission === "approved-user" ? false : true}
              />
            </Grid>

            <Grid item xs={12} md={2}>
              <Autocomplete
                disablePortal
                id="subscription-box-version"
                options={clusterVersionList || []}
                getOptionLabel={(option) => option}
                renderInput={(params) => (
                  <TextField variant="outlined" {...params} label="Version" />
                )}
                value={clusterVersion}
                onChange={(_event, newValue) =>
                  setClusterVersion(newValue as string)
                }
                disabled={userPermission === "approved-user" ? false : true}
              />
            </Grid>

            <Grid item xs={12} md={2}>
              <Button
                variant="contained"
                style={{ height: "100%" }}
                onClick={handleCreateCluster}
                fullWidth={true}
                disabled={
                  !restOfHostClusterResponse.isSuccess ||
                  !restOfSubscriptionResponse.isSuccess ||
                  !restOfClusterVersionResponse.isSuccess||
                  userPermission !== "approved-user"
                }
                disableElevation={true}
              >
                {isLoading ? (
                  <CircularProgress size={25} style={{ color: "white" }} />
                ) : (
                  "Create Cluster "
                )}
              </Button>
            </Grid>
          </Grid>
        </div>

        {createError ? (
          <div className={classes.alert}>
            <Alert
              color="error"
              onClose={() => {
                setCreateError("");
              }}
            >
              <Typography variant="subtitle1">{createError}</Typography>
            </Alert>
          </div>
        ) : null}

        {openPopup && (
          <Dialog
            open={openPopup}
            onClose={handleClose}
            aria-labelledby="alert-dialog-title"
            aria-describedby="alert-dialog-description"
          >
            <DialogTitle id="alert-dialog-title">{"Are you sure ?"}</DialogTitle>
            <DialogContent>
              <DialogContentText id="alert-dialog-description">
                This cluster is created for trial purposes and may be deleted by the admin without prior notice to the cluster owner.
              </DialogContentText>
            </DialogContent>
            <DialogActions>
              <Button variant="contained" color="warning" onClick={handleClose}>
                cancel
              </Button>
              <Button variant="contained" onClick={handleApproveSubs} autoFocus>
                continue
              </Button>
            </DialogActions>
          </Dialog>
        )}
      </section>
    </div>
  );
};
