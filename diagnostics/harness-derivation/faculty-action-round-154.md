# Harness derivation — faculty-action — round 154

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser bridge live state** — Safari browser bridge is online with 9 tabs (active x.com), but reports empty capabilities and empty nonce; pendingCommands=0 and staleForMs≈10.4s at probe time. This is a concrete integration gap for authenticated, capability-scoped execution.
  - evidence: describe GET /browser/status returned HTTP 200 with online:true, tabCount:9, capabilities:[], nonce:"", pendingCommands:0.

## Capabilities it proposed

### ""Handle this request across my Mac and browser, but don't tell me it worked until every step is independently verified; if a step fails, stop and tell me exactly what remains.""
- **useful because:** This is the core missing hand: multi-step work becomes trustworthy rather than a sequence of optimistic tool receipts. The planner can act, faculty-perception can verify fresh state, and the pendant can report verified/unknown without exposing secrets.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background for planning; realtime only for the short owner-facing status exchange
- **latency:** Initial plan under 2 s; each action step 1–5 s; verification within 2 s of each step; no silent timeout
- **cost:** Low-to-moderate: one planning call plus cheap verifier calls; browser/Mac latency dominates, not tokens
- **security:** Sensitive fields stay on Mac/browser; verifier returns hashes or minimal snippets. Mutations above the owner's policy threshold require the existing physical approval latch. On disconnect, mark unknown rather than retrying blindly.
- **missing:** A durable transaction coordinator that chains existing executor receipts to verify_operation_step and records per-step verified/unknown; A narrow actionId/attemptId correlation field in the granted verifier; A policy-controlled stop/compensation decision for partially completed workflows

### ""When I say 'prepare me for my next meeting,' use the pendant as the physical trigger, read the next calendar event on the Mac, gather only the relevant browser tabs/files, and speak me a private 30-second brief; never send or change anything.""
- **useful because:** It turns the wearable into a genuinely useful cross-node morning/transition assistant: calendar truth comes from the Mac, authenticated context comes from the browser, and the pendant provides the low-friction trigger and private audio output.
- **path:** pendant → mac-bridge → browser → relay-realtime → dashboard
- **model tier:** background for gathering/summarization; realtime for the spoken brief
- **latency:** Trigger acknowledgement under 300 ms; brief ready within 10 s; speak immediately when complete
- **cost:** One small summarization call per request; browser and local file inspection dominate; no recurring spend when unused
- **security:** Read-only by default; restrict collection to event-linked domains/paths, redact credentials and unrelated tabs, and require confirmation before opening or transmitting anything outside the Mac.
- **missing:** Calendar-to-context linker that resolves attendees, URLs, and local documents without broad tab scraping; A pendant gesture/command route usable while USB-attached today and LTE later; Private audio routing that guarantees the brief is not emitted until the owner explicitly triggers it

### ""If my Mac action gets stuck or the browser bridge disappears, keep trying only safe, idempotent recovery steps, then tell me on the pendant whether it is recovered, waiting for me, or permanently blocked.""
- **useful because:** Today a disconnected bridge or hung job leaves the owner guessing. A bounded recovery loop would make the system dependable while preserving the rule that uncertainty is surfaced instead of converted into duplicate clicks or submissions.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** cheap background model for classification and recovery planning; realtime only for owner notification
- **latency:** Detect health degradation in 5 s; attempt at most three recovery steps over 30 s; notify immediately on terminal state
- **cost:** Very low: health polling and deterministic retries dominate; model used only for ambiguous diagnosis
- **security:** Allowlist recovery to idempotent actions (reconnect bridge, refresh session, reopen app); never retry payment, send, delete, or submit operations. Preserve attempt logs and require physical approval to resume a risky transaction.
- **missing:** A lease-aware watchdog joining browser heartbeat, job status, and Mac health; Action idempotency keys and retry budgets in the job runner; A pendant status vocabulary/LED/audio mapping for recovered, waiting, and blocked

### ""Pause this task. When I pick up the pendant later, tell me exactly what was completed, what is still open, and let me resume from the next safe step without explaining everything again.""
- **useful because:** The owner can leave a task mid-flight without losing the mental state or accidentally repeating a completed action. A portable, encrypted handoff capsule would make the pendant, relay, Mac, and authenticated browser act like one continuing assistant rather than disconnected sessions.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background model to summarize and compact state; realtime only when the owner asks to resume
- **latency:** Checkpoint in under 1 s after pause; resume brief under 3 s; restore browser/Mac context within 10 s
- **cost:** Small summarization cost per checkpoint; storage and browser restoration dominate
- **security:** Capsule contains action state and locators, never passwords or page secrets. Encrypt at rest and bind restoration to the same browser session/device; expire capsules and require physical approval before any mutation.
- **missing:** A versioned encrypted task-capsule schema spanning relay, Mac, and browser; Checkpoint hooks that capture completed step IDs, verified postconditions, and safe resume point; A pendant command/gesture to pause and resume without opening a microphone continuously

