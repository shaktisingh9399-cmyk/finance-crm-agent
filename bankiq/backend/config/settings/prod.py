"""Production settings — hardened defaults."""

from config.settings.base import *  # noqa: F403

DEBUG = False

DATABASES["default"]["CONN_MAX_AGE"] = 60  # noqa: F405
