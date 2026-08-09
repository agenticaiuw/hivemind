# Harness derivation — unified — round 198

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Give me my scheduled briefing, but only speak claims that have fresh source evidence, tell me what is stale or failed, and let me ask ‘why?’ for the exact source.”"
- **useful because:** Today a routine can report completed while the pipeline shows failed runs and a briefing can become spoken without a transparent freshness boundary. This makes the wearable's short spoken brief trustworthy: relay gathers, Mac/browser researches, the system grades each claim, and the pendant speaks only evidence-backed material while retaining a compact source trail.
- **path:** relay-realtime → mac-planner → browser-extension → mac-vision → pendant → dashboard
- **model tier:** background for scheduled research and deterministic evidence grading; realtime only for the owner's follow-up question and concise explanation
- **latency:** Scheduled brief may take 1–3 minutes; follow-up source explanation under 2 seconds if the evidence capsule is cached
- **cost:** ~$0.01–$0.05 per scheduled brief depending on research depth; browser fetches and storage dominate, not realtime tokens
- **security:** Bind each claim to an allowlisted URL/tab and timestamp; redact credentials and page-private text from the capsule; never take an external action from a claim without a separate physical approval. Stale or failed sources must be spoken as such, never silently omitted.
- **missing:** claim-level evidence schema and freshness policy; relay persistence for evidence capsules and failed-source states; a briefing speech path that includes claim IDs without reading URLs aloud; dashboard/source drill-down UI

### "“Show me every personal fact this system inferred about me, where it came from, what copies exist, and forget just the ones I choose—then prove what is still pending off-device.”"
- **useful because:** The owner policy says unsolicited extracted facts must be listable and individually deletable, but the live graph visibly contains opaque entities such as an Unknown Person and derived copies are not presented as one object. A provenance-preserving erasure view turns hidden memory into something the owner can govern without deleting the action audit trail.
- **path:** mac-planner → relay-realtime → browser-extension → dashboard → pendant
- **model tier:** deterministic for enumeration, dependency closure, deletion and receipts; background model only to render human-readable summaries of evidence already selected
- **latency:** List under 1 second locally; local deletion under 2 seconds; off-machine acknowledgement reported asynchronously and never presented as complete until confirmed
- **cost:** <$0.01 per request; storage indexing and replicated deletion receipts dominate
- **security:** Require explicit selection and physical approval for destructive erasure; redact raw audio and secrets in previews; preserve job history but remove fact evidence capsules and all derived projections; return requested/pending states for relay replicas and make retries idempotent.
- **missing:** a fact-to-evidence dependency index spanning facts.json, context graph and relay rows; a single deletion transaction with idempotency key and off-machine tombstone; owner-facing route/UI for provenance and pending erasure receipts; a policy distinction between extracted facts and owner-created reminders/tasks

### "“Before my routine speaks, tell me whether the Mac, browser session, relay, and pendant can all complete it; if one is down, give me the exact degraded result instead of pretending it ran.”"
- **useful because:** The live system already exposes routines, pipeline runs, browser status, Mac health, and pendant/relay diagnostics, but they are separate and a routine can be marked completed while its audio or source delivery failed. A preflight-and-degraded-brief contract lets the owner trust scheduled behavior and know whether they heard a complete result.
- **path:** relay-realtime → mac-planner → browser-extension → mac-vision → pendant → dashboard
- **model tier:** deterministic health/capability joins and policy decisions; background model only to summarize degraded outcomes; realtime only if the owner asks during an active session
- **latency:** Preflight 300 ms target from cached heartbeats; hard timeout 2 seconds, then speak a bounded degraded notice and retain the work for retry
- **cost:** <$0.005 per run when using cached health; occasional model summary ~$0.01; network probes and receipts dominate
- **security:** Health results must not expose tab URLs, tokens, or page content; bind the verdict to routine ID and run ID; do not auto-retry irreversible actions; require physical approval for any recovery action beyond restarting polling or waking a bridge.
- **missing:** correlated run contract joining routine, pipeline, browser, relay and audio delivery states; fresh heartbeat/lease semantics for pendant and bridge, including LTE-unregistered state; degraded speech templates and a dashboard timeline; policy for whether to retry, defer, or cancel each routine class

### "“Before you touch anything, show me the exact browser and Mac changes this plan would cause, including what could not be predicted, and let me approve only the named effects from the pendant.”"
- **useful because:** A textual plan and a generic approval are not enough when a workflow spans authenticated browser tabs, Mac files, and a wearable. The owner should see a compact before/after effect set, with uncertainty called out, and bind physical approval to that exact set rather than approving a vague command.
- **path:** mac-planner → browser-extension → mac-vision → dashboard → pendant → relay-realtime
- **model tier:** deterministic state capture/diff and risk classification; planner model only to turn the verified diff into plain speech
- **latency:** Preview under 2 seconds for local state; browser-dependent previews may take 5 seconds and must expire if state moves
- **cost:** <$0.01 per preview; screenshots/state hashing and browser round trips dominate
- **security:** Never include page secrets or full file contents in the preview; hash and redact sensitive values; approval nonce must bind plan digest, world snapshot, expiry, and physical gesture. If any predicted effect becomes unknown, invalidate rather than broaden approval.
- **missing:** cross-surface before-state adapters and effect diff schema; world-change invalidation for browser tabs and Mac files; dashboard and pendant rendering of a bounded effect summary; execution gate that refuses any action outside the approved digest

