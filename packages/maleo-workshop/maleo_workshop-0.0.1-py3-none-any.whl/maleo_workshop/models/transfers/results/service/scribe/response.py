from __future__ import annotations
from pydantic import Field
from maleo_foundation.models.transfers.results.service.general import BaseServiceGeneralResultsTransfers
from maleo_workshop.models.transfers.general.scribe.response import ScribeResponseTransfers

class MaleoWorkshopScribeResponseServiceResultsTransfers:
    class Fail(BaseServiceGeneralResultsTransfers.Fail): pass

    class NoData(BaseServiceGeneralResultsTransfers.NoData): pass

    class SingleData(BaseServiceGeneralResultsTransfers.SingleData):
        data:ScribeResponseTransfers = Field(..., description="Single scribe response data")

    class MultipleData(BaseServiceGeneralResultsTransfers.PaginatedMultipleData):
        data:list[ScribeResponseTransfers] = Field(..., description="Multiple scribe responses data")