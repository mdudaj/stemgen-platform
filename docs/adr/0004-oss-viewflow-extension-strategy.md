# ADR 0004: Recreate required Viewflow Pro features locally

## Status

Accepted

## Context

The platform uses `django-viewflow` as the workflow and frontend foundation, but
the dissertation repo should remain buildable and runnable from open-source
dependencies and repo-owned code.

Some desirable Viewflow capabilities may only exist in Pro/commercial variants
or may be easier to achieve there. The project still needs those behaviors in a
few places, but it should not let paid-package availability dictate the
architecture.

## Decision

- Keep the platform on the OSS `django-viewflow` package baseline.
- If a needed capability is only available in Viewflow Pro, recreate it locally
  behind repo-owned seams instead of adopting Pro as a dependency.
- Keep those recreations thin, explicit, and app-scoped where possible.
- Record any significant local recreation seam in docs and code close to where
  it is introduced.

## Consequences

### Positive

- The repo remains reproducible from open dependencies plus local code.
- Dissertation outputs are not blocked on paid-package procurement.
- Extension seams stay explicit and reviewable.

### Negative

- The repo may need to maintain a small set of local replacements for missing
  Pro features.
- Some UX/workflow features may take longer to build than if Pro were adopted.

## Alternatives considered

### Adopt Viewflow Pro for any missing capability

Rejected because it weakens the repo's local-first, reproducible OSS baseline.

### Avoid all features that look Pro-like

Rejected because the platform still needs practical operator and evaluation
workflows; some gaps should be solved locally rather than avoided entirely.
