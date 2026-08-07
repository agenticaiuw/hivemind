# Harness derivation — relay-realtime — round 111

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "What happened to the thing I asked you to do earlier?"
- **useful because:** When the owner is away from their Mac, they still need a clear answer about whether a task is queued, failed, or completed, without guessing or re-asking later.
- **path:** relay → mac-bridge → mac-harness
- **model tier:** Realtime at relay for the voice response; cheaper Mac-side summarization only if receipts must be read.
- **latency:** Under a second when the relay has a record; longer only when it must fetch receipts from the Mac.
- **cost:** Very low for relay-only status reads; higher only if it needs to fetch receipts over the bridge.
- **security:** Do not fabricate status. The spoken response must come from recorded job state. Avoid exposing sensitive details from receipts; speak the prepared summary.
- **missing:** relay_job_status implementation (currently schema only); durable job runner or equivalent reliable job state persistence

### "“Is the thing I was working on safe to leave, and what is the one unresolved problem?” (or any spoken question that requires checking both my Mac and an authenticated browser session)"
- **useful because:** Today the pendant can hand off a goal or inspect one surface, but it cannot give a trustworthy cross-surface answer whose pieces were captured at the same moment. The owner needs one concise spoken answer that distinguishes observed facts from inference, identifies stale/unavailable surfaces, and points to the exact tab/app/document evidence—especially when they are away from the Mac.
- **path:** pendant → relay → mac-planner → mac-terminal → browser-extension → dashboard
- **model tier:** Use relay-realtime only for the short spoken framing and final answer; use mac-planner for orchestration, mac-terminal for local project state, and the browser extension for authenticated DOM state. Use a cheaper background model to reconcile/format the collected evidence; do not spend realtime tokens on the investigation.
- **latency:** Acknowledge in under 300 ms, collect parallel snapshots within 8 s, and speak a 10–20 second answer. If a surface is offline or older than the freshness threshold, say so instead of waiting indefinitely.
- **cost:** Roughly one realtime turn plus 2–4 cheap worker calls; dominated by Mac/browser round trips and screenshot/DOM payloads, not inference. Cache hashes and cited excerpts rather than resending whole pages on follow-up turns.
- **security:** Authenticated page text and local project metadata leave their respective devices only through the existing authenticated relay path. Never expose secrets or full page dumps in the spoken answer; redact them in evidence receipts. Read-only by default, with explicit owner confirmation required before turning a finding into a mutation.
- **missing:** A single cross-surface snapshot job with a freshness barrier and correlation id; Typed evidence records (surface, capture time, source locator, excerpt/hash, confidence, redactions) that mac-planner, terminal, and browser-extension can all emit; A reconciliation worker that reports contradictions and unavailable surfaces rather than silently merging them; A pendant-sized spoken response schema that can cite “Safari tab 3” or “VS Code file” without dumping sensitive contents

### "“Lock everything down now.” (a long-press or spoken emergency command when the pendant is lost, lent out, or a remote session looks wrong)"
- **useful because:** There is no single owner-controlled emergency action that reaches the relay, Mac agent, and authenticated browser at once. Today the owner may be away from the Mac and unable to revoke a browser session or stop queued work quickly. One authenticated pendant gesture should immediately contain the whole hive without requiring speech, a phone, or Mac access.
- **path:** pendant → relay → browser-extension → mac-planner → dashboard
- **model tier:** No realtime generation is needed for the button path; use deterministic firmware and relay logic. Use a cheap background model only to produce an optional human-readable incident summary after containment.
- **latency:** Local haptic/LED acknowledgment under 300 ms; relay revocation fan-out target under 2 s, with a durable retry and an explicit partial-failure state.
- **cost:** Negligible inference cost; one durable state write and a small fan-out to each connected surface. Main cost is implementation and testing of revocation semantics.
- **security:** This is intentionally destructive to active access and may interrupt work. Require a deliberate long press plus a distinct tactile confirmation pattern (or a spoken command with device authentication), make it idempotent, and never let a browser or Mac request cancel it. Revoke relay leases, invalidate pending action capabilities, pause browser commands, and close/lock authenticated browser sessions where supported. Keep only minimal incident metadata.
- **missing:** A relay-wide emergency containment state with monotonic generation/epoch numbers; Short-lived, revocable capability leases for Mac and browser actions instead of bearer access that remains valid; Browser-extension and Mac-agent handlers that observe the epoch and stop/cancel queued work; A local firmware long-press detector and unmistakable acknowledgment pattern; A recovery flow on the pendant/dashboard to re-pair and selectively resume safe read-only work


## Changes it proposed to its own stack

