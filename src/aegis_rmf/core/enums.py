"""Shared enumerations used across all NIST AI RMF functions."""

from enum import Enum


class RiskLevel(str, Enum):
    """Classification of risk severity."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class LifecycleStage(str, Enum):
    """Where an AI system sits in its lifecycle."""
    DESIGN = "design"
    DEVELOPMENT = "development"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    PRODUCTION = "production"
    MONITORING = "monitoring"
    RETIRED = "retired"


class SystemType(str, Enum):
    """The kind of AI system."""
    GENERATIVE = "generative"
    PREDICTIVE = "predictive"
    CLASSIFICATION = "classification"
    RECOMMENDATION = "recommendation"
    DECISION_SUPPORT = "decision_support"
    AUTONOMOUS = "autonomous"


class AssessmentType(str, Enum):
    """What triggered the assessment."""
    INITIAL = "initial"
    PERIODIC = "periodic"
    INCIDENT_TRIGGERED = "incident_triggered"
    PRE_DEPLOYMENT = "pre_deployment"
    AD_HOC = "ad_hoc"


class AssessmentStatus(str, Enum):
    """Current state of an assessment."""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ArtifactType(str, Enum):
    """What kind of compliance evidence this is."""
    POLICY_DOCUMENT = "policy_document"
    TEST_RESULT = "test_result"
    APPROVAL_RECORD = "approval_record"
    AUDIT_LOG = "audit_log"
    RISK_ASSESSMENT = "risk_assessment"
    MONITORING_REPORT = "monitoring_report"


class RiskCategory(str, Enum):
    """Dimensions along which we assess risk."""
    BIAS = "bias"
    SAFETY = "safety"
    PRIVACY = "privacy"
    SECURITY = "security"
    TRANSPARENCY = "transparency"
    RELIABILITY = "reliability"
    ACCOUNTABILITY = "accountability"
