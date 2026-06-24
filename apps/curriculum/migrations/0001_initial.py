# Generated for Slice 1 curriculum source snapshot evidence.

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="CurriculumSource",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("source_id", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ("title", models.CharField(max_length=255)),
                ("official_url", models.URLField(max_length=600)),
                ("publisher", models.CharField(default="Tanzania Institute of Education", max_length=255)),
                (
                    "source_tier",
                    models.CharField(
                        choices=[
                            ("tier_1", "Tier 1: Official curriculum facts"),
                            ("tier_2", "Tier 2: Official supporting material"),
                            ("tier_3", "Tier 3: Context and constraints"),
                            ("tier_4", "Tier 4: Research comparators"),
                        ],
                        default="tier_1",
                        max_length=20,
                    ),
                ),
                ("subject", models.CharField(max_length=120)),
                ("coverage", models.TextField()),
                ("standards_covered", models.JSONField(default=list)),
                ("expected_filename", models.CharField(max_length=180)),
                ("checksum_algorithm", models.CharField(default="sha256", max_length=20)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["title"]},
        ),
        migrations.CreateModel(
            name="CurriculumSnapshot",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("snapshot_id", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Draft"),
                            ("running", "Running"),
                            ("completed", "Completed"),
                            ("completed_with_warnings", "Completed with warnings"),
                            ("failed", "Failed"),
                        ],
                        default="draft",
                        max_length=40,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("source_count", models.PositiveIntegerField(default=0)),
                ("downloaded_count", models.PositiveIntegerField(default=0)),
                ("failed_count", models.PositiveIntegerField(default=0)),
                ("artifact_root", models.CharField(blank=True, max_length=500)),
                ("fetch_manifest_path", models.CharField(blank=True, max_length=500)),
                ("checksum_manifest_path", models.CharField(blank=True, max_length=500)),
                ("snapshot_manifest_path", models.CharField(blank=True, max_length=500)),
                (
                    "validation_status",
                    models.CharField(
                        choices=[("not_run", "Not run"), ("valid", "Valid"), ("invalid", "Invalid")],
                        default="not_run",
                        max_length=20,
                    ),
                ),
                ("validation_errors", models.JSONField(blank=True, default=list)),
                ("warnings", models.JSONField(blank=True, default=list)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="curriculum_snapshots",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"ordering": ["-created_at", "-id"]},
        ),
        migrations.CreateModel(
            name="CurriculumSnapshotSource",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("downloaded", "Downloaded"),
                            ("captured", "Captured"),
                            ("failed", "Failed"),
                            ("skipped", "Skipped"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("original_url", models.URLField(max_length=600)),
                ("stored_filename", models.CharField(blank=True, max_length=180)),
                ("stored_path", models.CharField(blank=True, max_length=500)),
                ("content_type", models.CharField(blank=True, max_length=120)),
                ("size_bytes", models.PositiveBigIntegerField(default=0)),
                ("sha256", models.CharField(blank=True, max_length=64)),
                ("retrieved_at", models.DateTimeField(blank=True, null=True)),
                ("error_message", models.TextField(blank=True)),
                (
                    "snapshot",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="captured_sources",
                        to="curriculum.curriculumsnapshot",
                    ),
                ),
                (
                    "source",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="snapshot_entries",
                        to="curriculum.curriculumsource",
                    ),
                ),
            ],
            options={
                "ordering": ["source__title"],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("snapshot", "source"),
                        name="unique_curriculum_snapshot_source",
                    )
                ],
            },
        ),
    ]
