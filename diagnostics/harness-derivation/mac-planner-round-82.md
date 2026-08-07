# Harness derivation — mac-planner — round 82

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If something I asked depends on my Mac or a logged-in browser that is unavailable, keep working with whatever evidence is already cached, tell me exactly what is blocked, and resume automatically when that surface comes back."
- **useful because:** Today a browser outage leaves five commands pending and the owner with no useful answer; this would turn failures into honest partial results plus automatic continuation, spanning the pendant, relay, Mac, and browser rather than merely reporting an error.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use a cheap background planner for retry classification and evidence reconciliation; reserve realtime for the one-sentence spoken status and final alert.
- **latency:** Speak a bounded status within 2 seconds; retry browser heartbeat/queued work in the background with exponential backoff and quiet hours, then deliver one completion alert.
- **cost:** Low: mostly D1/job state and heartbeat traffic; one background model call per failed or resumed job, with realtime only for the short status.
- **security:** Cached private-page evidence must retain its sensitivity and TTL and never be sent to a different browser session. No mutation should be attempted on resume without the existing owner policy; receipts must say whether data was cached, newly read, or stale.
- **missing:** A first-class blocked/partial/resumable job state shared by /jobs and /pipeline; A browser heartbeat-triggered retry worker that binds a job to its original tab/session; A pendant delivery record so an offline device receives exactly one resumed-result alert

### "Let me start a conversation on the pendant, continue it on my Mac without repeating myself, and then send the final answer back to the pendant—even if LTE drops briefly or I switch between speaking and typing."
- **useful because:** Today the pendant, relay, and Mac pipeline record related events but do not provide one interruption-safe conversation identity across devices. The owner loses context precisely when moving from voice to desktop, which is the moment a wearable assistant should become more useful.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use the realtime model only for live speech turns; use a cheaper background model to compact and reconcile the conversation transcript when handing off, and no model at all for ordered audio/text transport.
- **latency:** A handoff acknowledgment should be spoken or shown within 1 second; resume the conversation within 3 seconds after the Mac or pendant reconnects. Preserve ordering rather than racing late packets.
- **cost:** Low to moderate: mostly durable event storage and audio transfer; one small background summarization call per handoff, with realtime tokens only for actual spoken turns.
- **security:** Bind the conversation to the paired owner and device session; encrypt transcript/audio at rest, apply short retention, and never expose private browser evidence to the pendant unless it is explicitly part of the answer. A receipt must identify which device supplied each claim and whether it was live or queued.
- **missing:** A shared conversation-transfer protocol with monotonic turn IDs, resume tokens, and exactly-once delivery across pendant, relay, and Mac; A compact transcript/context snapshot endpoint that both realtime and Mac planners can consume without replaying the full history; Duplex audio/text reconciliation that handles LTE packet loss, late speech, and a typed Mac reply without duplicate responses; A visible pendant/Mac handoff control and durable completion receipt


## Changes it proposed to its own stack

### `integration` — Make execution authorization and pipeline status come from one shared policy/result object. A read-only research command currently reaches /pipeline as “Waiting for your approval” even though the live Mac agent reports FULL_CONTROL_MODE=true and the configured owner policy says no approval gate; add explicit action classes (read-only, reversible, destructive) for observability, execute according to the active policy, and emit the same class, decision, and reason in /jobs receipts, /pipeline events, and spoken status. Never claim “waiting for approval” when the action was actually uploaded and accepted.
- **owner gets:** The owner should not have to guess whether a request ran, is paused, or merely has a stale dashboard label. This fixes the concrete news-job failure and makes every future pendant-to-Mac action trustworthy without reducing access.
- effort: Medium: centralize the decision/result serializer used by POST /execute, job receipts, and pipeline event emission; add replay tests for read-only shell, reversible file action, and destructive mail/delete cases.  ·  risk: A policy mismatch could accidentally run or block an action. Recover with a compatibility flag, retain raw event history, and fail closed only on contradictory state while clearly reporting the contradiction.
- cost: Negligible runtime/API cost; fewer unnecessary planner retries and approval round trips.  ·  latency: Slightly lower latency for read-only work by removing the false approval wait; no added model call.
- security: Improves auditability and preserves the owner’s existing maximum-access policy; classification is telemetry, not an unrequested gate. Destructive actions remain labeled so the owner can inspect receipts.
- depends on: A single authoritative execution-policy configuration shared by local-agent and relay; Receipt schema that stores action class, decision, and evidence; Regression tests covering /execute and /pipeline together

### `hardware` — Replace the single nRF9160 development-kit audio/transport bottleneck in the wearable design with a two-processor audio architecture: a low-power audio MCU with DMA, larger RAM, and a timestamped 2–4 second bidirectional ring buffer handles 24 kHz playback/15.625 kHz capture, while the cellular/application processor handles LTE/TLS and relay protocol. Add a small hardware clock/timestamp boundary so queued PCM/Opus frames can be resumed and de-duplicated after modem stalls.
- **owner gets:** They would be able to speak naturally while the pendant is talking without the current LTE contention dropping roughly eight seconds of speech, and a brief coverage dip would sound like a short delay instead of losing the middle of the conversation.
- effort: High: select a production wearable audio MCU/codec and memory, redesign the board and power tree, define an inter-processor transport, then validate RF coexistence, thermal behavior, and end-to-end latency with real LTE-M traces.  ·  risk: More parts, firmware, and power domains create new failure modes; recover with watchdogs, a bypass mode that routes audio directly through the application processor, and a factory diagnostic that verifies clock/queue health before enabling the split path.
- cost: Roughly $8–$20 added BOM at low volume plus board redesign; approximately 10–30 mW average for the audio subsystem depending on codec/DSP choice, potentially offset by letting the cellular processor sleep during playback.  ·  latency: Adds about 1–5 ms of local buffering, but removes multi-second stalls and packet loss under simultaneous uplink/downlink; target conversational round-trip remains under 300 ms when coverage is good.
- security: The audio MCU must not retain raw speech beyond the bounded ring buffer; secure-boot both processors, authenticate their firmware, and erase buffers on call end or pairing change.
- depends on: A production audio/transport protocol with frame sequence numbers and resume semantics; Measured LTE-M contention and battery targets for the intended enclosure; End-to-end 24 kHz relay/Opus acceptance tests on the replacement hardware


## What it asked for

_Nothing._
## Its own summary

Fresh discovery found a concrete cross-surface inconsistency: /ops/status reports FULL_CONTROL_MODE=true and no required permissions, while the live /pipeline for a read-only news research job says “Waiting for your approval”; the job nevertheless rendered and uploaded 24 kHz PCM. I recorded an integration change to unify policy and pipeline/receipt status, and proposed resumable cached-evidence behavior for offline browser/Mac work. Browser remains offline with 5 pending commands and no attached tab; relay and Mac bridge are online. The granted mac_readonly_inspect interface exists but has no implementation, so local app/tab/log inspection is still unavailable. Accessibility and Screen Recording remain owner-side TCC blockers, and the pendant’s 24 kHz path is still prototype bandwidth/CPU constrained.

**Biggest unknown:** Whether the approval message is only stale dashboard text or an actual relay-side execution gate, and which component owns the five queued browser commands; resolving that needs a working read-only inspection/log surface or restoration of the browser heartbeat.

