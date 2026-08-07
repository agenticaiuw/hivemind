# Harness derivation — relay-realtime — round 40

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Handle this while I’m away, and only interrupt me if it becomes urgent; otherwise give me a short spoken result when it’s finished.” The pendant should accept a goal, let me continue walking, and later tell me the outcome without my having to ask what happened."
- **useful because:** Today delegation and status are pull-based and the wearable is usually away from the Mac. This gives the owner a true away-from-desk return channel: immediate acknowledgement, execution across the Mac and authenticated browser, urgency-aware interruption, and a concise voice completion. It is specifically useful when the owner cannot keep a screen open or remember to poll a job.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime handles only the initial utterance, acknowledgement, and final spoken rendering. A cheaper background planner performs the Mac/browser work and a small classifier determines whether an intermediate event meets the owner's stated interruption threshold.
- **latency:** Acknowledge on the pendant within 1–2 seconds. Start downstream work immediately when a surface is available. Deliver a completion or urgent interruption within 5 seconds of the downstream receipt; otherwise retain it until the next uplink.
- **cost:** One realtime turn for intake and one short realtime turn for the result; background planning and event classification dominate volume and should use the cheaper tier. Roughly $0.01–$0.05 per ordinary delegation, depending on browser/page content and retries.
- **security:** The goal may authorize actions in authenticated Mac/browser sessions, so the task envelope must bind to the owner, target surface, and expiry, and completion audio must not expose sensitive page contents in public settings. Intermediate evidence should stay on the relay/Mac unless needed for the spoken result. The owner has requested no confirmation gates for reversible work, but destructive actions need an explicit policy field and an auditable receipt.
- **missing:** A durable cross-surface task envelope carrying the owner's interruption policy, expiry, and preferred result format; Relay-to-pendant push delivery for urgent and completed events, with retry/deduplication across LTE-M dropouts; An event callback from Mac planner/browser harnesses rather than only pull-based job status; A compact urgency/result summarizer and a per-task audio notification mode (silent, LED-only, spoken); Dashboard controls to inspect, pause, expire, or replay the task and its receipts


## Changes it proposed to its own stack

### `hardware` — Add a tiny coin haptic motor (or linear resonant actuator), dedicated low-side driver, and a firmware notification queue to the pendant. Expose three local patterns—acknowledged, urgent, and completed—with cancellation on button press. The relay should select haptic versus spoken delivery in the task envelope, and Mac/browser receipts should carry the event severity that drives the pattern.
- **owner gets:** The owner can receive an urgent result while walking, in a meeting, or somewhere speech playback would disclose private information. A single LED is easy to miss and cannot communicate urgency while the pendant is worn; discreet tactile feedback makes away-from-Mac delegation dependable rather than something the owner must poll.
- effort: Pendant PCB revision or a small add-on board, driver integration, three-pattern firmware state machine, relay push/ retry handling, and an end-to-end test from browser/Mac receipt to tactile event. No new model is required.  ·  risk: Motor noise and vibration could be distracting, and an overly strong pattern could be uncomfortable. Bound duty cycle and amplitude, default to short patterns, provide a spoken/button configuration to disable it, and fall back to LED when the driver or battery budget is low. Since there is currently no battery gauge, add current-budget telemetry or conservative fixed limits before shipping.
- cost: Approximately $1–$4 in components and minor PCB/assembly cost; roughly 10–40 mA only during a short pulse, with negligible average draw if limited to a few notifications per hour. Relay/model API cost is effectively zero.  ·  latency: Local haptic onset after a push packet is received is under 100 ms; LTE-M delivery remains the dominant latency. Queueing and deduplication avoid repeated pulses after reconnect.
- security: Improves privacy by allowing sensitive completion notices without speech. Notification payloads should contain only an opaque event id and severity; content remains on the relay until the owner explicitly asks for audio.
- depends on: A durable task event envelope with severity and delivery preference; Relay-to-pendant push delivery with retry and deduplication; A pendant power/current budget and battery telemetry path


## What it asked for

_Nothing._
