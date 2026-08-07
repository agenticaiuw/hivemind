# Harness derivation — faculty-judgement — round 101

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Can I safely walk away from this?” Give me one honest spoken answer about whether the work will finish without me, what could still require my approval, and how you will tell me when it is done. If it is not safe, stop or convert it into a reviewable handoff."
- **useful because:** Today a relay acceptance, queued browser command, or stale Mac receipt can sound like completion. This gives the owner a single departure decision before they leave the desk, using live reachability and evidence rather than optimistic status. It is specifically valuable on a wearable: the owner need not inspect three consoles to know whether they can go.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use a cheap background/state reducer for reachability, job contracts, approval checkpoints, and evidence age; use realtime only to phrase the final one-sentence answer and ask for a decision. No expensive model for unchanged polling.
- **latency:** Under 2 seconds for the initial verdict from cached state; under 10 seconds when it must ask Mac/browser for fresh probes. Completion notification is asynchronous and must be acknowledged as delivered by the pendant, not merely generated.
- **cost:** Usually <$0.01 per check (state queries and reducer dominate; realtime wording only on state change). Continuous watches should be event-driven with bounded polling, not a model call per interval.
- **security:** Private tab titles, job contents, and approval policy may cross the relay; transmit only task IDs, capability state, and minimal evidence snippets. Never claim safe when an irreversible step is pending. Sending mail, purchasing, deleting, or form submission still requires the owner's explicit confirmation at the point of action. A physical stop gesture must cancel the watch.
- **missing:** A typed departure contract per job: expected completion, allowed autonomous actions, approval gates, timeout, and cancellation semantics.; A live cross-node freshness reducer that labels observations as live, queued, delivered, historical, or unknown and refuses stale receipts.; An authenticated pendant delivery-ack queue and a durable completion-watch scheduler with deduplication and quiet-hours policy.; A small dashboard card showing exactly why the verdict is safe/unsafe and the last evidence timestamp.

### "“If I change this, what else will it affect?” Before I approve a consequential change, show me a compact what-if map across my calendar, commitments, travel, private web accounts, files, and pending agent work: what becomes invalid, who may need a message, what deadlines move, and the safest alternative. Do not change anything until I choose."
- **useful because:** The owner can get a draft or a transaction preview today, but cannot see second-order consequences spanning systems that no single node can inspect. This prevents a meeting move, reservation change, subscription cancellation, or file reorganization from silently breaking another commitment. It is an explanation and choice surface, not an autonomous action.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-terminal → dashboard
- **model tier:** Use a cheaper background planner to collect entities and dependencies, normalize dates and identities, and generate candidate scenarios. Use realtime only to summarize the final impact map conversationally and accept the owner's choice.
- **latency:** Initial impact map within 15 seconds for a simple change; up to 60 seconds for a multi-account scenario. The pendant should first say that analysis is in progress and never imply that a change was made.
- **cost:** Approximately $0.03–$0.15 per scenario, dominated by authenticated page extraction and the planning model; cache stable calendar, file, and account facts and recompute only affected edges.
- **security:** This intentionally correlates sensitive calendar, mail, files, travel, and logged-in web data. Keep the graph encrypted and local to the owner's Mac where possible; send the relay only a redacted question and final spoken summary. Never infer or expose sensitive relationships in a shared room. Every proposed mutation requires explicit confirmation and a before/after receipt.
- **missing:** A cross-surface entity and dependency graph that links the same person, event, reservation, file, deadline, and agent job across Mac and authenticated browser evidence.; A scenario/snapshot engine that can apply hypothetical changes without mutating real systems and can label each predicted edge as confirmed, likely, or unknown.; A provenance-rich impact explanation format with source URLs or file paths, timestamps, and the exact assumption behind every predicted consequence.; A confirmation transaction that revalidates the scenario immediately before execution and aborts if any source changed.; A pendant interaction for choosing among alternatives with one button and short spoken prompts, including a physical cancel path.


## Changes it proposed to its own stack

### `hardware` — Add a real low-power audio front end to the product pendant: a 24 kHz-capable digital microphone/codec with shared clock, hardware acoustic-echo cancellation (AEC) reference from the speaker, and a small DMA ring buffer between the modem stream and audio path. Keep the nRF9160 prototype as a bring-up target, but do not ship the current 15,625 Hz capture / 24 kHz playback split as the product contract.
- **owner gets:** The owner can interrupt spoken replies naturally without the pendant hearing its own voice, and playback will not warble or drop when LTE-M and Opus compete for the single Cortex-M33. Conversations become usable in a noisy room instead of requiring the owner to wait silently for every answer.
- effort: Medium-high: select and lay out an audio codec or AEC microphone, implement clocking/DMA and fixed-point AEC, then validate echo return loss and barge-in latency across the enclosure. Requires an end-to-end acceptance test from microphone capture through relay transcription and 24 kHz playback.  ·  risk: AEC can suppress the owner's speech or add latency; codec integration can destabilize the modem power budget. Recover with a hardware bypass mode, an explicit half-duplex fallback, and staged firmware flags. Never silently change the negotiated sample-rate metadata.
- cost: Roughly $3–$8 BOM increase plus board revision; likely 10–30 mW average for the codec/AEC, partially offset by lower MCU duty cycle. No meaningful API-model cost.  ·  latency: Target <80 ms barge-in detection and <120 ms end-to-end interruption; DMA buffering should reduce underruns rather than add delay. AEC convergence may need a short warm-up after playback starts.
- security: Audio remains on the pendant/relay path; the AEC reference is local and must not be uploaded. Add explicit diagnostics that expose only levels and quality metrics, not raw microphone recordings.
- depends on: A typed end-to-end audio contract distinguishing capture sample rate, Opus rate, playback rate, and resampler stage; Pendant playback and delivery acknowledgements, including underrun/clock-drift telemetry; A real-device acceptance test for full-duplex speech in LTE-M contention


## What it asked for

_Nothing._
