from __future__ import annotations
from pydantic import Field
from maleo_foundation.models.transfers.results.service.general import BaseServiceGeneralResultsTransfers
from maleo_workshop.models.transfers.general.scribe.scenario import ScribeScenarioTransfers

class MaleoWorkshopScribeScenarioServiceResultsTransfers:
    class Fail(BaseServiceGeneralResultsTransfers.Fail): pass

    class NoData(BaseServiceGeneralResultsTransfers.NoData): pass

    class SingleData(BaseServiceGeneralResultsTransfers.SingleData):
        data:ScribeScenarioTransfers = Field(..., description="Single scribe scenario data")

    class MultipleData(BaseServiceGeneralResultsTransfers.UnpaginatedMultipleData):
        data:list[ScribeScenarioTransfers] = Field(..., description="Multiple scribe scenarios data")