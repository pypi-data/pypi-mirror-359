from enum import StrEnum

class MaleoWorkshopScribeResponseEnums:
    class IdentifierType(StrEnum):
        ID = "id"
        UUID = "uuid"

    class ExpandableFields(StrEnum):
        SCENARIO = "scenario"

    class InformationAmountComparison(StrEnum):
        MORE = "more"
        LESS = "less"

    class MissingInformationFrequency(StrEnum):
        OFTEN = "often"
        RARELY = "rarely"