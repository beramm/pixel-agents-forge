import { useRef, useState } from 'react';

import {
  AGENT_IDLE_TIMEOUT_MAX_MINUTES,
  AGENT_IDLE_TIMEOUT_MIN_MINUTES,
  AGENT_IDLE_TIMEOUT_STEP_MINUTES,
  NPC_QUIP_INTERVAL_MAX_SEC,
  NPC_QUIP_INTERVAL_MIN_SEC,
  NPC_QUIP_INTERVAL_STEP_SEC,
} from '../constants.js';
import { isSoundEnabled, setSoundEnabled } from '../notificationSound.js';
import { isBrowserRuntime } from '../runtime.js';
import { transport } from '../transport/index.js';
import { Button } from './ui/Button.js';
import { Checkbox } from './ui/Checkbox.js';
import { MenuItem } from './ui/MenuItem.js';
import { Modal } from './ui/Modal.js';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  isDebugMode: boolean;
  onToggleDebugMode: () => void;
  alwaysShowOverlay: boolean;
  onToggleAlwaysShowOverlay: () => void;
  externalAssetDirectories: string[];
  watchAllSessions: boolean;
  onToggleWatchAllSessions: () => void;
  hooksEnabled: boolean;
  onToggleHooksEnabled: () => void;
  /** Whether the areas overlay is rendered outside of the Areas edit tool. */
  showAreas: boolean;
  onToggleShowAreas: () => void;
  /** Hide the Show Areas checkbox entirely when areas are unavailable. */
  showAreasAvailable: boolean;
  /** Average seconds between ambient NPC speech bubbles (0 = off). */
  npcQuipIntervalSec: number;
  onChangeNpcQuipInterval: (seconds: number) => void;
  /** Minutes of inactivity before a smith is despawned (0 = never). */
  agentIdleTimeoutMin: number;
  onChangeAgentIdleTimeout: (minutes: number) => void;
  /** Browser-native layout export (standalone only; VS Code uses the host save dialog). */
  onExportLayout: () => void;
  /** Browser-native layout import from a chosen file (standalone only). */
  onImportLayout: (file: File) => void;
}

