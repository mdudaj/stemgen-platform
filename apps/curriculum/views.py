import json
import tempfile
from pathlib import Path

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import ValidationError
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import RedirectView
from django.views.generic import TemplateView
from django.views.generic import View

from apps.curriculum.forms import CurriculumSourceForm
from apps.curriculum.forms import SnapshotCaptureForm
from apps.curriculum.models import CurriculumSnapshot
from apps.curriculum.models import CurriculumSource
from apps.curriculum.services import create_curriculum_extraction
from apps.curriculum.services import create_snapshot
from apps.curriculum.services import curriculum_extraction_root
from apps.curriculum.services import generate_unique_snapshot_id
from apps.curriculum.services import read_json
from apps.curriculum.services import seed_curriculum_sources
from apps.curriculum.services import source_registry_payload
from apps.curriculum.services import validate_curriculum_extraction_artifacts


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


class CurriculumContextMixin:
    def curriculum_context(self):
        sources = CurriculumSource.objects.all()
        latest_snapshot = CurriculumSnapshot.objects.order_by("-created_at", "-id").first()
        return {
            "sources": sources,
            "source_count": sources.count(),
            "active_source_count": sources.filter(is_active=True).count(),
            "tier1_source_count": sources.filter(source_tier=CurriculumSource.SourceTier.TIER_1).count(),
            "latest_snapshot": latest_snapshot,
            "latest_warning_count": len(latest_snapshot.warnings) if latest_snapshot else 0,
            "extraction_count": curriculum_extraction_count(),
        }


class CurriculumHomeView(StaffRequiredMixin, CurriculumContextMixin, TemplateView):
    template_name = "curriculum/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.curriculum_context())
        active_tab = self.request.GET.get("tab", "sources")
        context["active_tab"] = active_tab if active_tab in {"sources", "snapshots", "extractions"} else "sources"
        context["curriculum_tabs"] = [
            {
                "key": "sources",
                "label": "Sources",
                "icon": "source",
                "url": f"{reverse('curriculum-home')}?tab=sources",
            },
            {
                "key": "snapshots",
                "label": "Latest Snapshot",
                "icon": "inventory_2",
                "url": f"{reverse('curriculum-home')}?tab=snapshots",
            },
            {
                "key": "extractions",
                "label": "Extractions",
                "icon": "fact_check",
                "url": f"{reverse('curriculum-home')}?tab=extractions",
            },
        ]
        return context


class CurriculumIntakeRedirectView(StaffRequiredMixin, RedirectView):
    pattern_name = "curriculum-home"
    permanent = False


class CurriculumSourceListView(StaffRequiredMixin, CurriculumContextMixin, ListView):
    model = CurriculumSource
    template_name = "curriculum/source_list.html"
    context_object_name = "sources"
    paginate_by = 50

    def get_queryset(self):
        return CurriculumSource.objects.order_by("title")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.curriculum_context())
        return context

    def post(self, request, *args, **kwargs):
        if request.POST.get("action") != "seed_sources":
            messages.error(request, "Unknown source action.")
            return redirect("curriculum-source-list")
        existing_ids = set(CurriculumSource.objects.values_list("source_id", flat=True))
        sources = seed_curriculum_sources()
        created_count = sum(1 for source in sources if source.source_id not in existing_ids)
        updated_count = len(sources) - created_count
        messages.success(request, f"Seeded {created_count} new source(s) and updated {updated_count} existing source(s).")
        return redirect("curriculum-source-list")


class CurriculumSourceCreateView(StaffRequiredMixin, TemplateView):
    template_name = "curriculum/source_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault("form", CurriculumSourceForm())
        return context

    def post(self, request, *args, **kwargs):
        form = CurriculumSourceForm(request.POST)
        if form.is_valid():
            source = form.save()
            messages.success(request, f"Added source {source.title}.")
            return redirect("curriculum-source-list")
        return self.render_to_response(self.get_context_data(form=form))


class CurriculumSnapshotCaptureView(StaffRequiredMixin, TemplateView):
    template_name = "curriculum/snapshot_capture.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault("form", SnapshotCaptureForm(initial={"validate": True, "no_download": True}))
        context["active_source_count"] = CurriculumSource.objects.filter(is_active=True).count()
        return context

    def post(self, request, *args, **kwargs):
        form = SnapshotCaptureForm(request.POST)
        if not CurriculumSource.objects.filter(is_active=True).exists():
            form.add_error(None, "Register at least one active curriculum source before capturing a snapshot.")
            return self.render_to_response(self.get_context_data(form=form))
        if form.is_valid():
            snapshot_id = generate_unique_snapshot_id()
            try:
                snapshot = create_snapshot_from_active_sources(
                    snapshot_id=snapshot_id,
                    description=form.cleaned_data["description"],
                    validate=form.cleaned_data["validate"],
                    no_download=form.cleaned_data["no_download"],
                    use_local_cache=form.cleaned_data["use_local_cache"],
                    created_by=request.user,
                )
            except ValidationError as exc:
                form.add_error(None, exc.message if hasattr(exc, "message") else str(exc))
                return self.render_to_response(self.get_context_data(form=form))
            messages.success(request, "Captured curriculum snapshot.")
            return redirect(reverse("curriculum-snapshot-detail", kwargs={"snapshot_id": snapshot.snapshot_id}))
        return self.render_to_response(self.get_context_data(form=form))


