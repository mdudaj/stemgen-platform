from django.urls import path

from apps.curriculum.views import CurriculumHomeView
from apps.curriculum.views import CurriculumExtractionCreateView
from apps.curriculum.views import CurriculumExtractionDetailView
from apps.curriculum.views import CurriculumExtractionListView
from apps.curriculum.views import CurriculumIntakeRedirectView
from apps.curriculum.views import CurriculumSnapshotCaptureView
from apps.curriculum.views import CurriculumSnapshotDetailView
from apps.curriculum.views import CurriculumSnapshotListView
from apps.curriculum.views import CurriculumSourceCreateView
from apps.curriculum.views import CurriculumSourceListView


urlpatterns = [
    path("", CurriculumHomeView.as_view(), name="curriculum-home"),
    path("intake/", CurriculumIntakeRedirectView.as_view(), name="curriculum-intake"),
    path("sources/", CurriculumSourceListView.as_view(), name="curriculum-source-list"),
    path("sources/new/", CurriculumSourceCreateView.as_view(), name="curriculum-source-create"),
    path("extractions/", CurriculumExtractionListView.as_view(), name="curriculum-extraction-list"),
    path("extractions/<slug:snapshot_id>/", CurriculumExtractionDetailView.as_view(), name="curriculum-extraction-detail"),
    path("extractions/<slug:snapshot_id>/create/", CurriculumExtractionCreateView.as_view(), name="curriculum-extraction-create"),
    path("snapshots/new/", CurriculumSnapshotCaptureView.as_view(), name="curriculum-snapshot-capture"),
    path("snapshots/", CurriculumSnapshotListView.as_view(), name="curriculum-snapshot-list"),
    path("snapshots/<slug:snapshot_id>/", CurriculumSnapshotDetailView.as_view(), name="curriculum-snapshot-detail"),
]
