# Configurable Research Workflow Engine

## Purpose

This document defines the layers of a research workflow engine for `stemgen-platform`. The engine should make curriculum intake, generation, evaluation, export, and replay auditable without implementing the full platform in Milestone 22.5.

## Layer 1: Governed Definition Layer

Purpose: define what a workflow may do before it is run.

Candidate entities:

- `ResearchWorkflowDefinition`
- `ResearchWorkflowVersion`
- `ResearchWorkflowNode`
- `ResearchWorkflowTransition`
- `ResearchWorkflowRoleBinding`
- `ResearchWorkflowArtifactDefinition`
- `ResearchWorkflowPublicationReview`

Artifact outputs:

- workflow definition YAML/JSON
- publication review report
- workflow version snapshot
- schema validation report

Validation rules:

- stable IDs for workflows, nodes, transitions, artifacts, and roles;
- no arbitrary executable code;
- all outputs mapped to evidence artifacts;
- high-risk workflows require review;
- published versions are immutable.

Relationship to Viewflow: definitions compile into stable runtime inputs for Viewflow-backed tasks; they do not create dynamic Python flow classes.

Relationship to Celery: definitions identify which transitions are async and which task contracts Celery may execute.

Relationship to exports/replay: definition version and checksum are included in every evidence bundle and replay attempt.

## Layer 2: Workflow Layer

Purpose: execute the published workflow version through stable Django/Viewflow processes.

Candidate entities:

- `ResearchExecutionManifest`
- `ResearchRun`
- `ResearchStepRun`
- `ResearchTaskAssignment`
- `ResearchRunStatusEvent`

Artifact outputs:

- execution manifest
- run manifest
- state transition log
- task assignment log

Validation rules:

- run references one immutable workflow version;
- current state must match a configured transition;
- actor and role must satisfy node requirements;
- async transitions must expose launch-to-status state.

Relationship to Viewflow: Viewflow owns process/task lifecycle, permissions, and workflow shell integration.

Relationship to Celery: Celery performs async step work and updates the `ResearchRun` status and artifacts.

Relationship to exports/replay: state transition logs become part of the full evidence bundle.

## Layer 3: Runtime Capture Layer

Purpose: preserve what was submitted, generated, reviewed, imported, or exported before it is accepted as domain evidence.

Candidate entities:

- `StepEvidenceSubmission`
- `EvidenceValidationResult`
- `EvidenceAcceptanceDecision`
- `RuntimeArtifactReference`
- `RuntimeAttachment`

Artifact outputs:

- raw payload JSON
- normalized payload JSON
- validation result JSON
- acceptance decision JSON
- attachment manifest

Validation rules:

- raw evidence is append-only;
- normalized evidence is separately identified;
- validation findings are durable;
- rejected or failed evidence remains reconstructable;
- accepted evidence is projected only by explicit services.

Relationship to Viewflow: task views and APIs capture submissions inside Viewflow task context.

Relationship to Celery: async jobs write runtime artifacts and validation reports but do not bypass acceptance decisions.

Relationship to exports/replay: raw and normalized evidence are exported with hashes and artifact references.

## Layer 4: Research Evidence Projection Layer

Purpose: convert accepted runtime evidence into typed research records.

Candidate entities:

- `CurriculumItem`
- `CandidateTopic`
- `TopicSelectionDecision`
- `TopicBrief`
- `GenerationRun`
- `VisualArtifact`
- `NarrationArtifact`
- `RubricResponse`
- `ExportBatch`

Artifact outputs:

- typed JSON records
- analysis CSV rows
- artifact references
- projection log

Validation rules:

- projections are idempotent;
- source evidence IDs are preserved;
- deterministic curriculum facts cannot be overwritten by LLM output;
- rejected evidence does not project;
- failed projection creates a review obligation.

Relationship to Viewflow: projection happens as part of completing accepted workflow tasks or async transitions.

Relationship to Celery: long projections may run async but must write status and decisions.

Relationship to exports/replay: projection records are the analysis-ready exports, linked back to source evidence.

## Layer 5: Audit and Reconstruction Layer

Purpose: reconstruct how a research output was produced and reviewed.

Candidate entities:

- `EvidenceReconstructionBundle`
- `ReplayAttempt`
- `ProvenanceEvent`
- `ExportManifest`
- `AuditFinding`

Artifact outputs:

- reconstruction bundle JSON
- replay attempt report
- provenance timeline
- export manifest

Validation rules:

- missing evidence is shown explicitly;
- deterministic steps define exact replay expectations;
- external AI steps record enough metadata to explain divergence;
- evaluator records follow privacy constraints;
- secrets and credentials are never exported.

Relationship to Viewflow: Viewflow process/task history contributes actor, task, and state evidence.

Relationship to Celery: replay and export jobs create manifests and reports.

Relationship to exports/replay: this layer is the source for dissertation reporting, audit review, and reproducibility checks.

## Implementation Posture

Milestone 22.5 defines this strategy only. Implementation should start with narrow vertical slices, not the full engine.
