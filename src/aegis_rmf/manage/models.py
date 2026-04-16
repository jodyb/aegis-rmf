"""Manage function models — controls, mitigation actions, and monitoring triggers."""

from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from aegis_rmf.core import (
    ActionPriority,
    ActionStatus,
    ControlStatus,
    EvaluationResult,
    RiskCategory,
)


class Control(BaseModel):
    """A technical or procedural safeguard that reduces risk for a system.

    Think of this like a SOC 2 control — it exists independently of any
    individual risk and can address multiple risk categories at once.
    """

    id: UUID = Field(default_factory=uuid4)
    system_id: UUID
    name: str
    description: str
    status: ControlStatus = ControlStatus.PLANNED
    categories: list[RiskCategory] = Field(default_factory=list)
    implementation_notes: str = ""
    created_at: datetime = Field(default_factory=datetime.now)


class MitigationAction(BaseModel):
    """A concrete, time-bound task to address a specific identified risk.

    Where Control is the policy ('use input filtering'), MitigationAction is
    the ticket ('deploy filter to prod by 2026-05-01, assigned to alice@').
    Think of it as a GitHub Issue attached to a risk finding.
    """

    id: UUID = Field(default_factory=uuid4)
    system_id: UUID
    risk_id: UUID                   # FK to MAP's IdentifiedRisk
    control_id: UUID | None = None  # optional link to a Control
    title: str
    description: str
    status: ActionStatus = ActionStatus.OPEN
    priority: ActionPriority
    assignee: str
    due_date: datetime
    resolution_notes: str = ""
    created_at: datetime = Field(default_factory=datetime.now)


class MonitoringTrigger(BaseModel):
    """Fires when a metric's evaluation result reaches a configured severity.

    This is the alerting layer on top of MEASURE — 'when the bias metric
    evaluation hits WARNING or worse, notify the risk officer.'
    Like a CloudWatch alarm action that pages on-call.
    """

    id: UUID = Field(default_factory=uuid4)
    system_id: UUID
    metric_id: UUID                      # FK to MEASURE's Metric
    minimum_result: EvaluationResult     # fire when actual result severity >= this
    action_description: str
    assignee: str
    created_at: datetime = Field(default_factory=datetime.now)
