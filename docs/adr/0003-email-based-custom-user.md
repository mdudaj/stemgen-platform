# ADR 0003: Use an email-based custom user model

## Status

Accepted

## Context

The dissertation platform needs authenticated operator and evaluator access, and
the repository had not yet committed to a long-term user identity model.

Django's default `auth.User` uses `username` as the login identifier. That would
force the project either to carry an extra username field that has no clear value
in the dissertation workflow or to defer the user-model decision until after more
application code and migrations exist.

Because the platform already expects user-facing workflow and evaluation
surfaces, the user model is a hard-to-reverse choice and should be fixed before
later slices add relationships to users.

## Decision

The platform will use a custom Django user model at `users.User` with:

- `email` as the unique login identifier
- no `username` field
- standard Django permissions/group support
- admin/forms wired for email-based account creation and editing

The local preview workflow also resets a legacy local development database when
it still reflects `auth.User` migration history, backing it up first under
`.scratch/db-backups/`.

## Consequences

### Positive

- Authentication aligns with the expected operator/evaluator identity model.
- Future models can safely reference `settings.AUTH_USER_MODEL` from the start.
- Admin and `createsuperuser` flows use email naturally.
- The project avoids a risky late-stage user-model swap.

### Negative

- Existing local dev databases created before this decision need a one-time reset
  to avoid inconsistent migration history.
- Any future code must consistently use `settings.AUTH_USER_MODEL` or
  `get_user_model()` instead of importing Django's default user model directly.

## Alternatives considered

### Keep Django's default `auth.User`

Rejected because it bakes in a `username` field the platform does not want and
makes a future custom-user migration harder.

### Add email login while keeping `username` as the actual identity field

Rejected because it preserves the same long-term mismatch while adding extra
auth complexity.
