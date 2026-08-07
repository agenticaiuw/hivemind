# Harness derivation — unified — round 46

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **cross-node action truth** — The live Mac agent is not ready for trustworthy GUI automation: Accessibility is untrusted, Screen Recording is false, synthesized events are rejected, and /observe explicitly warns ui_click/type/press can report success while doing nothing. Browser extension is offline with 3 pending commands. Relay and Mac bridge are reachable.
  - evidence: GET /ops/status and GET /observe at 2026-08-07T10:55Z

## Capabilities it proposed

### "When I ask you to do something on my Mac or in a logged-in browser, tell me truthfully whether it actually happened; if access or connection is unavailable, keep the safe parts queued and resume only when they can be verified—never claim success from a no-op."
- **useful because:** Today the Mac agent can report UI steps as successful even though Accessibility is untrusted and synthesized events are rejected; the browser is offline with pending commands. A worn-device conversation needs a single honest answer and safe recovery rather than silent loss or false completion.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use gpt-5.6-luna for planning/reconciliation and cheap relay/background workers for queue monitoring; reserve gpt-realtime-2.1 for the spoken status and owner confirmation.
- **latency:** Immediate spoken acknowledgement under 1 second; permission/connectivity probe 1–2 seconds; resume in background when a device heartbeat returns; final verified receipt within 5 seconds of execution.
- **cost:** Low per task: one planner call only when recovery or ambiguity occurs, roughly $0.01–$0.05; heartbeats and receipt validation are local/worker code and dominate no model cost.
- **security:** Never transmit private page contents beyond the existing authenticated browser session. Persist only action type, target hash, precondition, and receipt evidence. Irreversible actions remain paused for explicit approval. A reconnect must use idempotency keys and re-check target state to avoid duplicates.
- **missing:** A shared typed action-state contract across Mac/browser/relay (blocked, queued, executing, verified, failed) with evidence requirements; Mac-side preflight that hard-fails UI actions when Accessibility or Screen Recording is not trusted instead of emitting success; Browser heartbeat/reconnect and durable idempotent command replay for the currently stranded pending commands; Pendant/relay spoken status and dashboard timeline that distinguish attempted, delivered, and verified

### "Let me approve a bounded plan once from the pendant—such as 'handle routine scheduling under these limits'—and have you carry it out across my Mac and logged-in browser without asking me at every step, while automatically stopping if any step exceeds the limits or the approval expires."
- **useful because:** Today the owner must either micromanage multi-surface work or grant broad, opaque control. A wearable approval should be useful while walking away: it authorizes a narrowly described outcome, not an unbounded agent, and preserves a hard stop when reality differs from the plan.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use gpt-5.6-luna once to compile the spoken request into a typed constraint policy; use deterministic relay/Mac/browser enforcement for every step. Use gpt-realtime-2.1 only to ask a concise exception question or report completion.
- **latency:** Approval acknowledgement under 1 second; each step under 300 ms for policy checks; exception prompt within 2 seconds of detecting a violation. No model call is needed for ordinary allowed steps.
- **cost:** Roughly $0.01–$0.05 per authorization compilation, then near-zero per-step cost; signed policy checks and receipts are local/relay work.
- **security:** The approval must be an expiring, device-bound capability token containing allowed apps/sites, fields, value ranges, maximum count/time, and forbidden actions—not raw voice text. Irreversible sends, purchases, deletions, credential use, and policy expansion always require a fresh pendant confirmation. Store hashes and receipts, not private page contents; revoke on pendant privacy latch, disconnect timeout, or changed browser identity.
- **missing:** A shared constraint-policy schema and deterministic evaluator implemented identically in relay, Mac, and browser bridge; A pendant gesture/voice flow that displays or speaks the exact scope, expiry, and stop conditions before signing approval; Browser and Mac executors that attach the policy token to every step and refuse unscoped delegated actions; A dashboard showing the live authorization scope, remaining budget, exceptions, and immediate revoke control


## Changes it proposed to its own stack

