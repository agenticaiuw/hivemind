# Harness derivation — relay-realtime — round 173

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "While I’m wearing this, keep an ear out for relevant updates from my tools and summarize only what matters."
- **useful because:** The owner gets ambient awareness without constantly checking apps. It’s a wearable-native superpower when it’s selective and quiet.
- **path:** relay → mac-bridge → browser → unified
- **model tier:** Cheaper background tier for filtering, realtime only for delivery and quick clarification.
- **latency:** Minutes for most updates; seconds for urgent ones.
- **cost:** Moderate; dominated by filtering over multiple sources and occasional speech rendering.
- **security:** Tool output may include sensitive data. Apply source-specific rules, strip unnecessary details, and provide a quick way to dismiss or mute categories.
- **missing:** A unified event bus for sources (mail/calendar/files/browser) with priority and dedupe; Per-source privacy policies and redaction rules; Delivery channel to the pendant that doesn’t interfere with the single LED’s existing meanings

### "If my Mac is offline, still help me do simple things using the wearable and the relay."
- **useful because:** The owner is usually away from the Mac. If the Mac is down, the assistant shouldn’t become useless for basic tasks like status checks, reminders, and public lookups.
- **path:** relay → pendant → network
- **model tier:** Realtime for voice interaction; server-side for public web reads.
- **latency:** A few seconds for web lookups; under a second for local status/mode.
- **cost:** Low to moderate; dominated by web reads and occasional cloud calls.
- **security:** Keep offline features constrained to non-sensitive public data and local device state; avoid storing personal content.
- **missing:** A server-side browser capability (currently absent) OR a restricted set of public web endpoints the relay can read; A device-side skill set for basic interactions that do not depend on the Mac, such as quick notes that sync later via the existing outbox

### "Undo the last thing you did for me—whether it happened in a Mac app or my logged-in browser—and tell me exactly what was reversed."
- **useful because:** A remote voice interface needs a trustworthy escape hatch. Today a mistaken action can be reported but not located and compensated for across the Mac planner and browser session; the owner should be able to recover while away from the screen.
- **path:** pendant → relay → mac-planner → browser-extension → mac-terminal
- **model tier:** Realtime relay identifies the most recent completed job; a cheaper background planner derives and validates a compensating action from its receipt; Mac/browser agents execute it and return a typed result.
- **latency:** Speak acknowledgement within 500 ms; locate the receipt within 2 s; complete ordinary reversals within 15 s. If no safe compensating action exists, say so rather than pretending.
- **cost:** About $0.01–$0.05 per invocation; most cost is one planner call to derive the inverse, not the realtime turn.
- **security:** The journal must contain exact target, before/after state, and reversibility—not just prose. Never claim success without post-action verification. Destructive or externally visible actions need a spoken confirmation policy even though routine reversible actions should be immediate; retain an audit trail and allow 'stop' to abort.
- **missing:** A durable cross-surface action journal keyed by job and action, with before/after snapshots and inverse-action metadata; An inverse-action planner/executor contract for Mac and browser actions; A relay endpoint that resolves 'last thing' and dispatches a compensating job; Post-undo verification receipts

### "What is on my Mac right now? Read me the relevant window or browser page, and let me say 'the second one' or 'open that' to act on what you just described."
- **useful because:** The pendant is often worn away from the Mac and has no display. A snapshot-plus-spoken-reference mode would turn the Mac's current visual state into an interactive audio surface instead of forcing the owner to guess which app, tab, or item an agent is discussing.
- **path:** pendant → relay → mac-vision → mac-planner → browser-extension
- **model tier:** A low-cost vision/perception pass extracts windows, tabs, labels, and stable item IDs; realtime handles the short spoken narration and resolves follow-up references; planner/action tiers perform any requested click or open.
- **latency:** Initial inventory in 3–5 s, narration under 20 s; follow-up reference resolution under 1 s after the inventory is cached. Refresh only when the owner asks or the target state changes.
- **cost:** $0.01–$0.08 per snapshot depending on whether a screenshot is required; follow-up turns are mostly realtime text and cached IDs.
- **security:** Screenshots and page text may include private mail, credentials, or health data. Keep captures ephemeral, redact password fields, bind item IDs to a short-lived device/session, and never expose the inventory to another device without pairing. State when the view is stale.
- **missing:** A Mac-vision snapshot route that returns structured windows/tabs/controls rather than an opaque screenshot; Short-lived cross-turn visual reference state in the relay; A shared target-ID vocabulary accepted by mac-planner and browser-extension; A way to capture the Mac screen when the owner is away without disturbing foreground work

