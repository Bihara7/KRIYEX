"""Approval gate for tools. No confirmation-required operation runs implicitly."""

from dataclasses import dataclass

from kriyex.core.audit_service import AuditService
from kriyex.core.permissions import PermissionManager
from kriyex.core.tools import ToolDefinition, ToolRegistry
from kriyex.domain.models import SafetyLevel


@dataclass(frozen=True)
class ExecutionDecision:
    allowed: bool
    explanation: str


class ToolExecutor:
    def __init__(
        self,
        registry: ToolRegistry,
        permissions: PermissionManager,
        audit: AuditService,
    ) -> None:
        self._registry = registry
        self._permissions = permissions
        self._audit = audit

    def request(self, tool_name: str, reason: str) -> ExecutionDecision:
        tool = next((item for item in self._registry.list_tools() if item.name == tool_name), None)
        if tool is None:
            decision = ExecutionDecision(False, f"Unknown tool: {tool_name}")
        else:
            decision = self._evaluate(tool)
        self._audit.record("tool_request", f"{tool_name}: {reason}", "allowed" if decision.allowed else "pending")
        return decision

    def _evaluate(self, tool: ToolDefinition) -> ExecutionDecision:
        if tool.safety_level == SafetyLevel.SAFE:
            return ExecutionDecision(True, "This tool is classified as safe.")
        if all(self._permissions.is_allowed(capability) for capability in tool.permissions):
            return ExecutionDecision(True, "Required permissions were previously approved.")
        if all(self._permissions.consume_allow_once(capability) for capability in tool.permissions):
            return ExecutionDecision(True, "Required permission was approved for this one action.")
        return ExecutionDecision(False, "Explicit approval is required before this tool can run.")
