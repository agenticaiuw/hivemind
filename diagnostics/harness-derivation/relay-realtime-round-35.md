# Harness derivation — relay-realtime — round 35

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Keep working on that after I walk away, and tell me what happened when it finishes."
- **useful because:** This matches how a wearable is used: the owner may start a task by voice, then leave. They still want a clear, trustworthy result later without babysitting it.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Realtime only for initial confirmation; cheaper planner/executor tiers for the actual work and result collation.
- **latency:** Under 1 second to acknowledge on the pendant; minutes to hours for the job depending on complexity, with periodic status available and a final spoken summary.
- **cost:** Low per acknowledgment; main cost is downstream planning/execution and any browser automation. Avoids expensive relay time by offloading work.
- **security:** Must preserve a reliable audit trail and receipts. Avoid claiming completion unless a job status reports done. Ensure private data from logged-in sessions stays confined to the Mac/browser harnesses.
- **missing:** Durable job runner with persistence and retries; A notification path to the pendant for completion summaries; Typed receipts for browser and Mac actions with stable identifiers; Optional: server-side browser execution for public pages when Mac is offline

### "“Find me the best option on the site I’m logged into, make sure it fits my calendar and constraints, and leave the result ready for me—without reading my whole calendar or exposing unrelated private data.”"
- **useful because:** Today the pendant can hand work to the Mac or browser, but neither downstream surface can jointly apply authenticated web state, local calendar constraints, and the owner’s remembered preferences while minimizing what each agent sees. This gives the owner a genuinely remote, privacy-minimized way to perform useful multi-surface decisions while they are away from the Mac.
- **path:** pendant captures the request and speaks progress/result → relay extracts only the needed constraints and coordinates the job → mac-planner reads the narrowly scoped calendar/preferences and evaluates conflicts → browser harness uses the owner’s authenticated session to search and prepare the selected result → relay returns a compact explanation and a deep link or draft for the owner
- **model tier:** Use relay-realtime only for intent extraction, progress, and final spoken summary; use mac-planner for constraint evaluation and a cheaper background planner for ranking many browser results. Browser extraction should be deterministic where possible, escalating to a model only for page interpretation.
- **latency:** Acknowledge in under 1 second; begin work immediately; return progress within 5 seconds and final result when the browser and Mac finish. The owner should be able to interrupt or ask for status without losing the job.
- **cost:** Roughly $0.01–$0.08 per request depending on number of browser pages and planner calls; browser page extraction and ranking dominate, while relay speech should be a small fixed cost.
- **security:** Do not send the full calendar, browser cookies, or unrelated preferences across agents. Use scoped, expiring constraint tokens and return typed evidence (conflict interval, price, availability) rather than raw private data. Preparing a draft is reversible; submitting purchases, bookings, or messages must remain an explicit separate action. Log provenance and allow the owner to erase the job and its extracted data.
- **missing:** A cross-surface constraint broker that issues least-data, expiring projections from Mac state to a browser job; A durable correlation ID and typed result schema joining calendar evidence, browser evidence, and prepared output; A background job runner with retries and progress events so the pendant can remain responsive while the Mac/browser work continues; A browser-to-relay evidence channel for authenticated pages that does not copy whole page contents by default; An owner-visible receipt that explains exactly which constraints were used and what was merely inferred


## Changes it proposed to its own stack

### `relay` — Introduce a single canonical tool registry and name resolution layer for the relay. Tools listed as granted/available must be describable by the same name via describe(name), and should include a version string, deprecation flag, and a minimal schema fingerprint so the relay can safely route without guessing. Provide a compatibility map for renamed tools for one release cycle.
- **owner gets:** When the owner asks for something, the relay can route it reliably instead of failing on a naming mismatch. That means fewer "sorry, that’s not available" moments and more consistent handoffs between pendant, relay, Mac, and browser.
- effort: Medium. Needs a small registry service or static manifest, plus integration in the relay and orchestrator tool-grant path.  ·  risk: If the registry is wrong, routing breaks everywhere. Mitigate with versioning, a safe fallback path, and a health check that validates tool descriptors at startup.
- cost: Low ongoing API cost; small additional config payload. Biggest cost is engineering time to wire the registry and tests.  ·  latency: Slightly faster in practice because the relay stops doing extra discovery calls that fail.
- security: Improves security by reducing accidental capability exposure and preventing the relay from calling an unintended tool due to ambiguous naming.
- depends on: A source of truth for tool manifests (build artifact or orchestrator endpoint).

### `interaction` — Add a resumable conversation checkpoint protocol spanning pendant, relay, Mac planner, and browser harness. At every handoff, persist a compact encrypted checkpoint containing the owner’s normalized goal, unresolved questions, downstream job correlation, last confirmed facts, pending browser/Mac outputs, and the last audio sentence delivered. On reconnect or a new utterance such as “continue” or “what happened?”, the relay should restore that checkpoint, query live job state, and speak only the delta. Checkpoints must expire, be versioned, and be invalidated when the owner says to discard the task.
- **owner gets:** A dropped LTE link, a sleeping Mac, or a long browser task would no longer force the owner to repeat a request or guess whether anything happened. They could start work while walking, reconnect later, and receive a truthful continuation rather than a fresh conversation that has forgotten the handoff.
- effort: Medium-high: define a small encrypted checkpoint schema and idempotent resume API; add persistence and expiry at the relay; have Mac and browser workers publish checkpoint updates and terminal states; add pendant reconnect semantics and concise delta narration.  ·  risk: Stale or duplicated checkpoints could cause misleading status or repeated actions. Recover by making every downstream operation idempotent, displaying the checkpoint timestamp/source in the spoken summary, and treating unknown state as unknown rather than replaying a mutation. Expiry and explicit discard limit retained sensitive context.
- cost: Small storage and Durable Object/KV cost; roughly a few hundred bytes to a few KB per active task. One inexpensive status lookup on resume; no extra realtime model call unless the owner asks for a natural-language explanation.  ·  latency: Reconnect acknowledgement can be sub-second from the relay; live downstream status may add 0.5–3 seconds. Normal turns gain only a small write.
- security: Checkpoints contain potentially sensitive intent and derived facts, so encrypt at rest, bind them to the paired pendant, apply short retention, and never store cookies or full page/calendar contents. The owner must have a spoken erase/discard command.
- depends on: A durable relay store with atomic compare-and-swap/versioning; Stable correlation IDs and typed terminal/progress events from Mac and browser workers; Pendant reconnect/session identity and a resume utterance recognized by the realtime front door


## What it asked for

_Nothing._
## Its own summary

Recorded two new items: a privacy-minimized cross-surface constraint broker for jointly using authenticated browser state plus scoped Mac calendar/preferences, and resumable encrypted conversation checkpoints so dropped links or long jobs can continue without repeating requests. Both explicitly identify the durable correlation, progress, storage, and evidence infrastructure still required.

**Biggest unknown:** Whether the existing backend already has an undocumented durable event stream or encrypted per-pendant store; implementing either proposal should first confirm that, but no further discovery is available this round.

