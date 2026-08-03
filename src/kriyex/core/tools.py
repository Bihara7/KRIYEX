"""Declarative tool registry. Tools describe capabilities; execution stays opt-in."""

from collections.abc import Callable
from dataclasses import dataclass, field

from kriyex.domain.models import SafetyLevel


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    category: str
    safety_level: SafetyLevel
    permissions: tuple[str, ...] = ()
    parameters: dict[str, str] = field(default_factory=dict)


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}

    def register(self, definition: ToolDefinition) -> ToolDefinition:
        if definition.name in self._tools:
            raise ValueError(f"Tool already registered: {definition.name}")
        self._tools[definition.name] = definition
        return definition

    def list_tools(self) -> tuple[ToolDefinition, ...]:
        return tuple(self._tools.values())

    def tool(self, definition: ToolDefinition) -> Callable[[Callable[..., object]], Callable[..., object]]:
        def decorator(function: Callable[..., object]) -> Callable[..., object]:
            self.register(definition)
            return function
        return decorator


def create_default_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(ToolDefinition("calculator", "Evaluate a local arithmetic expression.", "productivity", SafetyLevel.SAFE))
    registry.register(ToolDefinition("read_file", "Read a user-selected file.", "filesystem", SafetyLevel.CONFIRM, ("filesystem",)))
    registry.register(ToolDefinition("run_command", "Run a terminal command after review.", "terminal", SafetyLevel.CONFIRM, ("terminal",)))
    return registry
