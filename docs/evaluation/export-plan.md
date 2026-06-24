# Export Plan

## Purpose

Exports support descriptive analysis, dissertation reporting, and reproducibility review without requiring production deployment.

## Export Types

| Export | Contents | Format | Purpose |
| --- | --- | --- | --- |
| Curriculum topic shortlist export | Accepted topics, source references, screening labels, human decisions. | CSV and JSON | Analyze topic selection and source alignment. |
| Generation manifest export | Run metadata, prompt/template IDs, provider/model metadata, hashes, timings, status. | JSON and CSV summary | Analyze production practicality and provenance. |
| Artifact bundle export | Script, visual, narration, assembly artifacts, checksums, manifest. | ZIP with JSON manifest | Review generated materials outside platform. |
| Rubric response export | Scores by criterion, evaluator role/expertise, artifact refs. | CSV and JSON | Descriptive feasibility analysis. |
| Open comments export | Qualitative comments linked to criteria/artifacts. | CSV with redaction review | Thematic review. |
| Production practicality export | run durations, retries, failures, refinement counts, operator notes. | CSV and JSON | Feasibility assessment. |
| Full evidence bundle export | Source registry, snapshots, extraction, topics, generation, review, export manifests, replay reports. | ZIP plus JSON manifests | Audit/reproducibility package. |
| Dissertation reporting summary | Human-readable summary of selected records and charts/tables. | Markdown/PDF | Reporting support. |

## Export Rules

- CSV is for analysis tables.
- JSON is for structured provenance.
- ZIP is for artifact packages.
- Markdown/PDF is for dissertation reporting summaries.
- Exports must include manifest, generated_at, generator version, record counts, checksums, and redaction status.
- Do not export raw provider secrets, raw WhatsApp payloads, `.env` data, or participant-sensitive evaluator details without explicit redaction policy.
