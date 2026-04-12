"""Core domain models shared across all NIST AI RMF functions."""

from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from aegis_rmf.core.enums import (
    ArtifactType,
    AssessmentStatus,
    AssessmentType,
    LifecycleStage,
    RiskCategory,
    RiskLevel,
    SystemType,
)


class AISystem(BaseModel):
    """A registered AI system under governance.

    This is the central entity — every NIST function references it.
    Think of it as the patient record that all hospital departments share.
    """

    id: UUID = Field(default_factory=uuid4)
    name: str
    description: str
    system_type: SystemType
    lifecycle_stage: LifecycleStage = LifecycleStage.DESIGN
    owner: str
    risk_level: RiskLevel = RiskLevel.MEDIUM
    tags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class RiskProfile(BaseModel):
    """A point-in-time snapshot of an AI system's risk landscape.

    An AISystem can have many RiskProfiles over its lifetime.
    The most recent one is the 'current' profile.
    Like a patient's chart — the latest reading matters most,
    but the history tells the full story.
    """

    id: UUID = Field(default_factory=uuid4)
    system_id: UUID
    risk_scores: dict[RiskCategory, RiskLevel] = Field(default_factory=dict)
    overall_risk: RiskLevel = RiskLevel.MEDIUM
    context: str = ""
    assessed_at: datetime = Field(default_factory=datetime.now)


class Assessment(BaseModel):
    """A point-in-time evaluation of an AI system.

    Can be manual, automated, or hybrid. The assessment is the
    container for findings — the receipt, not the process.
    """

    id: UUID = Field(default_factory=uuid4)
    system_id: UUID
    assessment_type: AssessmentType
    status: AssessmentStatus = AssessmentStatus.PLANNED
    assessor: str
    findings: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: datetime | None = None


class ComplianceArtifact(BaseModel):
    """Evidence that governance work was performed.

    The paperwork that proves you followed the process.
    Like the compliance docs you store in S3 for an audit.
    """

    id: UUID = Field(default_factory=uuid4)
    system_id: UUID
    assessment_id: UUID | None = None
    artifact_type: ArtifactType
    title: str
    description: str = ""
    framework: str = "NIST AI RMF"
    created_at: datetime = Field(default_factory=datetime.now)
    created_by: str
