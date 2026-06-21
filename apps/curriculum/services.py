from __future__ import annotations

import hashlib
import json
import shutil
import urllib.request
import uuid
from dataclasses import dataclass
from datetime import UTC
from datetime import datetime
from pathlib import Path
from typing import Callable

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from jsonschema import Draft202012Validator
from jsonschema import ValidationError as JsonSchemaValidationError

from apps.curriculum.models import CurriculumSnapshot
from apps.curriculum.models import CurriculumSnapshotSource
from apps.curriculum.models import CurriculumSource


FetchResult = tuple[bytes, str]
Fetcher = Callable[[CurriculumSource], FetchResult]

DEFAULT_TIMEOUT_SECONDS = 20
SOURCE_REGISTRY_FIXTURE = Path("fixtures/curriculum/tie_sources.json")


@dataclass(frozen=True)
class SnapshotPlan:
    snapshot_id: uuid.UUID
    artifact_root: Path
    sources: tuple[CurriculumSource, ...]
    description: str = ""


def load_source_registry(path: Path | None = None) -> list[dict]:
    registry_path = path or settings.BASE_DIR / SOURCE_REGISTRY_FIXTURE
    with registry_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def seed_curriculum_sources(path: Path | None = None) -> list[CurriculumSource]:
    sources: list[CurriculumSource] = []
    for item in load_source_registry(path):
        source, _created = CurriculumSource.objects.update_or_create(
            source_id=normalize_uuid(item["source_id"]),
            defaults={
                "title": item["title"],
                "description": item.get("description", item.get("coverage", "")),
                "official_url": item["official_url"],
                "publisher": item.get("publisher", "Tanzania Institute of Education"),
                "source_tier": item.get("source_tier", CurriculumSource.SourceTier.TIER_1),
                "subject": item["subject"],
                "coverage": item["coverage"],
                "standards_covered": item["standards_covered"],
                "expected_filename": safe_filename(item["expected_filename"]),
                "checksum_algorithm": item.get("checksum_algorithm", "sha256"),
                "is_active": True,
            },
        )
        sources.append(source)
    return sources


def plan_snapshot(
    *,
    snapshot_id: str | uuid.UUID | None = None,
    source_registry_path: Path | None = None,
    description: str = "",
) -> SnapshotPlan:
    sources = tuple(seed_curriculum_sources(source_registry_path))
    resolved_snapshot_id = normalize_uuid(snapshot_id) if snapshot_id else default_snapshot_id()
    return SnapshotPlan(
        snapshot_id=resolved_snapshot_id,
        artifact_root=artifact_root(resolved_snapshot_id),
        sources=sources,
        description=description,
    )


@transaction.atomic
def create_snapshot(
    *,
    snapshot_id: str | uuid.UUID | None = None,
    source_registry_path: Path | None = None,
    description: str = "",
    no_download: bool = False,
    use_local_cache: bool = False,
    validate: bool = False,
    created_by=None,
    fetcher: Fetcher | None = None,
) -> CurriculumSnapshot:
    plan = plan_snapshot(snapshot_id=snapshot_id, source_registry_path=source_registry_path, description=description)
    if plan.artifact_root.exists():
        raise ValidationError(f"Snapshot artifact directory already exists: {plan.artifact_root}")

    snapshot = CurriculumSnapshot.objects.create(
        snapshot_id=plan.snapshot_id,
        description=plan.description,
        status=CurriculumSnapshot.Status.RUNNING,
        created_by=created_by if getattr(created_by, "is_authenticated", False) else None,
        artifact_root=relative_path(plan.artifact_root),
        source_count=len(plan.sources),
    )

    downloaded_dir = plan.artifact_root / "downloaded_sources"
    downloaded_dir.mkdir(parents=True, exist_ok=False)

    warnings: list[str] = []
    source_entries: list[CurriculumSnapshotSource] = []
    checksum_lines: list[str] = []

    write_json(plan.artifact_root / "source_registry.json", source_registry_payload(plan.sources, snapshot_id=plan.snapshot_id))

    for source in plan.sources:
        entry = CurriculumSnapshotSource.objects.create(
            snapshot=snapshot,
            source=source,
            status=CurriculumSnapshotSource.Status.PENDING,
            original_url=source.official_url,
            stored_filename=safe_filename(source.expected_filename),
            stored_path=relative_path(downloaded_dir / safe_filename(source.expected_filename)),
        )
        try:
            if no_download:
                entry.status = CurriculumSnapshotSource.Status.SKIPPED
                entry.error_message = "Download skipped by --no-download."
            else:
                capture_source(
                    source=source,
                    entry=entry,
                    downloaded_dir=downloaded_dir,
                    checksum_lines=checksum_lines,
                    use_local_cache=use_local_cache,
                    fetcher=fetcher or fetch_source,
                )
        except Exception as exc:  # noqa: BLE001 - failures are evidence for the manifest.
            entry.status = CurriculumSnapshotSource.Status.FAILED
            entry.error_message = str(exc)
            warnings.append(f"{source.title}: {exc}")
        entry.save()
        source_entries.append(entry)

    (plan.artifact_root / "checksums.sha256").write_text("".join(checksum_lines), encoding="utf-8")
    write_json(plan.artifact_root / "fetch_manifest.json", fetch_manifest_payload(snapshot, source_entries))
    write_json(plan.artifact_root / "curriculum_snapshot_manifest.json", snapshot_manifest_payload(snapshot, source_entries))

    validation_errors: list[str] = []
    if validate:
        validation_errors = validate_snapshot_artifacts(plan.artifact_root)

    downloaded_count = sum(1 for entry in source_entries if entry.status in {CurriculumSnapshotSource.Status.DOWNLOADED, CurriculumSnapshotSource.Status.CAPTURED})
    failed_count = sum(1 for entry in source_entries if entry.status == CurriculumSnapshotSource.Status.FAILED)

    snapshot.downloaded_count = downloaded_count
    snapshot.failed_count = failed_count
    snapshot.fetch_manifest_path = relative_path(plan.artifact_root / "fetch_manifest.json")
    snapshot.checksum_manifest_path = relative_path(plan.artifact_root / "checksums.sha256")
    snapshot.snapshot_manifest_path = relative_path(plan.artifact_root / "curriculum_snapshot_manifest.json")
    snapshot.validation_status = CurriculumSnapshot.ValidationStatus.VALID if validate and not validation_errors else (
        CurriculumSnapshot.ValidationStatus.INVALID if validate else CurriculumSnapshot.ValidationStatus.NOT_RUN
    )
    snapshot.validation_errors = validation_errors
    snapshot.warnings = warnings
    snapshot.completed_at = timezone.now()
    if validation_errors or (failed_count and failed_count == len(source_entries)):
        snapshot.status = CurriculumSnapshot.Status.FAILED
    elif warnings or failed_count:
        snapshot.status = CurriculumSnapshot.Status.COMPLETED_WITH_WARNINGS
    else:
        snapshot.status = CurriculumSnapshot.Status.COMPLETED
    snapshot.save()
    return snapshot


