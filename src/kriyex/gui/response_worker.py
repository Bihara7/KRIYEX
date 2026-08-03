"""Background worker for streaming model output without blocking Qt."""

from PySide6.QtCore import QThread, Signal

from kriyex.core.chat_service import ChatService
from kriyex.core.providers import ChatProvider, ProviderError


class ResponseWorker(QThread):
    chunk_received = Signal(str)
    response_failed = Signal(str)

    def __init__(
        self,
        chat_service: ChatService,
        provider: ChatProvider,
        chat_id: int,
        parent: object | None = None,
    ) -> None:
        super().__init__(parent)
        self._chat_service = chat_service
        self._provider = provider
        self._chat_id = chat_id

    def run(self) -> None:
        response_parts: list[str] = []
        try:
            for chunk in self._provider.stream(self._chat_service.messages(self._chat_id)):
                response_parts.append(chunk)
                self.chunk_received.emit(chunk)
            response = "".join(response_parts).strip()
            if not response:
                raise ProviderError("Ollama returned an empty response.")
        except ProviderError as error:
            response = (
                "I could not contact the selected Ollama model. Confirm that Ollama is running, "
                "then check the endpoint and model in Settings."
            )
            self.response_failed.emit(str(error))
        self._chat_service.complete_turn(self._chat_id, response)
