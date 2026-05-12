import { ArrowDownRight, ArrowUpRight, Brain, Clock, Users } from "lucide-react";
import { GlassCard } from "../ui/GlassCard";
import { cn } from "../../lib/cn";

const stats = [
  {
    label: "Active cases",
    value: "128",
    change: "+12.4%",
    up: true,
    sub: "vs last week",
    icon: Users,
    accent: "from-cyan-500/20 to-blue-500/10",
  },
  {
    label: "AI analyses",
    value: "2,847",
    change: "+8.1%",
    up: true,
    sub: "sessions MTD",
    icon: Brain,
    accent: "from-violet-500/20 to-fuchsia-500/10",
  },
  {
    label: "Avg. turnaround",
    value: "4.2m",
    change: "-18%",
    up: true,
    sub: "time to insight",
    icon: Clock,
    accent: "from-blue-500/20 to-cyan-500/10",
  },
  {
    label: "Clinical accuracy",
    value: "97.2%",
    change: "+0.3%",
    up: true,
    sub: "benchmarked",
    icon: Brain,
    accent: "from-emerald-500/15 to-cyan-500/10",
  },
];

export function StatsRow() {
  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {stats.map((s, i) => {
        const Icon = s.icon;
        return (
          <GlassCard
            key={s.label}
            className={cn("animate-fade-in opacity-0", i === 1 && "delay-75", i === 2 && "delay-150", i === 3 && "delay-200")}
          >
            <div className="flex items-start justify-between gap-3">
              <div
                className={`rounded-xl bg-gradient-to-br ${s.accent} p-2.5 ring-1 ring-white/10`}
              >
                <Icon className="h-5 w-5 text-cyan-200/90" strokeWidth={1.75} />
              </div>
              <span
                className={`inline-flex items-center gap-0.5 rounded-full px-2 py-0.5 text-[11px] font-semibold ${
                  s.up ? "bg-emerald-500/15 text-emerald-400" : "bg-rose-500/15 text-rose-400"
                }`}
              >
                {s.up ? (
                  <ArrowUpRight className="h-3 w-3" />
                ) : (
                  <ArrowDownRight className="h-3 w-3" />
                )}
                {s.change}
              </span>
            </div>
            <p className="mt-4 text-2xl font-semibold tracking-tight text-white">{s.value}</p>
            <p className="text-sm font-medium text-zinc-400">{s.label}</p>
            <p className="mt-1 text-xs text-zinc-500">{s.sub}</p>
          </GlassCard>
        );
      })}
    </div>
  );
}
