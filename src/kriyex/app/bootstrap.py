"""
Application bootstrap.

This module is responsible for:
- Configuring logging.
- Creating the Qt application.
- Creating the application service container.
"""

from PySide6.QtWidgets import QApplication

from kriyex.app.container import ApplicationContainer
from kriyex.config.settings import settings
from kriyex.shared.logging import configure_logging


def create_application() -> QApplication:
    """
    Create and configure the QApplication instance.
    """
    configure_logging()

    app = QApplication([])

    app.setApplicationName(settings.app_name)
    app.setApplicationVersion(settings.version)
    app.setOrganizationName(settings.organization)

    return app


def create_services() -> ApplicationContainer:
    """
    Create and return the application's service container.
    """
    return ApplicationContainer()