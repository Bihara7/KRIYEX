from dataclasses import dataclass
from pathlib import Path

from kriyex.shared.constants import (
    APP_NAME,
    APP_VERSION,
    ORGANIZATION_NAME,
)


@dataclass(frozen=True)
class AppSettings:
    """Application configuration."""

    app_name: str = APP_NAME
    version: str = APP_VERSION
    organization: str = ORGANIZATION_NAME
    data_directory: Path = Path.home() / ".kriyex"

    @property
    def database_path(self) -> Path:
        return self.data_directory / "kriyex.db"


settings = AppSettings()
