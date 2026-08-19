import type { AgentStateStore } from './agentStateStore.js';
import { AGENT_IDLE_DESTROY_MS, IDLE_AGENT_SWEEP_INTERVAL_MS } from './constants.js';
import type { AgentState } from './types.js';

/**
 * Idle-agent sweep — a smith that has done nothing for
 * `AGENT_IDLE_DESTROY_MS` is taken off the Work Orders board and despawned.
 *
 * Distinct from `startStaleExternalAgentCheck` in fileWatcher.ts, which only
 * removes agents whose transcript file was DELETED and which stands down while
 * hooks are flowing. This sweep is about inactivity, so it runs in both modes.
 *
 * Removal mirrors a user closing the agent: the transcript is dismissed (short
 * cooldown) and the agent removed. When the session gets busy again the
 * scanner/hooks re-adopt it and the smith walks back in.
 */

/** Last moment this agent showed any sign of life. */
export function lastActivityOf(agent: AgentState): number {
  return Math.max(agent.lastActivityAt, agent.lastDataAt);
}

/** Ids of agents idle longer than `thresholdMs`. Pure — callers do the removing. */
export function collectIdleAgents(
  agents: Iterable<[number, AgentState]>,
  now: number,
  thresholdMs: number,
): number[] {
  const idle: number[] = [];
  for (const [id, agent] of agents) {
    // Never sweep an agent that is mid-task: a long Bash run or a permission
    // prompt can sit for minutes without producing a single transcript line.
    if (agent.activeToolIds.size > 0 || agent.isWaiting || agent.permissionSent) continue;
    const last = lastActivityOf(agent);
    if (last === 0) continue; // no activity recorded yet — not enough to judge
    if (now - last > thresholdMs) idle.push(id);
  }
  return idle;
}

export function startIdleAgentSweep(
  store: AgentStateStore,
  removeAgent: (id: number) => void,
  dismissFile: (path: string) => void,
  /** Live ref so a settings change takes effect on the next tick, no restart. */
  thresholdMsRef: { current: number } = { current: AGENT_IDLE_DESTROY_MS },
): ReturnType<typeof setInterval> {
  return setInterval(() => {
    const thresholdMs = thresholdMsRef.current;
    if (thresholdMs <= 0) return; // sweep disabled
    for (const id of collectIdleAgents(store, Date.now(), thresholdMs)) {
      const agent = store.get(id);
      if (!agent) continue;
      console.log(
        `[Pixel Agents] Idle sweep: Agent ${String(id)} idle > ${String(Math.round(thresholdMs / 1000))}s — removing`,
      );
      if (agent.jsonlFile) dismissFile(agent.jsonlFile);
      removeAgent(id);
    }
  }, IDLE_AGENT_SWEEP_INTERVAL_MS);
}
