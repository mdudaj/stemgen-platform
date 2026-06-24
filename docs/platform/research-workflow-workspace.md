# Research Workflow Workspace

## Purpose

The Research Workflow Workspace is the operator surface for defining, previewing, reviewing, publishing, and monitoring research workflows. It is inspired by the LIMS Operation Workspace but uses research-platform terminology.

## Tabs

| Tab | Purpose | Main user | Actions | Evidence shown | Safety constraints |
| --- | --- | --- | --- | --- | --- |
| Summary | Show workflow identity, purpose, lifecycle state, latest version, validation health, recent activity, and next safe action. | Research operator | View status, open draft, start validation, open latest run. | Objective links, version status, validation findings, recent run summaries. | No evidence mutation from summary cards. |
| Curriculum | Manage source registry, snapshots, extraction status, candidate topics, screening, automated review output, and human selection state. | Research operator | Register source, view snapshot manifest, inspect extraction, open topic decisions. | Source registry, checksums, normalized items, candidate dataset, review distributions, decisions. | TIE facts are read-only after snapshot; LLM review cannot overwrite deterministic records. |
| Workflow | Configure nodes, roles, transitions, async settings, artifact outputs, and validation gates. | Research operator and reviewer | Edit draft nodes, validate definition, inspect transition graph, prepare publication review. | Definition diff, node list, transitions, role bindings, artifact schemas. | Controlled expressions only; no arbitrary executable code. |
| Runtime Preview | Preview the same runner contract used by real workflow steps without creating canonical evidence. | Research operator | Run preview with sample payloads, inspect runner artifact, review validation. | Preview manifest, sample submissions, validation messages, no production records. | Preview cannot publish, project, export, or alter accepted evidence. |
| Versions | Show draft, published versions, checksums, publication notes, and compatibility. | Research operator and reviewer | Compare versions, open publication review, deprecate future versions. | Version snapshots, manifest hashes, publication approvals. | Published versions are immutable. |
| Settings | Manage allowed roles, artifact retention, export settings, provider boundaries, and channel policy. | Project maintainer | Edit draft settings, validate high-risk settings. | Settings snapshot, safety warnings, approval requirements. | Model provider, WhatsApp, data collection, and export changes require review. |
| Review | Gate publication and high-risk workflow changes. | Reviewer | Approve, request changes, block, record rationale. | Validation report, objective mapping, safety checklist, diff, test plan. | No publication without review for high-risk workflows. |

## Runtime Preview Contract

The `Runtime Preview` tab must use the same input/output contract as the real runner:

- workflow version or draft compile hash;
- workflow node ID;
- actor role;
- sample raw payload;
- normalized payload;
- validation result;
- proposed acceptance decision;
- projected output preview.

Preview runs must be marked `preview_only` and excluded from canonical evidence, exports, and replay baselines.
