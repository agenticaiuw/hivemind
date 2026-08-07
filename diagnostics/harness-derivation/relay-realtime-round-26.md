# Harness derivation — relay-realtime — round 26

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If this will take longer, keep working on my Mac and let me know when it’s done."
- **useful because:** This matches real life: the owner speaks a goal, then walks away. The system should continue the task on the Mac, track progress, and report back when finished, without requiring the owner to babysit the process.
- **path:** pendant → relay → mac-bridge → browser → relay
- **model tier:** Mac planner for the actual work; relay for quick conversational updates; cheaper completion model for summaries if available.
- **latency:** Under a second for the initial acknowledgment; the work itself can take minutes. Progress updates should be brief and optional.
- **cost:** Low cost at the relay (short acknowledgments). Main cost is Mac-side planning/execution and any browser automation; dominant cost is tool calls and page processing.
- **security:** Must avoid executing irreversible actions without explicit confirmation. Progress/status messages may contain sensitive page content; redact where possible and keep summaries minimal.
- **missing:** A reliable job status channel from Mac to relay for long-running delegated tasks; A notification mechanism to reach the pendant when the owner is away (push or poll); Durable storage for job state so the relay can reconnect after disconnects


## Changes it proposed to its own stack

### `context` — Add a typed capability registry that maps discovered tool names and surfaces to stable internal identifiers. The registry should reconcile differences between what’s granted, what’s discoverable, and what’s actually callable, and expose a single describe(name) namespace so newly granted tools are immediately describable without guessing the right category.
- **owner gets:** Prevents the assistant from getting stuck when a tool is granted but not discoverable under the expected category, so voice requests keep working and upgrades don’t break the conversation.
- effort: Medium: requires changes to discovery/registry wiring and tests for backwards compatibility.  ·  risk: Low: risk is misrouting if mapping is wrong; mitigate with explicit validation against a simple health probe and a fallback to known-good tools.
- cost: Small API overhead for registry sync; negligible runtime cost after cache.  ·  latency: Slightly higher on cold start to reconcile, then faster because describe calls stop failing.
- security: Low; must ensure registry cannot be poisoned by untrusted inputs and that tool metadata is not leaked across tenants.


## What it asked for

_Nothing._
