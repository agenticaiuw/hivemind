# Harness derivation — faculty-judgement — round 73

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“If the connection gets bad while I’m talking, don’t lose what I said—keep the conversation coherent and tell me only if you truly need me to repeat something.”"
- **useful because:** The current LTE-M link demonstrably loses several seconds of uplink when the agent speaks. Today that turns a wearable conversation into silent, dangerous omissions. This would make the pendant honest and recoverable rather than pretending it heard the owner.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → dashboard
- **model tier:** Realtime for detecting the live gap and asking at most one short clarification; a cheaper background model on the Mac can reconstruct context from the local transcript and queued jobs. No expensive model call for clean packets.
- **latency:** Add under 150 ms to normal turns. On loss, buffer and retransmit within 2–5 s; if still incomplete, one spoken clarification under 8 s, with a dashboard receipt later.
- **cost:** Negligible for clean turns; roughly $0.001–$0.01 only when a clarification/reconstruction model call is needed. LTE retry bytes and a small D1/R2 event record dominate infrastructure cost, not inference.
- **security:** Audio is retained only when an upload fails, matching the owner's SD policy; retransmitted chunks must be encrypted and deduplicated. The Mac reconstruction must stay within the existing local transcript and never invent a missing claim: say “I missed the phrase” and quote the uncertain span. Clarification is always non-destructive; no action is taken from a repaired transcript without the existing confirmation policy.
- **missing:** Firmware sequence numbers, bounded retransmit ring, and loss telemetry on the single full-duplex I2S path; Relay audio acknowledgements and a durable per-turn gap/recovery record; A model-routing rule that distinguishes packet loss from speech recognition uncertainty; A compact dashboard/receipt view of missing, recovered, and deliberately discarded audio

### "“Let me know silently when something important is ready, and let me approve or dismiss it without speaking or taking out my phone.”"
- **useful because:** The owner cannot reliably use the pendant in meetings, transit, or public places: its only local feedback is audio and one LED, and spoken confirmations are socially awkward or unsafe. A discreet tactile channel would make queued Mac/browser work and urgent personal notices usable in real life rather than only at a desk.
- **path:** relay-realtime → mac-planner → browser-extension → pendant → dashboard
- **model tier:** Background models prepare and rank the notification; realtime is used only if the owner presses the pendant and asks for the item. No model call is needed for dismiss/approve gestures once the signed notification is prepared.
- **latency:** Urgency decision within seconds of a job receipt or monitored event; tactile notification within 1 second after delivery; local approve/dismiss acknowledgment under 200 ms.
- **cost:** Near-zero incremental inference on delivery; approximately $5–$15 hardware BOM for a low-power haptic actuator and driver, plus negligible relay storage. Model cost is limited to the existing job or watch that generated the item.
- **security:** Only a short opaque item ID and urgency class should reach the pendant; sensitive text remains on the authenticated Mac/dashboard. Approval must be cryptographically bound to the exact proposed action, expire quickly, and still obey destructive-action confirmation. A long press must be an unconditional stop/dismiss, not an approval.
- **missing:** A production pendant revision with a low-power haptic actuator and a second distinguishable input gesture or capacitive surface; Signed, expiring notification envelopes shared by relay, Mac, and pendant; A notification policy that ranks urgency without leaking private content through vibration patterns; Receipt handling that records approve, dismiss, timeout, and delivery failure across surfaces


## Changes it proposed to its own stack

### `firmware` — Add an explicit loss-aware audio transport contract: every Opus frame gets a monotonic conversation/turn/frame id and CRC; keep a bounded RAM retransmit ring sized for ~2 seconds, spill only failed uploads to the existing SD failure buffer, and emit gap/recovered markers over the existing event stream. The relay ACKs frame ranges, deduplicates retries, and exposes a typed receipt; the realtime router must never treat a gap as silence. On unrecoverable loss, Mac-local transcript repair may summarize only surrounding verified text and must mark the missing span.
- **owner gets:** A dropped LTE-M burst would stop being an invisible omission. The owner either gets the complete sentence or a brief, trustworthy request to repeat it, instead of an agent confidently acting on half-heard speech.
- effort: Medium: firmware framing/ring and tests, relay ACK/idempotency state, one router policy, Mac receipt UI. Validate with forced modem contention and 24 kHz playback simultaneously.  ·  risk: Extra buffering can increase RAM pressure and retransmits can worsen congestion. Bound the ring, prioritize current uplink over playback ACKs, and fall back to the current behavior after a timeout. Recovery is safe because frame IDs make retries idempotent and missing spans are never silently filled.
- cost: No extra model cost on healthy calls; small D1 event and R2 bytes on loss. Firmware uses a bounded ~16–24 kB ring, within 211,608 B only after measuring current Opus headroom; no hardware purchase required.  ·  latency: Normal path unchanged except tiny framing/ACK overhead; impaired path adds up to 2–5 seconds for retransmission or one clarification.
- security: Audio remains TLS-protected; SD remains failure-only. Receipts should retain hashes and ranges, not raw audio, unless the existing retention policy explicitly permits it.
- depends on: 24 kHz end-to-end audio acceptance test and measured RAM/CPU headroom; Durable pipeline event/receipt schema; A single model-routing rule for verified-vs-uncertain transcript spans

