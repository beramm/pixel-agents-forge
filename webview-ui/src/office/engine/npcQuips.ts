/**
 * Sarcastic one-liners for the forge.
 *  - NPCs mutter generic sarcasm, and sometimes heckle a working smith by name/task.
 *  - Smiths (agents) mumble sarcastically about their own current task.
 *  - Clicking a work order makes that smith bark a blacksmith acknowledgement.
 */

/** One working smith's context, supplied by the UI layer. */
export interface WorkContextEntry {
  id: number;
  name: string;
  task: string;
  active: boolean;
}

// ── Generic ambient sarcasm (no context needed) ──────────────────
export const NPC_QUIPS: string[] = [
  'Another sword? Groundbreaking.',
  'It compiles. Ship it.',
  'Works on my anvil.',
  "I'm not procrastinating, I'm annealing.",
  'Have you tried the bellows off and on?',
  'This ticket just said "make it shinier".',
  'Merge conflict on the horseshoes again.',
  'Standing meeting at the anvil. Riveting.',
  'Legacy horseshoes. Do NOT touch them.',
  'The forge is hot. Unlike my social life.',
  'Overtime at the forge again. Shocking.',
  'Ah yes, "quick fix." My favorite lie.',
];

// ── NPC heckles about a named working smith ──────────────────────
const ABOUT_AGENT: Array<(name: string, task: string) => string> = [
  (n, t) => `${n} still fussin' with ${t}. Bless.`,
  (n, t) => `Watch ${n} reinvent ${t}.`,
  (n, t) => `Bet ${n} breaks the build with ${t}.`,
  (n, t) => `${n} calls ${t} "craftsmanship."`,
  (n, t) => `Three heats on ${t}, eh ${n}?`,
  (n) => `${n} at that anvil again. Riveting.`,
  (n) => `Someone tell ${n} it's just a horseshoe.`,
  (n, t) => `${n}'s "quick fix" is now ${t}.`,
];

// ── Smith self-mumbles about their own task ──────────────────────
const SELF_MUMBLE: Array<(task: string) => string> = [
  (t) => `${t}? Character-building, truly.`,
  (t) => `Ah, ${t}. Living the dream.`,
  (t) => `Another ${t}. Be still my heart.`,
  (t) => `${t}. Because sleep is optional.`,
  (t) => `Sure, ${t}. What could go wrong.`,
  (t) => `${t} again. The forge never sleeps.`,
  (t) => `They said ${t} would be "quick."`,
];
const SELF_GENERIC = [
  'Craftsmanship, apparently.',
  'This is fine. Everything is fine.',
  'Add it to the pile.',
  'Measure twice, hammer forever.',
];

// ── Blacksmith acknowledgements (work-order click) ───────────────
export const ACK_QUIPS: string[] = [
  'Aye, still at the anvil!',
  'Still hammerin’ away, boss!',
  'Keepin’ the forge hot!',
  'On it — give it another heat!',
  'Nearly forged, hold fast!',
  'Temperin’ it just right!',
  'Workin’ the bellows as we speak!',
  'Patience — good steel takes time!',
  'Almost got the edge on it!',
  'No rush rushes the forge!',
];

// ── Drunk mumbles (NPCs sitting at the tavern) ───────────────────
export const DRUNK_QUIPS: string[] = [
  '*hic* ...best forge in town...',
  'I love you, anvil. No—I mean it.',
  'the horseshoes... they’re singing to me',
  'one more round! for the... the metal',
  'who moved the floor?',
  'is it a sword? or a big... spoon?',
  'I’m not drunk, YOU’re *hic* blurry',
  'tell the smith he’s my besht friend',
  'shhh... the keg can hear us',
  'ale before anvil, that’s the... rule?',
  'I could forge that. probably. maybe.',
  '*hic* ...what were we talkin’ about',
];

export function randomDrunkQuip(): string {
  return pick(DRUNK_QUIPS);
}

