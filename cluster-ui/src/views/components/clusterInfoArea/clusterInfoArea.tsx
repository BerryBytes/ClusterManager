import { I_cluster } from "../../../models/clusters";
import {
  Box,
  Grid,
  Card,
  CardHeader,
  CardContent,
  Typography,
} from "@mui/material";

interface I_props {
  clusterDetails: I_cluster;
}



export const ClusterInfoArea = ({ clusterDetails }: I_props) => {
  console.log(clusterDetails);
  return (
  <>
    <Box>
      <Grid container justifyContent={"center"} sx={{width:'100%'}} spacing={4}>
        <Grid   sx={{width:'100%'}}item xs={12} md={6}>
          <Card sx={{ height: "auto", boxShadow: "none", padding: 1,width:'100%' }}>
            <CardHeader
              title={
                <Typography variant="h5"  sx={{ color: "#0057fa" }}>
                  Cluster Details
                </Typography>
              }
            />
            <CardContent>
              <Box
                component={"div"}
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  gap:2
                  
                }}
              >
                <Typography gutterBottom variant="h6" sx={{mb:"1em"}}>
                  Name
                </Typography>
                <Typography gutterBottom variant="h6" sx={{mb:"1em"}} color="text.secondary">
                  {clusterDetails.name}
                </Typography>
              </Box>
              <Box
                component={"div"}
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <Typography gutterBottom variant="h6" sx={{mb:"1em"}}>
                  Created By
                </Typography>
                <Typography gutterBottom variant="h6" sx={{mb:"1em"}} color="text.secondary">
                  {clusterDetails.user.name}
                </Typography>
              </Box>

              <Box
                component={"div"}
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <Typography gutterBottom variant="h6" sx={{mb:"1em"}}>
                  Region
                </Typography>
                <Typography gutterBottom variant="h6" sx={{mb:"1em"}} color="text.secondary">
                  {clusterDetails.hostCluster.region}
                </Typography>
              </Box>
              <Box
                component={"div"}
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <Typography gutterBottom variant="h6" sx={{mb:"1em"}}>
                  Plan
                </Typography>
                <Typography gutterBottom variant="h6" sx={{mb:"1em"}} color="text.secondary">
                  {clusterDetails.subscription.name}
                </Typography>
              </Box>
              <Box
                component={"div"}
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <Typography gutterBottom variant="h6" sx={{mb:"1em"}}>
                  Version
                </Typography>
                <Typography gutterBottom variant="h6" sx={{mb:"1em"}} color="text.secondary">
                  {clusterDetails.kube_version}
                </Typography>
              </Box>
              <Box
                component={"div"}
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <Typography gutterBottom variant="h6" sx={{mb:"1em"}}>
                  Provider
                </Typography>
                <Typography gutterBottom variant="h6" sx={{mb:"1em"}} color="text.secondary">
                  {clusterDetails.hostCluster.name}
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid  sx={{width:'100%'}} item xs={12} md={6}>
          <Card sx={{ height: "auto", boxShadow: "none", padding: 1,width:'100%' }}>
            <CardHeader
              title={
                <Typography variant="h5" sx={{ color: "#0057fa" }}>
                  Subscriptions
                </Typography>
              }
            />
            <CardContent>
              <Box
                component={"div"}
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  gap:2
                }}
              >
                <Typography gutterBottom variant="h6" sx={{mb:"1em"}}>
                  Name
                </Typography>
                <Typography gutterBottom variant="h6" sx={{mb:"1em"}} color="text.secondary">
                  {clusterDetails.subscription.name}
                </Typography>
              </Box>
              <Box
                component={"div"}
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <Typography gutterBottom variant="h6" sx={{mb:"1em"}}>
                  Pods
                </Typography>
                <Typography gutterBottom variant="h6" sx={{mb:"1em"}} color="text.secondary">
                  {clusterDetails.subscription.pods}
                </Typography>
              </Box>

              <Box
                component={"div"}
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <Typography gutterBottom variant="h6" sx={{mb:"1em"}}>
                  Service
                </Typography>
                <Typography gutterBottom variant="h6" sx={{mb:"1em"}} color="text.secondary">
                  {clusterDetails.subscription.service}
                </Typography>
              </Box>
              <Box
                component={"div"}
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <Typography gutterBottom variant="h6" sx={{mb:"1em"}}>
                  Config map
                </Typography>
                <Typography gutterBottom variant="h6" sx={{mb:"1em"}} color="text.secondary">
                  {clusterDetails.subscription.config_map}
                </Typography>
              </Box>
              <Box
                component={"div"}
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <Typography gutterBottom variant="h6" sx={{mb:"1em"}}>
                  PVC
                </Typography>
                <Typography gutterBottom variant="h6" sx={{mb:"1em"}} color="text.secondary">
                  {clusterDetails.subscription.persistance_vol_claims}
                </Typography>
              </Box>
              <Box
                component={"div"}
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <Typography gutterBottom variant="h6" sx={{mb:"1em"}}>
                  Secrets
                </Typography>
                <Typography gutterBottom variant="h6" sx={{mb:"1em"}} color="text.secondary">
                  {clusterDetails.subscription.secrets}
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
    </>
  );
};
