from __future__ import annotations
from maleo_foundation.models.schemas.parameter import BaseParameterSchemas
from maleo_workshop.models.schemas.general import MaleoWorkshopGeneralSchemas
from maleo_workshop.models.schemas.scribe.response import MaleoWorkshopScribeResponseSchemas

class MaleoWorkshopScribeResponseGeneralParametersTransfers:
    class GetSingleQuery(
        MaleoWorkshopScribeResponseSchemas.Expand,
        BaseParameterSchemas.OptionalListOfStatuses
    ): pass

    class GetSingle(
        MaleoWorkshopScribeResponseSchemas.Expand,
        BaseParameterSchemas.OptionalListOfStatuses,
        BaseParameterSchemas.IdentifierValue,
        MaleoWorkshopScribeResponseSchemas.IdentifierType
    ): pass

    class CreateQuery(MaleoWorkshopScribeResponseSchemas.Expand): pass

    class CreateBody(
        MaleoWorkshopScribeResponseSchemas.MissingInformationFrequency,
        MaleoWorkshopScribeResponseSchemas.MissingInformation,
        MaleoWorkshopScribeResponseSchemas.OptionalInformationAmountComparison,
        MaleoWorkshopScribeResponseSchemas.SimilarInformationAmount,
        MaleoWorkshopScribeResponseSchemas.PainScale,
        MaleoWorkshopScribeResponseSchemas.AdditionalComplaint,
        MaleoWorkshopScribeResponseSchemas.ChiefComplaint,
        MaleoWorkshopScribeResponseSchemas.PauseCount,
        MaleoWorkshopScribeResponseSchemas.TimeTaken,
        MaleoWorkshopScribeResponseSchemas.ScenarioId
    ): pass

    class CreateData(
        CreateBody,
        MaleoWorkshopGeneralSchemas.UserId,
        MaleoWorkshopGeneralSchemas.OptionalOrganizationId
    ): pass

    class Create(
        CreateData,
        CreateQuery
    ): pass