// ── Bartender lines (always busy) ────────────────────────────────
export const BARTENDER_QUIPS: string[] = [
  'Comin’ right up!',
  'One ale — no waitin’!',
  'No time to chat, orders up!',
  'Bar’s packed today!',
  'Fresh keg tapped!',
  'What’ll it be?',
  'Wipin’ mugs, always wipin’.',
  'Two ales? Make it four!',
  'Keep ’em comin’!',
  'Busy busy busy!',
];
export function randomBartenderQuip(): string {
  return pick(BARTENDER_QUIPS);
}
export function bartenderQuipCooldown(): number {
  return (6 + Math.random() * 8) * npcRateScale();
}

// ── Card players ─────────────────────────────────────────────────
export const CARD_QUIPS: string[] = [
  'Got any threes?',
  'Read ’em and weep!',
  'I’ll raise you two horseshoes.',
  'You’re bluffin’, smith.',
  'Deal me in!',
  'Full house! ...I think?',
  'No cheatin’ this time.',
  'All in!',
  'Ha! Beat that.',
  'One more hand, one more...',
];
export function randomCardQuip(): string {
  return pick(CARD_QUIPS);
}

// ── Musicians (band) ─────────────────────────────────────────────
export const MUSIC_QUIPS: string[] = [
  '♪ la la laaa ♪',
  '♪ strum strum ♪',
  '*drum solo*',
  '♪ a tavern tune ♪',
  'for the ale and the gold!',
  '♪ dum dum tss ♪',
  '♪ ...and a one, and a two ♪',
  '🎵 clang clang 🎵',
];
export function randomMusicQuip(): string {
  return pick(MUSIC_QUIPS);
}
export function musicQuipCooldown(): number {
  return (4 + Math.random() * 5) * npcRateScale();
}

// ── Tavern timing ────────────────────────────────────────────────
export const DRINK_RATE_PER_SEC = 1 / 16; // full drunk after ~16s of drinking
export const DRUNK_DECAY_PER_SEC = 1 / 30; // sobers up while wandering
export const DRUNK_QUIP_COOLDOWN_MIN_SEC = 4;
export const DRUNK_QUIP_COOLDOWN_MAX_SEC = 9;
export function drinkDuration(): number {
  return 12 + Math.random() * 16;
}
export function barVisitCooldown(): number {
  return 22 + Math.random() * 40;
}
export function drunkQuipCooldown(): number {
  return (
    (DRUNK_QUIP_COOLDOWN_MIN_SEC +
      Math.random() * (DRUNK_QUIP_COOLDOWN_MAX_SEC - DRUNK_QUIP_COOLDOWN_MIN_SEC)) *
    npcRateScale()
  );
}

// ── Ambient NPC chatter rate (user-configurable) ─────────────────
// Every NPC-side cooldown below is expressed relative to this interval, so a
// single setting scales drunks, bartenders, card players and hecklers alike.
// Agent (smith) quips are deliberately NOT scaled — they carry real work status.
/** Default average seconds between ambient NPC quips. Mirrors the server default. */
export const DEFAULT_NPC_QUIP_INTERVAL_SEC = 15;

let npcQuipIntervalSec = DEFAULT_NPC_QUIP_INTERVAL_SEC;

/** Set the average seconds between NPC quips. 0 silences ambient NPC chatter. */
export function setNpcQuipIntervalSec(seconds: number): void {
  npcQuipIntervalSec = Number.isFinite(seconds) ? Math.max(0, seconds) : npcQuipIntervalSec;
}

export function getNpcQuipIntervalSec(): number {
  return npcQuipIntervalSec;
}

/** False when the user has turned ambient NPC chatter off entirely. */
export function isNpcChatterEnabled(): boolean {
  return npcQuipIntervalSec > 0;
}

/** Multiplier applied to every NPC-flavored cooldown, relative to the default. */
function npcRateScale(): number {
  return npcQuipIntervalSec / DEFAULT_NPC_QUIP_INTERVAL_SEC;
}

