"""Tests for the Manage function."""

from datetime import datetime
from uuid import uuid4

from aegis_rmf.core import (
    ActionPriority,
    ActionStatus,
    AISystem,
    ControlStatus,
    EvaluationResult,
    RiskCategory,
    RiskLevel,
    SystemType,
)
from aegis_rmf.manage import Control, ManageService, MitigationAction, MonitoringTrigger

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _system(**kwargs: object) -> AISystem:
    return AISystem(
        name="Test System",
        description="",
        system_type=SystemType.CLASSIFICATION,
        owner="Test",
        **kwargs,  # type: ignore[arg-type]
    )


def _action(
    system_id: object,
    risk_id: object,
    priority: ActionPriority = ActionPriority.MEDIUM_TERM,
    status: ActionStatus = ActionStatus.OPEN,
    **kwargs: object,
) -> MitigationAction:
    return MitigationAction(
        system_id=system_id,  # type: ignore[arg-type]
        risk_id=risk_id,  # type: ignore[arg-type]
        title="Fix it",
        description="",
        priority=priority,
        assignee="alice@example.com",
        due_date=datetime(2026, 12, 31),
        status=status,
        **kwargs,  # type: ignore[arg-type]
    )


# ---------------------------------------------------------------------------
# TestControl
# ---------------------------------------------------------------------------

class TestControl:
    """Tests for the Control model."""

    def test_create_minimal(self):
        system = _system()
        control = Control(
            system_id=system.id,
            name="Input validation",
            description="Reject malformed inputs at the API boundary",
        )
        assert control.system_id == system.id
        assert control.status == ControlStatus.PLANNED
        assert control.categories == []
        assert control.implementation_notes == ""
        assert control.id is not None
        assert control.created_at is not None

    def test_create_full(self):
        system = _system()
        control = Control(
            system_id=system.id,
            name="Demographic parity constraint",
            description="Post-hoc fairness calibration applied at inference time",
            status=ControlStatus.ACTIVE,
            categories=[RiskCategory.BIAS, RiskCategory.TRANSPARENCY],
            implementation_notes="Deployed via SageMaker post-processing step",
        )
        assert control.status == ControlStatus.ACTIVE
        assert RiskCategory.BIAS in control.categories
        assert RiskCategory.TRANSPARENCY in control.categories

    def test_json_round_trip(self):
        system = _system()
        control = Control(
            system_id=system.id,
            name="PII redaction",
            description="Strips PII from model outputs",
            categories=[RiskCategory.PRIVACY],
        )
        serialized = control.model_dump_json()
        restored = Control.model_validate_json(serialized)
        assert restored.id == control.id
        assert restored.system_id == control.system_id
        assert restored.categories == [RiskCategory.PRIVACY]


# ---------------------------------------------------------------------------
# TestMitigationAction
# ---------------------------------------------------------------------------

class TestMitigationAction:
    """Tests for the MitigationAction model."""

    def test_create_minimal(self):
        system = _system()
        risk_id = uuid4()
        action = _action(system_id=system.id, risk_id=risk_id)
        assert action.system_id == system.id
        assert action.risk_id == risk_id
        assert action.status == ActionStatus.OPEN
        assert action.control_id is None
        assert action.resolution_notes == ""

    def test_create_full(self):
        system = _system()
        risk_id = uuid4()
        control_id = uuid4()
        action = MitigationAction(
            system_id=system.id,
            risk_id=risk_id,
            control_id=control_id,
            title="Deploy bias filter",
            description="Apply post-processing calibration",
            status=ActionStatus.IN_PROGRESS,
            priority=ActionPriority.SHORT_TERM,
            assignee="alice@example.com",
            due_date=datetime(2026, 5, 1),
            resolution_notes="In code review",
        )
        assert action.control_id == control_id
        assert action.status == ActionStatus.IN_PROGRESS
        assert action.priority == ActionPriority.SHORT_TERM

    def test_json_round_trip(self):
        system = _system()
        action = _action(system_id=system.id, risk_id=uuid4())
        restored = MitigationAction.model_validate_json(action.model_dump_json())
        assert restored.id == action.id
        assert restored.system_id == action.system_id


# ---------------------------------------------------------------------------
# TestMonitoringTrigger
# ---------------------------------------------------------------------------

class TestMonitoringTrigger:
    """Tests for the MonitoringTrigger model."""

    def test_create_trigger(self):
        system = _system()
        metric_id = uuid4()
        trigger = MonitoringTrigger(
            system_id=system.id,
            metric_id=metric_id,
            minimum_result=EvaluationResult.WARNING,
            action_description="Open P1 incident and notify risk officer",
            assignee="risk-officer@example.com",
        )
        assert trigger.system_id == system.id
        assert trigger.metric_id == metric_id
        assert trigger.minimum_result == EvaluationResult.WARNING
        assert trigger.id is not None
        assert trigger.created_at is not None


