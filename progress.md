# Session Progress Log

## Current State

**Last Updated:** 2026-06-24
**Active Feature:** feat-003 - Rule-Based Topic Screening

## Done

- [x] Normalized Kisomo image assets under `static/img/`.
- [x] Exported PNG assets for auth background, brand, muted hero, and Google mark.
- [x] Added Django project scaffold.
- [x] Added custom email-based user model and admin/forms/management command.
- [x] Added Google OAuth2 configuration through `django-allauth`.
- [x] Added left-panel Google-only login template.
- [x] Added separated dissertation auth/authenticated UI CSS layers.
- [x] Verified the baseline harness with `./init.sh`.
- [x] Applied baseline migrations with `python manage.py migrate --noinput`.
- [x] Verified focused auth/user behavior with `python manage.py test apps.users`.
- [x] Validated feature tracking JSON with `python scripts/validate_json.py`.
- [x] Verified the login page responds with `200 OK` at `/accounts/login/`
      on the local dev server.
- [x] Restored local email/password login below Google sign-in for superuser
      recovery and invite-created accounts.
- [x] Added governed user invitations with Research Operator and Evaluator
      roles, superuser-only invite creation, and invite acceptance.
- [x] Copied the relevant Google OAuth environment keys from the old
      dissertation `.env` into this workspace `.env` without carrying old
      database assumptions.
- [x] Verified `/accounts/google/login/` redirects to Google using the copied
      OAuth configuration.
- [x] Fixed `scripts/local_preview.sh` so `prep` waits for a real Postgres
      connection before migrations, `dev` prepares services before serving, and
      `down/status/logs/urls` are supported.
- [x] Replaced the authenticated Viewflow default page shell with a Kisomo-owned
      shell: side navigation, top bar, Dashboard, and Configuration / Users &
      Roles.
- [x] Delivered Milestone 22.5 evaluation-readiness documentation, ADRs,
      evidence schemas, and vertical-slice roadmap.
- [x] Added schema-backed curriculum source registry and reproducible snapshot
      evidence models with UUID identifiers.
- [x] Added staff-only curriculum intake surfaces for source management,
      default TIE source seeding, snapshot capture, and read-only snapshot
      review.
- [x] Added source registry fixtures, schema examples, snapshot command/service
      coverage, and dashboard evidence/status integration.
- [x] Hardened PostgreSQL UUID evidence migration by dropping non-constraint
      text-pattern indexes before UUID column conversion.
- [x] Squash-merged Milestone 22.5 delivery through PR #1 and verified with
      `./init.sh`, `python3 scripts/validate_json.py`, and
      `.venv/bin/python manage.py test apps.curriculum apps.users config`.
- [x] Added Slice 2 deterministic Science and Mathematics curriculum extraction
      from captured source snapshots.
- [x] Added `curriculum_extract create` to write `curriculum_items.json` and
      `candidate_topics.json` with source/page/section provenance and pending
      animation-suitability fields.
- [x] Added schema examples and validation coverage for curriculum item
      datasets and candidate topic datasets.

## In Progress

- [ ] Prepare Slice 3: rule-based topic screening for candidate topics.

## Next Review

- [ ] Define deterministic animation-suitability signals, deprioritization
      reasons, and human-review handoff criteria without accepting topics
      automatically.
