from django.conf import settings
from django.test import SimpleTestCase


class SettingsTests(SimpleTestCase):
    def test_default_allowed_hosts_support_local_preview_host(self):
        self.assertIn("localhost", settings.ALLOWED_HOSTS)
        self.assertIn("127.0.0.1", settings.ALLOWED_HOSTS)
        self.assertNotIn("0.0.0.0", settings.ALLOWED_HOSTS)