def capture_source(
    *,
    source: CurriculumSource,
    entry: CurriculumSnapshotSource,
    downloaded_dir: Path,
    checksum_lines: list[str],
    use_local_cache: bool,
    fetcher: Fetcher,
) -> None:
    filename = safe_filename(source.expected_filename)
    destination = downloaded_dir / filename
    content_type = "application/octet-stream"
    if use_local_cache:
        cached = find_cached_source(filename)
        if cached:
            shutil.copyfile(cached, destination)
            entry.status = CurriculumSnapshotSource.Status.CAPTURED
        else:
            raise FileNotFoundError(f"No local cache found for {filename}")
    else:
        payload, content_type = fetcher(source)
        destination.write_bytes(payload)
        entry.status = CurriculumSnapshotSource.Status.DOWNLOADED

    digest = sha256_file(destination)
    entry.stored_filename = filename
    entry.stored_path = relative_path(destination)
    entry.content_type = content_type
    entry.size_bytes = destination.stat().st_size
    entry.sha256 = digest
    entry.retrieved_at = timezone.now()
    checksum_lines.append(f"{digest}  downloaded_sources/{filename}\n")


def fetch_source(source: CurriculumSource) -> FetchResult:
    request = urllib.request.Request(source.official_url, headers={"User-Agent": "stemgen-platform-curriculum-snapshot/0.1"})
    with urllib.request.urlopen(request, timeout=DEFAULT_TIMEOUT_SECONDS) as response:  # noqa: S310 - explicit operator snapshot fetch.
        return response.read(), response.headers.get_content_type()


def source_registry_payload(sources: tuple[CurriculumSource, ...] | list[CurriculumSource], snapshot_id: str = "<snapshot_id>") -> dict:
    return {
        "registry_version": "0.1.0",
        "created_at": iso_now(),
        "sources": [
            {
                "source_id": str(source.source_id),
                "title": source.title,
                "description": source.description,
                "official_url": source.official_url,
                "publisher": source.publisher,
                "year": 2024,
                "subject": source.subject,
                "coverage": source.coverage,
                "subject_coverage": source.coverage,
                "standards_covered": source.standards_covered,
                "source_tier": source.source_tier,
                "expected_filename": source.expected_filename,
                "expected_local_snapshot_path": f"artifacts/curriculum-snapshots/{snapshot_id}/downloaded_sources/{source.expected_filename}",
                "checksum_algorithm": source.checksum_algorithm,
                "checksum_required": True,
                "licensing_caution": "Use for research evidence with copyright caution; do not redistribute source PDFs unless permitted.",
                "may_override_tier_1": False,
            }
            for source in sources
        ],
    }


