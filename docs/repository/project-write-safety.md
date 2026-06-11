# Project Write Safety

## Purpose

Project repository writes are high-risk because Karakana can operate across workspaces. Write actions must be project-scoped, explicit, and auditable.

## Safety Checks

- Resolve exactly one project path from workspace metadata.
- Confirm the path is a Git repository.
- Check the current branch and upstream.
- Reject main/master push targets.
- Reject force push.
- Reject unreviewed diffs.
- Reject blocked paths such as `.env`, `.env.*`, and `secrets/**`.
- Run secret scan before commit and push.
- Require patch review and patch gate artifacts.
- Require tests or a recorded justification.
- Refuse when unrelated worktree changes are present.

## Blocked Content

- secrets;
- `.env` files;
- participant-sensitive data;
- raw generated evaluation data unless explicitly selected and redacted;
- live credentials;
- provider authorization headers.

## Default Behavior

Read-only by default. Planning, requirements, docs generation, evals, and patch review do not imply commit or push.
