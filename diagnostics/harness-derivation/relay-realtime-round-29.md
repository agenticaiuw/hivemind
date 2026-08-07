# Harness derivation — relay-realtime — round 29

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Handle this later and keep working after I stop talking. Tell me when it’s done, and if you need my approval, ask at the right moment."
- **useful because:** The owner can start something from the pendant while away from the Mac, then trust the system to carry it through and report back without babysitting. It turns a quick voice command into a complete workflow with follow-through.
- **path:** relay → mac-bridge → browser → relay → pendant
- **model tier:** Realtime only for the initial clarification and confirmation; planning and execution run on a cheaper Mac-tier model; long waits and monitoring run in server-side background.
- **latency:** Under 1 second for acknowledgement; plan in a few seconds; execution may take minutes and should not block the conversation.
- **cost:** Low per invocation on the relay; cost dominated by Mac planning/execution and any browser automation time, plus occasional status checks.
- **security:** Needs careful handling of authenticated browser sessions and private files. Drafts and irreversible changes must be shown for approval before execution. Status updates should avoid leaking sensitive content over voice.
- **missing:** A real scheduler/background job runner (cron or alarms) to resume work later; Durable job receipts and a status lifecycle shared across relay and Mac; A notification path from background completion back to the relay/pendant; Typed context retrieval to avoid resending large context every turn

### "“Save this moment so I can pick it up when I’m back at my Mac,” and later, “Resume the thing I saved earlier.”"
- **useful because:** The pendant is worn while the owner is away from the Mac, so ideas, decisions, and interrupted work otherwise fall between devices. This would create a durable handoff capsule containing the spoken intent plus a snapshot of relevant Mac and authenticated-browser state, then restore that context and continue safely when the owner returns.
- **path:** pendant → relay → mac-bridge → browser → Mac planner → dashboard
- **model tier:** Realtime only extracts the short spoken request and gives immediate acknowledgement; a cheaper background model summarizes and ranks the capsule. Mac-planner gathers structured app/window/document state, while browser harness records page identity and resumable location without copying page secrets.
- **latency:** Acknowledge within 1 second. Capture should finish within 10 seconds when the Mac/browser are reachable; if they are not, retain the voice capsule and enrich it on the next explicit resume request. Resume should provide a spoken preview within 3 seconds before dispatching actions.
- **cost:** Roughly $0.01–$0.05 per save/resume, dominated by background summarization and any browser/page extraction; realtime cost is limited to the brief utterance and acknowledgement.
- **security:** The capsule may contain work titles, URLs, selected text, and application state. Keep it encrypted, owner-scoped, redact credentials and page contents by default, retain references rather than secrets, and make the resume preview audible before mutations. Do not silently send messages or alter work; reversible navigation/opening is fine under the owner's existing maximum-access policy.
- **missing:** A first-class durable context-capsule record with lifecycle, encryption, and redaction metadata; A Mac snapshot endpoint that reports focused app, windows, documents, selected task, and resumable action state without disturbing work; A browser-harness snapshot/resume interface for authenticated tabs that preserves session locality and never exports credentials; Relay orchestration to correlate pendant utterance, Mac snapshot, browser snapshot, and later resume; A spoken preview/receipt so the owner knows exactly which capsule is being resumed

### "“Work on this until it’s done, tell me what you find, and stop if I say cancel.” For example: research a purchase across authenticated and public sites, compare it, and prepare (but do not place) the order."
- **useful because:** Today a spoken request is effectively one handoff: the owner cannot stay in a live voice session while the Mac planner and browser encounter delays, ambiguity, login boundaries, or partial results. A voice-supervised expedition would let the owner be away from the Mac, receive concise progress on the pendant, answer clarification questions, redirect the goal, or cancel, while preserving the exact work state across Mac and browser.
- **path:** pendant → relay → mac-bridge → browser → Mac planner → dashboard
- **model tier:** Use the realtime model only for intent capture, concise progress phrasing, and interruption handling. Use gpt-5.6-luna or a cheaper background planner for decomposition and browser/Mac work; use the dashboard for a durable event log and receipts.
- **latency:** Immediate acknowledgement under 1 second; progress events within 5 seconds of meaningful state changes; clarification prompts should interrupt within 2 seconds and remain pending until answered. Final synthesis can take as long as the task requires.
- **cost:** About $0.03–$0.25 per expedition depending on planner turns and browser extraction; the dominant cost is repeated planning/context, so send incremental state diffs rather than the full transcript.
- **security:** Long-running authority can outlive the spoken turn and may encounter private sessions or consequential actions. Scope each expedition to an explicit goal, record every tool call, never submit purchases/messages or change data without an explicit in-session instruction, expire abandoned jobs, and provide a physical pendant cancel gesture that works even if the Mac link is down. Browser secrets stay in the browser harness.
- **missing:** A durable expedition state machine with pause, resume, redirect, cancel, timeout, and idempotent retry semantics; Server push from relay to pendant for progress and clarification, plus a local cancel path that survives a dropped link; Planner checkpoints and compact state-diff context so retries do not replay completed mutations; Browser and Mac adapters that emit structured progress, ambiguity, and completion receipts; A dashboard timeline showing the goal, current step, artifacts, and exact actions already taken


## Changes it proposed to its own stack

### `routines` — Add a scheduling layer that supports delayed and recurring jobs for both the relay (via Durable Object alarms/Cron Triggers) and the Mac agent (via a persistent queue), with a shared job schema and idempotency keys. Jobs should be resumable and report status back to the relay without requiring the Mac to stay online.
- **owner gets:** They can ask for something to happen later (or repeatedly) and trust it will actually occur, even if they walk away, lose connectivity, or the Mac sleeps.
- effort: Medium to high: requires new infrastructure wiring and a shared job contract.  ·  risk: Jobs may fire at the wrong time or duplicate. Mitigate with idempotency, clear logging, and safe defaults. Allow cancellation and pause.
- cost: Moderate: persistent storage for jobs and occasional background compute; relay cost remains low per request.  ·  latency: Improves perceived latency by decoupling long-running work from live conversation.
- security: Requires careful access control to ensure scheduled tasks can only act within the owner’s permissions and do not expose private data in logs.

### `context` — Introduce a typed context service that stores compact facts with provenance, sensitivity, TTL, and last-used timestamps, and delivers only task-relevant facts to each agent. Provide a small, stable schema and token budgeting per surface.
- **owner gets:** Conversations stay fast and accurate because agents stop re-sending and re-deriving the same context every turn, and they only see what they need.
- effort: Medium: new service plus migration of per-surface prompt context into structured retrieval.  ·  risk: Incorrect context scoping could hide necessary facts or leak sensitive ones. Mitigate with provenance, sensitivity tags, and conservative defaults.
- cost: Upfront build cost; reduces ongoing API cost by shrinking context payloads.  ·  latency: Reduces latency by minimizing prompt size and retrieval overhead.
- security: Improves privacy by limiting data exposure, but requires strict access controls and auditing.


## What it asked for

_Nothing._
