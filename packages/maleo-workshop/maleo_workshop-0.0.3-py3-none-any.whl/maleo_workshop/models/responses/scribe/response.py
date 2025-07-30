from pydantic import Field
from maleo_foundation.models.responses import BaseResponses
from maleo_workshop.enums.scribe.response import MaleoWorkshopScribeResponseEnums
from maleo_workshop.models.transfers.general.scribe.response import ScribeResponseTransfers

class MaleoWorkshopScribeResponseResponses:
    class InvalidIdentifierType(BaseResponses.BadRequest):
        code:str = "WKS-SCR-RES-001"
        message:str = "Invalid identifier type"
        description:str = "Invalid identifier type is given in the request"
        other: str = f"Valid identifier types: {[f'{e.name} ({e.value})' for e in MaleoWorkshopScribeResponseEnums.IdentifierType]}"

    class InvalidValueType(BaseResponses.BadRequest):
        code:str = "WKS-SCR-RES-002"
        message:str = "Invalid value type"
        description:str = "Invalid value type is given in the request"

    class GetSingle(BaseResponses.SingleData):
        code:str = "WKS-SCR-RES-003"
        message:str = "Scribe response found"
        description:str = "Requested scribe response found in database"
        data:ScribeResponseTransfers = Field(..., description="Scribe response")

    class GetMultiple(BaseResponses.PaginatedMultipleData):
        code:str = "WKS-SCR-RES-004"
        message:str = "Scribe responses found"
        description:str = "Requested scribe responses found in database"
        data:list[ScribeResponseTransfers] = Field(..., description="Scribe responses")

    class CreateFailed(BaseResponses.BadRequest):
        code:str = "WKS-SCR-RES-005"
        message:str = "Failed creating new scribe response"

    class CreateSuccess(BaseResponses.SingleData):
        code:str = "WKS-SCR-RES-006"
        message:str = "Successfully created new scribe response"
        data:ScribeResponseTransfers = Field(..., description="Scribe response")