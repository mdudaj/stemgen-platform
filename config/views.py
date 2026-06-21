from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from apps.curriculum.models import CurriculumSnapshot
from apps.curriculum.models import CurriculumSource


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "app/page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        latest_snapshot = CurriculumSnapshot.objects.order_by("-created_at", "-id").first()
        context["curriculum_source_count"] = CurriculumSource.objects.filter(is_active=True).count()
        context["latest_curriculum_snapshot"] = latest_snapshot
        context["latest_curriculum_warning_count"] = len(latest_snapshot.warnings) if latest_snapshot else 0
        return context
