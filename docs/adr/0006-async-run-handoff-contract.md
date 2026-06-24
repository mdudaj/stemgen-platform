# ADR 0006: Standardize the async-run handoff contract

## Status

Accepted

## Context

The dissertation platform now has multiple signals that long-running work will be
a recurring workflow shape rather than a curriculum-intake exception. Recent
curriculum-intake debugging exposed two classes of failure that future slices
would otherwise rediscover independently:

1. the local/runtime async stack can be absent or degraded even when the web app
   is up, leaving accepted runs queued without meaningful progress
2. browser navigation behavior can make a valid status page feel like a black-box
   handoff if the launch-to-status transition is not treated as a trust boundary

This is hard to reverse because future generation, replay, export, and evaluation
flows will reuse the same launch and monitoring posture. It is surprising without
context because the repo generally prefers framework defaults such as Turbo
navigation, but trustworthy async monitoring sometimes needs an explicit
full-reload handoff instead.

## Decision

- Treat async launch-to-status behavior as a platform contract, not a per-feature
  UI tweak.
- Keep Turbo as the general navigation model for the platform.
- When a start action launches background work and hands the operator into a
  durable monitoring page, the status destination becomes an explicit trust
  boundary and must support a full page reload handoff.
- Standardize async launch semantics so operators receive:
  - immediate submit acknowledgement
  - an explicit redirect into a durable status surface
  - operator-visible queued/running/completed/failed state language
  - terminal handoff actions for retry, review, promotion, or downstream work
- Require runtime readiness checks for async launch flows so missing worker or
  broker dependencies are surfaced before or at launch acceptance instead of
  being discovered only after a run appears stuck.
- Keep progress and degraded-state evidence in durable run metadata or execution
  trace surfaces rather than transient browser-only state.
- Treat temporary form-level Turbo opt-outs as short-term safety patches, not the
  preferred long-term baseline.

## Consequences

- Future async workflows should share one navigation and monitoring contract
  instead of inventing ad hoc launch behavior.
- The platform now has an explicit distinction between ordinary Turbo-friendly
  page navigation and async status destinations that must privilege trust and
  observability over navigation cleverness.
- Local preview and deployment guidance must include async runtime readiness as
  part of the expected stack, not as optional setup knowledge.
- The repo should add shared helpers, skill guidance, and verification patterns
  for async launch flows instead of solving the same problem at the template
  layer repeatedly.

## Alternatives Considered

### Disable Turbo on every async launch form

Rejected as the long-term baseline because it solves the symptom locally but
pushes the real rule into scattered form implementations rather than defining one
platform-level handoff contract.

### Keep Turbo defaults everywhere and rely on status-page refresh only

Rejected because it allowed a trustworthy server-rendered status page to feel
like a black box until manual refresh, which is unacceptable for operator-facing
background work.

### Detect worker/runtime failures only after launch on the status page

Rejected because operators should not learn that the async runtime is missing
only after the platform has already accepted the launch.
