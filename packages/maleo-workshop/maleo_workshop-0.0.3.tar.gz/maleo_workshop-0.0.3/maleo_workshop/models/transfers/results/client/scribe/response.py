from __future__ import annotations
from pydantic import Field
from maleo_foundation.models.transfers.results.client.service import BaseClientServiceResultsTransfers
from maleo_workshop.models.transfers.general.scribe.response import ScribeResponseTransfers

class MaleoWorkshopScribeResponseClientResultsTransfers:
    class Fail(BaseClientServiceResultsTransfers.Fail): pass

    class NoData(BaseClientServiceResultsTransfers.NoData): pass

    class SingleData(BaseClientServiceResultsTransfers.SingleData):
        data:ScribeResponseTransfers = Field(..., description="Single scribe response data")

    class MultipleData(BaseClientServiceResultsTransfers.PaginatedMultipleData):
        data:list[ScribeResponseTransfers] = Field(..., description="Multiple scribe responses data")