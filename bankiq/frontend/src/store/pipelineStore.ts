/** Agent pipeline stage and message state. */

import { create } from "zustand";

import { PipelineStage, type AgentMessage, type StageUpdate } from "@/types/agent";

interface PipelineStore {
  currentStage: PipelineStage;
  stageHistory: StageUpdate[];
  messages: AgentMessage[];
  isRunning: boolean;
  sessionId: string | null;
  setSessionId: (id: string) => void;
  setRunning: (running: boolean) => void;
  addStageUpdate: (update: StageUpdate) => void;
  addMessage: (message: AgentMessage) => void;
  reset: () => void;
}

const initialStage = PipelineStage.Init;

export const usePipelineStore = create<PipelineStore>((set) => ({
  currentStage: initialStage,
  stageHistory: [],
  messages: [],
  isRunning: false,
  sessionId: null,

  setSessionId: (id) => set({ sessionId: id }),
  setRunning: (isRunning) => set({ isRunning }),

  addStageUpdate: (update) =>
    set((state) => ({
      currentStage: update.stage,
      stageHistory: [...state.stageHistory, update],
    })),

  addMessage: (message) =>
    set((state) => ({ messages: [...state.messages, message] })),

  reset: () =>
    set({
      currentStage: initialStage,
      stageHistory: [],
      messages: [],
      isRunning: false,
      sessionId: null,
    }),
}));
