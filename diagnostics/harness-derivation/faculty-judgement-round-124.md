# Harness derivation — faculty-judgement — round 124

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **quiet execution prerequisites** — The Mac agent and Safari bridge are currently online, but the browser has one pending command; Accessibility and Screen Recording remain unavailable while AppleScript automation is granted. Any quiet mode must reconcile/expire pending commands rather than replay them and must use typed receipts, not vision.
  - evidence: GET /ops/snapshot returned browserExtension.online=true, pendingCommands=1, accessibility.trusted=false, screenRecording.granted=false, and automation grants for Safari, Mail, Calendar, Finder, Notes, Messages, and Reminders.

## Capabilities it proposed

### "“Handle it quietly, and only get my attention if you need me.”"
- **useful because:** The owner can delegate routine Mac/browser work in public or during a conversation without the pendant reading private details aloud. The Mac and authenticated browser carry out reversible steps, the relay aggregates receipts, and the pendant gives a discreet completion/approval-needed signal; only an exception opens a spoken conversation.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified → faculty-judgement → faculty-action
- **model tier:** Use the slower background model for planning and receipt summarization; use realtime only if the owner presses the pendant after an approval-needed haptic or asks a follow-up.
- **latency:** Start acknowledgment within 1 second as a short haptic pattern; background work may take minutes. Exception escalation should be delivered within 10 seconds of a blocked step or bridge loss.
- **cost:** Usually one cheap planning/receipt pass (roughly $0.01–$0.05 depending on task); no realtime tokens unless the owner engages. Hardware prototype cost roughly $3–$8 per unit for a coin ERM/LRA motor and $1–$3 for a fuel-gauge/ambient sensor if added.
- **security:** Never expose message subjects, account names, or page contents through audio or LED patterns. Bind haptic outcomes to a job ID and approval token, expire them, and require a button press to authorize irreversible steps. Persist only redacted receipt metadata; keep sensitive browser data on the Mac/bridge.
- **missing:** A pendant haptic actuator and driver (the current board has only one LED and one button); A privacy mode in the relay/pipeline that routes status to haptics and suppresses speech; Typed cross-surface event/receipt contracts connecting Mac and browser jobs to a pendant notification queue; A user-visible mapping and cancellation gesture for haptic patterns

### "“Before I commit to this, show me what it will cost me and what it will displace.”"
- **useful because:** The owner gets a consequence preview before accepting a meeting, booking travel, agreeing to a deadline, or sending a significant message. The system compares the proposed commitment with calendar load, existing tasks, travel time, active browser work, and known obligations, then presents the smallest set of real trade-offs without changing anything.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified → faculty-perception → faculty-judgement
- **model tier:** Use a cheaper background model for source collection and normalization; reserve realtime for the owner's short spoken decision and one clarifying question when a key assumption is missing.
- **latency:** Return a concise first risk preview within 10 seconds; deeper source reconciliation may continue in the background for up to 60 seconds. No external action occurs during preview.
- **cost:** Approximately $0.02–$0.10 per preview, dominated by multi-source extraction and synthesis; repeated unchanged source facts should be cached with freshness limits.
- **security:** Treat calendar, mail, account pages, travel data, and task details as private. Keep raw content on the Mac/browser where possible and send the relay only normalized claims with provenance. Clearly label estimates versus facts; never silently infer consent or make changes.
- **missing:** A first-class consequence-preview schema containing proposal, assumptions, affected commitments, displacement costs, confidence, and source evidence; A shared obligation/time model that can normalize Calendar, Reminders, Mail, browser account pages, and active Mac jobs without collapsing uncertainty; A read-only multi-surface gather operation with bounded parallelism and source freshness checks; A spoken comparison format that fits in one short turn and supports 'show me the worst case' or 'use the least disruptive option' follow-ups


## Changes it proposed to its own stack

