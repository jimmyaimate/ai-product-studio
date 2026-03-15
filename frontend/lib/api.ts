const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...init?.headers },
    ...init,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText);
    throw new Error(`API ${res.status}: ${text}`);
  }
  return res.json();
}

// Projects
export const api = {
  // Projects
  createProject: (body: { brief: string; template: string; name?: string }) =>
    request<{ project_id: string; status: string; message: string }>("/projects", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  getProject: (id: string) =>
    request<{ project_id: string; brief: any; outputs: Record<string, any> }>(`/projects/${id}`),

  getProjectStatus: (id: string) =>
    request<{
      project_id: string;
      completed_agents: string[];
      pending_agents: string[];
      credits: { tokens_used: number; tokens_remaining: number; max_tokens: number; fallback_mode: boolean };
    }>(`/projects/${id}/status`),

  // Tasks
  getTask: (id: string) =>
    request<{ task_id: string; status: string; ready: boolean; result: any; error: string | null }>(`/tasks/${id}`),

  retryTask: (id: string, body: { agent_type: string; project_id: string; input_data?: any }) =>
    request<{ task_id: string; new_celery_id: string; status: string }>(`/tasks/${id}/retry`, {
      method: "POST",
      body: JSON.stringify(body),
    }),

  // Credits
  getCredits: () =>
    request<{ tokens_used: number; tokens_remaining: number; max_tokens: number; fallback_mode: boolean }>("/credits"),

  reloadCredits: (additional_tokens?: number) =>
    request<{ message: string }>("/credits/reload", {
      method: "POST",
      body: JSON.stringify({ additional_tokens: additional_tokens ?? 10000 }),
    }),

  // Ingest
  ingestUrl: (body: { url: string; project_id: string }) =>
    request<{ source: string; chunks: number }>("/ingest/url", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  // Health
  health: () => request<{ status: string }>("/health"),
};
