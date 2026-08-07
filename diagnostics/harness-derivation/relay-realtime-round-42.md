# Harness derivation — relay-realtime — round 42

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Pause whatever you are doing on my Mac or in my authenticated browser, tell me exactly what has already happened and what remains, then resume it later from that checkpoint when I say continue."
- **useful because:** The owner is usually away from the Mac and cannot safely inspect a half-finished workflow. A spoken pause with a durable, redacted checkpoint prevents duplicate submissions or lost browser context, while explicit resume lets work continue without rebuilding the task from memory. This is a genuine pendant–relay–Mac–browser capability rather than a Mac-only feature.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Realtime handles only the short pause/resume utterance and the spoken receipt; a cheaper background planner serializes the checkpoint and reconstructs the next action. Mac-planner or browser-extension performs the actual continuation; faculty-perception verifies the observed state before resuming.
- **latency:** A pause acknowledgement and redacted receipt should reach the pendant in under 2 seconds; checkpoint capture may take up to 10 seconds. Resume can acknowledge immediately and report progress asynchronously, with spoken completion when the downstream agent finishes.
- **cost:** About $0.01–$0.05 per pause/resume exchange depending on whether state needs model summarization; most cost is one planner call, not realtime speech. Storage and transport are negligible.
- **security:** Checkpoints may contain authenticated page titles, typed text, or private app state. Persist only a redacted action log plus opaque session references, encrypt it, and never echo secrets through speech. Resume must be bound to the original Mac/browser session and detect changed page/application state; on mismatch it should report and stop rather than guessing. Pausing is an owner-directed control, not an approval gate.
- **missing:** A first-class pause/cancel/resume protocol shared by relay, Mac planner, computer-use loop, and browser extension, with job-scoped checkpoints and idempotency keys; Mac and browser adapters that can quiesce safely at action boundaries and report an observed checkpoint; Durable encrypted checkpoint storage and expiry on the relay; Pendant event transport for a short pause receipt and later completion/progress push; Faculty-action integration that treats resume as an explicit command while preserving the owner's no-confirmation policy for ordinary reversible actions

### "What changed on my Mac and in my open browser sessions since I left, and is anything waiting for me?"
- **useful because:** Because the pendant is worn away from the computer, the owner currently returns to an opaque machine state. A departure baseline and a spoken delta would expose new files, app changes, browser navigation, downloads, and completed/failed delegated work without requiring the owner to remember what was open. It combines wearable presence, always-on relay memory, Mac observation, and authenticated browser state.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement
- **model tier:** A cheap background comparator computes typed diffs and filters noise; realtime only answers the short question and reads a concise prioritized summary. Faculty-perception gathers evidence, while faculty-judgement ranks items as waiting, changed, or irrelevant.
- **latency:** Departure snapshot should finish within 15 seconds of the pendant becoming unreachable; a later spoken query should return an initial answer within 2 seconds and stream or follow with details within 10 seconds.
- **cost:** Roughly $0.005–$0.03 per query; storage and comparison dominate little, and model cost is limited to ranking a compact diff rather than replaying full Mac/browser context.
- **security:** The snapshot must not collect page bodies, keystrokes, or secrets by default. Store hashes, app/window metadata, file paths subject to redaction, browser tab identity, and action receipts with encrypted retention and owner-configurable expiry. Authenticated browser contents should be fetched only when the owner asks for a specific item. Detect shared/public machines and avoid speaking sensitive titles aloud unless requested.
- **missing:** A pendant-presence/departure event and reliable reconnect marker (not merely polling); A privacy-preserving baseline/delta schema spanning Mac filesystem/app state, browser tabs, and relay jobs; Mac and browser observers that emit typed changes with timestamps and provenance; A durable encrypted snapshot store with retention and redaction controls; A prioritization and spoken-summary path that can cite the underlying evidence and distinguish owner actions from automated actions


## Changes it proposed to its own stack

### `interaction` — Add a relay-to-pendant confirmation/pause interface: a small, explicit transport for the relay to push a “pause/confirm” event to the wearable and receive either a button press or voice confirmation, with a short timeout and a redacted summary string intended for the speaker.
- **owner gets:** It lets the system safely interrupt or pause an in-flight multi-surface action when the owner is wearing the pendant and the Mac is unattended, without inventing ad-hoc phrasing or requiring the owner to be at the computer.
- effort: Medium. Needs a defined event schema, a relay endpoint to emit it, and a device skill to handle it and report back.  ·  risk: If the link is flaky, confirmations could be missed. Mitigate with timeout, retry, and a clear fallback spoken response. Avoid sensitive content in the prompt by redacting details.
- cost: Low API cost per event; most cost is the relay invocation and the device round trip.  ·  latency: Adds a small delay only for actions requiring confirmation; otherwise no change.
- security: Moderate. Must treat the event as untrusted on-device, authenticate server-to-device messages, and keep the spoken summary redacted.
- depends on: A device skill to receive pause/confirm events and return button/voice response.; A relay route for emitting the event and correlating responses.


## What it asked for

_Nothing._
