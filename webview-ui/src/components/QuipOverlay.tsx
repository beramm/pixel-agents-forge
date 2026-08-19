import { useEffect, useState } from 'react';

import {
  CHARACTER_SITTING_OFFSET_PX,
  QUIP_BUBBLE_MAX_WIDTH_PX,
  TOOL_OVERLAY_VERTICAL_OFFSET,
} from '../constants.js';
import type { OfficeState } from '../office/engine/officeState.js';
import { CharacterState, TILE_SIZE } from '../office/types.js';

interface QuipOverlayProps {
  officeState: OfficeState;
  containerRef: React.RefObject<HTMLDivElement | null>;
  zoom: number;
  panRef: React.RefObject<{ x: number; y: number }>;
}

/**
 * Renders transient speech bubbles above any character carrying a `quip`
 * (NPC sarcasm on a cooldown, or an agent's acknowledgement when its work
 * order is clicked). Re-renders every frame so bubbles track the character.
 */
export function QuipOverlay({ officeState, containerRef, zoom, panRef }: QuipOverlayProps) {
  const [, setTick] = useState(0);
  useEffect(() => {
    let rafId = 0;
    const tick = () => {
      setTick((n) => n + 1);
      rafId = requestAnimationFrame(tick);
    };
    rafId = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(rafId);
  }, []);

  const el = containerRef.current;
  if (!el) return null;
  const rect = el.getBoundingClientRect();
  const dpr = window.devicePixelRatio || 1;
  const canvasW = Math.round(rect.width * dpr);
  const canvasH = Math.round(rect.height * dpr);
  const layout = officeState.getLayout();
  const mapW = layout.cols * TILE_SIZE * zoom;
  const mapH = layout.rows * TILE_SIZE * zoom;
  const deviceOffsetX = Math.floor((canvasW - mapW) / 2) + Math.round(panRef.current.x);
  const deviceOffsetY = Math.floor((canvasH - mapH) / 2) + Math.round(panRef.current.y);

  return (
    <>
      {[...officeState.characters.values()].map((ch) => {
        if (!ch.quip || ch.matrixEffect === 'despawn') return null;
        const sittingOffset = ch.state === CharacterState.TYPE ? CHARACTER_SITTING_OFFSET_PX : 0;
        const screenX = (deviceOffsetX + ch.x * zoom) / dpr;
        const screenY =
          (deviceOffsetY + (ch.y + sittingOffset - TOOL_OVERLAY_VERTICAL_OFFSET) * zoom) / dpr;
        return (
          <div
            key={ch.id}
            className="absolute flex flex-col items-center -translate-x-1/2 -translate-y-full"
            style={{ left: screenX, top: screenY, pointerEvents: 'none', zIndex: 44 }}
            data-testid="quip-bubble"
            data-agent-id={ch.id}
          >
            <div
              className="relative bg-bg-dark border-2 border-accent text-text shadow-pixel text-xs"
              style={{
                // Ambient quips self-expire, so they carry no dismiss button and
                // need no right-side gutter for it.
                padding: ch.quipSticky ? '4px 14px 4px 8px' : '4px 8px',
                maxWidth: QUIP_BUBBLE_MAX_WIDTH_PX,
                textAlign: 'center',
                lineHeight: 1.2,
                pointerEvents: 'auto',
              }}
            >
              {ch.quip}
              {ch.quipSticky && (
                <span
                  onClick={(e) => {
                    e.stopPropagation();
                    officeState.dismissQuip(ch.id);
                  }}
                  className="absolute text-accent cursor-pointer select-none"
                  style={{ top: -2, right: 2, lineHeight: 1, pointerEvents: 'auto' }}
                  data-testid="quip-dismiss"
                  aria-label="Dismiss"
                >
                  ×
                </span>
              )}
            </div>
            <div
              className="bg-bg-dark border-r-2 border-b-2 border-accent"
              style={{ width: 8, height: 8, marginTop: -5, transform: 'rotate(45deg)' }}
            />
          </div>
        );
      })}
    </>
  );
}
