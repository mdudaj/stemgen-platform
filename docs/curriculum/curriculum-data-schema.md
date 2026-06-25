# Curriculum Data Schema

## Curriculum Item

The curriculum item is the deterministic source-of-truth record extracted from official curriculum sources.

```json
{
  "item_id": "",
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
  "raw_text_excerpt": "",
  "extraction_warnings": [],
  "language": "",
  "animation_suitability": {
    "candidate": null,
    "rationale": "",
    "screening_method": "not_screened",
    "review_status": "pending"
  },
  "provenance": {
    "source_snapshot_id": "",
    "retrieved_at": "",
    "checksum": "",
    "extractor_version": "",
    "manual_reviewed_by": null
  }
}
```

## Field Rules

- `item_id` is the stable identifier referenced by candidate topic datasets.
- `source_id`, `source_url`, `source_title`, and `publisher` identify the Tier 1 source.
- `subject`, `standard`, `topic`, `subtopic`, `learning_objective`, and `competency` come from deterministic extraction or manual correction, not LLM enrichment.
- `content_reference` must locate the source sufficiently for human verification.
- `raw_text_excerpt` preserves the source text used to normalize the item.
- `extraction_warnings` records OCR, table parsing, missing page, or checksum gaps without blocking deterministic artifact creation.
- `language` records the extracted language or translation state.
- `animation_suitability` remains `candidate = null`, `screening_method = not_screened`, and `review_status = pending` until the rule-based screening slice.
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
- `screening_signals`
- `deprioritization_reasons`
- `source_references`
- `automated_review_artifact_id`
- `human_decision_id`
- `status`

## Validation

- Every candidate topic must reference at least one deterministic curriculum item.
- Slice 2 candidate topics are rule-ready but unscreened: `screening_signals = []` and `review_status = pending`.
- Every accepted topic must have a `TopicSelectionDecision` with `decision = accepted`.
- Automated review artifacts may inform candidate status but must not be treated as acceptance.

## Slice 2 Extraction Boundary

The first deterministic producer extracts Science and Mathematics seed items from the captured TIE source snapshot. It writes:

- `curriculum_items.json`
- `candidate_topics.json`

The producer uses source/page/section/table references from the official syllabi and leaves animation suitability blank/rule-ready. It can be launched from the staff web UI or the CLI. The web review surface displays generated items, candidate topics, artifact paths, validation state, and pending screening status. It does not perform PDF OCR, LLM enrichment, rule-based screening, human selection, or topic acceptance.
