# aegis-rmf

**Governance-as-code toolkit mapping AI regulatory frameworks to technical controls.**

Aegis RMF is an open-source Python SDK for ML engineers and governance teams who need to operationalize AI risk management — not just read about it. It maps NIST AI RMF, ISO 42001, and the EU AI Act to concrete data models, assessments, and controls you can wire into CI/CD pipelines and monitoring systems.

![CI](https://github.com/jodyb/aegis-rmf/actions/workflows/ci.yml/badge.svg)

> **Status:** Pre-alpha — Phase 1 (NIST AI RMF foundation) in active development. GOVERN function complete.

---

## Why this exists

Most AI governance tooling lives in spreadsheets, policy PDFs, and consultants' decks. Aegis RMF treats governance as code: versioned, testable, and integrated into the same engineering workflows teams already use. The goal is to make compliance a byproduct of good engineering practice, not a separate audit exercise.

---

## Quick start

```bash
# Install
uv sync --extra dev

# Run the test suite
uv run pytest -v
```

### Evaluate governance policies against an AI system

```python
from aegis_rmf.core import LifecycleStage, PolicyStatus, RiskLevel, SystemType
from aegis_rmf.core import AISystem
from aegis_rmf.govern import GovernancePolicy, GovernService, PolicyCondition

# Define a policy that targets high-risk production systems
policy = GovernancePolicy(
    name="High Risk Controls",
    description="Extra controls required for high-risk production systems",
    status=PolicyStatus.ACTIVE,
    condition=PolicyCondition(
        risk_levels=[RiskLevel.HIGH, RiskLevel.CRITICAL],
        lifecycle_stages=[LifecycleStage.PRODUCTION],
    ),
    requirements=["Monthly risk assessment", "Human-in-the-loop review"],
    owner="Risk Team",
)

# Register the policy with the service
service = GovernService()
service.add_policy(policy)

# Check which policies apply to a given system
system = AISystem(
    name="Fraud Detector",
    description="Flags suspicious transactions in real time",
    system_type=SystemType.CLASSIFICATION,
    owner="ML Platform Team",
    lifecycle_stage=LifecycleStage.PRODUCTION,
    risk_level=RiskLevel.HIGH,
)

applicable = service.get_applicable_policies(system)
for p in applicable:
    print(f"{p.name}: {p.requirements}")
# High Risk Controls: ['Monthly risk assessment', 'Human-in-the-loop review']
```

### Register an AI system

```python
from aegis_rmf.core import (
    AISystem,
    RiskProfile,
    Assessment,
    AssessmentType,
    LifecycleStage,
    RiskCategory,
    RiskLevel,
    SystemType,
)

# Register a system
system = AISystem(
    name="Fraud Detector",
    description="Flags suspicious transactions in real time",
    system_type=SystemType.CLASSIFICATION,
    owner="ML Platform Team",
    lifecycle_stage=LifecycleStage.PRODUCTION,
    risk_level=RiskLevel.HIGH,
    tags=["financial", "real-time"],
)

# Attach a risk profile
profile = RiskProfile(
    system_id=system.id,
    risk_scores={
        RiskCategory.BIAS: RiskLevel.HIGH,
        RiskCategory.PRIVACY: RiskLevel.MEDIUM,
        RiskCategory.RELIABILITY: RiskLevel.LOW,
    },
    overall_risk=RiskLevel.HIGH,
    context="Trained on historical transaction data; demographic skew identified in v2 audit.",
)

# Create a pre-deployment assessment
assessment = Assessment(
    system_id=system.id,
    assessment_type=AssessmentType.PRE_DEPLOYMENT,
    assessor="Governance Team",
)

# Serialize to JSON for storage or audit export
print(system.model_dump_json(indent=2))
```

---

## Project structure

```
src/aegis_rmf/
├── core/          # Shared domain models and enums (AISystem, RiskProfile, Assessment, ...)
├── govern/        # GOVERN function: policies, roles, accountability structures
├── map/           # MAP function: system context, stakeholder mapping, risk identification
├── measure/       # MEASURE function: metrics, thresholds, evaluation criteria
└── manage/        # MANAGE function: controls, mitigations, monitoring triggers
```

The four subpackages (`govern`, `map`, `measure`, `manage`) mirror the four functions of the [NIST AI Risk Management Framework](https://www.nist.gov/artificial-intelligence).

---

## Roadmap

### Phase 1 — NIST AI RMF foundation *(current)*
- [x] Project scaffold, packaging, CI tooling
- [x] GitHub Actions CI — tests run on every push and PR
- [x] Core domain models: `AISystem`, `RiskProfile`, `Assessment`, `ComplianceArtifact`
- [x] Shared enumerations: risk levels, lifecycle stages, system types, risk categories
- [x] GOVERN function: policy registry, role assignments, accountability chains
- [ ] MAP function: system context capture, stakeholder mapping, risk identification
- [ ] MEASURE function: metric definitions, thresholds, scoring logic
- [ ] MANAGE function: control catalog, mitigation actions, monitoring triggers
- [ ] pytest suite with full coverage of Phase 1 modules

### Phase 2 — ISO 42001 mapping
- [ ] ISO 42001 control catalog
- [ ] Cross-walk: map ISO 42001 clauses to NIST AI RMF subcategories
- [ ] Gap analysis tooling

### Phase 3 — EU AI Act compliance
- [ ] Risk classification engine (unacceptable / high / limited / minimal)
- [ ] Conformity assessment workflows for high-risk systems
- [ ] Article-level requirement mapping

### Phase 4 — CI/CD integration + LLM eval harness
- [ ] GitHub Actions / GitLab CI example integrations
- [ ] Golden-set evaluation framework
- [ ] Adversarial probes: hallucination, safety, bias, privacy leakage, robustness
- [ ] Cost and latency benchmarking

### Phase 5 — Agentic AI governance + web dashboard
- [ ] Governance primitives for multi-agent and agentic systems
- [ ] Web dashboard (read-only audit view)
- [ ] REST API for dashboard consumption

### Phase 6 — Polish and launch
- [ ] Documentation site
- [ ] Example integrations (Bedrock, Vertex AI, OpenAI)
- [ ] v1.0.0 release

---

## Development

```bash
# Install with dev dependencies
uv sync --extra dev

# Run tests
uv run pytest -v

# Lint
uv run ruff check src tests

# Type check
uv run mypy src
```

---

## License

Apache 2.0 — see [LICENSE](LICENSE).
