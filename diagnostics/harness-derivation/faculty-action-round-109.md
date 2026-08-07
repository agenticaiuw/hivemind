# Harness derivation — faculty-action — round 109

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-bridge** — The browser bridge is currently offline or timing out: authenticated browser actions cannot be relied on until Safari's extension polls successfully.
  - evidence: GET /jobs returned recent browser_navigate failures explicitly citing extension offline and Safari timeout; GET /browser/sessions returned only stale sessions.
- **audio-24khz** — The Mac-to-relay TTS path currently renders and uploads 24 kHz mono PCM successfully, but no pendant is connected to verify download/playback.
  - evidence: GET /pipeline showed TTS done with format s16le, sampleRate 24000, channels 1, pcmBytes 75734, clippedSamples 0, then relay_result done.

## Capabilities it proposed

### "“Resume the thing that got interrupted.”"
- **useful because:** Today a queued task can end in a browser timeout, an offline pendant, or a Mac approval gate, and the owner has to reconstruct what happened. This capability would inspect the durable job and receipts, distinguish completed from untouched steps, re-check current preconditions on the correct surface, continue only safe/reversible work, and give a concise spoken receipt. It is genuinely cross-surface: the pendant supplies the terse resume intent, relay owns durable state, Mac executes, and browser sessions provide authenticated continuity.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use the realtime tier only to resolve the short resume reference and speak the acknowledgment; use a cheaper background/local planner to reconcile receipts, preconditions, and retry steps. Escalate to realtime only for ambiguity or approval.
- **latency:** Acknowledge in under 1 second; reconcile within 2 seconds; retries may continue as a durable job and report completion later.
- **cost:** Approximately $0.005–$0.03 per invocation; dominant costs are background planner tokens and any browser/page extraction, not the short realtime turn.
- **security:** Private browser URLs/content and Mac receipts leave the device only through the authenticated relay. Never retry irreversible steps automatically; require confirmation for send/delete/purchase. Persist only job IDs, step hashes, and outcome summaries, with short retention for page evidence.
- **missing:** A first-class resume/retry route that understands step-level receipts and safe retry policy; Precondition verification and idempotency metadata per action; A durable user-facing pending/approval state that the pendant can query when the Mac or browser is offline

### "“Stop everything now.”"
- **useful because:** The owner needs a physical, immediate escape hatch when the Mac or browser is acting unexpectedly—without finding the dashboard or speaking a longer explanation. A deliberate pendant gesture would revoke the active execution lease across the relay, Mac, and browser, cancel queued reversible work, and prevent an approval-gated step from being released. It is a new cross-surface emergency control, not merely an activity log or ordinary undo.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** No expensive model is needed: firmware and relay perform the stop deterministically. Use a cheap background model only to summarize what was halted after the fact; realtime speaks a brief acknowledgment if the link is live.
- **latency:** Local haptic/LED acknowledgment in under 100 ms; relay cancellation propagation under 500 ms when connected; persist the stop locally and apply it when connectivity returns.
- **cost:** Negligible per invocation, under $0.001 for event storage and optional summary. Hardware cost is zero if the existing button/LED can support a guarded long press.
- **security:** A false trigger could interrupt useful work, so require a deliberate 1.5–2 second hold plus distinct vibration/LED confirmation. Cancellation must fail closed: once stopped, no queued irreversible action may run until a new explicit intent. Store only job ID, step ID, and cancellation reason; never speak private page contents.
- **missing:** Pendant firmware gesture and durable local stop latch that survives link loss; Relay-wide revocable execution leases understood by Mac and browser workers; Cancellation propagation and acknowledgement in the Mac/browser action protocols; Dashboard view showing exactly which steps stopped, completed, or remain untouched


## Changes it proposed to its own stack

### `integration` — Add a resumable-work coordinator between the relay job store, action receipts, Mac executor, and browser session store. On resume, it loads the last job graph, verifies each step's idempotency key and preconditions, marks completed steps immutable, retries only safe untouched/failed steps with exponential backoff, and pauses at an irreversible or approval-gated step. Emit pipeline events for resumed, skipped, blocked, and completed states and expose a compact pendant-safe status/receipt.
- **owner gets:** If Wi-Fi, Safari, or an approval dialog interrupts work, the owner can say “resume that” instead of repeating actions or wondering whether something was sent twice. They get an honest spoken result and no duplicate side effects.
- effort: Medium-high: shared action schema, coordinator state machine, receipt linkage, retry tests across Mac and browser, plus dashboard and relay status wiring.  ·  risk: A bad idempotency key could skip needed work or duplicate a mutation. Default to fail-closed on unknown keys, require explicit confirmation for irreversible steps, and allow undo for completed reversible actions. Recovery is to abandon the run and start a new job from the immutable receipt graph.
- cost: Low incremental API cost (roughly $0.001–$0.01 per resume for orchestration); storage increases by a small step graph and event records per job.  ·  latency: Sub-second acknowledgment; 0.5–2 seconds for reconciliation before execution, with long browser/Mac work remaining asynchronous.
- security: No new credential access; reuse authenticated relay and browser sessions. Store hashes and minimal evidence by default, redact page content from spoken receipts, and enforce per-step approval policy.
- depends on: A typed step/idempotency/precondition schema shared by Mac and browser executors; A durable coordinator worker (not just the current request/receipt endpoints); Pendant connectivity for spoken status; otherwise dashboard remains the fallback

### `firmware` — Implement a hardware-level emergency-stop latch on the pendant: a guarded long press (for example, 2 seconds) sets a persistent stop bit, emits a distinct vibration/LED pattern, and transmits a signed stop event whenever LTE reconnects. The relay treats that event as a global revocation for the owner's active execution leases; Mac and browser workers poll/subscribe to lease revocations and must abort before their next side effect. Clearing the latch requires a separate deliberate gesture and a fresh owner intent.
- **owner gets:** The owner can halt an unexpected automation immediately from the device in their hand, even when speech, Safari, the dashboard, or the network is unavailable. It prevents a queued action from continuing silently after the owner has lost trust in the run.
- effort: Medium: firmware button state machine and persistence, authenticated event type, relay lease registry, cancellation hooks in both executors, and an end-to-end fault-injection test for link loss and reconnect.  ·  risk: Accidental stops interrupt work; use a long press and unmistakable feedback. A worker that fails to receive revocation could still act, so every side-effecting action must validate a short-lived lease immediately before execution. Recovery is to inspect receipts, clear the latch intentionally, and start a new transaction.
- cost: Near-zero API cost; approximately 1–4 KB firmware flash/RAM plus a few bytes of nonvolatile state. No new hardware cost if the existing button and LED are sufficient.  ·  latency: Local stop feedback is immediate; network-connected cancellation should occur within 0.5–2 seconds, with fail-closed checks at each subsequent action.
- security: Requires authenticated, replay-protected stop events and owner/device binding. The stop bit should reveal only job identifiers and status, not private browser or Mac data.
- depends on: A signed pendant event format and reconnect queue; Relay execution leases with revocation and expiry; Mac and browser executors checking the lease before every side effect; A dashboard receipt that distinguishes cancelled, completed, and never-started steps


## What it asked for

_Nothing._
