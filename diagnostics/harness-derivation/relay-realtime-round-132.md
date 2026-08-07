# Harness derivation — relay-realtime — round 132

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“What was I looking at yesterday, what changed since then, and continue from where I left off.”"
- **useful because:** Today the owner must remember which Mac window, browser tab, document, and pending action formed a task. This would let the worn pendant recover a real interrupted task across an unattended Mac and authenticated browser, explain the delta with evidence, and resume it without making the owner reconstruct context.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use relay-realtime only for the short spoken clarification and final answer; use faculty-perception/background models to reconstruct yesterday’s evidence, mac-planner for Mac state, mac-vision only when a screenshot is required, and browser-extension for authenticated tab state.
- **latency:** Acknowledge in under 1 second on the pendant; return an initial recovered-task hypothesis in 5 seconds, then a cited change report and resumable next action within 30 seconds.
- **cost:** Roughly $0.03–$0.15 per recovery depending on whether vision and browser extraction are needed; the dominant cost is comparing stored page/document snapshots, not the spoken turn.
- **security:** This necessarily handles authenticated browser content and potentially private Mac documents. Keep evidence scoped to the owner’s explicit task, encrypt and expire snapshots, redact secrets from spoken output, and never resume a mutation until the owner explicitly says to continue. The owner’s maximum-access policy permits reversible inspection, but destructive or external sends still need the existing execution semantics.
- **missing:** A durable cross-surface task-thread record that links pendant utterances to Mac windows, browser tabs, documents, and action receipts over time; Periodic or event-triggered, privacy-scoped snapshots/digests of already-open browser tabs and relevant Mac app state, with timestamps and provenance; A delta/reconciliation service that can distinguish a changed document from a changed webpage and present cited evidence; A resume endpoint that hands the selected thread to mac-planner/mac-vision while preserving the thread and requiring explicit continuation for mutations

### "“While you’re doing that, stop before sending anything, change the recipient to Alex, and continue.”"
- **useful because:** A spoken correction after delegation currently arrives too late or forces the owner to start over. The owner should be able to interrupt a live Mac/browser workflow, inspect its next not-yet-started step, patch the plan, and resume while the pendant confirms exactly what was prevented and what changed.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** relay-realtime handles interruption intent and a concise confirmation; a cheaper planner validates and recompiles only the remaining action graph; mac-vision/browser-extension execute the revised steps; dashboard records the immutable before/after plan and receipts.
- **latency:** Detect the interruption in the next speech turn (<500 ms after transcript), issue a stop signal within 1 second, describe the safe boundary within 2 seconds, and resume within 8 seconds after the correction.
- **cost:** About $0.01–$0.06 per correction; most cost is replanning the remaining graph and re-reading the current browser/Mac state.
- **security:** The stop must be best-effort but explicit: report whether a step was already committed, never claim a prevented send without a receipt, and preserve an audit trail of original and patched plans. Patching must not silently alter already-completed mutations; external sends should remain clearly surfaced in the spoken confirmation.
- **missing:** A bidirectional live-control channel from relay-realtime to an executing Mac/browser job, with acknowledged stop-at-boundary semantics; Action-graph checkpoints identifying completed, in-flight, and not-started steps, plus typed receipts for each; A plan-patch endpoint that accepts a natural-language correction, recompiles only the remaining steps, and returns the revised graph; A pendant-visible result event carrying stop acknowledgement, committed-step evidence, and resume state


## Changes it proposed to its own stack

### `relay` — Implement the granted relay_route_intent schema as the relay’s default routing path for recognized intents, and connect it to the orchestrator’s existing plan/execute flow. The relay should emit a job record immediately and return a spoken status like “queued” plus a job id, then relay_job_status can answer follow-ups without Mac round-trips.
- **owner gets:** They can ask for something (“Open my project and summarize what changed”) and get a clear, consistent response about what’s happening, even if the Mac is asleep or busy. It removes ambiguity and prevents the relay from inventing its own routing behavior.
- effort: Medium: wiring and orchestration work, plus job record plumbing. No new model behavior required if the downstream planner already exists.  ·  risk: Misrouting or duplicate execution if the intent mapping is wrong. Mitigate with receipts and idempotency checks; keep actions reversible by default.
- cost: Low per request; the expensive part remains downstream planning/execution. Relay overhead is a small additional API call and job record write.  ·  latency: Slight increase at request time to create the routing envelope, but faster follow-ups because status checks avoid Mac round-trips.
- security: Intent routing must treat utterances as untrusted input. Ensure authentication on relay routes and strict schema validation; log minimal necessary data.
- depends on: Durable job runner or equivalent job record persistence so job ids are stable and queryable.; relay_job_status implementation to read those records (or reuse existing relay job store).