def create_snapshot_from_active_sources(*, snapshot_id, description, validate, no_download, use_local_cache, created_by):
    active_sources = list(CurriculumSource.objects.filter(is_active=True).order_by("title"))
    if not active_sources:
        raise ValidationError("Register at least one active curriculum source before capturing a snapshot.")
    registry = source_registry_payload(active_sources, snapshot_id=snapshot_id or "<snapshot_id>")
    fixture_payload = [source_registry_item_to_fixture(item) for item in registry["sources"]]
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json") as handle:
        json.dump(fixture_payload, handle, indent=2)
        handle.flush()
        return create_snapshot(
            snapshot_id=snapshot_id,
            description=description,
            source_registry_path=Path(handle.name),
            no_download=no_download,
            use_local_cache=use_local_cache,
            validate=validate,
            created_by=created_by,
        )


def source_registry_item_to_fixture(item):
    return {
        "source_id": item["source_id"],
        "title": item["title"],
        "description": item["description"],
        "official_url": item["official_url"],
        "publisher": item["publisher"],
        "source_tier": item["source_tier"],
        "subject": item["subject"],
        "coverage": item["coverage"],
        "standards_covered": item["standards_covered"],
        "expected_filename": item["expected_filename"],
        "checksum_algorithm": item["checksum_algorithm"],
    }


class CurriculumSnapshotListView(StaffRequiredMixin, ListView):
    model = CurriculumSnapshot
    template_name = "curriculum/snapshot_list.html"
    context_object_name = "snapshots"
    paginate_by = 25


class CurriculumSnapshotDetailView(StaffRequiredMixin, DetailView):
    model = CurriculumSnapshot
    template_name = "curriculum/snapshot_detail.html"
    context_object_name = "snapshot"
    slug_field = "snapshot_id"
    slug_url_kwarg = "snapshot_id"

    def get_queryset(self):
        return super().get_queryset().prefetch_related("captured_sources__source")


class CurriculumExtractionListView(StaffRequiredMixin, TemplateView):
    template_name = "curriculum/extraction_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        snapshots = CurriculumSnapshot.objects.order_by("-created_at", "-id").prefetch_related("captured_sources__source")
        context["snapshot_rows"] = [
            {
                "snapshot": snapshot,
                "summary": curriculum_extraction_summary(snapshot),
            }
            for snapshot in snapshots
        ]
        return context


class CurriculumExtractionCreateView(StaffRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        snapshot = get_object_or_404(CurriculumSnapshot, snapshot_id=kwargs["snapshot_id"])
        if curriculum_extraction_root(snapshot.snapshot_id).exists():
            messages.info(request, "Extraction artifacts already exist for this snapshot.")
            return redirect("curriculum-extraction-detail", snapshot_id=snapshot.snapshot_id)
        try:
            result = create_curriculum_extraction(source_snapshot_id=snapshot.snapshot_id, validate=True)
        except ValidationError as exc:
            messages.error(request, exc.message if hasattr(exc, "message") else str(exc))
            return redirect("curriculum-extraction-list")
        except CurriculumSnapshot.DoesNotExist as exc:
            raise Http404("Snapshot not found.") from exc
        if result.validation_errors:
            messages.warning(request, "Extraction completed with validation errors.")
        else:
            messages.success(request, "Extraction artifacts created for web review.")
        return redirect("curriculum-extraction-detail", snapshot_id=snapshot.snapshot_id)


class CurriculumExtractionDetailView(StaffRequiredMixin, TemplateView):
    template_name = "curriculum/extraction_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        snapshot = get_object_or_404(CurriculumSnapshot, snapshot_id=kwargs["snapshot_id"])
        summary = curriculum_extraction_summary(snapshot)
        if not summary["exists"]:
            raise Http404("Extraction artifacts do not exist for this snapshot.")
        context["snapshot"] = snapshot
        context["summary"] = summary
        context["items"] = summary["items"]
        context["topics"] = summary["topics"]
        return context


def curriculum_extraction_count() -> int:
    root = curriculum_extraction_root("00000000-0000-4000-8000-000000000000").parent
    if not root.exists():
        return 0
    return sum(1 for path in root.iterdir() if path.is_dir() and (path / "curriculum_items.json").exists())


def curriculum_extraction_summary(snapshot: CurriculumSnapshot) -> dict:
    root = curriculum_extraction_root(snapshot.snapshot_id)
    items_path = root / "curriculum_items.json"
    topics_path = root / "candidate_topics.json"
    exists = items_path.exists() and topics_path.exists()
    summary = {
        "exists": exists,
        "artifact_root": root,
        "curriculum_items_path": items_path,
        "candidate_topics_path": topics_path,
        "item_count": 0,
        "candidate_topic_count": 0,
        "screening_status": "not_generated",
        "validation_errors": [],
        "items": [],
        "topics": [],
    }
    if not exists:
        return summary
    try:
        items_payload = read_json(items_path)
        topics_payload = read_json(topics_path)
    except (OSError, json.JSONDecodeError) as exc:
        summary["validation_errors"] = [f"Unable to read extraction artifacts: {exc}"]
        return summary
    summary["items"] = items_payload.get("items", [])
    summary["topics"] = topics_payload.get("topics", [])
    summary["item_count"] = len(summary["items"])
    summary["candidate_topic_count"] = len(summary["topics"])
    summary["screening_status"] = topics_payload.get("screening_status", "unknown")
    summary["validation_errors"] = validate_curriculum_extraction_artifacts(root)
    return summary
