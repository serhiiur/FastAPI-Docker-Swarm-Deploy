import os

from app.core.constants import AppEnvironment

os.environ["APP_ENVIRONMENT"] = AppEnvironment.TEST
