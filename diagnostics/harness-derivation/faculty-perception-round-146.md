# Harness derivation — faculty-perception — round 146

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac and browser observability** — At 2026-08-08T01:53Z, /observe reports inputReachability.status=verified, Accessibility and Screen Recording granted, secure input false, and UI actions will reach screen. /ops/status reports Mac bridge and Safari extension online, browser tab x.com, pendingCommands=0, and relay reachable with D1 store. No pendant appears in live device discovery.
  - evidence: GET /observe, GET /ops/status, discover(devices) in round 146
- **Mac watch subsystem** — GET /watches is live and returns two persisted watches, both currently enabled:false. It already stores observed and previous field values plus change reports and acknowledged flags at /Users/evanliu/AI-Pendant-Workspace/.pendant-page-watches.json. Therefore a watch capability should extend this subsystem rather than propose a new watch store.
  - evidence: GET /watches returned HTTP 200 at 2026-08-08T01:53Z with wch_ccde... and wch_e466...

## Capabilities it proposed

### ""When I come back, tell me the one thing that needs my attention and let me resume it exactly where it stopped.""
- **useful because:** This would turn scattered stale jobs, browser tabs, relay work, and offline pendant events into a resumable handoff rather than a best-effort activity digest. It is the single most useful perception capability: it distinguishes owner-visible completion from mere Mac/relay acceptance, names the missing evidence, and gives a concrete resume target (tab, job, or approval).
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** background for assembling and ranking the handoff; realtime only to speak the final short result when the owner asks
- **latency:** under 3 s after the owner asks; under 1 s if a cached snapshot is fresh
- **cost:** <$0.01 per request when cached; dominated by one small ranking/context pass, not realtime audio
- **security:** Must not expose browser page text or tokens in the spoken summary; use capsule IDs, redacted snippets, and explicit confidence. Require confirmation before resuming an external action. Pendant absence must be reported as unknown, never offline-heard.
- **missing:** A resolved authenticated continuity snapshot tool (the granted read_continuity_snapshot currently fails resolution; GET /ops/snapshot is the nearest live route); A durable resume pointer joining pipeline/job receipts to browser session/tab and pending approval; A device-originated playback/consumed event, when a pendant exists

### ""Watch this logged-in page and tell me only when its important state changes, with proof of what changed.""
- **useful because:** The browser extension can observe an authenticated tab that the relay cannot reach. A content-addressed, redacted before/after capsule lets the owner know whether a billing, delivery, or account page actually changed, instead of receiving repeated screenshots or untraceable relay summaries.
- **path:** browser-extension → mac-planner → relay → pendant → dashboard
- **model tier:** background/scheduled polling and hash comparison; realtime only for the owner's spoken query
- **latency:** poll at an owner-selected cadence (5–60 min); spoken result under 2 s from cached evidence
- **cost:** <$0.005 per poll when unchanged (hash/redaction locally); occasional small model pass only for semantic change ranking
- **security:** Never send raw authenticated page content to relay. Redact locally, persist only capsule hashes and bounded claims, allow revocation, and require confirmation before opening or acting on a changed page.
- **missing:** A mounted browser provenance route and watcher that calls existing mintCapsule/recordExtraction; A relay notification path carrying capsule ID/hash rather than page text; Owner-configurable watch policy (what counts as important and quiet hours)

### ""If my speech was captured badly, stop the system from acting on it and ask me to repeat—then tell me whether the repeat was clear.""
- **useful because:** The pendant's offline capture sentinel can detect clipping, packet gaps, noise, and clock discontinuity before a cloud planner turns a bad utterance into a real action. The relay can retain the quality verdict, while the Mac planner can gate execution and the pendant can ask for a repeat locally even without LTE.
- **path:** pendant → relay-realtime → mac-planner → dashboard
- **model tier:** device-local rules for immediate gating/repeat; cheap background model only to summarize recurring quality problems
- **latency:** local verdict and repeat prompt within 200 ms of utterance end; planner gate before any action dispatch
- **cost:** negligible device/relay overhead; <$0.001 for optional summary, with no model call for clear audio
- **security:** A degraded verdict must fail closed for consequential actions, but never silently discard the owner's words; retain only metrics and sequence IDs by default, not raw audio. Require explicit confirmation if a low-confidence repeat is the only available input.
- **missing:** A relay contract for the sentinel's sequence-numbered quality frame; Planner policy that treats clear/degraded/unusable as an execution gate; A visible dashboard explanation when an action was withheld due to capture quality

