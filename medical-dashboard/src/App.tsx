import { useState } from "react";
import { Sidebar } from "./components/layout/Sidebar";
import { TopNav } from "./components/layout/TopNav";
import { DASHBOARD_NAV, type DashboardNavId } from "./constants/nav";
import { StatsRow } from "./components/sections/StatsRow";
import { AIAnalysisPanel } from "./components/sections/AIAnalysisPanel";
import { ImageUploadSection } from "./components/sections/ImageUploadSection";
import { ChartsSection } from "./components/sections/ChartsSection";
import { AppointmentSection } from "./components/sections/AppointmentSection";
import { ActivityTimeline } from "./components/sections/ActivityTimeline";
import { NotificationsPanel } from "./components/sections/NotificationsPanel";
import { DiagnosticResults } from "./components/sections/DiagnosticResults";
import { DownloadSection } from "./components/sections/DownloadSection";
import { ChatAssistant } from "./components/sections/ChatAssistant";

function scrollToSection(id: DashboardNavId) {
  const el = document.getElementById(`section-${id}`);
  el?.scrollIntoView({ behavior: "smooth", block: "start" });
}

export default function App() {
  const [active, setActive] = useState<DashboardNavId>("overview");

  const navigate = (id: DashboardNavId) => {
    setActive(id);
    scrollToSection(id);
  };

  return (
    <div className="flex min-h-screen">
      <Sidebar active={active} onSelect={navigate} />

      <div className="flex min-w-0 flex-1 flex-col lg:pl-0">
        <TopNav />

        <nav
          className="flex gap-2 overflow-x-auto border-b border-white/[0.06] bg-zinc-950/80 px-4 py-2 backdrop-blur-md lg:hidden"
          aria-label="Section navigation"
        >
          {DASHBOARD_NAV.map((item) => (
            <button
              key={item.id}
              type="button"
              onClick={() => navigate(item.id)}
              className={`shrink-0 rounded-full px-3 py-1.5 text-xs font-semibold transition-colors ${
                active === item.id
                  ? "bg-cyan-500/20 text-cyan-200 ring-1 ring-cyan-500/30"
                  : "bg-white/[0.04] text-zinc-400 hover:bg-white/[0.08]"
              }`}
            >
              {item.label}
            </button>
          ))}
        </nav>

        <main className="flex-1 overflow-y-auto px-4 pb-16 pt-2 sm:px-6 lg:px-10">
          <div className="mx-auto max-w-[1600px]">
            <div className="mb-8 mt-4 animate-fade-in opacity-0 lg:mt-6">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-cyan-500/90">Command center</p>
              <h1 className="mt-2 text-3xl font-semibold tracking-tight text-white sm:text-4xl">
                Intelligence for{" "}
                <span className="text-gradient">precision care</span>
              </h1>
              <p className="mt-3 max-w-2xl text-base leading-relaxed text-zinc-400">
                Unified diagnostics, operational analytics, and AI copilots — engineered for regulated
                healthcare environments.
              </p>
            </div>

            <div className="grid gap-6 xl:grid-cols-[1fr_360px]">
              <div className="min-w-0 space-y-6">
                <section id="section-overview" className="scroll-mt-28 space-y-6">
                  <StatsRow />
                </section>

                <section id="section-analysis" className="scroll-mt-28 space-y-6">
                  <AIAnalysisPanel />
                  <DiagnosticResults />
                </section>

                <section id="section-uploads" className="scroll-mt-28">
                  <ImageUploadSection />
                </section>

                <section id="section-reports" className="scroll-mt-28">
                  <DownloadSection />
                </section>

                <section id="section-appointments" className="scroll-mt-28">
                  <AppointmentSection />
                </section>

                <section id="section-insights" className="scroll-mt-28">
                  <ChartsSection />
                </section>
              </div>

              <aside className="flex min-w-0 flex-col gap-6 xl:sticky xl:top-24 xl:self-start">
                <NotificationsPanel />
                <ActivityTimeline />
                <ChatAssistant />
              </aside>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
