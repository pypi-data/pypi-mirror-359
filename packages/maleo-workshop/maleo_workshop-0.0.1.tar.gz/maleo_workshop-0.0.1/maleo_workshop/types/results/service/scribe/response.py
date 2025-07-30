from typing import Union
from maleo_workshop.models.transfers.results.service.scribe.response import MaleoWorkshopScribeResponseServiceResultsTransfers

class MaleoWorkshopScribeResponseServiceResultsTypes:
    GetMultiple = Union[
        MaleoWorkshopScribeResponseServiceResultsTransfers.Fail,
        MaleoWorkshopScribeResponseServiceResultsTransfers.NoData,
        MaleoWorkshopScribeResponseServiceResultsTransfers.MultipleData
    ]

    GetSingle = Union[
        MaleoWorkshopScribeResponseServiceResultsTransfers.Fail,
        MaleoWorkshopScribeResponseServiceResultsTransfers.NoData,
        MaleoWorkshopScribeResponseServiceResultsTransfers.SingleData
    ]

    Create = Union[
        MaleoWorkshopScribeResponseServiceResultsTransfers.Fail,
        MaleoWorkshopScribeResponseServiceResultsTransfers.SingleData
    ]