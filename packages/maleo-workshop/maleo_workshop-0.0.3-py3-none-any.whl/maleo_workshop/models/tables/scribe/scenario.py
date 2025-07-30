from sqlalchemy import Column
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, Text
from maleo_workshop.db import MaleoWorkshopMetadataManager
from maleo_foundation.models.table import DataTable

class ScribeScenariosMixin:
    order = Column(name="order", type_=Integer)
    key = Column(name="key", type_=Text, unique=True, nullable=False)
    name = Column(name="name", type_=Text, unique=True, nullable=False)
    file_name = Column(name="file_name", type_=Text, nullable=False)

class ScribeScenariosTable(
    ScribeScenariosMixin,
    DataTable,
    MaleoWorkshopMetadataManager.Base
):
    __tablename__ = "scribe_scenarios"

    responses = relationship(
        "ScribeResponsesTable",
        back_populates="scenario",
        cascade="all",
        lazy="select",
        order_by="ScribeResponsesTable.id"
    )