### `hardware` — Add a low-power LRA haptic actuator with a DRV2605-class I2C driver, plus a battery fuel gauge and (optionally) an ambient-light/proximity sensor. Reserve three local patterns: short pulse = completed, double pulse = approval needed, long pulse = blocked/connection lost. Keep the existing button as cancel/acknowledge and the LED as a secondary diagnostic channel.
- **owner gets:** They can receive private, actionable status while in public, driving, or talking to someone, instead of hearing account names and task details aloud or missing an important blocked action. Battery-aware escalation can also avoid silently draining the wearable.
- effort: Prototype wiring is modest because I2C is explicitly free; add board support, haptic patterns, event acknowledgements, enclosure and power tests. Product revision needs mechanical/acoustic validation and accessibility testing.  ·  risk: Extra current draw and mechanical buzz could annoy the wearer; a bad pattern could be mistaken for an approval. Default to conservative patterns, allow disabling, require an explicit button press for approval, and fall back to LED/audio when the haptic self-test fails.
- cost: Approximately $4–$12 BOM increase (motor, driver, gauge, passives, sensor) and a few mA during pulses; no per-call API cost. Fuel gauge reduces uncertainty but adds always-on quiescent current.  ·  latency: Local acknowledgment is sub-100 ms once an event reaches the pendant; no model latency. Haptic queue must survive LTE reconnects without replaying expired events.
- security: Improves privacy by removing sensitive audio from routine status. Do not encode semantic content in patterns beyond urgency/state; encrypt and authenticate event IDs, and expire approval challenges.
- depends on: A typed relay-to-pendant notification event and acknowledgement protocol; Privacy-mode routing in the pipeline; Cross-surface job receipts with idempotent event IDs and expiry

### `integration` — Implement a durable Quiet-Intent channel: when the owner says 'quietly', unified issues a signed mode lease (scope, expiry, allowed surfaces, speech suppression) to relay; Mac and browser jobs publish typed lifecycle events; relay reduces them to redacted state changes and delivers exactly-once pendant notifications. A button press acknowledges or cancels the lease; bridge reconnects must not replay expired events. Approval-required events carry only a nonce and human-safe label, with full details retrieved after an intentional spoken interaction.
- **owner gets:** This turns 'quietly' into a dependable behavior rather than a best-effort promise: private work continues across the Mac, logged-in browser, and sleeping relay, while the wearer gets only the minimum signal needed to act and can recover from a lost connection without duplicate actions.
- effort: Medium: define event and lease schemas, add relay D1 tables/TTL, adapt job/browser receipts, add reconnect reconciliation and tests for duplicate/out-of-order events, then add one voice command and dashboard history.  ·  risk: A stale lease could suppress speech when the owner expects it, or a lost event could hide a blocked task. Leases must expire quickly, surface a visible current-mode indicator in the dashboard, and default to normal speech after expiry; every event remains queryable in receipts.
- cost: Negligible storage and relay compute; roughly $0.001–$0.01 per background event batch, with no realtime model call. Context cost drops because only redacted state is injected into voice turns.  ·  latency: Local mode acknowledgment under 1 s; event delivery normally under 2 s, with reconnect reconciliation on next heartbeat. No added model round trip for ordinary completions.
- security: Strong privacy gain: browser content never crosses into the haptic/status payload. Signed leases prevent a tab or stale job from changing speech policy; enforce owner-scoped authorization and redact labels.
- depends on: Cross-surface transaction coordinator from faculty-action; Durable browser job runner and typed receipts; A pendant notification/acknowledgement transport; Owner interruption and quiet-hours policy

### `context` — Add a read-only consequence projection engine that accepts a proposed commitment as an untrusted hypothetical, resolves affected time windows and obligations across local Calendar/Reminders/Mail metadata, browser sessions, and active jobs, and returns a provenance-linked displacement graph. It must preserve competing interpretations instead of forcing one identity or deadline, assign confidence/expiry to every edge, and expose a compact spoken rendering plus an audit payload.
- **owner gets:** They can ask about a decision before making it and receive an honest answer such as 'this fits only if you give up lunch and delays the current browser task by two hours,' rather than discovering the conflict after committing.
- effort: Medium-to-high: schema and graph algorithms, local AppleScript readers, browser extraction adapters, hypothetical simulation tests, and a voice renderer. Start read-only with synthetic fixtures, then add live sources one at a time.  ·  risk: False conflicts could make the owner avoid worthwhile commitments; missed obligations are more dangerous. Show evidence and confidence, distinguish hard calendar conflicts from soft estimates, allow source-by-source inspection, and never write to external systems.
- cost: Low recurring storage; roughly $0.01–$0.08 per preview after cached extraction. The main cost is model synthesis over several normalized claims, not raw source reads.  ·  latency: Local extraction can begin immediately; a first estimate in seconds, full reconciliation under a minute. It must degrade to a partial answer when a source is unavailable rather than blocking.
- security: Read-only by design. Keep source text and account identifiers on the Mac/browser; relay receives redacted claim IDs, timestamps, confidence, and hashes. Hypothetical proposals must not be persisted as commitments unless the owner explicitly confirms.
- depends on: Typed task-relevant context projection with provenance and TTL; A normalized local obligation/time representation; Authenticated browser read/extract adapters; A read-only planning endpoint that accepts hypothetical inputs


## What it asked for

_Nothing._
