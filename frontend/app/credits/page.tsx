"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { formatTokens } from "@/lib/utils";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { CreditsBar } from "@/components/credits/credits-bar";
import { StatCard } from "@/components/dashboard/stat-card";
import { Zap, CreditCard, Activity, RefreshCw, AlertTriangle } from "lucide-react";

export default function CreditsPage() {
  const [credits, setCredits] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [resetting, setResetting] = useState(false);
  const [msg, setMsg] = useState("");

  async function load() {
    setLoading(true);
    try { setCredits(await api.getCredits()); } catch {}
    setLoading(false);
  }

  async function reset() {
    setResetting(true);
    try {
      const res = await api.reloadCredits();
      setMsg(res.message);
      await load();
    } catch (e: any) {
      setMsg(e.message);
    }
    setResetting(false);
  }

  useEffect(() => { load(); }, []);

  const pct = credits ? Math.round((credits.tokens_used / credits.max_tokens) * 100) : 0;

  return (
    <div className="space-y-6 animate-slide-up max-w-2xl">
      <div>
        <h2 className="text-xl font-bold text-text-primary">Credits & Usage</h2>
        <p className="text-text-secondary text-sm mt-1">
          Monitor token consumption across all agent calls.
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <StatCard
          label="Used"
          value={credits ? formatTokens(credits.tokens_used) : "—"}
          icon={Zap}
          accent="green"
        />
        <StatCard
          label="Remaining"
          value={credits ? formatTokens(credits.tokens_remaining) : "—"}
          icon={CreditCard}
          accent="purple"
        />
        <StatCard
          label="Mode"
          value={credits?.fallback_mode ? "Fallback" : "Live"}
          sub={credits?.fallback_mode ? "API paused" : "Active"}
          icon={Activity}
          accent={credits?.fallback_mode ? "purple" : "green"}
        />
      </div>

      {/* Usage bar */}
      <Card>
        <CardHeader>
          <CardTitle>Token Budget</CardTitle>
          <Button variant="ghost" size="sm" onClick={load}>
            <RefreshCw size={13} className={loading ? "animate-spin" : ""} />
          </Button>
        </CardHeader>
        {credits && (
          <CreditsBar
            tokensUsed={credits.tokens_used}
            maxTokens={credits.max_tokens}
            fallbackMode={credits.fallback_mode}
          />
        )}
      </Card>

      {/* Fallback warning */}
      {credits?.fallback_mode && (
        <Card className="border-yellow-500/30 bg-yellow-900/10">
          <div className="flex items-start gap-3">
            <AlertTriangle size={18} className="text-yellow-400 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-semibold text-yellow-400">Fallback Mode Active</p>
              <p className="text-xs text-text-secondary mt-1">
                Token budget exhausted. Agents are generating manual prompts instead of calling Claude.
                Reset the tracker below to resume live calls.
              </p>
            </div>
          </div>
        </Card>
      )}

      {/* Reset */}
      <Card>
        <CardHeader>
          <CardTitle>Reset Tracker</CardTitle>
        </CardHeader>
        <p className="text-sm text-text-secondary mb-4">
          This resets the in-memory token counter to zero and disables fallback mode.
          Useful during development or when starting a new session.
        </p>
        {msg && (
          <p className="text-xs text-accent bg-tag-bg border border-accent/20 rounded-lg px-3 py-2 mb-3">
            {msg}
          </p>
        )}
        <Button variant="outline" onClick={reset} loading={resetting}>
          <RefreshCw size={14} />
          Reset Credit Tracker
        </Button>
      </Card>

      {/* Info */}
      <Card className="bg-surface-raised">
        <p className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-3">How Credits Work</p>
        <div className="space-y-2 text-xs text-text-secondary">
          <p>• Each agent call estimates tokens before calling Claude to avoid overruns.</p>
          <p>• When budget is exhausted, the system switches to <span className="text-purple">fallback mode</span> — agents return manual prompts instead of API responses.</p>
          <p>• The tracker is per-session and in-memory. Configure <code className="text-accent bg-tag-bg px-1 rounded">MAX_TOKENS_PER_PROJECT</code> in <code className="text-accent bg-tag-bg px-1 rounded">.env.local</code> to adjust the budget.</p>
          <p>• In production, ledger entries are persisted to <code className="text-accent bg-tag-bg px-1 rounded">credit_ledger</code> in the database.</p>
        </div>
      </Card>
    </div>
  );
}
