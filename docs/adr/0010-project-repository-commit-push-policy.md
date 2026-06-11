# ADR 0010: Project Repository Commit Push Policy

Date: 2026-06-11

## Status

Accepted for Milestone 22.5 planning.

## Context

Milestone 22.5 prepares `stemgen-platform` as a research instrument for curriculum-aligned STEM animation and narration feasibility evaluation. The platform must preserve curriculum, workflow, generation, review, export, provenance, and replay evidence while avoiding premature full implementation.


This ADR continues the initial platform decisions now copied into this repository as ADRs 0001-0006: Django/Viewflow foundation, PostgreSQL/Redis/Celery infrastructure, email-based custom users, OSS Viewflow extension strategy, optional LLM enrichment boundaries, and the async launch-to-status handoff contract.

## Decision

Allow explicit, gated local commit and remote branch push for project repositories, while preserving no-push-by-default and blocking main/master, force push, failed gates, and unsafe diffs.

## Consequences

- Implementation slices must reference this decision before building workflow, curriculum, evaluation, messaging, export, replay, or repository-write features.
- Documentation and future schemas should preserve explicit evidence artifacts and human review gates.
- Tests and validation commands should be added before behavior changes become production paths.

## Alternatives Considered

- Hardcode workflow-specific views and forms for every research activity.
- Treat draft definitions as runtime authority.
- Defer governance until after generation works.

Rejected alternatives would weaken reproducibility, reviewability, and safety.

## Safety Rules

- No arbitrary executable code from workflow definitions.
- No credential or participant-sensitive data in source artifacts.
- High-risk changes require explicit review.

## Reproducibility Requirements

Record version IDs, checksums, actor, timestamps, input manifests, output manifests, validation results, and acceptance decisions.