### `relay` — Publish a Relay capabilities and routes inventory endpoint (e.g., GET /relay/capabilities and GET /relay/routes) generated from the live worker router, plus a small public schema for granted tools and context. Include versioning and a minimal changelog so agents can detect when a capability disappeared or semantics changed.
- **owner gets:** It prevents silent failures and repeated dead-end proposals. The owner gets a smoother experience: the pendant can explain what it can do right now, and avoid promising actions that rely on missing implementations.
- effort: Medium. Requires wiring a router introspection step into the Cloudflare Worker build and exposing a read-only route with auth.  ·  risk: Low. The main risk is exposing too much operational detail; mitigate by auth and by returning only high-level names, versions, and status.
- cost: Low API cost; small JSON payload. No extra per-invocation downstream usage.  ·  latency: Low. One quick GET when an agent needs to re-sync.
- security: Moderate if unauthenticated; keep bearer-protected and omit secrets, keys, and internal config values.

### `integration` — Add a CrossSurface Snapshot Envelope and freshness barrier between relay, Mac planner/terminal, and browser extension. A relay request creates one correlation id and a deadline; each producer returns a typed, redacted EvidenceItem {surface, locator, capturedAt, sourceVersion/hash, excerpt, availability}. The coordinator only issues a spoken synthesis after all required items meet the deadline, and marks missing/stale/contradictory items explicitly. Persist the envelope with the job receipt so a later voice turn can answer “which tab/file did you use?” without re-running the entire task.
- **owner gets:** When away from the Mac, the owner gets a dependable answer about the actual state of work instead of a confident blend of a fresh browser page and an old Mac status. They can act on one short answer and later audit exactly where it came from.
- effort: Medium-high: shared schema, parallel fan-out in the planner, browser-extension and terminal adapters, relay synthesis adapter, redaction tests, and receipt/dashboard rendering.  ·  risk: A producer may hang, report incompatible versions, or leak sensitive excerpts. Enforce a hard deadline, cap excerpt size, redact credentials, and return an explicit partial/contradictory result. Existing action receipts provide recovery; this path is read-only and can be disabled without affecting execution.
- cost: Small storage increase per snapshot (metadata plus bounded excerpts); one additional cheap reconciliation call when multiple sources exist. No realtime call beyond the final spoken response.  ·  latency: Parallel capture adds a bounded 3–8 second wait for cross-surface questions; acknowledgment remains immediate and timeout produces a partial answer.
- security: Improves security observability by retaining source locators and redaction status, but introduces a sensitive evidence cache. Encrypt it, apply short TTLs, and never place raw authenticated page text in logs or voice transcripts.
- depends on: A correlation-id propagated through /plan, /execute, browser inspection/command routes, and Mac action receipts; A shared redaction and bounded-excerpt library; A read-only snapshot coordinator; do not require the currently disabled computer-use loop

### `hardware` — Add a low-power haptic actuator (coin ERM or LRA) and a dedicated local alert driver to the pendant, with firmware patterns for queued, completed, failed, and needs-attention states. The relay emits signed alert intents keyed to the existing job/correlation id; firmware can acknowledge receipt and replay the last unread pattern with the single button. Keep the LED as a secondary channel and rate-limit alerts.
- **owner gets:** The owner can walk away from the Mac, mute audio, or be in a noisy place and still know that a delegated browser/Mac task finished or needs attention. A short tactile pattern communicates status without exposing private content aloud or requiring them to look at a phone.
- effort: Medium hardware revision plus firmware driver, battery characterization, relay alert delivery, and an end-to-end job-state mapping. Prototype with an LRA, transistor/driver, and a small PCB revision before committing to production.  ·  risk: Extra power draw, false or excessive alerts, and tactile annoyance. Make patterns brief, coalesce repeated updates, provide a long-press mute/quiet mode, and retain LED/audio fallback. A lost link must not cause a stuck motor; use a watchdog and hard duty-cycle limit.
- cost: Approximately $1–4 in components and modest PCB/assembly impact; roughly 10–30 mA only during a short vibration, near-zero standby with a proper driver. Firmware and relay calls add negligible API cost.  ·  latency: Local alert under 500 ms after a received event; LTE delivery remains link-dependent. No impact on normal voice latency.
- security: Transmit only opaque job ids and status classes, not task text or page contents. Authenticate alerts and expire them so a replay cannot vibrate the device indefinitely.
- depends on: A durable relay-to-pendant alert endpoint and job-state event mapping; Firmware event queue with deduplication and quiet-hours/mute state; Battery and enclosure validation for the pendant’s actual power and mechanical budget


## What it asked for

_Nothing._
## Its own summary

Recorded three owner-facing gaps. (1) A cross-surface, freshness-barrier answer that simultaneously checks Mac/project state and authenticated browser state, preserves redacted evidence, and speaks only facts plus explicit uncertainty. (2) A pendant haptic alert channel for delegated work completion/failure while the owner is away or audio is unavailable. (3) A deliberate pendant emergency-containment action that revokes relay/Mac/browser leases and pauses queued work across the hive. The required changes are respectively a shared evidence envelope/coordinator, haptic hardware plus firmware and alert delivery, and epoch-based revocable leases with fan-out containment. The tools/routes exist only as disconnected pieces; the missing work is the connective protocol and durable state.

**Biggest unknown:** Whether the current pendant PCB has an unused GPIO/power path and enough enclosure/battery margin for an LRA/ERM; hardware-specific validation was intentionally not performed because the owner said to stop discovering this round.

