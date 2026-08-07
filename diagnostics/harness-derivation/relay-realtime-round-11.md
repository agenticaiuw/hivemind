# Harness derivation — relay-realtime — round 11

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

- **tooling_discrepancy** — Stack spec says the realtime agent has exactly five tools (get_mac_status, mac_run_actions, browser_run_actions, web_search, mac_delegate), but the currently exposed tool list in this session is different (probe_http, get_hardware_spec, message_peer, request_context, request_tool, request_permission, record_finding, finish, propose_capability, propose_change, request_device_skill, relay_route_intent).
  - evidence: get_hardware_spec(component='stack') returned agent_tools_today list that does not match the tools available in this conversation.

## Changes it proposed to its own stack

### `model-routing` — Introduce a clear tiering rule: realtime relay model only handles conversational intent capture, clarification, and short confirmations. Any task that can run asynchronously (web search, email, file operations, automation, long summaries, scheduled reminders) should be routed to a cheaper background model via mac-planner or a server-side browser/search worker. Provide a standardized intent envelope and status updates so the relay doesn’t keep long context or poll for completion.
- **owner gets:** Faster, cheaper interactions. The pendant feels responsive, while longer work finishes in the background and returns when ready without burning tokens in a live conversation.
- effort: Medium. Requires routing contract and status UI, plus background workers for web/search if not already present.  ·  risk: Misrouting could cause delays or partial completion. Mitigate with explicit confirmation for high-impact actions and a fallback to tell the user when a task can’t run in the current tier.
- cost: Reduces per-second audio and token usage by moving heavy work off the realtime model. Costs shift to cheaper background tokens and occasional status messages.  ·  latency: Improves perceived latency for the owner. Background work may take longer overall but doesn’t block conversation.
- security: Limits the blast radius of the realtime agent. High-risk actions stay behind mac-planner’s risk scoring and confirmation gates.
- depends on: Authoritative tool/routing contract from orchestrator; mac-planner job queue/status primitives exposed to relay


## What it asked for

### `c6-wxri` (context) — owner_workflows_and_preferences
- why: To propose genuinely useful capabilities and safe default behaviors, I need to know what the owner actually wants to do with the pendant (e.g., reminders, dictation, web lookups, controlling Mac apps) and any preferences like privacy, verbosity, and confirmation style.
- would change: I will prioritize capabilities and changes that match the owner's top workflows, and set conservative confirmation and data-sharing defaults aligned with their preferences, reducing costs and unnecessary context.

### `c7-y69b` (context) — available_tools_and_routing_contract
- why: The stack spec references specific tools and a Mac planning pipeline. I need the orchestrator’s authoritative list of tools exposed to this agent and any routing/permission constraints so I don’t assume capabilities that aren’t available.
- would change: I will only propose or attempt actions that are actually possible, and use the correct tool (or request missing ones) rather than relying on mismatched documentation.

## Its own summary

I grounded in the real stack and hardware constraints. The pendant is an nRF9160 running Zephyr with tight RAM, audio is Opus over a constrained LTE-M half-duplex link, and the relay is a Cloudflare Worker with D1/R2. I also found a documentation/tooling mismatch: the stack spec lists five tools for this agent that don’t match the tools actually exposed in this session. I proposed a model-routing change: keep realtime for intent and confirmations, move heavy/async work to cheaper tiers with a standardized intent envelope and status updates. I requested context on owner workflows/preferences and the authoritative tool/routing contract; both are queued for later rounds.

**Biggest unknown:** What the owner’s top workflows are and what tools/routing are actually available to this agent right now. Without that, I can’t safely propose concrete capabilities that touch the Mac, browser, or memory without risking cost, latency, or security issues.

