import {
  Box,
  Grid,
  Card,
  CardHeader,
  CardContent,
  Typography,
  Skeleton,
} from "@mui/material";



export const ClusterDetailsSkeleton = () => {
  return (
    <Box>
      <Grid container justifyContent={"center"} spacing={4}>
        <Grid item xs={12} md={6}>
          <Card sx={{ height: "auto", boxShadow: "none", padding: "1em" }}>
            <CardHeader
              title={
                <Typography variant="h5" sx={{ color: "#0057fa" }}>
                  <Skeleton width={150} />
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
                  gap: 2,
                }}
              >
                <Typography gutterBottom variant="h6" sx={{ mb: "1em" }}>
                  <Skeleton width={80} />
                </Typography>
                <Typography
                  gutterBottom
                  variant="h6"
                  sx={{ mb: "1em" }}
                  color="text.secondary"
                >
                  <Skeleton width={120} />
                </Typography>
              </Box>
              <Box
                component={"div"}
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  gap: 2,
                }}
              >
                <Typography gutterBottom variant="h6" sx={{ mb: "1em" }}>
                  <Skeleton width={80} />
                </Typography>
                <Typography
                  gutterBottom
                  variant="h6"
                  sx={{ mb: "1em" }}
                  color="text.secondary"
                >
                  <Skeleton width={120} />
                </Typography>
              </Box>
              <Box
                component={"div"}
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  gap: 2,
                }}
              >
                <Typography gutterBottom variant="h6" sx={{ mb: "1em" }}>
                  <Skeleton width={80} />
                </Typography>
                <Typography
                  gutterBottom
                  variant="h6"
                  sx={{ mb: "1em" }}
                  color="text.secondary"
                >
                  <Skeleton width={120} />
                </Typography>
              </Box>
              <Box
                component={"div"}
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  gap: 2,
                }}
              >
                <Typography gutterBottom variant="h6" sx={{ mb: "1em" }}>
                  <Skeleton width={80} />
                </Typography>
                <Typography
                  gutterBottom
                  variant="h6"
                  sx={{ mb: "1em" }}
                  color="text.secondary"
                >
                  <Skeleton width={120} />
                </Typography>
              </Box>
              <Box
                component={"div"}
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  gap: 2,
                }}
              >
                <Typography gutterBottom variant="h6" sx={{ mb: "1em" }}>
                  <Skeleton width={80} />
                </Typography>
                <Typography
                  gutterBottom
                  variant="h6"
                  sx={{ mb: "1em" }}
                  color="text.secondary"
                >
                  <Skeleton width={120} />
                </Typography>
              </Box>
              <Box
                component={"div"}
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  gap: 2,
                }}
              >
                <Typography gutterBottom variant="h6" sx={{ mb: "1em" }}>
                  <Skeleton width={80} />
                </Typography>
                <Typography
                  gutterBottom
                  variant="h6"
                  sx={{ mb: "1em" }}
                  color="text.secondary"
                >
                  <Skeleton width={120} />
                </Typography>
              </Box>


              {/* ... (similar structure for other details) */}
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card sx={{ height: "auto", boxShadow: "none", padding: "1em" }}>
            <CardHeader
              title={
                <Typography variant="h5" sx={{ color: "#0057fa" }}>
                  <Skeleton width={150} />
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
                  gap: 2,
                }}
              >
                <Typography gutterBottom variant="h6" sx={{ mb: "1em" }}>
                  <Skeleton width={80} />
                </Typography>
                <Typography
                  gutterBottom
                  variant="h6"
                  sx={{ mb: "1em" }}
                  color="text.secondary"
                >
                  <Skeleton width={120} />
                </Typography>
              </Box>
              <Box
                component={"div"}
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  gap: 2,
                }}
              >
                <Typography gutterBottom variant="h6" sx={{ mb: "1em" }}>
                  <Skeleton width={80} />
                </Typography>
                <Typography
                  gutterBottom
                  variant="h6"
                  sx={{ mb: "1em" }}
                  color="text.secondary"
                >
                  <Skeleton width={120} />
                </Typography>
              </Box>
              <Box
                component={"div"}
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  gap: 2,
                }}
              >
                <Typography gutterBottom variant="h6" sx={{ mb: "1em" }}>
                  <Skeleton width={80} />
                </Typography>
                <Typography
                  gutterBottom
                  variant="h6"
                  sx={{ mb: "1em" }}
                  color="text.secondary"
                >
                  <Skeleton width={120} />
                </Typography>
              </Box>
              <Box
                component={"div"}
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  gap: 2,
                }}
              >
                <Typography gutterBottom variant="h6" sx={{ mb: "1em" }}>
                  <Skeleton width={80} />
                </Typography>
                <Typography
                  gutterBottom
                  variant="h6"
                  sx={{ mb: "1em" }}
                  color="text.secondary"
                >
                  <Skeleton width={120} />
                </Typography>
              </Box>

              <Box
                component={"div"}
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  gap: 2,
                }}
              >
                <Typography gutterBottom variant="h6" sx={{ mb: "1em" }}>
                  <Skeleton width={80} />
                </Typography>
                <Typography
                  gutterBottom
                  variant="h6"
                  sx={{ mb: "1em" }}
                  color="text.secondary"
                >
                  <Skeleton width={120} />
                </Typography>
              </Box>       <Box
                component={"div"}
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  gap: 2,
                }}
              >
                <Typography gutterBottom variant="h6" sx={{ mb: "1em" }}>
                  <Skeleton width={80} />
                </Typography>
                <Typography
                  gutterBottom
                  variant="h6"
                  sx={{ mb: "1em" }}
                  color="text.secondary"
                >
                  <Skeleton width={120} />
                </Typography>
              </Box>

              {/* ... (similar structure for other details) */}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};
