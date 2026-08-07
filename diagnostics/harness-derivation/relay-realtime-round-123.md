# Harness derivation — relay-realtime — round 123

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say something like “open the thing I was working on yesterday,” route it safely and tell me whether it’s queued, in progress, or done."
- **useful because:** This is the everyday voice workflow: vague references, context, and status. The owner shouldn’t have to remember job IDs or which agent did what; the system should resolve it and report back clearly.
- **path:** relay → mac-bridge → browser → mac-bridge → relay
- **model tier:** Realtime for interpreting the utterance and asking a quick clarification; cheaper planner tier for the actual workflow; relay status read for updates.
- **latency:** Under a second to acknowledge and clarify. The actual work can take longer on the Mac; status updates should be near-instant from relay job records.
- **cost:** Low per invocation. Most cost is the planner/computer-use tier and any browser automation; relay status reads are cheap.
- **security:** Avoid guessing the wrong target. Use job receipts and references; prefer safe, reversible actions and require explicit confirmation only for destructive changes. Do not expose sensitive page contents in spoken replies.
- **missing:** relay_route_intent needs an implementation, not just a schema; relay_job_status exists but relies on correct receipt writing and durable job records; a shared reference model for “that thing” linking speech, plans, and receipts

### "“I’m back—what changed while I was away?” Give me a short spoken summary of only meaningful changes across my Mac and authenticated browser tabs since I left, and let me ask for any item in detail."
- **useful because:** The pendant is worn away from the Mac, so the owner currently has no low-friction way to recover the context that changed during an absence. This creates a cross-node departure/return experience: the pendant identifies the return, the always-on relay holds the comparison point, Mac perception inspects local changes, and the browser harness inspects authenticated tabs without exposing raw pages unnecessarily.
- **path:** pendant → relay → mac-planner → browser-extension → faculty-perception → faculty-judgement
- **model tier:** Use the realtime model only to interpret the short spoken request and read the final answer. Use a cheaper background model (or deterministic diffing first) to compare typed Mac/browser snapshots, rank meaningful changes, and produce the brief; invoke realtime again only for follow-up detail.
- **latency:** Initial spoken answer within 2–4 seconds when both surfaces are online; degrade to an explicit partial answer in under 1 second if one surface is unavailable. Detailed follow-ups can take up to 8 seconds.
- **cost:** Typically <$0.02 per return check if typed snapshots and deterministic diffs dominate; up to ~$0.08 when an LLM must rank many changes. The main cost is browser-page summarization, not the short voice turn.
- **security:** Snapshots should contain typed metadata and redacted excerpts rather than whole page contents; authenticated browser data must remain within the browser/relay boundary and be disclosed only in the spoken response. Retain only the previous and current checkpoint plus a short result, with an owner command to discard the checkpoint. Require explicit confirmation before opening or reading sensitive changed content in detail.
- **missing:** A durable departure checkpoint store keyed to the pendant session and a return/compare operation; Mac typed perception snapshot covering active apps, notifications, changed files, and actionable app state; Browser authenticated-tab checkpoint and typed change extraction; Cross-surface significance ranking and cited spoken brief; A pendant return trigger (button gesture, reconnect event, or explicit voice phrase) and graceful partial-result handling

