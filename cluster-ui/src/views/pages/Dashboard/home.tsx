import { makeStyles } from "@mui/styles";
import { CreateClusterSection } from "../../components/createCluster/createCluster";
import { ClusterList } from "../../components/clusterList/clusterList";

const useStyles = makeStyles(() => ({
  root: {
    display: "flex",
    flexDirection: "column",
    gap: 10,
  },
}));

export const HomePage = () => {
  const classes = useStyles();
  return (
    <div className={classes.root}>
      <section><CreateClusterSection/></section>
      <section><ClusterList/></section>
    </div>
  );
};
