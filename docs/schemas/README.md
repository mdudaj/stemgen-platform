# Schema Contracts

## Purpose

Schemas define the machine-validated evidence contracts for `stemgen-platform`. They turn the Milestone 22.5 documentation into executable validation rules before implementation slices depend on those artifacts.

Schemas are part of the research evidence contract. A schema change must be reviewed with the related documentation and at least one validation example.

## Directory Layout

- `schemas/curriculum/`: curriculum source, snapshot, extraction, screening, automated review, and human topic-selection artifacts.
- `schemas/evaluation/`: evaluator invitations, rubric definitions, rubric responses, and export manifests.
- `schemas/workflows/`: configurable research workflow definitions, execution manifests, step evidence submissions, and validation results.
- `schemas/repository/`: project repository write-safety and push-policy contracts.
- `fixtures/examples/`: minimal synthetic examples used by offline validation.

## Relationship to Documentation

Markdown documents explain research intent, workflow design, and safety boundaries. JSON Schema files define the data contracts that implementation must satisfy. When a schema changes, update the related documentation and example fixture in the same patch.

## Validation

Run:

```bash
python3 scripts/validate_json.py
```

The command validates JSON syntax, checks every `*.schema.json` file with JSON Schema Draft 2020-12, and validates known example fixtures against their schemas. It does not require network access, live TIE downloads, live LLM calls, or WhatsApp credentials.

## Slice 1 Required Schemas

Slice 1: Reproducible TIE Curriculum Source Snapshot requires:

- `schemas/curriculum/source_registry.schema.json`
- `schemas/curriculum/fetch_manifest.schema.json`
- `schemas/curriculum/curriculum_snapshot_manifest.schema.json`

Slice 1 examples:

- `fixtures/examples/source_registry.example.json`
- `fixtures/examples/curriculum_snapshot_manifest.example.json`

## Future Expansion

Future slices should add or tighten schemas before implementing behavior that produces the artifact. Expected next contracts include extraction manifests, prompt-set manifests, generation manifests, artifact bundles, WhatsApp message templates, and replay reports.
