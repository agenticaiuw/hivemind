# Harness derivation — faculty-action — round 134

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live-action-surfaces** — Mac bridge and Safari extension are online, but the live ops snapshot reports Accessibility and Screen Recording ungranted and ready=false. Pipeline history includes a pending shell approval and an nRF9160 source event, while the device table still has no live pendant entry; USB-local serial proxy is not an existing route.
  - evidence: GET /ops/status 200; GET /browser/status 200; GET /pipeline 200; GET /capabilities 200

## Capabilities it proposed

### "“Make this a handoff I can finish later.” From the pendant, capture the current Mac/browser work state into a resumable card: active app and tabs, selected text or page region, pending draft/action, source links, and the next safe step. Put the card in a queue I can reopen from the pendant or Mac, and when I return say exactly what is still pending—never submit or send anything implicitly."
- **useful because:** The owner can leave a thought mid-task and recover it later without reconstructing context. It requires the worn device to mark the moment, the Mac/browser to gather private state, and the relay to preserve a compact handoff while devices disconnect.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → unified
- **model tier:** background for extracting and compressing the state; realtime only for the spoken confirmation and resume command.
- **latency:** Capture acknowledgement under 2 seconds; card assembly under 10 seconds; resume should begin within 3 seconds.
- **cost:** About $0.01–$0.05 per capture/resume, dominated by private-page extraction and summarization; most resumes should be deterministic with no model call.
- **security:** Private tab contents and drafts leave the Mac only to the authenticated relay; redact passwords, tokens, payment data, and hidden form fields. Resume cards expire and require explicit confirmation before any external mutation.
- **missing:** A first-class handoff-card schema and persistence/expiry route; Mac snapshot of focused app, selection, and draft without Accessibility (AppleScript/browser bridge fallback is partial); Pendant trigger and local acknowledgement over the currently USB-attached serial link

### "“Run this until it reaches the first decision point, then bring me in.” Execute a multi-surface task (for example, gather an order return, fill the reversible parts, and prepare the final page) while continuously checking that the page, account, and target are still the intended ones. Stop at the first irreversible or ambiguous step, send me a compact spoken summary plus before/after evidence, and let me approve, revise, or cancel from the pendant."
- **useful because:** This is the practical boundary between an assistant that merely drafts and one that actually gets work done: long tasks proceed without babysitting, but the owner is never surprised at the commit point. Browser sessions, Mac actions, relay persistence, and pendant interruption are all necessary.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → faculty-judgement → faculty-action
- **model tier:** background/cheap model for routine extraction and step checking; realtime model only for ambiguity resolution and the final spoken approval exchange.
- **latency:** Steps execute serially with progress updates within 5 seconds of each transition; decision packet under 3 seconds after a stop condition; approval takes one button or short utterance.
- **cost:** $0.03–$0.20 per task, mostly page interpretation; deterministic navigation and receipts should avoid repeated model calls.
- **security:** Never rely on stale DOM or an old approval. Bind every mutation to tab/session, URL, account identity, and a fresh evidence hash; redact sensitive fields from spoken output. Require explicit owner approval for send/submit/purchase/delete.
- **missing:** A durable step state machine with stop conditions and resumable leases; Fresh evidence/precondition verification before each mutation; A pendant-native approve/edit/cancel interaction that survives a dropped network link

### "“Tell me when the thing I asked for is truly finished, not merely handed off.” For every delegated Mac/browser job, keep working after the conversation ends, verify the final observable outcome on the target app or page, and deliver a short pendant notification containing outcome, evidence, and any remaining manual step. If the target disappears or changes, report “not verified” instead of claiming success."
- **useful because:** Owners currently have to ask whether a job happened; this turns delegation into trustworthy completion. The relay can stay awake, the Mac/browser can act in private sessions, and the pendant can notify without reopening the whole conversation.
- **path:** relay-realtime → mac-planner → browser-extension → pendant → faculty-perception → faculty-action
- **model tier:** Cheap background worker for polling and deterministic verification; realtime only when the owner asks for a detailed explanation.
- **latency:** Notify within 10 seconds of completion or failure; verify with at least one fresh readback, not just an action receipt.
- **cost:** $0.005–$0.05 per job after initial delegation; polling and readback dominate, with model use only for non-structured outcomes.
- **security:** Notifications must avoid exposing private page contents to anyone nearby; use a neutral LED/vibration pattern and speak details only after an owner interaction. Do not retry potentially duplicating external actions.
- **missing:** Outcome-specific verification adapters for Calendar, Mail, browser forms, and filesystem; Relay-to-pendant notification delivery over LTE or the present USB serial proxy; A distinction between accepted, executed, and externally verified job states

