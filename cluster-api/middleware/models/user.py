import uuid
from pydantic import BaseModel, Field

# Id, name, username, email

class User(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    name: str = Field(...)
    email: str = Field(...)
    userName: str = Field(...)

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example":{
                "name": "user one",
                "email": "example@example.com",
                "userName": "testUserName"
            }
        }
class UserLogin(BaseModel):
    userName: str = Field(...)
    password: str = Field(...)

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example":{
                "userName": "testUserName",
                "password": "testPassword"
            }
        }