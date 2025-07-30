from maleo_foundation.models.schemas.general import BaseGeneralSchemas
from maleo_workshop.models.schemas.general import MaleoWorkshopGeneralSchemas
from maleo_workshop.models.schemas.scribe.response import MaleoWorkshopScribeResponseSchemas
from .scenario import ExpandedScribeScenario

class ScribeResponseTransfers(
    MaleoWorkshopScribeResponseSchemas.TotalWordCount,
    MaleoWorkshopScribeResponseSchemas.TotalLetterCount,
    MaleoWorkshopScribeResponseSchemas.MissingInformationFrequency,
    MaleoWorkshopScribeResponseSchemas.MissingInformationWordCount,
    MaleoWorkshopScribeResponseSchemas.MissingInformationLetterCount,
    MaleoWorkshopScribeResponseSchemas.MissingInformation,
    MaleoWorkshopScribeResponseSchemas.OptionalInformationAmountComparison,
    MaleoWorkshopScribeResponseSchemas.SimilarInformationAmount,
    MaleoWorkshopScribeResponseSchemas.PainScale,
    MaleoWorkshopScribeResponseSchemas.AdditionalComplaintWordCount,
    MaleoWorkshopScribeResponseSchemas.AdditionalComplaintLetterCount,
    MaleoWorkshopScribeResponseSchemas.AdditionalComplaint,
    MaleoWorkshopScribeResponseSchemas.ChiefComplaintWordCount,
    MaleoWorkshopScribeResponseSchemas.ChiefComplaintLetterCount,
    MaleoWorkshopScribeResponseSchemas.ChiefComplaint,
    MaleoWorkshopScribeResponseSchemas.PauseCount,
    MaleoWorkshopScribeResponseSchemas.TimeTaken,
    ExpandedScribeScenario,
    MaleoWorkshopScribeResponseSchemas.ScenarioId,
    MaleoWorkshopGeneralSchemas.UserId,
    MaleoWorkshopGeneralSchemas.OptionalOrganizationId,
    BaseGeneralSchemas.Status,
    BaseGeneralSchemas.Timestamps,
    BaseGeneralSchemas.Identifiers
): pass