# Harness derivation — relay-realtime — round 21

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Every morning, give me a 30-second audio digest of what changed: calendar, reminders, and top emails.”"
- **useful because:** It turns the pendant into a daily briefing you can listen to while walking, without pulling out a phone or opening a laptop.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** Planner/summary runs on a cheaper background model via the Mac bridge or server-side browser for web sources; relay only delivers the audio and handles quick follow-ups.
- **latency:** Digest generation can take seconds to minutes; delivery should be instant when ready. The owner is not waiting in a live conversation.
- **cost:** Dominated by summarization tokens and any email/calendar access; delivery is cheap. Runs once per day.
- **security:** Requires access to mail and calendars. High-impact actions aren’t needed, but reading private data is sensitive—make sources explicit at setup, and provide a dashboard view of what was accessed.
- **missing:** A scheduler/routines system to run daily; An audio rendering pipeline that can package a digest for playback; Connectors for mail/calendar if not already available via the Mac bridge; A job status/listing UI so the owner can see and manage scheduled digests


## Changes it proposed to its own stack

### `routines` — Add a real scheduler: a Durable Object-backed job queue with delayed execution and recurring rules (cron-like). The relay can enqueue jobs, and a workers cron/alarm runner executes them, delegating to mac_delegate or server_browser_actions as needed. Include idempotency keys, retry with backoff, and cancellation.
- **owner gets:** They can say things like “Remind me tonight” or “Check for new messages every morning and summarize” and it actually happens without them keeping a Mac awake or staying online.
- effort: Medium to high: new Durable Object, queue schema, runner, and integration with existing job status/result reporting.  ·  risk: Jobs could run unexpectedly if time zone or recurrence rules are wrong; mitigate with clear job listings, pause/disable, and a dry-run mode. If a job fails repeatedly, quarantine it and notify the owner when they next connect.
- cost: Adds storage and compute cost for queued jobs and periodic runs; cheaper than keeping realtime model sessions open. Most cost is in downstream model invocations when jobs execute.  ·  latency: No impact on conversational latency; jobs run out of band.
- security: Scheduled tasks can read data or take actions without the owner present. Require explicit confirmation for high-impact actions at scheduling time, and show what data sources will be accessed.
- depends on: A status endpoint or tool to list scheduled jobs and results (for transparency)

### `memory` — Unify memory across surfaces: replace hand-written prompt sections per surface with a shared, versioned memory API that returns small, purpose-built summaries (profile, preferences, current projects, recent tasks) plus a citation trail. Add write paths with confidence and decay/TTL to prevent prompt bloat.
- **owner gets:** Tell the system something once, and every agent uses the same up-to-date understanding without growing context cost every turn.
- effort: Medium: define schemas, summaries, and citations; update each surface to fetch memory via the API; add pruning and summarization workers.  ·  risk: Bad memory writes could lock in wrong facts. Mitigate with confidence scores, recency bias, and user-visible correction commands.
- cost: Reduces per-turn token cost by keeping prompts small; adds occasional background summarization cost.  ·  latency: Small additional fetch latency on first use; cache summaries per session.
- security: Central memory is sensitive. Encrypt at rest, audit writes, and separate private vs shareable facts.

### `integration` — Wire up a server-side browser path using Cloudflare Browser Run and a routing rule: web reads/extraction default to server_browser_actions; only fall back to Mac browser bridge when authentication requires the owner’s existing Mac session.
- **owner gets:** Web tasks work even when the Mac is asleep, and they start faster because they don’t need to wake another machine.
- effort: Medium: implement routing, translate existing browser_run_actions to server_browser_actions, normalize results.  ·  risk: Server-side browsing may not share the owner’s authenticated sessions; tasks could fail silently. Detect auth walls and automatically escalate to the Mac path with a clear reason.
- cost: Adds server browser runtime cost; likely less than launching and coordinating Mac-side browser automation for simple reads.  ·  latency: Lower startup latency for many web reads; no impact on voice latency.
- security: Server-side browsing touches third-party sites; restrict to allowed domains where possible and log what was accessed for transparency.
- depends on: Clear contract for extracted data format shared by both browser paths


## What it asked for

_Nothing._
## Its own summary

Discovered the stack-level reality: the relay still has only five production tools, the Mac harness polls for work, and the whole system is a prototype with shared dashboard clients. Proposed three high-value additions: a real scheduler/recurring job mechanism, a unified memory API with summaries/citations to reduce prompt cost, and a daily audio digest capability. Also proposed wiring a server-side browser route to reduce dependence on the Mac for web reads.

**Biggest unknown:** Authentication and data-source constraints for mail/calendar, and which audio playback/voice UI exists on the pendant for queued digests (speaker, bone conduction, or phone handoff).

