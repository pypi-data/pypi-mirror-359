from pydantic import BaseModel, Field
from typing import List, Optional
from maleo_foundation.models.schemas.parameter import BaseParameterSchemas
from maleo_foundation.types import BaseTypes
from maleo_workshop.enums.scribe.response import MaleoWorkshopScribeResponseEnums

class MaleoWorkshopScribeResponseSchemas:
    class IdentifierType(BaseParameterSchemas.IdentifierType):
        identifier:MaleoWorkshopScribeResponseEnums.IdentifierType = Field(..., description="Scribe response's identifier")

    class Expand(BaseParameterSchemas.Expand):
        expand:Optional[List[MaleoWorkshopScribeResponseEnums.ExpandableFields]] = Field(None, description="Expanded field(s)")

    class ScenarioId(BaseModel):
        scenario_id:int = Field(..., ge=1, description="Scenario's ID")

    class OptionalListOfScenarioIds(BaseModel):
        scenario_ids:BaseTypes.OptionalListOfIntegers = Field(None, description="Scenario's IDs")

    class TimeTaken(BaseModel):
        time_taken:float = Field(..., description="Time taken")

    class PauseCount(BaseModel):
        pause_count:int = Field(0, description="Pause count")

    class ChiefComplaint(BaseModel):
        chief_complaint:str = Field(..., description="Chief complaint")

    class ChiefComplaintLetterCount(BaseModel):
        chief_complaint_letter_count:int = Field(..., description="Chief complaint letter count")

    class ChiefComplaintWordCount(BaseModel):
        chief_complaint_word_count:int = Field(..., description="Chief complaint word count")

    class AdditionalComplaint(BaseModel):
        additional_complaint:str = Field(..., description="Additional complaint")

    class AdditionalComplaintLetterCount(BaseModel):
        additional_complaint_letter_count:int = Field(..., description="Additional complaint letter count")

    class AdditionalComplaintWordCount(BaseModel):
        additional_complaint_word_count:int = Field(..., description="Additional complaint word count")

    class PainScale(BaseModel):
        pain_scale:BaseTypes.OptionalInteger = Field(None, ge=1, le=10, description="Pain scale")

    class SimilarInformationAmount(BaseModel):
        similar_information_amount:bool = Field(..., description="Whether information amount is similar")

    class OptionalInformationAmountComparison(BaseModel):
        information_amount_comparison:Optional[MaleoWorkshopScribeResponseEnums.InformationAmountComparison] = Field(None, description="Comparison of information amount")

    class MissingInformation(BaseModel):
        missing_information:str = Field(..., description="Missing informations")

    class MissingInformationLetterCount(BaseModel):
        missing_information_letter_count:int = Field(..., description="Missing information letter count")

    class MissingInformationWordCount(BaseModel):
        missing_information_word_count:int = Field(..., description="Missing information word count")

    class MissingInformationFrequency(BaseModel):
        missing_information_frequency:Optional[MaleoWorkshopScribeResponseEnums.MissingInformationFrequency] = Field(..., description="Missing information's frequency")

    class TotalLetterCount(BaseModel):
        total_letter_count:int = Field(..., description="Total letter count")

    class TotalWordCount(BaseModel):
        total_word_count:int = Field(..., description="Total word count")