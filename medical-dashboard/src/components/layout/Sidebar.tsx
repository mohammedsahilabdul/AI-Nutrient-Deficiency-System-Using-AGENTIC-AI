import { Activity, Home, Settings, Upload } from "lucide-react";
import { DASHBOARD_NAV, type DashboardNavId } from "../../constants/nav";
import { cn } from "../../lib/cn";

type SidebarProps = {
  active: DashboardNavId;
  onSelect: (id: DashboardNavId) => void;
};

export function Sidebar({ active, onSelect }: SidebarProps) {
  return (
    <aside className="sticky top-0 z-40 hidden h-screen w-[260px] shrink-0 flex-col border-r border-white/[0.06] bg-zinc-950/90 backdrop-blur-2xl lg:flex">
      <div className="flex items-center gap-3 border-b border-white/[0.06] px-5 py-6">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-cyan-500/20 to-violet-600/30 ring-1 ring-white/10">
          <Activity className="h-5 w-5 text-cyan-400" strokeWidth={2} />
        </div>
        <div>
          <p className="text-xs font-medium uppercase tracking-widest text-zinc-500">Clinical AI</p>
          <p className="font-semibold text-zinc-100">MedIntel</p>
        </div>
      </div>

      <nav className="flex flex-1 flex-col gap-1 p-3">
        <p className="px-3 pb-2 pt-4 text-[11px] font-semibold uppercase tracking-wider text-zinc-500">
          Workspace
        </p>
        {DASHBOARD_NAV.map((item) => {
          const Icon = item.icon;
          const isActive = active === item.id;
          return (
            <button
              key={item.id}
              type="button"
              onClick={() => onSelect(item.id)}
              className={cn(
                "group flex items-center gap-3 rounded-xl px-3 py-2.5 text-left text-sm font-medium transition-all duration-200",
                isActive
                  ? "bg-gradient-to-r from-cyan-500/15 to-violet-500/10 text-white shadow-glow ring-1 ring-cyan-500/20"
                  : "text-zinc-400 hover:bg-white/[0.04] hover:text-zinc-200"
              )}
            >
              <Icon
                className={cn(
                  "h-[18px] w-[18px] shrink-0 transition-colors",
                  isActive ? "text-cyan-400" : "text-zinc-500 group-hover:text-zinc-300"
                )}
                strokeWidth={1.75}
              />
              {item.label}
              {isActive && (
                <span className="ml-auto h-1.5 w-1.5 rounded-full bg-cyan-400 shadow-[0_0_8px_rgba(34,211,238,0.8)]" />
              )}
            </button>
          );
        })}

        <div className="mt-auto border-t border-white/[0.06] pt-3">
          <button
            type="button"
            className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-zinc-400 transition-colors hover:bg-white/[0.04] hover:text-zinc-200"
          >
            <Home className="h-[18px] w-[18px]" strokeWidth={1.75} />
            Home portal
          </button>
          <button
            type="button"
            className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-zinc-400 transition-colors hover:bg-white/[0.04] hover:text-zinc-200"
          >
            <Upload className="h-[18px] w-[18px]" strokeWidth={1.75} />
            Data import
          </button>
          <button
            type="button"
            className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-zinc-400 transition-colors hover:bg-white/[0.04] hover:text-zinc-200"
          >
            <Settings className="h-[18px] w-[18px]" strokeWidth={1.75} />
            Settings
          </button>
        </div>
      </nav>
    </aside>
  );
}