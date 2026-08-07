# Harness derivation — relay-realtime — round 16

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

- **Stack grounding for proposals** — The relay runs on a Cloudflare Worker with D1 and R2, and the realtime agent’s production routing contract is limited to five tools (get_mac_status, mac_run_actions, browser_run_actions, web_search, mac_delegate). There is no scheduler anywhere; delayed or recurring tasks cannot currently run.
  - evidence: get_hardware_spec(stack) returned relay environment and explicitly listed agent_tools_today as exactly five, and confirmed no scheduler exists across Worker or Mac agent.

## Capabilities it proposed

### "“When I get back to my desk, summarize what happened while I was away and queue anything urgent.”"
- **useful because:** The owner can wear the pendant and stay in the flow, then get a concise catch-up without manually checking email, tasks, and logs.
- **path:** relay: recognizes the request and hands it off → mac-bridge: mac_delegate plans and runs the catch-up using local data and browser where needed → browser: only if the plan needs web access (e.g., status pages) → relay: delivers a spoken summary back when the job completes, plus a dashboard entry if available
- **model tier:** mac-planner (cheaper than realtime) should do the heavy lifting. Realtime is only for quick confirmation and reading the result aloud if the owner asks.
- **latency:** Interactive setup under a couple seconds. The catch-up itself can take longer (tens of seconds to a few minutes) and should run without holding a live voice session.
- **cost:** Low realtime cost (brief handoff). Main cost is mac-planner tokens plus any browser actions. Avoid pulling large inbox content unless necessary; summarize and only expand on request.
- **security:** It touches email, tasks, and possibly internal tools. The plan should use least access. Anything that sends messages, deletes, or changes tasks requires explicit confirmation; read-only summarization should be allowed.
- **missing:** A scheduler/queue to run when the owner returns or at a set time; A relay job-status and result delivery path that can notify the owner later (audio or dashboard); A way to persist the owner’s preference for what sources to include

### "“Remind me every weekday at 5 to shut down and summarize what I did today.”"
- **useful because:** Creates a dependable end-of-day routine without the owner having to remember or keep the pendant session open.
- **path:** relay: captures the intent and schedules it → scheduler: triggers routine at the right time → mac-bridge: mac_delegate runs a day summary from local sources → relay: provides a short spoken summary if the owner asks, and posts a dashboard note
- **model tier:** A scheduled, cheaper background model should run the routine. Realtime should not stay engaged or poll.
- **latency:** Scheduling is instant. Summary can take up to a minute; delivery can be async.
- **cost:** Low per run if sources are summarized and only key changes are read. Avoid lengthy transcripts and large context carryover.
- **security:** Summaries may include sensitive work content. Store minimal output and respect data minimization. Any action that changes systems (closing apps, committing code) must require confirmation.
- **missing:** A real scheduler (cron or durable object alarms) and a routine store; A delivery mechanism for results (audio file in R2 and/or dashboard notification); Preference UI in the dashboard to configure time and included sources

### "“Read me the top three things I should care about right now.”"
- **useful because:** A quick, low-friction prioritization helps the owner focus without diving into multiple apps.
- **path:** relay: captures the request, confirms scope if needed → mac-bridge: mac_delegate collects signals (calendar, reminders, email flags, ongoing jobs) → browser: optional for external status checks → relay: reads out a concise prioritized list and offers to drill into one item
- **model tier:** Realtime for the short conversation and spoken output; mac-planner for gathering and ranking in the background.
- **latency:** Target under a second to acknowledge, then a brief pause while the Mac gathers. If the Mac is offline, offer a fallback using only cloud-accessible sources.
- **cost:** Moderate. The expensive part is gathering. Keep ranking simple and summaries tight; avoid full message bodies unless necessary.
- **security:** Calendar/email access is sensitive. Read-only by default. Any action like sending replies or changing reminders requires confirmation. Don’t expose private details unless the owner asks to open them.
- **missing:** Reliable detection of Mac availability and a fallback plan; A small preference store for signal weighting (e.g., prioritize calendar over email); Better result caching to avoid re-gathering within a short window


## Changes it proposed to its own stack

### `routines` — Add a first-class scheduler/queue for delayed and recurring work in the relay, backed by Durable Objects (alarms) or Worker Cron. Provide a routine store (D1) and a delivery mechanism that can produce an audio summary stored in R2 and a dashboard notification.
- **owner gets:** The owner can set routines once (daily brief, end-of-day shutdown, weekly review) and receive results later without keeping a live voice session open.
- effort: Medium to high: design routine schema, permissions, delivery, and failure handling; wire Mac agent polling or push for execution.  ·  risk: Missed alarms or duplicate runs if clocks drift or retries happen; recover with idempotency keys and run logs. Provide a manual “run now” command.
- cost: Adds storage and occasional scheduled compute. Saves money overall by shifting work off the realtime tier and avoiding long live sessions.  ·  latency: Improves perceived latency for users by making long tasks asynchronous.
- security: Scheduled tasks can touch sensitive data; require explicit confirmation for non-reversible actions and provide clear audit logs.
- depends on: Ground truth stack confirmed via get_hardware_spec(stack); A job status/result path (e.g., relay_job_status) and a delivery mechanism


## What it asked for

_Nothing._