### "“Can I leave my Mac?” Check whether anything needs my attention before I go—unsaved work, active calls or recordings, running uploads, low battery, and urgent browser or app state—and answer me by exception only."
- **useful because:** A wearable owner needs a reliable departure decision without walking back to inspect the Mac. This combines local Mac perception, authenticated browser state, relay aggregation, and judgment into a concise safety/context check; neither the pendant nor Mac alone can provide the same cross-surface answer while the owner is physically leaving.
- **path:** pendant → relay → mac-planner → browser-extension → faculty-perception → faculty-judgement
- **model tier:** Use deterministic typed checks and a cheap background ranker for the normal case. Realtime handles only the spoken question and the short exception summary; use a stronger model only when evidence conflicts or an app state is ambiguous.
- **latency:** Under 3 seconds for a normal check, with a partial answer in under 1 second when a surface is offline. Never block the owner’s departure on an optional deep inspection.
- **cost:** About <$0.02 per check when Mac and browser return typed status; ~$0.05–$0.10 only for ambiguous evidence requiring model interpretation. Network and browser inspection dominate latency, not voice generation.
- **security:** Return only exception facts and minimal app/site names by default; do not speak document contents or page text in public. Treat active calls, recordings, and unsaved files as sensitive. The check is read-only and should not alter or close anything; expose provenance and freshness so stale status is never presented as current.
- **missing:** A single typed departure-readiness endpoint aggregating Mac and authenticated browser observations; Mac observers for unsaved documents, active calls/recordings, uploads, battery, and foreground work state; Browser observer for pending uploads, unsent forms, and session warnings; Freshness/partial-availability semantics and a spoken exception-ranking response schema; A pendant command phrase/button shortcut that works while the owner is already walking away


## Changes it proposed to its own stack

### `integration` — Add a shared “reference binding” ledger that links a spoken phrase, a plan/execution jobId, and the resulting receipt(s). Provide a minimal API to resolve vague references (e.g. “that”, “the Outlook thing”, “yesterday’s note”) to the most recent matching job, with confidence and a fallback to ask a clarification question.
- **owner gets:** They can talk naturally and still reliably resume, check, or undo work. The system becomes usable in real life, not just in demos where tasks are explicit and short.
- effort: Medium to high: needs a small data model, write paths in relay and Mac planner, and read paths for status/undo. Also needs a policy for ambiguity.  ·  risk: Medium: misbinding could operate on the wrong task. Mitigate with confidence thresholds, recency bias, and asking for clarification when ambiguous.
- cost: Small storage and query cost; most cost is in the planner tier when resolving complex references.  ·  latency: Small overhead for binding; big reduction in conversational friction and retries.
- security: Bindings contain sensitive task context; protect with access control and avoid leaking details in spoken responses.
- depends on: durable job records with receipts (or equivalent); relay_route_intent implementation (or another authoritative routing record)

### `integration` — Add a read-only /v1/return-and-departure/assessment operation that fans out to Mac status/readonly inspection and authenticated browser inspection, normalizes observations into typed facts with timestamps and provenance, ranks only actionable exceptions, and returns a partial result with explicit stale/offline fields. Expose it to the realtime relay as a short spoken response and to follow-up detail requests without replaying raw page or document contents.
- **owner gets:** The owner can decide whether it is safe to walk away from the Mac by asking the pendant once, instead of manually checking several apps and browser tabs. It prevents both false reassurance and an overwhelming dump of irrelevant state.
- effort: Medium: define the typed observation schema, adapters for existing Mac/browser routes, freshness semantics, exception ranking, and a relay response formatter; add integration tests for each surface being offline or stale.  ·  risk: An observer may miss an app-specific unsaved state or report stale data. Recover by labeling every fact with source/time, saying 'I could not verify' rather than 'clear,' and keeping the operation strictly read-only. Browser inspection failures must not cause the Mac result to be presented as complete.
- cost: Small per-request API cost; deterministic normalization should dominate. No new hardware cost. A compact typed payload reduces repeated context and spoken-token cost.  ·  latency: Parallel Mac/browser fan-out keeps normal latency near the slower surface, roughly 1–3 seconds; timeout each adapter and return partial results rather than waiting indefinitely.
- security: No mutation authority. Minimize sensitive data to app/site names, state categories, and counts; redact document/page text and preserve provenance internally for an explicit detail request.
- depends on: A stable typed observation contract from the Mac planner and browser harness; Relay-side endpoint or tool implementation for the aggregator; Pendant voice/button trigger and concise exception speech formatter


## What it asked for

_Nothing._
