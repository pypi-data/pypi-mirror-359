from __future__ import annotations
from maleo_foundation.models.transfers.parameters.service import BaseServiceParametersTransfers
from maleo_workshop.models.schemas.general import MaleoWorkshopGeneralSchemas
from maleo_workshop.models.schemas.scribe.response import MaleoWorkshopScribeResponseSchemas

class MaleoWorkshopScribeResponseServiceParametersTransfers:
    class GetMultipleQuery(
        MaleoWorkshopScribeResponseSchemas.Expand,
        BaseServiceParametersTransfers.GetPaginatedMultipleQuery,
        MaleoWorkshopScribeResponseSchemas.OptionalListOfScenarioIds,
        MaleoWorkshopGeneralSchemas.OptionalListOfUserIds,
        MaleoWorkshopGeneralSchemas.OptionalListOfOrganizationIds,
    ): pass

    class GetMultiple(
        MaleoWorkshopScribeResponseSchemas.Expand,
        BaseServiceParametersTransfers.GetPaginatedMultiple,
        MaleoWorkshopScribeResponseSchemas.OptionalListOfScenarioIds,
        MaleoWorkshopGeneralSchemas.OptionalListOfUserIds,
        MaleoWorkshopGeneralSchemas.OptionalListOfOrganizationIds,
    ): pass