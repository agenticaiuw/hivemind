# Harness derivation — relay-realtime — round 125

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Did you send that to my Mac, and what’s happening with it?"
- **useful because:** This is the most common trust question in a voice assistant. It reduces anxiety and avoids repeats by giving a clear delivery and progress story from pendant to relay to Mac job receipts.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** Realtime only for the spoken response; cheaper backend logic should collate receipts and status.
- **latency:** Under 300ms when receipts are present; otherwise return a quick “unknown, still checking” and fall back to a single downstream status request.
- **cost:** Low per invocation; dominated by reading relay receipts and, if needed, one Mac job status read.
- **security:** Receipts are metadata but still sensitive. Should not expose spoken content; only show correlation ids and status. Must avoid claiming completion without a receipt.
- **missing:** relay delivery acknowledgements for intent routing; correlation ids shared across relay and Mac jobs; implemented relay_job_status tool or equivalent backend route

### "While I am away from my Mac, let me say “start this and keep me posted”: have the pendant capture the request, the always-on relay hand it to the right Mac or authenticated-browser surface, let that surface work through temporary disconnects, and resume the same spoken conversation later with a concise result, exact evidence, and the next safe continuation step when I say “continue that.”"
- **useful because:** Today a spoken request is tied to a live turn and the owner cannot reliably resume an interrupted multi-surface task by reference. This would make the wearable useful while away: the owner can delegate once, lose LTE/Mac connectivity or stop talking, and later recover what actually happened rather than repeating the task or guessing whether it ran. The distinctive value is continuity across pendant, relay, Mac planner, and browser-held sessions, with evidence instead of a bare success claim.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use relay-realtime only to acknowledge, disambiguate, and speak the final short update. Use the cheaper background Mac planner/browser workers for execution, polling, evidence extraction, and summarization; invoke realtime again only when the owner reconnects or asks a follow-up.
- **latency:** Acknowledge the initial voice request in under 1 second and persist it before speaking. Background work may take minutes and survive dropped links. On reconnect, deliver a 5–10 second summary first, then stream detail only if requested.
- **cost:** One realtime turn for capture/acknowledgement and one on reconnect; background planner/browser calls dominate and should be batched. Storage and receipts are negligible compared with model calls.
- **security:** The relay must persist only the normalized request, routing metadata, and encrypted evidence references; authenticated page contents remain in the browser session where possible. Every downstream action needs an immutable provenance chain (utterance, agent, target, timestamps, result, and undo receipt), and the owner must be told when a task is merely drafted, blocked, or completed. Resuming by voice must never silently substitute a different task with a similar name.
- **missing:** A durable cross-surface task/thread record with resumable state and provenance, not just a live job id; A reconnect-aware delivery queue that can speak pending updates to the pendant and collapse stale intermediate updates; A shared continuation-token protocol understood by relay, Mac planner, Mac vision, and browser extension (including tab/session affinity); A background worker/scheduler with retry and cancellation semantics for work after the live turn ends; A compact evidence bundle and spoken-summary generator that can cite browser/Mac receipts without replaying sensitive page contents


## Changes it proposed to its own stack

### `relay` — Add a relay-visible capabilities endpoint and event/receipt stream for the pendant surface, including device registration, connection state, intent delivery acknowledgements, and downstream job references. Mirror the Mac agent’s /capabilities with a minimal read-only inventory, and expose delivery receipts so the realtime agent can truthfully answer “did you hear me?” and “did you send it?”.
- **owner gets:** The owner can ask what’s happening right now and get a truthful answer. No more guessing whether the pendant is connected or whether an intent was delivered; fewer dropped tasks and less confusion during voice interactions.
- effort: Medium: new relay routes, durable storage for recent events/receipts, and a small schema shared with the orchestrator. Requires coordination with the orchestrator to emit receipts.  ·  risk: Low to medium. Incorrect receipts could mislead, but this is read-only introspection; start with conservative states and clear “unknown” responses. Add correlation ids to avoid mixing events.
- cost: Low API cost; small storage for recent receipts. Biggest cost is engineering time and maintaining the schema.  ·  latency: Improves conversational latency by removing extra probing and retries; receipts are a single read instead of multiple round trips.
- security: Moderate: exposes operational metadata. Protect with bearer auth and avoid leaking content; only expose ids, timestamps, and statuses.
- depends on: Orchestrator emitting delivery acknowledgements and correlating ids across relay and downstream jobs


## What it asked for

_Nothing._
## Its own summary

Discovered current tools, devices, and routes, and verified live device state via /v1/devices/status. The Mac bridge is online. relay_route_intent and relay_job_status are present but relay_route_intent is a schema with no implementation; relay_job_status is described but its real backend implementation still needs confirmation. Proposed a relay change: add a relay-visible capabilities inventory plus delivery receipts/ack stream so the realtime agent can truthfully answer delivery questions without guessing.

**Biggest unknown:** Whether delivery acknowledgements and correlation ids exist anywhere in the system today. If they do not, we need orchestrator support (and likely durable relay storage) to emit and store them; if they do, we need a relay-visible route to read them.

