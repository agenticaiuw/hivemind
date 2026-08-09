# Harness derivation — mac-planner — round 199

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“I’m wearing the pendant and looking at something on my Mac—remember exactly what I’m looking at and turn it into a useful follow-up card.”"
- **useful because:** A button bookmark currently remembers only a moment. This would bind that moment to the active app, browser URL/title, and a redacted screen context, so “that thing from earlier” becomes recoverable even when the pendant has no LTE. It is a genuinely cross-node memory handoff: pendant intent, Mac perception, browser session, relay ledger.
- **path:** pendant → mac-vision → browser-extension → relay-realtime → mac-planner
- **model tier:** Realtime only for the short spoken acknowledgement and intent; a cheaper background model extracts title, entities, and next action from the captured context.
- **latency:** Acknowledge within 1 s; capture card within 5 s; background enrichment under 30 s.
- **cost:** About $0.002–$0.02 per card depending on whether enrichment is invoked; Mac/browser capture and relay storage dominate latency, not inference.
- **security:** Capture must default to URL/title plus a redacted accessibility snapshot, never raw screen or page body unless explicitly requested. Authenticated pages and tokens must be excluded. The card should show its sources and support deletion.
- **missing:** A resolved USB-serial exchange path for the physically connected pendant when LTE is absent; A semantic Mac context operation for selected text/document identity; current ui_snapshot is not enough; A relay event schema that joins offline_moment_bookmark with a Mac/browser context receipt

### "“From the pendant, draft a reply to the item I’m looking at, put it in the correct Mail or browser composer, and tell me what you prepared without sending it.”"
- **useful because:** The owner can speak while away from the keyboard, while the browser extension supplies the authenticated page and the Mac planner places a draft in the right composer. This removes the painful context switch but preserves a hard non-send boundary. It works today for a pendant attached over USB even though the pendant is not LTE-registered.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → mac-vision
- **model tier:** Realtime model parses the short command; background model drafts and checks tone/recipient/context; Mac execution is deterministic and does not need an expensive model.
- **latency:** Read current context and acknowledge in 1 s; draft visible in 5–10 s; never wait on a long autonomous loop.
- **cost:** Roughly $0.01–$0.06 per draft, dominated by context extraction and generation; desktop/browser actions are negligible.
- **security:** Never send, click final-submit, or expose full message bodies by default. Show recipient, quoted source, and exact draft in a local receipt. Require an explicit later user action for sending. Redact secrets and avoid drafting from pages marked private.
- **missing:** A reliable pendant-to-Mac event transport while LTE is absent; Browser command metadata for composer identity and a typed no-submit stop condition; A local policy entry explicitly authorizing draft insertion but not send

### "“When I say ‘handle this’ or press the bookmark button, make the smallest safe next step on my Mac, then tell me what happened and leave a resumable receipt.”"
- **useful because:** This is the system’s highest-value behavior: the pendant captures intent at the moment of friction, perception identifies the real browser/app state, judgement chooses one bounded next step, and Mac action executes it with a receipt. If the link drops, the job remains resumable rather than silently disappearing. It turns the hive from a voice interface into an accountable action loop.
- **path:** pendant → relay-realtime → mac-vision → faculty-perception → faculty-judgement → faculty-action → mac-planner → browser-extension
- **model tier:** Realtime handles intent and a brief spoken result; background/cheaper model performs state interpretation, planning, and summarization. Use the expensive tier only when ambiguity remains.
- **latency:** Spoken acknowledgement under 1 s; first action within 5 s; receipt within 15 s. Long tasks should stream status and be resumable.
- **cost:** $0.01–$0.10 per action depending on visual/context reasoning; most simple actions should route to deterministic planners and cost near zero.
- **security:** The current FULL_CONTROL_MODE has no effective approval gate. This capability therefore needs explicit owner policy classes, action receipts, touched-resource previews, and a kill/undo path. Never claim success without a receipt; redact page text and credentials from relay logs.
- **missing:** A resolved pendant USB control path and offline event queue bridge; A policy-aware execution seam that observes but does not silently block owner-approved routines; A durable cross-node job/capsule protocol carrying intent, context hash, plan, action result, and resume token

### "“When my Mac wakes after being asleep or offline, restore the exact work state I was in: reopen the relevant apps and tabs, show me what changed while I was away, and ask me only about decisions that became stale.”"
- **useful because:** Today a dropped bridge or sleep boundary breaks continuity: the owner must reconstruct which tabs, files, and pending actions mattered. This capability would make the Mac a durable second body for the pendant, with freshness checks instead of blindly replaying stale instructions.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement
- **model tier:** Background model builds the state delta and staleness explanations; realtime is used only if the owner asks from the pendant. Deterministic Mac actions reopen approved apps/tabs.
- **latency:** Detect bridge return within 10 s; produce a concise delta within 30 s; never auto-act on stale high-impact state.
- **cost:** $0.005–$0.03 per wake/reconnect, mostly for summarizing changed state; local state hashing is effectively free.
- **security:** Persist only encrypted app/tab identifiers and hashes, not page secrets. Never restore authenticated workflows that have changed materially without an explicit decision. Provide a one-command discard of the saved state.
- **missing:** A durable cross-node state checkpoint distinct from individual job receipts; Browser tab change/version signals and Mac sleep/wake notifications; A stale-state decision protocol that can pause only the affected step while restoring safe context

