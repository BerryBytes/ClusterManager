import { AxiosRequestConfig } from "axios";

export const getAuthHeaderConfig = (token?: string): AxiosRequestConfig => {
  return {
    headers: {
      'Authorization': `Bearer ${token ?? ""}`,
      'Content-Type': 'application/json',
    },
  };
};
