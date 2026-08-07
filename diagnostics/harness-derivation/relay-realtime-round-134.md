# Harness derivation — relay-realtime — round 134

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If I lose connection, keep my last voice command queued and send it when the link comes back, then tell me what happened."
- **useful because:** This makes the pendant feel reliable. The owner can speak once, even in patchy LTE-M coverage, and the system will catch up without manual retries.
- **path:** pendant → relay → mac-bridge → faculty-action
- **model tier:** Realtime only for capturing the utterance; a cheaper background tier handles retry and delivery once connectivity returns.
- **latency:** Capture must be immediate; delivery can be delayed by network conditions. Confirmation should arrive as soon as the relay learns the outcome.
- **cost:** Low per invocation. Cost dominated by storage of a small buffered transcript and retry attempts.
- **security:** Buffering stores potentially sensitive speech. Encrypt at rest on-device and in transit; retain only until delivered and acknowledged.
- **missing:** relay_event_push implementation for delivery acknowledgements; durable queue/scheduler for retry on relay; device skill: offline voice note buffer and resend; receipt path that faculty-perception can read and faculty-action can act on

### "“Handle this across my devices: in the authenticated browser, find the latest order or booking matching what I said; on the Mac, add the verified details to the right app; then tell me exactly what changed.”"
- **useful because:** Today the browser and Mac can each act, but the owner cannot ask for one voice-directed workflow whose browser evidence is verified before a related Mac mutation. This would eliminate transcription mistakes and make the pendant genuinely useful while the owner is away from the desk.
- **path:** pendant → relay → browser → mac-planner → mac-terminal → dashboard
- **model tier:** Use relay-realtime only to clarify the utterance and give the short spoken result; use a cheaper background planner for cross-surface orchestration, with browser extraction and Mac execution as separate typed stages.
- **latency:** Acknowledge within 1 second; browser lookup and Mac update may take 10–60 seconds, with progress events and a final spoken receipt.
- **cost:** Roughly $0.01–$0.08 per workflow depending on browser pages and planner turns; browser and Mac execution dominate latency, not the realtime response.
- **security:** Authenticated page contents and the selected Mac app data leave their respective devices only as narrowly scoped evidence. The system must bind every Mac mutation to cited browser fields, show the planned field mapping in the pendant response/dashboard, and retain an auditable cross-surface receipt; destructive or externally consequential mutations should be explicitly called out before execution.
- **missing:** A cross-surface workflow runner with a durable correlation id and typed evidence references; A browser extraction result that can be consumed by the Mac planner without copying whole pages; A dependency/consistency check that refuses to mutate when required evidence is missing or changed; One unified receipt joining browser observations, Mac actions, and the spoken outcome; Reconnectable progress delivery to the pendant when either downstream surface is temporarily offline

### "“Remember that ‘work inbox’ means the currently authenticated Outlook tab in my browser plus the Outlook app on my Mac; whenever I say it, use whichever surface is reachable and tell me which one you used.”"
- **useful because:** The owner should not have to name apps, tabs, URLs, or accounts while speaking to a pendant. A durable, owner-controlled alias would let one utterance resolve to the right authenticated browser session or Mac app, while making fallback explicit instead of guessing.
- **path:** pendant → relay → browser → mac-planner → dashboard
- **model tier:** Use realtime only for extracting the alias request and resolving an unambiguous reference; store and match aliases with a cheap deterministic resolver, escalating to a background model only when multiple live targets conflict.
- **latency:** Alias lookup under 200 ms; target availability checks under 2 seconds; ask a short clarification only on a genuine conflict.
- **cost:** Usually below $0.001 per lookup after setup; occasional model-assisted alias creation or conflict resolution costs a few cents.
- **security:** Aliases can point at sensitive authenticated accounts. Store target ids and redacted labels rather than credentials or page contents; bind aliases to the owner/session, expose a spoken “I used browser tab X” trace, and provide immediate forget/replace behavior.
- **missing:** An owner-scoped target registry spanning browser sessions and Mac app identities; A deterministic resolver with availability, freshness, and account-bound matching; A compact voice/dashboard flow to create, inspect, disambiguate, and forget aliases; Adapters that turn a resolved alias into the existing browser and Mac tool inputs


## Changes it proposed to its own stack

