import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from apps.curriculum.services import create_snapshot
from apps.curriculum.services import artifact_root
from apps.curriculum.services import default_snapshot_id
from apps.curriculum.services import load_source_registry


class Command(BaseCommand):
    help = "Create reproducible TIE curriculum source snapshots."

    def add_arguments(self, parser):
        parser.add_argument("action", choices=["create"])
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--snapshot-id")
        parser.add_argument("--source-registry")
        parser.add_argument("--description", default="")
        parser.add_argument("--no-download", action="store_true")
        parser.add_argument("--use-local-cache", action="store_true")
        parser.add_argument("--validate", action="store_true")
        parser.add_argument("--json", action="store_true", dest="json_output")

    def handle(self, *args, **options):
        source_registry = Path(options["source_registry"]) if options.get("source_registry") else None
        if options["dry_run"]:
            snapshot_id = options.get("snapshot_id") or default_snapshot_id()
            planned_artifact_root = artifact_root(snapshot_id)
            sources = load_source_registry(source_registry)
            payload = {
                "dry_run": True,
                "snapshot_id": str(snapshot_id),
                "artifact_root": str(planned_artifact_root),
                "sources": [
                    {
                        "source_id": source["source_id"],
                        "title": source["title"],
                        "official_url": source["official_url"],
                        "expected_filename": source["expected_filename"],
                    }
                    for source in sources
                ],
                "artifact_paths": [
                    str(planned_artifact_root / "source_registry.json"),
                    str(planned_artifact_root / "fetch_manifest.json"),
                    str(planned_artifact_root / "checksums.sha256"),
                    str(planned_artifact_root / "curriculum_snapshot_manifest.json"),
                ],
            }
            self.write_payload(payload, options["json_output"])
            return

        try:
            snapshot = create_snapshot(
                snapshot_id=options.get("snapshot_id"),
                source_registry_path=source_registry,
                description=options["description"],
                no_download=options["no_download"],
                use_local_cache=options["use_local_cache"],
                validate=options["validate"],
            )
        except Exception as exc:  # noqa: BLE001 - management command should surface failures clearly.
            raise CommandError(str(exc)) from exc

        payload = {
            "snapshot_id": str(snapshot.snapshot_id),
            "status": snapshot.status,
            "validation_status": snapshot.validation_status,
            "source_count": snapshot.source_count,
            "downloaded_count": snapshot.downloaded_count,
            "failed_count": snapshot.failed_count,
            "artifact_root": snapshot.artifact_root,
            "warnings": snapshot.warnings,
            "validation_errors": snapshot.validation_errors,
        }
        self.write_payload(payload, options["json_output"])

    def write_payload(self, payload: dict, json_output: bool) -> None:
        if json_output:
            self.stdout.write(json.dumps(payload, indent=2, sort_keys=True))
            return
        for key, value in payload.items():
            self.stdout.write(f"{key}: {value}")
