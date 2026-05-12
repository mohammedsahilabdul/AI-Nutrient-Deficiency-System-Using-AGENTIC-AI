import { Bell, ChevronDown, Search, Sparkles } from "lucide-react";

export function TopNav() {
  return (
    <header className="sticky top-0 z-30 flex flex-col gap-4 border-b border-white/[0.06] bg-zinc-950/70 px-4 py-4 backdrop-blur-xl sm:flex-row sm:items-center sm:justify-between sm:px-6 lg:px-8">
      <div className="relative max-w-xl flex-1">
        <Search className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-zinc-500" />
        <input
          type="search"
          placeholder="Search patients, studies, reports…"
          className="w-full rounded-xl border border-white/[0.08] bg-white/[0.04] py-2.5 pl-10 pr-4 text-sm text-zinc-100 placeholder:text-zinc-500 outline-none ring-0 transition-all focus:border-cyan-500/40 focus:bg-white/[0.06] focus:shadow-[0_0_0_3px_rgba(34,211,238,0.12)]"
        />
      </div>

      <div className="flex items-center justify-end gap-2 sm:gap-3">
        <button
          type="button"
          className="hidden items-center gap-2 rounded-xl border border-white/[0.08] bg-white/[0.03] px-3 py-2 text-xs font-medium text-zinc-300 transition-all hover:border-violet-500/30 hover:bg-violet-500/10 sm:flex"
        >
          <Sparkles className="h-3.5 w-3.5 text-violet-400" />
          Ask AI
        </button>

        <button
          type="button"
          className="relative flex h-10 w-10 items-center justify-center rounded-xl border border-white/[0.08] bg-white/[0.03] text-zinc-400 transition-all hover:border-cyan-500/30 hover:text-cyan-300"
          aria-label="Notifications"
        >
          <Bell className="h-[18px] w-[18px]" strokeWidth={1.75} />
          <span className="absolute right-2 top-2 h-2 w-2 rounded-full bg-cyan-400 ring-2 ring-zinc-950" />
        </button>

        <button
          type="button"
          className="flex items-center gap-2 rounded-xl border border-white/[0.08] bg-white/[0.04] py-1.5 pl-1.5 pr-3 transition-all hover:border-white/[0.12] hover:bg-white/[0.06]"
        >
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-violet-600 text-xs font-bold text-white">
            MS
          </div>
          <div className="hidden text-left sm:block">
            <p className="text-xs font-semibold text-zinc-100">Dr. Sahil</p>
            <p className="text-[10px] text-zinc-500">Attending · AI Lab</p>
          </div>
          <ChevronDown className="hidden h-4 w-4 text-zinc-500 sm:block" />
        </button>
      </div>
    </header>
  );
}
