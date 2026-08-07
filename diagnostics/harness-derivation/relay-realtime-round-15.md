# Harness derivation — relay-realtime — round 15

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

- **Tooling state discrepancy** — Stack spec reports the realtime agent has exactly five tools (get_mac_status, mac_run_actions, browser_run_actions, web_search, mac_delegate), but the current system tool list also includes relay_route_intent, server_browser_actions, and relay_job_status.
  - evidence: get_hardware_spec(stack).agent_tools_today lists exactly five tools; system prompt tool list includes additional relay_* and server_browser_actions tools.

## Capabilities it proposed

### "“Check the weather and read the highlights to me.”"
- **useful because:** Quick, hands-free information while the owner is away from the Mac, without needing the Mac to be online.
- **path:** relay → server-side browser (Cloudflare Browser Run) → audio spoken response
- **model tier:** Cheaper non-realtime tier for browsing/extraction; realtime only for brief conversational follow-up.
- **latency:** A couple seconds for summary is fine; realtime should not wait on long page interactions.
- **cost:** Dominated by browser execution and extraction tokens; minimal relay tokens if it delegates.
- **security:** Web pages can contain tracking and malicious content; keep browsing sandboxed, avoid logging sensitive extracted data, and require confirmation before opening authenticated sessions.
- **missing:** Confirm production availability of server-side browser actions in the relay toolset and wire it to a safe extraction pipeline.


## Changes it proposed to its own stack

### `routines` — Add a Worker-side scheduler using Cron Triggers and Durable Object alarms to run routines even when the Mac is asleep, with a simple queue that delegates to the Mac when it’s online or performs server-side tasks when possible.
- **owner gets:** Time-based routines (daily summaries, reminders, check-ins) actually happen reliably, not only when the Mac is awake.
- effort: Medium: new Durable Object for routine state, Cron wiring, and execution routing logic.  ·  risk: Duplicate runs if both Mac and Worker schedulers fire; mitigate with idempotency keys and a last-run ledger.
- cost: Low per routine tick; costs dominated by downstream model/tool usage.  ·  latency: No realtime latency impact; runs in background.
- security: Worker can trigger actions; require explicit confirmation for irreversible actions (sending email, purchases), and keep least-privileged credentials.


## What it asked for

_Nothing._
## Its own summary

Grounded proposals in the real stack: relay is a Cloudflare Worker, Mac agent polls for jobs, dashboard is a single SvelteKit app shipped across surfaces, and the stack spec still claims only five tools even though additional relay/server browser tools appear present. Proposed a weather-readout capability using server-side browsing and a Worker-side scheduler to make routines reliable when the Mac is asleep. Shared routing facts with mac-terminal. Remaining work is to align tool availability/spec, and to design more end-to-end capabilities with explicit cost/latency/security tiers.

**Biggest unknown:** Whether the additional relay tools (relay_route_intent, server_browser_actions, relay_job_status) are fully wired and safe in production, and how to observe job progress end-to-end without inventing a protocol.

