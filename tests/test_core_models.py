"""Tests for core domain models."""

from aegis_rmf.core import (
    AISystem,
    Assessment,
    AssessmentStatus,
    AssessmentType,
    ComplianceArtifact,
    ArtifactType,
    LifecycleStage,
    RiskCategory,
    RiskLevel,
    RiskProfile,
    SystemType,
)


class TestAISystem:
    """Tests for the AISystem model."""

    def test_create_minimal(self):
        system = AISystem(
            name="Fraud Detector",
            description="Detects fraudulent transactions",
            system_type=SystemType.CLASSIFICATION,
            owner="ML Team",
        )
        assert system.name == "Fraud Detector"
        assert system.lifecycle_stage == LifecycleStage.DESIGN
        assert system.risk_level == RiskLevel.MEDIUM
        assert system.id is not None

    def test_create_full(self):
        system = AISystem(
            name="Chatbot",
            description="Customer service chatbot",
            system_type=SystemType.GENERATIVE,
            owner="Product Team",
            lifecycle_stage=LifecycleStage.PRODUCTION,
            risk_level=RiskLevel.HIGH,
            tags=["customer-facing", "generative"],
        )
        assert system.lifecycle_stage == LifecycleStage.PRODUCTION
        assert "generative" in system.tags

    def test_json_round_trip(self):
        system = AISystem(
            name="Recommender",
            description="Product recommendations",
            system_type=SystemType.RECOMMENDATION,
            owner="Data Team",
        )
        json_str = system.model_dump_json()
        restored = AISystem.model_validate_json(json_str)
        assert restored.name == system.name
        assert restored.id == system.id


class TestRiskProfile:
    """Tests for the RiskProfile model."""

    def test_create_with_scores(self):
        system = AISystem(
            name="Test System",
            description="For testing",
            system_type=SystemType.PREDICTIVE,
            owner="Test Owner",
        )
        profile = RiskProfile(
            system_id=system.id,
            risk_scores={
                RiskCategory.BIAS: RiskLevel.HIGH,
                RiskCategory.PRIVACY: RiskLevel.MEDIUM,
                RiskCategory.SAFETY: RiskLevel.LOW,
            },
            overall_risk=RiskLevel.HIGH,
            context="Healthcare model with sensitive data",
        )
        assert profile.risk_scores[RiskCategory.BIAS] == RiskLevel.HIGH
        assert profile.system_id == system.id

    def test_snapshot_versioning(self):
        """Two profiles for the same system represent different points in time."""
        system = AISystem(
            name="Evolving System",
            description="Risk changes over time",
            system_type=SystemType.PREDICTIVE,
            owner="Test Owner",
        )
        profile_v1 = RiskProfile(
            system_id=system.id,
            overall_risk=RiskLevel.LOW,
        )
        profile_v2 = RiskProfile(
            system_id=system.id,
            overall_risk=RiskLevel.HIGH,
            context="Retrained on new data, bias detected",
        )
        assert profile_v1.id != profile_v2.id
        assert profile_v1.system_id == profile_v2.system_id
        assert profile_v1.overall_risk != profile_v2.overall_risk


class TestAssessment:
    """Tests for the Assessment model."""

    def test_create_planned(self):
        system = AISystem(
            name="Test System",
            description="For testing",
            system_type=SystemType.GENERATIVE,
            owner="Test Owner",
        )
        assessment = Assessment(
            system_id=system.id,
            assessment_type=AssessmentType.PRE_DEPLOYMENT,
            assessor="Governance Team",
        )
        assert assessment.status == AssessmentStatus.PLANNED
        assert assessment.completed_at is None

    def test_assessment_with_findings(self):
        system = AISystem(
            name="Test System",
            description="For testing",
            system_type=SystemType.GENERATIVE,
            owner="Test Owner",
        )
        assessment = Assessment(
            system_id=system.id,
            assessment_type=AssessmentType.PERIODIC,
            status=AssessmentStatus.COMPLETED,
            assessor="Automated Eval Harness",
            findings=[
                "Bias detected in age demographic",
                "Latency exceeds threshold at p99",
            ],
        )
        assert len(assessment.findings) == 2


class TestComplianceArtifact:
    """Tests for the ComplianceArtifact model."""

    def test_create_artifact(self):
        artifact = ComplianceArtifact(
            system_id="550e8400-e29b-41d4-a716-446655440000",
            artifact_type=ArtifactType.TEST_RESULT,
            title="Bias evaluation results Q1 2026",
            created_by="Eval Harness",
        )
        assert artifact.framework == "NIST AI RMF"
        assert artifact.assessment_id is None