### ""Let me ask you to work with a sensitive website without ever sending its secret fields to the model: identify the fields by meaning, fill only what I explicitly approve, and show me a proof of which fields changed.""
- **useful because:** It would make authenticated browser automation safe enough for everyday forms while preserving the browser as a privacy boundary. The model can reason over typed field labels and hashes, while the extension keeps values local and the owner gets a precise change receipt.
- **path:** pendant → relay → browser → mac-bridge → dashboard
- **model tier:** background model for field planning; realtime only for the approval conversation
- **latency:** Field inventory under 2 s; approval preview under 3 s; submit only after a deliberate gesture
- **cost:** Low model cost for structured field metadata; browser-side diffing and local redaction dominate
- **security:** Secret values never cross the extension boundary; no screenshots for secret regions; values are zeroized after use. Submission requires the existing physical approval latch and independent postcondition verification.
- **missing:** A browser extension protocol for semantic field metadata, local fill, and redacted before/after hashes; A typed secret/non-secret sensitivity classifier enforced in the extension, not merely requested from the model; A receipt UI that maps each changed field to an owner-approved intent without revealing its value

### ""If I lose the Mac or browser connection while something important is underway, keep my place on the pendant, tell me whether anything might have happened, and let me cancel or safely recover when the connection returns.""
- **useful because:** The owner gets honest continuity across outages: not a false success, not a duplicate retry, but a durable uncertainty record and a safe recovery choice. This is especially valuable because the pendant is worn while the Mac and browser can sleep, disconnect, or restart.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** cheap background model for classifying outage state; realtime for immediate spoken/LED status
- **latency:** Local pendant status within 500 ms of link loss; relay reconciliation within 5 s of reconnection
- **cost:** Very low ongoing model cost; durable event storage and reconciliation are the main implementation cost
- **security:** The pendant stores only opaque operation IDs, risk class, expiry, and status—not page contents or secrets. Reconnection must reconcile against fresh Mac/browser evidence before offering resume; unknown actions never auto-retry.
- **missing:** A signed, crash-safe operation status envelope deliverable to the pendant over USB/LTE; Reconciliation rules for interrupted mutations versus idempotent reads; A small pendant UI/state machine for pending, unknown, cancelled, and recovered states


## Changes it proposed to its own stack

### `relay` — Add a pendant-presence attestation lease for the Mac-attached device: the relay issues a short-lived challenge, the nRF9160/USB serial endpoint signs or MACs it, and high-risk Mac/browser jobs must reference a still-live lease in addition to the existing human approval. Disconnect, stale heartbeat, or replay immediately transitions the job to unknown and prevents retries. The same lease can later be backed by LTE when the pendant registers.
- **owner gets:** A request cannot silently continue after the owner removes the pendant, loses the USB link, or walks away. Today the hardware is physically attached and testable over USB even though LTE is not registered, so this creates a real proximity boundary now rather than waiting for cellular.
- effort: Medium-high: serial challenge protocol, firmware endpoint, relay lease store, executor enforcement, and fault-injection tests.  ·  risk: A serial reset or cable wobble could pause legitimate work; recovery is to re-attest and require the existing physical approval again, never auto-resume a risky step. Do not treat USB presence as identity by itself.
- cost: Negligible API cost; engineering only. Firmware adds a small challenge/lease state machine and a few KB of flash/RAM.  ·  latency: One challenge round trip at job start (<250 ms over USB); heartbeat every 5–15 s. No impact on ordinary low-risk actions.
- security: Improves proximity and replay resistance, but is deliberately defense-in-depth: it must not replace the opaque nonce, expiry, and deliberate gesture in physical_transaction_approval_latch.
- depends on: A read-only serial protocol to the connected nRF9160 pendant; Durable job-to-lease binding in the relay; Action-risk policy that can require presence for selected classes


## What it asked for

_Nothing._
## Its own summary

Discovered the live Mac agent advertises 219 routes, and Safari’s browser bridge is online with 9 tabs but no reported capabilities or nonce. I recorded that as an integration finding. I submitted three capabilities: (1) verified multi-step execution that stops on unknown rather than trusting receipts, (2) a read-only “prepare for my next meeting” workflow joining calendar, browser context, and private pendant audio, and (3) bounded recovery for stalled Mac/browser work. I also proposed a USB/LTE-independent pendant-presence attestation lease for high-risk actions, defense-in-depth to the existing physical approval latch.

**Biggest unknown:** The system still lacks a demonstrated durable coordinator joining action attempts to verify_operation_step, and the live browser bridge’s empty capability/nonce report makes it unclear whether authenticated browser execution is actually usable despite online status. I still need a real read-only serial challenge/status surface for the physically attached nRF9160 and an owner policy specifying which action classes require presence plus physical approval.

