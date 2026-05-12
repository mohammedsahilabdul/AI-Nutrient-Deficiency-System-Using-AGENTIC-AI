import { Camera, CheckCircle2, ImageIcon, UploadCloud } from "lucide-react";
import { GlassCard } from "../ui/GlassCard";

const slots = [
  { id: "eye", label: "Ocular", status: "ready", hint: "JPEG / PNG · max 10MB" },
  { id: "nails", label: "Dermatologic", status: "pending", hint: "Well-lit, steady hand" },
  { id: "tongue", label: "Oral", status: "pending", hint: "Natural light preferred" },
] as const;

export function ImageUploadSection() {
  return (
    <GlassCard padding="lg">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-violet-500/15 ring-1 ring-violet-500/25">
            <Camera className="h-5 w-5 text-violet-300" strokeWidth={1.75} />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-white">Clinical imaging</h2>
            <p className="text-sm text-zinc-500">Drag-and-drop or browse — encrypted in transit</p>
          </div>
        </div>
        <button
          type="button"
          className="inline-flex items-center gap-2 rounded-xl border border-cyan-500/30 bg-cyan-500/10 px-4 py-2 text-sm font-semibold text-cyan-200 transition-all hover:bg-cyan-500/20"
        >
          <UploadCloud className="h-4 w-4" />
          Bulk upload
        </button>
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-3">
        {slots.map((slot) => (
          <div
            key={slot.id}
            className="group relative flex min-h-[160px] cursor-pointer flex-col items-center justify-center rounded-2xl border border-dashed border-white/[0.12] bg-gradient-to-b from-white/[0.04] to-transparent px-4 py-8 text-center transition-all duration-300 hover:border-cyan-500/35 hover:from-cyan-500/5 hover:shadow-glow"
          >
            <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-white/[0.06] ring-1 ring-white/10 transition-transform group-hover:scale-105">
              <ImageIcon className="h-6 w-6 text-zinc-400 group-hover:text-cyan-300" strokeWidth={1.5} />
            </div>
            <p className="font-medium text-zinc-200">{slot.label}</p>
            <p className="mt-1 text-xs text-zinc-500">{slot.hint}</p>
            {slot.status === "ready" ? (
              <span className="mt-4 inline-flex items-center gap-1 text-xs font-medium text-emerald-400">
                <CheckCircle2 className="h-3.5 w-3.5" />
                Sample loaded
              </span>
            ) : (
              <span className="mt-4 text-xs text-zinc-600">Awaiting upload</span>
            )}
          </div>
        ))}
      </div>
    </GlassCard>
  );
}