### "“Move this appointment everywhere it appears.” Find the appointment across Calendar, reminders, notes, drafts, and relevant logged-in pages; prepare one coordinated change set; show me a single diff of every affected record; then commit the changes together or leave every reversible local edit unapplied if any target cannot be verified."
- **useful because:** Today an assistant can edit individual surfaces but cannot keep a real-life fact consistent across them. The owner gets one trustworthy operation instead of manually hunting for stale copies after a reschedule.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Background model for entity matching and cross-surface reconciliation; realtime only for the spoken diff and commit confirmation.
- **latency:** Initial inventory under 20 seconds; diff under 5 seconds after discovery; commit only after explicit confirmation.
- **cost:** $0.05–$0.30 per coordinated change, dominated by private-page extraction and entity matching.
- **security:** Do not infer that similarly named events are identical without evidence. Every mutation needs a source locator, old value, new value, and independent readback. External messages remain drafts unless separately approved.
- **missing:** Cross-application transaction coordinator with prepare/commit/abort phases; Entity identity and conflict rules for Calendar, Reminders, Notes, Mail, and browser pages; Compensating operations for targets that cannot participate in a transaction; One pendant-visible confirmation of the complete diff

### "“If something only partly worked, make the situation safe and tell me exactly what remains.” After any multi-step Mac or browser job fails, compare the intended state with the actual state across all touched surfaces, undo reversible partial changes where safe, prepare compensating drafts for external changes that cannot be undone, and leave a precise recovery checklist with evidence."
- **useful because:** A failed automation currently leaves the owner to investigate whether half the task happened. This capability turns partial failure into a bounded recovery task rather than silent inconsistency or duplicate retries.
- **path:** relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-action → pendant
- **model tier:** Cheap deterministic verifier and compensation planner first; realtime model only to explain ambiguous residual state.
- **latency:** Failure classification within 5 seconds; recovery proposal within 15 seconds; no automatic retry of an external mutation.
- **cost:** $0.02–$0.15 per failed job, mainly fresh verification and residual-state reasoning.
- **security:** Never claim rollback when an external service provides no confirmation. Compensation messages are drafts. Preserve an append-only audit trail and expose sensitive details only after pendant interaction.
- **missing:** Per-action pre/post snapshots and semantic compensation handlers; Cross-surface residual-state verifier; A failure state distinct from cancelled, undone, and externally verified; Pendant notification that clearly says partial failure rather than success

### "“Give me a safe delegation budget for the day.” Let me authorize a bounded class of actions—specific services, maximum spend, time window, data scope, and a per-action count—from the pendant. The system may complete matching routine tasks without interrupting me, but must refuse anything outside the signed budget and give me a spoken/LED explanation."
- **useful because:** The owner currently has to approve each task interactively or grant broad trust to an agent. A time-limited, narrow delegation budget makes useful unattended work possible while preserving a physical escape hatch.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-judgement → faculty-action
- **model tier:** Deterministic policy engine for authorization and enforcement; background model may classify task intent, but never expands the budget.
- **latency:** Budget check under 100 ms locally; routine tasks proceed without a model round trip; exceptions notify within 2 seconds.
- **cost:** Negligible policy-check cost; $0.01–$0.10 for optional task classification and evidence summaries.
- **security:** Budgets must be cryptographically scoped, expire automatically, and bind to account, browser session, target service, and action type. No budget may authorize password changes, credential access, or unrestricted shell. A physical pendant cancel must revoke it immediately, including offline propagation when the link returns.
- **missing:** Signed delegation-token format and enforcement middleware across Mac, browser, and relay; Budget ledger with expiry, counters, and spend tracking; Offline-safe revocation/cancel propagation; A pendant UI for reviewing and revoking active budgets


## Changes it proposed to its own stack

### `integration` — Add a USB-attached pendant/bridge proxy on the Mac agent. Enumerate /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA, frame button/LED/audio-control messages with sequence numbers and heartbeats, and expose the pendant as a local device session to the relay. Translate relay job progress and cancel into LED patterns and button events, while explicitly marking this as USB-local (not LTE-registered). Keep serial access exclusive, reconnect safely, and never flash firmware.
- **owner gets:** The owner can wear and test the real control surface today while it is physically tethered to the Mac: tap to start/stop, see whether a delegated action is running, and cancel it without reaching for the keyboard. This makes the prototype useful now rather than waiting for LTE registration.
- effort: Moderate: a small Mac serial service, framing protocol, device-session adapter, and integration tests using loopback/fake serial; no firmware flash required.  ·  risk: A stale or noisy serial link could misreport state or consume the port needed by a developer. Use a lockfile, heartbeat timeout, reconnect backoff, and fail-closed cancel semantics; provide a one-command disable and leave the existing Mac/browser paths unaffected.
- cost: Negligible API cost; roughly one background Mac process and <1 MB memory. No hardware purchase; existing USB devices are used.  ·  latency: Button/LED control should be under 100 ms locally; relay job status remains network-bound. Heartbeats every 1–2 seconds add trivial USB traffic.
- security: Local serial is privileged physical control: accept only the known USB VID/PID/serial identities, authenticate the relay session, and do not expose raw audio or serial bytes to logs. USB-local state must not imply LTE reachability.
- depends on: A documented framed serial protocol for the nRF9160 and ESP32 bridge; A relay device-session endpoint that can represent USB-local connectivity; An owner-run serial permission/configuration step if macOS denies the agent access


## What it asked for

_Nothing._
