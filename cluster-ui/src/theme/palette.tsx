import { colors } from "@mui/material";

const white = "#FFFFFF";
const black = "#000000";

export default {
  black,
  white,
  primary: {
    contrastText: white,
    dark: colors.blue[900],
    main: "#0057fa",
    light: colors.blue[100],
  },
  secondary: {
    contrastText: white,
    dark: colors.pink[900],
    main: colors.pink["A400"],
    light: colors.pink["A400"],
  },
  success: {
    contrastText: white,
    dark: colors.green[900],
    main: colors.green[600],
    light: colors.green[400],
  },
  info: {
    contrastText: white,
    dark: colors.blue[900],
    main: colors.blue[600],
    light: colors.blue[400],
  },
  warning: {
    contrastText: white,
    dark: colors.orange[900],
    main: colors.orange[600],
    light: colors.orange[400],
  },
  error: {
    contrastText: white,
    dark: colors.red[900],
    main: colors.red[600],
    light: colors.red[400],
  },
  text: {
    secondary: "#7B7C8A",
    primary: "#43425D",
    link: colors.blue[600],
  },
  background: {
    default: "#f1f2f2",
    paper: "white",
  },
  icon: colors.blueGrey[600],
  divider: colors.grey[200],
};
