import json
import tempfile
from pathlib import Path

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import RedirectView
from django.views.generic import TemplateView

from apps.curriculum.forms import CurriculumSourceForm
from apps.curriculum.forms import SnapshotCaptureForm
from apps.curriculum.models import CurriculumSnapshot
from apps.curriculum.models import CurriculumSource
from apps.curriculum.services import create_snapshot
from apps.curriculum.services import generate_unique_snapshot_id
from apps.curriculum.services import seed_curriculum_sources
from apps.curriculum.services import source_registry_payload


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
        }


class CurriculumHomeView(StaffRequiredMixin, CurriculumContextMixin, TemplateView):
    template_name = "curriculum/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.curriculum_context())
        active_tab = self.request.GET.get("tab", "sources")
        context["active_tab"] = active_tab if active_tab in {"sources", "snapshots"} else "sources"
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
