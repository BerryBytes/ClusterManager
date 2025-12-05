export const StatusColorHelper = (status:string) =>{
        switch (status) {
            case "Creating":
                return "#1976D2";
            case "Pending":
                return "#FFC107";
            case "Failed":
                return "#F44336";
            case "Running":
                return "#4CAF50";
            case "Stopped":
                return "#db6607";
            default:
                return "#2196F3";
        }
}
