import { useKeycloak } from "@react-keycloak/web";
import { makeStyles } from "@mui/styles";
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";
import LoginBackground from "./login.svg";
import Grid from "@mui/material/Grid";
import React from "react";
import { useTheme } from "@mui/material/styles";
import useMediaQuery from "@mui/material/useMediaQuery";
const useStyles = makeStyles(() => ({
  root: {
    display: "flex",
    justifyContent: "center",
    flexDirection: "column",
    alignItems: "center",
    height: "100vh",
    padding: 20,
  },
  paper: {
    padding: 10,
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    maxWidth: "400px",
    width: "100%",
  },
  form: {
    width: "100%",
    marginTop: 10,
  },
  buttonSm: {
    marginTop: 10,
    width: "100%",
  },
  button: {
    marginTop: 10,
    width: "60%",
  },
  heroText: {
    fontWeight: "lighter",
    fontSize: 50,
    textAlign: "center",
    color: "#444",
  },
  subText: {
    fontWeight: "normal",
    fontSize: 20,
    textAlign: "center",
    color: "#444",
  },
}));

interface I_windowPayload {
  userEmail: string;
  authToken: string;
}

interface I_props {
  relayToken?: (token: I_windowPayload) => void;
}
export const LoginPage = (props: I_props) => {
  const classes = useStyles();
  const theme = useTheme();
  const matches = useMediaQuery(theme.breakpoints.up("md"));
  const matchesSm = useMediaQuery(theme.breakpoints.up("sm"));

  const { keycloak, initialized } = useKeycloak();
  const handleLogin = () => {
    keycloak.login();
  };

  React.useEffect(() => {
    if (!initialized || !keycloak.authenticated) return;
    if (props.relayToken && keycloak.tokenParsed) {
      props.relayToken({
        authToken: keycloak.token || "",
        userEmail: keycloak.tokenParsed.email,
      });
    }
  }, [initialized, keycloak.authenticated, keycloak.tokenParsed]);

  // if (!initialized) return <>Loading</>;

  return (
    <>
      <Grid container spacing={2}>
        {matches ? (
          <Grid item md={7}>
            <div
              style={{
                background: `linear-gradient(to right, transparent 10%, #f6f8fa)`,
                backgroundColor: "#0057fa",
              }}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "center",
                  flexDirection: "column",
                  width: "100%",
                  height: "100vh",
                  alignItems: "center",
                }}
              >
                <img
                  src={LoginBackground}
                  alt="logo"
                  style={{ width: "100%", height: "100%" }}
                />
              </div>
            </div>
          </Grid>
        ) : null}

        <Grid item md={5}>
          <div className={classes.root}>
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                justifyContent: "space-between",
              }}
            >
              <Typography
                variant="h1"
                gutterBottom
                className={classes.heroText}
              >
                Create, Manage & Monitor V-clusters
              </Typography>
              <Typography variant="h5" gutterBottom className={classes.subText}>
                Please log in to continue
              </Typography>
            </div>

            <div className={matchesSm ? classes.button : classes.buttonSm}>
              <Button
                onClick={handleLogin}
                fullWidth
                variant="contained"
                color="primary"
                disableElevation={true}
              >
                Login to Dashboard
              </Button>
            </div>
          </div>
        </Grid>
      </Grid>
    </>
  );
};

export default LoginPage;
