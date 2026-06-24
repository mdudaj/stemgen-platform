# LIMS Workflow Patterns Review

## Purpose

This review translates workflow-configuration lessons from the public `nimr-tz/lims` repository into `stemgen-platform` planning language. The goal is to borrow architecture patterns for governed research workflows without copying LIMS domain code or lab-specific assumptions.

## Files Reviewed

- `README.md`
- `docs/README.md`
- `docs/OPERATION_FORM_ENGINE.md`
- `docs/WORKFLOWS.md`
- `docs/adr/0006-viewflow-backed-dynamic-operation-runner.md`
- `docs/adr/0008-react-operation-designer-and-runner.md`
- `docs/adr/0013-operation-workspace-and-component-platform.md`
- `docs/adr/0016-operation-draft-form-and-workflow-designer.md`
- `docs/adr/0017-lims-native-operation-draft.md`
- `docs/adr/0019-runtime-projection-failure-resolution.md`
- `docs/adr/0020-governed-batch-manifest-intake.md`
- `docs/adr/0022-specimen-reconstruction-read-model.md`
- `docs/adr/0034-configurable-downstream-processing-through-operation-engine.md`

The SSH clone initially stalled, but the repository was available through `git ls-remote` and a shallow HTTPS clone. Reviewed HEAD was `3d15c60f3d3fa71c7856fb68ab569781637d900e`.

## Relevant LIMS Patterns

LIMS separates configuration authoring from runtime execution. It treats editable operation drafts as governed JSON, publishes immutable versions, compiles node-specific artifacts and execution manifests, captures runtime evidence separately from domain projections, and reconstructs records from preserved evidence rather than from flattened summaries.

The strongest lesson for `stemgen-platform` is that configurable workflows should not mean arbitrary runtime code. Definitions are data; execution runs through stable framework adapters, explicit services, validation records, and reconstruction bundles.

## Designer and Runner Pattern

LIMS uses a designer/runner split:

- the designer authors metadata, sections, fields, workflow nodes, transitions, roles, gates, projections, preview evidence, and publication readiness;
- the runner executes only published versions and compiled artifacts;
- runtime preview may compile drafts for inspection but must not create runtime evidence or domain records.

Translation for `stemgen-platform`:

- `ResearchWorkflowDefinition` is the editable definition;
- `ResearchWorkflowVersion` is the published immutable version;
- `ResearchWorkflowNode` defines steps such as curriculum intake, automated review, human topic selection, generation, expert review, export, or replay;
- `ResearchExecutionManifest` is the compiled runner contract;
- `ResearchRun` and `ResearchStepRun` capture execution.

## Governed Definition Layer

LIMS pattern: editable drafts, immutable published versions, stable semantic keys, controlled values, publish review, and compiled artifacts.

`stemgen-platform` should borrow this for research workflows: a draft can change, but a version used for evaluation evidence must be immutable and traceable. Workflow definitions should include objective links, data inputs, output artifacts, roles, transitions, validation rules, and export/replay obligations.

## Workflow Layer

LIMS pattern: workflow nodes, transitions, role bindings, prerequisites, controlled gates, and Viewflow-backed execution through stable adapters.

`stemgen-platform` should define workflow nodes for curriculum intake, source snapshot, extraction, topic screening, automated review, human topic selection, topic brief generation, generation run, artifact inspection, refinement logging, expert review, export, and replay. Viewflow should own process/task lifecycle, assignments, permissions, and state; platform definitions should own research semantics.

## Runtime Capture Layer

LIMS pattern: preserve raw payload, normalized payload, field responses, validation result, and ingest decision before projection.

`stemgen-platform` should preserve source snapshots, extracted text, normalized curriculum items, generation manifests, prompt sets, script drafts, artifacts, review submissions, and export records before projecting accepted evidence into analysis-ready records.

## Domain Projection Layer

LIMS pattern: explicit projection services create typed domain records only after evidence is accepted.

`stemgen-platform` should project accepted runtime evidence into typed research records such as `CandidateTopic`, `TopicSelectionDecision`, `GenerationRun`, `RubricResponse`, `ExportBatch`, and `ReplayAttempt`. Generic submissions must not become canonical records by themselves.

## Audit and Reconstruction Layer

LIMS pattern: reconstruct from governed evidence records and show missing evidence explicitly. Projection failures get separate disposition records rather than rewriting original evidence.

`stemgen-platform` should create evidence reconstruction bundles showing source registry, checksums, extraction, screening, automated review, human decisions, generation provenance, evaluator feedback, exports, replay attempts, and unresolved gaps.

## Viewflow Integration Lessons

- Use stable importable Viewflow flow/task code.
- Do not generate or mutate Python Viewflow flow classes at request time.
- Store configured workflow semantics in repo/database definitions and compile to manifests.
- Let Viewflow own process, task, assignment, locking, permissions, shell integration, and navigation.
- Let `stemgen-platform` own research-specific evidence, validation, projection, exports, and replay.

## What stemgen-platform Should Borrow

- Designer and runner separation.
- Editable draft vs immutable published version lifecycle.
- Stable semantic keys for fields, nodes, artifacts, roles, and transitions.
- Controlled value bindings and controlled expressions rather than arbitrary code.
- Node-specific compiled runner artifacts.
- Execution manifests that bind workflow nodes to stable runtime adapters.
- Runtime evidence preservation before projection.
- Raw payload plus normalized payload.
- Validation result and acceptance decision records.
- Explicit research evidence projection services.
- Reconstruction bundles over source evidence.
- Viewflow as stable workflow adapter, not generated runtime code.

Terminology translation:

| LIMS term | stemgen-platform term |
| --- | --- |
| OperationDefinition | ResearchWorkflowDefinition |
| OperationVersion | ResearchWorkflowVersion |
| OperationWorkflowNode | ResearchWorkflowNode |
| OperationExecutionManifest | ResearchExecutionManifest |
| OperationRun | ResearchRun |
| OperationStepRun | ResearchStepRun |
| StepSubmission | StepEvidenceSubmission |
| StepValidationResult | EvidenceValidationResult |
| StepIngestDecision | EvidenceAcceptanceDecision |
| DomainProjection | ResearchEvidenceProjection |
| ReconstructionBundle | EvidenceReconstructionBundle |

## What stemgen-platform Should Not Borrow

- Specimen, storage, QC, accession, and downstream laboratory domain models.
- Regulated laboratory terminology as user-facing research terminology.
- React runner complexity before the Django/Viewflow baseline needs it.
- LIMS role catalog details.
- LIMS batch and lab context assumptions.
- Any code copied blindly from LIMS.

## Open Questions

- Which workflows need editable UI in the first implementation slice, and which can start as repo-owned YAML definitions?
- Should publication be admin-only, operator-only, or require a separate reviewer?
- Which workflow definitions are required before the first topic brief run is restored?
- Which artifacts become database records in slice 1 versus JSON files under `artifacts/`?
- What minimum Viewflow adapter is enough for the first research workflow without overbuilding a full designer?
