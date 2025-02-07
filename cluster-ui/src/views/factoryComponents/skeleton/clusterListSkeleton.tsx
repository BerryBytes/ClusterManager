import { TableRow, TableCell, Skeleton } from '@mui/material';

const ClusterListSkeleton = () => {
    return (
        <TableRow>
            <TableCell colSpan={6}>
            <Skeleton variant="text" width="100%" />
            <Skeleton variant="text" width="100%" />
            <Skeleton variant="text" width="100%" />
            <Skeleton variant="text" width="100%" />
            <Skeleton variant="text" width="100%" />
            <Skeleton variant="text" width="100%" />
            <Skeleton variant="text" width="100%" />
            <Skeleton variant="text" width="100%" />
            <Skeleton variant="text" width="100%" />
            <Skeleton variant="text" width="100%" />
            </TableCell>
        </TableRow>
    );
};

export default ClusterListSkeleton;
