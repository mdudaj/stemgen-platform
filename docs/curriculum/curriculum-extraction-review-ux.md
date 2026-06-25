# Curriculum Extraction Review UX

## Artifact Gate

- Work type: frontend, curriculum evidence workflow, data artifact review.
- Required artifacts: behavior requirements, look-and-feel requirements, acceptance criteria, design-system fit, accessibility checklist, tests, handoff.
- Existing artifacts reused: ADR 0008, ADR 0011, `docs/curriculum/curriculum-data-schema.md`, `docs/platform/vertical-slice-roadmap.md`, `docs/curriculum/topic-screening-rules.md`.
- New or updated artifacts: this UX note, extraction web views/templates/tests, feature and progress bookkeeping.
- Implementation boundary: staff-only web launch and review surface for deterministic extraction artifacts; no topic screening, human acceptance, LLM review, or database promotion.
- Verification required: schema validation, focused Django curriculum tests, render/response checks for staff and non-staff access.

## Behavior Requirements

Staff operators must be able to launch deterministic curriculum extraction from the web after a source snapshot exists. The UI must:

- list snapshots that can be used for extraction;
- show whether extraction artifacts already exist for each snapshot;
- provide a POST-only extraction launch action;
- prevent duplicate extraction over an existing artifact directory;
- show extraction artifact paths, item count, candidate topic count, validation status, and validation errors;
- render curriculum items with subject, standard, topic, source title, page/section/table reference, raw excerpt, and warning status;
- render candidate topics with source item links, pending review status, empty screening signals, and deprioritization reasons;
- make clear that extraction review does not accept topics and does not perform animation suitability screening.

## Look And Feel Requirements

The extraction UI must follow the existing Kisomo authenticated design system:

- use the existing page stack, object header, action cards, metric list, table, state chip, and labeled back-action patterns;
- keep the page dense and evidence-focused, avoiding marketing or landing-page composition;
- present extraction launch and review as peers to source and snapshot management;
- use Material icons consistently in action cards and buttons;
- avoid nested cards and page-local colors;
- keep table content scannable with stable headings and wrapped code/reference text.

## Best-Practice Research

W3C WCAG 2.2 is the accessibility baseline for this web workflow. It emphasizes testable accessibility criteria and includes guidance relevant to this slice: page titles, headings and labels, focus visibility, consistent navigation/identification, labels or instructions, error identification, and status messages. Source: <https://www.w3.org/TR/WCAG22/>.

For this evidence-review task, the platform should favor predictable navigation, explicit status feedback, visible labels, and tabular comparison of source-linked records. These are applied through the existing Kisomo/Viewflow patterns rather than introducing a new UI framework.

## Design-System Fit

The page belongs under `curriculum/` and uses the authenticated CSS stack:

- `kisomo-page-stack` for page rhythm;
- `kisomo-object-header` for title and actions;
- `kisomo-action-card` for launch/review entry points;
- `kisomo-metric-list` for counts and validation state;
- `kisomo-table` for evidence review;
- `kisomo-state-chip` for compact statuses;
- `app/partials/back_action.html` for labeled back navigation.

## Accessibility Checklist

- Pages have explicit titles and breadcrumbs.
- Launch actions are real forms with CSRF protection.
- Buttons have visible text and icons marked decorative with `aria-hidden`.
- Tables have stable column headers.
- Empty and blocked states are rendered as text, not color alone.
- Messages and validation errors are visible after POST.
- Staff-only access is enforced server-side, not only by navigation.

## Acceptance Criteria

- A staff user can open an extraction review page from Curriculum.
- A staff user can launch extraction for a snapshot from the web and is redirected to artifact review.
- Existing extraction artifacts are shown as already generated and cannot be overwritten from the UI.
- A staff user can inspect item and candidate-topic tables linked to source/page/section references.
- Anonymous users are redirected to login and non-staff users receive forbidden responses.
- The UI copy preserves the boundary: not screened, not accepted, no human topic decision.
- Focused tests cover launch, review, access control, and duplicate-artifact behavior.

## Definition Of Done

- The corrective Slice 2.1 UX artifact exists.
- The curriculum home page exposes extraction as a first-class action.
- Staff-only extraction list/detail/launch routes exist.
- Extraction detail renders generated artifact content for review.
- Validation and Django tests pass.
- Remaining risks and next action are recorded in `progress.md`.
