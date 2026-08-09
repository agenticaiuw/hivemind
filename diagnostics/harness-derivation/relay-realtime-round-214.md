# Harness derivation — relay-realtime — round 214

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If my Mac is online, use it to do the heavy lifting, but keep the voice interaction snappy."
- **useful because:** The owner gets fast conversational control without paying realtime costs for multi-step planning, browsing, or long workflows.
- **path:** relay → mac-bridge → browser-extension
- **model tier:** realtime to interpret and hand off; planner tier for multi-step execution
- **latency:** Under a second to acknowledge and hand off; variable for completion.
- **cost:** Dominated by Mac planning/execution; relay cost is minimal routing and status updates.
- **security:** Handing off should preserve the owner’s wording and intent; avoid expanding scope. High-impact actions should still respect existing confirmation rules.
- **missing:** A reliable, explicit relay routing tool that resolves to real action types/enums (current relay_route_intent schema is a stub); A stable way to report the chosen plan back to the relay for logging and user confirmation in complex cases

### "Run a quick pendant and bridge audio self-check over USB while I’m at my Mac, and tell me what’s broken."
- **useful because:** This is the fastest path to trust: a daily-wear device needs a one-minute confidence check that audio, decoding, and the USB chain are healthy.
- **path:** pendant → bridge → mac-bridge → relay
- **model tier:** realtime for spoken guidance; local tools or firmware for measurements
- **latency:** Under a minute end-to-end; results summarized in one sentence.
- **cost:** Low; dominated by a short capture/playback loop and metrics collection.
- **security:** Audio captured during a test could contain speech. The test should use synthetic tones/loops and avoid storing user audio.
- **missing:** A device skill to run a self-test and report measured counters (decode/encode timing, packet loss, tx_starved); A Mac-side tool to command the bridge and gather results over USB serial; A relay-visible status endpoint for the test results

### "Let me start a task on the pendant, pause it, and continue the exact same conversation on my Mac (or resume it on the pendant) without repeating myself or risking the action twice."
- **useful because:** The owner is often away from the Mac. Today a voice session and a Mac job are separate worlds: moving between them loses conversational state or invites duplicate execution. Seamless migration would make the wearable, relay, and Mac feel like one reliable assistant rather than three endpoints.
- **path:** pendant → relay → mac-planner → mac-vision → dashboard
- **model tier:** Realtime handles only the short spoken handoff and intent extraction; a cheaper background model summarizes the session and reconstructs context when the surface changes. The Mac planner remains responsible for planning and execution.
- **latency:** A handoff acknowledgement under 500 ms; migration state available within 2 s. No model call is needed for a simple resume if the prior normalized intent and job state are already stored.
- **cost:** Usually <$0.01 per migration; dominated by one small background summarization call only when the context exceeds the compact transcript/state record.
- **security:** The relay must bind a migrated session to the authenticated device/account and never expose the transcript to an unpaired surface. Every mutating action needs a stable idempotency key, with the user-visible state distinguishing planned, started, and completed rather than claiming success from a handoff.
- **missing:** A durable session-migration record containing compact transcript, normalized intent, current surface, and action idempotency keys; A Mac-to-relay session attach/resume endpoint and pendant resume handshake over the currently USB-testable and eventual LTE paths; Execution deduplication that treats a replayed action key as a status read, not a second mutation; A UI/audio cue that says which surface currently owns the turn

### "Read and summarize this authenticated page for me, but automatically hide passwords, access tokens, payment numbers, and private messages before anything leaves my browser or Mac; tell me what was redacted."
- **useful because:** The wearable makes it natural to ask about whatever is open, but sending an entire authenticated page to a model can leak secrets. The owner should get the convenience of cross-surface understanding without having to manually sanitize every page, and should receive an honest redaction notice instead of silently losing context.
- **path:** pendant → relay → browser-extension → mac-planner → mac-vision
- **model tier:** A deterministic local redaction engine (browser extension for DOM and Mac harness for screenshots/accessibility text) runs first. Realtime only speaks the request and result; a small model may classify borderline entities after local masking, never before it.
- **latency:** Mask common patterns in under 150 ms; return a spoken summary in under 3 s. If classification is uncertain, omit the span and say so rather than blocking the owner with a confirmation flow.
- **cost:** <$0.005 for an ordinary page; most requests use local regex/entity detectors. A small classification call dominates the rare ambiguous case.
- **security:** Raw page text, screenshots, and secrets must not be uploaded for classification. Redaction should happen in the extension/Mac process, with a visible count and categories of masked spans, provenance linking the answer to the sanitized snapshot, and a kill switch for pages that disallow extraction.
- **missing:** A shared DOM/accessibility/screenshot sanitization library implemented in both the browser extension and Mac harness; Secret detectors for credentials, financial identifiers, private-message blocks, and user-defined patterns, with replacement tokens preserving useful structure; A relay request contract that accepts only the sanitized artifact plus redaction manifest, never the raw page; A spoken result that reports redaction categories and a dashboard inspection view

