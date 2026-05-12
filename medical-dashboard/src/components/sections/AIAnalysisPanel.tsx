import { Cpu, FileSearch, ShieldCheck } from "lucide-react";
import { GlassCard } from "../ui/GlassCard";

export function AIAnalysisPanel() {
  return (
    <GlassCard padding="lg" className="h-full">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-cyan-500/15 ring-1 ring-cyan-500/25">
              <Cpu className="h-4 w-4 text-cyan-400" strokeWidth={1.75} />
            </span>
            <h2 className="text-lg font-semibold tracking-tight text-white">AI analysis & reports</h2>
          </div>
          <p className="mt-1 max-w-xl text-sm leading-relaxed text-zinc-400">
            Multimodal fusion across imaging and structured intake. Models are versioned, audited, and
            aligned to clinical safety rails.
          </p>
        </div>
        <span className="rounded-full border border-emerald-500/25 bg-emerald-500/10 px-3 py-1 text-xs font-semibold text-emerald-400">
          Live · v2.4.1
        </span>
      </div>

      <div className="mt-6 grid gap-3 sm:grid-cols-3">
        {[
          { title: "Fusion engine", desc: "Eye · nails · tongue", pct: 94, color: "from-cyan-500 to-blue-500" },
          { title: "Report draft", desc: "Structured narrative", pct: 88, color: "from-blue-500 to-violet-500" },
          { title: "Safety review", desc: "Policy & contraindications", pct: 100, color: "from-violet-500 to-fuchsia-500" },
        ].map((row) => (
          <div
            key={row.title}
            className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-4 transition-colors hover:border-white/[0.1]"
          >
            <p className="text-xs font-medium uppercase tracking-wide text-zinc-500">{row.title}</p>
            <p className="mt-1 text-sm text-zinc-300">{row.desc}</p>
            <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-zinc-800">
              <div
                className={`h-full rounded-full bg-gradient-to-r ${row.color} transition-all duration-700`}
                style={{ width: `${row.pct}%` }}
              />
            </div>
            <p className="mt-2 text-right text-xs font-mono text-zinc-500">{row.pct}%</p>
          </div>
        ))}
      </div>

      <div className="mt-6 flex flex-wrap gap-3 border-t border-white/[0.06] pt-6">
        <button
          type="button"
          className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-cyan-600 to-blue-600 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-cyan-500/20 transition-all hover:brightness-110 active:scale-[0.98]"
        >
          <FileSearch className="h-4 w-4" strokeWidth={1.75} />
          Run full analysis
        </button>
        <button
          type="button"
          className="inline-flex items-center gap-2 rounded-xl border border-white/[0.1] bg-white/[0.04] px-4 py-2.5 text-sm font-medium text-zinc-200 transition-all hover:bg-white/[0.07]"
        >
          <ShieldCheck className="h-4 w-4 text-violet-400" strokeWidth={1.75} />
          View audit trail
        </button>
      </div>
    </GlassCard>
  );
}
