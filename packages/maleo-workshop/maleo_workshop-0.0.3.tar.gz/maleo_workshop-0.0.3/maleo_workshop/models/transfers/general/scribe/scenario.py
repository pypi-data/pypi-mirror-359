from pydantic import BaseModel, Field
from maleo_foundation.models.schemas.general import BaseGeneralSchemas
from maleo_workshop.models.schemas.scribe.scenario import MaleoWorkshopScribeScenarioSchemas

class ScribeScenarioTransfers(
    MaleoWorkshopScribeScenarioSchemas.OptionalFileUrl,
    MaleoWorkshopScribeScenarioSchemas.FileName,
    BaseGeneralSchemas.Name,
    BaseGeneralSchemas.Key,
    BaseGeneralSchemas.Order,
    BaseGeneralSchemas.Status,
    BaseGeneralSchemas.Timestamps,
    BaseGeneralSchemas.Identifiers
): pass

class ExpandedScribeScenario(BaseModel):
    scenario:ScribeScenarioTransfers = Field(..., description="Scribe scenario")