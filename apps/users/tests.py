from io import StringIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import Client
from django.test import TestCase
from django.test import override_settings
from django.urls import reverse

from apps.users.models import UserInvitation
from apps.users.roles import EVALUATOR
from apps.users.services import create_user_invitation


class UserModelTests(TestCase):
    def test_create_user_uses_email_as_username(self):
        user = get_user_model().objects.create_user(
            email="TestUser@Example.com",
            password="strong-password-123",
        )

        self.assertEqual(user.email, "testuser@example.com")
        self.assertEqual(user.get_username(), "testuser@example.com")

    def test_bootstrap_superuser_generates_password_in_noinput_mode(self):
        output = StringIO()
        with patch(
            "apps.users.management.commands.bootstrap_superuser.secrets.token_urlsafe",
            return_value="Generated-pass-123",
        ):
            call_command(
                "bootstrap_superuser",
                "admin@example.com",
                "--noinput",
                stdout=output,
            )

        user = get_user_model().objects.get(email="admin@example.com")
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.check_password("Generated-pass-123"))
        self.assertIn("Superuser created: admin@example.com", output.getvalue())


class AuthTemplateTests(TestCase):
    def test_login_page_renders_before_google_credentials_are_configured(self):
        response = Client().get(reverse("login"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sign in with Google")
        self.assertContains(response, reverse("google_login"))
        self.assertContains(response, "Sign In")
        self.assertNotContains(response, "Superuser fallback")

    @override_settings(
        SOCIALACCOUNT_PROVIDERS={
            "google": {
                "APPS": [
                    {
                        "client_id": "test-google-client-id",
                        "secret": "test-google-client-secret",
                    }
                ],
                "SCOPE": ["profile", "email"],
            }
        }
    )
    def test_login_page_uses_google_only_kisomo_surface(self):
        response = Client().get(reverse("login"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sign in to Kisomo")
        self.assertContains(response, "Sign in with Google")
        self.assertContains(response, "kisomo-brand.png")
        self.assertContains(response, "google-mark.png")
        self.assertNotContains(response, "Reset password")
        content = response.content.decode()
        self.assertLess(content.index("Sign In"), content.index("Sign in with Google"))

    def test_superuser_can_sign_in_with_local_password(self):
        get_user_model().objects.create_superuser(
            email="admin@example.com",
            password="strong-password-123",
        )
        response = Client().post(
            reverse("login"),
            {
                "username": "admin@example.com",
                "password": "strong-password-123",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Kisomo Dissertation Platform")

    def test_superuser_can_create_invitation_and_acceptance_creates_account(self):
        admin = get_user_model().objects.create_superuser(
            email="admin@example.com",
            password="strong-password-123",
        )
        invite = create_user_invitation(
            email="teacher@example.com",
            first_name="Teacher",
            last_name="Reviewer",
            role_key=EVALUATOR,
            invited_by=admin,
        )

        response = Client().post(
            reverse(
                "invite-accept",
                kwargs={"uid": invite.invitation.pk, "token": invite.token},
            ),
            {
                "new_password1": "accepted-strong-password-123",
                "new_password2": "accepted-strong-password-123",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        user = get_user_model().objects.get(email="teacher@example.com")
        self.assertTrue(user.check_password("accepted-strong-password-123"))
        invite.invitation.refresh_from_db()
        self.assertEqual(invite.invitation.status, UserInvitation.Status.ACCEPTED)

    @override_settings(
        SOCIALACCOUNT_PROVIDERS={
            "google": {
                "APPS": [
                    {
                        "client_id": "test-google-client-id",
                        "secret": "test-google-client-secret",
                    }
                ],
                "SCOPE": ["profile", "email"],
            }
        }
    )
    def test_google_login_redirects_directly_to_provider_when_configured(self):
        response = Client().get(reverse("google_login"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("accounts.google.com", response["Location"])

    def test_authenticated_user_can_access_baseline_dashboard(self):
        user = get_user_model().objects.create_user(
            email="operator@example.com",
            password="strong-password-123",
        )
        client = Client()
        client.force_login(user)

        response = client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Kisomo Dissertation Platform")
        self.assertContains(response, "Curriculum source snapshot evidence is now available for inspection before extraction")
        self.assertContains(response, "kisomo-page kisomo-page-stack")
        self.assertContains(response, "kisomo-card-grid kisomo-card-grid--two")
        self.assertContains(response, "kisomo-content-stack")
        self.assertContains(response, 'aria-labelledby="dashboard-curriculum-title"')
        self.assertContains(response, "kisomo-shell__sidebar")
        self.assertContains(response, "Dashboard")
        self.assertNotContains(response, "Users &amp; Roles")
        self.assertContains(response, "<title>Kisomo | Dashboard</title>", html=True)
        self.assertContains(response, "Notifications")
        self.assertContains(response, "kisomo-shell__account-menu")
        self.assertContains(response, "lock_reset")
        self.assertContains(response, "logout")
        self.assertContains(response, "data-kisomo-drawer-toggle")
        self.assertContains(response, "dissertation/ui/shell.js")
        self.assertContains(response, "?v=20260622-1")
        self.assertContains(response, '<nav class="kisomo-shell__breadcrumbs" aria-label="Breadcrumb">')
        self.assertNotContains(response, "Research Platform")
        self.assertNotContains(response, "<p>Kisomo</p>", html=True)
        self.assertNotContains(response, "vf-page__menu")

    def test_non_superuser_cannot_access_configuration(self):
        user = get_user_model().objects.create_user(
            email="operator-config@example.com",
            password="strong-password-123",
            is_staff=True,
        )
        client = Client()
        client.force_login(user)

        response = client.get(reverse("users-roles"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("dashboard"))

    def test_users_roles_page_uses_kisomo_shell(self):
        user = get_user_model().objects.create_superuser(
            email="admin@example.com",
            password="strong-password-123",
        )
        client = Client()
        client.force_login(user)

        response = client.get(reverse("users-roles"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<title>Kisomo | Users &amp; Roles</title>", html=True)
        self.assertContains(response, "kisomo-shell__sidebar")
        self.assertContains(response, "Users &amp; Roles")
        self.assertContains(response, "Research Operator")
        self.assertContains(response, "Evaluator")
        self.assertContains(response, "Invite User")
        self.assertNotContains(response, "vf-page__menu")
