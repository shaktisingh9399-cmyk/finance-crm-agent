/** RM query input — labelled textarea with clear call to action. */

import { FormEvent, useState } from "react";

interface ChatInputProps {
  onSend: (query: string) => void;
  isLoading: boolean;
}

export function ChatInput({ onSend, isLoading }: ChatInputProps) {
  const [text, setText] = useState("");

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    const trimmed = text.trim();
    if (!trimmed || isLoading) return;
    onSend(trimmed);
    setText("");
  };

  return (
    <form onSubmit={handleSubmit} className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <label htmlFor="rm-query" className="block text-sm font-medium text-bank-navy">
        Describe your campaign goal
      </label>
      <p className="mt-1 text-xs text-slate-500">
        Use everyday language — include product, filters (income, CIBIL, EMI), and channel if needed.
      </p>
      <textarea
        id="rm-query"
        rows={3}
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Example: Find customers in my portfolio who qualify for a personal loan this month…"
        maxLength={4000}
        disabled={isLoading}
        className="mt-3 w-full resize-none rounded-lg border border-slate-300 px-4 py-3 text-sm text-slate-800 placeholder:text-slate-400 focus:border-bank-gold focus:outline-none focus:ring-2 focus:ring-bank-gold/20 disabled:bg-slate-50"
      />
      <div className="mt-3 flex items-center justify-between gap-3">
        <span className="text-xs text-slate-400">{text.length} / 4,000 characters</span>
        <button
          type="submit"
          disabled={isLoading || !text.trim()}
          className="rounded-lg bg-bank-navy px-5 py-2.5 text-sm font-semibold text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isLoading ? "BankIQ is working…" : "Start campaign analysis"}
        </button>
      </div>
    </form>
  );
}
