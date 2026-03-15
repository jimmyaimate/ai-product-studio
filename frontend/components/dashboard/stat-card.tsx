import { cn } from "@/lib/utils";
import { Card } from "@/components/ui/card";
import type { LucideIcon } from "lucide-react";

interface StatCardProps {
  label: string;
  value: string | number;
  sub?: string;
  icon: LucideIcon;
  accent?: "green" | "purple";
  trend?: { value: string; up: boolean };
}

export function StatCard({ label, value, sub, icon: Icon, accent = "green", trend }: StatCardProps) {
  return (
    <Card className="relative overflow-hidden">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium text-text-muted uppercase tracking-wider">{label}</p>
          <p className={cn(
            "text-3xl font-bold mt-2",
            accent === "green" ? "text-accent" : "text-purple"
          )}>
            {value}
          </p>
          {sub && <p className="text-xs text-text-muted mt-1">{sub}</p>}
          {trend && (
            <p className={cn("text-xs font-medium mt-1.5", trend.up ? "text-accent" : "text-red-400")}>
              {trend.up ? "↑" : "↓"} {trend.value}
            </p>
          )}
        </div>
        <div className={cn(
          "w-10 h-10 rounded-xl flex items-center justify-center",
          accent === "green" ? "bg-tag-bg" : "bg-purple/10"
        )}>
          <Icon size={18} className={accent === "green" ? "text-accent" : "text-purple"} strokeWidth={1.8} />
        </div>
      </div>
      {/* Subtle glow bg */}
      <div className={cn(
        "absolute -bottom-4 -right-4 w-24 h-24 rounded-full blur-2xl opacity-10",
        accent === "green" ? "bg-accent" : "bg-purple"
      )} />
    </Card>
  );
}
