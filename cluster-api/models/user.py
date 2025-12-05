"""Models for user information and login credentials."""
import uuid

from pydantic import BaseModel, Field

# Id, name, username, email


class User(BaseModel):
    """Represents a user with basic profile information."""

    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    name: str = Field(...)
    email: str = Field(...)
    userName: str = Field(...)

    class Config:
        """Pydantic configuration for field population and schema examples."""

        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "name": "user one",
                "email": "example@example.com",
                "userName": "testUserName",
            }
        }


class UserLogin(BaseModel):
    """Represents login credentials for a user."""

    userName: str = Field(...)
    password: str = Field(...)

    class Config:
        """Pydantic configuration for field population and schema examples."""

        allow_population_by_field_name = True
        schema_extra = {
            "example": {"userName": "testUserName", "password": "testPassword"}
        }
