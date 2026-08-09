# Harness derivation — relay-realtime — round 168

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Tell me when that job finishes, even if I stop talking."
- **useful because:** This turns long-running Mac tasks into a set-and-forget experience instead of a polling ritual. The pendant can notify the owner at the moment it matters.
- **path:** relay → mac-bridge → pendant
- **model tier:** Cheaper background model for monitoring; realtime only for the spoken alert.
- **latency:** Owner hears a short spoken result within a few seconds of job completion, even if they are away from the Mac, subject to connectivity.
- **cost:** Low per job: a status poll plus a short speech render. Dominated by monitoring and audio generation, not reasoning.
- **security:** Only short summaries should be spoken. Include jobId scoping and TTL. Avoid reading sensitive content aloud unless explicitly requested.
- **missing:** A real implementation behind relay_event_push; A durable completion subscription mechanism (Durable Object or queue); A path to render and deliver short audio to the pendant when offline

### "Use the pendant button to approve that exact action list."
- **useful because:** It prevents accidental or surprising changes by tying a physical press to a specific plan, while keeping quick reversible actions fast.
- **path:** relay → mac-bridge → pendant
- **model tier:** Realtime to present the preview; no heavy reasoning needed.
- **latency:** Preview immediately, then wait for a press. Execution begins as soon as confirmation arrives.
- **cost:** Tiny: store a nonce, action hash, and expiry. Most cost is just state management.
- **security:** Nonce must be single-use, bound to the exact action list, and resistant to replay. Expire quickly.
- **missing:** Relay-side nonce state store; Action list hashing and binding; A firmware event to send the nonce on button press (or reuse an existing control path)

### "Do the web steps even if my Mac is asleep."
- **useful because:** When the owner is away from the Mac, browser tasks stall. A server-side browser would make some workflows independent of the Mac.
- **path:** relay → new-surface
- **model tier:** Cheaper background model for browsing; realtime only for brief updates.
- **latency:** Seconds to tens of seconds depending on page load; no need to block voice.
- **cost:** Higher than a simple HTTP fetch; dominated by headless browser runtime and page execution.
- **security:** Authenticated sessions and secrets must not be copied into a cloud browser. Prefer public web and explicit consent for logged-in contexts.
- **missing:** A real server_browser_actions implementation using a sandboxed browser; Session and credential isolation model; Logging and audit for actions

### "“Undo the last thing you did for me—even if it changed several apps or a browser account.”"
- **useful because:** Today the system can execute across Mac and browser, but recovery is fragmented. A spoken, owner-level undo would make autonomous action safe enough to trust: it would identify the exact prior transaction, show what can be reversed, and restore each surface rather than leaving the owner to repair it manually.
- **path:** relay-realtime → mac-planner → mac-terminal → browser-extension → faculty-action
- **model tier:** Realtime only interprets the short undo request and identifies the referenced receipt; a cheaper background planner computes inverse actions and faculty-action verifies them.
- **latency:** Acknowledge in under 500 ms; compute the inverse plan within 10 seconds; speak a result when all compensating actions finish.
- **cost:** Roughly $0.01–$0.08 per undo, dominated by the background inverse-plan model and any Mac/browser verification calls.
- **security:** Undo must be bound to an immutable transaction receipt, not a vague recent-history guess. The system must preserve a pre-action snapshot or inverse data for each mutation; restoring a deleted or externally changed item may be impossible and must be reported honestly. No data needs to leave the existing relay/Mac/browser path.
- **missing:** A transaction envelope spanning /plan and /execute with before-state or inverse metadata; Per-action compensating operations for Mac and browser mutations; Durable receipt retention and a resolver for spoken references such as “last thing”; A rollback executor that can stop after partial failure and report exactly which steps were restored

### "“Watch this live work session and, only when I explicitly press the pendant, turn the selected screen state into a finished handoff for the next person.”"
- **useful because:** The owner can currently ask for isolated Mac or browser actions, but cannot turn a real work session into a reliable handoff without manually gathering tabs, files, decisions, and unfinished work. This would combine the worn button as an explicit capture boundary with screen/browser evidence and a concise, shareable result.
- **path:** relay-realtime → mac-vision → mac-planner → browser-extension → faculty-perception → faculty-action
- **model tier:** A low-cost background perception pass extracts diffs and candidate artifacts; realtime handles only the press-time acknowledgement; a planner composes the handoff and an action tier saves or sends it.
- **latency:** Button acknowledgement under 300 ms; evidence freeze under 3 seconds; handoff draft under 20 seconds, with delivery completion pushed asynchronously.
- **cost:** About $0.03–$0.20 per handoff, dominated by screenshot/OCR and document synthesis; idle monitoring should use local hashes and not invoke a model.
- **security:** Nothing is captured continuously by default: only a bounded, explicitly pressed interval and currently selected app/window. Redact credentials and unrelated windows locally before upload. Sending externally or modifying a shared document requires a clear spoken target and an auditable receipt.
- **missing:** A Mac-vision session-diff stream with local redaction and selected-window semantics; A pendant gesture/protocol carrying capture start/end and target identity; Artifact bundling across Safari tabs, files, and terminal output; A durable handoff document destination and completion notification


## Changes it proposed to its own stack

### `context` — Add a cross-surface ‘state capsule’ generated at the end of every voice task: a compact, encrypted record containing the owner’s original utterance, interpreted constraints, selected targets, action IDs, receipts, unresolved assumptions, and the owner’s later correction. The relay should inject only the capsule relevant to a follow-up reference (“that tab”, “the version before you changed it”), rather than replaying the entire conversation.
- **owner gets:** The owner could speak naturally across hours and refer to prior work without repeating names, URLs, or constraints. It would also let the system notice when it misunderstood and avoid repeating the same mistake.
- effort: High: schema and retention policy in the relay, receipt correlation in Mac/browser agents, encrypted durable storage, and a relevance resolver in the realtime path.  ·  risk: Bad entity resolution could attach a new command to the wrong prior task. Mitigate with confidence thresholds and a short spoken disambiguation only when references collide; capsules must expire and support deletion.
- cost: Small storage cost; roughly 1–3 KB of structured context per completed task. Model cost decreases over time because only a selected capsule is resent instead of full history.  ·  latency: Adds approximately 50–200 ms for capsule lookup; no model call is needed for unambiguous IDs.
- security: Capsules may contain sensitive URLs, filenames, and action details. Encrypt at rest, isolate by owner/session, redact secrets from receipts, and expose a spoken “forget that task” operation.
- depends on: A durable relay-side task/receipt index linking /plan, /execute, and /jobs/:jobId; Typed entity references emitted by Mac and browser action results; A bounded context-selection routine in relay-realtime


## What it asked for

_Nothing._
