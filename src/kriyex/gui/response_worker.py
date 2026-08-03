"""Background worker for streaming model output without blocking Qt."""

from PySide6.QtCore import QThread, Signal

from kriyex.core.ai_service import AIService
from kriyex.core.chat_service import ChatService
from kriyex.core.providers import ChatProvider, ProviderError


class ResponseWorker(QThread):
    chunk_received = Signal(str)
    response_failed = Signal(str)

    def __init__(
        self,
        chat_service: ChatService,
        ai_service: AIService,
        provider: ChatProvider,
        chat_id: int,
        parent: object | None = None,
    ) -> None:
        super().__init__(parent)
        self._chat_service = chat_service
        self._ai_service = ai_service
        self._provider = provider
        self._chat_id = chat_id

    def run(self) -> None:
        response_parts: list[str] = []

        try:
            messages = self._chat_service.messages(self._chat_id)

            user_message = ""
            for message in reversed(messages):
                if message.role.value == "user":
                    user_message = message.content
                    break

            context = self._ai_service.analyze(
                user_message=user_message,
                chat_id=self._chat_id,
            )

            system_prompt = self._ai_service.build_system_prompt(context)

            for chunk in self._provider.stream(system_prompt, messages):
                response_parts.append(chunk)
                self.chunk_received.emit(chunk)

            response = "".join(response_parts).strip()

            if not response:
                raise ProviderError("Ollama returned an empty response.")

        except ProviderError as error:
            response = (
                "I could not contact the selected Ollama model. "
                "Confirm that Ollama is running."
            )
            self.response_failed.emit(str(error))

        self._chat_service.complete_turn(
            self._chat_id,
            response,
        )