# Harness derivation — faculty-action — round 137

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “save this page for later” while wearing the pendant, capture the exact current Safari tab (URL, title, selected text or relevant page excerpt, and timestamp), file it into my AI-Pendant-Workspace with a short note, and create a reminder only if I ask; tell me what was saved on the pendant."
- **useful because:** It turns a fleeting thought while away from the keyboard into a sourced, retrievable artifact. The pendant supplies intent and confirmation, Safari supplies the private logged-in page, and the Mac supplies durable storage; none alone can preserve the exact private context reliably.
- **path:** relay-realtime → pendant → browser-extension → mac-planner → mac-terminal
- **model tier:** background for extraction and filing; realtime only for the short spoken acknowledgement
- **latency:** Acknowledge intent under 1 second; capture and file within 10 seconds.
- **cost:** Usually one small planner call plus local AppleScript/file operations; roughly $0.01–$0.05, dominated by page extraction summarization.
- **security:** Private page contents leave Safari only to the local Mac agent and relay model if summarization is needed. Never transmit passwords or hidden form fields; require confirmation before creating any reminder or sharing the artifact.
- **missing:** A browser command that returns the active tab's selected text plus a bounded cited excerpt; A typed save-page artifact route linking tab provenance to a workspace file; A pendant delivery/ack event for the saved receipt

### "When a meeting is about to start, quietly prepare the room across my devices: open the meeting link in the existing browser session, set the Mac audio output to the configured bridge, and give the pendant a discreet ready cue; if the link or audio device is unavailable, tell me exactly which step failed instead of improvising."
- **useful because:** The owner gets a reliable physical-to-digital transition rather than a calendar reminder they must execute manually. The Mac can reach the meeting and audio, the browser holds authentication, and the pendant is the only surface that can signal readiness without a screen.
- **path:** relay-realtime → mac-planner → browser-extension → pendant → mac-vision
- **model tier:** background/scheduled cheap model for event preparation; realtime only for exceptions or owner questions
- **latency:** Start preparation 2 minutes before the event; ready cue within 15 seconds of the trigger; failure report within 5 seconds.
- **cost:** Mostly local actions and one calendar/link resolver call; approximately $0.01–$0.03 per meeting.
- **security:** Opening a meeting link is reversible but may expose presence to the service; never join, unmute, enable camera, or send messages automatically. Audio routing must be allowlisted. Require explicit confirmation to join if the platform would enter the call.
- **missing:** A calendar-event trigger routed to an action lease; A bridge-device selector and verification step for audio output; A local pendant ready/failure cue protocol

### "When I walk away from my Mac wearing the pendant, automatically enter a privacy state: lock the Mac, pause browser work, and suppress private notifications; when I return, restore the exact safe workspace and give me a discreet pendant cue, but never unlock the Mac or expose private content without my deliberate confirmation."
- **useful because:** The owner gets physical, context-aware privacy without remembering to lock or reconstruct work. The pendant is the proximity/presence token, the Mac enforces local protection, and the browser pauses authenticated activity.
- **path:** pendant → mac-planner → browser-extension → relay-realtime
- **model tier:** Local deterministic rules; no expensive model unless reconstructing a damaged workspace.
- **latency:** Lock and pause within 2 seconds of separation; restore a safe workspace within 10 seconds of return.
- **cost:** Near-zero API cost; local state machine and Mac/browser operations dominate.
- **security:** Presence must not become an unlock credential. Use cryptographic session binding, lock on uncertainty, redact notifications, and require a deliberate local or pendant-confirmed action after macOS authentication to reveal private work.
- **missing:** Reliable pendant proximity/presence events over USB/BLE/LTE; A Mac lock-and-notification-suppression adapter; Browser pause/resume with authenticated-session privacy guarantees; A safe workspace snapshot and restoration manifest

