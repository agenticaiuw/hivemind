# Harness derivation — relay-realtime — round 20

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Give me a quick overnight briefing.”"
- **useful because:** The owner wakes up to a concise, trustworthy summary of what happened while they slept: tasks completed, things that failed, messages worth attention, and any follow-up already queued. It turns the system into a dependable teammate instead of a chat window.
- **path:** relay → mac-bridge → dashboard
- **model tier:** Background planning and summarization should run on the Mac planner (cheaper, not latency-critical). The relay only plays back the result when asked, keeping realtime usage minimal.
- **latency:** Owner is not waiting for the work to happen; it should complete in the background and be ready instantly when requested. Playback should be near-instant.
- **cost:** Low per day if summarized once into a small artifact. Biggest cost is any email/calendar/file reads and summarization tokens on the planner tier; relay cost is just a short spoken reply.
- **security:** Summaries include sensitive data. The ledger must track provenance and avoid leaking content across contexts. Any action to fix something (e.g., send a message, move money, change files) must require explicit confirmation.
- **missing:** A scheduler/worker to run the briefing job daily (Cloudflare Cron or Durable Object alarms wired into the bridge); Event-sourced ledger and receipts wired end-to-end so the summary is based on auditable events; A stored ‘briefing artifact’ the relay can fetch quickly without recomputing; Permissioned readers for mail/calendar/files (or a defined scope)


## Changes it proposed to its own stack

### `routines` — Add a scheduling layer using Cloudflare Cron Triggers (for daily/weekly routines) and Durable Object alarms (for per-user delayed tasks and retries). Jobs emit ledger events and produce artifacts (e.g., briefing summaries) stored in D1/R2 with ids and provenance.
- **owner gets:** The system can do useful work while the owner sleeps or is away, and the result is ready when they ask — without burning realtime tokens or requiring the Mac to be awake at that moment.
- effort: Medium to high. Requires wiring Cron/alarms, defining job schemas, idempotency keys, and artifact storage; plus observability for failures.  ·  risk: Jobs could run at the wrong time or duplicate. Mitigate with idempotency keys, explicit timezones, and a replay-safe event log. Provide a ‘disable routine’ control in the dashboard.
- cost: Adds cheap scheduled compute and storage reads/writes. Saves realtime cost by shifting work off the expensive tier.  ·  latency: Improves perceived latency because results are precomputed; adds background job latency but nobody is waiting.
- security: Scheduled jobs can touch sensitive data. Require scoped readers and audit logs; high-impact follow-up actions must still require explicit confirmation.
- depends on: Event-sourced ledger/receipt system already proposed by mac-planner to be implemented end-to-end

### `browser-harness` — Give the relay a server-side browsing path using Cloudflare Browser Run for public web tasks, with a policy to prefer server_browser_actions over routing through the Mac when the target is public and doesn’t require the user’s authenticated sessions.
- **owner gets:** Web lookups and extraction can happen even when the Mac is asleep or disconnected. The pendant becomes more reliable for quick questions and research on the go.
- effort: Medium. Needs action schema, extraction patterns, error handling, and a fallback to mac-planner/browser extension when authentication is required.  ·  risk: Automated browsing can click the wrong thing or misread content. Mitigate with read-only defaults, explicit extraction, and clear provenance in the returned artifact.
- cost: Adds server-side browser runtime cost; offsets by reducing mac round-trips and planner tokens for simple extraction tasks.  ·  latency: Often faster than waiting for the Mac; still not realtime, so relay should present as ‘working’ and return when done.
- security: Public browsing is lower risk, but still needs URL allow/deny policies and content sanitization. Never treat it as authenticated unless explicitly configured. 


## What it asked for

_Nothing._
