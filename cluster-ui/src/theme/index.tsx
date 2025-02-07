import { createTheme } from "@mui/material/styles";

import palette from "./palette";
import typography from "./typography";
// import overrides from "./overrides";

export const theme = createTheme({
  palette,
  typography,
  breakpoints: {
    values: {
      xs:480,
      sm: 568,
      md: 768,
      lg: 1024,
      xl: 1280,
    },
  },
  // overrides,
  zIndex: {
    appBar: 1100,
    drawer: 1100,
  },
});
export default theme;
