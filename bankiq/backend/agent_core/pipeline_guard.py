"""Pipeline stage enumeration and transition guard for the agent loop."""

from enum import IntEnum
from typing import Optional

from agent_core.enums import PipelineError, ToolName, ToolOutputKey

_MANDATORY_STAGES = frozenset()  # populated after Stage definition

STAGE_TOOL_MAP: dict[ToolName, "Stage"] = {}


class Stage(IntEnum):
    """Ordered agent pipeline stages — transitions enforced by PipelineGuard."""

    INIT = 0
    SEARCH = 1
    FETCH_HISTORY = 2
    SCORE = 3
    COMPLIANCE = 4
    GENERATE_MESSAGES = 5
    FINALIZE = 6
    DONE = 7


_MANDATORY_STAGES = frozenset({Stage.COMPLIANCE})

STAGE_TOOL_MAP = {
    ToolName.SEARCH_CUSTOMERS: Stage.SEARCH,
    ToolName.GET_TRANSACTION_HISTORY: Stage.FETCH_HISTORY,
    ToolName.CALCULATE_CONVERSION_SCORE: Stage.SCORE,
    ToolName.CHECK_REGULATORY_COMPLIANCE: Stage.COMPLIANCE,
    ToolName.GENERATE_MESSAGES: Stage.GENERATE_MESSAGES,
    ToolName.FINALIZE_RESULTS: Stage.FINALIZE,
}


class PipelineGuardError(Exception):
    """Raised when a tool call violates pipeline stage order."""

    def __init__(self, message: str, expected: Optional[Stage] = None) -> None:
        super().__init__(message)
        self.expected = expected


class PipelineGuard:
    """
    Tracks visited stages and validates tool calls against strict ordering.
    COMPLIANCE is mandatory before FINALIZE.
    """

    def __init__(self) -> None:
        self.current: Stage = Stage.INIT
        self.visited: set[Stage] = {Stage.INIT}

    def advance(self, stage: Stage) -> None:
        """Record a successfully completed stage."""
        if stage.value != self.current.value + 1 and stage != Stage.DONE:
            raise PipelineGuardError(
                f"Cannot advance to {stage.name} from {self.current.name}",
                expected=Stage(self.current.value + 1) if self.current.value < 6 else None,
            )
        self.current = stage
        self.visited.add(stage)

    def validate_tool(self, tool_name: ToolName | str) -> Optional[dict]:
        """
        Validate whether tool_name may be called at the current stage.

        Returns:
            None if valid, or a PIPELINE_GUARD_ERROR dict if invalid.
        """
        try:
            tool = ToolName(tool_name)
        except ValueError:
            return None
        target = STAGE_TOOL_MAP.get(tool)
        if target is None:
            return None

        if tool == ToolName.FINALIZE_RESULTS:
            if Stage.COMPLIANCE not in self.visited:
                return _guard_error(
                    "finalize_results requires COMPLIANCE stage to be completed first.",
                    required_stage=Stage.COMPLIANCE.name,
                )
            if self.current.value < Stage.GENERATE_MESSAGES.value:
                return _guard_error(
                    "finalize_results cannot be called before GENERATE_MESSAGES.",
                    required_stage=Stage.FINALIZE.name,
                )
            return None

        expected = Stage(self.current.value + 1) if self.current != Stage.DONE else Stage.DONE
        if target != expected and target not in self.visited:
            return _guard_error(
                f"Tool '{tool.value}' requires stage {expected.name}, "
                f"but current stage is {self.current.name}.",
                required_stage=expected.name,
            )
        return None

    def complete_tool(self, tool_name: ToolName | str) -> None:
        """Advance pipeline after a successful tool execution."""
        try:
            tool = ToolName(tool_name)
        except ValueError:
            return
        target = STAGE_TOOL_MAP.get(tool)
        if target is not None and target not in self.visited:
            self.advance(target)


def _guard_error(message: str, required_stage: str) -> dict:
    return {
        ToolOutputKey.ERROR.value: PipelineError.GUARD_ERROR.value,
        ToolOutputKey.MESSAGE.value: message,
        ToolOutputKey.REQUIRED_STAGE.value: required_stage,
        ToolOutputKey.CURRENT_STAGE.value: None,
    }
