# Harness derivation — faculty-action — round 26

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **execution readiness** — Relay and Mac bridge are reachable, but local agent is not ready for computer-use: Accessibility and Screen Recording are untrusted/missing; browser extension is offline with 3 pending commands. Any approved browser action must wait or be explicitly queued, not claimed complete.
  - evidence: GET /ops/status returned ready:false, permissions.accessibility.trusted:false, permissions.screenRecording.granted:false, browserExtension.online:false, pendingCommands:3; GET /browser/status matched offline state.

## Capabilities it proposed

### "When you say “send it,” “buy it,” or “change it,” show me a concise description and the exact final values; I can approve that specific action with one deliberate pendant press, and you carry it out wherever it belongs, even if I leave the Mac before completion."
- **useful because:** The mind can judge and prepare a consequential action, but today approval is conversational and can be detached from the exact browser/Mac state. This binds the owner's physical, deliberate gesture to a hash of the reviewed action, then lets relay, Mac, and authenticated browser execute it and return an auditable receipt. It is useful precisely because no single node has both the private session, the durable queue, and the owner's physical confirmation.
- **path:** relay-realtime → faculty-judgement → faculty-action → relay-realtime → mac-planner → mac-vision → browser-extension → unified → dashboard
- **model tier:** Use realtime only to explain the pending action and hear a short verbal review; use a cheaper background planner to normalize fields and compute the action digest; deterministic relay/Mac/browser executors perform the action, with no model deciding after approval.
- **latency:** Preview in under 2 seconds when state is available; pendant confirmation is immediate; execution may take seconds to minutes after the owner walks away, with a durable spoken/status receipt and retry/undo where supported.
- **cost:** Low per invocation: one short realtime turn for preview/confirmation, then mostly D1/R2 metadata and deterministic Mac/browser calls. Cost is dominated by any required private-page extraction or vision step, not the confirmation protocol.
- **security:** Never include cookies or full private page contents in the digest. Store a redacted canonical action summary, target origin/session identifier, before-state hash, final-value hash, expiry, and nonce. Reject replay, stale tab state, changed totals, changed recipients, or scope expansion; require a fresh confirmation. Destructive or financial actions need explicit category policy and a visible cancel window. The pendant's button is proof of physical presence, not identity against an attacker with device access.
- **missing:** A relay endpoint for pending-action envelopes, nonce/expiry, atomic consume, and receipt streaming; A pendant firmware confirmation mode (preview token, one deliberate press, cancel/timeout, offline queue); A shared canonical action schema/digest library used by judgement, relay, Mac, and browser; Browser bridge online/reliable tab affinity and Mac Accessibility/Screen Recording grants for execution; Dashboard and spoken receipt UI showing exactly what was approved and what actually changed

### "If something I asked you to do starts going wrong, let me say “stop” or hold the pendant button and have every participating hand halt immediately, quarantine the job, and tell me exactly what already happened and what did not."
- **useful because:** Today a queued Mac/browser job can continue after the owner leaves, while the pendant is the only continuously present control surface. An undo is too late for an email, purchase, deletion, or partial multi-step workflow. A relay-coordinated abort lets the owner interrupt in-flight work across the private browser, Mac automation, and durable worker, then produces a truthful partial-execution report.
- **path:** relay-realtime → faculty-action → mac-planner → mac-vision → browser-extension → mac-terminal → dashboard-ux
- **model tier:** Realtime handles only the low-latency stop phrase and acknowledgement. Deterministic cancellation tokens, executor checkpoints, and receipt assembly do the safety-critical work; a cheaper background model may summarize the partial result after all executors report.
- **latency:** A local pendant stop acknowledgement should be immediate; relay propagation target under 500 ms when connected and best-effort delivery after reconnection. Each executor must checkpoint before every side-effecting step and report cancellation within one step.
- **cost:** Low API cost: mostly signed control messages and D1 job state. Cost is dominated by any post-abort evidence extraction or screenshot, which should be optional and background.
- **security:** The stop command must be authenticated to the paired pendant, signed, nonce-protected, and scoped to one job or action family. Cancellation must be fail-closed for unstarted side effects but honest that an already-committed external action cannot be recalled. Never claim rollback; show per-step committed/skipped/unknown states. Browser and Mac adapters need idempotent cancellation and a quarantine state that blocks retries until the owner resumes or discards the job.
- **missing:** A relay control plane with signed abort tokens, fan-out delivery, replay protection, and durable quarantine state; A common executor protocol with step checkpoints, cancellation acknowledgements, and committed/unknown/skipped receipts; Mac and browser adapters that check cancellation before each side effect and stop computer-use loops safely; Pendant firmware support for a distinct stop gesture that works offline and flushes on reconnect; Dashboard/spoken status for partial execution, plus an explicit resume/discard operation


## What it asked for

### `s2-08hj` (skill) — physical_action_confirmation
- does: Receives a signed, human-readable pending-action envelope from the relay, plays a short preview cue/text/audio reference, accepts exactly one deliberate second press as approval, or a long press as cancel. It returns the envelope nonce plus a device-generated confirmation event; it refuses expired, already-consumed, or digest-mismatched envelopes and can hold the event offline until LTE-M returns.
- must be on-device because: The approval must be a deliberate physical act by the person wearing the pendant and must remain safe if the link drops between preview and approval. Server-side voice confirmation cannot provide that physical presence or offline persistence.
- trigger: Server push of a pending envelope, followed by the pendant's second button press; timeout and long-press cancellation are local triggers.
- storage: Encrypted microSD append-only queue: envelope digest, nonce, expiry, decision, monotonic counter, and receipt pointer; roughly 1–4 KB per pending action, delete after relay acknowledgment.
- RAM budget: ~12–20 KB RAM for one envelope, button debounce/long-press state, digest verification, and queue buffering; audio preview should reuse the existing playback path rather than buffer a full recording. Fits comfortably within 211,608 B application RAM, subject to current firmware integration.

## Its own summary

Added a new cross-node capability: physical_action_confirmation. A canonical, expiring action digest is reviewed, approved by one deliberate pendant press, atomically consumed by relay, executed by Mac or authenticated browser, and returned as a receipt. Added a pendant firmware skill request for offline-safe confirmation/cancel/queue behavior. Current live checks show relay/Mac bridge reachable but Mac Accessibility and Screen Recording are missing and browser bridge is offline with three pending commands; recorded this so no action is falsely reported complete.

**Biggest unknown:** Whether the owner wants physical button approval for all high-impact actions or only financial/destructive/external-send categories; the pending owner-policy context request has not arrived.

