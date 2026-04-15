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


class PolicyStatus(str, Enum):
    """Lifecycle state of a governance policy."""
    DRAFT = "draft"
    ACTIVE = "active"
    UNDER_REVIEW = "under_review"
    DEPRECATED = "deprecated"


class RoleType(str, Enum):
    """Standard governance roles for AI systems."""
    SYSTEM_OWNER = "system_owner"
    RISK_OFFICER = "risk_officer"
    ETHICS_REVIEWER = "ethics_reviewer"
    TECHNICAL_LEAD = "technical_lead"
    DATA_STEWARD = "data_steward"
    COMPLIANCE_OFFICER = "compliance_officer"


class StakeholderType(str, Enum):
    """Categories of stakeholders affected by an AI system."""
    INTERNAL_USER = "internal_user"
    EXTERNAL_CUSTOMER = "external_customer"
    DATA_SUBJECT = "data_subject"
    REGULATOR = "regulator"
    VULNERABLE_POPULATION = "vulnerable_population"
    THIRD_PARTY = "third_party"
    SOCIETY = "society"


class DeploymentEnvironment(str, Enum):
    """Where an AI system runs."""
    ON_PREMISES = "on_premises"
    CLOUD_PUBLIC = "cloud_public"
    CLOUD_PRIVATE = "cloud_private"
    HYBRID = "hybrid"
    EDGE = "edge"


class DataSensitivity(str, Enum):
    """Sensitivity classification for data the system uses."""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    REGULATED = "regulated"
