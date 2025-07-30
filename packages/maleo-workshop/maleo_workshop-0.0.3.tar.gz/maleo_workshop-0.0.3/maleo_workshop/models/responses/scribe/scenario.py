from pydantic import Field
from maleo_foundation.models.responses import BaseResponses
from maleo_workshop.enums.scribe.scenario import MaleoWorkshopScribeScenarioEnums
from maleo_workshop.models.transfers.general.scribe.scenario import ScribeScenarioTransfers

class MaleoWorkshopScribeScenarioResponses:
    class InvalidIdentifierType(BaseResponses.BadRequest):
        code:str = "WKS-SCR-SCN-001"
        message:str = "Invalid identifier type"
        description:str = "Invalid identifier type is given in the request"
        other: str = f"Valid identifier types: {[f'{e.name} ({e.value})' for e in MaleoWorkshopScribeScenarioEnums.IdentifierType]}"

    class InvalidValueType(BaseResponses.BadRequest):
        code:str = "WKS-SCR-SCN-002"
        message:str = "Invalid value type"
        description:str = "Invalid value type is given in the request"

    class GetSingle(BaseResponses.SingleData):
        code:str = "WKS-SCR-SCN-003"
        message:str = "Scribe scenario found"
        description:str = "Requested scribe scenario found in database"
        data:ScribeScenarioTransfers = Field(..., description="Scribe scenario")

    class GetMultiple(BaseResponses.UnpaginatedMultipleData):
        code:str = "WKS-SCR-SCN-004"
        message:str = "Scribe scenarios found"
        description:str = "Requested scribe scenarios found in database"
        data:list[ScribeScenarioTransfers] = Field(..., description="Scribe scenarios")