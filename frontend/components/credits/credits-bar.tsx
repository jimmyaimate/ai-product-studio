"use client";

import { cn, formatTokens } from "@/lib/utils";

interface CreditsBarProps {
  tokensUsed: number;
  maxTokens: number;
  fallbackMode: boolean;
  className?: string;
}

export function CreditsBar({ tokensUsed, maxTokens, fallbackMode, className }: CreditsBarProps) {
  const pct = Math.min(100, Math.round((tokensUsed / maxTokens) * 100));
  const color =
    fallbackMode ? "bg-red-400" :
    pct > 90 ? "bg-red-400" :
    pct > 70 ? "bg-yellow-400" :
    "bg-accent";

  return (
    <div className={cn("space-y-1.5", className)}>
      <div className="flex items-center justify-between text-xs">
        <span className="text-text-muted">Token Usage</span>
        <span className={fallbackMode ? "text-red-400 font-medium" : "text-text-secondary"}>
          {formatTokens(tokensUsed)} / {formatTokens(maxTokens)}
          {fallbackMode && " — Fallback Mode"}
        </span>
      </div>
      <div className="h-1.5 bg-surface-raised rounded-full overflow-hidden">
        <div
          className={cn("h-full rounded-full transition-all duration-500", color)}
          style={{ width: `${pct}%` }}
        />
      </div>
      <div className="text-right text-xs text-text-muted">{pct}% used</div>
    </div>
  );
}
