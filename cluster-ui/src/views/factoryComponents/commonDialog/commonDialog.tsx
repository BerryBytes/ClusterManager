import { useState } from "react";
import Button from "@mui/material/Button";
import TextField from "@mui/material/TextField";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";
import { Divider, MenuItem, Typography, Box } from "@mui/material";

interface I_props {
  icon: JSX.Element;
  buttonText: string;
  title: string;
  action: string;
  contentText: string;
  submitText: string;
  onSubmit: () => void;
}

function CommonDialog(props: I_props) {
  const { buttonText, title, contentText, action, submitText, icon } = props;
  const [open, setOpen] = useState(false);
  const [inputValue, setInputValue] = useState("");
  const [isButtonDisabled, setIsButtonDisabled] = useState(true);

  const handleClickOpen = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setInputValue(newValue);

    if (newValue === contentText) {
      setIsButtonDisabled(false);
    } else {
      setIsButtonDisabled(true);
    }
  };

  const handleChange = (e: any) => {
    e.preventDefault();
  };

  const handleButtonClick = () => {
    if (!isButtonDisabled) {
      // Call the callback function if the button is not disabled
      props.onSubmit();
      setInputValue("");
      handleClose();
    }
  };

  return (
    <div style={{ width: "20em" }}>
      <MenuItem onClick={handleClickOpen}>
        {" "}
        <Box sx={{ color: "#0057fa", mr: "1.25em" }} component="span">
          {icon}
        </Box>
        <Typography variant="subtitle1" sx={{ color: "#0057fa" }}>
          {buttonText}
        </Typography>
      </MenuItem>
      <Dialog open={open} onClose={handleClose}>
        <DialogTitle>{title}</DialogTitle>
        <Divider></Divider>
        <DialogContent>
          <DialogContentText>
            <Typography
              color="common.black"
              variant="subtitle1"
              display="inline"
            >
              The action you are taking <strong>cannot be undone.</strong> This
              will <strong>permanently {action}</strong> your cluster{" "}
              <strong>{contentText}</strong>
            </Typography>
            <Typography
              mt={1}
              mb={1}
              color="common.black"
              variant="subtitle1"
              display="block"
            >
              If you are sure, please type <strong>{contentText}</strong>.
            </Typography>
          </DialogContentText>
          <TextField
            autoFocus
            margin="dense"
            id="name"
            type="text"
            fullWidth
            variant="outlined"
            value={inputValue}
            onChange={handleInputChange}
            onCut={handleChange}
            onCopy={handleChange}
            onPaste={handleChange}
          />
        </DialogContent>
        <DialogActions style={{ justifyContent: "center" }}>
          <Button onClick={handleButtonClick} disabled={isButtonDisabled}>
            {submitText}
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
}

export default CommonDialog;
