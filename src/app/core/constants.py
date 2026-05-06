from enum import StrEnum


class AppEnvironment(StrEnum):
    """List of environments to run the application in."""

    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TEST = "test"
