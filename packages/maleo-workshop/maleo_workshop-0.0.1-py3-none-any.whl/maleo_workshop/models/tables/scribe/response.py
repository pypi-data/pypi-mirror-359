from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, Enum, Text, Boolean, Integer, Float
from maleo_workshop.db import MaleoWorkshopMetadataManager
from maleo_workshop.enums.scribe.response import MaleoWorkshopScribeResponseEnums
from maleo_foundation.models.table import DataTable

class ScribeResponsesMixin:
    organization_id = Column("organization_id", type_=Integer)
    user_id = Column("user_id", type_=Integer, nullable=False)
    scenario_id = Column("scenario_id", Integer, ForeignKey("scribe_scenarios.id", ondelete="CASCADE", onupdate="CASCADE"))
    time_taken = Column("time_taken", type_=Float, nullable=False)
    pause_count = Column("pause_count", type_=Integer, default=0, nullable=False)
    chief_complaint = Column(name="chief_complaint", type_=Text, nullable=False)
    chief_complaint_letter_count = Column(name="chief_complaint_letter_count", type_=Integer, nullable=False)
    chief_complaint_word_count = Column(name="chief_complaint_word_count", type_=Integer, nullable=False)
    additional_complaint = Column(name="additional_complaint", type_=Text, nullable=False)
    additional_complaint_letter_count = Column(name="additional_complaint_letter_count", type_=Integer, nullable=False)
    additional_complaint_word_count = Column(name="additional_complaint_word_count", type_=Integer, nullable=False)
    pain_scale = Column(name="pain_scale", type_=Integer)
    similar_information_amount = Column(name="similar_information_amount", type_=Boolean, nullable=False)
    information_amount_comparison = Column(
        name="information_amount_comparison",
        type_=Enum(
            MaleoWorkshopScribeResponseEnums.InformationAmountComparison,
            name="information_amount_comparison"
        )
    )
    missing_information = Column(name="missing_information", type_=Text, nullable=False)
    missing_information_letter_count = Column(name="missing_information_letter_count", type_=Integer, nullable=False)
    missing_information_word_count = Column(name="missing_information_word_count", type_=Integer, nullable=False)
    missing_information_frequency = Column(
        name="missing_information_frequency",
        type_=Enum(
            MaleoWorkshopScribeResponseEnums.MissingInformationFrequency,
            name="missing_information_frequency"
        ),
        nullable=False
    )
    total_letter_count = Column(name="total_letter_count", type_=Integer, nullable=False)
    total_word_count = Column(name="total_word_count", type_=Integer, nullable=False)

class ScribeResponsesTable(
    ScribeResponsesMixin,
    DataTable,
    MaleoWorkshopMetadataManager.Base
):
    __tablename__ = "scribe_responses"

    scenario = relationship(
        "ScribeScenariosTable",
        back_populates="responses",
        uselist=False,
        cascade="all"
    )