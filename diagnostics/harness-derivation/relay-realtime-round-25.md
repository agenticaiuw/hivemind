# Harness derivation — relay-realtime — round 25

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "What’s connected right now, and can you hand this off to my Mac if needed?"
- **useful because:** The owner is often away from the Mac. A quick status check plus a clean handoff reduces friction and prevents asking the Mac to do things when the bridge is offline or the browser extension is down.
- **path:** pendant → relay → mac-bridge → browser
- **model tier:** realtime for the spoken status; mac-planner for follow-on tasks if the owner asks to proceed
- **latency:** Under 1 second for status from relay-visible sources; additional time only if the owner asks to proceed with a Mac task.
- **cost:** Very low for relay status probes; higher only if a delegated Mac plan is created.
- **security:** Status includes device presence and possibly network info; keep it minimal and do not expose anything beyond what the owner asked for.
- **missing:** A consistent status schema across relay and Mac surfaces so the spoken summary is stable.; A standard handoff intent taxonomy so the relay can say what it is delegating in a way downstream agents understand.


## Changes it proposed to its own stack

### `context` — Add a typed discovery registry for granted tools and capabilities. When the orchestrator grants a tool, it registers under a stable name with a version and a canonical describe() entry so relay can reliably introspect and route without guessing names or relying on system prompt text.
- **owner gets:** Fewer voice failures and faster handoffs. If I can always find what exists, I can route requests correctly instead of stumbling on missing descriptors.
- effort: Medium: define a registry schema, have the orchestrator populate it, and have list_capabilities/discover return canonical names that describe() resolves.  ·  risk: Low. Main risk is backward incompatibility with existing tool names; mitigate with alias support and deprecation windows.
- cost: Small API cost per discovery call; reduces wasted tool calls and retries.  ·  latency: Improves responsiveness by avoiding failed describe calls and misroutes.
- security: Low; registry contains metadata, not secrets.
- depends on: list_capabilities/discover/describe must support canonical naming and aliases


## What it asked for

_Nothing._
