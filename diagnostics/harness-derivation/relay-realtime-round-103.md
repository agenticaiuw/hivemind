# Harness derivation — relay-realtime — round 103

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Keep an eye on this long-running task across my devices. If it stalls, tell me what is blocked; if it finishes, give me the result; and if I say ‘stop that’ or ‘continue’, apply the change to the exact task I mean.”"
- **useful because:** Today a spoken request can be handed off or a job can be queried, but the owner cannot have one durable, voice-addressable task identity that follows a Mac/browser/relay workflow, detects stalls, reports meaningful milestones, and accepts unambiguous pause/resume/cancel commands while they are away from the Mac. This would make delegation feel like an ongoing assistant relationship rather than a fire-and-forget command.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime relay only handles intent resolution and concise spoken updates; mac-planner and mac-vision do execution and checkpoint interpretation; a cheaper background model classifies milestone/stall events and drafts the update; dashboard renders the task timeline.
- **latency:** Acknowledge or resolve a control command in under 2 seconds; milestone notifications within 10 seconds of an observed event; no low-latency model call for quiet polling intervals.
- **cost:** Roughly $0.01–$0.08 per active task per day depending on event frequency; the dominant cost is background summarization of checkpoint deltas, not the brief relay utterances.
- **security:** Task state may include authenticated page text, local files, or sensitive spoken constraints. Keep raw evidence on the owning surface where possible, send the relay only typed checkpoint summaries, encrypt task records, expire extracts, and never speak sensitive page contents aloud unless the owner explicitly asks. Control commands must target an exact task id resolved from recent spoken context, with a concise disambiguation when there are multiple matches.
- **missing:** A durable cross-surface task record with stable task id, owner/session binding, checkpoints, heartbeat, and expiry; A push event stream from Mac planner/vision and browser extension to the relay for progress, stall, and completion events; Idempotent pause/resume/cancel controls accepted by every executor, plus recovery after executor disconnects; A relay-side active-task resolver that maps phrases like “that task” to recent spoken context without guessing across concurrent tasks; Pendant notification policy and dashboard timeline for milestone/stall updates

### "“For the next hour, let this one task use my open work tabs and the files in my project folder, but do not retain or reuse anything it reads after the task ends.”"
- **useful because:** The owner currently has to choose between broad trusted access and manually policing what a delegated workflow can retain. A spoken, time-bounded context lease would let the pendant grant exactly the browser tabs and Mac scope needed for one job, then automatically revoke access and erase transient extracts, even if the owner is away.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime relay parses the lease request and speaks its compact scope; deterministic policy code enforces expiry and resource bindings; Mac/browser agents use a cheaper model for extraction and task work. No expensive model is needed to decide whether a lease is still valid.
- **latency:** Lease acknowledgement under 1 second; every resource request checked locally at sub-100 ms; revocation propagated to Mac and browser within 2 seconds.
- **cost:** Negligible inference cost after initial parsing (well under $0.01 per lease); engineering/storage costs dominate. Optional audit summarization is a small background-model charge.
- **security:** The lease itself must be authenticated to the owner's device and bound to a task, session, tab ids, file roots, purpose, and expiry. Never transmit raw credentials or cookies to the relay. Browser and Mac adapters must enforce deny-by-default outside the lease, redact evidence before relay storage, erase temporary content at expiry, and show an audit entry. Revocation must win over in-flight reads where feasible.
- **missing:** A signed lease token format and verifier shared by relay, Mac agent, and browser extension; Resource-level enforcement in the Mac and browser harnesses (tab ids, URL origins, file roots, and operation types), rather than only job-level authorization; A relay revocation/expiry service that survives Worker instance turnover and notifies connected executors; Secure erase/retention metadata for job evidence, logs, receipts, and model context; Pendant utterance support for grant, narrow, extend, revoke, and inspect-current-scope, plus dashboard visualization

