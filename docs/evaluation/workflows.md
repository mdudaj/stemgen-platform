# Evaluation Workflows


Source basis: the proposal uses structured expert review by teachers and subject/curriculum experts; pupils are not direct participants in this phase.

## Purpose

Evaluation workflows preserve the evidence needed for a feasibility-focused design science study. Teachers and subject/curriculum experts are evaluators; pupils are not direct participants in this phase.

## Workflow List

### Curriculum Intake

Register official curriculum sources, create snapshots, extract curriculum items, normalize, validate, and prepare candidate topics.

Evidence: source registry, fetch manifest, checksums, extraction manifest, raw text, normalized curriculum items.

### Topic Brief Creation

Create a concise generation brief from an accepted topic, including source references, learning objective, animation rationale, constraints, and expected artifacts.

Evidence: topic brief JSON/Markdown, source item links, reviewer decision links.

### Generation Run

Launch a prototype generation run using the accepted topic brief and recorded settings.

Evidence: generation manifest, prompt set, provider/model metadata where used, task status, output references.

### Artifact Inspection

Operator reviews script, visual, narration, and assembly artifacts before expert review.

Evidence: inspection checklist, artifact references, issues, refinement decisions.

### Refinement Cycle Logging

Record changes made after inspection or evaluator feedback.

Evidence: refinement log, before/after artifact IDs, reason, actor, timestamp.

### Expert Review Assignment

Assign selected artifacts to evaluators with role/profile context and due date.

Evidence: invitation, evaluator profile, assigned artifact set, review link token.

### Expert Review Submission

Evaluator completes rubric scores and comments through the web platform.

Evidence: rubric response, evaluator comments, submitted-at timestamp, artifact links.

### Rubric Scoring

Store structured 1-5 scores for feasibility criteria.

Evidence: per-criterion scores, comments, required follow-up flags.

### Comment Capture

Capture open comments linked to criteria and artifacts.

Evidence: comments with category, artifact, criterion, and evaluator profile context.

### Export for Descriptive Analysis

Create analysis-ready CSV/JSON/ZIP exports.

Evidence: export batch, export manifest, checksums, included record counts.

### Provenance Verification

Check that artifacts and reviews link back to source curriculum, run manifest, prompts, workflow version, and decisions.

Evidence: provenance verification report.

### Replay Attempt

Attempt deterministic replay where possible and explain divergence for external AI steps.

Evidence: replay attempt report, reproduced artifacts where applicable, divergence explanation.