### "Let me say “put this on my desk” about a document, webpage, or generated briefing, and have the system produce a physical handoff packet: print it to my selected printer or stage it in a named folder, put a short spoken index on the pendant, and retain a chain linking the artifact back to its source and the action that created it."
- **useful because:** It bridges the digital assistant to a physical workflow the owner can actually pick up, annotate, or carry. The browser can provide private source material, the Mac can render and print, and the pendant can identify the packet without opening a screen.
- **path:** relay-realtime → browser-extension → mac-planner → mac-terminal → pendant
- **model tier:** Background model for layout and concise indexing; realtime only for the request and completion acknowledgement.
- **latency:** Stage a digital packet within 15 seconds; printing is reported asynchronously with printer status.
- **cost:** Local rendering/printing costs almost nothing; optional summarization is about $0.01–$0.05.
- **security:** Private pages may be printed where others can see them. Require printer allowlists, show the destination and sensitivity before printing, never print passwords or hidden fields, and retain provenance without retaining unnecessary page contents.
- **missing:** A printer/file destination capability with status and cancellation; A provenance-preserving artifact renderer; A pendant queue/index playback protocol; A policy deciding which private content may leave the screen


## Changes it proposed to its own stack

### `integration` — Add a cross-surface action lease with a visible two-phase state machine: faculty-judgement issues an intent with expiry and required proof; faculty-action executes only reversible preparation steps, records per-step receipts, and sends a compact success/failure cue to the pendant. If the browser heartbeat, Mac bridge, or audio bridge disappears, the lease pauses and resumes from the last proven step rather than replaying earlier steps.
- **owner gets:** Long-running requests stop becoming mysterious partial failures. The owner can leave the Mac, return later, and know whether the real-world preparation happened, without duplicate browser navigation or accidental repeated actions.
- effort: Medium-high: shared lease schema, idempotency keys, step proofs, relay persistence, Mac/browser adapters, and pendant cue encoding.  ·  risk: A stale lease could suppress a needed action or resume against changed page state; expire leases aggressively, require fresh tab/session fingerprints, and expose undo/cancel. Recovery is a human-readable receipt showing the exact last proven step.
- cost: Negligible storage and local compute; background orchestration adds roughly $0.01 per multi-step job, with model cost only for ambiguous recovery.  ·  latency: Adds milliseconds per local step and up to one heartbeat interval on reconnect; avoids much larger retries and duplicate work.
- security: Improves safety by preventing replay, but lease tokens become control credentials; scope them to one job, bind to device/session, and never include page secrets in receipts.
- depends on: A durable browser job runner (chg-16bc5dee); Receipt/undo foundation (chg-5fc73ce3); A physical confirmation or cue protocol for the pendant; A typed browser provenance result (chg-14accc01)

### `new-surface` — Add a physical-world handoff surface: a small local service that accepts a typed artifact manifest from faculty-action, renders documents or cited web extracts, submits them to an allowlisted printer or removable-workspace folder, monitors completion, and returns a signed receipt that the pendant can announce. Include cancellation before printer submission and a visible sensitivity label on every packet.
- **owner gets:** The assistant can finish tasks in the physical world instead of stopping at a file or screen. The owner receives something tangible with trustworthy source labeling and can cancel a mistaken handoff.
- effort: High: renderer, printer discovery/status, local permissions, provenance labels, queue management, cancellation, and pendant receipt delivery.  ·  risk: Misprinting confidential material, paper waste, or a stale source being handed off. Default to staging rather than printing, expire manifests, require confirmation for sensitive destinations, and keep an undoable local copy.
- cost: No model cost for plain files; modest local CPU and printer consumables. Optional layout/summarization adds roughly $0.02 per packet.  ·  latency: Digital staging under 15 seconds; printer latency varies from seconds to minutes and must be asynchronous.
- security: Introduces a new data-exfiltration surface. Enforce destination allowlists, local-only rendering by default, sensitivity classification, signed manifests, and audit logs with content hashes rather than raw private text.
- depends on: A provenance-aware artifact model; A local printer/file handoff service; Pendant delivery and receipt protocol; Owner-configured destination and sensitivity policy


## What it asked for

_Nothing._
