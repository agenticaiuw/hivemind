# Harness derivation — mac-planner — round 118

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **briefing source authorization truthfulness** — GET /ops/status reports Calendar and Mail automation as granted in cache, but GET /briefing/latest says both were not read because an Automation grant is needed. The briefing adapter and permission health are inconsistent.
  - evidence: Fresh parallel probes in round 118: /ops/status permissions.automation.Calendar and Mail granted=true; /briefing/latest sections.Not read says calendar/mail needs an Automation grant.

## Capabilities it proposed

### "When I tap twice before a meeting, put me into meeting mode: identify the next calendar event, open the right project files and browser tabs on my Mac, start a private notes workspace, mute distractions, and give me a 20-second spoken agenda; when I tap twice after, save the notes and restore what I was doing."
- **useful because:** Meeting preparation exists as a brief, but the owner still has to translate it into a desktop state and later reconstruct their prior workspace. This turns the pendant into a low-friction start/stop control spanning calendar, Mac apps/files, authenticated tabs, relay speech, and reversible workspace restoration.
- **path:** pendant → relay → mac-bridge → browser
- **model tier:** Background model assembles the agenda and selects relevant project context; realtime only handles the two short spoken confirmations. Deterministic Mac/browser actions should not invoke a model once the plan is resolved.
- **latency:** Start mode in 8 seconds or less, with speech beginning within 3 seconds; exit mode in 10 seconds. If calendar or browser is unavailable, proceed with local files and announce the missing source.
- **cost:** Usually <$0.02: one small text planning call plus macOS speech; most cost is optional TTS/audio transfer. Two-tap events and workspace snapshots are metadata-only.
- **security:** Calendar titles, file names, and authenticated tab URLs remain on the Mac/relay encrypted job record; spoken agenda must omit sensitive attendee or document content unless requested. Capture a pre-meeting manifest (foreground app, open project files, tab IDs, volume/focus state) and restore only items this routine changed. Never send meeting notes or alter calendar invites automatically.
- **missing:** Pendant double-tap event mapped to a named routine with cancellation window; A Mac workspace snapshot/restore primitive that records only routine-owned changes and has a durable receipt; Calendar-to-project association rules with local-only fallback; Browser tab grouping/restore bound to authenticated session IDs; Focus/Do Not Disturb integration with an explicit owner-configured allowlist

### "When I say “continue this on my Mac,” move the conversation I was having through the pendant onto the Mac exactly where I left off: show the transcript and sources, expose the unfinished plan and its next decision, attach the relevant browser tabs/files, and let me hand it back to the pendant later without starting over."
- **useful because:** The pendant is good for capture and quick answers while walking, while the Mac is better for reading, editing, and acting. Today they can exchange isolated jobs, but the owner cannot transfer the live thread—including what was decided, what remains uncertain, and which private resources support it—without manually reconstructing context.
- **path:** pendant → relay → mac-bridge → browser
- **model tier:** Use a cheaper background model to compress and structure the thread into a handoff capsule; use realtime only for the spoken handoff acknowledgment. Deterministic Mac and browser attachment should use typed operations, not another full planning call.
- **latency:** Create the capsule in under 2 seconds after the phrase; render the Mac workbench in under 8 seconds. Returning to the pendant should begin with a one-sentence state summary in under 3 seconds.
- **cost:** Low: one bounded summarization call per handoff plus ordinary local UI/file work. Audio transfer is the dominant variable cost; avoid retranscribing audio already represented by the relay transcript.
- **security:** Private transcript, sources, tab IDs, and file paths remain encrypted and scoped to the paired Mac/session. Do not copy page bodies or secrets into a general clipboard or cloud memory. Require an explicit pairing and expiration for each capsule; on return, show the owner which tabs/files were attached and never send or submit anything merely because it was handed off.
- **missing:** A first-class handoff-capsule schema containing transcript, decisions, open questions, provenance, pending actions, and expiry; Relay support for bidirectional session ownership transfer rather than independent job records; A Mac workbench view that can render a capsule and attach existing browser tabs/files without duplicating them; Pendant controls for resume, switch-back, expire, and redact a capsule; A cross-surface provenance map linking spoken claims to browser extracts, Calendar/Mail reads, and Mac receipts