### `dashboard-ux` — Add a live “what I can safely do right now” contract card, compiled from relay, Mac ops snapshot, browser heartbeat, audio health, and permission state. It should say, in owner language, for example: “I can read Safari tabs: no (bridge offline); I can use Calendar via AppleScript: yes; GUI clicking: limited (Accessibility not trusted); battery: unavailable (no gauge); audio: 24 kHz playback / loss recovery: status.” Attach the same compact capability summary to a spoken clarification only when it changes the requested task, and log the snapshot with every action receipt.
- **owner gets:** The owner stops wasting attempts on operations that fail mysteriously. Before saying “read Gmail” or trusting a long voice instruction, they know whether the relevant reach exists and what safer alternative the hive can use.
- effort: Small-to-medium: normalize existing health/permission fields, add stale-time rules and a dashboard component, and expose a short relay formatter. No new model behavior is required.  ·  risk: A stale or overly technical card could mislead. Use explicit timestamps, three states (available/limited/unavailable), and never infer permission from a prior success. If health data is missing, display unknown rather than optimistic.
- cost: No inference cost; a few hundred bytes per snapshot and one dashboard request. Existing routes/tools provide the data.  ·  latency: Under 100 ms from cached snapshot; no impact on normal conversation unless a capability changed.
- security: Do not display bearer tokens, private URLs, or secret memory. Permission status and device health are local operational metadata; action receipts should retain only the relevant capability hash.
- depends on: A typed capability snapshot schema spanning relay and Mac; Existing GET /ops/snapshot, GET /browser/status, GET /health, GET /pipeline, and dashboard polling; Owner-facing wording that distinguishes a denied TCC grant from a transient offline bridge

### `hardware` — Replace the development pendant's unmeasured USB/battery supply with a production power path exposing battery voltage/current over the already-free I2C bus (for example, a low-quiescent fuel-gauge IC with an interrupt line). Add a small local state machine that reports capacity, charging, and critically-low events to relay; do not make the modem or audio path poll continuously.
- **owner gets:** Morning briefs and urgent conversations can finally tell the truth about whether the pendant will survive the day. The system can defer a long research briefing or warn before a call is cut off, instead of discovering an empty battery after the owner needs it.
- effort: Hardware revision plus driver, calibration across the chosen cell, and relay/dashboard fields; validate under LTE transmit and simultaneous 24 kHz playback.  ·  risk: Bad calibration or a brownout-prone power path could create false alarms or shorten runtime. Keep the existing supply as fallback, debounce readings, and treat unknown as unknown. A prototype board spin is required; this cannot be fixed purely in the relay.
- cost: Roughly $2–$6 BOM increase plus PCB revision; sub-milliamp quiescent draw depending on gauge, negligible versus LTE bursts. No per-call API cost.  ·  latency: Battery events local within seconds; no normal audio latency impact.
- security: Only coarse health telemetry (percentage/charging/low) leaves the device; no location or raw power traces. Firmware must authenticate the event like other pendant messages.
- depends on: A production battery/power design replacing the nRF9160 DK prototype; Relay health schema and dashboard capability card; A policy for when low battery may defer background jobs versus interrupt a live call

### `hardware` — Revise the pendant enclosure/PCB to add a coin-style low-power haptic actuator with a dedicated driver and a second input modality (a capacitive touch strip or distinct press/release gesture), while retaining the existing button as the universal stop. Define three non-content-bearing vibration patterns—ready, urgent, and failed delivery—and require signed, expiring notification envelopes so a local gesture can approve only the exact queued action.
- **owner gets:** They can handle reminders, completed Mac work, and urgent account changes discreetly in a meeting or outdoors, without exposing private speech or reaching for a phone. It also gives the owner a dependable way to stop an unwanted action immediately.
- effort: Hardware revision, enclosure acoustic/tactile testing, low-power driver firmware, relay notification envelope and receipt protocol, then integration tests for delivery, timeout, cancel, and approval.  ·  risk: False touches or ambiguous gestures could approve an action. Make approval a deliberate long press/double gesture, keep the existing button as stop-only, expire envelopes quickly, and require server-side action binding and existing destructive-action confirmation. If haptics fail, fall back to LED/audio and dashboard receipts.
- cost: Approximately $5–$15 added component and PCB/enclosure cost; tens to hundreds of microamps while idle depending on actuator driver. No recurring model cost beyond the underlying notification task.  ·  latency: Sub-second local feedback; no effect on ordinary audio conversation or Mac action execution.
- security: Vibration carries urgency only, never message content. Approval tokens are scoped, signed, short-lived, and auditable; private notification text remains on the Mac/dashboard.
- depends on: Production pendant hardware rather than the current nRF9160 development kit; Cross-surface signed notification and receipt protocol; A clear owner policy distinguishing stop, dismiss, and approve gestures


## What it asked for

_Nothing._
