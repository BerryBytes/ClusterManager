// ... Import statements

import React, { useState } from "react";
import {
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Button,
  TextField,
  CircularProgress,
} from "@mui/material";

// Define the prop types for the DownloadDialog component
interface DownloadDialogProps {
  open: boolean;
  handleClose: () => void;
  handleClickOnDownloadConfig: (text: string) => void; // Accepts a string parameter representing the text value
  isConfigDownloading: boolean;
}

const DownloadDialog: React.FC<DownloadDialogProps> = ({
  open,
  handleClose,
  handleClickOnDownloadConfig,
  isConfigDownloading,
}) => {
  const [textFieldValue, setTextFieldValue] = useState("");
  const [error, setError] = useState(false);

  const handleDownloadClick = () => {
    if (!textFieldValue) {
      setError(true);
      return;
    }
    // Call the handleClickOnDownloadConfig function with the current text value
    handleClickOnDownloadConfig(textFieldValue);
    setTextFieldValue("");
  };

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      aria-labelledby="alert-dialog-title"
      aria-describedby="alert-dialog-description"
    >
      <DialogTitle id="alert-dialog-title">Download Kubeconfig</DialogTitle>
      <DialogContent>
        {/* Replace the DialogContentText with TextField */}
        <TextField
          autoFocus
          margin="dense"
          id="expiration time"
          label="Expiration Time"
          type="text"
          placeholder="Example: 1h30m"
          fullWidth
          value={textFieldValue}
          onChange={(e) => {
            setError(false);
            setTextFieldValue(e.target.value);
          }}
          error={error}
          helperText={error ? "Please enter a valid value" : ""}
        />
      </DialogContent>
      <DialogActions
        sx={{
          display: "flex",
          justifyContent: "space-around",
          alignItems: "center",
        }}
      >
        <Button onClick={handleClose}>Cancel</Button>
        {isConfigDownloading ? (
          <CircularProgress size={20} sx={{ color: "#0057fa" }} />
        ) : (
          <Button onClick={handleDownloadClick} autoFocus>
            Download
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default DownloadDialog;
