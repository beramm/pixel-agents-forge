import type { Character, ToolActivity } from './office/types.js';

const IDLE_TEXT = 'Idle at the anvil';

/** Current task line + status dot color for one smith. Mirrors ToolOverlay. */
export function taskFor(
  id: number,
  ch: Character | undefined,
  agentTools: Record<number, ToolActivity[]>,
): { text: string; color: string | null } {
  if (ch?.bubbleType === 'permission')
    return { text: 'Needs approval', color: 'var(--color-status-permission)' };
  if (ch?.bubbleType === 'waiting' && ch.waitingAwaitingInput)
    return { text: 'Waiting for input', color: 'var(--color-status-permission)' };

  const tools = agentTools[id];
  if (tools && tools.length > 0) {
    const active = [...tools].reverse().find((t) => !t.done);
    if (active) {
      if (active.permissionWait)
        return { text: 'Needs approval', color: 'var(--color-status-permission)' };
      return { text: active.status, color: 'var(--color-status-active)' };
    }
    if (ch?.isActive) {
      const last = tools[tools.length - 1];
      if (last) return { text: last.status, color: 'var(--color-status-active)' };
    }
  }
  if (ch?.bubbleType === 'waiting')
    return { text: 'Order complete', color: 'var(--color-status-success)' };
  return { text: IDLE_TEXT, color: null };
}

export function smithName(id: number, ch: Character | undefined): string {
  if (ch?.isTeamLead) return `${ch.teamName ? `${ch.teamName} · ` : ''}Master Smith`;
  if (ch?.agentName) return ch.agentName;
  if (ch?.folderName) return ch.folderName;
  return `Smith #${id}`;
}

/** Plain current-task text for an agent (no color) — reused for quip context. */
export function smithTaskText(
  id: number,
  ch: Character | undefined,
  agentTools: Record<number, ToolActivity[]>,
): string {
  return taskFor(id, ch, agentTools).text;
}
