import { cn } from "@/lib/utils";

interface BadgeProps {
  children: React.ReactNode;
  variant?: "default" | "accent" | "purple" | "muted";
  className?: string;
}

export function Badge({ children, variant = "default", className }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium border",
        {
          "bg-surface-raised text-text-secondary border-border": variant === "default",
          "bg-tag-bg text-accent border-accent/30": variant === "accent",
          "bg-purple/10 text-purple border-purple/30": variant === "purple",
          "bg-surface text-text-muted border-border": variant === "muted",
        },
        className
      )}
    >
      {children}
    </span>
  );
}
