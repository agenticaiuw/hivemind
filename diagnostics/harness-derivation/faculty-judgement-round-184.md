# Harness derivation — faculty-judgement — round 184

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Did I actually hear today's brief, and what exactly did I miss?”"
- **useful because:** The system should distinguish a generated brief from one the pendant downloaded and the owner started or finished hearing. It would answer with the missing items, preserve the current item position, and offer a compact replay instead of pretending that a queued artifact was delivered.
- **path:** relay-realtime → pendant → mac-planner
- **model tier:** background for reconciliation and item ranking; realtime only for the spoken answer
- **latency:** under 3 seconds for status; under 8 seconds if a compact replay must be synthesized
- **cost:** Usually <$0.01; dominated by optional TTS/audio regeneration, not the receipt join
- **security:** Use opaque artifact/item IDs and provenance references, not raw brief text in the pendant ACK. Never mark heard from download alone; a finished ACK or explicit owner action is required. Replay should pass the existing redaction path.
- **missing:** wire record_pendant_delivery_event into the live receipt/journal query; a durable join from relay job/brief item to artifact ID; a read endpoint that folds downloaded/started/finished/interrupted ACKs into the catchup view

### "“Is my pendant ready before I leave?”"
- **useful because:** With the pendant and ESP32 physically attached over USB today, the Mac can run a one-button preflight of serial reachability, codec/audio acceptance metrics, relay health, queued ACKs, and stale firmware symptoms, then speak one honest ready/not-ready sentence and prepare a reviewable bug draft when it fails.
- **path:** pendant → mac-planner → relay-realtime
- **model tier:** background deterministic checks first; realtime only to explain an abnormal result
- **latency:** 10–20 seconds for the full USB/audio check; immediate cached health answer when checks are fresh
- **cost:** Near-zero API cost; local serial probes dominate. Optional model explanation is <$0.01.
- **security:** Keep UART contents local except a user-reviewed diagnostic draft. Do not upload microphone/audio payloads. Treat LTE as unavailable and report USB-tethered status distinctly from registered-device status.
- **missing:** a safe read-only Mac action for opening/reading both configured serial devices; a hardware test command that returns numeric codec and queue metrics without mutating firmware state; a freshness-bound readiness certificate consumed by the briefing scheduler

### "“Show me the private result; don't say the contents out loud.”"
- **useful because:** A deliberate per-request silent handoff lets the owner use the pendant in public without inventing a global disclosure policy: the browser or Mac displays the result, while the pendant says only that it is ready. This combines the worn device's intent with the browser's authenticated session and the Mac's screen.
- **path:** pendant → browser-extension → mac-planner → relay-realtime
- **model tier:** realtime for resolving the spoken instruction and selecting the current item; deterministic policy for the actual handoff
- **latency:** under 2 seconds to acknowledge; under 6 seconds to place/focus the destination page
- **cost:** Usually <$0.005; model parsing dominates, browser/Mac actions are local
- **security:** The mode must be explicit and scoped to one result, defaulting to no spoken payload. Require autonomy_policy_evaluate before navigation or display, attach source provenance, and never place credentials or page secrets in the relay prompt. If the browser is offline, say so rather than reading aloud.
- **missing:** a typed silent-delivery mode on the audio/brief item contract; a browser command that focuses an already-open result without copying its contents through the relay; a receipt proving the owner-visible display occurred

### "“When I unplug the pendant, freeze anything waiting for my approval and stop speaking; when I plug it back in, tell me what was held.”"
- **useful because:** USB attachment is the only live pendant transport today, so disconnect is a real physical absence signal. Treating it as a safety boundary prevents a stale browser or relay job from continuing while the owner has walked away, then gives a concise recovery list on reconnect.
- **path:** pendant → mac-planner → browser-extension → relay-realtime
- **model tier:** deterministic event handling and policy evaluation; background model only for the reconnect summary
- **latency:** freeze within 1 second of serial loss; reconnect summary within 5 seconds
- **cost:** Near-zero API cost; local serial monitoring and durable state dominate
- **security:** Fail closed on ambiguous disconnect. Cancel only owner-owned reversible work; irreversible actions remain blocked. Do not treat reconnect as consent. Persist opaque IDs and reasons, not page contents.
- **missing:** a production USB serial connection-state event from Mac to relay; a durable pending-plan freeze state that survives relay restart; a reconnect endpoint that lists held work with provenance

### "“I’m traveling—use the time where I am for spoken reminders, but never silently reinterpret my Mac’s timestamps.”"
- **useful because:** Today the Mac has an authoritative America/New_York zone while the pendant clock is zoneless and the owner's remembered timezone says America/Chicago. The owner cannot safely ask for 'this morning' or trust a routine after crossing time zones. This capability would keep machine time, owner-local time, and event time distinct, and surface ambiguity instead of silently choosing one.
- **path:** pendant → relay-realtime → mac-planner
- **model tier:** deterministic time resolution and signed state propagation; realtime only when the owner asks an ambiguous temporal question
- **latency:** under 1 second for a cached zone; under 5 seconds after a fresh network/GNSS/NITZ observation
- **cost:** Negligible model cost; hardware location/time acquisition and occasional relay sync dominate
- **security:** Persist coarse timezone/offset, not coordinates, by default. Require explicit consent before retaining location history. A stale or conflicting observation must produce 'ambiguous' and never fire a time-sensitive mutation.
- **missing:** GNSS or reliable NITZ capture on the pendant, or an explicit owner timezone control; a signed temporal-state record carrying source, observed_at, confidence, and expiry; routine and briefing evaluators that refuse to resolve relative time when the sources conflict

