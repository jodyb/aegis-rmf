"""Map function models — system context, stakeholders, and identified risks."""

from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from aegis_rmf.core import (
    DataSensitivity,
    DeploymentEnvironment,
    RiskCategory,
    RiskLevel,
    StakeholderType,
)


class DataSource(BaseModel):
    """A data source the AI system uses for training or inference."""

    name: str
    description: str
    sensitivity: DataSensitivity
    contains_pii: bool = False


class SystemContext(BaseModel):
    """The 'where, why, and how' of an AI system.

    Captures the operational context — purpose, environment, data,
    and dependencies. Like an architectural decision record for
    the AI system.
    """

    id: UUID = Field(default_factory=uuid4)
    system_id: UUID
    purpose: str
    intended_use: str
    out_of_scope_uses: list[str] = Field(default_factory=list)
    deployment_environment: DeploymentEnvironment
    data_sources: list[DataSource] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)


class Stakeholder(BaseModel):
    """A party affected by or interested in the AI system.

    Stakeholders can be internal (employees), external (customers),
    or societal (regulators, vulnerable populations).
    """

    id: UUID = Field(default_factory=uuid4)
    system_id: UUID
    name: str
    stakeholder_type: StakeholderType
    description: str
    impact_description: str = ""


class IdentifiedRisk(BaseModel):
    """A specific risk identified for an AI system.

    Unlike RiskProfile which captures overall risk levels by category,
    this is a granular finding — 'this specific risk exists, here's why,
    here's who it affects.'
    """

    id: UUID = Field(default_factory=uuid4)
    system_id: UUID
    category: RiskCategory
    level: RiskLevel
    title: str
    description: str
    affected_stakeholders: list[UUID] = Field(default_factory=list)
    identified_at: datetime = Field(default_factory=datetime.now)
