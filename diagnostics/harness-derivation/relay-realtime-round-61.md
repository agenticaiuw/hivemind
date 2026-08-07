# Harness derivation — relay-realtime — round 61

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I leave my desk, package my current work so I can ask from the pendant later, and when I say 'resume that work,' put me back where I was with a concise spoken handoff."
- **useful because:** The pendant is usually worn away from the Mac. This bridges the physical gap: the Mac captures the active work context, the browser contributes authenticated tab state, the relay keeps a durable handoff, and the pendant lets the owner recover context without remembering filenames, tabs, or unfinished steps.
- **path:** pendant → mac-planner → browser-extension → relay → dashboard
- **model tier:** Use relay-realtime only for the short spoken acknowledgement and retrieval conversation; use mac-planner's cheaper planning tier for capture/restore, and deterministic Mac/browser harnesses for state collection. No vision model is needed unless a tab cannot expose structured state.
- **latency:** Leaving-desk capture acknowledgement under 2 seconds, with packaging completing asynchronously in 10–30 seconds. Spoken resume summary under 3 seconds after the owner asks; restoration may continue in the background with progress receipts.
- **cost:** About $0.01–$0.05 per capture/resume depending on planner calls; most cost is one planner invocation to summarize and restore, while deterministic state collection is negligible.
- **security:** The package may contain document names, unsaved text, URLs, and authenticated page excerpts. Store encrypted, bind it to the owner's device/session, expire it by default, and never speak sensitive excerpts aloud unless explicitly requested. Restoration of unsaved edits or external side effects should be reported and, where destructive, require an explicit spoken confirmation.
- **missing:** A durable handoff record containing app/window/document/browser-tab provenance and timestamps, rather than only transient job receipts; Mac harness operations to enumerate active windows and safely reopen the captured workspace, including an explicit policy for unsaved documents; Browser-extension export/import of a selected tab set with session-safe metadata (URL/title/scroll and editable draft state where supported); Relay endpoints and pendant commands for creating, listing, selecting, expiring, and resuming handoff packages; A compact spoken-summary generator that cites which surface supplied each fact and clearly marks stale or unavailable context


## Changes it proposed to its own stack

### `relay` — Add a first-class "task receipt" channel in the relay that always returns a spoken status line combining relay_job_status (queued/running/completed/failed) with known fleet blockers (e.g., browser extension offline, Accessibility/ScreenRecording disabled). It should never claim completion unless the job status says done, and it should preserve the job id for follow-up. Provide a short, stable spoken format sized for the pendant speaker.
- **owner gets:** They get a clear, consistent answer to "did that thing happen?" even when the Mac is asleep, and they learn what is blocking progress without guessing.
- effort: Medium. Mostly glue logic and a small status formatter; requires reading existing ops status and job records.  ·  risk: Low. Main risk is misreporting state if sources disagree; mitigate by prioritizing job status for completion and labeling blockers as blockers, not failures.
- cost: Low API cost: one job-status read plus one ops-status read when requested.  ·  latency: Low; both reads are lightweight and avoid a Mac round-trip.
- security: Low; exposes only task status and blocker metadata, no sensitive content.
- depends on: relay_job_status tool availability in this runtime; ops status endpoint stability

### `context` — Add a durable, privacy-scoped task identity graph shared by relay, Mac planner, and browser harness. Each spoken request gets a stable task handle; plans, job receipts, Mac paths/apps, browser tab/session identifiers, extracted evidence, failures, and owner corrections attach to that handle. Resolve later references such as 'the one about the contract' using recency plus provenance, and expose a compact spoken/dashboard timeline rather than replaying full transcripts.
- **owner gets:** The owner can continue work naturally from the pendant—'what happened with that?' or 'finish the one I started on the train'—without repeating context or guessing which Mac job and browser tab they mean. It also makes stale, failed, or partially completed work understandable in one place.
- effort: Medium-high: schema and durable storage in the relay, correlation middleware across plan/execute/browser APIs, entity resolution, retention controls, and Mac/browser adapters that emit stable provenance. Build a read-only first version before enabling reference-based execution.  ·  risk: Wrong entity resolution could cause an action on the wrong task. Mitigate by speaking the resolved task title and source evidence before any non-read-only action, retaining immutable links to receipts, and allowing 'list candidates' fallback. A relay outage should degrade to explicit task IDs and never silently merge records.
- cost: Low storage cost; roughly one small structured write per event and an occasional inexpensive summarization call. Avoid resending full transcripts by storing normalized facts and pointers.  ·  latency: Add under 100 ms for correlation writes on the hot path; reference resolution can use a small model or indexed metadata and should complete within about 1 second before speech.
- security: The graph is sensitive because it links authenticated browser activity to voice requests. Encrypt at rest, isolate by owner/device, redact page bodies by default, retain only hashes/URLs/titles unless evidence is needed, and provide spoken/dashboard deletion and expiration.
- depends on: Durable relay storage with owner/device scoping; A correlation ID propagated through /plan, /execute, Mac jobs, and browser jobs; Structured receipts from both Mac and browser harnesses; A small indexed retrieval/resolution service and retention controls


## What it asked for

_Nothing._
## Its own summary

Recorded two new proposals. (1) Away-from-desk work handoff: the Mac and authenticated browser package the current workspace, the relay stores it, and the pendant later restores it with a spoken summary. (2) A durable cross-surface task identity graph links voice requests to Mac/browser evidence and receipts so the owner can refer naturally to unfinished work without repeating context. Both require new durable relay/context primitives and explicitly account for security, latency, and cost.

**Biggest unknown:** Whether an existing backlog item already covers either workspace handoff or cross-surface task identity; I was instructed not to perform further discovery this round, so these were intentionally scoped beyond the known receipt, briefing, and browser-read items.

