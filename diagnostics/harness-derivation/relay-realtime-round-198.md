# Harness derivation — relay-realtime — round 198

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "What’s going on right now?"
- **useful because:** Gives a quick situational awareness snapshot: recent job outcomes, anything waiting for the owner, and current Mac status, without making them check multiple places.
- **path:** relay → mac-bridge → pendant
- **model tier:** Realtime to orchestrate the conversation; cheaper tier to fetch and summarize logs and status.
- **latency:** Under 2 seconds for a spoken summary; longer details only if the owner asks for more.
- **cost:** Low; dominated by reading job status and device state, not generation.
- **security:** Summaries may reveal sensitive task names or app titles. Keep it minimal by default and only expand when asked.
- **missing:** A consistent event log view that merges job outcomes and alert inbox state; A standard summary format sized for pendant speech

### "Record these steps as a routine and run it later."
- **useful because:** Lets the owner turn a one-off voice-guided workflow into a reusable tool, so the system gets more useful over time with less repeated planning.
- **path:** relay → mac-bridge → browser
- **model tier:** Realtime for capturing intent and naming; mac-planner for turning steps into actions; reuse routine storage on the Mac side.
- **latency:** A few seconds to capture and confirm the routine name; execution later depends on the workflow.
- **cost:** Moderate when capturing multi-step flows; cheap to run once saved.
- **security:** Routines could encode sensitive accounts or URLs. Store minimal parameters and avoid embedding secrets.
- **missing:** A capture mode that records successful action sequences into a routine template; A confirmation UI/voice flow to name and store the routine

### "I meant the other thing — show me the options."
- **useful because:** Reduces misfires when a short utterance matches multiple intents. The owner can choose quickly by voice, avoiding unintended actions.
- **path:** relay → mac-bridge → browser
- **model tier:** Realtime to present options; mac-planner to propose candidate plans; cheaper tier for ranking.
- **latency:** Under 1.5 seconds to present 2–3 choices; longer only if the owner asks for details.
- **cost:** Low to moderate; cost is in generating candidate plans, not speaking.
- **security:** Showing options can leak context (like open tabs). Keep descriptions generic unless the owner asks for specifics.
- **missing:** A disambiguation contract that returns ranked candidate plans with short labels; A voice-safe selection mechanism that maps choice to execution

### "“Make this ready for me” — use whatever I’m currently looking at on my Mac or in my authenticated browser, identify the next concrete preparation steps, do them, and tell me exactly what is ready and what still needs my eyes."
- **useful because:** The owner can issue one natural command while away from the desk and have the wearable, relay, Mac planner, and authenticated browser collaborate around the actual current work context instead of requiring them to name apps, tabs, and action sequences.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension
- **model tier:** Realtime relay for intent capture and a short spoken acknowledgement; mac-planner for planning; mac-vision for visual state; browser-extension for authenticated pages; cheaper background model for summarizing receipts.
- **latency:** Acknowledge within 1 second; begin work within 5 seconds; completion may take 30–120 seconds, with a short spoken result and durable event when finished.
- **cost:** Roughly $0.02–$0.10 per invocation, dominated by Mac-planner/computer-use turns and screenshots; relay speech turn is a small fraction.
- **security:** Authenticated page contents and screenshots leave the Mac only to the relay/model path. Actions may edit external work. Owner policy permits trusted execution, but receipts must identify every mutation and distinguish completed from merely prepared.
- **missing:** A context snapshot endpoint that atomically captures active Mac app, browser tab, selection, and pending relay jobs; A planner contract for prepare-versus-submit boundaries; A verified multi-surface receipt that joins Mac and browser evidence

