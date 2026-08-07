# Harness derivation — relay-realtime — round 17

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Give me a quick briefing for my day, and make it something I can listen to later."
- **useful because:** You get a concise, spoken plan that you can play when you have time, instead of standing around while I think and fetch.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** Realtime captures the request and confirmation; a cheaper planner model compiles the briefing; text-to-speech (or existing audio pipeline) renders it for later playback.
- **latency:** Under 5 seconds to acknowledge and confirm. The actual research/compilation can take minutes and should not hold the mic open.
- **cost:** Low for the realtime capture; medium for planning and any web lookups; audio generation/storage costs dominate if the briefing is long.
- **security:** Briefings may include calendar, projects, and emails. Only include sources the user opted into. Require confirmation before accessing email or external services, and store only the final audio plus minimal metadata.
- **missing:** A scheduler or delayed job mechanism to run later; Reliable job status and delivery UI; Audio rendering path for scheduled output if not already present; Consent settings for which sources to include

### "Look up this topic on the web and summarize it for me."
- **useful because:** Fast, hands-free answers while you’re away from your computer, without needing the Mac to be online.
- **path:** pendant → relay → browser
- **model tier:** Realtime for intent and constraints; server-side browser for extraction; a smaller summarizer for synthesis.
- **latency:** Quick confirmation in under a few seconds; summary may take 5-20 seconds depending on page complexity.
- **cost:** Dominated by server browser runtime and summarization tokens; relay cost stays small if we keep context tight.
- **security:** Avoid logging extracted page content. For paywalled or authenticated sites, fall back to the Mac with explicit confirmation.
- **missing:** server_browser_actions routing and extraction templates; Fallback to mac_delegate for authenticated content; Clear error messages when blocked


## Changes it proposed to its own stack

### `routines` — Add a real scheduling layer for delayed and recurring work in the relay: use Cloudflare Cron Triggers for recurring jobs and Durable Object alarms for per-user delayed jobs. Jobs should enqueue a plan to mac-planner when appropriate, or run server-side web tasks when the Mac is offline. Provide a job table in D1 with status and receipts.
- **owner gets:** You can say “remind me every morning” or “check that thing in an hour” and it actually happens, even if the Mac is asleep. Briefings and research can arrive later as audio you play on your own schedule.
- effort: Medium: new worker routes, durable object, D1 migrations, job schema, and UI to list scheduled jobs.  ·  risk: Jobs could run unexpectedly or duplicate. Mitigate with idempotency keys, clear user-visible schedule list, and a hard limit on frequency. Provide cancel/disable controls.
- cost: Low per job: a small D1 write and an occasional cron/alarm wakeup. Most cost is downstream model tokens when the job actually runs.  ·  latency: Improves perceived latency because expensive work happens off the live conversation path.
- security: Scheduling can trigger actions later; require explicit confirmation for any destructive or external spend, and log receipts for audit.
- depends on: D1 job table and receipts; relay_job_status endpoint/tool for monitoring; mac-planner plan/execute endpoints already present

### `model-routing` — Default web reading and extraction to a server-side browser (Cloudflare Browser Run) via server_browser_actions when the task is purely web and does not require local files or accounts. Use mac_delegate only for tasks that need local access or app control. Keep the realtime model focused on intent capture and confirmation.
- **owner gets:** Web lookups become more reliable when you’re away from your Mac, and the pendant feels faster because the heavy lifting moves off the live voice loop.
- effort: Medium: add routing rules, timeouts, extraction templates, and fallback to Mac when server browser fails.  ·  risk: Server browser may hit anti-bot blocks or render differently. Provide graceful fallback and clear errors.
- cost: Moderate: server browser runtime plus tokens, but saves repeated relay turns and avoids waking the Mac.  ·  latency: Often faster end-to-end for web tasks; slower for pages with heavy scripts. Use timeouts and partial extraction.
- security: Web content is public, but it can still leak sensitive data if logged. Don’t store page contents unless needed; redact URLs and query terms in logs when appropriate.

### `relay` — Add a lightweight intent-routing policy that uses relay_route_intent to label the request and target mac-planner or server browser explicitly, and emits a short spoken confirmation when an action could change state or spend money. Keep a small, pruned context window and store summaries in memory instead of replaying long transcripts.
- **owner gets:** The pendant feels predictable and safe: you hear what will happen, and you don’t pay for extra tokens carrying irrelevant history around.
- effort: Low to medium: new policy module, small memory summaries, and confirmation prompts for a handful of risky categories.  ·  risk: Over-confirmation could feel annoying. Tune for reversible actions to proceed without prompts, and destructive/external actions to require confirmation.
- cost: Lower ongoing token cost by pruning context and summarizing. Small added cost for confirmation prompts.  ·  latency: Slight overhead for confirmation, but avoids expensive misroutes.
- security: Reduces accidental destructive actions and limits data exposure by minimizing context.


## What it asked for

_Nothing._
