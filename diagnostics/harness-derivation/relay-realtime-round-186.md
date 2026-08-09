# Harness derivation — relay-realtime — round 186

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Start this job on my Mac and browser, and if it reaches a real ambiguity, ask me one precise question through the pendant; use my answer to continue without restarting or losing the authenticated session."
- **useful because:** Long computer tasks fail today at the first ambiguous dialog or missing choice. This would let the owner leave the Mac and still resolve only the decisions that genuinely require them, while preserving browser state and producing one coherent result rather than a dead job or a guessed action.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension
- **model tier:** Realtime relay for the one short clarification exchange; mac-planner for orchestration; mac-vision/browser-extension for execution and evidence extraction.
- **latency:** Immediate acknowledgement under 1 second; clarification prompt within 5 seconds of a blocker; resume within 10 seconds of the owner's answer.
- **cost:** About $0.01-$0.08 per task depending on planner turns; the dominant cost is vision/planner retries, not the short relay utterances.
- **security:** The relay must send only the blocker and minimal options, never arbitrary page contents. The owner answer is bound to the exact job, step, and browser session, with expiry and a visible receipt so a stale answer cannot affect a later task. No automatic choice should be made when the blocker is consequential.
- **missing:** A durable clarification state machine that pauses an executing Mac/browser job and binds a single pendant answer to its step; A relay-to-pendant downlink prompt and answer endpoint that works after the original voice turn; Mac planner support for resumable checkpoints rather than terminal success/failure; A browser-session evidence envelope identifying the tab and URL at the blocker

### "I think someone may have access to my computer. From the pendant, put the Mac into a privacy posture, stop any active browser automation, and tell me exactly what was changed and what remains open."
- **useful because:** A worn button is the only control surface the owner can reach when away from the desk. Today the relay can start work, but there is no single cross-surface response to a suspected compromise. This gives the owner a fast, understandable incident response instead of needing to find the Mac or remember several commands.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension
- **model tier:** Realtime relay interprets the short emergency utterance; a deterministic Mac action bundle performs the response; the planner/vision tiers only inspect and report residual state.
- **latency:** Acknowledge immediately; issue lock/stop actions within 2 seconds when the Mac is online; speak a bounded outcome within 8 seconds.
- **cost:** Under $0.01 for the deterministic path; inspection and receipt generation dominate if the owner requests details.
- **security:** This must not claim protection if the Mac is offline. It should stop relay-originated jobs, close or freeze extension control, lock the Mac, mute active audio, and record a tamper-evident receipt; destructive tab closure or credential revocation should be separately requested. The pendant command needs replay protection and a distinct emergency utterance/button gesture.
- **missing:** A relay emergency-control endpoint that cancels queued/in-flight jobs and broadcasts a stop token; An idempotent Mac privacy action bundle (lock, mute, halt automation, freeze browser command intake) with honest per-action receipts; A pendant emergency gesture and offline LED acknowledgement; A browser extension kill-switch that refuses new commands until explicitly resumed

### "Give me a spoken 'since last check-in' that combines what changed in my Mac project, authenticated browser work, and relay tasks, with links or names I can ask you to open next."
- **useful because:** The owner is often away from the Mac and currently has to remember which surface changed what. A cross-surface delta, grounded in actual receipts rather than a generic summary, turns the pendant into a trustworthy return point after an interruption or a day away.
- **path:** pendant → relay → mac-planner → browser-extension → mac-vision
- **model tier:** A cheap background summarizer builds the delta from structured receipts; realtime only compresses it into speech and handles a follow-up such as 'open the second item'.
- **latency:** Precompute on each completed job or check-in; spoken response under 3 seconds, with a two-sentence default and on-demand expansion.
- **cost:** Roughly $0.005-$0.03 per delta; storage/indexing is negligible, while summarization of page diffs is the main cost.
- **security:** Authenticated browser content must remain on the relay or be reduced to user-approved metadata; do not read an entire portal aloud in a public setting. Every item needs source, timestamp, and confidence, and unchanged items must be excluded to prevent false novelty.
- **missing:** A per-owner checkpoint cursor spanning Mac receipts, browser inspections, and relay jobs; Structured before/after snapshots for files, app state, and browser pages instead of opaque action logs; A redaction/classification pass for sensitive browser content before persistence or speech; A pendant query that can select an item and route it back to the originating surface

### "Let me walk from outside LTE coverage to my Mac without losing the conversation: when I plug in the pendant, move the live voice session and its pending task to the USB-connected Mac/audio bridge, then move it back when I leave."
- **useful because:** The owner currently has two disconnected realities: the pendant is useful while worn, while the physically connected hardware is testable at the Mac. A session handoff would make one continuous assistant instead of forcing the owner to repeat context, restart audio, or abandon a task at the doorway.
- **path:** pendant → relay → mac-planner → mac-vision
- **model tier:** Realtime relay maintains the conversational session and selects the active transport; a deterministic handoff coordinator moves audio and job ownership; planner/vision continue the task without re-planning.
- **latency:** Detect USB attach or LTE loss within 2 seconds; freeze and resume audio in under 1 second with no duplicate command; preserve the last 30 seconds of transcript/context.
- **cost:** Under $0.02 per handoff; protocol work and short-lived session state dominate, not inference.
- **security:** Authenticate the exact USB serial device before treating it as the owner's local endpoint. Never expose a live session to an arbitrary Mac; revoke the old transport on handoff, sequence audio frames, and make command submission idempotent so reconnects cannot repeat an action.
- **missing:** A pendant/relay transport registry that recognizes the live nRF9160 and ESP32 USB serial pair; A session migration protocol with epoch, frame sequence, transcript cursor, and idempotent command ownership; Mac-side USB audio/serial adapter that can join an existing relay session rather than starting a new one; Explicit LTE-to-USB and USB-to-LTE transition signals in the firmware and relay


## What it asked for

_Nothing._
## Its own summary

Recorded four owner-facing capabilities: resumable pendant clarification checkpoints for Mac/browser jobs; a spoken emergency privacy/containment command; a cross-surface 'since last check-in' delta; and seamless live-session handoff between LTE pendant use and the USB-connected Mac/audio hardware. The first three are intentionally differentiated from completion notifications: they require pausing at a decision, active containment, and source-grounded change detection respectively.

**Biggest unknown:** The relay's complete live route inventory and the actual USB serial session/audio handoff contract are still not exposed to this agent. To ship these, the system needs durable cross-surface state, explicit device/session identity, resumable job checkpoints, and honest receipts—not another spoken wrapper around existing /plan or /execute.

