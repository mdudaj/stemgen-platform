# ADR 0005: Add optional LLM enrichment as an assistive curriculum-intake layer

## Status

Accepted

## Context

The curriculum intake slice already produces a deterministic candidate-topic dataset from TIE source material using a reproducible fetch, snapshot, and rule-based extraction path. The platform now needs optional LLM assistance for tasks where the deterministic pipeline is weak, such as normalization, bilingual hints, and suggested suitability rationale.

This change is hard to reverse because it affects workflow behavior, outbound data flow, and manifest contracts. It is also surprising without context because the dissertation platform treats reproducibility and observability as first-class constraints, while LLM providers introduce nondeterminism.

## Decision

- Keep the deterministic curriculum intake pipeline as the source of truth.
- Add an optional provider-backed LLM enrichment layer that runs only when explicitly configured.
- Support OpenAI-compatible chat-completion endpoints first through a repo-owned client abstraction and env-backed configuration.
- Store LLM output in a separate `candidate_topic_enrichment.json` artifact rather than mutating the deterministic `candidate_topic_dataset.json`.
- Persist LLM suggestions onto `CandidateTopic.llm_suggestion` so operators can see them during review, but keep them read-only until a human accepts them through bounded correction.
- Record enrichment provenance in a top-level `assistive_enrichment` manifest block and in trace events, excluding secrets.
- Treat LLM runtime failures as non-fatal for curriculum intake: the workflow falls back to the deterministic baseline and records the failure.

## Consequences

- Curriculum intake now has two output classes:
  - deterministic source-of-truth artifacts
  - optional assistive enrichment artifacts
- A completed intake run remains reproducible at the deterministic layer, but LLM enrichment is not guaranteed to replay bit-for-bit across time or provider changes.
- Operators gain more review context without allowing the LLM to silently rewrite extracted facts or promote topics downstream automatically.
- The platform now has an explicit outbound LLM egress surface that must stay allow-listed and observable.

## Alternatives Considered

### Put LLM-enriched fields directly into the deterministic candidate dataset

Rejected because it would make the core dataset artifact nondeterministic and weaken the run-manifest contract.

### Skip persistence and show LLM suggestions only transiently in the UI

Rejected because operator decisions need traceable context and artifact-backed provenance.

### Make LLM enrichment mandatory for every intake run

Rejected because the platform must still work without external provider access and should preserve a bare deterministic path.
