# TIE Source Snapshot Plan

## Purpose

Define how official TIE curriculum sources will be captured reproducibly before extraction. Milestone 22.5 does not perform live downloads unless a future explicit fetch command exists.

## Snapshot Steps

1. Load `docs/curriculum/source-registry.md` into a machine-readable registry.
2. Fetch each Tier 1 URL with an explicit operator command.
3. Store files under `artifacts/curriculum-snapshots/<snapshot_id>/downloaded_sources/`.
4. Record URL, timestamp, HTTP status, content type, byte count, and local path in `fetch_manifest.json`.
5. Compute SHA-256 checksums for each downloaded file.
6. Record checksum values in `checksums.sha256` and `fetch_manifest.json`.
7. Freeze the snapshot ID for downstream extraction.

## Snapshot ID

Use a stable ID such as:

```text
YYYYMMDD-tie-primary-stem-v1
```

## Failure Handling

- If a URL is unavailable, record the failure in `fetch_manifest.json`.
- Do not substitute unofficial copies without manual registry review.
- Do not overwrite an existing snapshot; create a new snapshot ID.

## Manual Review

A human reviewer should confirm source titles, years, subject coverage, standards covered, and licensing caution before the first accepted topic shortlist.
