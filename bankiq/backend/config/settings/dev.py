"""Development settings — DEBUG on, permissive hosts for local Docker."""

from config.settings.base import *  # noqa: F403

DEBUG = True
ALLOWED_HOSTS = ["*"]
