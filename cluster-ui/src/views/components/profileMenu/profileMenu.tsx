import Menu from "@mui/material/Menu";
import Typography from "@mui/material/Typography";
import Card from "@mui/material/Card";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItemText from "@mui/material/ListItemText";
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import LogoutIcon from "@mui/icons-material/Logout";
import Avatar from "@mui/material/Avatar";
import { T_user } from "../../../models/user";
import { Divider } from "@mui/material";

interface I_props {
  anchorElUser: null | HTMLElement;
  handleCloseUserMenu: () => void;
  handleUserLogout: () => void;
  handleCopyTOken:()=>void;
  userDetails: T_user;
}
export const ProfileMenu = ({
  anchorElUser,
  handleCloseUserMenu,
  handleUserLogout,
  handleCopyTOken,
  userDetails,
}: I_props) => {
  return (
    <Menu
      sx={{ mt: "45px" }}
      id="menu-appbar"
      anchorEl={anchorElUser}
      anchorOrigin={{
        vertical: "top",
        horizontal: "right",
      }}
      keepMounted
      transformOrigin={{
        vertical: "top",
        horizontal: "right",
      }}
      open={Boolean(anchorElUser)}
      onClose={handleCloseUserMenu}
    >
      <div>
        <Card elevation={0}>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              margin: 14,
              gap: 14,
              cursor: "pointer",
            }}
          >
            <Avatar
              alt={`${userDetails.name || userDetails.email || "A"}`}
              src="/static/images/avatar/2.jpg"
              sx={{ width: 56, height: 56, background: "#0057fa" }}
            />
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                justifyContent: "space-around",
              }}
            >
              <Typography
                display="block"
                noWrap={true}
                variant="h6"
                color="textPrimary"
                component="p"
                sx={{ color: "#0057fa" ,  whiteSpace: "nowrap",
                overflow: "hidden",
                textOverflow: "ellipsis",maxWidth:320}}
              >
                {userDetails && userDetails.email ? userDetails.email : ""} 
              </Typography>
            </div>
          </div>
        </Card>
      </div>
      <Divider sx={{width:'90%',margin:'auto'}}/>
      <div style={{ paddingLeft: 15, paddingRight: 15 }}>
        <List
          sx={{
            "&:hover": {
              cursor: "pointer",
            },
          }}
          component={"nav"}
        >
          <ListItem
            sx={{
              "&:hover": {
                background: "#f6f6f6",
              },
            }}
            onClick={handleCopyTOken}
          >
            <ListItemIcon style={{ maxWidth: 10 }}>
              <ContentCopyIcon style={{ color: "#0057fa" }} />
            </ListItemIcon>
            <ListItemText
              primary={
                <Typography
                  variant="subtitle1"
                  // color="textPrimary"
                  component="p"
                  style={{ color: "#0057fa", marginTop: "0.25em" }}
                >
                  Copy Token
                </Typography>
              }
            />
          </ListItem>
          <ListItem
            sx={{
              "&:hover": {
                background: "#f6f6f6",
              },
            }}
            onClick={handleUserLogout}
          >
            <ListItemIcon>
              <LogoutIcon style={{ color: "#0057fa" }} />
            </ListItemIcon>
            <ListItemText
              primary={
                <Typography
                  variant="subtitle1"
                  color="textPrimary"
                  component="p"
                  sx={{ color: "#0057fa", marginTop: "0.25em" }}
                >
                  Logout
                </Typography>
              }
            />
          </ListItem>
          
        </List>
      </div>
    </Menu>
  );
};
