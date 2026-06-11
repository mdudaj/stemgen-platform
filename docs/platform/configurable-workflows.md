# Configurable Workflows

## Purpose

`stemgen-platform` workflows should be configurable through repo-owned definitions rather than hardcoded one-off views. Configuration exists to support research evidence, not to create a general workflow product.

## Position

This strategy builds on ADR 0001's Django/Viewflow foundation, ADR 0002's Celery-backed async execution posture, ADR 0004's OSS Viewflow extension strategy, and ADR 0006's async launch-to-status handoff contract.

Configurable workflows are repo-owned definitions. Published workflow versions are immutable. Workflow definitions compile into execution manifests. Viewflow owns stable process/task execution. The platform must not generate arbitrary Python Viewflow classes dynamically. Rules are controlled expressions or configured transitions, not arbitrary code. Runtime submissions preserve raw and normalized evidence. Accepted evidence projects into typed research records through explicit services.

## Candidate Workflows

- curriculum intake
- topic screening
- automated curriculum review
- human topic selection
- topic brief generation
- generation run
- artifact inspection
- refinement logging
- expert review
- WhatsApp invitation
- export
- replay

## Workflow Definition Shape

```yaml
id: curriculum_intake
name: Curriculum Intake
version: 0.1.0
description: Import official curriculum sources, extract candidate topics, and prepare topic screening.
roles:
  operator:
    can_start: true
    can_review: true
  reviewer:
    can_start: false
    can_review: true
states:
  - draft
  - source_registered
  - snapshot_created
  - extraction_completed
  - candidates_generated
  - automated_review_completed
  - human_reviewed
  - accepted
  - failed
transitions:
  - id: register_source
    from: draft
    to: source_registered
    actor: operator
  - id: create_snapshot
    from: source_registered
    to: snapshot_created
    actor: operator
    async: true
  - id: extract_candidates
    from: snapshot_created
    to: candidates_generated
    actor: system
    async: true
  - id: automated_review
    from: candidates_generated
    to: automated_review_completed
    actor: system
    async: true
    optional: true
  - id: human_topic_selection
    from: automated_review_completed
    to: human_reviewed
    actor: operator
artifacts:
  - source_registry.json
  - fetch_manifest.json
  - checksums.sha256
  - normalized_curriculum_items.json
  - candidate_topic_dataset.json
  - candidate_topic_review_distribution.json
  - topic_selection_decisions.json
audit:
  require_run_id: true
  require_actor: true
  require_timestamp: true
```

## Governance Rules

- Editable drafts are not used as evaluation evidence.
- Publication creates immutable workflow versions and manifests.
- Every workflow has a research objective, evaluation activity, evidence artifact, or reproducibility requirement.
- Async steps must use the launch-to-status contract already accepted for the platform.
- Runtime preview must use the same runner contract but must not create canonical evidence.
- No workflow definition can execute arbitrary Python or shell code.
- Any workflow touching curriculum facts, evaluator communication, model providers, exports, or project repository writes is high risk and requires review.

## Relationship to Viewflow

Viewflow owns process state, task state, assignment, permissions, task locking, task URLs, history, and shell integration. The platform owns configured workflow identity, evidence semantics, artifact schemas, validation, projections, exports, and replay.

## Relationship to Celery

Celery executes long-running deterministic jobs and external-provider jobs behind explicit run records: snapshot fetch, extraction, generation, automated review, export packaging, and replay attempts. Celery tasks must update run status and attach manifests; they must not silently mutate accepted evidence.

## Definition of Done for Workflow Definitions

A workflow is ready for implementation when it has a definition file, versioning rule, manifest schema, runner contract, validation rules, evidence artifacts, export behavior, replay expectations, and tests or evals for unsafe paths.
