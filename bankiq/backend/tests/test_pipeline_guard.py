"""Unit tests for PipelineGuard stage enforcement."""

import pytest

from agent_core.enums import PipelineError, ToolName, ToolOutputKey
from agent_core.pipeline_guard import PipelineGuard, Stage


@pytest.mark.parametrize(
    "tool_name,should_error",
    [
        (ToolName.FINALIZE_RESULTS, True),
        (ToolName.SEARCH_CUSTOMERS, False),
    ],
)
def test_finalize_before_compliance(tool_name: ToolName, should_error: bool) -> None:
    guard = PipelineGuard()
    result = guard.validate_tool(tool_name)
    if should_error:
        assert result is not None
        assert result[ToolOutputKey.ERROR.value] == PipelineError.GUARD_ERROR.value
    else:
        assert result is None


def test_advance_stages_in_order() -> None:
    guard = PipelineGuard()
    guard.advance(Stage.SEARCH)
    assert Stage.SEARCH in guard.visited
    guard.advance(Stage.FETCH_HISTORY)
    assert guard.current == Stage.FETCH_HISTORY


def test_invalid_advance_raises() -> None:
    guard = PipelineGuard()
    with pytest.raises(Exception):
        guard.advance(Stage.SCORE)
