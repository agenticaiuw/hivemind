# Harness derivation — relay-realtime — round 22

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### ""Queue this up and tell me when it’s done" (for example: summarize a long document, compare options, draft an email, or research a topic)."
- **useful because:** It turns the pendant into a true front door: the owner can speak a task once, then go about their day while the system finishes it in the background and delivers a concise result when ready.
- **path:** relay: capture the request quickly and confirm it was queued → mac-bridge: plan and execute multi-step tasks when the Mac is available → relay/server: use server-side browser or public web readers when the Mac is offline or unnecessary → dashboard/iOS/menubar: show job status and receipts, and let the owner replay results
- **model tier:** Realtime for capturing intent and immediate confirmation; cheaper planner/executor on Mac or server for the actual work; no long-running work on the realtime tier.
- **latency:** Under ~1 second to acknowledge and queue; seconds to minutes for execution depending on task; results arrive asynchronously.
- **cost:** Low realtime cost per request (short acknowledgement). Main cost is downstream planning/execution tokens plus any browser automation; cheaper than keeping the realtime model engaged while work runs.
- **security:** Background jobs can read sensitive data or take actions. Provide a clear receipt showing what was read/changed. Require explicit confirmation for irreversible or high-impact actions (e.g., sending email, purchases).
- **missing:** A real scheduler/queue in the relay (Durable Object or D1-backed) with alarms for retries; A stable enqueue/status/receipt API between relay and Mac; Result delivery mechanism to the relay (webhook/polling); Server-side browser integration as a fallback path; UI for job status and receipts across surfaces


## Changes it proposed to its own stack

### `routines` — Add a relay-owned durable work queue with retries and a receipt log, implemented as a Durable Object (or D1 + Durable Object alarms). The relay exposes enqueue/status endpoints, persists intent payloads, and emits receipts when downstream nodes complete. Jobs can be routed to Mac or server browser based on availability and task type.
- **owner gets:** The owner can hand off tasks by voice and trust they will finish even if they walk away, the network drops, or the Mac goes offline. They get a clear record of what happened.
- effort: Medium to high: queue design, idempotency keys, retries, backoff, receipt schema, and UI changes.  ·  risk: Queue bugs could duplicate work or lose jobs. Mitigate with idempotency keys, explicit job states, and receipts. Provide manual cancel/retry controls.
- cost: Moderate: storage in D1, occasional Durable Object alarms; cheaper than keeping realtime sessions open.  ·  latency: Improves perceived latency: quick acknowledgement, work happens asynchronously.
- security: Must authenticate enqueue calls and protect stored payloads. Receipts should avoid logging sensitive content; store references when possible.
- depends on: A receipt schema shared across relay and Mac harness; Status reporting from Mac harness back to relay

### `integration` — Use the new server-side browser capability for public web tasks directly from the relay, reserving the Mac harness for authenticated sessions and local data. Add routing logic: public pages -> server browser; authenticated workflows -> Mac browser bridge.
- **owner gets:** Faster results when the Mac is away, and fewer points of failure. The pendant can answer more questions without depending on the laptop being online.
- effort: Medium: implement server browser actions, extraction patterns, and routing heuristics.  ·  risk: Automation could break on site changes; implement robust extraction and fallback to web_search/read_web_page.
- cost: Moderate: browser automation is more expensive than a simple search, but avoids Mac dependency and can reduce retries.  ·  latency: Often faster than waiting for the Mac to come online, but slower than simple search; choose accordingly.
- security: Keep it to public web unless explicit authentication support is added. Avoid storing scraped personal data unnecessarily.

### `memory` — Introduce a unified, cross-node memory write API with schema (entities, events, preferences, tasks) and TTLs, plus a pruning policy. Replace hand-written per-surface prompt sections with retrieval-based context assembly.
- **owner gets:** Tell the system something once and every node knows it. Less repetition, better continuity, and lower token costs over time.
- effort: High: schema design, migrations, retrieval, and updates to all surfaces.  ·  risk: Bad memory writes could propagate errors. Mitigate with confidence scoring, source attribution, and easy correction commands.
- cost: Reduces prompt bloat and repeated context over time; storage costs increase modestly.  ·  latency: Small overhead for retrieval; overall faster than shipping large prompts every turn.
- security: Memory can contain sensitive data; enforce access control per node and encrypt at rest where possible.


## What it asked for

_Nothing._
## Its own summary

Confirmed the current stack and tools, including new relay-side tools (intent routing, server browser, job status). Proposed a background job capability and concrete changes: a durable queue/receipt system, public-web routing via server browser, and a unified memory API to reduce cost and improve continuity. Also messaged mac-planner with relay needs for queue/receipt contracts.

**Biggest unknown:** There is still no wired scheduler/queue or receipt contract. I need a concrete enqueue/status/receipt API and, ideally, a shared schema for job payloads and results so the relay can acknowledge, track, and deliver outcomes safely.

