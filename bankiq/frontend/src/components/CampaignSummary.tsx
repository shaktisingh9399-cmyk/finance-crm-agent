/** Campaign outreach summary — targeted, approved, rejected counts. */

interface CampaignSummaryProps {
  targeted: number;
  approved: number;
  rejected: number;
}

export function CampaignSummary({ targeted, approved, rejected }: CampaignSummaryProps) {
  return (
    <div className="grid grid-cols-3 gap-4">
      <SummaryCard label="Targeted" value={targeted} color="text-bank-navy" />
      <SummaryCard label="Approved" value={approved} color="text-emerald-600" />
      <SummaryCard label="Rejected" value={rejected} color="text-red-600" />
    </div>
  );
}

function SummaryCard({
  label,
  value,
  color,
}: {
  label: string;
  value: number;
  color: string;
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 text-center">
      <p className={`text-2xl font-bold ${color}`}>{value}</p>
      <p className="mt-1 text-xs uppercase tracking-wide text-slate-400">{label}</p>
    </div>
  );
}
