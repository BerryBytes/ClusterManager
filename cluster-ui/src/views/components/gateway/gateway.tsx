import { Route } from "react-router-dom";
import ResponsiveAppBar from "../header/header";
import { useKeycloak } from "@react-keycloak/web";
import { useEffect, useState } from "react";
import Loading from "../../factoryComponents/loader/loader";
import {  useSnackbar } from "notistack";
import { T_user } from "../../../models/user";
import { LoginPage } from "../../pages/login/login";
interface Props {
  path: string;
  component:React.FC
  exact: boolean;
  privateRoute?: boolean;
}

export const GateWay = ({
  component,
  privateRoute = false,
  ...rest
}: Props) => {
  const Component = component; // Now, you can access the match props
  const { keycloak, initialized } = useKeycloak();
  const {enqueueSnackbar}=useSnackbar()
  const [userDetails, setUserDetails] = useState<T_user | null>(null);
  const [authError, setAuthError] = useState("");
  const [isLoginPage, setIsLoginPage] = useState(false);

  useEffect(() => {
    if (!initialized || !privateRoute) return;
    if (privateRoute && !keycloak.authenticated) {
      // keycloak.login();
      setIsLoginPage(true);

      return;
    }

    const authentiatedUserDetails = keycloak.tokenParsed;
    if (!authentiatedUserDetails) return;

    setUserDetails(() => {
      const name = authentiatedUserDetails.name;
      const email = authentiatedUserDetails.email;
      const email_verified = authentiatedUserDetails.email_verified;

      if (!email) {
        setAuthError("Email not found");
        return null;
      }
      return { name, email, email_verified };
    });
  }, [keycloak, initialized]);

  useEffect(() => {
    if (authError) {
      enqueueSnackbar(authError,{variant:'error'})
    }
  }, [authError]);

  // Check if the token is expired and refresh it if necessary
  useEffect(() => {
    const refreshToken = async () => {
      if (keycloak.authenticated && keycloak.isTokenExpired()) {
        try {
          await keycloak.updateToken(5); // Refresh the token with a 5-second buffer
        } catch (error) {
          console.error("Error refreshing token:", error);
        }
      }
    };

    refreshToken();
  }, [keycloak]);

  if (!initialized) return <Loading />;
  if (isLoginPage || !keycloak.authenticated || !keycloak.token || !privateRoute) {
    rest.path = "/login";
    return (
      <Route
        {...rest}
        render={() => (
          <div>
            {
              <div >
                <LoginPage />
              </div>
            }
          </div>
        )}
      />
    );
  }
  return (
    <Route
      {...rest}
      render={() => (
        <div>
          <ResponsiveAppBar userDetails={userDetails} />
          {
            <div style={{ margin: "2rem 2rem" }}>
              <Component />
            </div>
          }
        </div>
      )}
    />
  );
};

export default GateWay;
