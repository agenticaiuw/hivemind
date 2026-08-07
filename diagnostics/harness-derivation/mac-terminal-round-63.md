# Harness derivation — mac-terminal — round 63

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac execution observability and readiness** — Live Mac agent v0.5.0 has FULL_CONTROL_MODE and planner enabled, but computer-use loop disabled, vision upload consent false, Accessibility untrusted, Screen Recording missing, browser extension offline with 5 pending commands, while relay and Mac bridge are reachable. The newly granted mac_read_diagnostics interface still has no implementation.
  - evidence: GET /ops/snapshot and GET /browser/status returned these live fields; mac_read_diagnostics(checks=[...]) returned error: tool granted schema but has no implementation yet.

## Capabilities it proposed

### "“Do it, and if one of your connections or permissions is down, recover or use another part of the hive instead of leaving me with a dead end.”"
- **useful because:** Today the Mac agent reports browser offline, Accessibility untrusted, and Screen Recording missing while still advertising broad capabilities; a request can therefore fail late or silently queue behind five stale browser commands. This capability would preflight the exact path, select a viable pendant/relay/Mac/browser route, retry transient failures as a durable job, and give one concise explanation plus a recovery option. It is materially more useful than merely exposing status because the owner does not need to diagnose which node is broken.
- **path:** pendant → relay → mac-planner → browser-extension → mac-vision → dashboard
- **model tier:** Deterministic health/precondition classifier and durable job runner first; background model for summarizing the failure and alternatives; realtime only to speak the short result over the pendant.
- **latency:** Under 300 ms for local health checks and route selection; up to 2 s for one retry decision; long-running work becomes a durable job with pendant notification, so the owner is not held on the voice turn.
- **cost:** Usually near-zero model cost when deterministic checks and typed actions suffice; roughly 1–3k background tokens only when explaining alternatives. Dominant cost is existing Mac/browser execution, not realtime inference.
- **security:** Health data can reveal logged-in tabs, app names, permissions, and network state; keep raw diagnostics local and send the relay only typed capability state and redacted error summaries. Never silently substitute a public page for an authenticated one, and preserve the existing owner policy of no confirmation gates for ordinary actions; explicitly surface when a requested authenticated action cannot be completed.
- **missing:** A single typed precondition schema shared by Mac, browser, relay, and pendant (online, permission, session, freshness, retryability).; A route planner that distinguishes transient transport failure from missing permission and chooses a safe fallback without claiming completion.; A durable retry/dead-letter worker tied to job receipts, with stale browser-command reconciliation and an owner-visible reason code.; Implementation of the granted read-only diagnostics tool; its current interface returns “no implementation yet,” so the health preflight cannot cheaply verify host facts.

### "“When you say you did it, prove it—and if you can’t verify the result, tell me that instead of guessing.”"
- **useful because:** Today Mac, browser, relay, and pendant actions can each produce local receipts, but the owner cannot reliably distinguish “command accepted” from “the world now matches what I asked.” This capability would define a completion test for each request, collect independent postconditions where possible, and speak a short evidence-backed result. For example, after changing a setting it would re-read the setting; after editing a browser form it would verify the DOM value and session state; after a cross-surface handoff it would verify the downstream receipt. It is a new trust guarantee, not merely another log or undo button.
- **path:** pendant → relay → mac-planner → browser-extension → mac-vision → dashboard
- **model tier:** Deterministic postcondition checks and receipt correlation do the core work; a cheaper background model normalizes evidence into a concise explanation; realtime only handles the immediate spoken response.
- **latency:** Add 100–500 ms for local verification on short actions. For browser or multi-step work, verification runs asynchronously and the pendant says it is checking, then delivers a durable result.
- **cost:** Near-zero model cost for typed postconditions and existing receipts; typically under 1k background tokens when evidence must be summarized. The dominant cost is any extra Mac/browser read, not inference.
- **security:** Evidence may contain private URLs, window titles, form values, or file paths. Keep raw evidence on the Mac/browser bridge, transmit only redacted claims and hashes to relay, and expose the source surface and timestamp in the dashboard. Never treat an executor acknowledgement as proof of a real-world mutation.
- **missing:** A common completion-contract format with preconditions, postconditions, evidence source, freshness, and confidence.; Typed verification probes for Mac actions and browser actions, including safe readback after mutations.; A receipt state that distinguishes accepted, executed, verified, contradicted, and unverifiable, with contradiction recovery rather than silent success.; Pendant/dashboard rendering for a concise claim plus “why I believe this” evidence trail.

