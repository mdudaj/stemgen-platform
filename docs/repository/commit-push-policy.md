# Commit and Push Policy

## Purpose

Karakana may commit and push to external project repositories only through explicit, gated, auditable commands. This policy enables project repository work without changing the default no-push behavior.

## Required Rules

- No commit by default.
- No push by default.
- No push to main/master.
- No force push.
- No push with failing patch gates.
- No push with blocked patch review.
- No push with secrets.
- No push if worktree contains unrelated changes.
- No push without explicit branch.
- No push without explicit `--push`.
- No push without remote verification.

## Allowed Flow

```text
patch review
  -> patch gate
  -> optional local branch
  -> optional patch apply
  -> optional tests
  -> optional local commit
  -> optional push to remote branch
```

## Proposed Commands

Prefer extending the existing patch lifecycle:

```bash
karakana patch commit \
  --patch-run <patch-run-id> \
  --message "docs: define evaluation-readiness artifacts" \
  --write

karakana patch push \
  --patch-run <patch-run-id> \
  --branch karakana/evaluation-readiness \
  --remote origin \
  --push
```

A project-specific command may be added later if cross-repository path resolution needs a clearer UX.

## Push Preconditions

Before push:

- workspace project resolved;
- repo path exists;
- remote URL verified;
- current branch is not main/master;
- target branch is not main/master;
- patch review not blocked;
- patch gate passed;
- tests attached or justified;
- no secret findings;
- no force push requested;
- user explicitly passed `--push`.

## Audit Record

Commit/push commands should record:

- project ID and path;
- patch run ID;
- branch and remote;
- commit SHA;
- push result;
- patch review and gate artifacts;
- tests run or justification;
- actor and timestamp.