### ""Only carry out sensitive browser actions while I am physically present; if I walk away or the pendant is unavailable, pause and ask me to re-authorize.""
- **useful because:** A logged-in browser session can reach accounts the relay cannot, while the pendant is the owner's physical presence. Binding a short-lived action lease to a pendant presence beacon, a fresh spoken challenge, the Mac bridge, and the exact browser tab would prevent a queued or delayed agent from sending messages, purchasing, deleting, or changing account settings after the owner has left.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** cheap rule engine for lease and presence checks; realtime only for the fresh spoken challenge
- **latency:** presence check under 150 ms; challenge response under 2 s; no action dispatch if the lease is stale
- **cost:** negligible per action; one short realtime turn only when a sensitive action needs re-authorization
- **security:** Presence is not identity by itself: require a nonce bound to the action, never expose session cookies, expire leases within 60 seconds, and require explicit confirmation for irreversible actions. If the pendant is absent, fail closed rather than infer presence from the Mac.
- **missing:** Pendant-to-relay monotonic presence frames and nonce signing; Browser command executor enforcing an action lease immediately before mutation; A policy registry classifying actions by sensitivity and lease duration

### ""When something goes wrong, show me the complete chain from what I said to what changed, including the exact evidence and the undo point.""
- **useful because:** Today a pipeline can be marked complete even when playback is unknown, and a browser mutation can be separated from its originating request. A cross-surface incident replay would let the owner audit a consequential action: captured utterance quality, transcription, plan, approval, browser evidence, mutation receipt, and resulting state, with gaps called out instead of invented success.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** background deterministic event join and redaction; use a cheap model only to explain the timeline in plain language
- **latency:** cached replay opens in under 2 s; full evidence hydration under 5 s
- **cost:** <$0.01 per replay; dominated by optional summarization, since hashes and receipts are local
- **security:** Sensitive page bodies and audio stay local; dashboard shows redacted claims by default. Every event needs source, timestamp, correlation ID, and confidence. Undo must be offered only when an authenticated reversible receipt exists.
- **missing:** One correlation ID propagated from pendant utterance through relay job and Mac pipeline; A durable join between action ledger, browser provenance, pipeline events, and relay job receipts; A dashboard replay view that distinguishes observed, asserted, and missing evidence

### ""Before you tell me that a real-world task is done, independently verify the result and keep checking until it is actually true.""
- **useful because:** The system can currently execute a browser or Mac step and report that the agent finished, but completion is often only local acceptance. A verification loop would use the browser session for authenticated state, Mac APIs for local state, the relay for delayed work, and the pendant for a concise result: done, not done, or unable to verify. It would catch silent failures such as an email left in draft, a setting not saved, or a page that reverted.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** background deterministic postcondition checks with a cheap model for ambiguous page text; realtime only for the final spoken answer
- **latency:** initial verification within 3 s; scheduled recheck according to task policy, from 1 minute to 24 hours
- **cost:** <$0.01 per verification cycle; mostly local browser/Mac reads, with model calls only for ambiguous claims
- **security:** Verification reads may expose authenticated data, so redact and hash locally. Never mutate while verifying. A timeout must be reported as unverified, not failed or complete; delayed retries require owner policy and confirmation for consequential changes.
- **missing:** A typed postcondition schema attached to each planned action; A scheduler that can re-open the same browser session or Mac resource without replaying the mutation; Relay-side durable verification jobs and a result state separate from execution completion


## Changes it proposed to its own stack

### `integration` — Introduce a single owner-intent envelope, created at the pendant or voice ingress, carrying intentId, utterance sequence, sensitivity class, and expiry. Propagate it unchanged through relay jobs, Mac pipeline events, browser commands, evidence capsules, action ledger entries, receipts, and final verification. Reject or quarantine any terminal result that lacks the envelope rather than silently attaching it by timestamp.
- **owner gets:** When an action is wrong or disputed, the owner can see exactly which spoken request caused it and whether every later event belongs to that request. This prevents two simultaneous tasks from being confused and makes the system able to say 'I cannot prove this was yours.'
- effort: Medium-high: protocol field changes across relay, Mac, browser extension, evidence, and dashboard, plus migration for legacy events.  ·  risk: Legacy jobs may lack an intentId and become unverifiable; show them as legacy rather than guessing. Envelope leakage could correlate sensitive activity, so use opaque random IDs and redact speech. Recover by accepting old events as unlinked.
- cost: Negligible storage and bandwidth; small background processing cost for joins.  ·  latency: Under 1 ms per local event; no meaningful voice latency.
- security: Improves auditability and prevents cross-task confusion, but requires careful access control because correlation reveals behavioral patterns.
- depends on: A defined terminal state for verification separate from Mac execution completion; A durable relay-to-Mac job correlation contract; A browser provenance writer mounted on the Mac


## What it asked for

_Nothing._
