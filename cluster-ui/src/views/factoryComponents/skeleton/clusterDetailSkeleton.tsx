import Skeleton from '@mui/material/Skeleton';
import { Box, Grid, Typography } from '@mui/material';

const ClusterDetailSkeleton = () => {
return (
    <Box sx={{ flexGrow: 1 }}>
                <Grid container spacing={2}>
                    {/* Skeleton for First Row */}
                    <Grid item xs={12}>
                        <Box
                            sx={{
                                p: 2,
                                boxShadow: 3,
                                display: "flex",
                                flexWrap: "wrap",
                                justifyContent: "space-between",
                                alignItems: "center",
                            }}
                        >
                            <Skeleton variant="circular" width={40} height={40} />
                            <Skeleton variant="text" width={150} />
                            <Skeleton variant="text" width={100} />
                        </Box>
                    </Grid>
                    {/* Skeletons for Second Row */}
                    <Grid item xs={12} sm={6}>
                        <Box sx={{ p: 2, boxShadow: 3 }}>
                            <Typography ml={1} variant="h6">
                                <Skeleton variant="text" width={150} />
                            </Typography>
                            <Skeleton variant="text" width="80%" />
                            <Skeleton variant="text" width="70%" />
                            <Skeleton variant="text" width="60%" />
                            <Skeleton variant="text" width="50%" />
                            <Skeleton variant="text" width="40%" />
                            <Skeleton variant="text" width="30%" />
                        </Box>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                        <Box sx={{ p: 2, boxShadow: 3 }}>
                            <Typography ml={1} variant="h6">
                                <Skeleton variant="text" width={180} />
                            </Typography>
                            <Skeleton variant="text" width="80%" />
                            <Skeleton variant="text" width="70%" />
                            <Skeleton variant="text" width="60%" />
                            <Skeleton variant="text" width="50%" />
                            <Skeleton variant="text" width="40%" />
                            <Skeleton variant="text" width="30%" />
                        </Box>
                    </Grid>
                </Grid>
            </Box>
  );
};

export default ClusterDetailSkeleton;
