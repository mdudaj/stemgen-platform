import json
import tempfile
import uuid
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import Client
from django.test import TestCase
from django.test import override_settings
from django.urls import reverse
from jsonschema import Draft202012Validator

from apps.curriculum.models import CurriculumSnapshot
from apps.curriculum.models import CurriculumSnapshotSource
from apps.curriculum.models import CurriculumSource
from apps.curriculum.services import create_snapshot
from apps.curriculum.services import generate_curriculum_source_id
from apps.curriculum.services import generate_unique_curriculum_source_id
from apps.curriculum.services import generate_unique_snapshot_id
from apps.curriculum.services import load_source_registry
from apps.curriculum.services import seed_curriculum_sources
from apps.curriculum.services import source_registry_payload
from apps.curriculum.services import validate_snapshot_artifacts


class CurriculumDesignSystemTests(TestCase):
    def test_metric_list_auto_fills_tab_surface_columns(self):
        css_path = Path(__file__).resolve().parents[2] / "static/dissertation/ui/components.css"
        css = css_path.read_text(encoding="utf-8")

        self.assertIn("grid-template-columns: repeat(auto-fit, minmax(min(100%, 180px), 1fr));", css)
        self.assertNotIn("grid-template-columns: repeat(4, minmax(0, 1fr));", css)


class CurriculumModelTests(TestCase):
    def test_curriculum_source_model_defaults(self):
        source = CurriculumSource.objects.create(
            title="Test Source",
            official_url="https://www.tie.go.tz/test.pdf",
            subject="Science",
            coverage="Test coverage",
            standards_covered=["III"],
            expected_filename="test.pdf",
        )

        self.assertEqual(source.publisher, "Tanzania Institute of Education")
        self.assertEqual(source.source_tier, CurriculumSource.SourceTier.TIER_1)
        self.assertEqual(source.checksum_algorithm, "sha256")

    def test_curriculum_snapshot_model_defaults(self):
        snapshot = CurriculumSnapshot.objects.create()

        self.assertEqual(snapshot.status, CurriculumSnapshot.Status.DRAFT)
        self.assertEqual(snapshot.validation_status, CurriculumSnapshot.ValidationStatus.NOT_RUN)
        self.assertEqual(snapshot.warnings, [])

    def test_curriculum_snapshot_source_model(self):
        source = CurriculumSource.objects.create(
            title="Test Source",
            official_url="https://www.tie.go.tz/test.pdf",
            subject="Science",
            coverage="Test coverage",
            standards_covered=["III"],
            expected_filename="test.pdf",
        )
        snapshot = CurriculumSnapshot.objects.create()
        entry = CurriculumSnapshotSource.objects.create(
            snapshot=snapshot,
            source=source,
            original_url=source.official_url,
        )

        self.assertEqual(entry.status, CurriculumSnapshotSource.Status.PENDING)
        self.assertEqual(str(entry), f"{snapshot.snapshot_id}: {source.source_id}")


