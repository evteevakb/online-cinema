from django.conf import settings

INSTALLED_APPS = [
    "corsheaders",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "users.apps.UsersConfig",
    "movies.apps.MoviesConfig",
]

if settings.DEBUG:
    INSTALLED_APPS += [
        "debug_toolbar",
    ]
