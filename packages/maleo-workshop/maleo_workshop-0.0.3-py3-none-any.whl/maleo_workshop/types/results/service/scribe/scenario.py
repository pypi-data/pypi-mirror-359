from typing import Union
from maleo_workshop.models.transfers.results.service.scribe.scenario import MaleoWorkshopScribeScenarioServiceResultsTransfers

class MaleoWorkshopScribeScenarioServiceResultsTypes:
    GetMultiple = Union[
        MaleoWorkshopScribeScenarioServiceResultsTransfers.Fail,
        MaleoWorkshopScribeScenarioServiceResultsTransfers.NoData,
        MaleoWorkshopScribeScenarioServiceResultsTransfers.MultipleData
    ]

    GetSingle = Union[
        MaleoWorkshopScribeScenarioServiceResultsTransfers.Fail,
        MaleoWorkshopScribeScenarioServiceResultsTransfers.NoData,
        MaleoWorkshopScribeScenarioServiceResultsTransfers.SingleData
    ]