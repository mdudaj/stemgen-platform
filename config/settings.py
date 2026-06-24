import os
from pathlib import Path
from urllib.parse import unquote
from urllib.parse import urlparse


BASE_DIR = Path(__file__).resolve().parent.parent


def load_env_file(env_path: Path) -> None:
    if not env_path.exists():
        return

    for line in env_path.read_text().splitlines():
        raw_line = line.strip()
        if not raw_line or raw_line.startswith("#") or "=" not in raw_line:
            continue
        key, value = raw_line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def parse_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def parse_csv(value: str | None) -> tuple[str, ...]:
    if not value:
        return ()
    return tuple(item.strip() for item in value.split(",") if item.strip())


def database_config_from_url(database_url: str, base_dir: Path) -> dict[str, str]:
    parsed = urlparse(database_url)

    if parsed.scheme in {"postgres", "postgresql"}:
        return {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": parsed.path.lstrip("/"),
            "USER": unquote(parsed.username or ""),
            "PASSWORD": unquote(parsed.password or ""),
            "HOST": parsed.hostname or "localhost",
            "PORT": str(parsed.port or 5432),
        }

    if parsed.scheme == "sqlite":
        raw_path = f"{parsed.netloc}{parsed.path}" or "db.sqlite3"
        sqlite_path = Path("/" + raw_path.lstrip("/")) if raw_path.startswith("//") else base_dir / raw_path.lstrip("/")
        return {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": str(sqlite_path),
        }

    raise ValueError(f"Unsupported DATABASE_URL scheme: {parsed.scheme}")


load_env_file(BASE_DIR / ".env")

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", os.environ.get("SECRET_KEY", "change-me"))
DEBUG = parse_bool(os.environ.get("DJANGO_DEBUG", os.environ.get("DEBUG")), default=True)
ALLOWED_HOSTS = list(
    parse_csv(
        os.environ.get(
            "DJANGO_ALLOWED_HOSTS",
            os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1"),
        )
    )
)
CSRF_TRUSTED_ORIGINS = list(parse_csv(os.environ.get("CSRF_TRUSTED_ORIGINS")))

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sites",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "viewflow",
    "viewflow.workflow",
    "apps.curriculum.apps.CurriculumConfig",
    "apps.users.apps.UsersConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": database_config_from_url(
        os.environ.get("DATABASE_URL", "sqlite:///db.sqlite3"),
        BASE_DIR,
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

AUTH_USER_MODEL = "users.User"
SITE_ID = 1
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]
LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/accounts/login/"

ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "first_name", "last_name"]
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USER_MODEL_EMAIL_FIELD = "email"
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = "none"
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True
SOCIALACCOUNT_LOGIN_ON_GET = True
SOCIALACCOUNT_STORE_TOKENS = True
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online"},
        "FETCH_USERINFO": True,
        "VERIFIED_EMAIL": True,
        **({"HD": os.environ["GOOGLE_OAUTH_HD"]} if os.environ.get("GOOGLE_OAUTH_HD") else {}),
        **(
            {
                "APPS": [
                    {
                        "client_id": os.environ["GOOGLE_OAUTH_CLIENT_ID"],
                        "secret": os.environ["GOOGLE_OAUTH_CLIENT_SECRET"],
                    }
                ]
            }
            if os.environ.get("GOOGLE_OAUTH_CLIENT_ID") and os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET")
            else {}
        ),
    }
}

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Dar_es_Salaam"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
CURRICULUM_ARTIFACT_ROOT = BASE_DIR / "artifacts" / "curriculum-snapshots"
CURRICULUM_EXTRACTION_ROOT = BASE_DIR / "artifacts" / "curriculum-extractions"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REDIS_URL = os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/1")
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://127.0.0.1:6379/0")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", CELERY_BROKER_URL)
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TASK_TRACK_STARTED = True

EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend" if DEBUG else "django.core.mail.backends.smtp.EmailBackend",
)
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "webmaster@localhost")
