"""Celery tasks for agent pipeline execution."""

import logging
from datetime import datetime, timezone
from typing import Any

from asgiref.sync import async_to_sync
from celery import shared_task
from channels.layers import get_channel_layer

from agent_core.enums import (
    ChannelEventField,
    ChannelEventType,
    MessageField,
    MessageRole,
    PipelineError,
    PipelineEventStatus,
    PipelinePayloadKey,
)
from agent_core.orchestrator import run as run_orchestrator

logger = logging.getLogger(__name__)


def _push_stage(session_id: str, stage: str, status: str, data: dict) -> None:
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return
    payload = {
        PipelinePayloadKey.STAGE.value: stage,
        PipelinePayloadKey.STATUS.value: status,
        PipelinePayloadKey.DATA.value: data,
        PipelinePayloadKey.TIMESTAMP.value: datetime.now(timezone.utc).isoformat(),
    }
    async_to_sync(channel_layer.group_send)(
        f"agent_{session_id}",
        {
            ChannelEventField.TYPE.value: ChannelEventType.PIPELINE_STAGE.value,
            ChannelEventField.PAYLOAD.value: payload,
        },
    )


@shared_task(bind=True, max_retries=2, name="tasks.run_agent_pipeline")
def run_agent_pipeline(self, session_id: str, rm_id: str, query: str) -> dict[str, Any]:
    """
    Run the agent orchestrator and stream stage updates via Channels.

    Parameters:
        session_id: WebSocket session UUID string.
        rm_id: Authenticated RM UUID string.
        query: Sanitized RM natural-language query.

    Returns:
        Serialized OrchestratorResult summary dict.
    """
    try:
        def stage_callback(stage: str, status: str, data: dict) -> None:
            _push_stage(session_id, stage, status, data)

        result = run_orchestrator(
            query=query,
            rm_id=rm_id,
            stage_callback=stage_callback,
        )

        assistant_content = ""
        for msg in reversed(result.messages):
            if (
                msg.get(MessageField.ROLE.value) == MessageRole.ASSISTANT.value
                and msg.get(MessageField.CONTENT.value)
            ):
                assistant_content = msg[MessageField.CONTENT.value]
                break

        _push_stage(
            session_id,
            result.final_stage,
            PipelineEventStatus.FINISHED.value,
            {
                PipelinePayloadKey.SUCCESS.value: result.success,
                PipelinePayloadKey.MESSAGE.value: assistant_content,
                PipelinePayloadKey.ERROR.value: result.error,
            },
        )

        return {
            PipelinePayloadKey.SUCCESS.value: result.success,
            PipelinePayloadKey.FINAL_STAGE.value: result.final_stage,
            PipelinePayloadKey.PROVIDER.value: result.provider,
            PipelinePayloadKey.ERROR.value: result.error,
        }
    except Exception as exc:
        logger.exception("Agent pipeline failed session=%s", session_id)
        try:
            raise self.retry(exc=exc, countdown=2 ** self.request.retries)
        except self.MaxRetriesExceededError:
            _push_stage(
                session_id,
                PipelineError.ERROR_STAGE.value,
                PipelineEventStatus.FAILED.value,
                {PipelinePayloadKey.ERROR.value: str(exc)},
            )
            raise
