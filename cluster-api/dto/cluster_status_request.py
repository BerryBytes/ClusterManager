from pydantic import BaseModel

class ClusterStatusRequest(BaseModel):
    name: str 
    id: str 
    status: str 

    class Config:
        schema_extra = {
            "example":{
                "name":"cluster-name",
                "id": "066de609-b04a-4b30-b46c-32537c7f1f6e",
                "status":"Running"
            }
        }