### "“Find the source of this problem and fix it” — correlate what I say on the pendant with current device health, relay pipeline state, Mac logs, and the browser state, then apply the smallest repair and explain the evidence."
- **useful because:** Today the owner has to know whether a failure is audio, transport, relay, Mac, or browser. This would turn the wearable into a genuine end-to-end troubleshooter that can diagnose across physical and software boundaries and recover without a desk session.
- **path:** pendant → relay → mac-terminal → mac-planner → browser-extension → dashboard
- **model tier:** Faculty-perception or a cheap diagnostic model gathers structured observations; faculty-judgement selects a repair; mac-terminal/mac-planner executes; realtime relay only conducts the conversation and speaks the diagnosis.
- **latency:** Initial diagnosis in 5–10 seconds; reversible repair within 30 seconds; if uncertain, speak the top two causes rather than pretending certainty.
- **cost:** About $0.01–$0.08, dominated by log/context collection and any Mac planner turn; no recurring cost for the physical health fields.
- **security:** Logs can contain transcripts, URLs, and tokens; redact secrets before model exposure. Repairs must be limited to reversible changes or clearly report when a restart/configuration mutation was made. Never claim hardware health from stale last-seen data.
- **missing:** A single correlation ID propagated from pendant audio through pipeline, Mac action, and browser command; Read-only diagnostic adapters for USB pendant/ESP32 serial and Mac/browser telemetry; A repair playbook with measured post-fix verification, not model confidence alone

### "“Keep an eye on the thing I just asked you to change, and interrupt me only if it becomes unsafe, regresses, or needs a decision.”"
- **useful because:** Long-running work currently ends at a queued job or a spoken completion; the owner cannot delegate judgment over the interval. This creates a useful human-in-the-loop mode: the system proceeds autonomously, but the pendant becomes an exception channel instead of requiring polling.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Cheap background worker evaluates periodic job evidence against an explicit success/risk predicate; realtime relay is used only for an actual exception or final concise result.
- **latency:** No owner-visible delay for routine progress; exception delivery target under 5 seconds after detection; retain the exception until the owner acknowledges it.
- **cost:** Approximately $0.01–$0.05 per monitored job, primarily periodic evidence checks; idle monitoring should use Durable Object alarms or queue workers rather than realtime inference.
- **security:** The monitor must not silently broaden the original objective. Store the exact scope, stop conditions, and evidence. Browser pages may contain private data. A needs_attention event should state the concrete decision and offer pause/continue, not fabricate approval.
- **missing:** A real durable monitor with alarms/queue workers (none exists today); A job scope and stop-condition schema persisted with the job; A resumable pause/continue protocol across Mac planner, browser extension, relay, and pendant inbox; A verified event delivery path to the worn device, including the currently absent pendant registration/pairing


## Changes it proposed to its own stack

### `relay` — Add a USB-tethered pendant session broker: the Mac bridge registers the nRF9160 and ESP32 serial identities with a short-lived device lease, forwards button/audio/status frames to the relay using the same session identity as LTE would, and exposes a pairing receipt plus last-seen/ack counters. When LTE registration later exists, the relay must reconcile the USB and LTE transports into one device identity rather than creating a second pendant.
- **owner gets:** The owner can wear and test the real pendant today while it is attached to the Mac, hear replies, and receive queued events; they no longer get a false “Mac is online but no pendant exists” state or have to debug device registration before every test.
- effort: Medium: bridge-side serial framing and identity handshake, relay lease/reconciliation route, device inventory update, and an end-to-end hardware test. No new model work is required.  ·  risk: A stale USB lease could make the relay report a device as alive after unplugging, or duplicate audio/events when LTE and USB overlap. Use explicit lease expiry, transport sequence numbers, and deduplication; recover by dropping the lease and re-pairing.
- cost: Negligible API cost; approximately 1–2 engineering weeks. No hardware purchase; uses the already-connected nRF9160 and ESP32 USB serial links.  ·  latency: Adds under 100 ms for serial forwarding and removes manual registration delays; event delivery becomes possible during tethered tests.
- security: Pairing must require a physical button gesture or one-time USB challenge and bind the lease to the Mac bridge identity. Do not expose raw serial control to unauthenticated callers.
- depends on: A real relay device-registration/announce endpoint (the current inventory does not expose one to this agent); Mac bridge access to both /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; A common event sequence/ack schema shared by USB and LTE transports


## What it asked for

_Nothing._
## Its own summary

Recorded four owner-facing proposals: a cross-surface “make this ready” command, evidence-backed end-to-end troubleshooting, exception-only monitoring with durable follow-up, and a USB-tethered pendant session broker so the live hardware can work today. The most useful is the first: one spoken request that coordinates current Mac context, authenticated browser state, planner execution, and wearable feedback. The proposals explicitly require missing connective pieces rather than pretending existing routes already provide them.

**Biggest unknown:** The exact production pendant registration/pairing contract and whether the relay can currently accept a USB-bridged device identity. That determines how quickly the physically connected hardware can become a usable spoken endpoint.

