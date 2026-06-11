# ADR 0011: Automated Curriculum Review Before Human Selection

Date: 2026-06-11

## Status

Accepted for Milestone 22.5 planning.

## Context

Milestone 22.5 prepares `stemgen-platform` as a research instrument for curriculum-aligned STEM animation and narration feasibility evaluation. The platform must preserve curriculum, workflow, generation, review, export, provenance, and replay evidence while avoiding premature full implementation.


This ADR continues the initial platform decisions now copied into this repository as ADRs 0001-0006: Django/Viewflow foundation, PostgreSQL/Redis/Celery infrastructure, email-based custom users, OSS Viewflow extension strategy, optional LLM enrichment boundaries, and the async launch-to-status handoff contract.

## Decision

Add optional automated curriculum review before human topic selection using deterministic screening and optional verbalized-sampling-inspired LLM review, while keeping official curriculum extraction as source of truth and requiring human acceptance before topic promotion.

## Consequences

- Implementation slices must reference this decision before building workflow, curriculum, evaluation, messaging, export, replay, or repository-write features.
- Documentation and future schemas should preserve explicit evidence artifacts and human review gates.
- Tests and validation commands should be added before behavior changes become production paths.

## Alternatives Considered

### Manual-only topic selection

Viable as a baseline but may miss useful uncertainty triage and rationale diversity.

### Single-answer LLM topic suitability judgment

Rejected. A single answer hides uncertainty and encourages false authority.

### LLM auto-selection

Rejected. It violates the source-of-truth and human gate rules.

### Deterministic-only screening

Useful and required, but may not expose borderline cases and rationale diversity for reviewers.

## Safety Rules

- LLM auto-selection is rejected.
- LLM overwrite of curriculum facts is rejected.
- Single-answer LLM as the only suitability judgment is rejected.
- Human acceptance is required before topic promotion.

## Reproducibility Requirements

Store source snapshot ID, deterministic dataset hash, prompt template ID, provider/model when used, input hash, output hash, uncertainty flags, and human decision link.