## Changes it proposed to its own stack

### `integration` — Make the briefing source adapter perform a live per-source authorization probe and normalize errors before composing the brief. If Calendar/Mail automation is actually available, read through the bounded mac_read_sources path; if it is unavailable, distinguish TCC denial from timeout, stale grant cache, and empty data. Include a source-health receipt (checkedAt, method, result) in the briefing and suppress the misleading generic 'needs an Automation grant' message when the cached and live states disagree.
- **owner gets:** The current workday brief says Calendar and Mail were not read because an Automation grant is needed, while /ops/status reports both grants as available. The owner needs a truthful brief, not a false missing-permission warning or silent omission.
- effort: Small-to-medium: adapter preflight, error taxonomy, and receipt fields; add tests for grant-cache disagreement and empty inbox/calendar.  ·  risk: A probe could trigger an unwanted permission prompt if implemented with the wrong API; use the existing bounded read source adapter and never open UI. On failure, retain the current conservative omission and explain the exact reason.
- cost: Negligible API cost; one local read/preflight per briefing. No new cloud storage beyond a few status fields.  ·  latency: Adds roughly 100–500 ms per source, parallelized.
- security: Improves privacy by keeping reads bounded and making source health explicit; do not store message bodies in the health receipt.
- depends on: Use the granted mac_read_sources implementation rather than the legacy briefing.js AppleScript path; A typed source-health result shared by /briefing and /briefing/latest

### `context` — Introduce a signed, expiring Continuity Capsule contract as the sole handoff object between pendant, relay, Mac, and browser. The capsule must carry a redacted transcript, decisions, unresolved questions, source/provenance references, pending action DAG, session ownership, and attachment descriptors (tab IDs/file bookmarks), with per-field sensitivity and a monotonic revision. Each surface acknowledges the same capsule revision and appends receipts instead of copying context into separate prompts. A return handoff produces a delta, not a second summary.
- **owner gets:** The owner can switch from speaking to working without losing the exact thread or accidentally acting on stale context. They can see what the system knows, what is unresolved, and what changed while they were away, then continue on either device as one conversation.
- effort: Medium-to-large: define and validate the schema, encrypted storage and expiry, redaction, revision conflict handling, and adapters for relay sessions, Mac jobs, browser tabs, and pendant playback.  ·  risk: A malformed or stale capsule could attach the wrong private tab or cause context confusion. Require paired-device identity, origin/session checks, revision matching, automatic expiry, and a visible mismatch state that refuses attachment rather than guessing.
- cost: Small metadata/storage cost; summarization cost falls over time because deltas replace repeated full-context prompts. No page bodies or raw audio need be duplicated.  ·  latency: Initial handoff adds a small serialization step; subsequent turns should be faster because only capsule deltas and relevant fields are sent.
- security: Improves data minimization and auditability, but creates a concentrated sensitive object. Encrypt at rest and in transit, field-level redact by default, use short TTLs, and allow pendant gesture to expire or redact it.
- depends on: Relay session ownership and resume semantics; Typed browser attachment descriptors with session/origin validation; Mac workbench renderer and receipt integration; Pendant resume/expire interaction


## What it asked for

_Nothing._
## Its own summary

Round 118 produced two non-duplicate outcomes: (1) a recorded integration fix for the live contradiction where /ops/status reports Calendar/Mail automation granted but the workday brief reports both missing; (2) a recorded cross-surface double-tap Meeting Mode that snapshots/restores the Mac workspace, opens project files and authenticated tabs, uses bounded Calendar reads, and speaks a short agenda. I also sent mac-vision its safe activation conditions: loop and screenshot upload remain off without explicit owner consent, and TCC grants are still absent.

**Biggest unknown:** Whether the owner wants to manually grant Accessibility and Screen Recording to AI Pendant Agent. Those TCC grants cannot be enabled from this harness; without them, visual GUI automation remains unavailable, though AppleScript, bounded source reads, and non-visual Mac actions work. Browser extension is currently offline with 9 pending commands, so authenticated-tab features remain degraded until it reconnects.

