/** Masked customer info card with score badge and tier indicator. */

import type { Customer } from "@/types/api";

interface CustomerCardProps {
  customer: Customer;
  score?: number;
}

function tierFromScore(score: number): { label: string; className: string } {
  if (score >= 75) return { label: "HIGH", className: "bg-emerald-100 text-emerald-800" };
  if (score >= 50) return { label: "MEDIUM", className: "bg-amber-100 text-amber-800" };
  return { label: "LOW", className: "bg-slate-100 text-slate-600" };
}

export function CustomerCard({ customer, score }: CustomerCardProps) {
  const tier = score !== undefined ? tierFromScore(score) : null;

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <div className="flex items-start justify-between">
        <div>
          <p className="font-semibold text-bank-navy">{customer.name}</p>
          <p className="text-xs text-slate-500">{customer.email}</p>
        </div>
        {tier && (
          <span className={`rounded-full px-2 py-0.5 text-xs font-bold ${tier.className}`}>
            {tier.label}
          </span>
        )}
      </div>
      <dl className="mt-3 grid grid-cols-2 gap-2 text-xs text-slate-600">
        <div>
          <dt className="text-slate-400">CIBIL</dt>
          <dd className="font-medium">{customer.credit_score}</dd>
        </div>
        <div>
          <dt className="text-slate-400">Income</dt>
          <dd className="font-medium">₹{customer.annual_income}</dd>
        </div>
        <div>
          <dt className="text-slate-400">EMI Ratio</dt>
          <dd className="font-medium">{customer.emi_ratio}</dd>
        </div>
        {score !== undefined && (
          <div>
            <dt className="text-slate-400">Score</dt>
            <dd className="font-medium text-bank-gold">{score.toFixed(1)}</dd>
          </div>
        )}
      </dl>
    </div>
  );
}
