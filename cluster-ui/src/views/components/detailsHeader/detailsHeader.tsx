import { Paper, Typography, Box } from "@mui/material";
import ArrowBackIosIcon from "@mui/icons-material/ArrowBackIos";
import { useHistory } from "react-router-dom";

export const DetailsHeader = () => {
  const history = useHistory();

  const gotoHomePage = () => {
    history.push("/");
  };

  return (
    <Paper elevation={0} sx={{ padding: "1.5em", display: "flex" }}>
      <Box
        onClick={gotoHomePage}
        component="div"
        sx={{
          display: "flex",
          alignItems: "center",
          gap: 2,
          "&:hover": {
            cursor: "pointer",
            transition: "0.2s",
            transform: "scale(102%,102%) translate(-4%,0%)",
          },
          transition: "transform 0.2s",
        }}
      >
        <ArrowBackIosIcon sx={{ color: "blue" }} />{" "}
        <Typography
          variant="subtitle1"
          style={{
            color: "#0057fa",
            marginTop: "0.25em",
            fontWeight: "bold",
          }}
        >
          Return to
        </Typography>{" "}
        <Typography
          style={{ marginTop: "0.25em", fontWeight: "bold" }}
          variant="subtitle1"
        >
          / Home
        </Typography>
      </Box>
    </Paper>
  );
};
