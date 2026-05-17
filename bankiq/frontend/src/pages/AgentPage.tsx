/** Main workspace — campaign query, conversation, and live progress. */

import { ChatInput } from "@/components/ChatInput";
import { ConversationPanel } from "@/components/ConversationPanel";
import { PipelineTracker } from "@/components/PipelineTracker";
import { getStageLabel } from "@/constants/pipelineStages";
import { useAgent } from "@/hooks/useAgent";
import { usePipelineStore } from "@/store/pipelineStore";

export function AgentPage() {
  const { isRunning, sendQuery } = useAgent();
  const { currentStage, messages, stageHistory } = usePipelineStore();

  const handleExample = (text: string) => {
    void sendQuery(text);
  };

  const lastUpdate = stageHistory[stageHistory.length - 1];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-bank-navy">Campaign assistant</h1>
        <p className="mt-1 max-w-2xl text-sm text-slate-600">
          Describe who you want to reach. BankIQ searches your portfolio, checks compliance, and
          prepares outreach you can review before sending.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-5">
        <div className="space-y-6 lg:col-span-3">
          <ConversationPanel
            messages={messages}
            isRunning={isRunning}
            onExampleSelect={handleExample}
          />
          <ChatInput onSend={sendQuery} isLoading={isRunning} />
        </div>

        <aside className="space-y-4 lg:col-span-2">
          <PipelineTracker currentStage={currentStage} isRunning={isRunning} />

          <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <h3 className="text-sm font-semibold text-bank-navy">What you will get</h3>
            <ul className="mt-3 space-y-2 text-xs text-slate-600">
              <li className="flex gap-2">
                <span className="text-emerald-600">✓</span>
                Ranked list of customers in your portfolio
              </li>
              <li className="flex gap-2">
                <span className="text-emerald-600">✓</span>
                Compliance-approved contacts only
              </li>
              <li className="flex gap-2">
                <span className="text-emerald-600">✓</span>
                Draft WhatsApp messages (masked PII throughout)
              </li>
            </ul>
          </div>

          {lastUpdate && (
            <div className="rounded-lg bg-slate-100 px-4 py-3 text-xs text-slate-600">
              <span className="font-medium text-slate-800">Latest update: </span>
              {getStageLabel(lastUpdate.stage)} — {lastUpdate.status}
            </div>
          )}
        </aside>
      </div>
    </div>
  );
}
