import { AlertTriangle, HeartPulse, Microscope, Stethoscope } from "lucide-react";
import { GlassCard } from "../ui/GlassCard";

const cards = [
  {
    title: "Primary impression",
    value: "Moderate systemic stress pattern",
    detail: "Correlated with nail bed and ocular micro-vascular signals.",
    icon: Stethoscope,
    border: "border-cyan-500/20",
    glow: "shadow-[inset_0_0_0_1px_rgba(34,211,238,0.12)]",
  },
  {
    title: "Severity index",
    value: "Moderate",
    detail: "Within expected variance for outpatient triage.",
    icon: HeartPulse,
    border: "border-violet-500/20",
    glow: "shadow-[inset_0_0_0_1px_rgba(139,92,246,0.12)]",
  },
  {
    title: "Differential (AI)",
    value: "3 candidates",
    detail: "Ranked by multimodal confidence and guideline fit.",
    icon: Microscope,
    border: "border-blue-500/20",
    glow: "shadow-[inset_0_0_0_1px_rgba(59,130,246,0.12)]",
  },
];

export function DiagnosticResults() {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <AlertTriangle className="h-4 w-4 text-amber-400/90" strokeWidth={1.75} />
        <p className="text-xs font-medium text-amber-200/80">
          Decision support only — all outputs require licensed clinician review.
        </p>
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        {cards.map((c) => {
          const Icon = c.icon;
          return (
            <GlassCard
              key={c.title}
              className={`border ${c.border} ${c.glow}`}
              padding="md"
            >
              <div className="flex items-center gap-2 text-zinc-500">
                <Icon className="h-4 w-4 text-cyan-400/80" strokeWidth={1.75} />
                <span className="text-xs font-semibold uppercase tracking-wide">{c.title}</span>
              </div>
              <p className="mt-3 text-lg font-semibold leading-snug text-white">{c.value}</p>
              <p className="mt-2 text-sm leading-relaxed text-zinc-400">{c.detail}</p>
            </GlassCard>
          );
        })}
      </div>
    </div>
  );
}
