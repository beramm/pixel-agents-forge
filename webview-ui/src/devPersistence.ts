/**
 * Vite-dev-only persistence (localStorage).
 *
 * In `npm run dev` there is no server behind the webview: `browserMock` injects
 * the bundled default layout and settings, and `saveLayout` / `set*` messages go
 * into a WebSocket that never opens. Without this store every code edit (HMR
 * full-reload) threw away the layout the user had just built.
 *
 * VS Code and the standalone server persist through `~/.pixel-agents/`; this
 * module is guarded by `import.meta.env.DEV` at both call sites and is tree-shaken
 * out of production builds.
 */

const LAYOUT_KEY = 'pixel-agents.dev.layout';
const SETTINGS_KEY = 'pixel-agents.dev.settings';

/** Layout revision field — mirrors LAYOUT_REVISION_KEY in server/src/constants.ts. */
const LAYOUT_REVISION_KEY = 'layoutRevision';

export interface DevSettings {
  npcQuipIntervalSec?: number;
  agentIdleTimeoutMin?: number;
}

function readJson<T>(key: string): T | null {
  try {
    const raw = localStorage.getItem(key);
    return raw ? (JSON.parse(raw) as T) : null;
  } catch {
    return null;
  }
}

function writeJson(key: string, value: unknown): void {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch (err) {
    console.warn('[DevPersistence] Failed to write', key, err);
  }
}

export function readDevLayout(): Record<string, unknown> | null {
  return readJson<Record<string, unknown>>(LAYOUT_KEY);
}

export function writeDevLayout(layout: Record<string, unknown>): void {
  writeJson(LAYOUT_KEY, layout);
}

export function clearDevLayout(): void {
  try {
    localStorage.removeItem(LAYOUT_KEY);
  } catch {
    /* ignore */
  }
}

/**
 * Pick the layout dev should boot with. Mirrors the server rule in
 * `loadLayout()`: the saved layout wins unless the bundled default carries a
 * newer revision, in which case the bundled one replaces it.
 */
export function resolveDevLayout(
  bundledDefault: Record<string, unknown> | null,
): Record<string, unknown> | null {
  const saved = readDevLayout();
  if (!saved) return bundledDefault;
  const savedRevision = (saved[LAYOUT_REVISION_KEY] as number | undefined) ?? 0;
  const defaultRevision = (bundledDefault?.[LAYOUT_REVISION_KEY] as number | undefined) ?? 0;
  if (bundledDefault && defaultRevision > savedRevision) {
    console.log(
      `[DevPersistence] Bundled default is newer (${String(savedRevision)} < ${String(defaultRevision)}) — discarding saved dev layout`,
    );
    clearDevLayout();
    return bundledDefault;
  }
  console.log('[DevPersistence] Restored layout from localStorage');
  return saved;
}

export function readDevSettings(): DevSettings {
  return readJson<DevSettings>(SETTINGS_KEY) ?? {};
}

export function patchDevSettings(patch: DevSettings): void {
  writeJson(SETTINGS_KEY, { ...readDevSettings(), ...patch });
}
