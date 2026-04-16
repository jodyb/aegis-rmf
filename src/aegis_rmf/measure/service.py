"""Measure function service — metric tracking and evaluation."""

from uuid import UUID

from aegis_rmf.core import EvaluationResult
from aegis_rmf.measure.models import Measurement, Metric, Threshold


class MeasureService:
    """Tracks metrics, thresholds, and measurements for AI systems.

    Like a CloudWatch + Alarms combination — stores the definitions,
    receives the data points, and evaluates them against thresholds.
    """

    def __init__(self) -> None:
        self._metrics: list[Metric] = []
        self._thresholds: list[Threshold] = []
        self._measurements: list[Measurement] = []

    def register_metric(self, metric: Metric) -> None:
        """Register a metric definition."""
        self._metrics.append(metric)

    def set_threshold(self, threshold: Threshold) -> None:
        """Register a threshold for a metric."""
        self._thresholds.append(threshold)

    def record_measurement(self, measurement: Measurement) -> None:
        """Record a new measurement data point."""
        self._measurements.append(measurement)

    def get_thresholds_for_metric(self, metric_id: UUID) -> list[Threshold]:
        """Return all thresholds defined for a given metric."""
        return [t for t in self._thresholds if t.metric_id == metric_id]

    def get_measurements_for_system(self, system_id: UUID) -> list[Measurement]:
        """Return all measurements recorded for a given system."""
        return [m for m in self._measurements if m.system_id == system_id]

    def evaluate_measurement(self, measurement: Measurement) -> EvaluationResult:
        """Evaluate a measurement against all thresholds for its metric.

        If any threshold fails, returns FAIL. If any warns, returns WARNING.
        Otherwise PASS. Worst-case wins — like a compound alarm.
        """
        thresholds = self.get_thresholds_for_metric(measurement.metric_id)
        if not thresholds:
            return EvaluationResult.PASS  # no thresholds means nothing to fail

        results = [t.evaluate(measurement.value) for t in thresholds]
        if EvaluationResult.FAIL in results:
            return EvaluationResult.FAIL
        if EvaluationResult.WARNING in results:
            return EvaluationResult.WARNING
        return EvaluationResult.PASS

    def get_failing_measurements(self, system_id: UUID) -> list[Measurement]:
        """Return all measurements for a system that currently fail evaluation."""
        return [
            m for m in self.get_measurements_for_system(system_id)
            if self.evaluate_measurement(m) == EvaluationResult.FAIL
        ]
