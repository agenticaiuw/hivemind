# Harness derivation — relay-realtime — round 200

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If I say a command and the Mac is asleep, queue it and do it when the Mac comes back."
- **useful because:** The owner is often away from the Mac. Queuing turns failures into eventual success without needing them to repeat themselves.
- **path:** relay → mac-bridge → mac-planner
- **model tier:** Realtime to capture intent; cheaper planner to execute when available.
- **latency:** Immediate confirmation of queuing; execution whenever the Mac reconnects.
- **cost:** Mostly storage and a retry loop; minimal compute per queued job.
- **security:** Queued actions must be auditable and reversible where possible. Avoid queuing destructive actions without explicit confirmation.
- **missing:** A durable job queue at the relay (not just in-memory); Reconnect trigger from mac-bridge to drain the queue; Idempotency keys to prevent double execution; A policy for which actions are reversible and which require confirmation

### "When I say “take care of this” while I’m away from my Mac, use the pendant’s captured utterance plus the Mac’s current screen and authenticated browser context to complete the smallest safe interpretation, then tell me exactly what changed and let me undo it by voice."
- **useful because:** This is the core hive-mind experience: the pendant supplies intent and physical presence, the relay preserves the handoff, and the Mac/browser supply context and reach. Today the owner must spell out app, page, and steps, and cannot reliably resume an interrupted handoff.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension
- **model tier:** Realtime relay for a one-sentence clarification and acknowledgement; mac-planner for planning; mac-vision/browser harness for observing the live UI; background worker for execution receipts and undo window.
- **latency:** Acknowledge in under 1 second; first context-grounded question in under 5 seconds; completion can take minutes with a spoken or queued result.
- **cost:** About $0.01–$0.08 per handoff, dominated by planner calls and any vision frames; relay speech should remain one short turn.
- **security:** Current screen contents, authenticated pages, and the owner’s utterance leave the Mac for planning. Redact secrets from screenshots, bind the handoff to the current Mac session, keep an append-only action journal, and expose a voice undo command; do not silently broaden an ambiguous request.
- **missing:** A cross-surface handoff capsule with correlation ID, context snapshot, clarification state, and resumable execution; Mac vision loop enabled and able to return structured observations; A durable undoable action journal and relay-side clarification delivery

### "Read the important parts of the page I’m looking at into my ear, in short sections; pause when I press the pendant, remember the exact paragraph, and continue when I press again—even if the page is behind my authenticated browser session."
- **useful because:** The owner can consume a private webpage hands-free while walking, without asking the relay to dump an entire page or losing their place. The pendant’s existing interrupt gesture and 24 kHz downlink make this materially better than a generic text summary.
- **path:** pendant → relay → browser-extension → mac-planner
- **model tier:** Browser extraction and section ranking on a cheaper background model; realtime relay only manages turn-taking, interruption, and concise spoken delivery; local browser agent retains the page and selection state.
- **latency:** First 2–3 sentence section within 3 seconds of the request; pause/resume acknowledgement under 300 ms; later sections may be prefetched.
- **cost:** Roughly $0.005–$0.03 per section, dominated by authenticated-page extraction and speech generation; prefetching should be capped.
- **security:** Never send page contents to an untrusted cloud browser; extraction stays on the Mac/browser session and only selected text is sent for speech. Do not persist page text after the turn; bind resume tokens to the browser session and expire them.
- **missing:** A browser action that returns semantic sections plus stable paragraph IDs instead of a raw page dump; A relay audio playlist/cursor protocol supporting pause, resume, and cancellation at packet boundaries; A session-scoped encrypted cursor store shared by browser and pendant

### "While I’m in a meeting at my Mac, let me press the pendant to hear a private, rolling one-sentence summary of what has just been said, and let me ask “what was the decision?” or “what do I owe?” without interrupting the meeting audio for anyone else."
- **useful because:** The owner gets an unobtrusive second channel: the pendant can answer a clarification or recover a missed decision without announcing an assistant in the room. This requires the worn device, Mac-local audio, relay turn-taking, and speech generation together; none of those surfaces alone can provide it.
- **path:** pendant → mac-planner → mac-vision → relay → browser-extension
- **model tier:** Mac-local speech capture/transcription and a cheap rolling summarizer; realtime relay only handles the owner’s short query and delivers a tightly bounded answer; use a stronger model only for ambiguity around decisions or owners.
- **latency:** Rolling summaries every 10–20 seconds; a query answer within 2 seconds after the owner releases the button; stop all capture immediately on button release.
- **cost:** Approximately $0.02–$0.12 per meeting hour depending on local versus hosted transcription; the dominant cost is continuous transcription, so local capture and periodic compact deltas are essential.
- **security:** Meeting audio is extremely sensitive. Capture must be physically button-gated, visibly indicated on the Mac and pendant, never retained by default, and sent off-device only as short encrypted transcript deltas needed for the current answer. Provide a hard disconnect and automatic expiry at meeting end.
- **missing:** A Mac-local meeting-audio capture and transcription surface with explicit consent lifecycle; A low-latency rolling-summary state machine that retains only bounded deltas; A private pendant query channel that can interrupt summary playback without stopping capture


## Changes it proposed to its own stack

### `hardware` — Add a tiny coin vibration motor (or linear resonant actuator) with a dedicated low-side driver and one firmware PWM/GPIO, while keeping the existing LED and button. Define three tactile patterns: queued reply, clarification needed, and task complete/failed. The relay should be able to request a pattern even when the speaker is busy or muted.
- **owner gets:** The owner can feel that a reply, question, or failed task is waiting without staring at the single LED or wearing headphones. This makes asynchronous Mac/browser work discoverable in the real world rather than silently stranded.
- effort: Mechanical re-spin or a small pendant revision, driver transistor/MOSFET, firmware pattern scheduler, and relay event mapping; validate vibration strength through clothing and battery impact.  ·  risk: Added vibration could annoy or wake the owner, and a stuck GPIO could drain the battery. Use a hard maximum pulse duration, watchdog shutdown, and a physical disable setting; retain LED/audio fallbacks. Recovered units can boot with the motor disabled if self-test fails.
- cost: Approximately $0.50–$2 in components and assembly, plus a few mA only during pulses; negligible idle draw if the driver is off.  ·  latency: Sub-100 ms tactile notification once the relay event reaches the device; no effect on audio codec latency.
- security: No new data exposure. Patterns must not encode sensitive content—only urgency/type—and should be suppressed for private notifications when configured.
- depends on: A real relay-to-pendant asynchronous event delivery path; Firmware event queue integration with the existing inbox and one-LED state machine; A battery/EMI validation pass


## What it asked for

_Nothing._
## Its own summary

Recorded four proposals: a context-grounded “take care of this” handoff, resumable private browser page reading, a button-gated private meeting sidecar, and a haptic notification upgrade. The owner still cannot have these today because the relay lacks a durable cross-surface handoff/cursor protocol, the Mac vision loop and local meeting-audio capture are unavailable, browser extraction has no semantic cursor, asynchronous event delivery is not live, and the pendant has no tactile actuator. The most valuable is the first: intent from the worn pendant plus current Mac/browser context, resumable execution, truthful receipt, and voice undo.

**Biggest unknown:** Which already-recorded backlog items implement or overlap the proposed handoff, page cursor, meeting sidecar, and haptic actuator; the recorder accepted all four but flagged each as adjacent, so they should be checked against the backlog before engineering starts.

