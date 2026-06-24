# Curriculum Intake IA User Stories

Date: 2026-06-20

## Artifact Gate

- Work type: UI/UX, generated identifiers, route organization, curriculum source workflow.
- Required artifacts: UX grill, ADR, user stories, milestone/readiness note, tests.
- Existing artifacts reused: ADR 0008, source registry docs, TIE snapshot plan, curriculum UX research notes.
- New artifacts: ADR 0012 and this user-story artifact.
- Implementation boundary: split intake into focused pages and generate IDs; no extraction, topic screening, review, generation, or export.
- Verification required: Django view/form/service tests and JSON/schema validation where fixtures change.

## Roles

- Staff operator: manages curriculum source evidence and snapshots.
- Superuser/administrator: manages configuration only.
- Non-staff authenticated user: cannot access curriculum management pages.

## Story 1: Open Curriculum Hub

As a staff operator, I want a single Curriculum menu item so that I can choose the relevant curriculum task without scanning sidebar submenus.

Acceptance criteria:

- Sidebar shows `Dashboard` and `Curriculum` as sibling top-level items for staff users.
- `/curriculum/` shows action cards for source management, snapshot capture, and snapshot review.
- `/curriculum/` does not embed source or snapshot forms.
- Non-staff users receive forbidden access for curriculum routes.

## Story 2: Manage Sources

As a staff operator, I want to review registered TIE sources in a focused list so that I can verify official links before snapshot capture.

Acceptance criteria:

- `/curriculum/sources/` lists registered sources in a full-width table/list.
- The page has a back icon action to `/curriculum/`.
- The page has an action to add a new official source.
- Technical `source_id` UUID values are not entered by users and are not primary table content.

## Story 3: Add Official TIE Source

As a staff operator, I want to add an official curriculum or syllabus URL and metadata so that the system can register a governed source.

Acceptance criteria:

- `/curriculum/sources/new/` has one form for one task.
- The form asks for document type, title, official URL, subject/scope, coverage, standards, expected filename, tier, and active state.
- The form does not include a `source_id` input.
- The system assigns a UUID source ID using ADR 0012.
- Source descriptions provide the operator-facing context.
- Form controls use Material/Viewflow/Kisomo styling with visible labels.

## Story 4: Capture Snapshot

As a staff operator, I want to capture a snapshot from active sources with a human-readable description and without choosing a technical ID so that evidence IDs are consistent and traceable without cluttering the UI.

Acceptance criteria:

- `/curriculum/snapshots/new/` has one capture form.
- The form does not include a `snapshot_id` input.
- The system assigns a UUID snapshot ID and uses the description as the human-facing label.
- The page blocks capture when no active sources exist.
- Capture uses active registered sources only.
- The page has a back icon action to `/curriculum/` or `/curriculum/snapshots/` according to entry context.

## Story 5: Review Snapshots

As a staff operator, I want to review captured snapshots separately from source intake so that inspection stays focused and read-only.

Acceptance criteria:

- `/curriculum/snapshots/` remains the read-only snapshot list.
- Snapshot detail remains read-only and links captured source evidence.
- Snapshot pages have icon back actions.
- No approve, accept topic, extraction, or screening action appears in this slice.

## Non-Goals

- PDF extraction.
- Topic screening.
- Automated curriculum review.
- Human topic selection.
- Workflow engine integration.
- WhatsApp messaging.
- Generation runs.
- Export/replay.
