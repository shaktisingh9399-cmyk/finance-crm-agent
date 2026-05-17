/** Human-readable pipeline stage labels for end users. */

import { PipelineStage } from "@/types/agent";

export interface StageInfo {
  key: PipelineStage;
  label: string;
  description: string;
}

export const PIPELINE_STAGES: StageInfo[] = [
  {
    key: PipelineStage.Search,
    label: "Find customers",
    description: "Search your portfolio using income, credit score, and EMI filters.",
  },
  {
    key: PipelineStage.FetchHistory,
    label: "Review history",
    description: "Pull recent transaction patterns for shortlisted customers.",
  },
  {
    key: PipelineStage.Score,
    label: "Score leads",
    description: "Rank customers by how likely they are to convert.",
  },
  {
    key: PipelineStage.Compliance,
    label: "Compliance check",
    description: "Verify KYC, consent, DNC, and regulatory rules (required).",
  },
  {
    key: PipelineStage.GenerateMessages,
    label: "Draft messages",
    description: "Create personalised WhatsApp outreach for approved customers.",
  },
  {
    key: PipelineStage.Finalize,
    label: "Prepare campaign",
    description: "Package approved leads and messages for your review.",
  },
];

export const EXAMPLE_PROMPTS = [
  {
    title: "Personal loan — high value",
    text: "Find high-value customers likely to convert for a personal loan this month. Income above 12L, CIBIL 720+, EMI below 35%.",
  },
  {
    title: "Fixed deposit — re-engage",
    text: "Identify customers with strong savings but low app activity for a fixed deposit campaign. Balance above 3L, no active FD.",
  },
  {
    title: "Fresh loan after closure",
    text: "Find customers who recently closed a loan with low EMI burden — good candidates for a new personal loan.",
  },
] as const;

export function getStageLabel(stage: PipelineStage): string {
  if (stage === PipelineStage.Init) return "Ready to start";
  if (stage === PipelineStage.Done) return "Complete";
  if (stage === PipelineStage.Error) return "Something went wrong";
  return PIPELINE_STAGES.find((s) => s.key === stage)?.label ?? stage;
}
