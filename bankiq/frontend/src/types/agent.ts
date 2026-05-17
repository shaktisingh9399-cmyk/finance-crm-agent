/** Agent pipeline and WebSocket message types. */

export enum PipelineStage {
  Init = "INIT",
  Search = "SEARCH",
  FetchHistory = "FETCH_HISTORY",
  Score = "SCORE",
  Compliance = "COMPLIANCE",
  GenerateMessages = "GENERATE_MESSAGES",
  Finalize = "FINALIZE",
  Done = "DONE",
  Error = "ERROR",
}

export enum PipelineEventStatus {
  Queued = "queued",
  Started = "started",
  Completed = "completed",
  Finished = "finished",
  Failed = "failed",
}

export enum AgentMessageRole {
  User = "user",
  Assistant = "assistant",
  System = "system",
}

export enum AgentToolName {
  SearchCustomers = "search_customers",
  GetTransactionHistory = "get_transaction_history",
  CalculateConversionScore = "calculate_conversion_score",
  CheckRegulatoryCompliance = "check_regulatory_compliance",
  GenerateMessages = "generate_messages",
  FinalizeResults = "finalize_results",
}

export enum PipelineDataKey {
  Error = "error",
  Message = "message",
}

export interface StageUpdate {
  stage: PipelineStage;
  status: PipelineEventStatus;
  data: Record<string, unknown>;
  timestamp: string;
}

export interface AgentMessage {
  id: string;
  role: AgentMessageRole;
  content: string;
  timestamp: string;
}

export interface PipelineState {
  currentStage: PipelineStage;
  stageHistory: StageUpdate[];
  messages: AgentMessage[];
  isRunning: boolean;
}
