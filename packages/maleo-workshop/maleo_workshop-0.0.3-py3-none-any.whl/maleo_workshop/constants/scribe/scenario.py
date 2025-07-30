from typing import Dict
from uuid import UUID
from maleo_workshop.enums.scribe.scenario import MaleoWorkshopScribeScenarioEnums

class MaleoWorkshopScribeScenarioConstants:
    IDENTIFIER_TYPE_VALUE_TYPE_MAP:Dict[
        MaleoWorkshopScribeScenarioEnums.IdentifierType,
        object
    ] = {
        MaleoWorkshopScribeScenarioEnums.IdentifierType.ID: int,
        MaleoWorkshopScribeScenarioEnums.IdentifierType.UUID: UUID,
        MaleoWorkshopScribeScenarioEnums.IdentifierType.KEY: str,
        MaleoWorkshopScribeScenarioEnums.IdentifierType.NAME: str
    }