export function SettingsModal({
  isOpen,
  onClose,
  isDebugMode,
  onToggleDebugMode,
  alwaysShowOverlay,
  onToggleAlwaysShowOverlay,
  externalAssetDirectories,
  watchAllSessions,
  onToggleWatchAllSessions,
  hooksEnabled,
  onToggleHooksEnabled,
  showAreas,
  onToggleShowAreas,
  showAreasAvailable,
  npcQuipIntervalSec,
  onChangeNpcQuipInterval,
  agentIdleTimeoutMin,
  onChangeAgentIdleTimeout,
  onExportLayout,
  onImportLayout,
}: SettingsModalProps) {
  const [soundLocal, setSoundLocal] = useState(isSoundEnabled);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [assetDirDraft, setAssetDirDraft] = useState('');

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Settings">
      {/* Open Sessions Folder opens an OS file manager — impossible in the browser. */}
      {!isBrowserRuntime && (
        <MenuItem
          onClick={() => {
            transport.send({ type: 'openSessionsFolder' });
            onClose();
          }}
        >
          Open Sessions Folder
        </MenuItem>
      )}
      <MenuItem
        onClick={() => {
          if (isBrowserRuntime) {
            onExportLayout();
          } else {
            transport.send({ type: 'exportLayout' });
          }
          onClose();
        }}
      >
        Export Layout
      </MenuItem>
      <MenuItem
        onClick={() => {
          if (isBrowserRuntime) {
            // Open the native file picker; the import is applied in onChange below.
            fileInputRef.current?.click();
          } else {
            transport.send({ type: 'importLayout' });
            onClose();
          }
        }}
      >
        Import Layout
      </MenuItem>
      {isBrowserRuntime && (
        <input
          ref={fileInputRef}
          type="file"
          accept="application/json"
          className="hidden"
          onChange={(e) => {
            const file = e.target.files?.[0];
            // Reset the value so re-selecting the same file fires change again.
            e.target.value = '';
            if (file) {
              onImportLayout(file);
              onClose();
            }
          }}
        />
      )}
      {/* Browser has no native directory picker, so accept a typed absolute path. */}
      {isBrowserRuntime ? (
        <div className="flex items-center gap-4 py-4 px-10">
          <input
            type="text"
            value={assetDirDraft}
            placeholder="Absolute asset directory path"
            onChange={(e) => setAssetDirDraft(e.target.value)}
            className="flex-1 min-w-0 text-xs py-2 px-4 bg-bg border-2 border-border rounded-none text-text"
          />
          <Button
            variant="default"
            size="sm"
            onClick={() => {
              const path = assetDirDraft.trim();
              if (!path) return;
              transport.send({ type: 'addExternalAssetDirectory', path });
              setAssetDirDraft('');
            }}
            className="shrink-0"
          >
            Add
          </Button>
        </div>
      ) : (
        <MenuItem
          onClick={() => {
            transport.send({ type: 'addExternalAssetDirectory' });
            onClose();
          }}
        >
          Add Asset Directory
        </MenuItem>
      )}
      {externalAssetDirectories.map((dir) => (
        <div key={dir} className="flex items-center justify-between py-4 px-10 gap-8">
          <span
            className="text-xs text-text-muted overflow-hidden text-ellipsis whitespace-nowrap"
            title={dir}
          >
            {dir.split(/[/\\]/).pop() ?? dir}
          </span>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => transport.send({ type: 'removeExternalAssetDirectory', path: dir })}
            className="shrink-0"
          >
            x
          </Button>
        </div>
      ))}
      <Checkbox
        label="Sound Notifications"
        checked={soundLocal}
        onChange={() => {
          const newVal = !isSoundEnabled();
          setSoundEnabled(newVal);
          setSoundLocal(newVal);
          transport.send({ type: 'setSoundEnabled', enabled: newVal });
        }}
      />
      <Checkbox
        label="Watch All Sessions"
        checked={watchAllSessions}
        onChange={onToggleWatchAllSessions}
      />
      <Checkbox
        label="Instant Detection (Hooks)"
        checked={hooksEnabled}
        onChange={onToggleHooksEnabled}
      />
      <Checkbox
        label="Always Show Labels"
        checked={alwaysShowOverlay}
        onChange={onToggleAlwaysShowOverlay}
      />
      {showAreasAvailable && (
        <Checkbox label="Show Areas" checked={showAreas} onChange={onToggleShowAreas} />
      )}
      <div className="flex items-center justify-between py-4 px-10 gap-8">
        <span className="text-xs text-text">
          NPC Chatter
          <span className="text-text-muted">
            {' '}
            {npcQuipIntervalSec > 0 ? `every ~${String(npcQuipIntervalSec)}s` : 'off'}
          </span>
        </span>
        <input
          type="range"
          min={NPC_QUIP_INTERVAL_MIN_SEC}
          max={NPC_QUIP_INTERVAL_MAX_SEC}
          step={NPC_QUIP_INTERVAL_STEP_SEC}
          value={npcQuipIntervalSec}
          aria-label="NPC chatter interval in seconds"
          onChange={(e) => onChangeNpcQuipInterval(Number(e.target.value))}
          className="shrink-0 w-96"
        />
      </div>
      <div className="flex items-center justify-between py-4 px-10 gap-8">
        <span className="text-xs text-text">
          Idle Smith Timeout
          <span className="text-text-muted">
            {' '}
            {agentIdleTimeoutMin > 0 ? `${String(agentIdleTimeoutMin)} min` : 'never'}
          </span>
        </span>
        <input
          type="range"
          min={AGENT_IDLE_TIMEOUT_MIN_MINUTES}
          max={AGENT_IDLE_TIMEOUT_MAX_MINUTES}
          step={AGENT_IDLE_TIMEOUT_STEP_MINUTES}
          value={agentIdleTimeoutMin}
          aria-label="Idle timeout in minutes before a smith leaves the board"
          onChange={(e) => onChangeAgentIdleTimeout(Number(e.target.value))}
          className="shrink-0 w-96"
        />
      </div>
      <Checkbox label="Debug View" checked={isDebugMode} onChange={onToggleDebugMode} />
    </Modal>
  );
}
