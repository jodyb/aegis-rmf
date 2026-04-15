"""Map function service — risk identification and aggregation."""

from uuid import UUID

from aegis_rmf.core import RiskCategory, RiskLevel, RiskProfile
from aegis_rmf.map.models import IdentifiedRisk


class MapService:
    """Identifies risks and aggregates them into RiskProfile snapshots.

    The Map function produces the risk picture that everything else
    uses. Think of it like a vulnerability scanner — it finds individual
    issues and rolls them up into an overall risk score.
    """

    # Ordering for risk levels — used to find the maximum
    _RISK_ORDER = {
        RiskLevel.LOW: 1,
        RiskLevel.MEDIUM: 2,
        RiskLevel.HIGH: 3,
        RiskLevel.CRITICAL: 4,
    }

    def __init__(self) -> None:
        self._identified_risks: list[IdentifiedRisk] = []

    def add_risk(self, risk: IdentifiedRisk) -> None:
        """Register an identified risk."""
        self._identified_risks.append(risk)

    def get_risks_for_system(self, system_id: UUID) -> list[IdentifiedRisk]:
        """Return all identified risks for a given system."""
        return [r for r in self._identified_risks if r.system_id == system_id]

    def build_risk_profile(self, system_id: UUID, context: str = "") -> RiskProfile:
        """Aggregate identified risks into a RiskProfile snapshot.

        For each risk category, takes the highest risk level found.
        Like a security scanner that reports the worst CVE per category.
        """
        risks = self.get_risks_for_system(system_id)
        scores: dict[RiskCategory, RiskLevel] = {}

        for risk in risks:
            current = scores.get(risk.category)
            if current is None or self._RISK_ORDER[risk.level] > self._RISK_ORDER[current]:
                scores[risk.category] = risk.level

        overall = max(
            (level for level in scores.values()),
            key=lambda lvl: self._RISK_ORDER[lvl],
            default=RiskLevel.LOW,
        )

        return RiskProfile(
            system_id=system_id,
            risk_scores=scores,
            overall_risk=overall,
            context=context,
        )
