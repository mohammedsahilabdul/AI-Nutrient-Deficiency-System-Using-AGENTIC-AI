import { useEffect, useState } from "react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { GlassCard } from "../ui/GlassCard";
import { Loader2 } from "lucide-react";

const volume = [
  { d: "Mon", v: 42 },
  { d: "Tue", v: 55 },
  { d: "Wed", v: 48 },
  { d: "Thu", v: 72 },
  { d: "Fri", v: 65 },
  { d: "Sat", v: 38 },
  { d: "Sun", v: 44 },
];

const latency = [
  { name: "Fusion", ms: 820 },
  { name: "Report", ms: 540 },
  { name: "RAG", ms: 310 },
  { name: "Vision", ms: 1200 },
];

const tipStyle = {
  backgroundColor: "rgba(15, 15, 20, 0.92)",
  border: "1px solid rgba(255,255,255,0.08)",
  borderRadius: "10px",
  fontSize: "12px",
};

export function ChartsSection() {
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const t = setTimeout(() => setLoading(false), 900);
    return () => clearTimeout(t);
  }, []);

  return (
    <div className="grid gap-4 lg:grid-cols-5">
      <GlassCard className="relative min-h-[280px] overflow-hidden lg:col-span-3" padding="lg">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h3 className="text-sm font-semibold uppercase tracking-wider text-zinc-500">Throughput</h3>
            <p className="text-lg font-semibold text-white">Analysis volume</p>
          </div>
          {loading && (
            <span className="flex items-center gap-2 text-xs text-zinc-500">
              <Loader2 className="h-3.5 w-3.5 animate-spin text-cyan-400" />
              Syncing
            </span>
          )}
        </div>
        <div className={loading ? "pointer-events-none opacity-30 blur-[1px]" : "opacity-100 transition-opacity duration-500"}>
          <ResponsiveContainer width="100%" height={220}>
            <AreaChart data={volume} margin={{ top: 8, right: 8, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="fillVol" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#22d3ee" stopOpacity={0.35} />
                  <stop offset="100%" stopColor="#22d3ee" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="d" tick={{ fill: "#71717a", fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: "#71717a", fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={tipStyle} labelStyle={{ color: "#a1a1aa" }} />
              <Area type="monotone" dataKey="v" stroke="#22d3ee" strokeWidth={2} fill="url(#fillVol)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </GlassCard>

      <GlassCard className="min-h-[280px] lg:col-span-2" padding="lg">
        <h3 className="text-sm font-semibold uppercase tracking-wider text-zinc-500">Pipeline</h3>
        <p className="text-lg font-semibold text-white">Latency by stage</p>
        <div className="mt-4 h-[220px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={latency} layout="vertical" margin={{ left: 4, right: 16 }}>
              <defs>
                <linearGradient id="barGrad" x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0%" stopColor="#6366f1" />
                  <stop offset="100%" stopColor="#22d3ee" />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" horizontal={false} />
              <XAxis type="number" hide />
              <YAxis
                type="category"
                dataKey="name"
                width={56}
                tick={{ fill: "#a1a1aa", fontSize: 11 }}
                axisLine={false}
                tickLine={false}
              />
              <Tooltip contentStyle={tipStyle} formatter={(v: number) => [`${v} ms`, ""]} />
              <Bar dataKey="ms" radius={[0, 6, 6, 0]} fill="url(#barGrad)" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </GlassCard>
    </div>
  );
}