### "“What would have changed your mind, and can you watch for that evidence?”"
- **useful because:** An explanation today can cite what supported an action, but it cannot expose the missing observation that would have reversed the judgement or keep watching for it. This capability turns uncertainty into a concrete, owner-reviewable test: competing hypotheses, discriminating evidence, expiry, and a notification only when the evidence actually arrives.
- **path:** faculty-judgement → relay-realtime → mac-planner → browser-extension
- **model tier:** background model to formulate competing hypotheses and discriminating tests; deterministic watch evaluation; realtime only for the concise answer
- **latency:** under 5 seconds to explain the current judgement; watch checks follow the source's normal poll interval
- **cost:** <$0.02 per explanation; recurring cost depends on the number of read-only watches and browser polls
- **security:** Do not turn uncertainty into permission to act. Watches are read-only by default, expire automatically, carry source provenance, and never send messages or mutate accounts. Sensitive evidence remains local/redacted.
- **missing:** a typed counterevidence object attached to judgement/provenance records; a watch condition that can evaluate 'evidence contradicts hypothesis' rather than only page churn; a durable history of dismissed and confirmed counterevidence


## Changes it proposed to its own stack

### `interaction` — Add an explicit owner-visible 'transport truth' line to every spoken status: USB-tethered, relay-reachable, LTE-registered, or unknown, with the timestamp and whether playback was actually acknowledged. Make the relay refuse claims of remote availability when only USB is present.
- **owner gets:** They will know whether the pendant can work because it is beside the Mac or because it can work independently, instead of discovering after leaving the desk that LTE was never registered.
- effort: Medium: propagate a typed transport state from the Mac serial monitor and pendant ACKs into status, briefing, and catchup responses.  ·  risk: A stale heartbeat could produce a false ready state; require expiry and fail to 'unknown'. Recovery is a fresh serial probe or authenticated ACK.
- cost: Negligible API cost; local polling only.  ·  latency: Adds at most one cached lookup; fresh probe may add 1–2 seconds.
- security: Improves honesty; no content leaves the device. Avoid exposing device identifiers in spoken output.
- depends on: a live serial monitor for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; record_pendant_delivery_event wired to durable receipts

### `hardware` — Add a small local acoustic-presence classifier path (or a dedicated near-field/bystander sensor) that emits only an ephemeral 'likely private / likely shared space / uncertain' signal; combine it with pendant playback state and the owner's explicit per-request silent mode before any sensitive text is synthesized.
- **owner gets:** The pendant should stop being socially unsafe when another person is nearby. Today it can speak arbitrary caller-provided text and has no bystander or content gate. A local, non-recording signal would let it withhold sensitive playback or ask the owner to view it, without uploading room audio.
- effort: High: sensor/firmware DSP or a small on-device model, signed uncertainty events, and a server policy that treats uncertainty as no permission to disclose. Requires field calibration and an owner override.  ·  risk: False positives could suppress useful speech; false negatives are worse. Fail closed for secret content, provide a discreet non-content acknowledgment, and never store PCM. Recovery is an explicit owner override for that item.
- cost: Roughly $2–8 for a microphone/sensor change if needed, plus modest firmware RAM/flash and continuous low-power draw; model cost is near zero once local.  ·  latency: 10–100 ms local classification before sensitive playback; no network round trip.
- security: Improves privacy by keeping room evidence local, but the presence signal itself is sensitive and must not leave the device by default.
- depends on: a defined owner disclosure policy; a firmware-local classifier that fits the remaining application RAM; a mandatory confidentiality gate in pendantSpeech.js and audioBrief.js


## What it asked for

_Nothing._
## Its own summary

This round produced four owner-facing ideas: delivery-truth recovery ('what did I actually hear?'), a USB-attached pendant readiness check, explicit silent handoff ('show it, don't say it'), and a fail-closed freeze when the pendant is unplugged. I also proposed transport truth in every status so USB tethering cannot be mistaken for LTE independence. The strongest near-term capability is delivery-truth recovery: generated is not downloaded, downloaded is not played, and played is not finished. The recorder flagged similarity between that and existing catch-up work, so implementation must make the distinguishing field the authenticated pendant playback ACK, not another generic briefing queue.

**Biggest unknown:** Whether the live system already has routes that join pendant delivery ACKs to brief items/jobs, expose USB serial connection state, or provide a delivery-aware catchup view. The granted reconciliation call also resolved to a side-effecting POST /briefing instead of performing the requested read-only reconciliation, so its binding is not yet trustworthy.

