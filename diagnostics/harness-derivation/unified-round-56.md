# Harness derivation — unified — round 56

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### ""Keep me from being interrupted when I'm busy, but don't let anything genuinely urgent slip through.""
- **useful because:** Today the pendant, relay, Mac, and browser each know only part of the owner's attention state. This capability turns that into one dependable behavior: routine alerts wait silently during meetings/focus/music, while urgent account or safety events are summarized and surfaced once, with no duplicate chimes after reconnect.
- **path:** mac-planner reads active app, Focus/Do Not Disturb, microphone/call state, and the next calendar event; browser-extension supplies urgency signals from already-open authenticated tabs; relay maintains the durable attention queue, deduplicates and applies quiet hours; pendant firmware gives a single tactile/LED indication and lets the owner acknowledge or defer with its one button; dashboard shows why an item was held or escalated.
- **model tier:** Use deterministic Mac/browser classifiers and relay rules for most events; use a cheaper background text model only to rank or compress queued items. Reserve realtime for the owner's spoken query or an actual urgent announcement.
- **latency:** State changes should reach the relay in under 2 seconds; ordinary queue updates may take 30 seconds. An urgent alert should interrupt audio only after a 1–2 second deduplication window, and acknowledgement should survive a dropped link.
- **cost:** Usually <$0.01/day: mostly rule evaluation and D1 writes; model cost only when several queued items need summarization. No realtime tokens for routine suppression.
- **security:** Calendar titles, active-app state, and browser-derived urgency labels leave the Mac only as minimized typed signals; never upload page contents for attention scoring. Require confirmation before any alert-triggered external action. Keep sensitive page details out of pendant speech unless the owner asks.
- **missing:** A typed attention-state contract (focus, call, driving/away, quiet-until, urgency, expiry) shared by Mac, browser, relay, and pendant; A durable per-item alert queue with idempotency keys, escalation policy, acknowledgement/defer receipts, and reconnect replay; Mac event adapters for Focus/call/audio state and a browser-side semantic urgency classifier; Firmware mapping for queued/urgent/acknowledged states using the single LED and button without conflicting with conversation start/end

### ""Quiet for the next hour, except for things I explicitly marked urgent—and remind me what I missed when the hour is over.""
- **useful because:** The owner cannot currently control interruption policy from the worn device or get a trustworthy post-quiet digest. This is a concrete, bounded interaction that makes the pendant useful in meetings, transit, and focused work without requiring the owner to open the dashboard.
- **path:** Pendant button gesture starts/cancels a timed quiet lease and uses generic LED/haptic states; relay persists the lease, queues eligible events, deduplicates them, and emits a completion digest; Mac reports Focus/call state as supporting evidence; browser bridge labels changes from already-open authenticated tabs; dashboard and voice provide review/edit of the lease and the held-items digest.
- **model tier:** No realtime model for lease enforcement or urgency gates. Use deterministic policy and a cheap background model only to compress the held queue at lease expiry; use realtime only if the owner asks for the digest conversationally.
- **latency:** A button gesture should be acknowledged locally in under 100 ms and reach the relay within 2 seconds. Lease expiry should produce a digest within 30 seconds, with reconnect replay and no duplicate delivery.
- **cost:** Typically under $0.01 per lease/day; D1 writes and event filtering dominate, with one small background summarization call only when multiple items are held.
- **security:** Store lease metadata and redacted event summaries, not private page contents, on the relay. Browser evidence remains on the Mac unless explicitly requested. Require paired-device authentication, signed lease revisions, and confirmation before any held item can trigger an external action.
- **missing:** A lease protocol with expiry, renewal, cancellation, priority allow-list, and monotonic revision numbers; A durable held-event queue with per-item acknowledgement and post-lease digest receipts; A pendant-local gesture/state machine that cannot confuse quiet control with conversation start/end; Mac/browser adapters that emit typed urgency without exporting page content


## Changes it proposed to its own stack

### `integration` — Add an Attention Envelope protocol shared by Mac, browser bridge, relay, dashboard, and pendant: {eventId, category, urgency, evidenceRef, sensitivity, createdAt, expiresAt, quietPolicy, ackState}. The relay stores only the envelope plus a redacted summary, merges duplicates by eventId/source fingerprint, and emits a reconnect-safe stream. Mac and browser producers publish state changes; pendant consumes only redacted urgency and acknowledgement commands. Add contract tests for focus transitions, duplicate browser events, expiry, and offline replay.
- **owner gets:** The owner gets one calm, predictable notification stream instead of repeated or mistimed interruptions, while urgent things still arrive after a meeting or network drop with an explanation of why they were held.
- effort: Medium: protocol/types and D1 migration, Mac Focus/call adapter, browser urgency adapter, relay queue/stream, dashboard view, and small pendant LED/button state-machine update; then end-to-end fault-injection tests.  ·  risk: A bad classifier could suppress something important or over-alert. Default unknown to non-suppressible only for explicitly high-risk categories, expire stale items, expose the held queue in the dashboard, and provide a physical long-press or spoken 'what did I miss?' recovery path. Roll out shadow-only before enabling suppression.
- cost: Negligible runtime cost (small D1 envelopes and WebSocket messages); one background summarization call only for grouped items. Firmware memory impact should stay under ~8 kB if it stores state, not content.  ·  latency: Adds <2 seconds for normal state propagation and a 1–2 second urgent dedupe window; no added latency to the live audio codec path.
- security: Reduces data exposure by sending typed urgency and redacted evidence references instead of page/calendar content. Require authenticated paired producers and signed event IDs; never let a browser event directly trigger an external action.
- depends on: A shared typed context projection so attention state is not hand-written per surface; A durable relay queue with acknowledgement/defer receipts and reconnect replay; Mac Focus/call/audio-state observation and browser extension heartbeat/urgency metadata; A pendant-local LED/button attention state machine


## What it asked for

### `c9-ozum` (context) — owner's interruption and urgency policy
- why: The new attention-envelope proposal needs a safe default for what counts as urgent and when a held item may interrupt speech; this is not specified by hardware or route discovery.
- would change: I would encode explicit categories and escalation defaults instead of guessing, reducing the chance of suppressing an important alert or waking the owner for routine browser changes.

## Its own summary

Discovered the live stack is healthy at relay/Mac level, but browser extension is offline with 4 pending commands and Mac computer-use is not ready (Accessibility and Screen Recording are ungranted). I recorded a new cross-surface capability: an Attention Envelope/quiet-interruption system where Mac Focus/call state and authenticated-browser urgency feed a durable relay queue, and the pendant gives only generic queued/urgent/ack feedback with reconnect-safe replay. I also recorded the integration change and asked for the missing owner interruption/urgency policy. What I still need to ship it: that policy, the shared typed attention contract, durable queue/ack replay, Mac Focus/call adapters, browser heartbeat/urgency metadata, and a pendant-local LED/button state machine. Separately, the owner's current audio goal still depends on the pending 24 kHz acceptance/architecture context and the existing audio validation/fault-injection work.

**Biggest unknown:** Which event categories the owner personally considers interrupt-now versus hold-until-free; without that, suppression defaults are necessarily conservative.

