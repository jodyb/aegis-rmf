"""Measure function models — metrics, thresholds, and measurements."""

from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from aegis_rmf.core import (
    EvaluationResult,
    MetricType,
    ThresholdOperator,
)


class Metric(BaseModel):
    """Definition of something measurable about an AI system.

    A metric is a specification — it says 'this is a thing we track'
    without any actual values attached. Like a CloudWatch metric
    definition before any data points are published.
    """

    id: UUID = Field(default_factory=uuid4)
    name: str
    description: str
    metric_type: MetricType
    unit: str
    higher_is_better: bool = True
    created_at: datetime = Field(default_factory=datetime.now)


class Threshold(BaseModel):
    """A pass/fail boundary for a metric.

    A threshold says 'a measurement of this metric passes if it
    meets this condition.' Like a CloudWatch alarm threshold.
    """

    id: UUID = Field(default_factory=uuid4)
    metric_id: UUID
    operator: ThresholdOperator
    value: float
    # Used only when operator is BETWEEN (lower bound is `value`, upper is `upper_value`)
    upper_value: float | None = None
    warning_value: float | None = None
    description: str = ""

    def evaluate(self, measurement_value: float) -> EvaluationResult:
        """Check whether a measurement passes this threshold."""
        # Check the hard pass/fail condition first
        passes = self._matches(measurement_value, self.operator, self.value,
                               self.upper_value)
        if not passes:
            return EvaluationResult.FAIL

        # Optionally check for warning level (softer threshold)
        if self.warning_value is not None:
            warning_passes = self._matches(
                measurement_value, self.operator, self.warning_value,
                self.upper_value,
            )
            if not warning_passes:
                return EvaluationResult.WARNING

        return EvaluationResult.PASS

    @staticmethod
    def _matches(value: float, operator: ThresholdOperator, target: float,
                 upper: float | None) -> bool:
        """Check whether a value satisfies the operator against targets."""
        if operator == ThresholdOperator.LESS_THAN:
            return value < target
        if operator == ThresholdOperator.LESS_THAN_OR_EQUAL:
            return value <= target
        if operator == ThresholdOperator.GREATER_THAN:
            return value > target
        if operator == ThresholdOperator.GREATER_THAN_OR_EQUAL:
            return value >= target
        if operator == ThresholdOperator.EQUALS:
            return value == target
        if operator == ThresholdOperator.BETWEEN:
            if upper is None:
                raise ValueError("BETWEEN operator requires upper_value")
            return target <= value <= upper
        raise ValueError(f"Unknown operator: {operator}")


class Measurement(BaseModel):
    """A recorded measurement of a metric at a point in time.

    This is the actual data point — 'the latency was 347ms at 10:15am.'
    Produced by the eval harness (Phase 4) or manually recorded.
    """

    id: UUID = Field(default_factory=uuid4)
    system_id: UUID
    metric_id: UUID
    value: float
    measured_at: datetime = Field(default_factory=datetime.now)
    source: str = "manual"  # 'manual', 'eval_harness', 'monitoring', etc.
    notes: str = ""