### `integration` — Implement the granted server_browser_actions schema using a sandboxed browser runtime (e.g., Cloudflare Browser Run) with a strict action list: navigate, query, extract, and return structured results. Add a policy that it only runs on public URLs unless an authenticated session mechanism is explicitly provided.
- **owner gets:** The pendant can answer simple web checks even when the Mac is offline, without waiting for a Mac planner round. That’s a big quality-of-life improvement when they’re out and about.
- effort: Medium to high: needs runtime integration, action serialization, timeouts, and output normalization. Additional work if authenticated browsing is desired.  ·  risk: Data exfiltration if it accesses private sites or follows unexpected redirects. Mitigate with URL allowlists/deny-lists, content-type checks, and strict timeout/size limits.
- cost: Moderate per run due to browser compute; keep it for cases where web_search/read_web_page is insufficient (dynamic pages).  ·  latency: Higher than a simple HTTP fetch, but still faster than waking the Mac for many tasks; bounded by timeout.
- security: High sensitivity: must restrict domains and sanitize extracted data. No credential handling unless a secure session system exists.
- depends on: A sandboxed browser runtime and orchestrator support for provisioning it.; Logging/receipts for actions and extracted outputs.

### `integration` — Make relay-realtime perform a live reachability preflight before dispatching any Mac UI action, cache the result for the short session, and turn downstream no-op/success-shaped receipts into a spoken, typed outcome: executed, queued, unavailable, or unverified. When Accessibility or Screen Recording is false, automatically choose browser/shell alternatives only when they are semantically equivalent; otherwise tell the owner the exact missing reachability and preserve the request for later retry rather than claiming success.
- **owner gets:** The owner can be away from the Mac and currently may hear that an action succeeded even when the Mac cannot control its UI. They get an honest answer and a useful fallback instead of believing a reminder, message, or browser change happened when it did not.
- effort: Medium: add a preflight adapter over /ops/status and /observe, normalize receipts in the relay, teach mac-planner to declare equivalence/fallbacks, and add regression cases for Accessibility=false, Screen Recording=false, browser-only success, and shell success.  ·  risk: A stale preflight could incorrectly avoid a newly available route, or an over-eager fallback could perform a different operation. Use a short TTL, include the observed timestamp in the spoken result, and require semantic equivalence from the planner; recovery is retry after the next preflight.
- cost: Negligible API cost; one small status request per session or after a reachability error. No hardware cost.  ·  latency: Adds roughly 100–500 ms on the first Mac-directed turn; subsequent turns use the short-lived cached status.
- security: Improves security truthfulness by preventing false completion claims. It does not add a permission gate or reduce the owner’s maximum-access policy; it only reports actual reachability.
- depends on: mac-planner exposes an explicit fallback/equivalence field and committed-step receipt; Relay can read the existing /ops/status and /observe responses from the Mac bridge


## What it asked for

_Nothing._
## Its own summary

Recorded three new proposals: (1) cross-surface recovery of an interrupted task with timestamped evidence and resume state; (2) spoken mid-flight interruption and patching of a live Mac/browser action graph; and (3) truthful Mac reachability preflight so the pendant never reports UI success when Accessibility/Screen Recording is unavailable. The latter is grounded in the live finding that UI actions currently produce no-op success-shaped receipts.

**Biggest unknown:** Whether the existing job runner and Mac bridge can expose step-level checkpoints and a bidirectional stop acknowledgement; those are the essential missing primitives for the interruption proposal.

