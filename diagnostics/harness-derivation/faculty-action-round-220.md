# Harness derivation — faculty-action — round 220

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Run this task across my Mac and browser, but if any step cannot be independently verified, stop there, preserve what happened, and give me one physical retry or cancel choice on the pendant.”"
- **useful because:** Today an executor receipt can say an action ran while the world remains uncertain. A typed, step-scoped stop barrier prevents later steps from compounding an unknown state and turns a dropped link or stale browser into a recoverable handoff rather than a silent partial task.
- **path:** faculty-judgement → faculty-action → mac-planner → browser-extension → faculty-perception → relay-realtime → pendant
- **model tier:** background model compiles the dependency graph and recovery options; realtime model speaks only the concise uncertainty and waits for the owner's gesture
- **latency:** Each step executes normally; uncertainty decision under 1 s after verifier response; recovery packet durable within 500 ms
- **cost:** ~$0.02–$0.08 per multi-step task, dominated by graph planning and one verification call; no recurring device cost
- **security:** Never auto-retry mutations unless classified idempotent. Persist only opaque operation/step IDs, action class, hashes, and redacted recovery metadata. Physical retry must be bound to the exact failed step and expiry; cancellation must be the safe default. Do not claim completion from executor receipts alone.
- **missing:** operation dependency and compensation graph in the relay; a live resolver for verify_operation_step (currently only a schema grant); pendant protocol for step-specific retry/cancel envelopes and signed outcomes

### "“When I ask you to do something involving a private browser session, keep the entire sensitive interaction on my Mac, then tell me from the pendant only whether the requested outcome is verified, unknown, or safely cancelled.”"
- **useful because:** This creates a privacy boundary no single surface can provide: the browser session stays local, Mac executes, perception checks fresh state, relay carries only an opaque status, and the pendant gives a compact authenticated outcome. It is useful for banking, health portals, and private messages where even a screenshot or transcript is too much disclosure.
- **path:** relay-realtime → faculty-judgement → mac-planner → browser-extension → faculty-action → faculty-perception → pendant
- **model tier:** background model for policy and plan; realtime only for status phrasing and physical confirmation
- **latency:** Status beacon within 2 s after verification; private Mac/browser work may take as long as the site requires
- **cost:** ~$0.01–$0.06 per operation; cost dominated by planning and verification, with no audio/media upload
- **security:** Classify the task as private before execution; block screenshots, page text, clipboard export, and form-value telemetry. Browser-side policy must enforce origin, tab/session binding, and redacted receipts. Require physical approval for external side effects; on privacy-policy violation immediately revoke the operation and report only a content-free failure code.
- **missing:** end-to-end private-mode policy bit recognized by every executor; content-free privacy-wipe/revocation receipt joining browser, Mac, relay, and pendant; browser extension enforcement hooks for screenshot/clipboard/form telemetry suppression

### "“For a high-risk action, require both my pendant gesture and a live browser-session confirmation bound to the exact site and operation; if either disappears, do not submit.”"
- **useful because:** A pendant gesture proves possession of the wearable, but cannot prove the Mac is still on the intended origin or that a private browser session has not navigated. Binding two physically separate surfaces to one short-lived operation sharply reduces wrong-site, stale-tab, and unattended-session mistakes while preserving the existing approval latch.
- **path:** faculty-judgement → relay-realtime → browser-extension → mac-planner → faculty-action → faculty-perception → pendant
- **model tier:** background model chooses the risk threshold and compiles the challenge; realtime model communicates the short challenge and waits for the gesture
- **latency:** Challenge creation under 1 s; browser and pendant confirmations may arrive within 60 s; submit only after both are fresh
- **cost:** ~$0.01–$0.04 per high-risk operation, mostly one planning call; no continuous model cost
- **security:** Bind both approvals to an opaque operation nonce, browser origin/tab/session ID, expected action digest, and expiry. Browser confirmation must be a local UI action and must never expose credentials. Reject replay, navigation, stale sessions, mismatched digests, and one-sided approval. Default to cancel on timeout or link loss.
- **missing:** browser-side explicit confirmation primitive bound to origin and operation digest; relay join record for two independent approvals and freshness/expiry; risk-policy configuration identifying which action classes require dual confirmation

### "“Do this job under a hard action budget I specify—only this folder, at most 20 files, no deletion or external send—and stop before crossing any limit.”"
- **useful because:** The owner gets bounded autonomy instead of choosing between doing everything manually and granting an opaque open-ended task. The same limits follow the work from judgement to Mac, browser, relay, and pendant, so a planner cannot accidentally broaden scope after starting.
- **path:** faculty-judgement → relay-realtime → mac-planner → mac-terminal → browser-extension → faculty-action → pendant → faculty-perception
- **model tier:** Use a cheaper background model to compile the spoken limits into a signed policy; realtime is only needed to clarify an ambiguous limit or announce exhaustion.
- **latency:** Policy compilation under 1 second; enforcement adds under 50 ms per action; stop notification within 1 second of a limit being reached.
- **cost:** About $0.005–$0.03 per task, dominated by parsing and policy compilation; enforcement is local and nearly free.
- **security:** Limits must be explicit, monotonic, and enforced by executors rather than treated as planner advice. Count attempted and completed mutations separately; bind the policy to an operation nonce and expiry. On uncertainty, scope mismatch, or counter disagreement, stop safely and require a new policy. The pendant receives only the budget summary and remaining counters, never private file or page contents.
- **missing:** A canonical signed action-budget envelope understood by every executor; Mac and browser enforcement hooks that reject out-of-scope actions before execution; Ledger counters for attempted/completed/externally-visible mutations with independent verification; A compact pendant display/haptic vocabulary for budget remaining and exhaustion

