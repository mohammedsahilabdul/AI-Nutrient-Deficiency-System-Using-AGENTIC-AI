import { Download, FileJson, FileText, Table } from "lucide-react";
import { GlassCard } from "../ui/GlassCard";

const files = [
  { name: "Clinical_report_v3.pdf", size: "842 KB", icon: FileText, hot: true },
  { name: "Diet_protocol.pdf", size: "312 KB", icon: FileText, hot: false },
  { name: "Structured_findings.json", size: "48 KB", icon: FileJson, hot: false },
  { name: "Billing_codes.csv", size: "12 KB", icon: Table, hot: false },
];

export function DownloadSection() {
  return (
    <GlassCard padding="lg">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h3 className="text-lg font-semibold text-white">Exports & downloads</h3>
          <p className="text-sm text-zinc-500">Immutable versions with checksums for audit.</p>
        </div>
        <button
          type="button"
          className="inline-flex items-center gap-2 rounded-xl border border-white/[0.1] bg-white/[0.05] px-4 py-2 text-sm font-medium text-zinc-200 transition-all hover:border-cyan-500/30 hover:text-white"
        >
          <Download className="h-4 w-4" />
          Bundle all
        </button>
      </div>
      <ul className="mt-5 divide-y divide-white/[0.06] rounded-xl border border-white/[0.06] bg-black/20">
        {files.map((f) => {
          const Icon = f.icon;
          return (
            <li
              key={f.name}
              className="flex items-center justify-between gap-4 px-4 py-3 transition-colors hover:bg-white/[0.03]"
            >
              <div className="flex min-w-0 items-center gap-3">
                <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-white/[0.06] ring-1 ring-white/10">
                  <Icon className="h-4 w-4 text-zinc-400" strokeWidth={1.75} />
                </span>
                <div className="min-w-0">
                  <p className="truncate text-sm font-medium text-zinc-100">{f.name}</p>
                  <p className="text-xs text-zinc-500">{f.size}</p>
                </div>
              </div>
              <button
                type="button"
                className={`shrink-0 rounded-lg px-3 py-1.5 text-xs font-semibold transition-all ${
                  f.hot
                    ? "bg-gradient-to-r from-cyan-600 to-blue-600 text-white shadow-lg shadow-cyan-500/20 hover:brightness-110"
                    : "border border-white/[0.08] bg-white/[0.04] text-zinc-300 hover:bg-white/[0.08]"
                }`}
              >
                Download
              </button>
            </li>
          );
        })}
      </ul>
    </GlassCard>
  );
}
