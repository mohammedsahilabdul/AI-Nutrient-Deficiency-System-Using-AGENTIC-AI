import { useState } from "react";
import { CornerDownLeft, Sparkles } from "lucide-react";
import { GlassCard } from "../ui/GlassCard";

const suggestions = [
  "Summarize differential for this case",
  "Draft patient-friendly explanation",
  "List red-flag symptoms to monitor",
];

export function ChatAssistant() {
  const [input, setInput] = useState("");

  return (
    <GlassCard padding="lg" className="flex h-full min-h-[420px] flex-col">
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-violet-500/30 to-cyan-500/20 ring-1 ring-white/10">
            <Sparkles className="h-4 w-4 text-violet-200" strokeWidth={1.75} />
          </div>
          <div>
            <h3 className="font-semibold text-white">Clinical copilot</h3>
            <p className="text-xs text-zinc-500">Grounded on your workspace context</p>
          </div>
        </div>
        <span className="rounded-full bg-emerald-500/15 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide text-emerald-400">
          Online
        </span>
      </div>

      <div className="mt-4 flex-1 space-y-3 overflow-y-auto rounded-xl border border-white/[0.06] bg-black/25 p-4">
        <div className="flex gap-3">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-zinc-800 text-xs font-bold text-zinc-400">
            AI
          </div>
          <div className="rounded-2xl rounded-tl-sm border border-white/[0.08] bg-white/[0.04] px-4 py-3 text-sm leading-relaxed text-zinc-300">
            Good morning. I can help interpret the latest imaging run, compare against prior baselines, or
            prep handoff notes for your care team.
          </div>
        </div>
        <div className="flex flex-row-reverse gap-3">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-blue-600 to-violet-600 text-xs font-bold text-white">
            You
          </div>
          <div className="rounded-2xl rounded-tr-sm border border-cyan-500/20 bg-cyan-500/10 px-4 py-3 text-sm text-cyan-50">
            Highlight the top three findings I should discuss with the patient.
          </div>
        </div>
        <div className="flex gap-3">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-zinc-800 text-xs font-bold text-zinc-400">
            AI
          </div>
          <div className="rounded-2xl rounded-tl-sm border border-white/[0.08] bg-white/[0.04] px-4 py-3 text-sm leading-relaxed text-zinc-300">
            1) Microvascular stress pattern consistent with intake vitals. 2) Nail morphology suggests mild
            iron-load variance — correlate with labs. 3) Ocular surface clear; no acute red-flag markers in
            this capture.
          </div>
        </div>
      </div>

      <div className="mt-3 flex flex-wrap gap-2">
        {suggestions.map((s) => (
          <button
            key={s}
            type="button"
            onClick={() => setInput(s)}
            className="rounded-full border border-white/[0.08] bg-white/[0.03] px-3 py-1.5 text-xs text-zinc-400 transition-all hover:border-violet-500/30 hover:text-zinc-200"
          >
            {s}
          </button>
        ))}
      </div>

      <div className="mt-3 flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask anything about this dashboard context…"
          className="min-w-0 flex-1 rounded-xl border border-white/[0.1] bg-zinc-900/80 px-4 py-3 text-sm text-zinc-100 placeholder:text-zinc-600 outline-none transition-all focus:border-cyan-500/40 focus:ring-2 focus:ring-cyan-500/20"
        />
        <button
          type="button"
          className="inline-flex shrink-0 items-center justify-center rounded-xl bg-gradient-to-r from-violet-600 to-cyan-600 px-4 text-white shadow-lg shadow-violet-500/25 transition-all hover:brightness-110 active:scale-[0.98]"
          aria-label="Send"
        >
          <CornerDownLeft className="h-5 w-5" strokeWidth={1.75} />
        </button>
      </div>
    </GlassCard>
  );
}
