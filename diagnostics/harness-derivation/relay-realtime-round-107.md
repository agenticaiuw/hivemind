# Harness derivation — relay-realtime — round 107

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Undo the changes you made in that last task,” or “Undo the browser and Mac changes from the email task,” spoken through the pendant."
- **useful because:** Today receipts and an undo-last endpoint exist, but the owner cannot reliably reverse one conversational task spanning Mac actions and authenticated browser commands by referring to it naturally. A causal, cross-surface rollback would let someone away from the Mac recover from an accidental or unwanted automation without finding the right app, tab, or job.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Realtime relay resolves the spoken reference and immediately reports whether a rollback is available; a cheaper background coordinator computes and executes the compensation bundle, while mac-planner/browser-extension perform their respective reversals.
- **latency:** Acknowledge in under 500 ms with the matched task and rollback scope; complete reversible actions asynchronously, with progress and final receipt delivered to the pendant/dashboard.
- **cost:** Approximately $0.01–$0.05 per rollback depending on ambiguity resolution and number of compensating actions; most cost is the background model call and per-surface execution, not the short realtime utterance.
- **security:** Rollback must be restricted to actions with recorded, tested compensations and must never claim success for an irreversible mutation. The relay should read only task metadata and receipts needed to identify the task; browser page contents and private Mac data stay on their originating surface. If multiple tasks match, speak the candidates and require a disambiguating utterance, but do not impose a blanket approval gate on already-reversible actions.
- **missing:** A durable cross-surface transaction/causal ledger linking one voice request to Mac and browser child jobs; Compensation descriptors for each reversible Mac action and browser command, including dependency order and partial-failure handling; A relay endpoint that accepts a natural-language rollback reference and returns a rollback job with live status; Pendant delivery for completion/failure notifications when the owner is no longer in the original voice turn


## Changes it proposed to its own stack

### `integration` — Add authoritative live-origin semantics shared across relay, Mac pipeline, and browser. Every event/audio chunk/observation should carry origin device id, connection epoch, monotonic sequence, and a flag indicating whether it is live, replayed, or historical. Consumers must refuse to report historical data as live unless explicitly requested.
- **owner gets:** Prevents confusing “it’s happening now” reports based on stale recordings or backfilled telemetry. The owner hears what’s truly live.
- effort: Medium to high. Requires schema updates across pipeline events, storage, and consumers, plus UI/voice wording changes.  ·  risk: Compatibility issues with existing stored events. Mitigate with migration and defaulting rules.
- cost: Low to moderate per event for extra metadata; dominated by storage and processing of telemetry already present.  ·  latency: Minimal; metadata tagging is cheap.
- security: Improves traceability. Needs careful handling of identifiers to avoid leaking sensitive device info.
- depends on: Shared observation/event schema across relay and Mac; Downstream enforcement in perception layer

### `hardware` — Add a low-power vibration motor and a simple haptic driver to the pendant, paired with a firmware notification queue. Define three short patterns (job completed, job failed/needs attention, and connection lost/recovered), with deduplication and a physical-button acknowledgment; the relay emits notifications when Mac/browser jobs finish even if the voice turn is over.
- **owner gets:** The owner wears the pendant away from the Mac and currently has only one LED and one button, so work handed to another surface can finish invisibly. A private tactile cue lets them know when to speak for the result without staring at a screen or exposing sensitive content in public audio.
- effort: Moderate hardware revision, enclosure/comfort testing, haptic driver and firmware queue, plus relay delivery semantics and battery characterization.  ·  risk: Added vibration and driver faults could drain the battery or create nuisance alerts. Cap vibration duration, rate-limit repeated events, persist only compact event IDs, and fall back to the existing LED/button when the motor is unavailable. Do not vibrate for content that could reveal sensitive information; use generic patterns only.
- cost: Roughly $2–$8 BOM increase for motor, driver, and PCB changes; a few milliamps only during brief pulses, with negligible average draw if rate-limited. No meaningful model-token cost.  ·  latency: Notification latency becomes bounded by the relay's delivery acknowledgment and the pendant uplink; the tactile alert itself is immediate after receipt. It enables asynchronous work without keeping the realtime model in a live turn.
- security: Patterns convey only category, never message content. Firmware must authenticate notification packets, reject replayed event IDs, and avoid storing transcripts or page data on the device.
- depends on: A durable relay-to-pendant notification/delivery-ack route for completed Mac and browser jobs; A compact event-ID and deduplication protocol shared by /jobs, /pipeline/events, and the pendant firmware; A user-facing mapping from haptic acknowledgment to relay_job_status or equivalent result retrieval


## What it asked for

_Nothing._
