/** WhatsApp message preview with character count. */

const WHATSAPP_LIMIT = 4096;

interface MessagePreviewProps {
  message: string;
  customerLabel?: string;
}

export function MessagePreview({ message, customerLabel }: MessagePreviewProps) {
  const count = message.length;
  const overLimit = count > WHATSAPP_LIMIT;

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4">
      {customerLabel && (
        <p className="mb-2 text-xs font-medium uppercase tracking-wide text-slate-400">
          {customerLabel}
        </p>
      )}
      <p className="whitespace-pre-wrap text-sm text-slate-700">{message || "No message generated yet."}</p>
      <p className={`mt-2 text-right text-xs ${overLimit ? "text-red-600" : "text-slate-400"}`}>
        {count} / {WHATSAPP_LIMIT} chars
      </p>
    </div>
  );
}
