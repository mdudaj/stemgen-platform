# Automated Curriculum Review

## Purpose

Automated curriculum review is an optional assistive stage after deterministic extraction and rule-based screening, before human topic selection. It helps reviewers see suitability uncertainty but must not replace human judgment.

## Pipeline

```text
TIE source registry
  -> source snapshot
  -> deterministic extraction
  -> rule-based topic screening
  -> optional verbalized curriculum review
  -> human review
  -> accepted topic shortlist
```

## Principles


This design extends ADR 0005's optional LLM enrichment boundary: deterministic curriculum intake remains authoritative, and model output is stored as separate assistive evidence.

- Official TIE sources remain the source of truth.
- Deterministic extraction remains the source-of-truth dataset.
- LLM review is assistive only.
- LLM review must not overwrite curriculum facts.
- LLM review must not auto-accept topics.
- LLM review outputs must be stored separately.
- Human review is required before promotion to topic shortlist.

## Criteria

Automated review should consider:

- animation suitability;
- process/sequence/change-over-time presence;
- cause-and-effect clarity;
- abstract relationship visualizability;
- primary-level appropriateness;
- curriculum alignment risk;
- scientific accuracy risk;
- local-context risk;
- resource/practicality risk.

## Uncertainty Handling

Flag topics for human attention when:

- judgment distribution is high entropy;
- top two judgments are close;
- curriculum source reference is weak;
- topic/subtopic extraction is ambiguous;
- LLM rationale conflicts with deterministic screening;
- LLM suggests facts not present in TIE source.

## Required Artifacts

- `candidate_topic_review_distribution.json`
- `automated_curriculum_review_manifest.json`

## Implementation Boundary

Milestone 22.5 documents the review stage only. No live LLM calls are required, and no provider credentials are required.