### "Remember this as a decision: [statement]. Later, if my Mac, calendar, files, or logged-in browser contradicts it, tell me which source conflicts and ask whether to update the decision."
- **useful because:** The owner currently has voice capture and action history, but no durable, provenance-linked layer that distinguishes a decision from a memo and notices when reality drifts. This prevents the wearable from repeatedly helping with obsolete assumptions and catches contradictions while the owner is away.
- **path:** pendant → relay → mac-planner → mac-terminal → browser-extension
- **model tier:** Realtime extracts the decision and its scope; a cheaper background indexer maintains normalized decision records and periodically checks only opted-in sources; faculty-perception compares evidence and faculty-judgement ranks conflicts before the relay speaks.
- **latency:** Acknowledge capture in under 1 s. Conflict checks can run in the background and deliver an alert within 1–5 minutes of observed evidence; an on-demand 'check my decisions' response within 10 s.
- **cost:** $0.02–$0.10 for capture and normalization; ongoing checks should use cheap embeddings/diffs and only invoke a stronger model for an actual conflict.
- **security:** Decisions can be highly personal. Encrypt at rest, retain source URLs/file paths and timestamps but not unnecessary page contents, support per-decision expiry and deletion, and never silently change a decision. A conflict alert must quote evidence and label uncertainty; authenticated browser content must remain scoped to the paired owner.
- **missing:** A durable decision-record store with scope, validity interval, provenance, confidence, and supersession fields; Incremental change feeds or snapshots for selected Mac folders, calendar/files, and authenticated browser pages; A background scheduler/worker to run checks (explicitly absent today); A relay inbox delivery path for conflict alerts plus a spoken 'update/ignore/snooze' operation


## Changes it proposed to its own stack

### `integration` — Create a USB-serial bridge harness on the Mac that can stream pendant debug telemetry (audio counters, packet loss, tx_starved, mic_drops, boot/session IDs) to the relay in near real time during a voice session, so relay-realtime can adapt prompts and delivery (e.g., shorten responses if tx_starved rises).
- **owner gets:** If audio quality degrades, the assistant can gracefully adjust instead of sounding broken — shorter, clearer replies when the link is struggling.
- effort: Medium to high. Requires Mac-side serial reader, relay ingestion route, and a compact telemetry schema.  ·  risk: Medium. Telemetry could expose sensitive usage patterns; keep it minimal, aggregate where possible, and allow opt-out.
- cost: Low runtime cost; mostly development effort plus small bandwidth for telemetry.  ·  latency: Positive: improves perceived responsiveness by adapting early.
- security: Ensure telemetry is authenticated and never stored longer than needed.
- depends on: Mac agent serial access to /dev/cu.usbmodem* and /dev/cu.usbserial*; A relay ingestion endpoint and schema


## What it asked for

_Nothing._
## Its own summary

Recorded three non-trivial owner-facing proposals: (1) a cross-Mac/browser spoken undo that derives and verifies compensating actions from durable receipts; (2) an interactive audio view of the unattended Mac with short-lived references such as “the second one”; and (3) a provenance-linked decision ledger that detects contradictions across Mac, calendar/files, and authenticated browser sources. The main missing pieces are durable semantic state, inverse-action metadata, visual target IDs, incremental source snapshots, and a real background worker; none should be assumed to exist merely because adjacent routes do.

**Biggest unknown:** The recorder flagged the audio Mac-view proposal as close to existing “what is on my Mac/read the page” work, so that item may need consolidation rather than separate implementation. The decision ledger’s /v1/ops/memory and /v1/ops/history routes were named from established context but not fully inventoried this round.

