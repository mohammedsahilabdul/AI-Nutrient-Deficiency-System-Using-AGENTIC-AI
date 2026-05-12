import { BellRing, Check, X } from "lucide-react";
import { GlassCard } from "../ui/GlassCard";

const notes = [
  {
    id: 1,
    title: "SLA: report due in 45m",
    body: "Priority queue · Cardiology consult",
    unread: true,
  },
  {
    id: 2,
    title: "New model weights available",
    body: "Vision encoder patch — review changelog",
    unread: true,
  },
  {
    id: 3,
    title: "Weekly compliance digest",
    body: "Zero policy violations · full log attached",
    unread: false,
  },
];

export function NotificationsPanel() {
  return (
    <GlassCard padding="lg" className="h-full">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <BellRing className="h-4 w-4 text-amber-400/90" strokeWidth={1.75} />
          <h3 className="text-lg font-semibold text-white">Notifications</h3>
        </div>
        <button type="button" className="text-xs font-medium text-cyan-400 hover:text-cyan-300">
          Mark all read
        </button>
      </div>
      <ul className="mt-4 space-y-2">
        {notes.map((n) => (
          <li
            key={n.id}
            className={`group rounded-xl border px-3 py-3 transition-all duration-200 ${
              n.unread
                ? "border-cyan-500/20 bg-cyan-500/[0.06] hover:border-cyan-500/35"
                : "border-white/[0.05] bg-white/[0.02] hover:border-white/[0.1]"
            }`}
          >
            <div className="flex items-start justify-between gap-2">
              <div>
                <p className="text-sm font-medium text-zinc-100">{n.title}</p>
                <p className="mt-0.5 text-xs leading-relaxed text-zinc-500">{n.body}</p>
              </div>
              {n.unread && <span className="mt-1 h-2 w-2 shrink-0 rounded-full bg-cyan-400" />}
            </div>
            <div className="mt-2 flex gap-2 opacity-0 transition-opacity group-hover:opacity-100">
              <button
                type="button"
                className="inline-flex items-center gap-1 rounded-md bg-white/[0.06] px-2 py-1 text-[11px] text-zinc-300 hover:bg-white/10"
              >
                <Check className="h-3 w-3" /> Ack
              </button>
              <button
                type="button"
                className="inline-flex items-center gap-1 rounded-md px-2 py-1 text-[11px] text-zinc-500 hover:text-zinc-300"
              >
                <X className="h-3 w-3" /> Dismiss
              </button>
            </div>
          </li>
        ))}
      </ul>
    </GlassCard>
  );
}
