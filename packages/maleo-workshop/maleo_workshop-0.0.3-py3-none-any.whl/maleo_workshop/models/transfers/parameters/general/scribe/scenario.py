from __future__ import annotations
from pydantic import Field
from maleo_foundation.models.transfers.parameters.general import BaseGeneralParametersTransfers
from maleo_workshop.enums.scribe.scenario import MaleoWorkshopScribeScenarioEnums

class MaleoWorkshopScribeScenarioGeneralParametersTransfers:
    class GetSingleQuery(BaseGeneralParametersTransfers.GetSingleQuery): pass

    class GetSingle(BaseGeneralParametersTransfers.GetSingle):
        identifier:MaleoWorkshopScribeScenarioEnums.IdentifierType = Field(..., description="Identifier")