import { DetailsHeader } from "../../components/detailsHeader/detailsHeader";
import { ClusterDetails } from "../../components/clusterDetails/clusterDetails";
export const ClusterInfo = () => {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
      <section>
        <DetailsHeader />
      </section>

      <section>
        <ClusterDetails />
      </section>
     
    </div>
  );
};
