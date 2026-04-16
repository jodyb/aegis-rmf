"""Tests for the Measure function."""

import pytest

from aegis_rmf.core import (
    AISystem,
    EvaluationResult,
    MetricType,
    SystemType,
    ThresholdOperator,
)
from aegis_rmf.measure import Measurement, MeasureService, Metric, Threshold


class TestMetric:
    """Tests for the Metric model."""

    def test_create_performance_metric(self):
        metric = Metric(
            name="Accuracy",
            description="Classification accuracy on held-out test set",
            metric_type=MetricType.PERFORMANCE,
            unit="ratio",
            higher_is_better=True,
        )
        assert metric.metric_type == MetricType.PERFORMANCE
        assert metric.higher_is_better is True

    def test_create_latency_metric(self):
        metric = Metric(
            name="p99 Latency",
            description="99th percentile inference latency",
            metric_type=MetricType.OPERATIONAL,
            unit="ms",
            higher_is_better=False,
        )
        assert metric.higher_is_better is False


class TestThreshold:
    """Tests for threshold evaluation."""

    def test_less_than_pass(self):
        metric = Metric(
            name="Latency", description="", metric_type=MetricType.OPERATIONAL,
            unit="ms", higher_is_better=False,
        )
        threshold = Threshold(
            metric_id=metric.id,
            operator=ThresholdOperator.LESS_THAN,
            value=500.0,
        )
        assert threshold.evaluate(300.0) == EvaluationResult.PASS
        assert threshold.evaluate(500.0) == EvaluationResult.FAIL
        assert threshold.evaluate(700.0) == EvaluationResult.FAIL

    def test_greater_than_or_equal_pass(self):
        metric = Metric(
            name="Accuracy", description="", metric_type=MetricType.PERFORMANCE,
            unit="ratio",
        )
        threshold = Threshold(
            metric_id=metric.id,
            operator=ThresholdOperator.GREATER_THAN_OR_EQUAL,
            value=0.90,
        )
        assert threshold.evaluate(0.95) == EvaluationResult.PASS
        assert threshold.evaluate(0.90) == EvaluationResult.PASS
        assert threshold.evaluate(0.85) == EvaluationResult.FAIL

    def test_between_operator(self):
        metric = Metric(
            name="Bias Parity", description="", metric_type=MetricType.FAIRNESS,
            unit="ratio",
        )
        threshold = Threshold(
            metric_id=metric.id,
            operator=ThresholdOperator.BETWEEN,
            value=0.8,
            upper_value=1.2,
        )
        assert threshold.evaluate(1.0) == EvaluationResult.PASS
        assert threshold.evaluate(0.8) == EvaluationResult.PASS
        assert threshold.evaluate(1.2) == EvaluationResult.PASS
        assert threshold.evaluate(0.7) == EvaluationResult.FAIL
        assert threshold.evaluate(1.3) == EvaluationResult.FAIL

    def test_between_requires_upper_value(self):
        metric = Metric(
            name="Test", description="", metric_type=MetricType.FAIRNESS, unit="ratio",
        )
        threshold = Threshold(
            metric_id=metric.id,
            operator=ThresholdOperator.BETWEEN,
            value=0.8,
        )
        with pytest.raises(ValueError, match="BETWEEN operator requires"):
            threshold.evaluate(1.0)

    def test_less_than_or_equal(self):
        metric = Metric(
            name="Error rate", description="", metric_type=MetricType.RELIABILITY,
            unit="ratio", higher_is_better=False,
        )
        threshold = Threshold(
            metric_id=metric.id,
            operator=ThresholdOperator.LESS_THAN_OR_EQUAL,
            value=0.05,
        )
        assert threshold.evaluate(0.05) == EvaluationResult.PASS
        assert threshold.evaluate(0.04) == EvaluationResult.PASS
        assert threshold.evaluate(0.06) == EvaluationResult.FAIL

    def test_greater_than(self):
        metric = Metric(
            name="Precision", description="", metric_type=MetricType.PERFORMANCE,
            unit="ratio",
        )
        threshold = Threshold(
            metric_id=metric.id,
            operator=ThresholdOperator.GREATER_THAN,
            value=0.90,
        )
        assert threshold.evaluate(0.91) == EvaluationResult.PASS
        assert threshold.evaluate(0.90) == EvaluationResult.FAIL
        assert threshold.evaluate(0.85) == EvaluationResult.FAIL

    def test_equals(self):
        metric = Metric(
            name="Output class", description="", metric_type=MetricType.QUALITY,
            unit="label",
        )
        threshold = Threshold(
            metric_id=metric.id,
            operator=ThresholdOperator.EQUALS,
            value=1.0,
        )
        assert threshold.evaluate(1.0) == EvaluationResult.PASS
        assert threshold.evaluate(0.0) == EvaluationResult.FAIL

    def test_warning_tier(self):
        """Warning triggers between the hard threshold and the warning threshold."""
        metric = Metric(
            name="Latency", description="", metric_type=MetricType.OPERATIONAL,
            unit="ms", higher_is_better=False,
        )
        # Fail if >= 500ms. Warn if >= 400ms.
        threshold = Threshold(
            metric_id=metric.id,
            operator=ThresholdOperator.LESS_THAN,
            value=500.0,
            warning_value=400.0,
        )
        assert threshold.evaluate(300.0) == EvaluationResult.PASS
        assert threshold.evaluate(450.0) == EvaluationResult.WARNING
        assert threshold.evaluate(550.0) == EvaluationResult.FAIL


