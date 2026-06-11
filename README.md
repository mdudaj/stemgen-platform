# Kisomo Dissertation Platform Harness

Cookiecutter-style Django + Viewflow harness for a dissertation platform focused
on curriculum-aligned STEM media experimentation, artifact review, and
feasibility evidence.

## Current State

This rebuild currently includes the baseline harness only:

- Django project scaffold
- custom email-based user model
- Google OAuth2 integration through `django-allauth`
- local email/password fallback for superusers and invite-created accounts
- governed invitation acceptance flow
- Viewflow auth shell
- left-panel Kisomo login screen using `static/img/` assets
- separated auth and authenticated design-system CSS layers

Curriculum intake, topic-brief runs, artifact review, replay, and export slices
are intentionally held for review before being restored.

## Bootstrap

```bash
./init.sh
```

## Local Preview

```bash
./scripts/local_preview.sh prep
./scripts/local_preview.sh dev
```

Useful commands:

- `./scripts/local_preview.sh prep` - start Postgres/Redis and apply migrations
- `./scripts/local_preview.sh dev` - prepare services/migrations, then run the Django development server
- `./scripts/local_preview.sh test` - run Django checks and user/auth tests
- `./scripts/local_preview.sh down` - stop preview services
- `./scripts/local_preview.sh status` - show preview service status
- `./scripts/local_preview.sh urls` - print local preview and OAuth callback URLs
- `./scripts/local_preview.sh create-superuser --email admin@example.com`

## Google OAuth

Set these values in `.env` to enable Google sign-in:

```bash
GOOGLE_OAUTH_CLIENT_ID=your-google-client-id
GOOGLE_OAUTH_CLIENT_SECRET=your-google-client-secret
GOOGLE_OAUTH_HD=
```

Register the callback URI in Google Cloud Console:

```text
http://localhost:8000/accounts/google/login/callback/
http://127.0.0.1:8000/accounts/google/login/callback/
```

If the preview runs on another port, register that exact callback too, for
example:

```text
http://127.0.0.1:8002/accounts/google/login/callback/
```

Leave `GOOGLE_OAUTH_HD` blank to allow any Google account. Set it only when
sign-in should be constrained to one Google Workspace hosted domain.

## Local Superuser And Invites

The login page keeps a local email/password fallback below Google sign-in for
superuser recovery and invite-created local accounts.

Superusers can create invitations at:

```text
/accounts/invite/new/
```

Invite acceptance creates a local account and assigns either the Research
Operator or Evaluator role.

## Milestone 22.5 Planning Artifacts

Evaluation and curriculum-readiness planning lives under:

- `docs/research/`
- `docs/curriculum/`
- `docs/evaluation/`
- `docs/platform/`
- `docs/repository/`
- `docs/adr/0007-0011*.md`

These artifacts define the next implementation slices for reproducible TIE curriculum data, configurable research workflows, expert review, evidence export, provenance/replay, WhatsApp evaluator coordination, and gated project repository writes.


The planning artifacts are aligned with the proposal PDF under `/home/jmduda/Desktop/UDSM/Dissertation/` and the initial platform ADRs from `/home/jmduda/Desktop/FikraBytez/dissertation/docs/adr/`, now copied into `docs/adr/0001-0006*.md`.

