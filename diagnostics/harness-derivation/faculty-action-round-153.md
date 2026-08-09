# Harness derivation — faculty-action — round 153

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### ""Do this whole thing for me, and don't tell me it's done until you can prove each step; if something fails, stop safely and tell me exactly where.""
- **useful because:** This is the highest-value action contract: one request can cross Mac apps and logged-in browser sessions while preserving a checkpointed, truthful boundary between planned, executed, verified, and unknown. The owner gets outcomes rather than optimistic confirmations.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → faculty-judgement → faculty-perception → faculty-action
- **model tier:** Use the realtime tier only for the short conversational framing and interruption; use a cheaper background planner for decomposition, local Mac/browser executors for actions, and faculty-perception for independent postcondition checks.
- **latency:** First acknowledgement under 500 ms; begin safe steps within 2 s; multi-step completion is asynchronous with spoken progress only at checkpoints or failures.
- **cost:** Roughly one inexpensive planning call plus local executor/verifier calls; realtime spend is limited to acknowledgement and exceptions. Dominant cost is model context for long workflows, reduced by sending step summaries and hashes rather than full page contents.
- **security:** Never send browser secrets or full page contents to the pendant. Risk-classify each step, stage irreversible actions for the existing physical approval latch, and stop on an unverifiable postcondition. A failed compensation must be reported as unknown, never hidden.
- **missing:** A durable checkpoint/compensation runner that persists step state and resumes after Mac, browser, or relay interruption; A narrow actionId/attemptId correlation amendment to verify_operation_step; Owner policy data declaring which action classes may run automatically versus staged for approval

### ""I’m back at my Mac—show me what I was doing, and put me back at the exact place I left off.""
- **useful because:** The pendant becomes a physical resume key: it turns the current Mac/browser state and the mind's recent unfinished work into one privacy-preserving resume card, then reopens only the selected app/tab. This solves the daily cost of losing a train of thought across sleep, travel, and interruptions.
- **path:** pendant → mac-planner → mac-vision → browser-extension → relay-realtime → faculty-perception → faculty-action
- **model tier:** Use a cheap background summarizer over structured app/tab metadata and relay job records; use realtime only to disambiguate among a few resume candidates. Perception supplies state, action opens the chosen destination.
- **latency:** List three candidates in under 2 s after the button press; reopen the selected destination in under 1 s. No continuous recording or microphone is needed.
- **cost:** Low: one short summarization call over titles, URLs, timestamps, and job IDs; most work is local state collection and deterministic open_app/open_url actions.
- **security:** Keep URL query strings and document names redacted unless the owner selects a candidate. Never transmit page bodies or credentials. Require an explicit selection before opening a potentially sensitive destination, and verify the resulting app/tab URL after navigation.
- **missing:** A durable cross-surface resume-card schema linking focused app, browser tab/session, unfinished relay job, and last verified checkpoint; A Mac status/read route that returns focused window and stable document identity without screenshots; A pendant trigger path over today's USB serial connection, with LTE treated as optional

### ""Watch this batch while I’m away, and only bother me if it needs a decision or cannot prove it finished.""
- **useful because:** A long-running action can execute locally across a browser and Mac app without keeping a voice session open. The owner receives a compact pendant interrupt only for an approval, a failure, or an independently verified completion, rather than repeated progress chatter.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → faculty-action → faculty-perception → faculty-judgement
- **model tier:** Use a cheap background/scheduled runner and deterministic local actions; reserve realtime for an exception interrupt and use faculty-perception only at checkpoints or final verification.
- **latency:** Start acknowledgement under 1 s; unattended work may run for minutes or hours; interrupt delivery should occur within 2 s of a blocked decision or failed verification.
- **cost:** Low-to-moderate: local execution dominates; model calls are limited to initial decomposition and exception interpretation. Persist compact receipts, not screenshots or full pages.
- **security:** The runner must have an expiry, lease, and kill switch. Irreversible steps pause for the existing physical approval latch. A relay reconnect must not duplicate a step; every attempt needs an idempotency key and a verifier receipt. Private browser content stays on the Mac.
- **missing:** A durable scheduled job runner with idempotent step leases and restart recovery (the existing router alone is insufficient); A pendant event/inbox delivery path for exception-only interrupts while attached by USB today and LTE later; A compact action dashboard or spoken status protocol distinguishing running, waiting-for-owner, verified, failed, and unknown

