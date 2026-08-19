import type { ClientMessage, ServerMessage } from '../../../core/src/messages.js';
import { patchDevSettings, writeDevLayout } from '../devPersistence.js';
import { isBrowserRuntime } from '../runtime.js';
import { PostMessageTransport } from './postMessageTransport.js';
import type { MessageTransport } from './types.js';
import { WebSocketTransport } from './webSocketTransport.js';

function createTransport(): MessageTransport {
  if (!isBrowserRuntime) {
    return new PostMessageTransport();
  }
  // Standalone browser: connect via WebSocket to the same host serving the SPA
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsUrl = `${protocol}//${window.location.host}/ws`;
  const ws = new WebSocketTransport(wsUrl);
  ws.connect();
  // Vite dev only: there is no server to connect to, so `browserMock` injects
  // ServerMessages as `window` 'message' events. Bridge them into the transport
  // (the WebSocket never opens against the dev server). Guarded by DEV so it's
  // tree-shaken out of the production standalone build.
  if (import.meta.env.DEV) {
    // No server in Vite dev: persist the state the server would have owned so a
    // code edit (HMR full-reload) doesn't wipe the layout or the NPC settings.
    const rawSend = ws.send.bind(ws);
    ws.send = (msg: ClientMessage): void => {
      if (msg.type === 'saveLayout' && msg.layout) {
        writeDevLayout(msg.layout as Record<string, unknown>);
      } else if (msg.type === 'setNpcQuipInterval') {
        patchDevSettings({ npcQuipIntervalSec: msg.seconds });
      } else if (msg.type === 'setAgentIdleTimeout') {
        patchDevSettings({ agentIdleTimeoutMin: msg.minutes });
      }
      rawSend(msg);
    };
    window.addEventListener('message', (e: MessageEvent) => {
      const data = e.data as unknown;
      if (
        data &&
        typeof data === 'object' &&
        typeof (data as { type?: unknown }).type === 'string'
      ) {
        ws.deliver(data as ServerMessage);
      }
    });
  }
  return ws;
}

/** Singleton transport instance. Import this everywhere instead of vscodeApi. */
export const transport: MessageTransport = createTransport();
export type { MessageTransport } from './types.js';
