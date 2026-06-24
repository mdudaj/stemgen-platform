# Provenance and Replay

## Purpose

The platform must record enough information to explain how curriculum topics, generated artifacts, expert reviews, and exports were produced.

## Replay Expectation

Deterministic layers should replay exactly where possible. External AI generation may not replay bit-for-bit. The platform must record enough metadata to explain divergence.

## Deterministic Layers

Expected to replay exactly or fail with an explainable difference:

- source registry loading;
- checksum verification;
- text/table extraction with fixed extractor version;
- normalization with fixed rules;
- rule-based topic screening;
- export packaging from fixed records.

## Non-Deterministic or External Layers

Expected to be explainable, not bit-for-bit identical:

- LLM enrichment;
- verbalized-sampling-inspired automated review;
- image/video/audio generation;
- external provider responses.

## Provenance Fields

- source snapshot ID;
- workflow definition/version/checksum;
- run ID and step IDs;
- actor or system principal;
- timestamps;
- provider/model where used;
- prompt template ID and input hash;
- output hash;
- artifact checksums;
- validation results;
- human acceptance decisions;
- export batch ID.

## Replay Attempt Report

A replay report should include:

- replay_id;
- original run IDs;
- requested deterministic scope;
- environment/tool versions;
- artifacts reproduced exactly;
- artifacts divergent;
- divergence explanation;
- missing dependencies;
- reviewer notes.
