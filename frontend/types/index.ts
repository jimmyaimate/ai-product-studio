export type DeploymentMode = "local" | "server";

export type AgentType =
  | "research"
  | "strategy"
  | "ux"
  | "ui"
  | "automation"
  | "documentation";

export const AGENT_SEQUENCE: AgentType[] = [
  "research",
  "strategy",
  "ux",
  "ui",
  "automation",
  "documentation",
];

export const AGENT_LABELS: Record<AgentType, string> = {
  research: "Research",
  strategy: "Strategy",
  ux: "UX Design",
  ui: "UI Design",
  automation: "Automation",
  documentation: "Documentation",
};

export const AGENT_DESCRIPTIONS: Record<AgentType, string> = {
  research: "User personas, competitor matrix, market sizing",
  strategy: "Business model, GTM, feature prioritization",
  ux: "User flows, wireframes, IA",
  ui: "Design system, components, Figma prompts",
  automation: "Integrations, API specs, Claude Code tasks",
  documentation: "PRD, README, onboarding guides",
};

export type ProjectStatus = "pending" | "started" | "running" | "completed" | "failed";

export interface ProjectStatusResponse {
  project_id: string;
  completed_agents: AgentType[];
  pending_agents: AgentType[];
  credits: CreditsInfo;
}

export interface CreditsInfo {
  tokens_used: number;
  tokens_remaining: number;
  max_tokens: number;
  fallback_mode: boolean;
}

export type TemplateId = "saas" | "landing_page" | "dashboard" | "marketplace";

export interface Template {
  id: TemplateId;
  name: string;
  description: string;
  icon: string;
}

export const TEMPLATES: Template[] = [
  { id: "saas", name: "SaaS Dashboard", description: "Auth, billing, teams, analytics", icon: "⚡" },
  { id: "landing_page", name: "Landing Page", description: "High-converting marketing page", icon: "🚀" },
  { id: "dashboard", name: "Analytics Dashboard", description: "Data-heavy admin interface", icon: "📊" },
  { id: "marketplace", name: "Marketplace", description: "Two-sided buyer/seller platform", icon: "🏪" },
];