### `integration` — Introduce a shared Action Truth Ledger used by relay, Mac planner/vision, and browser bridge. Every action gets an idempotency key, precondition snapshot, executor heartbeat, and an evidence policy. The Mac executor must run an inputReachability/permission preflight and emit BLOCKED_PERMISSIONS before any UI step when Accessibility or Screen Recording is false; browser commands remain QUEUED_OFFLINE until extension heartbeat returns. Only postcondition evidence (DOM/state reread, app/model query, or screenshot with valid Screen Recording) can transition to VERIFIED. Relay maps state transitions to concise pendant speech and dashboard receipts; reconnect workers replay only non-committed reversible steps.
- **owner gets:** The owner stops hearing 'done' when nothing reached the screen, and safe work is not lost when the browser or Mac temporarily disconnects. They get a clear reason, a resumable task, and proof when it really completed.
- effort: Medium: shared schema plus D1/local persistence, Mac executor guards, browser reconnect loop, and receipt UI; 1–2 weeks including failure-injection tests.  ·  risk: Existing clients may assume success after dispatch; migrate them to explicit states and preserve old receipts as attempted. Replays could duplicate side effects unless idempotency and postcondition checks are mandatory; irreversible actions are never auto-replayed.
- cost: Negligible storage/worker cost; one extra local state read and optional verification call per action. Model spend decreases because recovery is state-machine driven rather than replanned conversationally.  ·  latency: Adds ~100–300 ms preflight and verification for local actions; offline tasks intentionally wait for heartbeat rather than falsely completing.
- security: Improves privacy and safety by storing hashes/metadata rather than page contents, refusing unverifiable UI control, and requiring approval for irreversible transitions.
- depends on: Mac Accessibility/Screen Recording permission fix or explicit blocked state; Browser extension heartbeat and command replay endpoint; A durable shared receipt schema consumed by relay and dashboard

### `hardware` — Add a low-power fuel-gauge IC (I²C, e.g. MAX17048-class) and a second RGB status indicator or haptic driver to the pendant, with firmware telemetry fields for battery percentage, estimated time-to-empty, LTE transmit state, and a local queued-action count. Relay and Mac ledger use this to defer large audio/verification transfers before brownout, flush the owner’s task receipt, and speak/flash 'saved locally / waiting for link' rather than dropping a conversation.
- **owner gets:** The pendant currently has no readable battery state, while LTE bursts are power-hungry and the owner can lose the very task status they depend on when it dies. They would get an early warning and confidence that a pending request and its completion proof survived.
- effort: Medium hardware revision and firmware driver; add fuel-gauge calibration, telemetry schema, and relay/Mac policies. Prototype on the current board with an external gauge before enclosure redesign.  ·  risk: Gauge estimates drift across battery chemistry and temperature; expose confidence and recalibrate. Added LED/haptic output could distract or leak state in public, so default to subtle patterns and allow mute. Brownout can still occur; journal state before transmit.
- cost: Approximately $2–$5 BOM increase plus <100 µA gauge draw; negligible model cost. Firmware telemetry adds a few hundred bytes of RAM and small periodic LTE payloads.  ·  latency: No conversational latency when healthy; low-battery mode may delay nonurgent audio uploads by seconds to preserve an explicit receipt.
- security: Battery and queue metadata are low sensitivity; do not include task text in telemetry. Local indicator must not reveal private action content.
- depends on: A durable relay action/receipt journal; Pendant firmware telemetry fields and brownout-safe local storage; Relay policy that can distinguish urgent owner speech from deferred background transfers


## What it asked for

_Nothing._
## Its own summary

Discovered a still-live safety gap and proposed a new cross-node capability plus implementation: truthful action states with permission/connectivity preflight, idempotent browser replay, postcondition evidence, and pendant/dashboard receipts. Live evidence: Mac Accessibility=false and Screen Recording=false; synthesized UI events are rejected despite possible success receipts; browser extension offline with 3 pending commands. Also proposed a hardware fuel gauge/status path so battery brownout cannot erase task continuity.

**Biggest unknown:** The orchestrator still needs to establish the owner-approved recovery policy for queued actions and obtain actual Accessibility/Screen Recording permission for the running AI Pendant Agent binary. Without those, GUI work must remain explicitly blocked and browser work queued—not reported complete.