### "“When I say ‘I’m done with this’, close out the conversation, cancel only its outstanding work, and tell me what was stopped, what already happened, and what cannot be undone.”"
- **useful because:** The system has sessions, jobs, browser commands, pipeline runs, and audio queues, but no owner-level end-of-task boundary. A single spoken close command should prevent stale work from continuing across relay, Mac, browser, and pendant while preserving the audit trail and clearly separating completed effects from cancelled ones.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-vision → dashboard
- **model tier:** deterministic correlation, cancellation, and receipt classification; realtime model only to resolve the utterance and summarize the final state
- **latency:** Stop newly cancellable work within 1 second; reconcile stragglers within 10 seconds; summary can be spoken as soon as the first authoritative receipts arrive
- **cost:** <$0.01 per close request; reconciliation polling and durable receipts dominate
- **security:** Scope cancellation to an explicit session/conversation nonce, never global jobs; do not claim cancellation for already-dispatched irreversible actions; preserve action history and expose partial completion. Require confirmation for cancelling a separately scheduled routine.
- **missing:** session-to-job/browser-command/pipeline/audio correlation; idempotent cross-surface cancellation protocol with leases; a final-state classifier for stopped|completed|in-flight|irreversible; pendant command recognition and owner-facing reconciliation receipt

### "“Move my active preferences, trusted devices, and unfinished conversation to a replacement pendant or Mac without copying my old audio or hidden memory, and show me exactly what crossed the boundary.”"
- **useful because:** A wearable or Mac can be replaced, reset, or temporarily unavailable, but today context is tied to local stores and sessions with no owner-controlled migration boundary. A selective, encrypted handoff would preserve continuity without silently exporting recordings, inferred facts, browser secrets, or the action audit trail.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** deterministic selection, encryption, manifest verification, and import; no expensive model needed except an optional realtime explanation of excluded items
- **latency:** Create a manifest under 2 seconds; transfer/import under 30 seconds for preferences and active context; refuse rather than partially import if integrity checks fail
- **cost:** <$0.01 per migration; encrypted transfer and manifest storage dominate
- **security:** Owner selects categories explicitly; encrypt to the destination device key; exclude raw audio, inferred facts, browser cookies/tokens, and job history by default; require physical approval on the source and destination or an equivalent out-of-band pairing; provide a signed manifest and a deletion/expiry policy for the relay copy.
- **missing:** versioned selective context-capsule format; device-key pairing and destination authentication; export/import endpoints with category allowlists and atomic rollback; owner-facing manifest showing included, excluded, and pending items


## Changes it proposed to its own stack

### `integration` — Add a typed routine-run completion contract that is created before execution and closed only when every declared deliverable has a receipt: source acquisition, browser result (if requested), Mac artifact, relay persistence, and pendant audio delivery/hearing. Store per-deliverable status as pending|succeeded|degraded|failed|not_applicable, freshness timestamps, retryability, and a stable run ID. Make /routines/:routineId/run and /pipeline emit the same contract instead of independent success strings; have scheduled speech render the contract rather than infer success from the last job status.
- **owner gets:** A scheduled brief will stop saying it completed when the research failed, the browser was offline, or audio never reached the pendant. The owner hears exactly what happened and can retry only the missing part.
- effort: Medium: schema and state transitions are straightforward, but relay/Mac/pipeline/audio receipt correlation and migration of existing routine statuses require careful integration tests.  ·  risk: Existing consumers may assume completed means a single boolean; version the contract and preserve legacy fields. A missing receipt must become degraded, never silently successful. Recover by replaying only idempotent deliverables using the existing job/run IDs.
- cost: Negligible storage and token cost; roughly one small record per routine run and fewer unnecessary model retries.  ·  latency: <100 ms local bookkeeping; no added model latency. Preflight may add up to 300 ms if fresh health is required.
- security: Use opaque run IDs and redact URLs/page contents from owner-facing speech; preserve audit history. Any recovery action remains behind the existing approval/physical latch.
- depends on: relay job lease/requeue semantics; audio delivery acknowledgement queue; correlation fields joining routine run, pipeline, browser result and pendant delivery receipt


## What it asked for

_Nothing._
## Its own summary

Round 198 produced three recorded owner-facing capabilities and one integration change. The strongest is a typed routine-run completion contract: scheduled work must correlate research/browser/Mac/relay/pendant audio receipts and speak degraded truth instead of a misleading completed flag. I also proposed evidence-backed briefings with claim-level freshness/source drill-down, and owner-controlled provenance-preserving deletion of inferred facts with pending off-device erasure receipts. I discovered the live graph contains opaque inferred entities and the live routine/pipeline surfaces are separate; the Mac bridge is online while the mobile device is offline.

**Biggest unknown:** The missing cross-surface correlation contracts are not yet inventoried or implemented: specifically how a routine run ID maps to browser results, relay jobs, pipeline audio, and the pendant's actual-heard receipt. I still need that schema and owner policy for which degraded outcomes should retry versus merely be reported; I did not assume either.

