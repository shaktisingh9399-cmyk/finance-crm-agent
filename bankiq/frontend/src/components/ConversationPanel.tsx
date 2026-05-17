/** Chat-style conversation area with welcome state and message bubbles. */

import { FormattedMessage } from "@/components/FormattedMessage";
import { EXAMPLE_PROMPTS } from "@/constants/pipelineStages";
import { AgentMessageRole, type AgentMessage } from "@/types/agent";

interface ConversationPanelProps {
  messages: AgentMessage[];
  isRunning: boolean;
  onExampleSelect: (text: string) => void;
}

export function ConversationPanel({
  messages,
  isRunning,
  onExampleSelect,
}: ConversationPanelProps) {
  if (messages.length === 0) {
    return (
      <section className="rounded-xl border border-dashed border-slate-300 bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-bank-navy">Start a new campaign analysis</h2>
        <p className="mt-2 max-w-xl text-sm leading-relaxed text-slate-600">
          Tell BankIQ what you want to achieve. It will search your portfolio, score leads, run
          compliance checks, and draft outreach — only on customers you are allowed to contact.
        </p>

        <div className="mt-6">
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
            Try one of these examples
          </p>
          <ul className="mt-3 grid gap-3 sm:grid-cols-1">
            {EXAMPLE_PROMPTS.map((example) => (
              <li key={example.title}>
                <button
                  type="button"
                  disabled={isRunning}
                  onClick={() => onExampleSelect(example.text)}
                  className="w-full rounded-lg border border-slate-200 bg-slate-50 p-4 text-left transition hover:border-bank-gold hover:bg-amber-50/50 disabled:opacity-50"
                >
                  <p className="text-sm font-medium text-bank-navy">{example.title}</p>
                  <p className="mt-1 line-clamp-2 text-xs text-slate-600">{example.text}</p>
                  <p className="mt-2 text-xs font-medium text-bank-gold">Use this example →</p>
                </button>
              </li>
            ))}
          </ul>
        </div>

        <div className="mt-6 flex items-start gap-2 rounded-lg bg-blue-50 p-3 text-xs text-blue-900">
          <span className="font-bold" aria-hidden>
            i
          </span>
          <p>
            Customer names and contact details are always masked. Compliance (KYC, consent, and
            do-not-contact) runs before any message is prepared.
          </p>
        </div>
      </section>
    );
  }

  return (
    <section className="rounded-xl border border-slate-200 bg-white shadow-sm">
      <div className="border-b border-slate-100 px-4 py-3">
        <h2 className="text-sm font-semibold text-bank-navy">Your conversation</h2>
        <p className="text-xs text-slate-500">Questions you asked and updates from BankIQ</p>
      </div>
      <div className="max-h-[420px] space-y-4 overflow-y-auto p-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.role === AgentMessageRole.User ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                msg.role === AgentMessageRole.User
                  ? "bg-bank-navy text-white"
                  : "border border-slate-200 bg-slate-50 text-slate-800"
              }`}
            >
              {msg.role === AgentMessageRole.User && (
                <p className="mb-1 text-[10px] font-semibold uppercase tracking-wide text-bank-gold/90">
                  You asked
                </p>
              )}
              {msg.role === AgentMessageRole.Assistant && (
                <p className="mb-1 text-[10px] font-semibold uppercase tracking-wide text-slate-500">
                  BankIQ
                </p>
              )}
              {msg.role === AgentMessageRole.User ? (
                msg.content
              ) : (
                <FormattedMessage content={msg.content} />
              )}
            </div>
          </div>
        ))}
        {isRunning && (
          <div className="flex justify-start">
            <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-600">
              <span className="inline-flex items-center gap-2">
                <span className="h-2 w-2 animate-pulse rounded-full bg-bank-gold" />
                Analysing your portfolio…
              </span>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
