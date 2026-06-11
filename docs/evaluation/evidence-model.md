# Evidence Model

## Purpose

The evidence model defines records that make the platform a research instrument rather than only a media generator.

| Entity | Purpose | Key fields | Links | Evidence role | Export behavior | Privacy considerations |
| --- | --- | --- | --- | --- | --- | --- |
| CurriculumSource | Registry entry for source material. | source_id, title, URL, publisher, tier, expected path. | CurriculumSnapshot, CurriculumItem. | Establishes source authority. | JSON registry export. | Public source metadata only. |
| CurriculumSnapshot | Fixed retrieval set. | snapshot_id, retrieved_at, checksums, fetch status. | CurriculumSource, CurriculumItem. | Reproducibility anchor. | JSON manifest and checksum export. | No secrets; no private data. |
| CurriculumItem | Deterministic extracted curriculum fact. | subject, standard, topic, subtopic, objective, reference, provenance. | CandidateTopic. | Source-of-truth curriculum record. | JSON/CSV with references. | Copyright caution for text excerpts. |
| CandidateTopic | Potential animation topic. | topic_id, source_item_ids, screening labels, status. | TopicSelectionDecision, TopicBrief. | Candidate evidence before selection. | Topic dataset export. | No participant data. |
| TopicSelectionDecision | Human acceptance gate. | decision, reviewer, reason, checks, timestamp. | CandidateTopic. | Final gate for shortlist. | Decision CSV/JSON. | Reviewer identity may need pseudonymization in dissertation exports. |
| TopicBrief | Generation-ready brief. | brief_id, topic_id, objective, constraints, source refs. | GenerationRun. | Input to generation. | Markdown/JSON. | No private data. |
| GenerationRun | One generation attempt. | run_id, status, workflow version, settings, started_at. | GenerationManifest, artifacts. | Production-practicality evidence. | Run CSV/JSON. | Provider metadata only, no credentials. |
| GenerationManifest | Detailed run provenance. | provider, model, prompt ids, inputs, hashes, timings. | PromptSet, artifacts. | Reproducibility and divergence explanation. | JSON. | Redact secrets and sensitive prompt data. |
| PromptSet | Prompt templates and rendered prompts. | prompt_set_id, template ids, hashes, rendered prompt refs. | GenerationManifest. | Generation trace. | JSON with redaction. | Avoid credentials and private evaluator data. |
| ScriptDraft | Generated or edited script. | script_id, version, text ref, source run. | GenerationRun, RefinementLog. | Artifact evidence. | Artifact bundle. | Copyright/source caution. |
| VisualArtifact | Visual output. | artifact_id, media type, path, checksum, source run. | AssemblyArtifact. | Reviewable artifact. | ZIP bundle and manifest. | Do not expose unpublished full bundles over WhatsApp. |
| NarrationArtifact | Audio/narration output. | artifact_id, path, checksum, voice settings. | AssemblyArtifact. | Reviewable artifact. | ZIP bundle and manifest. | Voice licensing/provider metadata. |
| AssemblyArtifact | Combined prototype. | artifact_id, components, path, checksum. | RubricResponse. | Expert review target. | ZIP bundle and review manifest. | Secure review links only. |
| RefinementLog | Change log across iterations. | refinement_id, reason, before/after refs, actor. | GenerationRun, artifacts. | Production practicality evidence. | CSV/JSON. | Operator identity may be internal. |
| EvaluationInvitation | Assigns review to evaluator. | invitation_id, evaluator_id, artifact refs, token, status. | EvaluatorProfile, channel records. | Review workflow evidence. | Invitation summary export. | Token must not be exported raw. |
| EvaluatorProfile | Evaluator metadata. | evaluator_id, role, expertise, channel prefs. | RubricResponse. | Context for descriptive analysis. | Pseudonymized CSV. | Treat as participant-sensitive. |
| RubricResponse | Structured expert review. | response_id, scores, comments, submitted_at. | EvaluatorProfile, artifacts. | Primary evaluation evidence. | CSV/JSON. | Pseudonymize evaluator in public outputs. |
| EvaluatorComment | Open qualitative feedback. | comment_id, criterion, text, artifact ref. | RubricResponse. | Qualitative evidence. | CSV with redaction review. | Review for identifying details. |
| ExportBatch | Export package. | batch_id, included records, formats, checksums. | All evidence. | Analysis and reporting package. | CSV/JSON/ZIP/Markdown/PDF. | Apply export policy. |
| ReplayAttempt | Reproducibility attempt. | replay_id, run refs, exact/different, divergence. | GenerationRun, ExportBatch. | Reproducibility evidence. | JSON/Markdown report. | No secrets. |
