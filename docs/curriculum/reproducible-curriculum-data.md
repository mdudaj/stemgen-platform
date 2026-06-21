# Reproducible Curriculum Data

## Purpose

This plan builds on ADR 0005: deterministic curriculum intake remains the source of truth, while optional enrichment and review artifacts are separate and non-authoritative.

The platform must generate structured curriculum data from official TIE sources in a reproducible way. Deterministic extraction is the source-of-truth dataset. LLM enrichment and automated review are assistive artifacts stored separately.

## Pipeline

```text
source registry
  -> fetch/snapshot
  -> checksum
  -> text/table extraction
  -> normalization
  -> validation
  -> candidate topic generation
  -> optional LLM enrichment
  -> optional automated curriculum review
  -> human review
  -> accepted topic shortlist
```

## Snapshot Directory

Slice 1 currently creates the first five entries only:

```text
artifacts/curriculum-snapshots/<snapshot_id>/
├── source_registry.json
├── fetch_manifest.json
├── downloaded_sources/
├── checksums.sha256
├── extraction_manifest.json
├── raw_extracted_text.jsonl
├── normalized_curriculum_items.json
├── candidate_topic_dataset.json
├── candidate_topic_enrichment.json
├── candidate_topic_review_distribution.json
├── automated_curriculum_review_manifest.json
└── topic_selection_decisions.json
```

Extraction, normalized items, candidate topics, automated review artifacts, and topic selection decisions are later-slice outputs and are not produced by Slice 1.

## Artifact Responsibilities

- `source_registry.json`: versioned source list and tiers.
- `fetch_manifest.json`: retrieval metadata, URLs, timestamps, HTTP metadata when available, and local filenames.
- `checksums.sha256`: checksum for each downloaded source and generated deterministic artifact.
- `extraction_manifest.json`: extraction tool version, parameters, parser warnings, source pages/sections processed.
- `raw_extracted_text.jsonl`: page/section/table text with source references.
- `normalized_curriculum_items.json`: deterministic normalized curriculum items.
- `candidate_topic_dataset.json`: candidate topics generated from deterministic items and rule screening.
- `candidate_topic_enrichment.json`: optional assistive enrichment, separate from deterministic facts.
- `candidate_topic_review_distribution.json`: optional automated review distribution.
- `automated_curriculum_review_manifest.json`: automated review run metadata.
- `topic_selection_decisions.json`: human acceptance/rejection/needs-revision decisions.

## Slice 1 Command

```bash
python manage.py curriculum_snapshot create --dry-run --json
python manage.py curriculum_snapshot create --no-download --validate --json
python manage.py curriculum_snapshot create --validate --json
```

`--dry-run` prints the planned snapshot UUID, sources, and artifact paths without writing artifacts or database rows. `--no-download` creates registry and manifest artifacts and marks source downloads as skipped. A real run fetches the official URLs only when the command is run without `--dry-run` and without `--no-download`.

## Dashboard Review

The main dashboard summarizes the latest source snapshot. Staff users can open `/curriculum/snapshots/` to inspect snapshot metadata, validation status, manifest paths, warnings/errors, captured source metadata, stored filenames, file sizes, and SHA-256 checksums.

## Automated Review Manifest

```json
{
  "snapshot_id": "",
  "review_run_id": "",
  "created_at": "",
  "deterministic_dataset": "candidate_topic_dataset.json",
  "review_artifacts": [
    "candidate_topic_review_distribution.json"
  ],
  "provider": "",
  "model": "",
  "prompt_template_id": "",
  "candidate_count": 5,
  "temperature": null,
  "top_p": null,
  "input_hash": "",
  "output_hash": "",
  "failure_mode": null,
  "human_review_required": true
}
```

## Reproducibility Rules

- Tier 1 source snapshots must be checksummed before extraction.
- Extraction must record tool version and parameters.
- Normalization must preserve source references.
- Optional LLM enrichment/review must record provider, model, prompt template, input hash, output hash, and failure mode.
- LLM output cannot overwrite `normalized_curriculum_items.json`.
- Human topic decisions must reference the deterministic item and optional review artifacts inspected.