### "“Before I leave this Mac, make a private handoff package for tomorrow: the exact files and tabs I need, the unresolved questions, and a short spoken reminder when I next put on the pendant.”"
- **useful because:** End-of-day context is currently scattered across tabs, files, mail, and memory. A handoff package would turn an arbitrary stopping point into a deliberate restart point, reducing the cost of resuming work without requiring the owner to write a status report.
- **path:** mac-planner → browser-extension → relay-realtime → pendant → faculty-perception → faculty-judgement
- **model tier:** Cheaper background model extracts unresolved questions and summarizes only selected local sources; realtime speaks the reminder when requested or when the pendant reconnects.
- **latency:** Create in under 20 s for a normal work session; spoken reminder under 3 s after pendant connection.
- **cost:** $0.01–$0.05 per package depending on document count; storage and local hashing dominate.
- **security:** The package must be local-first and encrypted, with per-source inclusion shown before capture. Do not include whole documents or browser bodies by default. Expire reminders after a configurable date.
- **missing:** A first-class encrypted handoff bundle format with source manifests; A Mac sleep/session boundary hook and browser tab snapshot versioning; A pendant notification payload that can reference the bundle without transmitting its contents


## Changes it proposed to its own stack

### `integration` — Add a USB-local pendant gateway on the Mac bridge: accept bookmark, privacy, inbox, and audio-delivery status frames from /dev/cu.usbmodem00096003658*, timestamp them against Mac monotonic time, and forward them as authenticated relay events when online. Queue outbound acknowledgements locally with sequence numbers and replay them idempotently after reconnect. This is explicitly a local-mode path, not an LTE assumption.
- **owner gets:** The pendant is physically wearable and connected today but unregistered with LTE. The owner should still be able to press the button, get a real acknowledgement, and have the Mac understand the event instead of losing the most useful wearable behavior in the exact environment available for testing.
- effort: Medium: serial framing/parser, device identity handshake, replay ledger, and a small bridge daemon; then exercise existing firmware queues over USB.  ·  risk: Malformed or stale frames could create duplicate bookmarks or replay an old privacy state. Use monotonic sequence numbers, device nonce, and idempotent event keys; expose a local reset command. Do not forward microphone payloads unless the existing privacy/recording state permits it.
- cost: Negligible API cost; roughly 1–2 weeks engineering. No hardware cost or meaningful power increase while USB-powered.  ·  latency: Local acknowledgement under 100 ms; relay forwarding is best-effort and does not block button feedback.
- security: USB serial is a privileged local channel. Authenticate the device handshake, bind events to the Mac session, and keep raw audio off the relay by default.
- depends on: A resolved mac_serial_exchange tool or equivalent implementation in the Mac bridge; A stable event envelope shared with offline_moment_bookmark and local_privacy_latch

### `context` — Define a cross-surface Context Receipt object that every perception/action can emit: source surface, timestamp, URL/app/document identity, redaction class, content hash, and a short human-readable label. Make plans consume receipts rather than scraping fresh context ad hoc, and let the owner ask to reopen or delete a receipt.
- **owner gets:** When the owner says “that one,” the system can prove which page, app, or document it meant and recover after a dropped link. It prevents the common failure where the Mac acts on a changed tab while the pendant conversation still refers to the old one.
- effort: Medium: schema, relay persistence/TTL, browser and Mac adapters, and receipt display in job results.  ·  risk: A receipt may outlive the sensitive page it describes. Default to hashes and labels, short TTLs, explicit source links, and deletion propagation; never persist credentials or full private page text.
- cost: Low storage and inference cost; roughly $0.001–$0.01 per receipt plus engineering time.  ·  latency: Adds under 200 ms to normal planning; avoids much slower re-observation and retries.
- security: Improves auditability but creates metadata. Encrypt at rest, redact by source, and make retention visible.
- depends on: A semantic Mac context operation for selected text/document identity; Browser command/result payloads carrying tab and frame identity; Durable relay job receipts

### `memory` — Add a local-first provenance and deletion ledger that tracks every derived fact, summary, reminder, and action back to its source surface and capture time. When a source is deleted or expires, automatically invalidate dependent summaries and notify the owner instead of leaving stale memory presented as truth.
- **owner gets:** The owner should never have to wonder why the assistant still believes something after the underlying email, tab, file, or bookmark was removed or changed. This would make long-lived personal memory trustworthy rather than merely persistent.
- effort: High: dependency graph, source tombstones, expiry propagation across relay and Mac, and user-facing invalidation notices.  ·  risk: Over-aggressive invalidation could erase useful history; preserve a user-approved archival snapshot separately from live memory and make every deletion reversible for a short window.
- cost: Low per-event API cost but meaningful engineering and encrypted storage overhead; background graph updates can use a cheap model.  ·  latency: No perceptible impact on ordinary actions; source-change propagation may take seconds to minutes.
- security: Improves privacy by propagating deletion, but the dependency graph itself is sensitive. Keep raw content on the Mac where possible, send hashes and labels to the relay, and encrypt all provenance records.
- depends on: A shared Context Receipt or equivalent source identity; Change notifications from browser and Mac sources; Relay-side dependency storage and deletion propagation


## What it asked for

_Nothing._
