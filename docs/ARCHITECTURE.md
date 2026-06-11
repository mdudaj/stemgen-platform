# Architecture

## Baseline

The platform is a Django application with Viewflow-facing operator surfaces and
Google OAuth2 authentication through `django-allauth`.

Current baseline apps:

```text
apps/
└── users/      # custom email user and superuser bootstrap
```

Planned domain apps after review:

```text
apps/
├── curriculum/
├── experiments/
├── artifacts/
├── evaluations/
├── workflows/
└── observability/
```

## Auth

The repository owns a custom `users.User` model with email as the login
identifier. Google OAuth2 is the primary sign-in path. Local password login is
retained below the OAuth action for superuser recovery and invite-created
accounts.

Superusers can create governed invitations. Invite acceptance creates a local
account, records attribution on `UserInvitation`, and assigns one dissertation
role: Research Operator or Evaluator.

## UI

Auth pages and authenticated pages use separate stylesheet layers:

- `static/dissertation/auth/auth.css`
- `static/dissertation/ui/tokens.css`
- `static/dissertation/ui/components.css`
- `static/dissertation/ui/authenticated.css`

The visual direction borrows LIMS discipline and Viewflow/MDC structure, then
adapts it to an educational research platform: lighter canvas, curriculum
texture, academic blue/teal, and restrained warm accent.

## Infrastructure

Local preview uses PostgreSQL and Redis through Docker Compose. The default
settings fall back to SQLite when `DATABASE_URL` is not set so baseline checks
remain easy to run in a fresh workspace.

## Research Workflow Architecture Direction

Research workflows should follow a governed definition, workflow/runtime, runtime capture, evidence projection, and audit/reconstruction layering. Viewflow remains the preferred process/task runtime. Repo-owned workflow definitions compile into execution manifests; the platform must not generate arbitrary Python Viewflow classes dynamically.

Deterministic curriculum extraction is the source of truth. Optional LLM enrichment and automated review are assistive artifacts and cannot overwrite curriculum facts or promote topics without human acceptance.

