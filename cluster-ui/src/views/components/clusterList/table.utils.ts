import { Data } from "./table";
export function createData(
  id: JSX.Element,
  sn: JSX.Element,
  name: JSX.Element,
  date:JSX.Element,
  region: JSX.Element,
  plan: JSX.Element,
  status: JSX.Element,
  actions: JSX.Element,
  download: JSX.Element
): Data {
  return { id, sn, name,date, region, plan, status, actions, download };
}


export  const formatDate = (dateString: string): string => {
  const monthNames = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
  ];
  const originalDateString = dateString;
  const date = new Date(originalDateString);

  const year = date.getFullYear().toString(); // Get the last two digits of the year
  const month = monthNames[date.getMonth()]; // Month is zero-based, so add 1 and format as two digits
  const day = String(date.getDate()).padStart(2, "0"); // Format day as two digits
  const hours = String(date.getHours()).padStart(2, "0");
  const minutes = String(date.getMinutes()).padStart(2, "0");
  const seconds = String(date.getSeconds()).padStart(2, "0");
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
};
