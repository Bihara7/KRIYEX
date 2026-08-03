"""Model-provider interface and local Ollama implementation."""

import json
from collections.abc import Callable, Iterator
from typing import Protocol
from urllib.error import URLError
from urllib.request import Request, urlopen
from kriyex.core.prompting.prompt_builder import PromptBuilder

from kriyex.domain.models import Message, ProviderConfig


class ProviderError(RuntimeError):
    """An approved model provider could not complete a request."""


class ChatProvider(Protocol):
    def stream(self, messages: list[Message]) -> Iterator[str]: ...


class OllamaProvider:
    def __init__(
        self,
        config: ProviderConfig,
        memories: tuple[str, ...] = (),
        opener: Callable[..., object] = urlopen,
    ) -> None:
        self._config = config
        self._memories = memories
        self._opener = opener

    def stream(self, messages: list[Message]) -> Iterator[str]:
        payload = {
            "model": self._config.model,
            "stream": True,
            "messages": [
                {
    "role": "system",
    "content": PromptBuilder().build(self._memories),
},
                *(
                    [
                        {
                            "role": "system",
                            "content": "User-approved relevant memories:\n- "
                            + "\n- ".join(self._memories),
                        }
                    ]
                    if self._memories
                    else []
                ),
                *[
                    {"role": message.role.value, "content": message.content}
                    for message in messages
                ],
            ],
        }
        request = Request(
            f"{self._config.endpoint.rstrip('/')}/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with self._opener(request, timeout=90) as response:  # type: ignore[union-attr]
                for raw_line in response:
                    if not raw_line.strip():
                        continue
                    event = json.loads(raw_line)
                    content = event.get("message", {}).get("content", "")
                    if content:
                        yield str(content)
        except (URLError, OSError, TimeoutError, json.JSONDecodeError) as error:
            raise ProviderError(f"Unable to reach Ollama at {self._config.endpoint}.") from error


class ProviderFactory:
    def create(self, config: ProviderConfig, memories: tuple[str, ...] = ()) -> ChatProvider:
        if config.provider == "ollama":
            return OllamaProvider(config, memories)
        raise ProviderError(f"Unsupported provider: {config.provider}")
