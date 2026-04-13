"""Tests for the Govern function."""

from aegis_rmf.core import (
    AISystem,
    LifecycleStage,
    PolicyStatus,
    RiskLevel,
    RoleType,
    SystemType,
)
from aegis_rmf.govern import (
    AccountabilityMapping,
    GovernancePolicy,
    GovernService,
    PolicyCondition,
    Role,
)


class TestPolicyCondition:
    """Tests for policy condition matching."""

    def test_empty_condition_matches_everything(self):
        condition = PolicyCondition()
        assert condition.matches(
            risk_level=RiskLevel.LOW,
            lifecycle_stage=LifecycleStage.PRODUCTION,
            system_type=SystemType.GENERATIVE,
        )

    def test_risk_level_filter(self):
        condition = PolicyCondition(risk_levels=[RiskLevel.HIGH, RiskLevel.CRITICAL])
        assert condition.matches(
            risk_level=RiskLevel.HIGH,
            lifecycle_stage=LifecycleStage.PRODUCTION,
            system_type=SystemType.GENERATIVE,
        )
        assert not condition.matches(
            risk_level=RiskLevel.LOW,
            lifecycle_stage=LifecycleStage.PRODUCTION,
            system_type=SystemType.GENERATIVE,
        )

    def test_multiple_filters_all_must_match(self):
        condition = PolicyCondition(
            risk_levels=[RiskLevel.HIGH],
            lifecycle_stages=[LifecycleStage.PRODUCTION],
        )
        # Both match
        assert condition.matches(
            risk_level=RiskLevel.HIGH,
            lifecycle_stage=LifecycleStage.PRODUCTION,
            system_type=SystemType.GENERATIVE,
        )
        # Risk matches but lifecycle doesn't
        assert not condition.matches(
            risk_level=RiskLevel.HIGH,
            lifecycle_stage=LifecycleStage.TESTING,
            system_type=SystemType.GENERATIVE,
        )


class TestGovernancePolicy:
    """Tests for governance policies."""

    def test_draft_policy_applies_to_nothing(self):
        policy = GovernancePolicy(
            name="Test Policy",
            description="A test",
            status=PolicyStatus.DRAFT,
            owner="Test Owner",
        )
        assert not policy.applies_to(
            risk_level=RiskLevel.HIGH,
            lifecycle_stage=LifecycleStage.PRODUCTION,
            system_type=SystemType.GENERATIVE,
        )

    def test_active_policy_with_matching_condition(self):
        policy = GovernancePolicy(
            name="High Risk Review",
            description="All high-risk systems need quarterly review",
            status=PolicyStatus.ACTIVE,
            condition=PolicyCondition(risk_levels=[RiskLevel.HIGH, RiskLevel.CRITICAL]),
            requirements=["Quarterly assessment", "Human-in-the-loop review"],
            owner="Risk Team",
        )
        assert policy.applies_to(
            risk_level=RiskLevel.HIGH,
            lifecycle_stage=LifecycleStage.PRODUCTION,
            system_type=SystemType.GENERATIVE,
        )
        assert not policy.applies_to(
            risk_level=RiskLevel.LOW,
            lifecycle_stage=LifecycleStage.PRODUCTION,
            system_type=SystemType.GENERATIVE,
        )


class TestGovernService:
    """Tests for the Govern service — policy matching."""

    def test_get_applicable_policies(self):
        service = GovernService()

        high_risk_policy = GovernancePolicy(
            name="High Risk Controls",
            description="Extra controls for high-risk systems",
            status=PolicyStatus.ACTIVE,
            condition=PolicyCondition(risk_levels=[RiskLevel.HIGH, RiskLevel.CRITICAL]),
            requirements=["Monthly assessment"],
            owner="Risk Team",
        )
        generative_policy = GovernancePolicy(
            name="GenAI Content Filter",
            description="All generative systems need content filtering",
            status=PolicyStatus.ACTIVE,
            condition=PolicyCondition(system_types=[SystemType.GENERATIVE]),
            requirements=["Content filtering enabled"],
            owner="Safety Team",
        )
        draft_policy = GovernancePolicy(
            name="Future Policy",
            description="Not yet active",
            status=PolicyStatus.DRAFT,
            owner="Policy Team",
        )

        service.add_policy(high_risk_policy)
        service.add_policy(generative_policy)
        service.add_policy(draft_policy)

        # High-risk generative system — both active policies apply
        high_risk_genai = AISystem(
            name="Customer Chatbot",
            description="Customer-facing generative AI",
            system_type=SystemType.GENERATIVE,
            owner="Product Team",
            risk_level=RiskLevel.HIGH,
            lifecycle_stage=LifecycleStage.PRODUCTION,
        )
        applicable = service.get_applicable_policies(high_risk_genai)
        assert len(applicable) == 2

        # Low-risk classification system — neither policy applies
        low_risk_classifier = AISystem(
            name="Spam Filter",
            description="Internal email spam detection",
            system_type=SystemType.CLASSIFICATION,
            owner="IT Team",
            risk_level=RiskLevel.LOW,
            lifecycle_stage=LifecycleStage.PRODUCTION,
        )
        applicable = service.get_applicable_policies(low_risk_classifier)
        assert len(applicable) == 0


class TestRole:
    """Tests for governance roles."""

    def test_create_role(self):
        role = Role(
            role_type=RoleType.RISK_OFFICER,
            name="AI Risk Officer",
            description="Oversees AI risk management",
            responsibilities=[
                "Review risk assessments",
                "Approve high-risk deployments",
                "Escalate critical findings",
            ],
        )
        assert role.role_type == RoleType.RISK_OFFICER
        assert len(role.responsibilities) == 3


class TestAccountabilityMapping:
    """Tests for accountability mappings."""

    def test_create_mapping(self):
        system = AISystem(
            name="Test System",
            description="For testing",
            system_type=SystemType.GENERATIVE,
            owner="Test Owner",
        )
        role = Role(
            role_type=RoleType.SYSTEM_OWNER,
            name="System Owner",
            description="Responsible for the system",
        )
        policy = GovernancePolicy(
            name="Test Policy",
            description="A policy",
            status=PolicyStatus.ACTIVE,
            owner="Policy Team",
        )
        mapping = AccountabilityMapping(
            system_id=system.id,
            role_id=role.id,
            assignee="jody@example.com",
            policy_ids=[policy.id],
        )
        assert mapping.system_id == system.id
        assert mapping.assignee == "jody@example.com"
