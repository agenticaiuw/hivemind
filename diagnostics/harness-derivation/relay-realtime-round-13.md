# Harness derivation — relay-realtime — round 13

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

- **Tooling description mismatch** — The stack spec says the realtime agent has exactly five tools (get_mac_status, mac_run_actions, browser_run_actions, web_search, mac_delegate), but the tools available in this session include a different set (probe_http, get_hardware_spec, message_peer, request_context, request_tool, request_permission, record_finding, finish, propose_capability, propose_change, request_device_skill, relay_route_intent).
  - evidence: get_hardware_spec(stack) returned the five-tool list, while the session tool registry exposes a different set of tools.

## Capabilities it proposed

### "“Summarize the key points from this page and read them to me later.”"
- **useful because:** The owner can capture useful info while on the move, then hear a concise summary when they have time, without staring at a screen.
- **path:** relay: capture request and confirm target timing/output → browser (server-side or via mac-planner): fetch and extract page content → background worker: summarize and store audio/text artifact → dashboard: show saved summaries and playback history → pendant: later playback as audio when requested
- **model tier:** Realtime only for capture/confirmation. Summarization runs on a cheaper background model. Text-to-speech can be offline-prepared and stored.
- **latency:** Interactive confirmation under 2-3 seconds. Fetching and summarizing can take 10-60 seconds in the background; playback is instant once ready.
- **cost:** Capture cost is small (short transcript). Background cost dominated by page text length and summary generation; TTS cost depends on audio duration.
- **security:** Web content could be malicious or contain tracking. Only fetch the target URL, avoid executing scripts when possible, and store only what’s needed. If the page requires login, require explicit confirmation before using authenticated sessions.
- **missing:** A job queue / background worker contract; Server-side browser actions or a reliable Mac delegation path; Storage and playback pipeline for prepared audio artifacts


## Changes it proposed to its own stack

### `stack` — Align the stack spec and orchestrator tool registry for the realtime agent, and publish a single authoritative capability manifest (tools, endpoints, permissions, and model routing) that both the runtime and documentation derive from. Add a health endpoint that returns the active manifest so agents can reason safely about what exists.
- **owner gets:** Fewer routing errors and less back-and-forth. When I say I can do something, it actually works, which means faster help and lower cost.
- effort: Medium. Requires orchestrator changes plus docs/tests for manifest generation and validation.  ·  risk: If manifest generation is wrong, agents could lose access to tools. Mitigate by rolling out behind a flag and validating against a golden manifest in CI.
- cost: Low. Mostly engineering time; runtime cost is a small extra manifest fetch or cached config.  ·  latency: Low. A cached manifest avoids per-turn overhead; improves reliability.
- security: Positive. A single manifest makes permission boundaries explicit and auditable.


## What it asked for

### `c8-s13o` (context) — job scheduling and background workers
- why: To propose useful routines that finish later (like summaries, reminders, or queued web reads), I need to know what job queue endpoints exist and which model tier runs them.
- would change: If a queue exists, I’ll route non-urgent work there and keep the realtime session short. If it doesn’t, I’ll avoid proposing scheduled/queued features and focus on immediate, low-latency interactions.

### `t6-5w4j` (tool) — server_browser_actions
- why: Enable the relay to run safe, sandboxed browser interactions without relying on the owner’s Mac being online, using Cloudflare Browser Run when available.

```json
{
  "type": "object",
  "properties": {
    "url": {
      "type": "string",
      "description": "The starting URL to open."
    },
    "actions": {
      "type": "array",
      "description": "High-level browser actions to perform (navigate, click, extract, search).",
      "items": {
        "type": "object"
      }
    },
    "timeout_ms": {
      "type": "number",
      "description": "Overall timeout in milliseconds."
    }
  },
  "required": [
    "url",
    "actions"
  ]
}
```

### `p6-8psf` (permission) — probe:post:/v1/bridge/work
- why: If I’m going to delegate tasks to the Mac harness reliably, I need to enqueue work rather than rely on ad-hoc routing.
- risk it sees: This could trigger actions on the owner’s computer. It should require explicit user confirmation per task and strict risk scoring with a visible summary before execution.

## Its own summary

Discovered a mismatch between the documented realtime toolset and the actual tools available, and proposed unifying them with an authoritative manifest. Proposed a useful ‘summarize and play later’ capability, with proper tiering (realtime capture, background processing) to control latency and cost. Requested context for background job scheduling, a server-side browser tool, and permission to enqueue work for the Mac harness, but those are pending orchestrator decisions.

**Biggest unknown:** Whether there is a supported background job queue/worker and which model tier runs it, plus whether the relay can use a server-side browser or must always delegate web tasks to the Mac harness.

