# Branching Policy

## Purpose

Branching rules keep project repository pushes reviewable and prevent accidental mutation of protected branches.

## Rules

- Do not commit or push directly to `main` or `master`.
- Use a descriptive branch such as `karakana/evaluation-readiness`.
- Verify the remote URL before pushing.
- Push only the named branch passed explicitly by the user or command.
- Do not force push.
- Do not auto-create PRs from project repository push commands.
- Keep generated runtime artifacts out of commits unless they are intentional source fixtures or documentation artifacts.

## Recommended Branch Names

- `karakana/evaluation-readiness`
- `karakana/curriculum-source-registry`
- `karakana/expert-review-slice`
- `karakana/whatsapp-channel-design`

## Main/Master Handling

If the checkout is on `main` or `master`, the gated command must create or require a safe feature branch before commit/push.
