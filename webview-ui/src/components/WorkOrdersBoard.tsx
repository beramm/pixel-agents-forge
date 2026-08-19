import type { OfficeState } from '../office/engine/officeState.js';
import type { ToolActivity } from '../office/types.js';
import { smithName, taskFor } from '../smithActivity.js';

interface WorkOrdersBoardProps {
  agents: number[];
  agentTools: Record<number, ToolActivity[]>;
  officeState: OfficeState;
  onSelectAgent: (id: number) => void;
}

/**
 * Forge "Work Orders" board — a fixed panel listing every active smith (agent)
 * and the task/goal they are currently working on. Click a row to select that
 * smith in the scene.
 */
export function WorkOrdersBoard({
  agents,
  agentTools,
  officeState,
  onSelectAgent,
}: WorkOrdersBoardProps) {
  return (
    <div
      className="absolute bg-bg-dark border-2 border-border shadow-pixel select-none"
      style={{ top: 16, right: 16, width: 340, maxWidth: '44vw', zIndex: 45 }}
      data-testid="work-orders-board"
    >
      <div className="px-12 py-8 border-b-2 border-border text-sm text-accent">⚒ Work Orders</div>
      <div style={{ maxHeight: '45vh', overflowY: 'auto' }}>
        {agents.length === 0 ? (
          <div className="px-12 py-10 text-xs text-text-muted">
            The forge is quiet. No smiths at work.
          </div>
        ) : (
          agents.map((id) => {
            const ch = officeState.characters.get(id);
            const { text, color } = taskFor(id, ch, agentTools);
            return (
              <div
                key={id}
                onClick={() => onSelectAgent(id)}
                className="flex items-start gap-8 px-12 py-8 border-b border-border cursor-pointer hover:bg-btn-hover"
                data-agent-id={id}
              >
                <span
                  className="inline-block shrink-0"
                  style={{
                    width: 10,
                    height: 10,
                    marginTop: 6,
                    background: color ?? 'var(--color-text-muted)',
                  }}
                />
                <span className="flex flex-col" style={{ minWidth: 0 }}>
                  <span className="text-xs text-text truncate">{smithName(id, ch)}</span>
                  <span className="text-xs text-text-muted truncate">{text}</span>
                </span>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