### "Watch me perform this workflow once in my browser and Mac, then let me say “run my weekly expense check” and repeat it later, adapting to changed page layouts while telling me exactly what it did and where it stopped."
- **useful because:** The owner should not need an engineer for every personal routine. Demonstration-based teaching turns the Mac and browser agents' concrete actions into a reusable personal skill, while the relay makes that skill invokable from a worn device even when the owner is away from the desk.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** A background model converts a recorded demonstration into a parameterized workflow; mac-planner validates and executes it, and mac-vision/browser-extension supply grounded UI state. Realtime is used only for naming the skill, collecting a missing parameter, and speaking the result.
- **latency:** Start acknowledgement under 500 ms; skill compilation can take 10–30 s in the background. Each replay should stream step receipts and stop within 2 s of an unverifiable state rather than guessing.
- **cost:** About $0.03–$0.15 to compile a new workflow, dominated by screenshot/action summarization; replays cost <$0.01 plus ordinary planner inference.
- **security:** Demonstrations may contain secrets and destructive actions. Store only semantic actions and masked targets where possible, encrypt the artifact, bind it to the owner's account, and provide a dashboard diff of the planned replay. Do not silently widen a learned workflow when a page changes; report the blocked step and preserve evidence.
- **missing:** A demonstration recorder that pairs browser DOM/accessibility snapshots and Mac UI/action events with timestamps; A versioned workflow format supporting variables, assertions, retries, and explicit stop conditions rather than brittle coordinates; A compiler/evaluator that turns the recording into a planner-readable skill and tests it in dry-run mode; A skill registry, edit/delete UI, and per-run receipts linked to the originating demonstration; A relay invocation path that resolves a spoken skill name and collects only missing parameters


## Changes it proposed to its own stack

### `relay` — Add a relay /capabilities endpoint (or equivalent tool inventory) that lists shipped tools, supported delivery targets, and event delivery status. Make it the source of truth for this surface, like the Mac agent’s /capabilities.
- **owner gets:** Fewer invisible failures. If the relay advertises what it can do, the voice agent can avoid promising features that aren’t implemented and can gracefully degrade.
- effort: Medium: define a manifest, expose it via HTTP, and wire tool resolution to it.  ·  risk: The manifest could drift from implementation. Mitigate with a startup self-check that validates tool bindings and routes.
- cost: Small. One lightweight endpoint and a manifest build step.  ·  latency: Improves responsiveness by reducing trial-and-error probing.
- security: Expose only capability names and versions; avoid secrets or internal URLs.
- depends on: A manifest format and build process shared across surfaces

### `integration` — Implement job completion delivery end-to-end: job_completion_watch emits events; relay_event_push (or pipeline events) delivers to pendant/phone/dashboard; acknowledgements prevent repeats.
- **owner gets:** This is the single most useful thing for a wearable assistant: you can ask for something, walk away, and be told when it’s done.
- effort: Medium to high: eventing, persistence, and retry semantics.  ·  risk: Duplicate or lost notifications. Mitigate with idempotent event IDs and receipt tracking.
- cost: Moderate ongoing cost for watches and delivery retries.  ·  latency: No impact on live conversation; adds asynchronous delivery.
- security: Notifications may contain sensitive content; keep them short and allow opt-out per target.
- depends on: A delivery target registry (pendant/phone/dashboard) and a receipt store

### `hardware` — Add a low-profile haptic actuator and a side rotary encoder with a detent press, while retaining the existing primary voice button. The encoder would navigate/seek through a spoken response, switch between queued choices, and adjust reply verbosity; the haptic motor would provide distinct private pulses for listening, awaiting a decision, action started, and action result. Firmware should expose a small event vocabulary and preserve operation with the current single-button hardware.
- **owner gets:** The owner can control and understand the assistant discreetly in public, while walking or when speaking is awkward: turn to skip a result, press to select, or feel that a task failed without relying on the one LED or an audible interruption. This makes the pendant genuinely wearable rather than a phone microphone on a lanyard.
- effort: Medium hardware spin plus firmware input/debouncing, haptic pattern tests, enclosure and power redesign; prototype over the currently USB-connected pendant before committing to a jewellery enclosure.  ·  risk: Added controls can cause accidental commands and haptic patterns can be misunderstood. Require a deliberate detent press for mutations, keep the existing button semantics unchanged, provide a firmware-disable setting, and fall back to the current LED/button path if the new component fails.
- cost: Roughly $3–10 in prototype components/PCB changes and perhaps 5–20 mA peak during haptic/encoder activity; negligible ongoing model/API cost.  ·  latency: Local feedback under 50 ms; no network round trip for navigation or acknowledgement.
- security: No new data leaves the device. The firmware must never treat a rotation alone as authorization for a high-impact external action.
- depends on: A revised pendant PCB/enclosure with space and a power budget for the actuator and encoder; A firmware event contract consumed by the relay and alert/audio playback state machine; A haptic/gesture interaction specification tested against the existing one-button meanings


## What it asked for

_Nothing._
## Its own summary

Discovered current tools, surfaces, routes, and granted items. Proposed three capabilities: async status with completion notifications, fast relay-to-Mac handoff with clear status, and a USB audio self-test. Proposed changes: a relay capability manifest and end-to-end completion delivery. The standout capability is completion delivery after the voice session ends — it makes the pendant feel like a real assistant instead of a push-to-talk remote.

**Biggest unknown:** Which relay-side capabilities are truly implemented (job completion watch, event push, delivery targets) and how the relay can introspect its own tool inventory without probing. A relay /capabilities manifest would remove this uncertainty.

