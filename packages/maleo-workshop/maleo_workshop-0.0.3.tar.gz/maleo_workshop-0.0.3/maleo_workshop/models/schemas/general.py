from pydantic import BaseModel, Field
from maleo_foundation.types import BaseTypes

class MaleoWorkshopGeneralSchemas:
    class OptionalOrganizationId(BaseModel):
        organization_id:BaseTypes.OptionalInteger = Field(None, ge=1, description="Organization's ID")

    class OptionalListOfOrganizationIds(BaseModel):
        organization_ids:BaseTypes.OptionalListOfIntegers = Field(None, description="Organization's IDs")

    class UserId(BaseModel):
        user_id:int = Field(..., ge=1, description="User's ID")

    class OptionalListOfUserIds(BaseModel):
        user_ids:BaseTypes.OptionalListOfIntegers = Field(None, description="User's IDs")