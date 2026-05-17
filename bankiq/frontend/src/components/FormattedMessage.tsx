import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeRaw from "rehype-raw";
import { AgentToolName } from "@/types/agent";

const STEP_LABELS: Record<string, string> = {
  [AgentToolName.SearchCustomers]: "Search Customers",
  [AgentToolName.GetTransactionHistory]: "Get Transaction History",
  [AgentToolName.CalculateConversionScore]: "Calculate Conversion Score",
  [AgentToolName.CheckRegulatoryCompliance]: "Check Regulatory Compliance",
  [AgentToolName.GenerateMessages]: "Generate Messages",
  [AgentToolName.FinalizeResults]: "Finalize Results",
};

interface FormattedMessageProps {
  content: string;
}

export function FormattedMessage({ content }: FormattedMessageProps) {
  return (
    <div className="space-y-3 text-sm leading-relaxed text-slate-800 markdown-content w-full overflow-hidden">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeRaw]}
        components={{
          h3: ({ children }) => {
            const text = String(children || "");
            const normalized = text.toLowerCase().replace(/\s+/g, "_").replace(/\*/g, "");
            if (STEP_LABELS[normalized]) {
              return (
                <h3 className="mt-5 mb-2 flex items-center gap-2 rounded-lg bg-amber-50/75 px-3 py-2 font-bold text-bank-navy border-l-4 border-bank-gold shadow-sm">
                  <span className="h-2 w-2 rounded-full bg-bank-gold animate-pulse" />
                  {STEP_LABELS[normalized]}
                </h3>
              );
            }
            if (text.startsWith("Step ")) {
              return (
                <h3 className="mt-4 mb-2 flex items-center gap-2 rounded-lg bg-amber-50/60 px-3 py-2 font-bold text-bank-navy border-l-4 border-bank-gold">
                  <span className="h-2 w-2 rounded-full bg-bank-gold" />
                  {text}
                </h3>
              );
            }
            return <h3 className="mt-4 mb-2 font-bold text-bank-navy text-base">{children}</h3>;
          },
          h1: ({ children }) => <h1 className="mt-6 mb-3 font-bold text-bank-navy text-xl border-b pb-1">{children}</h1>,
          h2: ({ children }) => <h2 className="mt-5 mb-2 font-bold text-bank-navy text-lg">{children}</h2>,
          p: ({ children }) => <p className="mb-2 text-slate-700">{children}</p>,
          strong: ({ children }) => <strong className="font-bold text-bank-navy">{children}</strong>,
          ul: ({ children }) => <ul className="space-y-1 my-2 pl-4 list-disc text-slate-700">{children}</ul>,
          ol: ({ children }) => <ol className="space-y-1 my-2 pl-4 list-decimal text-slate-700">{children}</ol>,
          li: ({ children }) => <li className="text-slate-700">{children}</li>,
          blockquote: ({ children }) => (
            <blockquote className="my-3 border-l-4 border-slate-300 pl-3 italic text-slate-600">
              {children}
            </blockquote>
          ),
          code: ({ children }) => (
            <code className="rounded bg-slate-100 px-1 py-0.5 font-mono text-xs text-rose-600">
              {children}
            </code>
          ),
          table: ({ children }) => (
            <div className="my-4 w-full overflow-x-auto rounded-xl border border-slate-200 shadow-md">
              <table className="min-w-full divide-y divide-slate-200 text-[11px] text-left">
                {children}
              </table>
            </div>
          ),
          thead: ({ children }) => (
            <thead className="bg-[#0f172a] text-slate-100 uppercase tracking-wider text-[9px] font-semibold">
              {children}
            </thead>
          ),
          tbody: ({ children }) => <tbody className="divide-y divide-slate-100 bg-white">{children}</tbody>,
          tr: ({ children }) => <tr className="hover:bg-slate-50/70 transition-colors border-b border-slate-100">{children}</tr>,
          th: ({ children }) => <th className="px-3 py-2.5 font-bold">{children}</th>,
          td: ({ children }) => (
            <td className="px-3 py-2 text-slate-700 font-medium whitespace-normal max-w-[200px] break-words align-middle">
              {children}
            </td>
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
