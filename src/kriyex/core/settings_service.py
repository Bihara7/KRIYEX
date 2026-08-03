"""Persisted, non-secret application settings."""

from kriyex.domain.models import ProviderConfig
from kriyex.infrastructure.database import Database


class SettingsService:
    _PROVIDER_KEY = "provider"
    _ENDPOINT_KEY = "ollama_endpoint"
    _MODEL_KEY = "ollama_model"
    _PRIVATE_MODE_KEY = "private_mode"

    def __init__(self, database: Database) -> None:
        self._database = database

    def provider_config(self) -> ProviderConfig:
        values = self._values()
        return ProviderConfig(
            provider=values.get(self._PROVIDER_KEY, "ollama"),
            endpoint=values.get(self._ENDPOINT_KEY, "http://127.0.0.1:11434"),
            model=values.get(self._MODEL_KEY, "llama3.2"),
        )

    def save_provider_config(self, config: ProviderConfig) -> None:
        values = {
            self._PROVIDER_KEY: config.provider,
            self._ENDPOINT_KEY: config.endpoint.rstrip("/"),
            self._MODEL_KEY: config.model,
        }
        with self._database.connection() as connection:
            connection.executemany(
                """INSERT INTO settings(key, value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)
                   ON CONFLICT(key) DO UPDATE SET value = excluded.value,
                   updated_at = CURRENT_TIMESTAMP""",
                values.items(),
            )

    def _values(self) -> dict[str, str]:
        with self._database.connection() as connection:
            rows = connection.execute("SELECT key, value FROM settings").fetchall()
        return {row["key"]: row["value"] for row in rows}

    def private_mode(self) -> bool:
        return self._values().get(self._PRIVATE_MODE_KEY, "false") == "true"

    def set_private_mode(self, enabled: bool) -> None:
        with self._database.connection() as connection:
            connection.execute(
                """INSERT INTO settings(key, value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)
                   ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = CURRENT_TIMESTAMP""",
                (self._PRIVATE_MODE_KEY, str(enabled).lower()),
            )
