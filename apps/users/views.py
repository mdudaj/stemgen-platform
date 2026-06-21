from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import PasswordContextMixin
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import FormView
from django.views.generic import TemplateView

from apps.users.forms import DissertationAuthenticationForm
from apps.users.forms import InviteAcceptanceForm
from apps.users.forms import UserInvitationForm
from apps.users.models import UserInvitation
from apps.users.roles import ROLE_CATALOG
from apps.users.services import accept_user_invitation


class DissertationLoginView(LoginView):
    authentication_form = DissertationAuthenticationForm
    template_name = "registration/login.html"


class UserInvitationCreateView(LoginRequiredMixin, FormView):
    template_name = "users/invite_form.html"
    form_class = UserInvitationForm

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.error(request, "Only superusers can create invitations.")
            return redirect("dashboard")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        try:
            invite = form.save(invited_by=self.request.user)
        except ValidationError as exc:
            form.add_error(None, exc)
            return self.form_invalid(form)
        acceptance_url = self.request.build_absolute_uri(
            reverse(
                "invite-accept",
                kwargs={"uid": invite.invitation.pk, "token": invite.token},
            )
        )
        messages.success(
            self.request,
            f"Invitation created. Acceptance link: {acceptance_url}",
        )
        return redirect("dashboard")


class UsersRolesView(LoginRequiredMixin, TemplateView):
    template_name = "users/index.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.error(request, "Only superusers can manage configuration.")
            return redirect("dashboard")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        User = get_user_model()
        users = User.objects.order_by("email")[:25]
        context["users"] = users
        context["user_count"] = User.objects.filter(is_active=True).count()
        context["pending_invite_count"] = UserInvitation.objects.filter(
            status=UserInvitation.Status.PENDING,
        ).count()
        context["roles"] = ROLE_CATALOG
        return context


class InviteAcceptanceView(PasswordContextMixin, FormView):
    template_name = "registration/invite_accept.html"
    form_class = InviteAcceptanceForm
    title = "Create Account"

    def dispatch(self, request, *args, **kwargs):
        self.invitation = get_object_or_404(UserInvitation, pk=kwargs["uid"])
        self.token = kwargs["token"]
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        User = get_user_model()
        user = User.objects.filter(email=self.invitation.email).first()
        if user is None:
            user = User(
                email=self.invitation.email,
                first_name=self.invitation.first_name,
                last_name=self.invitation.last_name,
                is_active=True,
            )
        kwargs["user"] = user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["invitation"] = self.invitation
        context["role_label"] = self._role_label(self.invitation.role_key)
        return context

    def form_valid(self, form):
        try:
            accept_user_invitation(
                invitation=self.invitation,
                token=self.token,
                password=form.cleaned_data["new_password1"],
            )
        except ValidationError as exc:
            form.add_error(None, exc)
            return self.form_invalid(form)
        messages.success(self.request, "Account created. Sign in to continue.")
        return redirect("login")

    def _role_label(self, role_key):
        for role in ROLE_CATALOG:
            if role.key == role_key:
                return role.label
        return role_key
