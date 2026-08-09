# Harness derivation — faculty-action — round 247

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“When I’m moving, never send or publish anything; queue it and ask me when I’m still.”"
- **useful because:** A worn IMU can detect walking or handling while the Mac/browser can see a staged draft. The system can prevent a hurried public send without requiring the owner to remember a safety command, then resume only after stillness and a deliberate pendant confirmation.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** background for motion classification and policy; realtime only for the short confirmation conversation
- **latency:** Motion classification under 250 ms; queueing is immediate; resume check within 2 s of stillness.
- **cost:** About $0.01–$0.05 per queued decision, dominated by a small judgement call; IMU and relay checks are local.
- **security:** Motion features, not raw sensor streams, leave the pendant. Never transmit message contents to the pendant. Default to queueing when motion or sensor confidence is unknown; require the existing physical transaction approval before irreversible sends.
- **missing:** motion_context_safety_gate firmware skill (already requested and pending); relay policy field for motion-required/stillness-required action classes; Mac/browser executor integration that can leave a draft untouched while paused

### "“Before you click buy/send/book, re-check the exact price, recipient, and account; if anything changed, stop and tell me what changed.”"
- **useful because:** A plan made on one browser snapshot can become unsafe seconds later. This makes the Mac executor and browser extension perform a fresh, independent read immediately before the irreversible step, compare it with the approved digest, and turn drift into a safe pause rather than a wrong click.
- **path:** relay → mac-planner → browser → mac-vision → pendant → dashboard
- **model tier:** background for diffing structured fields; realtime only when explaining a detected drift
- **latency:** Fresh preflight under 3 seconds; no action is released while the preflight is stale or incomplete.
- **cost:** Typically $0.01–$0.08 per guarded action; browser/Mac reads dominate, with model cost only for ambiguous diffs.
- **security:** The pendant receives only a redacted field summary and digest, never credentials or full page contents. A missing or ambiguous field is treated as drift. Approval is bound to the preflight digest and expires after a short deadline.
- **missing:** a first-class preflight digest in the operation envelope; executor support for a mandatory read-only browser/Mac step immediately before commit; dashboard and pendant rendering of a concise drift explanation

### "“Keep an eye on this page for me and interrupt me only if the status, price, deadline, or required action changes.”"
- **useful because:** The browser session can see authenticated state that the relay and pendant cannot. A durable watcher lets the owner delegate waiting: the relay schedules checks, the browser extension reads only the named fields, perception compares snapshots, and the pendant interrupts only on a meaningful change.
- **path:** browser → relay → mac-planner → faculty-perception → pendant → dashboard
- **model tier:** background/scheduled model for polling and structured comparison; realtime only to explain a change when the owner asks
- **latency:** Configurable polling from 5 minutes to 24 hours; alert delivery within one polling interval plus 10 seconds.
- **cost:** $0.01–$0.10 per check depending on page complexity; browser/Mac wakeups and screenshots dominate, not model tokens.
- **security:** The watcher is bound to one URL/session and an explicit field allowlist. Do not retain full page snapshots or secrets; hash or redact unchanged fields. Expire watchers automatically, show the next check and last-observed time, and require physical approval before any follow-up action.
- **missing:** durable watcher records with field allowlists and expiry; a scheduled browser inspection job that can wake the Mac bridge; structured diff and quiet-hours/notification policy across relay and pendant

### "“Make this a private moment.”"
- **useful because:** One deliberate gesture should create a verifiable privacy boundary across every body: the pendant stops retaining audio, the relay refuses durable transcript/context storage, Mac/browser capture and watchers pause, and the dashboard shows what was suppressed. Today privacy is per-surface and the owner cannot know whether a browser watcher or queued job still has access.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** No model needed for enforcement; use the realtime tier only to acknowledge state and explain exceptions.
- **latency:** Pendant acknowledgement under 300 ms; relay/Mac/browser policy propagation under 2 seconds; fail closed if any surface cannot confirm.
- **cost:** Near-zero per event; durable audit receipts and control messages dominate, not inference.
- **security:** The privacy state must be signed, monotonic, and fail closed. It must not claim deletion where data has already left the system; return a per-surface receipt identifying paused, purged, or unknown. A later action cannot silently clear privacy mode; only an explicit physical gesture can do so.
- **missing:** a cross-surface privacy-state protocol with signed epoch and expiry; pendant firmware handling for the privacy gesture and local retention gate; relay enforcement that blocks persistence and invalidates active watcher reads; Mac/browser hooks that pause capture, watchers, and queued observations; a dashboard receipt showing each surface's privacy state


## Changes it proposed to its own stack

### `relay` — Add a mandatory preflight_digest to every irreversible operation: faculty-perception records a redacted, field-level hash from fresh Mac/browser state; faculty-action may commit only if that digest matches the approved envelope and the verifier returns fresh provenance. Any mismatch becomes drift_pending, never an implicit retry.
- **owner gets:** A stale cart, recipient, amount, or appointment cannot silently turn an earlier approval into a different real-world action.
- effort: Medium: operation schema, preflight read adapters, verifier correlation, and pendant/dashboard drift rendering.  ·  risk: A site that changes harmless presentation fields may cause false pauses; recover by classifying fields as semantic or cosmetic and letting the owner re-approve. Never auto-ignore a semantic mismatch.
- cost: Negligible storage; one extra read-only browser/Mac pass and occasional low-cost comparison model call.  ·  latency: Adds up to 3 seconds before commit; safer actions are worth the bounded delay.
- security: Improves security by binding approval to fresh redacted state; page secrets remain outside the pendant and relay summary.
- depends on: verify_operation_step; a correlation field linking operation/action attempt to the preflight receipt; structured field extraction from browser and Mac surfaces


## What it asked for

_Nothing._
## Its own summary

Recorded three owner-facing capabilities: motion-aware safe queueing while moving, fresh preflight drift detection before irreversible clicks, and durable browser condition watchers; also recorded a concrete relay preflight_digest change. The strongest immediate value is preventing a stale approved action from becoming a wrong send/purchase.

**Biggest unknown:** Whether motion_context_safety_gate is actually granted/implemented this round, and which existing scheduler/browser-inspection path can host durable watchers. I still need those implementation decisions, plus owner policy for which action classes may auto-resume after stillness or a watcher condition.

