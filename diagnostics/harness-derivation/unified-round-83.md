# Harness derivation — unified — round 83

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser failure recovery** — The live journal shows a specific idempotency key for browser_navigate failed 6 of 6 runs, while a different navigate key succeeded 7 of 7; current browser status is online with 7 pending commands. This supports a per-request circuit breaker rather than assuming the browser is globally offline.
  - evidence: GET /journal at 2026-08-07T12:59Z: repeatedActions act_36a2da2b0b8c runs=6 failed=6; act_d183ad77fc69 runs=7 failed=0. GET /browser/status: online=true, pendingCommands=7.

## Capabilities it proposed

### "If something I asked you to do gets stuck, recover it without repeating a submission, and tell me on the pendant exactly where it stopped and what I need to approve."
- **useful because:** Today a failed browser step can be retried blindly while the owner is away from the Mac. This makes the wearable, relay, Mac, and browser one resumable workflow: the pendant is the interrupt and approval surface, the relay keeps the durable checkpoint, and the Mac/browser recover using the session that actually has access.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic circuit-breaker and checkpointing first; use the cheaper background model to summarize the incident. Escalate to planner only when choosing among genuinely different recovery paths; realtime is only for the spoken alert and approval exchange.
- **latency:** Speak a concise stuck/recovered notice within 2 seconds of a classified failure; recovery probes can run in the background. Never make the owner wait through repeated 45-second retries.
- **cost:** Usually near-zero model cost for classification and receipt assembly; one background summary only for a nontrivial incident. Dominant cost is a single alternate read-only browser probe, not conversation tokens.
- **security:** Never replay writes automatically. Keep private authenticated pages on the Mac/browser bridge; only public pages may use server-side browsing. The pendant announcement should omit page contents and say only app/site, checkpoint, and approval needed. Owner confirmation is required to resume a mutation.
- **missing:** Durable cross-surface checkpoint schema linking relay job, browser requestId, tab/session, evidence capsule, and next step; Failure classifier/circuit breaker and one-shot backend fallback; Pendant event/approval protocol for resume or abandon; A tested public/private Browser Run routing policy

### "When you are unsure which of my open tabs, accounts, or Mac documents I mean, ask me one short disambiguating question on the pendant with the two concrete choices, then continue without making me repeat the whole task."
- **useful because:** Today ambiguity is resolved by whichever surface happens to answer first, or by sending a long task back to the planner. The owner should be able to resolve identity while away from the screen: the browser contributes candidate tabs and evidence, the Mac contributes document/app candidates, the relay reduces them to a safe choice, and the pendant captures the owner's answer. This prevents acting on the wrong private account or document without requiring a desktop session.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Deterministic candidate collection and identity matching first; use a cheap background model to rank and phrase the two choices. Use realtime only to ask/hear the short question and parse the answer. Escalate to the planner only if no safe pair can be formed.
- **latency:** Candidate collection under 3 seconds when surfaces are online; the question must be spoken in under 5 seconds. Wait indefinitely for the owner's answer without expiring the task, while preserving the candidates and their timestamps.
- **cost:** Normally no expensive model call: typed metadata and deterministic ranking. A small background call is the dominant cost only when labels need semantic comparison; realtime cost is limited to the brief clarification turn.
- **security:** Read only titles, domains, app names, and redacted snippets into the candidate set; never speak full sensitive content. Do not expose candidate names from unrelated tabs. Bind the owner's answer to the exact tab/document IDs and freshness timestamps, and invalidate it if the selected surface changes before execution.
- **missing:** A cross-surface candidate identity protocol with stable tab/document identifiers and freshness; A relay-held clarification state that pauses the task without losing its plan; Pendant two-choice prompt and response grammar; A policy for redacting sensitive candidate labels before speech


## Changes it proposed to its own stack

### `browser-harness` — Add an evidence-driven browser failure circuit breaker and resumable handoff. For each requestId/idempotencyKey, classify timeout, tab-disconnect, navigation-error, and auth-block separately; after two identical failures stop replaying the same command, capture current tab/session health and last evidence capsule, try exactly one safe alternate backend (authenticated Mac bridge versus server Browser Run when the page is public), then persist a checkpoint with the last confirmed URL/DOM hash and the next non-duplicating step. Emit a pendant-readable failure/recovery event and require confirmation before retrying any mutation.
- **owner gets:** The system will stop burning minutes repeating a dead browser command and will not accidentally submit something twice. The owner hears whether it recovered, needs one tap to resume, or needs to take over, with proof of the last known page.
- effort: Medium: local-agent circuit-breaker/checkpoint store, relay event schema, Browser Run fallback adapter, and dashboard/pendant rendering; test against the observed repeated browser_navigate failures.  ·  risk: A backend switch can lose a private authenticated session or misclassify a transient LTE/Mac outage. Keep mutations disabled during recovery, require same-origin/session checks, retain the original request for manual retry, and make fallback read-only unless explicitly approved.
- cost: Negligible API cost for deterministic classification; one extra read-only probe at most. Storage is a small checkpoint and evidence reference per failed job.  ·  latency: Fast failure after the second identical timeout instead of another 45-second wait; alternate read-only probe adds roughly one round trip.
- security: Do not send private page contents to Browser Run; route only public URLs there, and record backend choice plus evidence hashes. Confirmation remains mandatory for writes.
- depends on: chg-14accc01 request IDs/tab affinity/typed browser results; the existing action receipts/evidence capsules and /journal; a read-only Browser Run adapter with explicit public-versus-private classification


## What it asked for

_Nothing._