class TestMeasurement:
    """Tests for the Measurement model."""

    def test_create_measurement(self):
        system = AISystem(
            name="Chatbot", description="", system_type=SystemType.GENERATIVE,
            owner="Test",
        )
        metric = Metric(
            name="Accuracy", description="", metric_type=MetricType.PERFORMANCE,
            unit="ratio",
        )
        measurement = Measurement(
            system_id=system.id,
            metric_id=metric.id,
            value=0.92,
            source="eval_harness",
        )
        assert measurement.value == 0.92
        assert measurement.source == "eval_harness"


class TestMeasureService:
    """Tests for the Measure service."""

    def test_evaluate_with_no_thresholds_passes(self):
        service = MeasureService()
        system = AISystem(
            name="Test", description="", system_type=SystemType.GENERATIVE,
            owner="Test",
        )
        metric = Metric(
            name="Accuracy", description="", metric_type=MetricType.PERFORMANCE,
            unit="ratio",
        )
        service.register_metric(metric)
        measurement = Measurement(
            system_id=system.id, metric_id=metric.id, value=0.50,
        )
        assert service.evaluate_measurement(measurement) == EvaluationResult.PASS

    def test_evaluate_against_multiple_thresholds_worst_wins(self):
        service = MeasureService()
        system = AISystem(
            name="Test", description="", system_type=SystemType.GENERATIVE,
            owner="Test",
        )
        metric = Metric(
            name="Latency", description="", metric_type=MetricType.OPERATIONAL,
            unit="ms", higher_is_better=False,
        )
        service.register_metric(metric)
        # Two thresholds — under 1000 and under 500
        service.set_threshold(Threshold(
            metric_id=metric.id,
            operator=ThresholdOperator.LESS_THAN,
            value=1000.0,
        ))
        service.set_threshold(Threshold(
            metric_id=metric.id,
            operator=ThresholdOperator.LESS_THAN,
            value=500.0,
        ))
        # 300ms passes both
        m1 = Measurement(system_id=system.id, metric_id=metric.id, value=300.0)
        assert service.evaluate_measurement(m1) == EvaluationResult.PASS
        # 700ms fails one (the 500 one)
        m2 = Measurement(system_id=system.id, metric_id=metric.id, value=700.0)
        assert service.evaluate_measurement(m2) == EvaluationResult.FAIL

    def test_get_failing_measurements(self):
        service = MeasureService()
        system = AISystem(
            name="Test", description="", system_type=SystemType.GENERATIVE,
            owner="Test",
        )
        metric = Metric(
            name="Accuracy", description="", metric_type=MetricType.PERFORMANCE,
            unit="ratio",
        )
        service.register_metric(metric)
        service.set_threshold(Threshold(
            metric_id=metric.id,
            operator=ThresholdOperator.GREATER_THAN_OR_EQUAL,
            value=0.90,
        ))
        # Three measurements — one passing, two failing
        service.record_measurement(Measurement(
            system_id=system.id, metric_id=metric.id, value=0.95,
        ))
        service.record_measurement(Measurement(
            system_id=system.id, metric_id=metric.id, value=0.80,
        ))
        service.record_measurement(Measurement(
            system_id=system.id, metric_id=metric.id, value=0.70,
        ))

        failing = service.get_failing_measurements(system.id)
        assert len(failing) == 2
        assert all(m.value < 0.90 for m in failing)

    def test_evaluate_measurement_returns_warning(self):
        """evaluate_measurement returns WARNING when a threshold has a warning tier."""
        service = MeasureService()
        system = AISystem(
            name="Test", description="", system_type=SystemType.GENERATIVE,
            owner="Test",
        )
        metric = Metric(
            name="Latency", description="", metric_type=MetricType.OPERATIONAL,
            unit="ms", higher_is_better=False,
        )
        service.register_metric(metric)
        # Hard fail at 500ms, warn at 400ms
        service.set_threshold(Threshold(
            metric_id=metric.id,
            operator=ThresholdOperator.LESS_THAN,
            value=500.0,
            warning_value=400.0,
        ))
        m = Measurement(system_id=system.id, metric_id=metric.id, value=450.0)
        assert service.evaluate_measurement(m) == EvaluationResult.WARNING
