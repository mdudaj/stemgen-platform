from urllib.parse import urlparse

from django import forms
from django.core.exceptions import ValidationError
from viewflow.forms import FieldSet
from viewflow.forms import Layout
from viewflow.forms import Row

from apps.curriculum.models import CurriculumSource
from apps.curriculum.services import generate_unique_curriculum_source_id
from apps.curriculum.services import safe_filename

OFFICIAL_TIE_HOST = "www.tie.go.tz"


class CurriculumSourceForm(forms.Form):
    document_type = forms.ChoiceField(
        choices=(("curriculum", "Curriculum"), ("syllabus", "Syllabus")),
        initial="syllabus",
        help_text="Classifies the official document for later evidence review.",
    )
    year = forms.IntegerField(
        min_value=2000,
        max_value=2100,
        initial=2024,
        help_text="Use confirmed document year when known.",
    )
    title = forms.CharField(max_length=255)
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
        help_text="Operator-facing context for this source. Do not include secrets.",
    )
    official_url = forms.URLField(
        max_length=600,
        help_text="Official TIE PDF URL. Tier 1 intake is limited to www.tie.go.tz.",
    )
    subject = forms.CharField(max_length=120)
    coverage = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}))
    standards_covered = forms.CharField(
        help_text="Comma-separated standards, for example III, IV, V, VI.",
    )
    expected_filename = forms.CharField(max_length=180)
    source_tier = forms.ChoiceField(
        choices=CurriculumSource.SourceTier.choices,
        initial=CurriculumSource.SourceTier.TIER_1,
    )
    is_active = forms.BooleanField(required=False, initial=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout = Layout(
            FieldSet(
                "Source Identity",
                Row("document_type", "year"),
                Row("title"),
                Row("description"),
                Row("official_url"),
            ),
            FieldSet(
                "Curriculum Coverage",
                Row("subject"),
                Row("coverage"),
                Row("standards_covered", "expected_filename"),
                Row("source_tier", "is_active"),
            ),
        )

    def clean_official_url(self):
        official_url = self.cleaned_data["official_url"].strip()
        host = urlparse(official_url).netloc.lower()
        if host != OFFICIAL_TIE_HOST:
            raise ValidationError("Use an official TIE URL from www.tie.go.tz for Tier 1 intake.")
        return official_url

    def clean_standards_covered(self):
        standards = [item.strip() for item in self.cleaned_data["standards_covered"].split(",") if item.strip()]
        if not standards:
            raise ValidationError("Provide at least one covered standard.")
        return standards

    def clean_expected_filename(self):
        expected_filename = self.cleaned_data["expected_filename"].strip()
        if safe_filename(expected_filename) != expected_filename or not expected_filename.lower().endswith(".pdf"):
            raise ValidationError("Provide a safe PDF filename without path separators.")
        return expected_filename

    def save(self):
        source = CurriculumSource.objects.create(
            source_id=generate_unique_curriculum_source_id(
                document_type=self.cleaned_data["document_type"],
                subject=self.cleaned_data["subject"],
                standards_covered=self.cleaned_data["standards_covered"],
                year=self.cleaned_data["year"],
                official_url=self.cleaned_data["official_url"],
            ),
            title=self.cleaned_data["title"],
            description=self.cleaned_data["description"],
            official_url=self.cleaned_data["official_url"],
            publisher="Tanzania Institute of Education",
            source_tier=self.cleaned_data["source_tier"],
            subject=self.cleaned_data["subject"],
            coverage=self.cleaned_data["coverage"],
            standards_covered=self.cleaned_data["standards_covered"],
            expected_filename=self.cleaned_data["expected_filename"],
            checksum_algorithm="sha256",
            is_active=self.cleaned_data["is_active"],
        )
        return source


class SnapshotCaptureForm(forms.Form):
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
        help_text="Operator-facing note for why this snapshot is being captured.",
    )
    validate = forms.BooleanField(required=False, initial=True)
    no_download = forms.BooleanField(
        required=False,
        initial=True,
        help_text="Create manifests without downloading PDFs.",
    )
    use_local_cache = forms.BooleanField(
        required=False,
        help_text="Use files already available under the configured curriculum cache.",
    )
    live_retrieval = forms.BooleanField(
        required=False,
        help_text="Download the registered official sources now.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout = Layout(
            FieldSet(
                "Snapshot Capture",
                Row("description"),
                Row("validate"),
                Row("no_download", "use_local_cache"),
                Row("live_retrieval"),
            ),
        )

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("live_retrieval"):
            cleaned_data["no_download"] = False
            cleaned_data["use_local_cache"] = False
        elif cleaned_data.get("use_local_cache"):
            cleaned_data["no_download"] = False
        else:
            cleaned_data["no_download"] = True
        return cleaned_data
