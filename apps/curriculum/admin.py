from django.contrib import admin

from apps.curriculum.models import CurriculumSnapshot
from apps.curriculum.models import CurriculumSnapshotSource
from apps.curriculum.models import CurriculumSource


class CurriculumSnapshotSourceInline(admin.TabularInline):
    model = CurriculumSnapshotSource
    extra = 0
    readonly_fields = (
        "source",
        "status",
        "stored_filename",
        "stored_path",
        "content_type",
        "size_bytes",
        "sha256",
        "retrieved_at",
        "error_message",
    )
    can_delete = False


@admin.register(CurriculumSource)
class CurriculumSourceAdmin(admin.ModelAdmin):
    list_display = ("source_id", "title", "subject", "source_tier", "is_active")
    search_fields = ("source_id", "title", "official_url")
    list_filter = ("source_tier", "is_active", "subject")


@admin.register(CurriculumSnapshot)
class CurriculumSnapshotAdmin(admin.ModelAdmin):
    list_display = ("snapshot_id", "status", "validation_status", "source_count", "downloaded_count", "failed_count", "created_at")
    search_fields = ("snapshot_id",)
    list_filter = ("status", "validation_status")
    inlines = [CurriculumSnapshotSourceInline]


@admin.register(CurriculumSnapshotSource)
class CurriculumSnapshotSourceAdmin(admin.ModelAdmin):
    list_display = ("snapshot", "source", "status", "stored_filename", "size_bytes")
    search_fields = ("snapshot__snapshot_id", "source__source_id", "source__title")
    list_filter = ("status",)
