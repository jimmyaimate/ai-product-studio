import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatTokens(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}k`;
  return n.toString();
}

export function formatDate(iso: string): string {
  return new Intl.DateTimeFormat("en-GB", {
    day: "2-digit", month: "short", year: "numeric",
    hour: "2-digit", minute: "2-digit",
  }).format(new Date(iso));
}

export function statusColor(status: string): string {
  switch (status) {
    case "completed": return "text-accent";
    case "running":
    case "started": return "text-purple";
    case "failed": return "text-red-400";
    default: return "text-text-secondary";
  }
}

export function statusBg(status: string): string {
  switch (status) {
    case "completed": return "bg-tag-bg text-accent border-accent/30";
    case "running":
    case "started": return "bg-purple/10 text-purple border-purple/30";
    case "failed": return "bg-red-900/20 text-red-400 border-red-400/30";
    default: return "bg-surface-raised text-text-secondary border-border";
  }
}
