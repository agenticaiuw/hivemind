# Harness derivation — relay-realtime — round 18

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Summarize the top results from the web about X, and keep it out of my Mac.”"
- **useful because:** It lets the owner get quick research-style answers while away from the Mac, without waking the desktop agent or touching private authenticated sessions.
- **path:** relay → server browser → dashboard
- **model tier:** A cheaper background model should run the browsing and extraction. The realtime relay should only parse the request, confirm scope, and read back the summary.
- **latency:** Conversation stays snappy because the relay hands off quickly; the browsing takes as long as needed without the owner waiting on live audio.
- **cost:** Low relay cost (short prompt), moderate browsing cost dominated by page loads and extraction tokens. Cheaper than routing through the Mac planner for purely public web content.
- **security:** Avoid authenticated pages and anything requiring login unless explicitly routed to the Mac browser bridge. Confirm any action beyond reading/extracting (no purchases, no form submissions).
- **missing:** server-side browser auth policy and allowlist for public-only browsing; a small summary/extraction pipeline that produces concise, citation-backed output; a job status UI in the dashboard so the owner can see progress if the task continues after the call

### "“Check my inbox and tell me what needs attention, but don’t send anything.”"
- **useful because:** The owner gets a quick triage while walking, without sitting down at the Mac. It’s an everyday wearable superpower: prioritize, not compose.
- **path:** relay → mac-bridge → browser
- **model tier:** Mac planner should handle the workflow. Realtime relay only captures the request and delivers the summary. Browser actions must stop before sending or making changes.
- **latency:** Short initial handoff; the Mac can work in the background. If it takes longer, the relay can provide a brief status update and finish later.
- **cost:** Mac planner cost dominates; browser interaction cost depends on mailbox size. Relay remains minimal.
- **security:** Inbox is sensitive. Require explicit confirmation for accessing any new account/source. Never send replies or delete/archive without confirmation. Present proposed changes as a payload for approval.
- **missing:** a reliable background job mechanism or durable alarm to continue work and report back later; a relay-to-owner notification mechanism (audio or dashboard) when triage completes; a standardized summary format for triage results


## Changes it proposed to its own stack

### `routines` — Add a scheduler layer using Worker Cron Triggers and Durable Object alarms for delayed and recurring jobs, with a job table in D1 and a relay job-status endpoint. Jobs can target relay, server browser, or mac-bridge, and can emit a completion notification to the dashboard and optionally an audio snippet to play later.
- **owner gets:** They can ask for things like “every morning summarize my calendar” or “remind me in two hours,” and it actually happens without them keeping a session open.
- effort: Medium to high: wiring cron, durable alarms, persistence, idempotency, and status reporting.  ·  risk: Jobs could run unexpectedly or repeatedly. Mitigate with clear job listing, pause/disable controls, and per-job confirmation for first run.
- cost: Adds storage reads/writes and occasional cron invocations; overall cost controlled by keeping job payloads small and using cheaper models for execution.  ·  latency: Improves perceived latency by moving work off the realtime path; adds no delay to immediate conversations.
- security: Scheduled jobs can access data without the owner present. Require explicit confirmation, scope limits, and readable audit logs in the dashboard.
- depends on: Define job schema and status API; notification channel to dashboard/audio

### `interaction` — Introduce a confirmation gate for high-risk actions: relay summarizes intent, shows/reads a payload (e.g., draft email, purchase order, form submission), and requires a clear “confirm” before sending. Provide a reversible safe mode for exploratory actions.
- **owner gets:** It prevents accidental spends or messages while keeping quick tasks fast. The owner stays in control, especially when away from the Mac.
- effort: Low to medium: implement payload generation conventions and a consistent confirmation phrase.  ·  risk: Too many prompts could frustrate. Keep it for high-risk actions only; allow reversible actions without confirmation.
- cost: Small extra tokens for summarizing payloads.  ·  latency: Tiny delay for confirmation; worth it for risky operations.
- security: Reduces risk of unintended data changes and spending; creates auditable checkpoints.
- depends on: Standard payload format from mac-planner/browser actions


## What it asked for

### `s12-egbt` (skill) — offline_voice_memo_store_and_forward
- does: Records a short voice memo locally when the network is unavailable, then forwards it to the relay when connectivity returns. Provides a simple LED pattern to indicate stored memos.
- must be on-device because: It must work when LTE-M is down and survive link drops. Only the device can capture audio at that moment.
- trigger: button press while offline (or network error during capture)
- storage: store compressed audio plus a small header in flash; keep a bounded queue (e.g., up to N memos or total size cap)
- RAM budget: Target under ~20–30 KB incremental RAM for buffering and queue metadata; reuse existing audio buffers where possible; avoid large dynamic allocations.

## Its own summary

I discovered the current surfaces/categories and confirmed the stack: the relay runs on a Cloudflare Worker with only five production tools, while server-side browser capability exists as a potential path to remove the Mac from public web tasks. I proposed a relay capability for public web summarization via a server browser, a Mac-based inbox triage capability, a firmware skill for offline voice memo store-and-forward, and changes for a scheduler and confirmation gates.

**Biggest unknown:** The biggest unknown is the exact current capability/tool inventory and route details (especially job status, notification mechanisms, and any existing dashboard support) needed to implement scheduling, progress updates, and completion delivery without keeping the realtime session open.