### `relay` — Publish a relay-side capabilities endpoint (e.g., GET /capabilities) and a durable intent/job ledger for the relay surface, mirroring what the Mac agent exposes. Include tool availability (implemented vs schema-only), route inventory, and a job/status log that downstream and faculty agents can read.
- **owner gets:** It reduces silent failures and confusion. When the owner asks “did that work?” the system can answer reliably, even if the Mac is asleep, and developers can see what the relay can actually do without guessing.
- effort: Medium. Add a small router module and persistence via Durable Object or KV; write adapters to record tool calls and job receipts.  ·  risk: Low. Main risk is leaking sensitive metadata in logs; mitigate with redaction and access control.
- cost: Low ongoing cost; storage for compact job records. Occasional writes per routed intent.  ·  latency: Minimal; reads should be fast and local to the worker.
- security: Positive if done right: better auditability. Needs strict scoping so only authorized agents read logs.

### `integration` — Add a durable cross-surface evidence-and-commit protocol: every browser observation is emitted as a small signed typed fact (source session/tab, timestamp, selector or page reference, value hash, freshness), and every dependent Mac action must reference the fact ids it consumed. The relay creates one workflow id, streams stage progress, and writes a single joined receipt; if a fact expires or differs at commit time, the workflow reports a checkpoint instead of applying a stale mutation. This is orchestration and data binding between existing routes, not another action broker or approval gate.
- **owner gets:** The owner can safely say one sentence such as “look up my latest booking and put it in Calendar” without manually relaying details between the browser and Mac, while retaining an understandable explanation of exactly which browser facts caused which Mac changes.
- effort: Medium-high: define schemas, persistence and freshness rules; adapt browser extraction, planner inputs, Mac action receipts, relay progress events, and dashboard rendering; add crash/reconnect tests across both downstream agents.  ·  risk: A partial failure could leave the Mac change applied while the browser workflow is incomplete. Recovery is an idempotency key plus compensating action metadata and a clear “applied/unknown/not applied” state; never silently retry a non-idempotent Mac mutation.
- cost: Negligible storage and Worker CPU; one additional cheap planner/evidence-normalization turn per workflow, with no extra realtime-model call unless the owner asks a follow-up.  ·  latency: Adds roughly 0.5–2 seconds for evidence normalization and receipt persistence; downstream browser/Mac latency remains the dominant factor.
- security: Improves provenance and limits data transfer to selected typed facts, but introduces sensitive cross-device correlation records. Encrypt/expire evidence, scope facts to the workflow, and avoid retaining raw authenticated page content.
- depends on: A durable workflow record and reconnectable event stream on the relay; Typed browser extraction results with stable source references; Mac actions accepting idempotency keys and evidence references; A unified receipt schema across browser and Mac

### `memory` — Implement an owner-scoped live target registry and resolver between relay speech and existing browser/Mac tools. A registry entry stores an alias, surface, stable session/app identity, account label hash, last-seen time, and reachability—not credentials or page content. At invocation, resolve by exact owner alias plus current reachability/freshness; if more than one target survives, return a one-sentence clarification rather than silently selecting. Emit the resolved target id into the existing job and receipt records.
- **owner gets:** The owner can speak naturally from anywhere (“check work inbox” or “put that in calendar”) and receive an honest indication of which authenticated surface was used, without repeatedly navigating or exposing account details aloud.
- effort: Medium: registry schema and CRUD, browser-session and Mac-status adapters, resolver tests for stale/duplicate targets, and small pendant/dashboard create-forget-confirm flows.  ·  risk: A stale alias could direct work to the wrong account or app. Mitigate with freshness and account-label matching, explicit conflict responses, reversible alias deletion, and recording the target in receipts for recovery.
- cost: Low storage/CPU and no recurring model cost for exact matches; occasional clarification adds one realtime turn.  ·  latency: Typically tens of milliseconds for lookup plus existing reachability checks; conflict handling adds one conversational turn.
- security: Reduces accidental broad context transfer, but creates metadata linking aliases to accounts. Encrypt or hash account labels, limit registry visibility to the owner, and expire unreachable browser targets unless pinned by the owner.
- depends on: A durable owner/session identity on the relay; A stable browser session/tab identity exposed by browser sessions; Mac app identity and reachability in get_mac_status; Receipt/job records accepting resolved target ids


## What it asked for

_Nothing._
## Its own summary

Recorded three non-duplicate proposals: (1) cross-surface evidence-bound workflows that verify authenticated browser facts before Mac mutations, (2) the durable evidence/commit protocol and unified receipt needed to make that safe across reconnects, and (3) owner-defined aliases such as “work inbox,” backed by a live cross-surface target registry and deterministic resolver. The owner cannot have these today because existing browser/Mac primitives are not joined by durable typed evidence, target identity, or commit lineage.

**Biggest unknown:** Whether the existing job and browser-session persistence can be extended without schema migration; no further discovery was performed as instructed.

