import { useEffect, useState, useRef } from "react";
import { w3cwebsocket as W3CWebSocket } from "websocket";
import { useClusterListResponse } from "../hooks/useClusterListResponse";
import { useKeycloak } from "@react-keycloak/web";

export const WebsocketConnection = () => {
  const { keycloak } = useKeycloak();
  const [ws, setWS] = useState<W3CWebSocket | null>(null);
  const [clusterStatus, setClusterStatus] = useState<any[]>([]); 
  const config = (window as any).config;

  const {
    isError: isClusterListError,
    data: clusterDataFromAPI,
    refetch: refetchClusterListData,
  } = useClusterListResponse(keycloak.token || "");

  const socketConnection = (id: string) => {
    if (ws) return; 

    const newWs = new W3CWebSocket(`${config.VITE_APP_WEBSOCKET_CONNECTION_URL}/${id}`);
    setWS(newWs);

    newWs.onopen = () => {
      console.info("WebSocket Client Connected");
    };

    newWs.onclose = (e) => {
      console.info("WebSocket connection closed", e);
      setWS(null);
      if (e.code !== 1000) {
        setTimeout(() => socketConnection(id), 5000); 
      }
    };

    newWs.onerror = () => {
      console.info("WebSocket error");
      newWs.close();
      setWS(null);
    };

    newWs.onmessage = (event: any) => {
      const response = event.data;
      console.log(response);

      if (response) {
        try {
          const _data = JSON.parse(response);
          console.log(_data);
          if (_data.event === "cluster_status_updated") {
            setClusterStatus((prevStatus: any[]) => {
              return prevStatus.map((statusObj) => {
                if (statusObj.clusterId === _data.clusterId) {
                  return { clusterId: _data.clusterId, status: _data.status };
                }
                return statusObj;
              });
            });
            refetchClusterListData(); 
          }
        } catch (err) {
          console.error("Error parsing message data:", err);
        }
      }
    };
  };

  const hasSocketConnection = useRef(false); 

  useEffect(() => {
    if (!isClusterListError && clusterDataFromAPI && clusterDataFromAPI.data.data.length > 0) {
      const initialStatusList = clusterDataFromAPI.data.data.map(cluster => ({
        clusterId: cluster.id,
        status: cluster.status,
      }));
      setClusterStatus(initialStatusList);

      const userId = clusterDataFromAPI.data.data[0].user._id;

      if (!hasSocketConnection.current && userId) {
        socketConnection(userId);
        hasSocketConnection.current = true;
      }
    } else {
      setClusterStatus([]); 
    }


    return 
  }, [clusterDataFromAPI, isClusterListError]);

  console.log(clusterStatus); 

  return { clusterStatus }; 
};
