import uuid

from django.conf import settings
from django.db import models


class CurriculumSource(models.Model):
    class SourceTier(models.TextChoices):
        TIER_1 = "tier_1", "Tier 1: Official curriculum facts"
        TIER_2 = "tier_2", "Tier 2: Official supporting material"
        TIER_3 = "tier_3", "Tier 3: Context and constraints"
        TIER_4 = "tier_4", "Tier 4: Research comparators"

    source_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    official_url = models.URLField(max_length=600)
    publisher = models.CharField(max_length=255, default="Tanzania Institute of Education")
    source_tier = models.CharField(max_length=20, choices=SourceTier.choices, default=SourceTier.TIER_1)
    subject = models.CharField(max_length=120)
    coverage = models.TextField()
    standards_covered = models.JSONField(default=list)
    expected_filename = models.CharField(max_length=180)
    checksum_algorithm = models.CharField(max_length=20, default="sha256")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]

    def __str__(self) -> str:
        return self.title


class CurriculumSnapshot(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        RUNNING = "running", "Running"
        COMPLETED = "completed", "Completed"
        COMPLETED_WITH_WARNINGS = "completed_with_warnings", "Completed with warnings"
        FAILED = "failed", "Failed"

    class ValidationStatus(models.TextChoices):
        NOT_RUN = "not_run", "Not run"
        VALID = "valid", "Valid"
        INVALID = "invalid", "Invalid"

    snapshot_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=40, choices=Status.choices, default=Status.DRAFT)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="curriculum_snapshots",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    source_count = models.PositiveIntegerField(default=0)
    downloaded_count = models.PositiveIntegerField(default=0)
    failed_count = models.PositiveIntegerField(default=0)
    artifact_root = models.CharField(max_length=500, blank=True)
    fetch_manifest_path = models.CharField(max_length=500, blank=True)
    checksum_manifest_path = models.CharField(max_length=500, blank=True)
    snapshot_manifest_path = models.CharField(max_length=500, blank=True)
    validation_status = models.CharField(
        max_length=20,
        choices=ValidationStatus.choices,
        default=ValidationStatus.NOT_RUN,
    )
    validation_errors = models.JSONField(default=list, blank=True)
    warnings = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self) -> str:
        return str(self.snapshot_id)


class CurriculumSnapshotSource(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        DOWNLOADED = "downloaded", "Downloaded"
        CAPTURED = "captured", "Captured"
        FAILED = "failed", "Failed"
        SKIPPED = "skipped", "Skipped"

    snapshot = models.ForeignKey(
        CurriculumSnapshot,
        on_delete=models.CASCADE,
        related_name="captured_sources",
    )
    source = models.ForeignKey(
        CurriculumSource,
        on_delete=models.PROTECT,
        related_name="snapshot_entries",
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    original_url = models.URLField(max_length=600)
    stored_filename = models.CharField(max_length=180, blank=True)
    stored_path = models.CharField(max_length=500, blank=True)
    content_type = models.CharField(max_length=120, blank=True)
    size_bytes = models.PositiveBigIntegerField(default=0)
    sha256 = models.CharField(max_length=64, blank=True)
    retrieved_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ["source__title"]
        constraints = [
            models.UniqueConstraint(
                fields=["snapshot", "source"],
                name="unique_curriculum_snapshot_source",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.snapshot.snapshot_id}: {self.source.source_id}"
