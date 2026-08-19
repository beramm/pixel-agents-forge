import { describe, expect, it } from 'vitest';

import { collectIdleAgents, lastActivityOf } from '../src/idleAgentSweep.js';
import type { AgentState } from '../src/types.js';

const NOW = 1_700_000_000_000;
const FIVE_MIN = 300_000;

function agent(overrides: Partial<AgentState> = {}): AgentState {
  return {
    id: 1,
    sessionId: 'sess',
    isExternal: true,
    projectDir: '/p',
    jsonlFile: '/p/sess.jsonl',
    fileOffset: 0,
    lineBuffer: '',
    activeToolIds: new Set(),
    activeToolStatuses: new Map(),
    activeToolNames: new Map(),
    activeSubagentToolIds: new Map(),
    activeSubagentToolNames: new Map(),
    backgroundAgentToolIds: new Set(),
    isWaiting: false,
    permissionSent: false,
    hadToolsInTurn: false,
    lastDataAt: 0,
    lastActivityAt: NOW,
    linesProcessed: 0,
    seenUnknownRecordTypes: new Set(),
    hookDelivered: false,
    inputTokens: 0,
    outputTokens: 0,
    ...overrides,
  } as AgentState;
}

describe('collectIdleAgents', () => {
  it('removes an agent idle past the threshold', () => {
    const a = agent({ lastActivityAt: NOW - FIVE_MIN - 1 });
    expect(collectIdleAgents([[1, a]], NOW, FIVE_MIN)).toEqual([1]);
  });

  it('keeps an agent that is exactly at the threshold', () => {
    const a = agent({ lastActivityAt: NOW - FIVE_MIN });
    expect(collectIdleAgents([[1, a]], NOW, FIVE_MIN)).toEqual([]);
  });

  it('keeps an agent whose JSONL activity is recent even if the hook stamp is old', () => {
    const a = agent({ lastActivityAt: NOW - FIVE_MIN - 1, lastDataAt: NOW - 1000 });
    expect(collectIdleAgents([[1, a]], NOW, FIVE_MIN)).toEqual([]);
  });

  it('never sweeps an agent mid-tool, waiting, or awaiting permission', () => {
    const old = NOW - FIVE_MIN - 1;
    const busy = agent({ lastActivityAt: old, activeToolIds: new Set(['t1']) });
    const waiting = agent({ lastActivityAt: old, isWaiting: true });
    const permission = agent({ lastActivityAt: old, permissionSent: true });
    expect(collectIdleAgents([[1, busy]], NOW, FIVE_MIN)).toEqual([]);
    expect(collectIdleAgents([[2, waiting]], NOW, FIVE_MIN)).toEqual([]);
    expect(collectIdleAgents([[3, permission]], NOW, FIVE_MIN)).toEqual([]);
  });

  it('ignores an agent with no recorded activity at all', () => {
    const a = agent({ lastActivityAt: 0, lastDataAt: 0 });
    expect(collectIdleAgents([[1, a]], NOW, FIVE_MIN)).toEqual([]);
  });

  it('lastActivityOf takes the newer of the hook and JSONL stamps', () => {
    expect(lastActivityOf(agent({ lastActivityAt: 5, lastDataAt: 9 }))).toBe(9);
    expect(lastActivityOf(agent({ lastActivityAt: 9, lastDataAt: 5 }))).toBe(9);
  });
});
