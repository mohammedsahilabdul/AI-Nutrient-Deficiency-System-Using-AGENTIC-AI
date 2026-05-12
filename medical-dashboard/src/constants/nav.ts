import {
  BarChart3,
  Brain,
  Calendar,
  FileText,
  ImagePlus,
  LayoutDashboard,
} from "lucide-react";
export const DASHBOARD_NAV = [
  { id: "overview" as const, label: "Overview", icon: LayoutDashboard },
  { id: "analysis" as const, label: "AI Analysis", icon: Brain },
  { id: "uploads" as const, label: "Imaging", icon: ImagePlus },
  { id: "reports" as const, label: "Reports", icon: FileText },
  { id: "appointments" as const, label: "Appointments", icon: Calendar },
  { id: "insights" as const, label: "Analytics", icon: BarChart3 },
] as const;

export type DashboardNavId = (typeof DASHBOARD_NAV)[number]["id"];