### "“Why did you do that, and what exactly did you use to decide?”"
- **useful because:** The owner cannot currently receive a spoken, causal explanation that connects their original utterance to the planner decision, browser/Mac evidence, and the concrete action receipt. A provenance view would make autonomous cross-device behavior debuggable while the owner is away, without requiring them to inspect raw logs or remember which tab was involved.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Deterministic provenance assembly joins event and receipt records; a cheap background model compresses the chain into a short explanation; realtime is used only to answer the owner's immediate follow-up and should not re-plan the action.
- **latency:** Return a first spoken explanation in under 3 seconds from stored records; deeper evidence links can load asynchronously in the dashboard.
- **cost:** Under $0.01 per explanation when records are structured; storage/indexing and redaction dominate rather than model tokens.
- **security:** Evidence may contain private page text, filenames, or message content. Store hashes and typed references by default, retain raw snippets only under an explicit retention policy, redact secrets before indexing, and distinguish observed facts from model inferences. The explanation must never claim an agent observed evidence that it did not record.
- **missing:** A tamper-evident causal event schema linking utterance, intent, plan revision, evidence reference, action, result, and receipt; Cross-surface correlation IDs propagated through relay, Mac planner/vision, browser extension, and job records; A provenance query endpoint with redaction and owner-facing spoken-summary mode; A model-independent formatter that can say “unknown” when a link in the chain is absent; Dashboard and pendant controls for opening the cited evidence or deleting the provenance record


## Changes it proposed to its own stack

### `browser-harness` — Implement the granted server_browser_actions schema using Cloudflare Browser Run as a fallback/alternative to the Mac browser extension. Provide a durable command queue, request ids, idempotency keys, typed results (page metadata, extracted text, screenshots), and explicit irreversible-action checkpoints. Allow public web reads when the Mac is offline; route authenticated/private pages only via the Mac Safari bridge.
- **owner gets:** The owner can ask for quick web checks while away from the Mac. Public tasks can run without waking the Mac, and private tasks remain protected, making the system more responsive and reliable.
- effort: High: requires browser runner integration, durable queue storage, result streaming, and careful separation of public vs authenticated contexts.  ·  risk: Unexpected site behavior, bot detection, and accidental irreversible actions. Mitigate with read-first default, typed actions, irreversible checkpoints, and clear receipts.
- cost: Moderate per run; dominated by browser runtime time. Durable storage costs for command/result logs.  ·  latency: Faster for simple public lookups; less waiting on Mac availability.
- security: Strong boundary: never mix authenticated browsing into server-runner. Strict allowlist for actions; redact extracted secrets; store minimal artifacts.

### `relay` — Add a versioned, authenticated relay capability manifest and self-test endpoint generated from the Worker router, including live route schemas, supported event types, delivery guarantees, and explicit unavailable features. Have the pendant and dashboard cache the manifest with a version/hash, and run a contract test on deployment that exercises health, voice ingress, job handoff, and event delivery. Do not expose secrets or bearer material.
- **owner gets:** The owner should not be told that a voice command, status update, or handoff is supported when the relay silently lacks that route, nor should a dropped deployment make the pendant appear unresponsive. The pendant can give an honest immediate answer and the dashboard can show exactly what the system can do right now.
- effort: Medium: router introspection, schema sanitization, signed manifest caching, deployment contract tests, and a small firmware/dashboard display path.  ·  risk: A stale manifest could misdescribe behavior; bind it to a deployment version and fail closed to “capability unknown.” An accidentally exposed schema could reveal internals; strip implementation details and secrets. Recovery is to invalidate the manifest and fall back to the minimal built-in health/voice contract.
- cost: Near-zero API cost; one small manifest read per deployment/session. A few KB of Worker response and modest dashboard storage.  ·  latency: No added latency on normal voice turns; manifest refresh is asynchronous. Self-tests add deployment time only.
- security: Improves security by reducing undocumented attack surface and allowing clients to verify they are speaking to the expected relay version; endpoint must require the existing bearer/authentication and omit credentials, raw route internals, and user data.
- depends on: A sanitized schema registry in the relay router; A deployment identifier/signature and cache invalidation path; A minimal pendant/dashboard consumer for capability version and health state


## What it asked for

_Nothing._
## Its own summary

Recorded four new items: a durable voice-addressable task control plane with stall/milestone handling; time-bounded cross-device context leases; causal provenance explanations; and a signed relay capability manifest/self-test contract. The owner still cannot have these today because the missing pieces are durable cross-surface event correlation, executor pause/resume/revoke primitives, resource-level scope enforcement, retention/redaction, provenance links, and relay router introspection/contract tests.

**Biggest unknown:** Whether any existing backlog item already implements part of the newly proposed relay manifest or provenance work; discovery was explicitly unavailable this round, so I did not re-check.

