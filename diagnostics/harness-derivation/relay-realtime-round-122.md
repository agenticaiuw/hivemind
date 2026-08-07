# Harness derivation — relay-realtime — round 122

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If my pendant connection drops or I walk away mid-request, let me say “resume” later and have you restore the exact unfinished conversation, evidence, and next safe step—without repeating work or losing which Mac/browser task it belongs to."
- **useful because:** Today a voice interaction can strand the owner between speech, relay, Mac planning, and authenticated browser work. Durable, recoverable checkpoints would make the hive feel like one continuous assistant even across LTE gaps, sleep, and delayed Mac jobs, while preventing duplicate actions.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Realtime handles only the short spoken resume/clarification turn; a cheaper background worker compacts the checkpoint and reconciles job receipts.
- **latency:** Resume acknowledgement under 500 ms from relay-local state; evidence reconciliation within 3 seconds; no duplicate downstream execution.
- **cost:** Low per invocation: mostly Durable Object/storage reads and compact summaries; occasional background model call (roughly $0.01–$0.05) only when rebuilding a long checkpoint.
- **security:** Checkpoint data may contain authenticated-page excerpts, voice transcript, and action details. Encrypt at rest, scope by owner/session, expire raw page content, and speak only a minimal summary until the owner explicitly asks for sensitive details. Reconciliation must use idempotency keys and receipts, never replay an uncertain mutation.
- **missing:** A relay-side durable conversation-checkpoint schema containing utterance, normalized intent, evidence references, downstream job IDs, and resumable state; Exactly-once/idempotent correlation propagated from relay through /plan or Mac delegation into /execute and browser command queues; A reconnect/resume event on the pendant protocol and a compaction worker or Durable Object alarm; A spoken checkpoint/recovery response that distinguishes completed, still-running, failed, and unknown actions

### "Let me refer to things naturally—“send that one,” “close the tab I was looking at,” or “tell her the number from this screen”—and have the pendant resolve “that/this/her” across my latest Mac window, authenticated browser tab, and conversation before acting."
- **useful because:** A worn voice interface has no pointer or display. Without cross-surface reference grounding, the owner must repeat URLs, names, and exact text, which defeats hands-free use and makes short commands unsafe or frustrating. This would make the pendant usable while walking away from the computer.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime performs lightweight reference resolution and asks one short spoken disambiguation only when confidence is low; background models build and index richer Mac/browser observations.
- **latency:** Resolve from recent state in under 700 ms and speak a clarification in under 1.5 s; never block a simple, high-confidence read request on a background scan.
- **cost:** Usually near-zero beyond storage/lookups; use a small model only for ambiguous candidate ranking (about $0.005–$0.02), with expensive vision invoked only when the reference points to an image or screen region.
- **security:** The resolver must not leak page text or private contact data into unrelated sessions. Keep candidate evidence owner-scoped, redact spoken output by default, retain short-lived references, and require an explicit clarification when two candidates could cause different mutations. Logging should record which candidate and evidence won.
- **missing:** A shared, time-windowed entity/reference index spanning transcript, active Mac window, browser tab/session, and action receipts; Typed candidate objects with stable opaque IDs, source surface, timestamp, confidence, and human-readable spoken labels; Mac-vision and browser-extension observation snapshots exposed to relay with session affinity; A relay policy that converts pronouns/deictic phrases into explicit downstream arguments and emits an auditable resolution receipt


## Changes it proposed to its own stack

### `relay` — Add a relay-side capability inventory endpoint and a typed intent routing endpoint. The inventory should list the relay’s own routes/tools (including granted schemas) so the realtime agent can see what it can do without guessing. The typed intent endpoint should accept an intent label, normalized utterance, and target, and then forward to mac-planner or browser harness using existing routing contracts, returning a job reference for later status checks.
- **owner gets:** The pendant can respond faster and more reliably. Today the relay is the front door but cannot reliably introspect its own surface, so it repeatedly re-discovers missing pieces and can’t confidently route multi-step tasks. An explicit inventory and intent routing path reduces misroutes and repeated questions, and makes status follow-ups consistent.
- effort: Medium. Requires adding relay routes, wiring to existing router, and aligning with existing job/receipt structures. No UI.  ·  risk: Routing bugs could send tasks to the wrong surface. Mitigate with strict schema validation, logging, and a safe fallback to mac_delegate for ambiguous intents. Add receipts for traceability.
- cost: Low per-call (one Worker request plus small D1 write for job record). Main cost is engineering time; runtime cost dominated by downstream agent work.  ·  latency: Improves average latency by reducing back-and-forth and retries. Adds a small validation overhead per intent.
- security: Introduces a new entry point; must require auth, validate input, and avoid leaking transcript content. Only emit minimal job metadata. Ensure no arbitrary tool invocation is possible.
- depends on: Implement relay_route_intent as a real tool or route, not just a schema; align with existing job/receipt tables.


## What it asked for

_Nothing._
