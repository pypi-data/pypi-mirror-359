from pydantic import BaseModel, Field
from maleo_foundation.models.schemas.parameter import BaseParameterSchemas
from maleo_foundation.types import BaseTypes
from maleo_workshop.enums.scribe.scenario import MaleoWorkshopScribeScenarioEnums

class MaleoWorkshopScribeScenarioSchemas:
    class IdentifierType(BaseParameterSchemas.IdentifierType):
        identifier:MaleoWorkshopScribeScenarioEnums.IdentifierType = Field(..., description="Scribe scenario's identifier")

    class FileName(BaseModel):
        file_name:str = Field(..., description="Scenario's file name")

    class OptionalFileUrl(BaseModel):
        file_url:BaseTypes.OptionalString = Field(None, description="Scenario's file url")