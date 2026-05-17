/** Agent hook — REST query dispatch + WebSocket pipeline updates. */

import { useCallback, useRef } from "react";

import { api } from "@/lib/api";
import { useAuthStore } from "@/store/authStore";
import { usePipelineStore } from "@/store/pipelineStore";
import type { AgentQueryResponse } from "@/types/api";
import {
  AgentMessageRole,
  PipelineDataKey,
  PipelineEventStatus,
  PipelineStage,
  type StageUpdate,
} from "@/types/agent";

const WS_BASE = import.meta.env.VITE_WS_BASE_URL ?? "ws://localhost:8000";

export function useAgent() {
  const wsRef = useRef<WebSocket | null>(null);
  const {
    sessionId,
    isRunning,
    setSessionId,
    setRunning,
    addStageUpdate,
    addMessage,
    reset,
  } = usePipelineStore();

  const connectWebSocket = useCallback(
    (id: string) => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      const token = useAuthStore.getState().accessToken;
      const url = token
        ? `${WS_BASE}/ws/agent/${id}/?token=${token}`
        : `${WS_BASE}/ws/agent/${id}/`;
      const ws = new WebSocket(url);
      ws.onmessage = (event) => {
        const update = JSON.parse(event.data as string) as StageUpdate;
        addStageUpdate({
          ...update,
          stage: update.stage as PipelineStage,
        });
        if (
          update.status === PipelineEventStatus.Finished ||
          update.stage === PipelineStage.Done ||
          update.stage === PipelineStage.Error
        ) {
          setRunning(false);
          const assistantMsg =
            (update.data?.[PipelineDataKey.Message] as string) ||
            (update.data?.[PipelineDataKey.Error] as string);
          if (assistantMsg) {
            addMessage({
              id: crypto.randomUUID(),
              role: AgentMessageRole.Assistant,
              content: assistantMsg,
              timestamp: new Date().toISOString(),
            });
          }
        }
      };
      ws.onerror = () => {
        console.error("WebSocket connection error");
        setRunning(false);
      };
      ws.onclose = () => {
        wsRef.current = null;
      };
      wsRef.current = ws;
    },
    [addStageUpdate, setRunning],
  );

  const sendQuery = useCallback(
    async (query: string) => {
      const id = crypto.randomUUID();
      setSessionId(id);
      setRunning(true);
      addMessage({
        id: crypto.randomUUID(),
        role: AgentMessageRole.User,
        content: query,
        timestamp: new Date().toISOString(),
      });

      connectWebSocket(id);

      await api.post<AgentQueryResponse>("/agent/query/", {
        query,
        session_id: id,
      });
    },
    [addMessage, connectWebSocket, setRunning, setSessionId],
  );

  const disconnect = useCallback(() => {
    wsRef.current?.close();
    reset();
  }, [reset]);

  return { sessionId, isRunning, sendQuery, disconnect };
}
