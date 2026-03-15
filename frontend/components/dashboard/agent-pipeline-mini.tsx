import { cn } from "@/lib/utils";
import { AGENT_SEQUENCE, AGENT_LABELS, type AgentType } from "@/types";
import { CheckCircle2, Circle, Loader2 } from "lucide-react";

interface AgentPipelineMiniProps {
  completedAgents: AgentType[];
  pendingAgents: AgentType[];
}

export function AgentPipelineMini({ completedAgents, pendingAgents }: AgentPipelineMiniProps) {
  const runningAgent = pendingAgents[0] as AgentType | undefined;

  return (
    <div className="flex items-center gap-1 flex-wrap">
      {AGENT_SEQUENCE.map((agent, i) => {
        const done = completedAgents.includes(agent);
        const running = agent === runningAgent;
        return (
          <div key={agent} className="flex items-center gap-1">
            <div className={cn(
              "flex items-center gap-1.5 px-2 py-1 rounded-md text-xs font-medium",
              done ? "bg-tag-bg text-accent" :
              running ? "bg-purple/10 text-purple" :
              "bg-surface-raised text-text-muted"
            )}>
              {done ? <CheckCircle2 size={11} /> :
               running ? <Loader2 size={11} className="animate-spin" /> :
               <Circle size={11} />}
              {AGENT_LABELS[agent]}
            </div>
            {i < AGENT_SEQUENCE.length - 1 && (
              <div className={cn("w-3 h-px", done ? "bg-accent/40" : "bg-border")} />
            )}
          </div>
        );
      })}
    </div>
  );
}
