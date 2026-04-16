"""Manage function service — control registration, action tracking, and triggers."""

from uuid import UUID

from aegis_rmf.core import ActionPriority, ActionStatus, EvaluationResult, RiskLevel
from aegis_rmf.manage.models import Control, MitigationAction, MonitoringTrigger


class ManageService:
    """Coordinates controls, mitigation actions, and monitoring triggers.

    This is the action layer that sits on top of MAP (which found the risks) and
    MEASURE (which evaluated metric thresholds). ManageService turns risk findings
    into tracked work and alerting rules.
    """

    # Severity ordering for fire_triggers comparisons
    _RESULT_ORDER: dict[EvaluationResult, int] = {
        EvaluationResult.PASS: 0,
        EvaluationResult.WARNING: 1,
        EvaluationResult.FAIL: 2,
    }

    # Maps a risk level to the recommended action priority (NIST Manage 1)
    _RISK_TO_PRIORITY: dict[RiskLevel, ActionPriority] = {
        RiskLevel.CRITICAL: ActionPriority.IMMEDIATE,
        RiskLevel.HIGH: ActionPriority.SHORT_TERM,
        RiskLevel.MEDIUM: ActionPriority.MEDIUM_TERM,
        RiskLevel.LOW: ActionPriority.LONG_TERM,
    }

    # Sort key for get_open_actions (IMMEDIATE = highest urgency = 0)
    _PRIORITY_ORDER: dict[ActionPriority, int] = {
        ActionPriority.IMMEDIATE: 0,
        ActionPriority.SHORT_TERM: 1,
        ActionPriority.MEDIUM_TERM: 2,
        ActionPriority.LONG_TERM: 3,
    }

    def __init__(self) -> None:
        self._controls: list[Control] = []
        self._actions: list[MitigationAction] = []
        self._triggers: list[MonitoringTrigger] = []

    # --- Registration ---

    def register_control(self, control: Control) -> None:
        """Register a risk control."""
        self._controls.append(control)

    def add_action(self, action: MitigationAction) -> None:
        """Register a mitigation action."""
        self._actions.append(action)

    def add_trigger(self, trigger: MonitoringTrigger) -> None:
        """Register a monitoring trigger."""
        self._triggers.append(trigger)

    # --- Queries ---

    def get_controls_for_system(self, system_id: UUID) -> list[Control]:
        """Return all controls registered for a given system."""
        return [c for c in self._controls if c.system_id == system_id]

    def get_open_actions(self, system_id: UUID) -> list[MitigationAction]:
        """Return OPEN and IN_PROGRESS actions for a system, sorted by priority.

        Highest priority (IMMEDIATE) is returned first — satisfies NIST Manage 1's
        requirement that highest-priority risks are addressed first.
        """
        active = {ActionStatus.OPEN, ActionStatus.IN_PROGRESS}
        open_actions = [
            a for a in self._actions
            if a.system_id == system_id and a.status in active
        ]
        return sorted(open_actions, key=lambda a: self._PRIORITY_ORDER[a.priority])

    def get_actions_for_risk(self, risk_id: UUID) -> list[MitigationAction]:
        """Return all actions targeting a specific identified risk."""
        return [a for a in self._actions if a.risk_id == risk_id]

    # --- Analysis ---

    def get_unaddressed_risks(
        self, system_id: UUID, risk_ids: list[UUID]
    ) -> list[UUID]:
        """Return risk IDs that have no active treatment decision.

        A risk is considered addressed if it has at least one action in
        OPEN, IN_PROGRESS, ACCEPTED, or TRANSFERRED status. ACCEPTED and
        TRANSFERRED represent documented risk treatment decisions (per NIST
        Manage 4) — they count as addressed even though the risk is not
        technically mitigated.

        A risk with only RESOLVED actions is treated as unaddressed: the
        action completed but the risk was never formally accepted or closed,
        so it surfaces here until someone makes an explicit decision.
        """
        addressed_statuses = {
            ActionStatus.OPEN,
            ActionStatus.IN_PROGRESS,
            ActionStatus.ACCEPTED,
            ActionStatus.TRANSFERRED,
        }
        unaddressed = []
        for risk_id in risk_ids:
            actions = [
                a for a in self.get_actions_for_risk(risk_id)
                if a.system_id == system_id
            ]
            has_active = any(a.status in addressed_statuses for a in actions)
            if not has_active:
                unaddressed.append(risk_id)
        return unaddressed

    def fire_triggers(
        self,
        system_id: UUID,
        evaluation_results: dict[UUID, EvaluationResult],
    ) -> list[MonitoringTrigger]:
        """Return triggers whose minimum severity threshold has been met or exceeded.

        A trigger fires when the actual evaluation result severity is greater than
        or equal to the trigger's minimum_result severity
        (PASS=0, WARNING=1, FAIL=2).

        Missing metric IDs in evaluation_results are silently skipped — this
        supports partial/incremental evaluation where only changed metrics are
        passed on each call.
        """
        fired = []
        for trigger in self._triggers:
            if trigger.system_id != system_id:
                continue
            actual = evaluation_results.get(trigger.metric_id)
            if actual is None:
                continue
            if self._RESULT_ORDER[actual] >= self._RESULT_ORDER[trigger.minimum_result]:
                fired.append(trigger)
        return fired

    @classmethod
    def priority_for_risk_level(cls, risk_level: RiskLevel) -> ActionPriority:
        """Map a risk level to the recommended action priority.

        CRITICAL → IMMEDIATE, HIGH → SHORT_TERM,
        MEDIUM → MEDIUM_TERM, LOW → LONG_TERM.

        Useful when auto-creating MitigationActions directly from MAP's
        IdentifiedRisk objects without instantiating the service.
        """
        return cls._RISK_TO_PRIORITY[risk_level]