# ---------------------------------------------------------------------------
# TestManageService
# ---------------------------------------------------------------------------

class TestManageService:
    """Tests for the Manage service — action tracking, priority, and triggers."""

    def test_register_and_retrieve_controls(self):
        service = ManageService()
        system_a = _system()
        system_b = _system()

        service.register_control(Control(
            system_id=system_a.id, name="A1", description="",
        ))
        service.register_control(Control(
            system_id=system_a.id, name="A2", description="",
        ))
        service.register_control(Control(
            system_id=system_b.id, name="B1", description="",
        ))

        assert len(service.get_controls_for_system(system_a.id)) == 2
        assert len(service.get_controls_for_system(system_b.id)) == 1

    def test_get_open_actions_filters_by_status(self):
        service = ManageService()
        system = _system()
        risk_id = uuid4()

        for status in ActionStatus:
            service.add_action(_action(
                system_id=system.id, risk_id=risk_id, status=status,
            ))

        open_actions = service.get_open_actions(system.id)
        assert len(open_actions) == 2
        statuses = {a.status for a in open_actions}
        assert statuses == {ActionStatus.OPEN, ActionStatus.IN_PROGRESS}

    def test_get_open_actions_sorted_by_priority(self):
        """Highest priority (IMMEDIATE) should come first — NIST Manage 1."""
        service = ManageService()
        system = _system()
        risk_id = uuid4()

        # Add in reverse priority order
        for p in [
            ActionPriority.LONG_TERM,
            ActionPriority.IMMEDIATE,
            ActionPriority.SHORT_TERM,
            ActionPriority.MEDIUM_TERM,
        ]:
            service.add_action(_action(
                system_id=system.id, risk_id=risk_id, priority=p,
            ))

        ordered = service.get_open_actions(system.id)
        priorities = [a.priority for a in ordered]
        assert priorities == [
            ActionPriority.IMMEDIATE,
            ActionPriority.SHORT_TERM,
            ActionPriority.MEDIUM_TERM,
            ActionPriority.LONG_TERM,
        ]

    def test_get_actions_for_risk(self):
        service = ManageService()
        system = _system()
        risk_a = uuid4()
        risk_b = uuid4()

        service.add_action(_action(system_id=system.id, risk_id=risk_a))
        service.add_action(_action(system_id=system.id, risk_id=risk_a))
        service.add_action(_action(system_id=system.id, risk_id=risk_b))

        assert len(service.get_actions_for_risk(risk_a)) == 2
        assert len(service.get_actions_for_risk(risk_b)) == 1

    def test_get_unaddressed_risks_no_actions(self):
        service = ManageService()
        system = _system()
        risk_ids = [uuid4(), uuid4(), uuid4()]

        unaddressed = service.get_unaddressed_risks(system.id, risk_ids)
        assert set(unaddressed) == set(risk_ids)

    def test_get_unaddressed_risks_with_active_actions(self):
        service = ManageService()
        system = _system()
        risk_a = uuid4()
        risk_b = uuid4()
        risk_c = uuid4()

        service.add_action(
            _action(system_id=system.id, risk_id=risk_a, status=ActionStatus.OPEN)
        )
        service.add_action(_action(
            system_id=system.id, risk_id=risk_b, status=ActionStatus.IN_PROGRESS,
        ))
        # risk_c has no action

        unaddressed = service.get_unaddressed_risks(system.id, [risk_a, risk_b, risk_c])
        assert unaddressed == [risk_c]

    def test_get_unaddressed_risks_accepted_is_addressed(self):
        """ACCEPTED is a documented treatment decision — addressed per Manage 4."""
        service = ManageService()
        system = _system()
        risk_a = uuid4()

        service.add_action(
            _action(system_id=system.id, risk_id=risk_a, status=ActionStatus.ACCEPTED)
        )

        unaddressed = service.get_unaddressed_risks(system.id, [risk_a])
        assert unaddressed == []

    def test_get_unaddressed_risks_transferred_is_addressed(self):
        """TRANSFERRED (risk moved to a third party) is a valid treatment decision."""
        service = ManageService()
        system = _system()
        risk_a = uuid4()

        service.add_action(_action(
            system_id=system.id, risk_id=risk_a, status=ActionStatus.TRANSFERRED,
        ))

        unaddressed = service.get_unaddressed_risks(system.id, [risk_a])
        assert unaddressed == []

    def test_get_unaddressed_risks_resolved_only_is_unaddressed(self):
        """RESOLVED action completes the task but doesn't formally close the risk.
        The risk surfaces as unaddressed until explicitly accepted or transferred.
        """
        service = ManageService()
        system = _system()
        risk_a = uuid4()

        service.add_action(
            _action(system_id=system.id, risk_id=risk_a, status=ActionStatus.RESOLVED)
        )

        unaddressed = service.get_unaddressed_risks(system.id, [risk_a])
        assert unaddressed == [risk_a]

    def test_fire_triggers_fail_fires_on_warning_trigger(self):
        """FAIL severity >= WARNING minimum → trigger fires."""
        service = ManageService()
        system = _system()
        metric_id = uuid4()

        service.add_trigger(MonitoringTrigger(
            system_id=system.id,
            metric_id=metric_id,
            minimum_result=EvaluationResult.WARNING,
            action_description="Page risk officer",
            assignee="risk@example.com",
        ))

        fired = service.fire_triggers(system.id, {metric_id: EvaluationResult.FAIL})
        assert len(fired) == 1

    def test_fire_triggers_warning_fires_on_warning_trigger(self):
        """WARNING severity == WARNING minimum → trigger fires."""
        service = ManageService()
        system = _system()
        metric_id = uuid4()

        service.add_trigger(MonitoringTrigger(
            system_id=system.id,
            metric_id=metric_id,
            minimum_result=EvaluationResult.WARNING,
            action_description="Page risk officer",
            assignee="risk@example.com",
        ))

        fired = service.fire_triggers(system.id, {metric_id: EvaluationResult.WARNING})
        assert len(fired) == 1

    def test_fire_triggers_pass_does_not_fire_warning_trigger(self):
        """PASS severity < WARNING minimum → trigger does not fire."""
        service = ManageService()
        system = _system()
        metric_id = uuid4()

        service.add_trigger(MonitoringTrigger(
            system_id=system.id,
            metric_id=metric_id,
            minimum_result=EvaluationResult.WARNING,
            action_description="Page risk officer",
            assignee="risk@example.com",
        ))

        fired = service.fire_triggers(system.id, {metric_id: EvaluationResult.PASS})
        assert fired == []

    def test_fire_triggers_missing_metric_skips_silently(self):
        """Triggers referencing metrics absent from evaluation_results are skipped."""
        service = ManageService()
        system = _system()

        service.add_trigger(MonitoringTrigger(
            system_id=system.id,
            metric_id=uuid4(),  # not present in evaluation_results
            minimum_result=EvaluationResult.WARNING,
            action_description="Page risk officer",
            assignee="risk@example.com",
        ))

        fired = service.fire_triggers(system.id, {uuid4(): EvaluationResult.FAIL})
        assert fired == []

    def test_fire_triggers_system_isolation(self):
        """Triggers for system_b must not fire when evaluating system_a."""
        service = ManageService()
        system_a = _system()
        system_b = _system()
        metric_id = uuid4()

        service.add_trigger(MonitoringTrigger(
            system_id=system_b.id,
            metric_id=metric_id,
            minimum_result=EvaluationResult.WARNING,
            action_description="Notify system B owner",
            assignee="owner-b@example.com",
        ))

        fired = service.fire_triggers(system_a.id, {metric_id: EvaluationResult.FAIL})
        assert fired == []

    def test_priority_for_risk_level_classmethod(self):
        """priority_for_risk_level works without instantiating the service."""
        P = ManageService.priority_for_risk_level
        assert P(RiskLevel.CRITICAL) == ActionPriority.IMMEDIATE
        assert P(RiskLevel.HIGH) == ActionPriority.SHORT_TERM
        assert P(RiskLevel.MEDIUM) == ActionPriority.MEDIUM_TERM
        assert P(RiskLevel.LOW) == ActionPriority.LONG_TERM

    def test_integration_map_to_manage(self):
        """Full MANAGE 1+4 flow: risk → priority → action → addressed → unaddressed."""
        from aegis_rmf.map import IdentifiedRisk

        system = _system()
        service = ManageService()

        # MAP produced a high-severity bias risk
        risk = IdentifiedRisk(
            system_id=system.id,
            category=RiskCategory.BIAS,
            level=RiskLevel.HIGH,
            title="Demographic skew in training data",
            description="Lower precision for some geographic regions",
        )

        # Derive priority from risk level (NIST Manage 1)
        priority = ManageService.priority_for_risk_level(risk.level)
        assert priority == ActionPriority.SHORT_TERM

        # Open a mitigation action
        action = MitigationAction(
            system_id=system.id,
            risk_id=risk.id,
            title="Deploy fairness calibration",
            description="Apply post-processing step",
            priority=priority,
            assignee="ml-platform@example.com",
            due_date=datetime(2026, 5, 1),
        )
        service.add_action(action)

        # Risk should now be addressed
        assert service.get_unaddressed_risks(system.id, [risk.id]) == []

        # The action is completed but never formally accepted → risk resurfaces
        resolved_action = action.model_copy(update={"status": ActionStatus.RESOLVED})
        service._actions = [resolved_action]

        assert service.get_unaddressed_risks(system.id, [risk.id]) == [risk.id]

        # Formally accept the residual risk → addressed again
        accepted_action = action.model_copy(update={"status": ActionStatus.ACCEPTED})
        service._actions = [accepted_action]

        assert service.get_unaddressed_risks(system.id, [risk.id]) == []
