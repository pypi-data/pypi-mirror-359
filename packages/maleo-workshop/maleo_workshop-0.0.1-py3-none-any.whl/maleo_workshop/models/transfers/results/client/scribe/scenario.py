from __future__ import annotations
from pydantic import Field
from maleo_foundation.models.transfers.results.client.service import BaseClientServiceResultsTransfers
from maleo_workshop.models.transfers.general.scribe.scenario import ScribeScenarioTransfers

class MaleoWorkshopScribeScenarioClientResultsTransfers:
    class Fail(BaseClientServiceResultsTransfers.Fail): pass

    class NoData(BaseClientServiceResultsTransfers.NoData): pass

    class SingleData(BaseClientServiceResultsTransfers.SingleData):
        data:ScribeScenarioTransfers = Field(..., description="Single scribe scenario data")

    class MultipleData(BaseClientServiceResultsTransfers.PaginatedMultipleData):
        data:list[ScribeScenarioTransfers] = Field(..., description="Multiple scribe scenarios data")