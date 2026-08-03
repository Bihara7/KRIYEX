from dataclasses import dataclass, field
from pathlib import Path

from kriyex.shared.constants import (
    APP_NAME,
    APP_VERSION,
    ORGANIZATION_NAME,
)


# ------------------------------------------------------------------
# General Application Settings
# ------------------------------------------------------------------

@dataclass(frozen=True)
class GeneralSettings:
    app_name: str = APP_NAME
    version: str = APP_VERSION
    organization: str = ORGANIZATION_NAME


# ------------------------------------------------------------------
# Database Settings
# ------------------------------------------------------------------

@dataclass(frozen=True)
class DatabaseSettings:
    data_directory: Path = Path.home() / ".kriyex"

    @property
    def database_path(self) -> Path:
        return self.data_directory / "kriyex.db"


# ------------------------------------------------------------------
# AI Settings
# ------------------------------------------------------------------

@dataclass(frozen=True)
class AISettings:
    default_provider: str = "ollama"
    streaming: bool = True
    temperature: float = 0.7


# ------------------------------------------------------------------
# Logging Settings
# ------------------------------------------------------------------

@dataclass(frozen=True)
class LoggingSettings:
    level: str = "INFO"
    save_to_file: bool = True


# ------------------------------------------------------------------
# Root Settings
# ------------------------------------------------------------------

@dataclass(frozen=True)
class AppSettings:
    general: GeneralSettings = field(default_factory=GeneralSettings)
    database: DatabaseSettings = field(default_factory=DatabaseSettings)
    ai: AISettings = field(default_factory=AISettings)
    logging: LoggingSettings = field(default_factory=LoggingSettings)

    @property
    def app_name(self) -> str:
        return self.general.app_name

    @property
    def version(self) -> str:
        return self.general.version

    @property
    def organization(self) -> str:
        return self.general.organization

    @property
    def database_path(self) -> Path:
        return self.database.database_path


settings = AppSettings()