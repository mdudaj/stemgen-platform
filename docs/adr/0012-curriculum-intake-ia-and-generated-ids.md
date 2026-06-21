# ADR 0012: Curriculum Intake IA and UUID Evidence IDs

Date: 2026-06-20

## Status

Accepted for next curriculum UX revision.

## Context

The first curriculum intake UI exposed too many actions on one page: source registration, seeding, snapshot capture, latest snapshot state, and source registry table. It also asked users to enter `source_id` and `snapshot_id` values directly.

That creates cognitive load and increases the chance of unstable identifiers. For this research platform, users should provide curriculum facts and official links; the system should generate stable technical identifiers and route users through focused task pages.

## Decision

1. Use `/curriculum/` as the Curriculum landing page and action hub.
2. Keep one top-level sidebar item: `Curriculum`, sibling to `Dashboard`.
3. Split curriculum work into focused pages:
   - `/curriculum/sources/` lists registered sources.
   - `/curriculum/sources/new/` adds an official TIE source.
   - `/curriculum/snapshots/new/` captures a snapshot from active sources.
   - `/curriculum/snapshots/` reviews snapshots.
4. Do not ask users to type source IDs or snapshot IDs.
5. Use UUID-backed source IDs and snapshot IDs in the system layer.
6. Keep UUIDs out of ordinary operator-facing tables and headings; use titles and descriptions for human context.
6. Keep child pages equipped with top-header icon back actions.
7. Use Material/Viewflow/Kisomo form components, Viewflow form layouts/rendering, and visible labels throughout.
8. Use reusable page-stack spacing so major sibling surfaces never touch.
9. Use reusable Material/MDC tabs for sibling status/list panels on the Curriculum hub, with bottom active indicators by default.
10. Style tab panel contents as structured summaries, metrics, panels, or empty states rather than punctuation-separated prose.
11. Use full-width Viewflow/Material form cards for focused form routes, with fields rendered through Viewflow layouts.
12. Keep sibling action cards structurally consistent: icon policy, content body, action region, action-button styling, and button placement must match.
13. Use reusable labeled back actions that state their destination.

## UUID ID Rules

### Source ID

Generated as a UUID. Seed fixtures use stable UUIDs so repeated seeding is idempotent. Runtime-created sources use UUID identifiers assigned by the system.

Operators do not enter or normally inspect the UUID. Source title, description, subject, standards, tier, and official URL provide the readable context.

### Snapshot ID

Generated as a UUID when capture starts. Snapshot descriptions explain why the snapshot was captured and are the operator-facing label in lists and status panels.

## UX Organization Rules

- Cards are for action entry points and short summaries.
- Dense source and snapshot records use list/table pages, not action cards.
- Forms are isolated to task pages.
- The user sees one primary task per page.
- Breadcrumbs show hierarchy, while icon back buttons support common parent navigation.
- Major page sections use stack spacing rather than touching adjacent components.
- Curriculum hub status panels use Material/MDC tabs when source and snapshot content would otherwise compete vertically.
- Active tab indicators use bottom placement unless an explicit project style overrides it.
- Tab panel content uses reusable styled summaries such as metric lists or empty states.
- Form routes use a reusable Viewflow/Material form-card abstraction that renders Viewflow layouts, not template-level field loops.
- Sibling action cards use the same icon/body/action-region structure so buttons align across the group.
- Back navigation uses a reusable labeled icon+text action.

## Consequences

- Existing `/curriculum/intake/` should become either a redirect or be replaced by focused source/snapshot pages.
- Tests must assert that source/snapshot IDs are UUID-backed, not required form inputs, and not primary visible table content.
- Tests must assert that the Curriculum landing page exposes action cards, not embedded multi-action forms.
- Documentation and fixtures must distinguish legacy fixture IDs from generated runtime IDs.

## Verification

- Django tests for UUID source and snapshot ID generation behavior.
- View tests for separated route access and back actions.
- UX tests/assertions that source and snapshot forms do not render ID inputs.
- UX tests/assertions for page-stack spacing hooks, MDC tab markup, bottom active indicators, structured tab-panel content, Viewflow-rendered form fields, labeled back actions, and aligned action-card action regions.
