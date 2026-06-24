# Vertical Slice Roadmap


Source basis: slices are ordered to satisfy the proposal's feasibility workflow: curriculum topic selection, generation/prototype evidence, expert review, export, and replay/provenance explanation.

## Slice 1: Reproducible TIE Curriculum Source Snapshot

Goal: create a versioned source registry and snapshot artifacts for Tier 1 TIE sources.
Research objective supported: topic identification.
Workflow definition: curriculum intake.
Evidence produced: source registry, fetch manifest, downloaded sources, checksums.
Models/entities required: CurriculumSource, CurriculumSnapshot.
Acceptance criteria: four provided TIE URLs are registered; snapshot manifest records checksums; no unofficial source overrides Tier 1.
Verification command: future `python3 scripts/validate_curriculum_snapshot.py`.
Risks: URL drift, copyright handling, missing metadata.
Out of scope: full extraction.

## Slice 2: Deterministic Curriculum Extraction and Candidate Topic Dataset

Goal: extract normalized curriculum items and generate candidate topics.
Research objective supported: topic identification.
Workflow definition: curriculum intake.
Evidence produced: extraction manifest, raw text, normalized items, candidate topic dataset.
Models/entities required: CurriculumItem, CandidateTopic.
Acceptance criteria: candidates link to source items and page/section/table references.
Verification command: future `python3 scripts/validate_candidate_topics.py`.
Risks: PDF extraction quality.
Out of scope: LLM enrichment.

## Slice 3: Rule-Based Topic Screening

Goal: classify candidate topics using deterministic animation-suitability rules.
Research objective supported: topic identification.
Workflow definition: topic screening.
Evidence produced: screening labels and rationale.
Models/entities required: CandidateTopic.
Acceptance criteria: screening signals and deprioritization signals are recorded.
Verification command: future `python3 scripts/validate_topic_screening.py`.
Risks: over-filtering suitable topics.
Out of scope: human acceptance.

## Slice 4: Verbalized-Sampling-Assisted Automated Curriculum Review

Goal: optionally produce suitability distributions and uncertainty flags.
Research objective supported: topic identification and feasibility review.
Workflow definition: automated curriculum review.
Evidence produced: review distribution and review manifest.
Models/entities required: automated review artifact references.
Acceptance criteria: output stored separately, includes human_review_required, cannot auto-accept.
Verification command: future `python3 scripts/validate_review_distribution.py`.
Risks: model hallucination, false certainty.
Out of scope: live model requirement.

## Slice 5: Human Topic Selection Gate

Goal: accept, reject, or revise candidate topics with source checks.
Research objective supported: topic identification.
Workflow definition: human topic selection.
Evidence produced: topic selection decisions.
Models/entities required: TopicSelectionDecision.
Acceptance criteria: accepted topics require valid source, reviewed extraction, animation rationale, and recorded reviewer decision.
Verification command: future `python3 scripts/validate_topic_decisions.py`.
Risks: reviewer burden.
Out of scope: generation.

## Slice 6: Topic Brief Run with Manifest and Trace

Goal: generate a topic brief for an accepted topic.
Research objective supported: system design.
Workflow definition: topic brief generation.
Evidence produced: topic brief and run manifest.
Models/entities required: TopicBrief, GenerationRun.
Acceptance criteria: brief references accepted topic and source items.
Verification command: future Django test for topic brief run.
Risks: premature generation complexity.
Out of scope: full animation generation.

## Slice 7: Artifact Inspection Shell

Goal: provide an operator shell to inspect prototype artifacts and record issues.
Research objective supported: system design and feasibility.
Workflow definition: artifact inspection.
Evidence produced: inspection checklist and artifact references.
Models/entities required: VisualArtifact, NarrationArtifact, AssemblyArtifact.
Acceptance criteria: operator can record artifact readiness without evaluator exposure.
Verification command: future Django view tests.
Risks: UI polish overbuild.
Out of scope: expert review scoring.

## Slice 8: Expert Review Submission

Goal: allow evaluators to score artifacts using the rubric.
Research objective supported: feasibility evaluation.
Workflow definition: expert review.
Evidence produced: evaluator profile, invitation, rubric response, comments.
Models/entities required: EvaluatorProfile, EvaluationInvitation, RubricResponse, EvaluatorComment.
Acceptance criteria: web review is canonical and exportable.
Verification command: future Django form/view tests.
Risks: participant data handling.
Out of scope: WhatsApp messaging.

## Slice 9: Evidence Export Bundle

Goal: package analysis tables, provenance JSON, and artifacts.
Research objective supported: feasibility evaluation and reproducibility.
Workflow definition: export.
Evidence produced: export batch and manifests.
Models/entities required: ExportBatch.
Acceptance criteria: CSV/JSON/ZIP outputs include checksums and record counts.
Verification command: future `python3 scripts/validate_export_bundle.py`.
Risks: sensitive comments or identifiers.
Out of scope: public publication.

## Slice 10: Replay/Provenance Verification

Goal: verify deterministic replay where possible and explain AI generation divergence.
Research objective supported: reproducibility.
Workflow definition: replay.
Evidence produced: replay attempt report.
Models/entities required: ReplayAttempt.
Acceptance criteria: deterministic artifacts match or explain failure; external generation divergence is explained.
Verification command: future replay smoke test.
Risks: provider changes.
Out of scope: bit-for-bit AI media replay guarantee.

## Slice 11: WhatsApp Invitation MVP

Goal: support optional opt-in WhatsApp invitation/reminder delivery of secure web review links.
Research objective supported: evaluator coordination.
Workflow definition: WhatsApp invitation.
Evidence produced: template, message log, delivery status.
Models/entities required: EvaluatorContact, WhatsAppMessageTemplate, WhatsAppMessageLog, WhatsAppWebhookEvent.
Acceptance criteria: no full artifact bundles sent; web remains canonical; email/web fallback exists.
Verification command: future template and webhook tests using fake provider.
Risks: privacy, provider credentials, opt-in management.
Out of scope: live WhatsApp credentials in local dev.
