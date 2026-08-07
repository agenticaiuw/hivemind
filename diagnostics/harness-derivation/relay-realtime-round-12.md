# Harness derivation — relay-realtime — round 12

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

- **tool availability mismatch** — Hardware spec says the realtime agent has exactly five tools (get_mac_status, mac_run_actions, browser_run_actions, web_search, mac_delegate), but the currently exposed tool list in this session only shows a different set (probe_http, get_hardware_spec, message_peer, request_context, request_tool, request_permission, record_finding, finish, propose_capability, propose_change, request_device_skill, relay_route_intent).
  - evidence: get_hardware_spec(component='stack') returned agent_tools_today listing five tools that are not visible in the current tool schema.

## Capabilities it proposed

### "“Plan my day. Pull my calendar, summarize critical tasks and travel time, and give me a 30-second briefing.”"
- **useful because:** It turns scattered commitments into a concise spoken plan the owner can use while walking, commuting, or getting ready.
- **path:** relay: capture the request, clarify constraints (time horizon, preferred tone), and hand off → mac-bridge: fetch calendar/tasks from local apps if available; browser: fetch from web services if needed → relay: deliver a short audio briefing; dashboard: show the same summary for later review
- **model tier:** Realtime for the initial conversation and confirmation; a cheaper background model for aggregation/summarization, scheduled as a job and returned when ready.
- **latency:** Under 2-3 seconds to acknowledge and confirm scope; tens of seconds for the background job is okay because it arrives as audio when ready.
- **cost:** Realtime cost dominated by a short confirmation turn; background cost dominated by calendar/task API calls and summarization tokens. Use the smallest context window and avoid pulling full event descriptions unless needed.
- **security:** Calendar and task data is sensitive. Require explicit confirmation before accessing new accounts or expanding scope (e.g., reading email). Clearly state what sources will be read. Avoid storing raw event bodies; store only derived summary if at all.
- **missing:** A standardized intent-to-job route from relay to mac-planner/browser, with status updates; Confirmed availability of calendar/task connectors (local or web) and permissions to access them; An audio job delivery mechanism to queue and play back the briefing on the pendant

### "“Read my notifications and tell me only what’s important.”"
- **useful because:** Reduces distraction by turning notification overload into a brief, prioritized spoken digest.
- **path:** relay: capture the request and preferences (sources, urgency rules) → mac-bridge and/or phone integration: collect notifications from allowed sources → background model: classify and rank; relay: speak the digest; dashboard: let the owner adjust rules
- **model tier:** Realtime for preference capture and confirmation; cheaper background model for classification, deduping, and digest generation.
- **latency:** 1-2 seconds to confirm the filter; digest can take a few seconds more and arrive as audio when ready.
- **cost:** Low realtime cost; background cost dominated by notification text volume and classification. Use strict source filters and truncate long content.
- **security:** Notifications can contain private messages and codes. Require explicit opt-in per source (e.g., messaging apps). Never read out one-time codes by default. Avoid storing sensitive content beyond what’s needed.
- **missing:** A phone-side notification pipeline (iOS/Android) or a desktop notification collector; Rule UI in the dashboard and a preferences store; A safe default policy for sensitive content like 2FA codes

### "“Start a focus session for 25 minutes. Block distractions and let me know when time’s up.”"
- **useful because:** Helps the owner create a simple, repeatable routine to get work done without fiddling with apps.
- **path:** relay: start/stop commands and quick status → mac-bridge: enforce blocking (apps/sites) when the Mac is present → background job: timer; relay or pendant audio: end-of-session chime; dashboard: session log
- **model tier:** Realtime for start/stop and confirmation; cheap timer job for scheduling; mac agent for enforcement policies.
- **latency:** Under a second to start; timer runs in the background; end notification timing must be accurate to within a few seconds.
- **cost:** Minimal realtime tokens; cheap timer job; enforcement cost depends on how many actions need to be applied on the Mac.
- **security:** Blocking apps/sites alters the owner’s computer behavior. Require explicit confirmation the first time a blocklist is applied. Provide a clear override phrase. Log changes for transparency.
- **missing:** A timer/scheduler service for jobs; Mac enforcement actions and permission to control apps/network; A pendant-side chime or audio playback capability for offline end-of-session alerts

### "“Remember this: my bike lock code is 4829.”"
- **useful because:** Lets the owner offload small facts and retrieve them later by voice.
- **path:** relay: capture and confirm what to store; relay: retrieve on request → memory store: save encrypted or access-controlled entries; dashboard: manage and delete stored memories
- **model tier:** Realtime for capture/recall; cheap storage operations. Use minimal context to avoid paying to re-send stored facts.
- **latency:** Under a second to confirm storage; recall should be near-instant.
- **cost:** Very low; dominated by a brief confirmation turn and a small memory write/read.
- **security:** Sensitive secrets are risky. Require explicit confirmation and label as sensitive. Store encrypted, restrict retrieval to authenticated sessions, and avoid speaking secrets out loud unless the owner asks and is in a safe context.
- **missing:** A secure memory write/read API with encryption and access controls; Policies for sensitive data handling and redaction; A way to mark entries as secret vs general


## Changes it proposed to its own stack

### `model-routing` — Introduce a clear tiering policy: relay-realtime handles only intent capture, brief clarification, and immediate safety checks; everything else becomes a job executed by cheaper background models via the Mac bridge or a server-side browser, with status updates streamed back.
- **owner gets:** Faster, more reliable voice interactions and lower cost, because long-running work happens elsewhere without tying up the live conversation.
- effort: Medium: define intent schema, job queue contracts, and status events; update orchestrator routing.  ·  risk: Misrouted intents could cause wrong actions. Mitigate with explicit confirmation for destructive or high-risk actions and a visible job log.
- cost: Lower ongoing cost by reducing realtime tokens and audio time; background jobs pay only for what they use.  ·  latency: Improves perceived latency for conversation; background work may take longer but doesn’t block the user.
- security: Better isolation if high-risk operations are confined to mac-vision/planner with risk scoring; still requires strong auth and audit.
- depends on: Confirm the five agent tools listed in hardware spec exist and are wired, or update the spec/tooling to match reality

### `integration` — Add a server-side browser harness (Cloudflare Browser Run) so the relay can perform read-only web tasks without requiring the Mac to be online, with strict allowlists and output sanitization.
- **owner gets:** Web lookups and account-independent tasks work even when the Mac is asleep or away, making the pendant more useful on the go.
- effort: Medium: implement harness, allowlists, and fallback to Mac browser bridge when needed.  ·  risk: Web automation can leak data or trigger unintended actions. Keep it read-only by default, require confirmation for form submissions, and log actions.
- cost: Potentially cheaper than waking the Mac; cost dominated by browsing time and model tokens.  ·  latency: Removes dependency on Mac availability; web page loads still dominate.
- security: Strict origin allowlists, content stripping, and no credential use unless explicitly authorized.


## What it asked for

_Nothing._
## Its own summary

I grounded proposals in the real stack: the relay should capture intent and hand off longer work to cheaper tiers; background jobs can return audio later. I proposed capabilities for day planning, notification digests, focus sessions, and secure memory, plus routing and server-side browser changes. I also recorded a mismatch between the hardware spec’s listed realtime tools and the tools actually exposed in this session.

**Biggest unknown:** Tooling and permissions reality: the stack spec says the realtime agent has five specific tools, but they aren’t visible here. I need either those tools wired in, or updated specs/tooling so I can actually route jobs and perform useful actions. Also missing are confirmed connectors (calendar/notifications), a scheduler/audio job delivery path, and secure memory APIs.

