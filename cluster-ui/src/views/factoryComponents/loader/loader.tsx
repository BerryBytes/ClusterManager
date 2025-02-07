import { CircularProgress, Backdrop } from '@mui/material';
import { makeStyles } from '@mui/styles';

const useStyles = makeStyles(() => ({
    backdrop: {
        zIndex: 100,
        color: '#fff',
    },
}));

const Loading = () => {
    const classes = useStyles();

    return (
        <Backdrop className={classes.backdrop} open={true}>
            <CircularProgress color="inherit" />
        </Backdrop>
    );
};

export default Loading;
