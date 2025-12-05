import { GateWay } from "./views/components/gateway/gateway.tsx";
import { Redirect, BrowserRouter as Router, Switch } from "react-router-dom";
import LoginPage from "./views/pages/login/login.tsx";
import { HomePage } from "./views/pages/Dashboard/home.tsx";
import { ClusterInfo } from "./views/pages/ClusterDetail/clusterInfo.tsx";
import { Route } from "react-router-dom";
import { OauthPage } from "./views/pages/Oauth/Oauth.tsx";
const NoMatch=()=> <Redirect to='/' />
export const App = () => {
  return (
    <>
      <Router>
        <Switch>
          <GateWay path="/" privateRoute={true} exact component={HomePage} />
          <Route path="/signin/identifier" component={OauthPage} />

          <GateWay
            path="/login"
            privateRoute={false}
            exact
            component={LoginPage}
          ></GateWay>

          <GateWay
            path="/cluster/:id"
            privateRoute={true}
            exact
            component={ClusterInfo}
          ></GateWay>

          <Route component={NoMatch}>

          </Route>
        </Switch>
      </Router>
    </>
  );
};
