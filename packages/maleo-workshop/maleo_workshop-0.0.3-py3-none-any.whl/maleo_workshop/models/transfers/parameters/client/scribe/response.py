from __future__ import annotations
from maleo_foundation.models.transfers.parameters.client import BaseClientParametersTransfers
from maleo_workshop.models.schemas.general import MaleoWorkshopGeneralSchemas
from maleo_workshop.models.schemas.scribe.response import MaleoWorkshopScribeResponseSchemas

class MaleoWorkshopScribeResponseClientParametersTransfers:
    class GetMultipleQuery(
        MaleoWorkshopScribeResponseSchemas.Expand,
        BaseClientParametersTransfers.GetPaginatedMultipleQuery,
        MaleoWorkshopScribeResponseSchemas.OptionalListOfScenarioIds,
        MaleoWorkshopGeneralSchemas.OptionalListOfUserIds,
        MaleoWorkshopGeneralSchemas.OptionalListOfOrganizationIds,
    ): pass

    class GetMultiple(
        MaleoWorkshopScribeResponseSchemas.Expand,
        BaseClientParametersTransfers.GetPaginatedMultiple,
        MaleoWorkshopScribeResponseSchemas.OptionalListOfScenarioIds,
        MaleoWorkshopGeneralSchemas.OptionalListOfUserIds,
        MaleoWorkshopGeneralSchemas.OptionalListOfOrganizationIds,
    ): pass