import { CalendarClock, MapPin, User } from "lucide-react";
import { GlassCard } from "../ui/GlassCard";

export function AppointmentSection() {
  return (
    <GlassCard padding="lg">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold text-white">Appointment management</h2>
          <p className="mt-1 text-sm text-zinc-500">Sync with calendars, send invites, and track confirmations.</p>
        </div>
        <button
          type="button"
          className="rounded-xl bg-white/[0.06] px-4 py-2 text-sm font-medium text-zinc-200 ring-1 ring-white/10 transition-all hover:bg-white/[0.1]"
        >
          New booking
        </button>
      </div>

      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <div className="space-y-3 rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
          <label className="text-xs font-semibold uppercase tracking-wide text-zinc-500">Physician</label>
          <div className="flex items-center gap-3 rounded-lg border border-white/[0.08] bg-zinc-900/50 px-3 py-2.5">
            <User className="h-4 w-4 text-zinc-500" />
            <span className="text-sm text-zinc-200">Dr. Neha Gupta · General Physician</span>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs font-semibold uppercase tracking-wide text-zinc-500">Date</label>
              <div className="mt-1 flex items-center gap-2 rounded-lg border border-white/[0.08] bg-zinc-900/50 px-3 py-2 text-sm text-zinc-200">
                <CalendarClock className="h-4 w-4 text-cyan-400/80" />
                May 14, 2026
              </div>
            </div>
            <div>
              <label className="text-xs font-semibold uppercase tracking-wide text-zinc-500">Time</label>
              <div className="mt-1 rounded-lg border border-white/[0.08] bg-zinc-900/50 px-3 py-2 text-sm text-zinc-200">
                09:30 AM
              </div>
            </div>
          </div>
          <div>
            <label className="text-xs font-semibold uppercase tracking-wide text-zinc-500">Location</label>
            <div className="mt-1 flex items-center gap-2 rounded-lg border border-white/[0.08] bg-zinc-900/50 px-3 py-2 text-sm text-zinc-300">
              <MapPin className="h-4 w-4 text-violet-400/90" />
              Delhi · Outpatient clinic
            </div>
          </div>
        </div>

        <div className="flex flex-col justify-between rounded-xl border border-white/[0.06] bg-gradient-to-br from-violet-500/10 via-transparent to-cyan-500/10 p-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500">Queue</p>
            <p className="mt-2 text-3xl font-semibold text-white">6</p>
            <p className="text-sm text-zinc-400">Pending confirmations today</p>
          </div>
          <div className="mt-6 space-y-2">
            {["ICS sent", "SMS reminder", "EMR sync"].map((step, i) => (
              <div
                key={step}
                className="flex items-center justify-between rounded-lg border border-white/[0.05] bg-black/20 px-3 py-2 text-xs text-zinc-400"
              >
                <span>{step}</span>
                <span className="font-mono text-emerald-400/90">{i < 2 ? "OK" : "—"}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </GlassCard>
  );
}
