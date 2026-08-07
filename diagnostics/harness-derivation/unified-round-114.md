# Harness derivation — unified — round 114

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-bridge-recovery** — The home Mac bridge is online, but home-chrome is offline with zero tabs. Owner has repeatedly asked to launch/reconnect the browser bridge without replaying pending commands; current device state supports a safe launch-and-heartbeat workflow but not proof that it exists.
  - evidence: discover(devices) returned home-macbook-bridge online (last seen 2026-08-07T14:55:06.132Z) and home-chrome browser offline, 0 tab(s). owner memory projection lists five bridge-launch requests with failed outcomes.

## Capabilities it proposed

### "“Make the pendant audio clear here.”"
- **useful because:** A single spoken request launches a closed-loop calibration instead of guessing. The pendant records a short local reference and reports modem/link telemetry, the relay evaluates intelligibility and packet loss, and the Mac applies only reversible codec/gain/buffering changes. The owner hears a before/after sample and gets a durable pass/fail profile for this location and link condition—something no Mac-only or relay-only node can establish.
- **path:** pendant → relay-realtime → mac-planner → dashboard
- **model tier:** Use the realtime tier only for the short owner-facing interaction and final explanation; use a background/cheap model (or deterministic DSP) for spectral analysis, packet statistics, and profile comparison.
- **latency:** Begin speaking confirmation in under 1 s; 10–20 s for the calibration burst and analysis; apply changes within 5 s; never interrupt an active conversation without explicit request.
- **cost:** Usually near-zero model cost when DSP/statistics decide; at most one short realtime turn for confirmation/explanation. Dominant costs are LTE-M calibration bytes and optional stored samples; discard raw samples by default.
- **security:** Calibration audio is sensitive and must stay on-device or be streamed transiently; do not retain raw voice unless explicitly pinned. Mac changes are reversible and limited to the pendant audio profile. Require confirmation before changing persistent defaults or uploading diagnostic audio; expose a delete control and a receipt.
- **missing:** A firmware calibration mode that emits/records a bounded reference and exports timestamped link/audio metrics; A relay DSP scorer for 24 kHz target intelligibility, jitter, loss, and half-duplex turn clipping; A Mac action/API to apply and roll back named pendant audio profiles; A dashboard view for before/after score, profile provenance, and deletion

### "“Reconnect my browser bridge, but don’t replay anything pending.”"
- **useful because:** The owner has repeatedly asked this and currently receives a failure. The pendant can acknowledge the request, the relay can inspect and quarantine queued commands, the Mac can launch/restart the bridge, and the browser extension can prove a fresh heartbeat before any command is released. This turns a fragile manual recovery into a safe, observable operation.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic state checks and the background job runner should do the work; realtime is used only to speak the immediate status and final result.
- **latency:** Speak 'I’m reconnecting it without replaying commands' within 1 s; launch and heartbeat verification within 15 s; if unavailable, report the exact blocked stage rather than retrying indefinitely.
- **cost:** Negligible model cost; a few relay/database operations and one Mac launch action. No page content or audio needs to leave the device.
- **security:** Quarantine, do not delete, pending commands; preserve IDs and idempotency keys. Never auto-submit browser actions during recovery. Require confirmation to release the quarantined queue later, and audit who/what launched the bridge.
- **missing:** A bridge lifecycle state machine with launch/heartbeat/degraded states; A queue quarantine operation distinct from replay or deletion; A fresh browser heartbeat challenge bound to the bridge instance and session; A Mac allowlisted open/restart action for the bridge app and a dashboard release/inspect control

