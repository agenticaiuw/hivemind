# Harness derivation — mac-terminal — round 117

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-readiness-2026-08-07** — Live /observe and /ops/status show fullControlMode=true but the actual AI Pendant Agent binary is not Accessibility-trusted, Screen Recording is false, and browser extension home-chrome is offline with 10 pending commands. UI action receipts are explicitly untrustworthy under this state.
  - evidence: GET /observe at 2026-08-07T14:40:28Z; GET /ops/status at same time.

## Capabilities it proposed

### "“Did that actually happen?” — verify the real-world result across my Mac and logged-in browser, not just whether an agent returned success, and tell me what is confirmed, what is only prepared, and what could not be checked."
- **useful because:** The current Mac observation proves that UI actions can report success while doing nothing when Accessibility is unavailable, and browser commands can sit pending while the extension is offline. A spoken postcondition check would make the hive dependable when the owner cannot inspect the screen.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** deterministic first for receipts, readiness, and browser results; background model only to summarize conflicting evidence; realtime only for the owner's live spoken follow-up
- **latency:** Under 2 seconds for receipt/readiness checks; up to 10 seconds only when a fresh browser or Mac verification action is necessary.
- **cost:** Usually near-zero model cost for structured checks; roughly 2k–4k input tokens only when evidence conflicts and a background summary is needed. The dominant cost is an optional fresh verification action, not planning.
- **security:** Verification may read private page contents or app state. Limit it to the job's bound tab/session and relevant Mac evidence, redact secrets from spoken output, and never perform a compensating mutation merely to verify. Tell the owner when confirmation is inferred rather than directly observed.
- **missing:** A shared postcondition/evidence schema linking Mac job receipts, /observe readiness, browser command results, and timestamps.; A verifier that distinguishes attempted, applied, observed, and confirmed states instead of treating executor success as completion.; Browser extension reconnection handling so queued commands get an explicit expired/ran result rather than remaining ambiguous.

### "“I’m offline right now—remember this exactly and carry it out when the right device comes back, but tell me if anything changed before you do it.”"
- **useful because:** A pendant is often used precisely when the Mac, browser bridge, or relay is temporarily unavailable. Today an offline utterance can be lost or become an opaque queued command. The owner needs durable intent continuity with explicit freshness and conflict handling, not merely eventual execution.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic event logging and replay for capture, deduplication, expiry, and device handoff; background model for re-planning only when the original context has changed; realtime only for the immediate acknowledgement.
- **latency:** Immediate local acknowledgement under 300 ms; synchronization on reconnect within 5 seconds; re-planning may take up to 10 seconds before any consequential action.
- **cost:** Near-zero model cost for storing, syncing, and checking timestamps/hashes. Background re-planning is typically 2k–6k input tokens per stale intent; the expensive model is unnecessary unless the changed context is genuinely ambiguous.
- **security:** The relay must store encrypted intent envelopes, not unrestricted audio or credentials. Bind each intent to its originating user/session and permitted surface, expire sensitive intents, and never replay a stale browser submission or destructive Mac mutation without a fresh owner instruction.
- **missing:** An append-only intent envelope with client timestamp, source surface, target capability, semantic hash, expiry, and causal predecessor.; A reconnect synchronizer that performs idempotent delivery across relay, Mac jobs, and browser commands while returning conflict states instead of silently replaying.; A stale-context resolver that compares the original evidence capsule/page fingerprint/Mac state with current state and asks the pendant for clarification when they diverge.; A pendant-local durable queue so capture survives a dropped relay link and power-cycle.


## Changes it proposed to its own stack

### `integration` — Add a readiness-aware action contract across Mac planner, relay, and pendant. Before any UI-dependent Mac action (ui_click, ui_menu, type_text, press_keys, screenshot/computer-use), the planner reads GET /observe and records a capability snapshot (Accessibility, Screen Recording, secure input, browser online state). The executor must attach that snapshot and a machine-readable precondition result to the job receipt; if UI reachability is false, it should automatically choose a non-UI route when one exists (shell/AppleScript/browser command), otherwise return a truthful blocked/unavailable result. Relay and pendant responses should render that state distinctly from success (e.g. “prepared but not applied”), including the exact missing permission or offline surface. Re-check readiness after reconnect/permission changes and annotate queued browser commands with the surface state that existed when queued.
- **owner gets:** Today a job can say it succeeded while doing nothing: live observation shows Accessibility is untrusted and Screen Recording is missing, while browser commands are queued against an offline extension. The owner would stop receiving false completion claims and could still get work done through alternate Mac or browser paths automatically. This is especially valuable when they are away from the screen and only hear the pendant.
- effort: Medium: typed readiness schema, planner preflight, executor receipt fields, relay serialization, and a small pendant vocabulary/UI state. No new model is required.  ·  risk: A stale readiness snapshot could incorrectly suppress a newly available route or produce a false fallback. Use a short TTL, re-check on retry, and preserve raw probe evidence in the receipt. Do not block unrestricted shell work; this is truthfulness and routing, not an approval gate.
- cost: Negligible API cost; one local observation call per UI job. Avoids expensive vision/planner retries when the host cannot interact. Storage is a few hundred bytes per receipt.  ·  latency: ~10–50 ms for local preflight; faster overall by avoiding doomed 25-step UI loops.
- security: Improves disclosure of permission and browser-state facts without granting new access. Receipts should redact paths/tokens and expose only capability booleans plus remediation text.
- depends on: Actual Accessibility permission for AI Pendant Agent (and Screen Recording for screenshots) remains missing; the contract must work honestly before those are granted.; A shared readiness schema consumed by mac-planner, faculty-action, and relay-realtime.; Browser extension heartbeat/online state and durable command queue must remain available.


## What it asked for

_Nothing._
