import { Typography, Box } from "@mui/material";
import { useParams } from "react-router-dom";
import { useKeycloak } from "@react-keycloak/web";
import { ClusterActionArea } from "../clusterActionArea/clusterActionArea";
import { ClusterInfoArea } from "../clusterInfoArea/clusterInfoArea";
import { useClusterDetailsResponse } from "../../../hooks/useClusterDetails";
import { ClusterDetailsSkeleton } from "./clusterDetailsLoader";
import { Skeleton } from "@mui/material";
export const ClusterDetails = () => {
  const { id } = useParams<{ id: string }>();
  const { keycloak } = useKeycloak();

  const {

    isError: isClusterDetailsError,
    data: clusterDetailResponse,
    ...rest
  } = useClusterDetailsResponse(id, keycloak.token || "");

  if (rest.fetchStatus === "fetching")
    return (
      <Box sx={{ height: 100 }}>
        <Box
          sx={{
            display: "flex",
            background: "transparent",
            justifyContent: "space-between",
            flexWrap: "wrap",
            alignItems: "center",
            gap: 5,
          }}
        >
          <Typography variant="h5" color="text.secondary">
            <Box component={"span"} sx={{ display: "flex", gap: 2 }}>
              <Skeleton height={40} width={150} />
              <Skeleton height={40} width={120} />
            </Box>
          </Typography>

          <Typography variant="h5" color="text.secondary">
            <Skeleton width={120} height={100} />
          </Typography>
        </Box>

        <ClusterDetailsSkeleton />
      </Box>
    );

  if (isClusterDetailsError)
    return (
      <Box sx={{ height: 100, padding: 10 }}>
        <Typography variant="h5" align="center">
          Something went wrong.Please try again in some time.
        </Typography>
      </Box>
    );

  return clusterDetailResponse ? (
    <>
      <ClusterActionArea clusterDetails={clusterDetailResponse.data.data} />
      <ClusterInfoArea clusterDetails={clusterDetailResponse.data.data} />
    </>
  ) : null;
};
