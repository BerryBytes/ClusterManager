from pydantic import BaseModel


class GenerateKubeconfig(BaseModel):
    expiryTime: str
    clusterId: str

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "expiryTime": "1h20m",
                "clusterId": "066de609-b04a-4b30-b46c-32537c7f1f6e",
            }
        }
