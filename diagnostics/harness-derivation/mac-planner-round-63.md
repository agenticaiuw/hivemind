# Harness derivation — mac-planner — round 63

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-planner execution readiness** — Live /ops/status shows fullControlMode=true and relay reachable, but Mac agent ready=false because Accessibility trusted=false and Screen Recording granted=false; browser extension is offline with 3 pending commands. mac_readonly_inspect is granted in schema but currently returns 'no implementation yet'.
  - evidence: GET /ops/status HTTP 200 at 2026-08-07 round 63; three mac_readonly_inspect calls returned implementation error.

## Capabilities it proposed

### "“If my Mac or browser drops out, keep this task alive and let me resume it from the pendant later—tell me what is ready, let me continue with one button, and finish it when the Mac comes back.”"
- **useful because:** Today a long task can strand its state when the Mac is asleep, accessibility is unavailable, or the browser extension is offline. A compact, signed action capsule would let the relay preserve the plan and evidence, the pendant announce the exact resume point, and the Mac/browser complete it after reconnection. This gives the owner continuity no single surface can provide without requiring an always-open Mac session.
- **path:** mac-planner reads Calendar/Mail and prepares the bounded plan/evidence capsule → browser-extension contributes authenticated tab evidence and pending form state when online → relay-realtime stores the encrypted capsule, retries delivery, and emits a short spoken status → pendant presents a compressed spoken summary and uses its physical button as resume/skip → mac-planner rehydrates the capsule, executes the remaining typed actions, and returns a receipt to relay and pendant
- **model tier:** Use a cheaper background text model to summarize and compress the capsule; use realtime only for the live spoken resume interaction. No model is needed for retry, hashing, or state transitions.
- **latency:** Initial capsule under 3 seconds after the source reads complete; pendant status under 500 ms from relay delivery; completion is asynchronous and may wait for Mac/browser reconnection. Retry with exponential backoff rather than burning realtime tokens.
- **cost:** Roughly $0.01–$0.05 per task for background summarization and optional TTS; durable relay storage and retries dominate operational cost, not inference.
- **security:** Capsules may contain private mail/calendar snippets, URLs, and authenticated-page evidence. Store only redacted excerpts plus references, encrypt at rest/in transit, bind each capsule to the paired pendant and Mac, expire it by TTL, and include a hash in the receipt. The button should be an optional explicit resume control for actions the owner has not pre-authorized; never transmit cookies or credentials through the relay.
- **missing:** Durable cross-surface action-capsule schema with versioning, TTL, and idempotency key; Relay delivery and retry channel to the pendant, including offline acknowledgement state; Mac/browser rehydration endpoint that can distinguish stale evidence from executable remaining steps; A pendant button/status skill for announcing and resuming a capsule; Capability-aware fallback when Accessibility or browser connectivity is missing

### "“Compare my private mail, calendar, and logged-in pages, but keep the underlying personal data on my devices—tell me the answer and exactly which local sources support it.”"
- **useful because:** The owner cannot safely use the whole hive for sensitive cross-source questions today: authenticated page contents, mail, and calendar would be assembled across surfaces without a guaranteed raw-data boundary. This capability would let the relay coordinate the work while the Mac/browser retain the sensitive text, returning only redacted claims, confidence, and source hashes. It is useful for questions such as conflicting appointment details, account changes, or whether an email matches a logged-in portal notice.
- **path:** mac-planner reads bounded Calendar/Mail sources and computes local structured claims → browser-extension extracts only the requested fields from authenticated tabs and keeps page text local → faculty-perception produces source-labelled claims and hashes on the Mac → faculty-judgement reconciles conflicts and returns a minimal answer plus confidence → relay-realtime routes the query and receives only the redacted claim bundle → pendant speaks the answer and can ask the owner whether to reveal a specific source excerpt
- **model tier:** Use a cheaper background model for local extraction, normalization, and conflict comparison; use realtime only if the owner asks follow-up questions aloud. The relay should not need an LLM for raw private content.
- **latency:** Local source collection and comparison within 5 seconds for up to 10 sources; spoken response under 1 second after the claim bundle arrives. A source-specific reveal may take another 2–3 seconds.
- **cost:** About $0.005–$0.03 per query if local extraction uses a small model; relay bandwidth and local inference dominate. Realtime cost is limited to follow-ups.
- **security:** Raw mail bodies, calendar details, cookies, and page text must never enter relay logs, prompts, or durable queues. Use an explicit field allowlist, local redaction, per-claim provenance hashes, short-lived encrypted source handles, and separate consent for revealing excerpts over audio. Hashes are for audit, not substitutes for access control.
- **missing:** A local privacy boundary that enforces field-level extraction before relay transmission; Typed claim and provenance schema supporting disagreement, freshness, and source hashes; Browser extraction that returns allowlisted fields without exporting raw DOM or cookies; Local model execution or a trusted Mac-side inference endpoint; Relay log and telemetry redaction for claim payloads; Pendant interaction for requesting one narrowly scoped source excerpt


## Changes it proposed to its own stack

### `integration` — Add a cross-surface Action Capsule protocol. Each long-running plan becomes an append-only record containing capsuleId, owner/paired-device binding, ordered steps, required surface, redacted evidence references, preconditions, idempotency keys, expiry, and a monotonic checkpoint. The relay persists and retries it; Mac-planner and browser-extension claim only steps matching their current connectivity/permissions, report structured receipts, and atomically advance the checkpoint. The pendant receives only a compact spoken summary plus capsule status and can request resume/skip; stale browser evidence forces a fresh read rather than replaying a mutation.
- **owner gets:** A task can survive a sleeping Mac, a dropped browser extension, or a temporary missing permission instead of silently failing or starting over. The owner can leave home with the pendant and return to a finished, auditable result, while each surface does only the work it is physically capable of.
- effort: Medium-large: shared schema/state machine in relay and Mac agent, reconnect and idempotency tests, browser checkpoint adapter, pendant status/resume firmware skill, and receipt rendering. Start read-only and reversible workflows before mutations.  ·  risk: Duplicate or stale mutations are the primary risk. Mitigate with idempotency keys, precondition hashes, lease expiry, explicit stale-evidence states, and existing job receipts/undo where available. If a surface disappears, leave the capsule paused and report the exact checkpoint; never guess completion.
- cost: Low recurring API cost because retries and state transitions are deterministic; background summarization/TTS is roughly cents per capsule. Relay D1/R2 storage is small if evidence is referenced by hash and expires.  ·  latency: No impact on normal instant commands. Reconnect adds one state sync round trip (typically sub-second on LAN); long tasks remain asynchronous.
- security: Private source snippets must be minimized and encrypted; capsule access requires the paired-device identity. URLs and DOM evidence need TTLs. Do not place cookies, tokens, or raw mail bodies in relay payloads; receipts should expose hashes and redacted summaries.
- depends on: A versioned relay persistence schema and idempotent job runner; A pendant offline/status-and-resume device skill; Browser session/tab affinity and stale-evidence detection; Mac capability/permission preflight reported as machine-readable step blockers


## What it asked for

_Nothing._
