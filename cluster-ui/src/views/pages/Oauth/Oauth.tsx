import React, { useEffect } from "react";
import LoginPage from "../login/login";
import { useHistory, useLocation } from "react-router-dom";

interface I_windowPayload {
  userEmail: string;
  authToken: string;
}

type t_hostDetails = {
  app_id: string | null;
  redirect_url: string | null;
};
export const OauthPage = () => {
  const [windowPayload, setWindowPayload] =
    React.useState<I_windowPayload | null>(null);
  const [hostDetails, setHostDetails] = React.useState<t_hostDetails | null>(
    null
  );

  const history = useHistory();

  const locationParams = useLocation();

  const handleLogin = (payload: I_windowPayload) => {
    if (
      !window.opener ||
      !hostDetails ||
      !hostDetails.app_id ||
      !hostDetails.redirect_url ||
      !isRedirectURLValid(hostDetails.app_id, hostDetails.redirect_url)
    ) {
      history.push("/");
      return;
    }

    if (hostDetails && hostDetails.app_id && hostDetails.redirect_url) {
      window.location.href = `${hostDetails?.redirect_url}?email=${payload.userEmail}&token=${payload.authToken}`;
    }
  };

  React.useEffect(() => {
    if (windowPayload) {
      handleLogin(windowPayload);
    }
  }, [windowPayload]);

  const relayToken = (payload: I_windowPayload) => {
    setWindowPayload(payload);
  };

  const isRedirectURLValid = (appId: string, redirect_url: string) => {
    return (window as any).config["O_AUTH_CLIENTS"][appId].includes(
      redirect_url
    );
  };

  useEffect(() => {
    if (Object.keys(locationParams).length) {
      const urlObject = locationParams;
      const searchParams = new URLSearchParams(urlObject.search);
      const searchFields = {
        app_id: searchParams.get("app_id"),
        redirect_url: searchParams.get("redirect_url"),
      };

      setHostDetails(searchFields);
    }
  }, [locationParams]);

  return (
    <>
      <LoginPage relayToken={relayToken} />
    </>
  );
};
