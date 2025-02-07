import { TableCell, Typography, TableRow } from "@mui/material";
import { Data } from "./table";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import Paper from "@mui/material/Paper";
import { TableComponents } from "react-virtuoso";
import React from "react";

interface ColumnData {
  id?: number;
  dataKey: keyof Data;
  label: string;
  numeric?: boolean;
  width: number;
}

const columns: ColumnData[] = [
  {
    width: 30,
    label: "SN",
    dataKey: "sn",
  },
  
  {
    width: 200,
    label: "Name",
    dataKey: "name",
  },
  {
    width: 120,
    label: "Date Created (UTC)",
    dataKey: "date",
  },
  {
    width: 120,
    label: "Region",
    dataKey: "region",
    numeric: true,
  },
  {
    width: 120,
    label: "Plan",
    dataKey: "plan",
    numeric: true,
  },
  {
    width: 120,
    label: "Status",
    dataKey: "status",
    numeric: true,
  },
 
  {
    width: 120,
    label: "Download",
    dataKey: "download",
    numeric: true,
  },
];
export const rowContent = (_index: number, row: Data) => {
  return (
    <React.Fragment>
      {columns.map((column) => (
        <TableCell
          sx={{ background: _index % 2 === 0 ? "transparent" : "#fafafa" }}
          key={column.dataKey}
          align={"center"}
        >
        {row[column.dataKey]}
        </TableCell>
      ))}
    </React.Fragment>
  );
};

export const fixedHeaderContent = () => {
  return (
    <TableRow
      sx={{
        backgroundColor: "#0057fa",
      }}
    >
      {columns.map((column) => (
        <TableCell
          key={column.dataKey}
          variant="head"
          align={"center"}
          style={{ width: column.width }}
          sx={
            {
              // backgroundColor: "#0057fa",
            }
          }
        >
          <Typography
            sx={{ fontWeight: "bold", color: "white" }}
            variant="subtitle1"
          >
            {column.label}
          </Typography>
        </TableCell>
      ))}
    </TableRow>
  );
};

export const VirtuosoTableComponents: TableComponents<Data> = {
  Scroller: React.forwardRef<HTMLDivElement>((props, ref) => (
    <TableContainer
      sx={{
        boxShadow: "none",
        border: "1px solid #eee",
        "::-webkit-scrollbar": {
          width: "4px",
        },
        "::-webkit-scrollbar-thumb": {
          background: "#0057fa",
          borderRadius: "10px",
        },
        "::-webkit-scrollbar-track": {
          background: "#ddd",
          borderRadius: "10px",
        },
      }}
      component={Paper}
      {...props}
      ref={ref}
    />
  )),
  Table: (props) => (
    <Table
      size="small"
      {...props}
      sx={{ borderCollapse: "separate", tableLayout: "fixed" }}
    />
  ),
  TableHead: React.forwardRef<HTMLTableSectionElement>((props, ref) => (
    <TableHead {...props} ref={ref} />
  )) as any,
  TableRow: ({ item: _, ...props }) => <TableRow {...props} />,
  TableBody: React.forwardRef<HTMLTableSectionElement>((props, ref) => (
    <TableBody {...props} ref={ref} />
  )),
};
