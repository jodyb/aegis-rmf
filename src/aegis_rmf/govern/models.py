"""Govern function models — policies, roles, and accountability."""

from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from aegis_rmf.core import (
    LifecycleStage,
    PolicyStatus,
    RiskLevel,
    RoleType,
    SystemType,
)


class PolicyCondition(BaseModel):
    """A condition that determines when a policy applies.

    Think of this like an IAM policy condition — 'this rule applies
    when the system matches these criteria.'
    """

    risk_levels: list[RiskLevel] = Field(default_factory=list)
    lifecycle_stages: list[LifecycleStage] = Field(default_factory=list)
    system_types: list[SystemType] = Field(default_factory=list)

    def matches(self, risk_level: RiskLevel, lifecycle_stage: LifecycleStage,
                system_type: SystemType) -> bool:
        """Check whether a given system matches this condition."""
        if self.risk_levels and risk_level not in self.risk_levels:
            return False
        if self.lifecycle_stages and lifecycle_stage not in self.lifecycle_stages:
            return False
        if self.system_types and system_type not in self.system_types:
            return False
        return True


class GovernancePolicy(BaseModel):
    """A governance rule that AI systems must comply with.

    Like an AWS Config rule — it defines what 'compliant' looks like
    and which resources it applies to.
    """

    id: UUID = Field(default_factory=uuid4)
    name: str
    description: str
    status: PolicyStatus = PolicyStatus.DRAFT
    version: str = "1.0"
    condition: PolicyCondition = Field(default_factory=PolicyCondition)
    requirements: list[str] = Field(default_factory=list)
    owner: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    def applies_to(self, risk_level: RiskLevel, lifecycle_stage: LifecycleStage,
                   system_type: SystemType) -> bool:
        """Check whether this policy applies to a given AI system."""
        if self.status != PolicyStatus.ACTIVE:
            return False
        return self.condition.matches(risk_level, lifecycle_stage, system_type)


class Role(BaseModel):
    """A governance role with defined responsibilities.

    Like an IAM role — it defines what someone is allowed and
    expected to do, separate from who actually holds the role.
    """

    id: UUID = Field(default_factory=uuid4)
    role_type: RoleType
    name: str
    description: str
    responsibilities: list[str] = Field(default_factory=list)


class AccountabilityMapping(BaseModel):
    """Connects a role to a specific AI system with applicable policies.

    This is the wiring — it answers 'for this system, who is
    responsible for what?' Like an IAM role attached to a specific
    resource with a specific policy.
    """

    id: UUID = Field(default_factory=uuid4)
    system_id: UUID
    role_id: UUID
    assignee: str
    policy_ids: list[UUID] = Field(default_factory=list)
    effective_date: datetime = Field(default_factory=datetime.now)
