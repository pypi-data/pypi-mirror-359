from typing import Dict
from uuid import UUID
from maleo_workshop.enums.scribe.response import MaleoWorkshopScribeResponseEnums

class MaleoWorkshopScribeResponseConstants:
    IDENTIFIER_TYPE_VALUE_TYPE_MAP:Dict[
        MaleoWorkshopScribeResponseEnums.IdentifierType,
        object
    ] = {
        MaleoWorkshopScribeResponseEnums.IdentifierType.ID: int,
        MaleoWorkshopScribeResponseEnums.IdentifierType.UUID: UUID,
    }