### "“If my Mac is asleep or disconnected, remember exactly what I asked from the pendant and finish it when the Mac comes back—without making me repeat myself.”"
- **useful because:** The pendant is the only surface continuously with the owner, while the Mac and browser are intermittent. Today a spoken request can end at a transient bridge or browser failure, and the owner has no durable, user-visible intent envelope preserving the exact request, constraints, and intended verification. This capability would capture the request locally/at the relay, acknowledge it immediately, bind it to the returning Mac/browser session, and resume only when the required surface is available. It preserves uncertainty and asks a focused follow-up if the request becomes stale instead of improvising.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Realtime extracts a compact intent envelope during the voice turn; deterministic relay storage, wake/reconnect matching, and execution handle the rest; a cheaper background model resolves stale or ambiguous intents. No realtime model is needed while waiting.
- **latency:** Immediate pendant acknowledgement under 500 ms when offline; reconnect matching under 2 s; execution time is asynchronous and reported through the pendant/dashboard.
- **cost:** Small durable relay storage and reconnect polling cost; usually no additional model call. Background resolution of stale intents is roughly 1–3k tokens only when needed.
- **security:** Queued intents may contain private account or file details. Encrypt the envelope at rest, bind it to the paired pendant and Mac identity, expire it by owner-selected TTL, and avoid replaying authenticated browser mutations after session or page context changes. The owner must be told when execution is deferred and when context changed.
- **missing:** A pendant/relay intent-envelope protocol with encrypted storage, TTL, constraints, and required-surface declarations.; A reconnect matcher that binds an intent to the correct Mac/browser session and rejects stale or changed authenticated contexts.; An offline-safe pendant acknowledgement and later completion notification path.; Dashboard controls to inspect, edit, cancel, or expire queued intents before reconnect execution.


## Changes it proposed to its own stack

### `integration` — Add a typed capability-preflight and recovery coordinator between planner and executors. Before dispatch, it queries /ops/status, /browser/status, /routing, and the relevant session state, then emits a compact decision record: route, required permissions/session, freshness, retry class, fallback routes, and owner-facing reason code. On browser reconnect it reconciles pendingCommands by request/idempotency key (five are currently pending while the extension is offline), marks stale commands dead-lettered rather than replaying blindly, and links every retry/fallback to the existing job receipt and journal. It must observe and explain, not introduce blocking approval gates.
- **owner gets:** The pendant stops promising actions that cannot run, recovers when the browser or relay briefly disappears, and tells the owner exactly whether work completed, is waiting, or needs a permission fix. It also prevents duplicate browser clicks after reconnect.
- effort: Medium: shared schema, coordinator in planner/dispatcher, stale-command reconciler, receipt/journal integration, and fault-injection tests for offline browser, expired session, relay timeout, and missing Mac permissions.  ·  risk: A bad retry classification could repeat a non-idempotent browser action. Default retries to reads and explicitly idempotent steps; require an executor-provided idempotency key for mutations, and preserve before/after receipts. If coordinator fails, fall back to today's direct dispatch and report degraded observability.
- cost: No meaningful API cost for deterministic checks; small local CPU/storage cost for decision records and dead-letter metadata. Avoids expensive planner retries and duplicate work.  ·  latency: Adds roughly 50–200 ms for local preflight; skip checks whose health lease is fresh. Long jobs remain asynchronous.
- security: Diagnostics stay local; relay receives only redacted typed health and reason codes. Session URLs, tab text, and permission details remain in the Mac agent. No new authority or gates are introduced.
- depends on: A concrete implementation of the already-granted mac_read_diagnostics/mac_readonly_diagnostics_impl tool, or equivalent local health provider.; A shared idempotency-key field across browser command queue and Mac job receipts.; The existing browser command queue and receipt/journal paths must expose stale-command age and terminal reason codes.


## What it asked for

_Nothing._
