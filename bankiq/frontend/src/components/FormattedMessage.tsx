
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
  const lines = content.split("\n");

  return (
    <div className="space-y-2 text-sm leading-relaxed text-slate-800">
      {lines.map((line, idx) => {
        const trimmed = line.trim();

        if (!trimmed) {
          return <div key={idx} className="h-2" />;
        }

        // Handle tool step headers (e.g. "Search_customers", "get_transaction_history", etc.)
        const normalized = trimmed.toLowerCase().replace(/\s+/g, "_").replace(/\*/g, "");
        if (STEP_LABELS[normalized]) {
          const cleanLabel = STEP_LABELS[normalized];
          return (
            <h3
              key={idx}
              className="mt-5 mb-2 flex items-center gap-2 rounded-lg bg-amber-50/75 px-3 py-2 font-bold text-bank-navy border-l-4 border-bank-gold shadow-sm"
            >
              <span className="h-2 w-2 rounded-full bg-bank-gold animate-pulse" />
              {cleanLabel}
            </h3>
          );
        }

        // Handle step headers: "**Step X: ...**"
        const isStepHeader = trimmed.startsWith("**Step ") && trimmed.endsWith("**");
        if (isStepHeader) {
          const stepText = trimmed.replace(/\*\*/g, "");
          return (
            <h3
              key={idx}
              className="mt-4 mb-2 flex items-center gap-2 rounded-lg bg-amber-50/60 px-3 py-2 font-bold text-bank-navy border-l-4 border-bank-gold"
            >
              <span className="h-2 w-2 rounded-full bg-bank-gold" />
              {stepText}
            </h3>
          );
        }

        // Handle full bold lines: "**Text**"
        const isBoldLine = trimmed.startsWith("**") && trimmed.endsWith("**");
        if (isBoldLine) {
          const boldText = trimmed.replace(/\*\*/g, "");
          return (
            <p key={idx} className="font-bold text-bank-navy mt-3 mb-1">
              {boldText}
            </p>
          );
        }

        // Handle bullet lists: "* item" or "- item"
        if (trimmed.startsWith("* ") || trimmed.startsWith("- ")) {
          const text = trimmed.substring(2);
          return (
            <li key={idx} className="ml-3 flex items-start gap-2 list-none text-slate-700">
              <span className="text-bank-gold select-none font-bold">•</span>
              <span>{renderInlineBold(text)}</span>
            </li>
          );
        }

        // Handle numbered lists: "1. item" or "1: item"
        const numListMatch = trimmed.match(/^(\d+[\.\:])\s+(.*)$/);
        if (numListMatch) {
          const [, num, text] = numListMatch;
          return (
            <div key={idx} className="ml-3 flex items-start gap-2 text-slate-700">
              <span className="font-bold text-bank-navy min-w-[18px]">{num}</span>
              <span>{renderInlineBold(text)}</span>
            </div>
          );
        }

        // Normal paragraph with inline bolding
        return (
          <p key={idx} className="text-slate-700">
            {renderInlineBold(trimmed)}
          </p>
        );
      })}
    </div>
  );
}

function renderInlineBold(text: string) {
  const parts = text.split(/\*\*([^*]+)\*\*/g);
  return parts.map((part, index) => {
    if (index % 2 === 1) {
      return (
        <strong key={index} className="font-bold text-bank-navy">
          {part}
        </strong>
      );
    }
    return part;
  });
}
