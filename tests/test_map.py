"""Tests for the Map function."""

from aegis_rmf.core import (
    AISystem,
    DataSensitivity,
    DeploymentEnvironment,
    RiskCategory,
    RiskLevel,
    StakeholderType,
    SystemType,
)
from aegis_rmf.map import (
    DataSource,
    IdentifiedRisk,
    MapService,
    Stakeholder,
    SystemContext,
)


class TestSystemContext:
    """Tests for the SystemContext model."""

    def test_create_context(self):
        system = AISystem(
            name="Customer Chatbot",
            description="Generative AI for customer service",
            system_type=SystemType.GENERATIVE,
            owner="Product Team",
        )
        context = SystemContext(
            system_id=system.id,
            purpose="Answer customer service questions",
            intended_use="Tier-1 customer support automation",
            out_of_scope_uses=["Medical advice", "Legal advice"],
            deployment_environment=DeploymentEnvironment.CLOUD_PUBLIC,
            data_sources=[
                DataSource(
                    name="Product knowledge base",
                    description="Internal product documentation",
                    sensitivity=DataSensitivity.INTERNAL,
                ),
                DataSource(
                    name="Customer interaction history",
                    description="Past chat transcripts",
                    sensitivity=DataSensitivity.CONFIDENTIAL,
                    contains_pii=True,
                ),
            ],
            dependencies=["AWS Bedrock", "Internal RAG service"],
        )
        assert context.system_id == system.id
        assert len(context.data_sources) == 2
        assert context.data_sources[1].contains_pii is True


class TestStakeholder:
    """Tests for the Stakeholder model."""

    def test_create_stakeholder(self):
        system = AISystem(
            name="Test System",
            description="For testing",
            system_type=SystemType.GENERATIVE,
            owner="Test Owner",
        )
        stakeholder = Stakeholder(
            system_id=system.id,
            name="Customers",
            stakeholder_type=StakeholderType.EXTERNAL_CUSTOMER,
            description="End users of the chatbot",
            impact_description="Receive AI-generated responses to support questions",
        )
        assert stakeholder.stakeholder_type == StakeholderType.EXTERNAL_CUSTOMER


class TestIdentifiedRisk:
    """Tests for the IdentifiedRisk model."""

    def test_create_risk(self):
        system = AISystem(
            name="Test System",
            description="For testing",
            system_type=SystemType.GENERATIVE,
            owner="Test Owner",
        )
        risk = IdentifiedRisk(
            system_id=system.id,
            category=RiskCategory.PRIVACY,
            level=RiskLevel.HIGH,
            title="PII exposure in training data",
            description="Customer chat logs used for training contain unredacted PII",
        )
        assert risk.category == RiskCategory.PRIVACY
        assert risk.level == RiskLevel.HIGH


class TestMapService:
    """Tests for the Map service — risk aggregation."""

    def test_build_profile_from_no_risks(self):
        service = MapService()
        system = AISystem(
            name="Clean System",
            description="No risks",
            system_type=SystemType.CLASSIFICATION,
            owner="Test Owner",
        )
        profile = service.build_risk_profile(system.id)
        assert profile.overall_risk == RiskLevel.LOW
        assert profile.risk_scores == {}

    def test_aggregate_takes_highest_per_category(self):
        service = MapService()
        system = AISystem(
            name="Test System",
            description="For testing",
            system_type=SystemType.GENERATIVE,
            owner="Test Owner",
        )
        # Two privacy risks — high and medium
        service.add_risk(IdentifiedRisk(
            system_id=system.id,
            category=RiskCategory.PRIVACY,
            level=RiskLevel.HIGH,
            title="PII in training data",
            description="Unredacted PII",
        ))
        service.add_risk(IdentifiedRisk(
            system_id=system.id,
            category=RiskCategory.PRIVACY,
            level=RiskLevel.MEDIUM,
            title="Logging includes user IDs",
            description="Log retention is 90 days",
        ))
        # One bias risk
        service.add_risk(IdentifiedRisk(
            system_id=system.id,
            category=RiskCategory.BIAS,
            level=RiskLevel.MEDIUM,
            title="Demographic gap",
            description="Lower accuracy for users under 25",
        ))

        profile = service.build_risk_profile(system.id, context="Initial assessment")
        # Privacy should be HIGH (max of high and medium)
        assert profile.risk_scores[RiskCategory.PRIVACY] == RiskLevel.HIGH
        assert profile.risk_scores[RiskCategory.BIAS] == RiskLevel.MEDIUM
        # Overall should be HIGH (max across all categories)
        assert profile.overall_risk == RiskLevel.HIGH
        assert profile.context == "Initial assessment"

    def test_get_risks_for_system_filters_correctly(self):
        service = MapService()
        system_a_id = AISystem(
            name="System A",
            description="A",
            system_type=SystemType.GENERATIVE,
            owner="Owner A",
        ).id
        system_b_id = AISystem(
            name="System B",
            description="B",
            system_type=SystemType.GENERATIVE,
            owner="Owner B",
        ).id

        service.add_risk(IdentifiedRisk(
            system_id=system_a_id,
            category=RiskCategory.SAFETY,
            level=RiskLevel.HIGH,
            title="Risk A",
            description="A risk",
        ))
        service.add_risk(IdentifiedRisk(
            system_id=system_b_id,
            category=RiskCategory.SAFETY,
            level=RiskLevel.LOW,
            title="Risk B",
            description="A risk",
        ))

        a_risks = service.get_risks_for_system(system_a_id)
        assert len(a_risks) == 1
        assert a_risks[0].title == "Risk A"
