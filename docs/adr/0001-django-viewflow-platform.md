# ADR 0001: Use Django and Viewflow as the platform foundation

## Status

Accepted

## Context

The dissertation platform needs operator-facing interfaces for experimentation and evaluation, plus a workflow-oriented backend that can preserve observability and reproducibility artifacts across long-running work. The chosen direction is Django for the web platform and `django-viewflow` as the rapid-development foundation for both workflow and frontend capabilities.

The repository is currently at harness-bootstrap stage, so this ADR records the platform direction early enough to keep future scaffolding aligned.

## Decision

- Use Django as the primary application framework.
- Use `django-viewflow` as the rapid-development workflow and frontend foundation for operator-facing experimentation and evaluation interfaces.
- Keep the platform on the OSS Viewflow baseline; if a needed Pro-only capability appears later, recreate it locally behind repo-owned seams instead of adopting Pro by default.
- Treat observability and reproducibility as first-class constraints rather than later enhancements.
- Introduce the actual Django project through the first vertical slice instead of through setup-only work.

## Consequences

- The repo needs durable Python dependency manifests from the start.
- Runs will need manifest-backed provenance, not only database state.
- Long-running generation work should eventually move to background execution rather than stay request-bound.
- The platform should start by leaning on Viewflow's built-in workflow and frontend modules rather than assuming bespoke UI and orchestration code.
- If later work requires capabilities beyond the chosen OSS `django-viewflow` posture, the default response is to recreate them locally; any actual package/edition change must be recorded in a follow-up ADR before implementation.

## Alternatives Considered

### CLI-first pipeline without a web platform

Rejected because the dissertation explicitly needs experimentation and evaluation interfaces, not only backend automation.

### Django without Viewflow

Rejected for now because the project benefits from a workflow-oriented UI and process model rather than inventing bespoke orchestration screens from scratch.
