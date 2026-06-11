# Topic Screening Rules

## Purpose

Topic screening identifies curriculum topics that are likely to benefit from animation and narration before human selection.

## Suitable Topic Signals

A topic is suitable for animation if it involves one or more:

- process
- sequence
- change over time
- cause and effect
- spatial relationship
- abstract relationship
- measurement transformation
- system interaction

## Deprioritization Signals

A topic should be deprioritized if:

- it is mostly memorization;
- it is purely factual recall;
- it requires sensitive or culturally risky representation;
- it cannot be represented within the prototype scope.

## Screening Output

Each screened candidate should record:

- `topic_id`
- `source_item_ids`
- suitability labels
- positive signals found
- deprioritization signals found
- rule version
- deterministic rationale
- reviewer status

## Human Topic Selection Gate

A topic can become part of the accepted shortlist only when:

- source reference is valid;
- deterministic extraction is reviewed;
- animation suitability is justified;
- automated review, if present, is inspected;
- human operator accepts the topic;
- acceptance decision is recorded.

Required artifact: `topic_selection_decisions.json`.

```json
{
  "topic_id": "",
  "decision": "accepted|rejected|needs_revision",
  "reviewer": "",
  "reviewed_at": "",
  "reason": "",
  "source_references_checked": true,
  "automated_review_considered": true,
  "notes": ""
}
```

## Safety Rules

- No LLM auto-selection.
- No promotion without human acceptance.
- No accepted topic without valid Tier 1 source reference.
- Do not hide uncertainty flags; route them to human review.
