# Curriculum Data Schema

## Curriculum Item

The curriculum item is the deterministic source-of-truth record extracted from official curriculum sources.

```json
{
  "source_id": "",
  "source_url": "",
  "source_title": "",
  "publisher": "Tanzania Institute of Education",
  "subject": "",
  "standard": "",
  "topic": "",
  "subtopic": "",
  "learning_objective": "",
  "competency": "",
  "content_reference": {
    "page": null,
    "section": null,
    "table": null
  },
  "language": "",
  "animation_suitability": {
    "candidate": false,
    "rationale": "",
    "screening_method": "",
    "review_status": "pending"
  },
  "provenance": {
    "retrieved_at": "",
    "checksum": "",
    "extractor_version": "",
    "manual_reviewed_by": null
  }
}
```

## Field Rules

- `source_id`, `source_url`, `source_title`, and `publisher` identify the Tier 1 source.
- `subject`, `standard`, `topic`, `subtopic`, `learning_objective`, and `competency` come from deterministic extraction or manual correction, not LLM enrichment.
- `content_reference` must locate the source sufficiently for human verification.
- `language` records the extracted language or translation state.
- `animation_suitability` stores screening status; optional automated review writes separate review distribution artifacts.
- `provenance` records retrieval and extraction metadata.

## Candidate Topic

A candidate topic aggregates one or more curriculum items for potential animation.

Suggested fields:

- `topic_id`
- `source_item_ids`
- `subject`
- `standard`
- `topic`
- `subtopics`
- `screening_labels`
- `screening_rationale`
- `source_references`
- `automated_review_artifact_id`
- `human_decision_id`
- `status`

## Validation

- Every candidate topic must reference at least one deterministic curriculum item.
- Every accepted topic must have a `TopicSelectionDecision` with `decision = accepted`.
- Automated review artifacts may inform candidate status but must not be treated as acceptance.