def fetch_manifest_payload(snapshot: CurriculumSnapshot, entries: list[CurriculumSnapshotSource]) -> dict:
    return {
        "fetch_run_id": f"fetch-{snapshot.snapshot_id}",
        "snapshot_id": str(snapshot.snapshot_id),
        "created_at": iso_now(),
        "sources": [
            {
                "source_id": str(entry.source.source_id),
                "official_url": entry.original_url,
                "local_path": f"downloaded_sources/{entry.stored_filename}" if entry.stored_filename else "",
                "status": manifest_fetch_status(entry.status),
                "sha256": entry.sha256 or None,
                "failure_reason": entry.error_message or None,
            }
            for entry in entries
        ],
    }


def snapshot_manifest_payload(snapshot: CurriculumSnapshot, entries: list[CurriculumSnapshotSource]) -> dict:
    downloaded = [
        {
            "source_id": str(entry.source.source_id),
            "local_path": f"downloaded_sources/{entry.stored_filename}",
            "sha256": entry.sha256,
            "included_in_git": False,
            "copyright_note": "Captured source file is local research evidence and is not intended for public redistribution.",
        }
        for entry in entries
        if entry.sha256
    ]
    return {
        "snapshot_id": str(snapshot.snapshot_id),
        "created_at": iso_now(),
        "source_registry_path": "source_registry.json",
        "fetch_manifest_path": "fetch_manifest.json",
        "downloaded_sources": downloaded,
        "checksum_manifest_path": "checksums.sha256",
        "notes": "Slice 1 source snapshot evidence. No curriculum extraction or topic screening is included.",
    }


def validate_snapshot_artifacts(root: Path) -> list[str]:
    checks = {
        root / "source_registry.json": settings.BASE_DIR / "schemas/curriculum/source_registry.schema.json",
        root / "fetch_manifest.json": settings.BASE_DIR / "schemas/curriculum/fetch_manifest.schema.json",
        root / "curriculum_snapshot_manifest.json": settings.BASE_DIR / "schemas/curriculum/curriculum_snapshot_manifest.schema.json",
    }
    errors: list[str] = []
    for artifact_path, schema_path in checks.items():
        try:
            schema = read_json(schema_path)
            Draft202012Validator.check_schema(schema)
            Draft202012Validator(schema).validate(read_json(artifact_path))
        except (OSError, json.JSONDecodeError, JsonSchemaValidationError) as exc:
            errors.append(f"{artifact_path.name}: {exc}")
    return errors


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def manifest_fetch_status(status: str) -> str:
    if status in {CurriculumSnapshotSource.Status.DOWNLOADED, CurriculumSnapshotSource.Status.CAPTURED}:
        return "fetched"
    if status == CurriculumSnapshotSource.Status.SKIPPED:
        return "skipped"
    if status == CurriculumSnapshotSource.Status.FAILED:
        return "failed"
    return "planned"


def find_cached_source(filename: str) -> Path | None:
    root = artifact_root_base()
    if not root.exists():
        return None
    matches = sorted(root.glob(f"*/downloaded_sources/{filename}"), reverse=True)
    return matches[0] if matches else None


def default_snapshot_id() -> uuid.UUID:
    return generate_unique_snapshot_id()


def generate_unique_snapshot_id(now=None) -> uuid.UUID:
    return uuid.uuid4()


def generate_curriculum_source_id(*, document_type: str, subject: str, standards_covered: list[str], year: int) -> uuid.UUID:
    seed = "|".join([document_type, subject, ",".join(standards_covered), str(year)])
    return uuid.uuid5(uuid.NAMESPACE_URL, seed)


def generate_unique_curriculum_source_id(*, document_type: str, subject: str, standards_covered: list[str], year: int, official_url: str) -> uuid.UUID:
    return uuid.uuid4()


def normalize_uuid(value: str | uuid.UUID) -> uuid.UUID:
    if isinstance(value, uuid.UUID):
        return value
    try:
        return uuid.UUID(str(value))
    except ValueError as exc:
        raise ValidationError("Expected a UUID value.") from exc


def artifact_root(snapshot_id: str | uuid.UUID) -> Path:
    return artifact_root_base() / safe_snapshot_id(snapshot_id)


def artifact_root_base() -> Path:
    return Path(getattr(settings, "CURRICULUM_ARTIFACT_ROOT", settings.BASE_DIR / "artifacts/curriculum-snapshots"))


def safe_snapshot_id(snapshot_id: str | uuid.UUID) -> str:
    return str(normalize_uuid(snapshot_id))


def safe_filename(filename: str) -> str:
    name = Path(filename).name
    safe = "".join(char if char.isalnum() or char in {"-", "_", "."} else "-" for char in name)
    if not safe:
        raise ValidationError("Filename cannot be empty.")
    return safe


def relative_path(path: Path) -> str:
    try:
        return str(path.relative_to(settings.BASE_DIR))
    except ValueError:
        return str(path)


def iso_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
