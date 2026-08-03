"""Deterministic, inspectable first-pass plans for user goals."""

from dataclasses import dataclass


@dataclass(frozen=True)
class PlanStep:
    title: str
    requires_approval: bool = False
    capability: str | None = None


class Planner:
    def create_plan(self, goal: str) -> list[PlanStep]:
        normalized = goal.strip()
        if not normalized:
            raise ValueError("A goal is required to create a plan.")
        steps = [
            PlanStep("Review the goal and clarify expected output"),
            PlanStep("Inspect the relevant files and current state"),
        ]
        lowered = normalized.lower()
        if any(term in lowered for term in ("create", "build", "write", "generate")):
            steps.append(
                PlanStep(
                    "Create or update the required files",
                    requires_approval=True,
                    capability="filesystem",
                )
            )
        if any(term in lowered for term in ("install", "download", "deploy", "publish")):
            steps.append(
                PlanStep(
                    "Request approval before external or system changes",
                    requires_approval=True,
                    capability="terminal",
                )
            )
        steps.extend(
            [
                PlanStep("Validate the result and inspect errors"),
                PlanStep("Present the completed work and remaining decisions"),
            ]
        )
        return steps