### ""Freeze everything right now, and make sure nothing on my Mac or in my browser can continue acting until I explicitly unlock it.""
- **useful because:** A true panic stop is different from cancelling one staged transaction: it gives the owner a single physical, fail-closed way to revoke every outstanding automation lease when a device is lost, a browser session looks wrong, or the owner simply wants the system silent.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → faculty-action → faculty-perception
- **model tier:** Deterministic control-plane operation; no expensive model call should be needed. Use realtime only to acknowledge state after the freeze.
- **latency:** Local USB pendant event to lease revocation under 250 ms; all executors must observe the revoked epoch before starting another step.
- **cost:** Very low API cost; most work is signed control messages and executor checks.
- **security:** The freeze must be fail-closed, monotonic, replay-resistant, and usable without network access over the connected USB pendant. It must revoke browser and Mac leases, suppress queued relay work, preserve receipts, and never erase evidence. Unlock should require a deliberate physical gesture plus a fresh authenticated session.
- **missing:** A global revocation epoch shared by relay, Mac executor, and browser bridge; A local USB fast path from the pendant to the Mac control plane; Executor hooks that check the epoch before every action, not only at job start; A distinct pendant indication for frozen versus merely idle

### ""Only interrupt me for things that genuinely matter, and escalate if I keep missing them.""
- **useful because:** The owner gets one coherent attention channel across Mac jobs, browser events, and relay messages instead of either missing urgent work or being trained to ignore constant notifications. The pendant can escalate an unresolved high-priority event while quieting routine completions.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → faculty-judgement → faculty-perception → faculty-action
- **model tier:** Cheap background classifier for urgency and deduplication; realtime is reserved for the actual escalation dialogue. Deterministic timers handle retry and quiet-hour policy.
- **latency:** Classify within 2 s; first alert within 5 s of an event; escalation after configurable delays. Must honor the Mac’s America/New_York quiet-hour calculations while not assuming that is the owner’s physical timezone.
- **cost:** Low: one short classification per candidate event, with hashes and metadata rather than page content; most notifications are suppressed locally.
- **security:** Private event titles and browser content remain on-device unless needed for the spoken alert. The owner must be able to inspect why an event was escalated, snooze it, or permanently mute its source. Never infer urgency from sensitive content without an explicit policy.
- **missing:** A unified attention-event schema with deduplication keys, urgency, expiry, and escalation schedule; A pendant alert acknowledgment/snooze transport over USB now and LTE later; Owner-configurable source and quiet-hour policy rather than hard-coded priorities


## Changes it proposed to its own stack

### `integration` — Add a USB-serial pendant session bridge on the Mac that exposes a signed, framed bidirectional control channel for button events, compact spoken-status cues, approval-latch envelopes, and exception interrupts. It should reconnect safely, queue only bounded control messages, and make LTE an interchangeable transport rather than a prerequisite.
- **owner gets:** The pendant is physically beside the owner and testable now even though LTE registration is absent: a button press can invoke or interrupt real Mac/browser work today, and the same interaction survives when cellular transport is added later.
- effort: Medium: serial framing/reconnect daemon, relay transport adapter, firmware event/status handlers, and an end-to-end test harness using the two connected USB devices. No firmware flash should occur without separate approval.  ·  risk: Malformed or replayed serial frames could trigger actions; bind messages to device/session counters and route approvals through the existing latch. On disconnect, fail closed and leave jobs staged. Recover by restarting the bridge and reconciling receipts.
- cost: Negligible API cost; modest engineering effort. No new hardware cost. USB power is already present; radio remains off in tether mode.  ·  latency: Button-to-Mac event target under 100 ms locally; relay-mediated status may add network latency. Reconnect may take seconds but must not duplicate actions.
- security: USB becomes a local trust boundary: authenticate the device, rotate session nonce, never put secrets/page contents on the pendant, and log frame hashes rather than payloads.
- depends on: Existing physical_transaction_approval_latch envelope and monotonic counter; A serial framing implementation for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; Owner approval before any flash or persistent firmware change

### `memory` — Create a sealed, owner-readable action evidence vault: each completed mutation stores a compact before/after digest, executor receipt, verifier provenance, and human-readable explanation, with automatic expiry and a per-item export/delete control. It should support app-specific reversal metadata without storing screenshots or secrets.
- **owner gets:** When the system changes something important, the owner can later answer “what changed, why, and can I undo it?” without trusting a vague voice confirmation or exposing their entire browser history.
- effort: Medium-to-high: evidence schema, local encrypted storage, retention controls, app-specific reversal adapters, and a small pendant/Mac query surface.  ·  risk: Digests can still reveal timing or document identity, and incomplete reversal metadata could create false confidence. Mark every item reversible, non-reversible, or unknown; never present a reversal as available unless it has been tested and verified.
- cost: Low recurring API cost; storage is compact. Engineering cost is primarily adapters and retention UX.  ·  latency: Negligible on normal actions if receipts are appended asynchronously; querying a history item should take under 2 s.
- security: Keep evidence on the Mac by default, encrypt at rest, redact secrets, and require physical confirmation before exporting or invoking a reversal.
- depends on: A stable action/attempt identity shared across Mac, browser, relay, and verifier; Independent postcondition verification; Owner-selected retention and export policy


## What it asked for

_Nothing._
