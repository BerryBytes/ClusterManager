import * as React from "react";
import AppBar from "@mui/material/AppBar";
import Box from "@mui/material/Box";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";
import { Link } from "react-router-dom";
import { useKeycloak } from "@react-keycloak/web";
import { ProfileMenu } from "../profileMenu/profileMenu";
import { T_user } from "../../../models/user";
import { useHistory } from "react-router-dom";
import { useSnackbar } from "notistack";
import logo from './../..//../assets/logo.svg'
interface I_props {
  userDetails: T_user | null;
}

function ResponsiveAppBar({ userDetails }: I_props) {
  const { keycloak } = useKeycloak();
  const { enqueueSnackbar } = useSnackbar();
  const [anchorElUser, setAnchorElUser] = React.useState<null | HTMLElement>(
    null
  );
  const history = useHistory();

  const handleOpenUserMenu = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorElUser(event.currentTarget);
  };

  const handleCloseUserMenu = () => {
    setAnchorElUser(null);
  };

  const handleCopyTOken = async () => {
    if (!keycloak.token) return;
    try {
      await navigator.clipboard.writeText(keycloak.token);
      enqueueSnackbar("Token copied to clipboard !", {
        variant: "success",
        anchorOrigin: {
          vertical: "top",
          horizontal: "center",
        },
      });
    } catch (err) {
      enqueueSnackbar("Failed to copy token !", {
        variant: "error",
        anchorOrigin: {
          vertical: "top",
          horizontal: "center",
        },
      });
    }
    handleCloseUserMenu();
  };
  const handleUserLogout = async () => {
    history.push("/");
    keycloak.logout();
  };

  return (
    <AppBar position="static" style={{ background: "#0057fa" }}>
      <Toolbar
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
        }}
      >
       <Box component={'span'} sx={{display:'flex',alignItems:'center'}}>
        <Box component={'span'} sx={{pr:1}}>
        <img src={logo} alt="Logo" />
        </Box>
       <Link to="/" style={{ textDecoration: "none", color: "white" }}>
          <Typography
            variant="h6"
            noWrap
            component="a"
            sx={{
              fontFamily: "comfortaa",
              fontWeight: 700,
              letterSpacing: ".3rem",
              color: "inherit",
            }}
          >
            Cluster Manager
          </Typography>
        </Link>
       </Box>

        {userDetails && userDetails.email && userDetails.name && (
          <Box
            sx={{ flexGrow: 0, display: "flex", alignItems: "center", gap: 2 }}
          >
            <Typography
              onClick={handleOpenUserMenu}
              display="block"
              variant="subtitle1"
              color="textPrimary"
              noWrap={true}
              sx={{
                fontSize: "20px",
                color: "#fff",

                "&:hover": {
                  cursor: "pointer",
                  // background:"#5d92f5",
                  px: "0.5em",
                  transition: "0.4s",
                },
                transition: "padding 0.4s",
              }}
            >
              Hello, {userDetails ? userDetails.name.split(" ")[0] : ""}{" "}
            </Typography>

            <ProfileMenu
              userDetails={userDetails}
              anchorElUser={anchorElUser}
              handleCloseUserMenu={handleCloseUserMenu}
              handleUserLogout={handleUserLogout}
              handleCopyTOken={handleCopyTOken}
            />
          </Box>
        )}
      </Toolbar>
    </AppBar>
  );
}
export default ResponsiveAppBar;
