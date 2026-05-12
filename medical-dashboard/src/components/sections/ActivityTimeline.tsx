import { GlassCard } from "../ui/GlassCard";

const items = [
  { t: "09:42", title: "Multimodal analysis completed", meta: "Case #MED-2847 · High confidence", tone: "cyan" },
  { t: "09:18", title: "Report exported to PDF", meta: "Dr. Sahil · Version locked", tone: "violet" },
  { t: "08:55", title: "New intake submitted", meta: "Bangalore · 3 images attached", tone: "zinc" },
  { t: "08:30", title: "Model v2.4.1 promoted", meta: "Staging → Production", tone: "emerald" },
] as const;

export function ActivityTimeline() {
  return (
    <GlassCard padding="lg" className="h-full">
      <h3 className="text-sm font-semibold uppercase tracking-wider text-zinc-500">Activity</h3>
      <p className="text-lg font-semibold text-white">Recent timeline</p>
      <ul className="relative mt-5 space-y-0 border-l border-white/[0.08] pl-5">
        {items.map((item) => (
          <li key={item.title} className="relative pb-6 last:pb-0">
            <span
              className={`absolute -left-[21px] top-1.5 h-2.5 w-2.5 rounded-full border-2 border-zinc-950 ${
                item.tone === "cyan"
                  ? "bg-cyan-400 shadow-[0_0_10px_rgba(34,211,238,0.5)]"
                  : item.tone === "violet"
                    ? "bg-violet-400 shadow-[0_0_10px_rgba(167,139,250,0.4)]"
                    : item.tone === "emerald"
                      ? "bg-emerald-400"
                      : "bg-zinc-500"
              }`}
            />
            <time className="font-mono text-[11px] text-zinc-500">{item.t}</time>
            <p className="mt-0.5 text-sm font-medium text-zinc-100">{item.title}</p>
            <p className="text-xs text-zinc-500">{item.meta}</p>
          </li>
        ))}
      </ul>
    </GlassCard>
  );
}