class CurriculumSnapshotServiceTests(TestCase):
    def test_source_registry_fixture_loads(self):
        registry = load_source_registry()

        self.assertEqual(len(registry), 4)
        self.assertEqual(registry[0]["source_id"], "2699cece-a5fd-5eb6-9a84-4ff89f5e04cd")

    def test_source_registry_fixture_seeds_sources(self):
        sources = seed_curriculum_sources()

        self.assertEqual(len(sources), 4)
        self.assertEqual(CurriculumSource.objects.count(), 4)
        self.assertTrue(CurriculumSource.objects.filter(source_tier=CurriculumSource.SourceTier.TIER_1).exists())

    def test_source_registry_payload_validates_against_schema(self):
        sources = seed_curriculum_sources()
        payload = source_registry_payload(sources)
        schema = self.load_schema("source_registry.schema.json")

        Draft202012Validator(schema).validate(payload)
        self.assertEqual(payload["sources"][0]["description"], sources[0].description)

    def test_dry_run_command_does_not_write_artifacts_or_database(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with override_settings(CURRICULUM_ARTIFACT_ROOT=Path(temp_dir)):
                output = StringIO()
                snapshot_id = uuid.uuid4()
                call_command(
                    "curriculum_snapshot",
                    "create",
                    "--dry-run",
                    "--snapshot-id",
                    str(snapshot_id),
                    "--json",
                    stdout=output,
                )

                payload = json.loads(output.getvalue())
                self.assertTrue(payload["dry_run"])
                self.assertEqual(payload["snapshot_id"], str(snapshot_id))
                self.assertFalse((Path(temp_dir) / str(snapshot_id)).exists())
                self.assertEqual(CurriculumSnapshot.objects.count(), 0)
                self.assertEqual(CurriculumSource.objects.count(), 0)

    def test_no_download_snapshot_writes_valid_manifests(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with override_settings(CURRICULUM_ARTIFACT_ROOT=Path(temp_dir)):
                snapshot_id = uuid.uuid4()
                snapshot = create_snapshot(
                    snapshot_id=snapshot_id,
                    no_download=True,
                    validate=True,
                )

                root = Path(temp_dir) / str(snapshot_id)
                self.assertEqual(snapshot.status, CurriculumSnapshot.Status.COMPLETED)
                self.assertEqual(snapshot.validation_status, CurriculumSnapshot.ValidationStatus.VALID)
                self.assertEqual(snapshot.downloaded_count, 0)
                self.assertEqual(snapshot.failed_count, 0)
                self.assertTrue((root / "source_registry.json").exists())
                self.assertTrue((root / "fetch_manifest.json").exists())
                self.assertTrue((root / "checksums.sha256").exists())
                self.assertTrue((root / "curriculum_snapshot_manifest.json").exists())
                self.assertEqual((root / "checksums.sha256").read_text(encoding="utf-8"), "")
                self.assertEqual(validate_snapshot_artifacts(root), [])
                self.assertEqual(snapshot.captured_sources.filter(status=CurriculumSnapshotSource.Status.SKIPPED).count(), 4)

    def test_download_snapshot_generates_checksum_manifest(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with override_settings(CURRICULUM_ARTIFACT_ROOT=Path(temp_dir)):
                snapshot_id = uuid.uuid4()
                snapshot = create_snapshot(
                    snapshot_id=snapshot_id,
                    validate=True,
                    fetcher=lambda _source: (b"example pdf bytes", "application/pdf"),
                )

                root = Path(temp_dir) / str(snapshot_id)
                checksums = (root / "checksums.sha256").read_text(encoding="utf-8")
                self.assertEqual(snapshot.status, CurriculumSnapshot.Status.COMPLETED)
                self.assertEqual(snapshot.downloaded_count, 4)
                self.assertIn("downloaded_sources/tie-primary-curriculum-2024.pdf", checksums)
                first = snapshot.captured_sources.order_by("source__source_id").first()
                self.assertEqual(len(first.sha256), 64)
                self.assertEqual(first.content_type, "application/pdf")

    def test_failed_download_is_recorded(self):
        def failing_fetcher(_source):
            raise TimeoutError("network unavailable")

        with tempfile.TemporaryDirectory() as temp_dir:
            with override_settings(CURRICULUM_ARTIFACT_ROOT=Path(temp_dir)):
                snapshot_id = uuid.uuid4()
                snapshot = create_snapshot(
                    snapshot_id=snapshot_id,
                    validate=True,
                    fetcher=failing_fetcher,
                )

                self.assertEqual(snapshot.status, CurriculumSnapshot.Status.FAILED)
                self.assertEqual(snapshot.failed_count, 4)
                self.assertEqual(snapshot.validation_status, CurriculumSnapshot.ValidationStatus.VALID)
                entry = snapshot.captured_sources.first()
                self.assertEqual(entry.status, CurriculumSnapshotSource.Status.FAILED)
                self.assertIn("network unavailable", entry.error_message)
                manifest = json.loads((Path(temp_dir) / str(snapshot_id) / "fetch_manifest.json").read_text(encoding="utf-8"))
                self.assertEqual(manifest["sources"][0]["status"], "failed")

    def load_schema(self, name):
        schema_path = Path(__file__).resolve().parents[2] / "schemas/curriculum" / name
        with schema_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)


class CurriculumDashboardTests(TestCase):
    def setUp(self):
        self.staff = get_user_model().objects.create_user(
            email="operator@example.com",
            password="strong-password-123",
            is_staff=True,
        )
        self.regular = get_user_model().objects.create_user(
            email="teacher@example.com",
            password="strong-password-123",
        )

    def test_dashboard_summary_includes_latest_snapshot(self):
        seed_curriculum_sources()
        CurriculumSnapshot.objects.create(
            description="Dashboard source evidence",
            status=CurriculumSnapshot.Status.COMPLETED,
            validation_status=CurriculumSnapshot.ValidationStatus.VALID,
            source_count=4,
            downloaded_count=2,
            failed_count=0,
        )
        client = Client()
        client.force_login(self.staff)

        response = client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Curriculum Sources")
        self.assertContains(response, "Dashboard source evidence")
        self.assertContains(response, "kisomo-page kisomo-page-stack")
        self.assertContains(response, 'aria-labelledby="dashboard-curriculum-title"')
        self.assertContains(response, "kisomo-metric-list")
        self.assertContains(response, "Latest Snapshot")
        self.assertContains(response, "Downloaded")
        self.assertContains(response, "2 / 4")
        self.assertContains(response, "Open Curriculum")
        self.assertContains(response, "kisomo-card-actions")
        self.assertContains(response, "mdc-button__icon")
        self.assertContains(response, reverse("curriculum-home"))

    def test_snapshot_list_page_requires_authentication(self):
        response = Client().get(reverse("curriculum-snapshot-list"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response["Location"])

    def test_snapshot_detail_page_requires_authentication(self):
        snapshot = CurriculumSnapshot.objects.create()

        response = Client().get(reverse("curriculum-snapshot-detail", kwargs={"snapshot_id": snapshot.snapshot_id}))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response["Location"])

    def test_non_staff_user_cannot_access_snapshot_pages(self):
        client = Client()
        client.force_login(self.regular)

        response = client.get(reverse("curriculum-snapshot-list"))

        self.assertEqual(response.status_code, 403)

    def test_staff_can_access_snapshot_list_and_detail(self):
        source = seed_curriculum_sources()[0]
        snapshot = CurriculumSnapshot.objects.create(
            description="Detail source evidence",
            status=CurriculumSnapshot.Status.COMPLETED,
            validation_status=CurriculumSnapshot.ValidationStatus.VALID,
            artifact_root="artifacts/curriculum-snapshots/detail-test",
            fetch_manifest_path="artifacts/curriculum-snapshots/detail-test/fetch_manifest.json",
            checksum_manifest_path="artifacts/curriculum-snapshots/detail-test/checksums.sha256",
            snapshot_manifest_path="artifacts/curriculum-snapshots/detail-test/curriculum_snapshot_manifest.json",
            source_count=1,
            downloaded_count=1,
        )
        CurriculumSnapshotSource.objects.create(
            snapshot=snapshot,
            source=source,
            status=CurriculumSnapshotSource.Status.DOWNLOADED,
            original_url=source.official_url,
            stored_filename=source.expected_filename,
            stored_path=f"artifacts/curriculum-snapshots/detail-test/downloaded_sources/{source.expected_filename}",
            size_bytes=123,
            sha256="a" * 64,
        )
        client = Client()
        client.force_login(self.staff)

        list_response = client.get(reverse("curriculum-snapshot-list"))
        detail_response = client.get(reverse("curriculum-snapshot-detail", kwargs={"snapshot_id": snapshot.snapshot_id}))

        self.assertEqual(list_response.status_code, 200)
        self.assertContains(list_response, "Detail source evidence")
        self.assertContains(list_response, "Back to Curriculum")
        self.assertContains(list_response, reverse("curriculum-home"))
        self.assertContains(list_response, "kisomo-page-stack")
        self.assertContains(list_response, "kisomo-object-header__actions")
        self.assertEqual(detail_response.status_code, 200)
        self.assertContains(detail_response, "Back to Snapshots")
        self.assertContains(detail_response, reverse("curriculum-snapshot-list"))
        self.assertContains(detail_response, "kisomo-page-stack")
        self.assertContains(detail_response, "kisomo-object-header__actions")
        self.assertContains(detail_response, "Review captured artifacts")
        self.assertContains(detail_response, "checksums.sha256")
        self.assertContains(detail_response, "a" * 64)
        self.assertContains(detail_response, source.official_url)

    def test_snapshot_detail_uses_read_only_language(self):
        snapshot = CurriculumSnapshot.objects.create()
        client = Client()
        client.force_login(self.staff)

        response = client.get(reverse("curriculum-snapshot-detail", kwargs={"snapshot_id": snapshot.snapshot_id}))

        self.assertContains(response, "Read-only source snapshot evidence")
        self.assertContains(response, "Ready for extraction")
        self.assertNotContains(response, "Approve")
        self.assertNotContains(response, "Accept topic")


class CurriculumIntakeTests(TestCase):
    def setUp(self):
        self.staff = get_user_model().objects.create_user(
            email="intake-operator@example.com",
            password="strong-password-123",
            is_staff=True,
        )
        self.regular = get_user_model().objects.create_user(
            email="intake-teacher@example.com",
            password="strong-password-123",
        )

    def test_source_registry_fixture_uses_standard_iii_vi_for_mathematics(self):
        registry = load_source_registry()
        mathematics = next(item for item in registry if item["title"] == "Mathematics Syllabus Primary Education")

        self.assertEqual(mathematics["coverage"], "Mathematics syllabus for primary education Standard III-VI")
        self.assertEqual(mathematics["standards_covered"], ["III", "IV", "V", "VI"])

    def test_dashboard_links_to_curriculum_landing(self):
        client = Client()
        client.force_login(self.staff)

        response = client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Open Curriculum")
        self.assertContains(response, reverse("curriculum-home"))

    def test_curriculum_home_requires_authentication(self):
        response = Client().get(reverse("curriculum-home"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response["Location"])

    def test_non_staff_user_cannot_access_curriculum_home(self):
        client = Client()
        client.force_login(self.regular)

        response = client.get(reverse("curriculum-home"))

        self.assertEqual(response.status_code, 403)

    def test_staff_can_open_curriculum_home_with_action_cards(self):
        client = Client()
        client.force_login(self.staff)

        response = client.get(reverse("curriculum-home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "dissertation/ui/components.css")
        self.assertContains(response, "?v=20260621-1")
        self.assertContains(response, "kisomo-page-stack")
        self.assertContains(response, "kisomo-card-grid")
        self.assertContains(response, "kisomo-action-card__body", count=3)
        self.assertContains(response, "kisomo-action-card__actions", count=3)
        self.assertContains(response, "mdc-button__icon", count=3)
        self.assertContains(response, "Manage Sources")
        self.assertContains(response, reverse("curriculum-source-list"))
        self.assertContains(response, "Capture Snapshot")
        self.assertContains(response, reverse("curriculum-snapshot-capture"))
        self.assertContains(response, "Review Snapshots")
        self.assertContains(response, reverse("curriculum-snapshot-list"))
        self.assertContains(response, "mdc-card kisomo-tab-surface")
        self.assertContains(response, "mdc-tab-bar kisomo-material-tabs")
        self.assertContains(response, "mdc-tab-scroller")
        self.assertContains(response, "mdc-tab ", count=2)
        self.assertContains(response, "mdc-tab--active")
        self.assertContains(response, "mdc-tab-indicator--active")
        self.assertContains(response, "mdc-tab-indicator__content--underline")
        self.assertContains(response, 'role="tabpanel"')
        self.assertContains(response, "kisomo-tab-panel__header")
        self.assertContains(response, "kisomo-metric-list")
        self.assertContains(response, "Total Sources")
        self.assertContains(response, "Active Sources")
        self.assertContains(response, "Tier 1 Sources")
        self.assertContains(response, "?tab=sources")
        self.assertContains(response, "?tab=snapshots")
        self.assertNotContains(response, 'name="official_url"')
        self.assertNotContains(response, 'name="no_download"')

    def test_intake_route_redirects_to_curriculum_home(self):
        client = Client()
        client.force_login(self.staff)

        response = client.get(reverse("curriculum-intake"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("curriculum-home"))

    def test_sources_page_requires_authentication(self):
        response = Client().get(reverse("curriculum-source-list"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response["Location"])

    def test_non_staff_user_cannot_access_source_pages(self):
        client = Client()
        client.force_login(self.regular)

        list_response = client.get(reverse("curriculum-source-list"))
        create_response = client.get(reverse("curriculum-source-create"))
        capture_response = client.get(reverse("curriculum-snapshot-capture"))

        self.assertEqual(list_response.status_code, 403)
        self.assertEqual(create_response.status_code, 403)
        self.assertEqual(capture_response.status_code, 403)

    def test_staff_menu_exposes_single_curriculum_entry(self):
        client = Client()
        client.force_login(self.staff)

        response = client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Curriculum")
        self.assertContains(response, reverse("curriculum-home"))
        self.assertNotContains(response, reverse("curriculum-source-list"))
        self.assertNotContains(response, reverse("curriculum-snapshot-list"))

    def test_staff_can_open_source_list(self):
        client = Client()
        client.force_login(self.staff)

        response = client.get(reverse("curriculum-source-list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Curriculum Sources")
        self.assertContains(response, "kisomo-page-stack")
        self.assertContains(response, "kisomo-object-header__actions")
        self.assertContains(response, "kisomo-back-action")
        self.assertContains(response, "Back to Curriculum")
        self.assertContains(response, reverse("curriculum-home"))
        self.assertContains(response, reverse("curriculum-source-create"))
        self.assertContains(response, "Seed TIE Defaults")
        self.assertContains(response, "kisomo-action-card__body", count=2)
        self.assertContains(response, "kisomo-action-card__actions", count=2)
        self.assertContains(response, "mdc-button--raised", count=2)
        self.assertContains(response, "mdc-button__icon", count=3)
        self.assertContains(response, "library_add")
        self.assertContains(response, "playlist_add")

    def test_staff_can_open_add_source_form_without_source_id_input(self):
        client = Client()
        client.force_login(self.staff)

        response = client.get(reverse("curriculum-source-create"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Add Curriculum Source")
        self.assertContains(response, "operator-facing description")
        self.assertContains(response, "UUID identifier is assigned silently")
        self.assertContains(response, "kisomo-page-stack")
        self.assertContains(response, "kisomo-object-header__actions")
        self.assertContains(response, "kisomo-back-action")
        self.assertContains(response, "Back to Sources")
        self.assertContains(response, "mdc-layout-grid")
        self.assertContains(response, "mdc-layout-grid__cell--span-12")
        self.assertContains(response, "mdc-card vf-card kisomo-card")
        self.assertContains(response, "vf-form")
        self.assertContains(response, "vf-card__form")
        self.assertContains(response, "vf-field-input")
        self.assertContains(response, "vf-field-textarea")
        self.assertContains(response, "vf-form-row")
        self.assertContains(response, "mdc-card__actions vf-card__actions")
        self.assertContains(response, "mdc-button")
        self.assertContains(response, "kisomo-form-card")
        self.assertNotContains(response, 'name="source_id"')

    def test_staff_can_seed_default_tie_sources_idempotently(self):
        client = Client()
        client.force_login(self.staff)

        first = client.post(reverse("curriculum-source-list"), {"action": "seed_sources"})
        second = client.post(reverse("curriculum-source-list"), {"action": "seed_sources"})

        self.assertEqual(first.status_code, 302)
        self.assertEqual(second.status_code, 302)
        self.assertEqual(CurriculumSource.objects.count(), 4)
        self.assertEqual(
            CurriculumSource.objects.get(source_id=uuid.UUID("af3128e1-3ac3-5973-8146-c5d87de060b5")).standards_covered,
            ["III", "IV", "V", "VI"],
        )

    def test_source_id_generation_returns_uuid(self):
        source_id = generate_curriculum_source_id(
            document_type="syllabus",
            subject="Science",
            standards_covered=["III", "IV", "V", "VI"],
            year=2024,
        )

        self.assertIsInstance(source_id, uuid.UUID)

    def test_unique_source_id_generation_returns_uuid(self):
        CurriculumSource.objects.create(
            title="Existing Source",
            official_url="https://www.tie.go.tz/uploads/documents/existing.pdf",
            subject="Science",
            coverage="Existing coverage",
            standards_covered=["III", "IV"],
            expected_filename="existing.pdf",
        )

        source_id = generate_unique_curriculum_source_id(
            document_type="syllabus",
            subject="Science",
            standards_covered=["III", "IV"],
            year=2024,
            official_url="https://www.tie.go.tz/uploads/documents/example.pdf",
        )

        self.assertIsInstance(source_id, uuid.UUID)
        self.assertFalse(CurriculumSource.objects.filter(source_id=source_id).exists())

    def test_staff_can_add_official_tie_source_with_generated_id(self):
        client = Client()
        client.force_login(self.staff)

        response = client.post(reverse("curriculum-source-create"), self.source_payload())

        self.assertEqual(response.status_code, 302)
        source = CurriculumSource.objects.get(title="Added Source")
        self.assertEqual(source.official_url, "https://www.tie.go.tz/uploads/documents/example.pdf")
        self.assertEqual(source.standards_covered, ["III", "IV"])
        self.assertTrue(source.is_active)
        self.assertIsInstance(source.source_id, uuid.UUID)

    def test_invalid_source_metadata_is_rejected(self):
        client = Client()
        client.force_login(self.staff)
        payload = self.source_payload(
            official_url="https://example.com/source.pdf",
            expected_filename="../source.pdf",
        )

        response = client.post(reverse("curriculum-source-create"), payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(CurriculumSource.objects.count(), 0)
        self.assertContains(response, "Use an official TIE URL from www.tie.go.tz for Tier 1 intake.")
        self.assertContains(response, "Provide a safe PDF filename without path separators.")

    def test_capture_snapshot_page_has_no_snapshot_id_input(self):
        client = Client()
        client.force_login(self.staff)

        response = client.get(reverse("curriculum-snapshot-capture"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Capture Snapshot")
        self.assertContains(response, "describe why it was captured")
        self.assertContains(response, "kisomo-page-stack")
        self.assertContains(response, "kisomo-object-header__actions")
        self.assertContains(response, "kisomo-back-action")
        self.assertContains(response, "Back to Curriculum")
        self.assertContains(response, "Review Sources")
        self.assertContains(response, "mdc-layout-grid__cell--span-12")
        self.assertContains(response, "mdc-card vf-card kisomo-card")
        self.assertContains(response, "vf-card__form")
        self.assertContains(response, "vf-field-checkbox")
        self.assertContains(response, "vf-form-row")
        self.assertContains(response, "mdc-card__actions vf-card__actions")
        self.assertContains(response, "kisomo-form-card")
        self.assertNotContains(response, "Active Sources")
        self.assertNotContains(response, 'name="snapshot_id"')

    def test_snapshot_id_generation_returns_uuid(self):
        first = generate_unique_snapshot_id()
        CurriculumSnapshot.objects.create(snapshot_id=first)
        second = generate_unique_snapshot_id()

        self.assertIsInstance(first, uuid.UUID)
        self.assertIsInstance(second, uuid.UUID)
        self.assertNotEqual(first, second)

    def test_capture_snapshot_blocks_without_active_sources(self):
        client = Client()
        client.force_login(self.staff)

        response = client.post(
            reverse("curriculum-snapshot-capture"),
            {"validate": "on"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(CurriculumSnapshot.objects.count(), 0)
        self.assertContains(response, "Register at least one active curriculum source before capturing a snapshot.")

    def test_staff_captures_no_download_snapshot_from_active_sources(self):
        seed_curriculum_sources()
        client = Client()
        client.force_login(self.staff)

        with tempfile.TemporaryDirectory() as temp_dir:
            with override_settings(CURRICULUM_ARTIFACT_ROOT=Path(temp_dir)):
                response = client.post(
                    reverse("curriculum-snapshot-capture"),
                    {"description": "Operator capture note", "validate": "on"},
                )

                self.assertEqual(response.status_code, 302)
                snapshot = CurriculumSnapshot.objects.get()
                self.assertIsInstance(snapshot.snapshot_id, uuid.UUID)
                self.assertIn(reverse("curriculum-snapshot-detail", kwargs={"snapshot_id": snapshot.snapshot_id}), response["Location"])
                self.assertEqual(snapshot.created_by, self.staff)
                self.assertEqual(snapshot.description, "Operator capture note")
                self.assertEqual(snapshot.source_count, 4)
                self.assertEqual(snapshot.validation_status, CurriculumSnapshot.ValidationStatus.VALID)
                self.assertEqual(snapshot.captured_sources.count(), 4)
                self.assertEqual(snapshot.captured_sources.filter(status=CurriculumSnapshotSource.Status.SKIPPED).count(), 4)
                registry_path = Path(temp_dir) / str(snapshot.snapshot_id) / "source_registry.json"
                registry = json.loads(registry_path.read_text(encoding="utf-8"))
                self.assertEqual(len(registry["sources"]), 4)
                self.assertIn("description", registry["sources"][0])


    def source_payload(self, **overrides):
        payload = {
            "document_type": "syllabus",
            "year": "2024",
            "title": "Added Source",
            "official_url": "https://www.tie.go.tz/uploads/documents/example.pdf",
            "subject": "Science",
            "coverage": "Added source coverage",
            "standards_covered": "III, IV",
            "expected_filename": "tie-added-source.pdf",
            "source_tier": CurriculumSource.SourceTier.TIER_1,
            "is_active": "on",
        }
        payload.update(overrides)
        return payload