### "“If I hold the pendant's emergency control, immediately revoke every pending or running computer action everywhere, close browser command authority, and tell me which ones were stopped versus already committed.”"
- **useful because:** A single physical kill switch is the one response that remains available when the owner cannot safely speak, find the Mac, or inspect a browser. It limits damage from a mistaken command, compromised session, or runaway loop across all cooperating surfaces.
- **path:** pendant → relay-realtime → faculty-action → mac-planner → mac-terminal → browser-extension → faculty-perception
- **model tier:** No expensive model is needed to revoke authority; use a signed relay broadcast and deterministic executors. A background model may later summarize the resulting ledger.
- **latency:** Pendant-to-relay revocation under 2 seconds when connected; each executor must enter deny-new-work mode immediately and acknowledge within 1 second. Already-started OS calls may report unknown rather than pretending cancellation.
- **cost:** Less than $0.01 per activation; mostly relay writes and executor acknowledgements.
- **security:** Use a hardware-originated signed revocation counter, not a spoken command. Revocation must be monotonic, replay-resistant, and valid even when no operation is currently pending. Executors must reject new work until a fresh session authorization is established. Never claim that an in-flight syscall was undone; return committed/stopped/unknown per operation. Prevent a compromised Mac session from suppressing or acknowledging its own revocation.
- **missing:** Pendant firmware emergency gesture and durable monotonic revocation counter; Relay fan-out and persistence for global revocation epochs; Mac and browser executors that enforce revocation before every mutation and acknowledge state; A recovery protocol for re-authorizing normal operation after the stop

### "“For this one task, give the agent access only to this folder and this browser tab for ten minutes, then revoke it automatically—even if the task fails or the Mac reconnects later.”"
- **useful because:** The owner can delegate useful work without granting the whole Mac or browser session broad standing authority. It makes the pendant, Mac, browser, and relay cooperate around a short-lived least-privilege capability rather than trusting a planner's promise to stay in scope.
- **path:** faculty-judgement → relay-realtime → pendant → mac-planner → mac-terminal → browser-extension → faculty-action → faculty-perception
- **model tier:** Background model turns the request into resource identifiers and a narrow capability; realtime only confirms the short summary and expiry.
- **latency:** Capability issuance under 2 seconds; revocation must propagate within 1 second of expiry or explicit cancellation; task execution latency is unchanged.
- **cost:** About $0.01–$0.04 per delegation, mostly policy compilation; token checks and revocation are local.
- **security:** Capabilities must name concrete file roots, browser session/tab IDs, allowed verbs, operation nonce, and expiry, and be signed by the relay. Executors must enforce deny-by-default, prevent path traversal and tab switching, and re-check expiry before every mutation. No capability may contain passwords or page contents. Reconnect must not resurrect an expired grant.
- **missing:** A cross-surface capability-token format and verifier; Mac sandbox/path enforcement for action types and browser tab/session binding; Relay revocation/expiry propagation that works across reconnects; Pendant UX for displaying and cancelling resource scope without a screen


## Changes it proposed to its own stack

### `firmware` — Integrate the owned DRV2605L and motor on i2c2 as the physical outcome channel: enable i2c2 in devicetree, add a tiny signed-outcome decoder, and render success/retry/unknown/cancel patterns locally with a watchdog-safe queue. Keep the existing single LED as a fallback and never let a haptic event approve or execute an action.
- **owner gets:** The owner can understand whether something actually happened without looking at a screen or hearing a crowded voice prompt—especially in public or noisy places. The jewellery-like pendant becomes a discreet, reliable status instrument rather than a blinking dev board.
- effort: 1–2 firmware iterations plus bench tests; validate I2C recovery, motor startup current, and patterns over link loss. Requires no new parts; the owned DRV2605L, motor, and I2C wiring must be physically connected.  ·  risk: A wedged I2C bus or motor surge could interfere with audio/radio timing. Isolate the driver on a work queue, reset the controller on timeout, cap duty cycle, and fall back to LED/audio. Do not flash hardware without explicit approval.
- cost: $0 new component cost; brief motor pulses likely tens of mA, with a small battery-life impact. Firmware flash size and RAM are modest but must be measured against the 211,608 B application budget.  ·  latency: Pattern begins under 100 ms after a verified signed outcome; no impact on codec path if offloaded from audio thread.
- security: Haptic input is output-only. Verify signature, nonce, and expiry before rendering; never treat button acknowledgement as approval. Avoid transmitting sensitive operation details—only compact outcome class and event ID.
- depends on: Physical DRV2605L-to-ESP/nRF I2C wiring continuity must be confirmed; tactile_action_outcome_beacon firmware behavior must be implemented and tested; signed outcome envelope and monotonic replay protection from physical_transaction_approval_latch


## What it asked for

_Nothing._