// ── Timing ───────────────────────────────────────────────────────
export const QUIP_VISIBLE_SEC = 4.5;
export const ACK_VISIBLE_SEC = 3.5;
export const NPC_COOLDOWN_MIN_SEC = 9;
export const NPC_COOLDOWN_MAX_SEC = 22;
export const AGENT_COOLDOWN_MIN_SEC = 16;
export const AGENT_COOLDOWN_MAX_SEC = 38;

// ── Chatter budget ───────────────────────────────────────────────
// Ambient quips are flavor, not signal. Without a global cap every character
// speaks on its own timer and the map turns into a wall of overlapping boxes.
/** Max ambient (non-sticky) quips visible at once, across the whole map. */
export const MAX_CONCURRENT_QUIPS = 2;
/** Of those, at most this many may come from NPCs. */
export const MAX_NPC_QUIPS = 1;
/** Retry window when a character wants to speak but the budget is full. */
export const QUIP_RETRY_MIN_SEC = 1.5;
export const QUIP_RETRY_MAX_SEC = 4;
/** Hard cap on quip length — long text makes the bubble dwarf the sprite. */
export const QUIP_MAX_CHARS = 60;

export function quipRetryCooldown(): number {
  return QUIP_RETRY_MIN_SEC + Math.random() * (QUIP_RETRY_MAX_SEC - QUIP_RETRY_MIN_SEC);
}

/** Clamp quip text so bubbles stay small. Cuts on a word boundary when it can. */
export function truncateQuip(text: string): string {
  if (text.length <= QUIP_MAX_CHARS) return text;
  const cut = text.slice(0, QUIP_MAX_CHARS - 1);
  const lastSpace = cut.lastIndexOf(' ');
  return `${(lastSpace > QUIP_MAX_CHARS * 0.6 ? cut.slice(0, lastSpace) : cut).trimEnd()}…`;
}

function pick<T>(arr: T[]): T {
  return arr[Math.floor(Math.random() * arr.length)];
}

export function randomAck(): string {
  return pick(ACK_QUIPS);
}

/** Shorten a raw status string into a compact task phrase for quips. */
export function shortenTask(status: string | undefined): string {
  if (!status) return 'that task';
  let t = status
    .replace(/^Using\s+/i, '')
    .replace(/mcp__[A-Za-z0-9]+__/g, '')
    .replace(/_/g, ' ')
    .trim();
  if (!t || /^idle$/i.test(t)) return 'that task';
  if (t.length > 26) t = `${t.slice(0, 24).trim()}…`;
  return t;
}

/**
 * Pick a quip for a character.
 * @param isNpc  true for ambient villagers, false for smith self-mumble
 * @param ctx    current working-smith context (names + tasks)
 * @param selfId the character's own id (to avoid self-heckling / find own task)
 */
export function pickQuip(isNpc: boolean, ctx: WorkContextEntry[], selfId: number): string {
  if (isNpc) {
    const others = ctx.filter((e) => e.id !== selfId && e.active);
    // 55% of the time (when someone is working) heckle a named smith
    if (others.length > 0 && Math.random() < 0.55) {
      const target = pick(others);
      return pick(ABOUT_AGENT)(target.name, shortenTask(target.task));
    }
    return pick(NPC_QUIPS);
  }
  // Smith self-mumble about own current task
  const self = ctx.find((e) => e.id === selfId);
  if (self && self.active) {
    return pick(SELF_MUMBLE)(shortenTask(self.task));
  }
  return pick(SELF_GENERIC);
}

export function npcCooldown(): number {
  return (
    (NPC_COOLDOWN_MIN_SEC + Math.random() * (NPC_COOLDOWN_MAX_SEC - NPC_COOLDOWN_MIN_SEC)) *
    npcRateScale()
  );
}
export function agentCooldown(): number {
  return AGENT_COOLDOWN_MIN_SEC + Math.random() * (AGENT_COOLDOWN_MAX_SEC - AGENT_COOLDOWN_MIN_SEC);
}
