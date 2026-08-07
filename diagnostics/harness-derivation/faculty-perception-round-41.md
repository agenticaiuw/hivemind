# Harness derivation — faculty-perception — round 41

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **macOS computer-use perception readiness** — As of 2026-08-07T11:05Z, AI Pendant Agent is running (PID 25245) but Accessibility is not trusted for the running com.aipendant.agent binary and synthesized input probe fails; Screen Recording is also not granted. /ops/status reports computerUse.loopEnabled=false and visionUploadConsented=false. Therefore UI actions cannot be trusted and vision upload/loop cannot safely run.
  - evidence: GET /observe and GET /ops/status at 2026-08-07T11:05Z
- **Cross-surface availability** — At 2026-08-07T11:05Z the relay and Mac bridge are reachable, but the browser extension home-chrome is offline (last seen 09:21:08Z) with 3 pending commands; Mac has 3 durable browser sessions but no live extension tab. This makes authenticated browser state non-current and commands not safely executable.
  - evidence: GET /ops/status and GET /browser/status

## Capabilities it proposed

### "Before you do anything, tell me whether you can actually see the relevant screen/page, hear me, and control the target—and if any part is stale, offline, or only inferred, say exactly what is missing and ask me to reconnect or confirm."
- **useful because:** Today the system can report optimistic action receipts even when Mac input is unreachable, while the browser is offline and visual access is unavailable. A cross-surface reality check prevents acting on a stale tab, an imagined UI state, or an unavailable pendant, and gives the owner an actionable diagnosis instead of a silent failure.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Cheap background/state classifier for heartbeat reconciliation; realtime only to speak the concise result during a live request. No expensive vision model unless the target is actually reachable and the owner has consented.
- **latency:** Under 500 ms from cached heartbeats; up to 2 s if a fresh Mac/browser probe is needed. Never block on an unavailable surface indefinitely.
- **cost:** Usually near-zero model cost (typed status comparison); roughly $0.001–$0.01 only when a fresh text reconciliation is needed. Vision upload is opt-in and dominates cost/privacy.
- **security:** Do not capture screen or authenticated page content merely to establish reachability. Return capability/status metadata with timestamps, not secrets. Require explicit consent before any screenshot upload and confirmation before treating a degraded state as sufficient for an irreversible action.
- **missing:** A signed, unified reachability snapshot schema spanning pendant audio/link, relay freshness, Mac Accessibility/Screen Recording/input reachability, and browser extension/tab/session state; Freshness/expiry and contradiction rules (for example, action receipt success must be rejected when inputReachability is failed); A precondition gate in the planner/executor that consumes this snapshot and produces a human-readable diagnosis; Correct Accessibility and Screen Recording authorization for the exact running AI Pendant Agent binary, plus explicit vision-upload consent

### "When something goes wrong, show me what each part of you actually knew at that moment—what the pendant heard, what the Mac and browser could reach, which facts were fresh or stale, and why you believed the action was safe—without pretending to reconstruct information that was never observed."
- **useful because:** The owner cannot currently distinguish a bad decision from a bad observation or a disconnected surface. A cross-node epistemic replay would make failures diagnosable and prevent repeated mistakes: it would show the exact observation boundary, freshness, contradictions, and missing permissions at the time, rather than an after-the-fact narrative generated from current state.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic event/evidence indexing and rule-based diffing first; use a cheap text model only to explain the already-cited timeline. Realtime is unnecessary except for a short spoken answer while the owner is asking.
- **latency:** Sub-second to load a bounded event window; under 3 seconds to render a cited explanation. Retention and indexing happen asynchronously.
- **cost:** Negligible model cost for ordinary replay; roughly $0.001–$0.02 for optional natural-language synthesis. Main cost is bounded encrypted storage and event indexing, not inference.
- **security:** Store claims and metadata by default, not raw microphone audio, screenshots, or authenticated page bodies. Encrypt per owner, redact secrets, enforce short retention, and show when a source was unavailable. Any raw evidence export requires explicit confirmation.
- **missing:** An append-only, clock-disciplined observation ledger shared by pendant, relay, Mac agent, and browser bridge; Per-observation provenance with source, capture time, monotonic age, confidence, sensitivity, and deletion deadline; A correlation ID linking observations, plans, preconditions, actions, and receipts without claiming that a receipt proves the underlying observation; Dashboard and spoken query support for 'what did you know then?' with Unknown/Contradicted states; A privacy-preserving retention and redaction policy for optional raw evidence


## Changes it proposed to its own stack

### `relay` — Implement a signed Reachability/Reality Snapshot protocol. Mac agent publishes timestamped observations (inputReachability, Accessibility, Screen Recording, foreground app, browser online/pending queue); browser bridge publishes extension/tab/session freshness; relay adds pendant link/audio pipeline freshness. The relay verifies signatures and emits per-target predicates: visible, controllable, audible, authenticated, fresh, and contradictory. Planner and executor must attach the snapshot ID to every plan/receipt and refuse to claim success when a required predicate is false or expired.
- **owner gets:** The owner gets an honest answer about what the system knows and can touch right now. A failed GUI input will be reported as unavailable rather than appearing completed, and stale/offline browser sessions will be caught before a transaction is prepared.
- effort: Medium-high: shared schema, signing/key rotation, heartbeat adapters on Mac/browser/relay/pendant, planner preconditions, dashboard display, and adversarial tests for stale/contradictory states.  ·  risk: Clock skew, dropped heartbeats, or a buggy adapter could cause unnecessary refusals; recover with monotonic local age, explicit Unknown rather than false, retries, and a manual 'recheck' path. Never downgrade Unknown to reachable.
- cost: Small storage/compute overhead; a few bytes to hundreds of bytes per heartbeat and negligible D1 writes if coalesced. No model cost for normal operation.  ·  latency: Adds <100 ms for cached predicates; fresh probes may add up to 2 s but are bounded and cancellable.
- security: Positive if signatures prevent one surface from spoofing another; avoid including screen/page contents in snapshots. Keys must be scoped per device and rotated. Vision remains opt-in.
- depends on: Exact-binary Accessibility and Screen Recording authorization must be fixed for Mac perception; A durable pendant diagnostics/continuity read path; Browser heartbeat/command queue must expose freshness and session affinity; Executor receipts need a required snapshot ID and precondition result


## What it asked for

_Nothing._
## Its own summary

Fresh probes established a critical perception/control contradiction: the Mac agent and relay report online, but the exact running AI Pendant Agent binary is not Accessibility-trusted, Screen Recording is missing, input reachability fails, computer-use is disabled, and vision upload consent is false. The browser extension is offline with 3 queued commands, so its authenticated state is not current. I recorded both findings, notified mac-vision, faculty-judgement, and unified, and proposed a signed cross-surface Reality/Reachability Snapshot plus a user-facing preflight capability that refuses to claim success when visibility/control/freshness predicates are false.

**Biggest unknown:** Whether macOS privacy authorization can actually be applied to the exact running app/binary (and whether the owner will grant explicit vision-upload consent); pendant diagnostics and continuity freshness remain unavailable, so wearable-side reachability cannot yet be independently verified.