### "“Before you do that, tell me exactly what data will leave my devices, where it will go, and how long you’ll keep it.”"
- **useful because:** Today the owner must trust a multi-surface task without seeing its data boundary. This would give them a concise spoken privacy preview before work begins: which microphone snippets, browser fields, files, and telemetry are involved; which node processes each; retention and deletion behavior; and which steps require approval. It makes the hive usable for sensitive work without forcing the owner to understand its internals.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use deterministic policy evaluation and typed data-flow metadata for the preview; reserve realtime model usage for translating the result into one short spoken sentence and answering follow-ups.
- **latency:** Under 1 second for a preview of a planned task; under 3 seconds if browser tabs or Mac files must be inspected to enumerate fields. No action starts until the preview is delivered when the owner requests it.
- **cost:** Negligible model cost; mostly local metadata and policy evaluation. No sensitive content should be sent merely to produce the preview.
- **security:** The preview itself must not reveal secret values, only categories and destinations. Treat missing provenance or retention metadata as a stop condition. Require explicit confirmation for voice, private browser content, credentials, or cross-device transfer; record the approved scope and invalidate it when the plan changes.
- **missing:** A typed data-flow manifest attached to every plan and action, including field category, source surface, destination, purpose, retention, and deletion path; A policy evaluator that computes the union of data leaving each device before execution; A redacted spoken/visual preview renderer and confirmation token bound to the exact plan hash; Instrumentation from pendant audio, Mac actions, browser extraction, relay storage, and model calls


## Changes it proposed to its own stack

### `integration` — Add a versioned AudioProfile transaction spanning pendant, relay, and Mac: calibration creates a profile with codec/sample-rate/gain/jitter-buffer parameters plus measured conditions and expiry; relay validates bounds, Mac applies it through an allowlisted action, and a commit/rollback receipt is written only after a post-apply sample passes. Keep the prior profile for one-click rollback and make raw calibration audio ephemeral by default.
- **owner gets:** The owner can ask for clearer audio in a noisy or weak-signal place and know the system either improved it or restored the old settings. It prevents silent half-applied tuning and avoids keeping their calibration speech indefinitely.
- effort: Medium: shared schema and receipt state machine, firmware calibration command, deterministic scorer, Mac apply/rollback adapter, and dashboard status.  ·  risk: A bad profile could make speech worse or cause reconnect churn. Enforce parameter bounds, apply atomically at conversation boundaries, time-limit profiles, and auto-rollback on failed post-apply score or missing acknowledgement.
- cost: Small implementation cost; no recurring model cost when scoring is deterministic. Calibration adds one short LTE-M exchange and optional tiny metrics record; raw audio storage is zero by default.  ·  latency: Adds roughly 10–20 seconds only when the owner explicitly calibrates; normal conversations are unchanged.
- security: Metrics may reveal location/time patterns; minimize and expire them. Raw voice stays transient unless the owner explicitly saves diagnostics. Persistent profile changes require explicit confirmation.
- depends on: Firmware calibration mode and 24 kHz-compatible audio path; Relay deterministic audio-quality scorer; Mac allowlisted profile apply/rollback action; Receipt/undo storage with profile provenance

### `context` — Make data provenance a first-class, immutable PlanManifest carried from /plan through every execution step: each step declares input categories, source surface, destination, model/provider, retention, deletion route, and approval requirement; execution rejects scope drift and emits a redacted owner-facing privacy preview plus a hash-bound confirmation receipt.
- **owner gets:** Before asking the pendant to touch private mail, browser sessions, files, or voice, the owner can know exactly what will cross boundaries and can safely approve or refuse the specific plan instead of granting broad invisible trust.
- effort: Medium-to-high: typed manifest schema, instrumentation adapters for pendant audio/Mac/browser/relay/model calls, policy evaluation, redaction, and drift tests.  ·  risk: Incomplete instrumentation could create false reassurance. Default unknown fields to blocked, fail closed on unregistered destinations, and run a shadow audit period before enabling approvals.
- cost: Small storage and computation overhead per plan; no meaningful model cost. Privacy previews should avoid transmitting sensitive payloads.  ·  latency: Sub-second for metadata-only plans; up to a few seconds for enumerating browser/file sources. Execution is delayed only when explicit approval is required.
- security: Improves confidentiality and auditability, but manifests themselves can reveal sensitive structure. Encrypt them, redact values, apply short retention, and restrict dashboard access.
- depends on: Typed action metadata from Mac and browser harnesses; Pendant audio provenance and retention events; Relay/model call instrumentation; Approval token and plan-hash enforcement


## What it asked for

_Nothing._
