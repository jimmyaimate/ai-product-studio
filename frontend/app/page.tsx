"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { formatTokens } from "@/lib/utils";
import { StatCard } from "@/components/dashboard/stat-card";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { FolderOpen, Zap, CreditCard, Activity, ArrowRight, Plus } from "lucide-react";

export default function DashboardPage() {
  const [credits, setCredits] = useState<any>(null);
  const [health, setHealth] = useState<"ok" | "error" | "loading">("loading");

  useEffect(() => {
    api.getCredits().then(setCredits).catch(() => {});
    api.health().then(() => setHealth("ok")).catch(() => setHealth("error"));
  }, []);

  const usedPct = credits
    ? Math.round((credits.tokens_used / credits.max_tokens) * 100)
    : 0;

  return (
    <div className="space-y-8 animate-slide-up">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-2xl font-bold text-text-primary">
            Hey, I&apos;m <span className="text-gradient">OpenClaw Jimmy</span> 👋
          </h2>
          <p className="text-text-secondary mt-1 text-sm">
            Your AI product studio manager. Let&apos;s build something great.
          </p>
        </div>
        <Link href="/projects/new">
          <Button size="lg">
            <Plus size={16} />
            Start New Project
          </Button>
        </Link>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <StatCard
          label="Tokens Used"
          value={credits ? formatTokens(credits.tokens_used) : "—"}
          sub={`of ${credits ? formatTokens(credits.max_tokens) : "—"} budget`}
          icon={Zap}
          accent="green"
        />
        <StatCard
          label="Tokens Remaining"
          value={credits ? formatTokens(credits.tokens_remaining) : "—"}
          icon={CreditCard}
          accent="purple"
          trend={credits ? { value: `${usedPct}% used`, up: usedPct < 80 } : undefined}
        />
        <StatCard
          label="Mode"
          value={credits?.fallback_mode ? "Fallback" : "Live"}
          sub={credits?.fallback_mode ? "API calls paused" : "Claude API active"}
          icon={Activity}
          accent={credits?.fallback_mode ? "purple" : "green"}
        />
        <StatCard
          label="Backend"
          value={health === "loading" ? "…" : health === "ok" ? "Online" : "Offline"}
          sub={health === "ok" ? "API responding" : health === "error" ? "Check your server" : "Connecting…"}
          icon={FolderOpen}
          accent={health === "ok" ? "green" : "purple"}
        />
      </div>

      {/* Quick actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardHeader>
            <CardTitle>Quick Start</CardTitle>
          </CardHeader>
          <div className="space-y-2">
            {[
              { template: "saas", label: "SaaS Dashboard", desc: "Auth, billing, teams", icon: "⚡" },
              { template: "landing_page", label: "Landing Page", desc: "High-converting", icon: "🚀" },
              { template: "dashboard", label: "Analytics Dashboard", desc: "Data-heavy UI", icon: "📊" },
              { template: "marketplace", label: "Marketplace", desc: "Two-sided platform", icon: "🏪" },
            ].map(({ template, label, desc, icon }) => (
              <Link
                key={template}
                href={`/projects/new?template=${template}`}
                className="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-surface-raised transition-colors group"
              >
                <span className="text-lg">{icon}</span>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium text-text-primary">{label}</div>
                  <div className="text-xs text-text-muted">{desc}</div>
                </div>
                <ArrowRight size={14} className="text-text-muted group-hover:text-accent transition-colors" />
              </Link>
            ))}
          </div>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Agent Pipeline</CardTitle>
          </CardHeader>
          <div className="space-y-2.5">
            {[
              { name: "Research", desc: "Personas, competitors, market", color: "accent" },
              { name: "Strategy", desc: "Business model, GTM, roadmap", color: "accent" },
              { name: "UX Design", desc: "Flows, wireframes, IA", color: "purple" },
              { name: "UI Design", desc: "Design system, components", color: "purple" },
              { name: "Automation", desc: "Integrations, API, code tasks", color: "accent" },
              { name: "Documentation", desc: "PRD, README, guides", color: "purple" },
            ].map(({ name, desc, color }, i) => (
              <div key={name} className="flex items-center gap-3">
                <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${color === "accent" ? "bg-tag-bg text-accent" : "bg-purple/10 text-purple"}`}>
                  {i + 1}
                </div>
                <div>
                  <div className="text-sm font-medium text-text-primary">{name}</div>
                  <div className="text-xs text-text-muted">{desc}</div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}
