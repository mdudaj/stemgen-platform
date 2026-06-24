import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from apps.curriculum.services import create_curriculum_extraction


class Command(BaseCommand):
    help = "Create deterministic curriculum item and candidate topic datasets from a source snapshot."

    def add_arguments(self, parser):
        parser.add_argument("action", choices=["create"])
        parser.add_argument("--snapshot-id", required=True)
        parser.add_argument("--item-fixture")
        parser.add_argument("--validate", action="store_true")
        parser.add_argument("--json", action="store_true", dest="json_output")

    def handle(self, *args, **options):
        item_fixture = Path(options["item_fixture"]) if options.get("item_fixture") else None
        try:
            result = create_curriculum_extraction(
                source_snapshot_id=options["snapshot_id"],
                item_fixture_path=item_fixture,
                validate=options["validate"],
            )
        except Exception as exc:  # noqa: BLE001 - management command should surface failures clearly.
            raise CommandError(str(exc)) from exc

        payload = {
            "dataset_id": result.dataset_id,
            "source_snapshot_id": str(result.source_snapshot_id),
            "artifact_root": str(result.artifact_root),
            "item_count": result.item_count,
            "candidate_topic_count": result.candidate_topic_count,
            "curriculum_items_path": str(result.curriculum_items_path),
            "candidate_topics_path": str(result.candidate_topics_path),
            "validation_errors": result.validation_errors,
        }
        if options["json_output"]:
            self.stdout.write(json.dumps(payload, indent=2, sort_keys=True))
            return
        for key, value in payload.items():
            self.stdout.write(f"{key}: {value}")
