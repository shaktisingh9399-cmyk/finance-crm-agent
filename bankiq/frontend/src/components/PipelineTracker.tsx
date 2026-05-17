/** Visual progress for the agent pipeline — plain-language labels. */

import { PIPELINE_STAGES, getStageLabel } from "@/constants/pipelineStages";
import { PipelineStage } from "@/types/agent";

interface PipelineTrackerProps {
  currentStage: PipelineStage;
  isRunning: boolean;
}

function stageProgressIndex(stage: PipelineStage): number {
  if (stage === PipelineStage.Init) return -1;
  if (stage === PipelineStage.Done || stage === PipelineStage.Error) return PIPELINE_STAGES.length;
  const idx = PIPELINE_STAGES.findIndex((s) => s.key === stage);
  return idx === -1 ? 0 : idx;
}

export function PipelineTracker({ currentStage, isRunning }: PipelineTrackerProps) {
  const activeIdx = stageProgressIndex(currentStage);
  const allDone = currentStage === PipelineStage.Done;

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="mb-4 flex items-start justify-between gap-2">
        <div>
          <h2 className="text-sm font-semibold text-bank-navy">Campaign progress</h2>
          <p className="mt-0.5 text-xs text-slate-500">
            BankIQ runs these steps automatically. Compliance cannot be skipped.
          </p>
        </div>
        <span
          className={`shrink-0 rounded-full px-2.5 py-1 text-xs font-medium ${
            isRunning
              ? "bg-amber-50 text-amber-800"
              : allDone
                ? "bg-emerald-50 text-emerald-800"
                : "bg-slate-100 text-slate-600"
          }`}
        >
          {isRunning ? "In progress" : allDone ? "Finished" : getStageLabel(currentStage)}
        </span>
      </div>

      <ol className="space-y-3">
        {PIPELINE_STAGES.map((stage, idx) => {
          const done = idx < activeIdx || allDone;
          const active = idx === activeIdx && isRunning;
          const upcoming = idx > activeIdx && !allDone;

          return (
            <li key={stage.key} className="flex gap-3">
              <div
                className={`mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-xs font-bold ${
                  done
                    ? "bg-emerald-500 text-white"
                    : active
                      ? "bg-bank-gold text-bank-navy ring-2 ring-bank-gold/30"
                      : "bg-slate-100 text-slate-400"
                }`}
              >
                {done ? "✓" : idx + 1}
              </div>
              <div className="min-w-0 flex-1">
                <p
                  className={`text-sm font-medium ${
                    active ? "text-bank-navy" : done ? "text-emerald-800" : "text-slate-700"
                  }`}
                >
                  {stage.label}
                </p>
                <p className={`text-xs ${upcoming ? "text-slate-400" : "text-slate-500"}`}>
                  {stage.description}
                </p>
              </div>
            </li>
          );
        })}
      </ol>
    </section>
  );
}
