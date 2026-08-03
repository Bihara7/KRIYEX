"""Local model settings. Secrets are intentionally not collected here."""

from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
)

from kriyex.core.settings_service import SettingsService
from kriyex.domain.models import ProviderConfig


class SettingsDialog(QDialog):
    def __init__(self, settings_service: SettingsService, parent: object | None = None) -> None:
        super().__init__(parent)
        self._settings_service = settings_service
        config = settings_service.provider_config()
        self.setWindowTitle("KRIYEX Settings")
        self.setMinimumWidth(440)

        layout = QFormLayout(self)
        self.endpoint = QLineEdit(config.endpoint)
        self.model = QLineEdit(config.model)
        self.private_mode = QCheckBox("Private Mode — do not save new chats or use memory")
        self.private_mode.setChecked(settings_service.private_mode())
        self.endpoint.setPlaceholderText("http://127.0.0.1:11434")
        self.model.setPlaceholderText("llama3.2")
        layout.addRow("Ollama endpoint", self.endpoint)
        layout.addRow("Model", self.model)
        layout.addRow(self.private_mode)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def _save(self) -> None:
        endpoint = self.endpoint.text().strip().rstrip("/")
        model = self.model.text().strip()
        if not endpoint.startswith(("http://", "https://")) or not model:
            QMessageBox.warning(self, "Invalid settings", "Enter an HTTP(S) endpoint and a model name.")
            return
        self._settings_service.save_provider_config(ProviderConfig(endpoint=endpoint, model=model))
        self._settings_service.set_private_mode(self.private_mode.isChecked())
        self.accept()
