"""Govern function service — policy evaluation and accountability."""

from aegis_rmf.core import AISystem
from aegis_rmf.govern.models import GovernancePolicy


class GovernService:
    """Evaluates which policies apply to which AI systems.

    Think of this like an AWS Config evaluator — it takes a set of
    rules and a set of resources, and tells you which rules apply where.
    """

    def __init__(self) -> None:
        self._policies: list[GovernancePolicy] = []

    def add_policy(self, policy: GovernancePolicy) -> None:
        """Register a policy."""
        self._policies.append(policy)

    def get_applicable_policies(self, system: AISystem) -> list[GovernancePolicy]:
        """Return all active policies that apply to a given AI system."""
        return [
            policy for policy in self._policies
            if policy.applies_to(system.risk_level, system.lifecycle_stage,
                                 system.system_type)
        ]
