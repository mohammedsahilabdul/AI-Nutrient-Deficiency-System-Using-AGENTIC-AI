import { type ReactNode } from "react";
import { cn } from "../../lib/cn";

type GlassCardProps = {
  children: ReactNode;
  className?: string;
  hover?: boolean;
  padding?: "sm" | "md" | "lg";
};

const pad = { sm: "p-4", md: "p-5", lg: "p-6" };

export function GlassCard({
  children,
  className,
  hover = true,
  padding = "md",
}: GlassCardProps) {
  return (
    <div
      className={cn(
        "glass rounded-2xl shadow-card ring-glow transition-all duration-300",
        pad[padding],
        hover && "hover:border-white/[0.12] hover:bg-white/[0.05] hover:shadow-glow",
        className
      )}
    >
      {children}
    </div>
  );
}
