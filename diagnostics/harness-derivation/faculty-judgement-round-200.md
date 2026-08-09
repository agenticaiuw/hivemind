# Harness derivation — faculty-judgement — round 200

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When my request fails or produces no action, stop retrying it blindly: tell me what failed, preserve the original request, and offer the one concrete next route that can actually complete it."
- **useful because:** The owner's history shows repeated news, time, and page-inspection requests ending in failed or empty browser commands. A failure-loop breaker would prevent wasted turns and make the pendant say 'the browser bridge is offline; I can queue this' instead of pretending progress or asking the same model to retry.
- **path:** relay → mac → browser → pendant → dashboard
- **model tier:** Deterministic classifier and idempotent failure counter first; a cheap background model may phrase the recovery. Realtime is used only for the spoken one-sentence status.
- **latency:** Under 300 ms after a failed receipt; no additional model call for known failure classes.
- **cost:** Negligible state-machine cost; at most a short background-model call for an unfamiliar failure.
- **security:** Keep the original intent redacted and scoped; do not include page contents, mail bodies, or secrets in spoken diagnostics. A retry must pass autonomy_policy_evaluate and cross_surface_preflight again, never reuse stale permission claims.
- **missing:** A durable intent fingerprint joining relay, Mac, and browser attempts (current IDs are separate).; A typed failure taxonomy distinguishing no-op, unavailable surface, permission denial, stale plan, and mutation rejection.; A user-visible retry/cancel state with bounded retry budget and provenance.

### "Keep the pendant useful when its battery or link is poor: shorten or defer nonurgent spoken work, preserve urgent items, and tell me whether a response was delivered or only queued."
- **useful because:** A wearable that spends most of its budget decoding 24 kHz audio should not drain itself on a long research brief or repeatedly retry a weak link. The owner gets predictable availability: urgent interaction remains responsive, routine audio becomes a compact queued item, and the device never claims success from server generation alone.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Deterministic resource/urgency policy using battery, queue depth, link health, item sensitivity, and deadline; a cheap background model can produce a shorter text variant. Realtime is reserved for urgent live conversation.
- **latency:** Policy decision under 50 ms from a health event; text shortening under 2 s only for nonurgent items; no extra work on the healthy path.
- **cost:** Tiny policy overhead; occasional small background-model call for a compact variant, offset by fewer audio bytes and retries.
- **security:** Health telemetry should contain battery percentage, link quality, queue depth, and opaque artifact IDs—not transcripts. Never lower privacy classification merely to fit a degraded mode. Urgent does not mean authorized: external actions still require autonomy policy and physical approval where applicable.
- **missing:** A signed pendant health envelope and authenticated upload of battery/link/queue metrics; current delivery ACKs cover artifacts but not continuous health.; A relay-side budget planner that can request text-only, short-audio, or defer modes and bind them to an item ID.; A measured audio-cost profile for short/long variants and an owner policy for which classes may be shortened or deferred.

### "After you change something for me, verify the world—not just the command receipt—and tell me what actually changed, what did not, and what remains uncertain."
- **useful because:** A successful Mac or browser command can report acceptance while the page, file, reminder, or external service rejects it, changes a different object, or is stale. The owner should receive an outcome grounded in a fresh read, not a comforting execution status.
- **path:** relay → mac → browser → dashboard → pendant
- **model tier:** Deterministic postcondition checks for typed actions and source diffs; use the expensive model only to explain an ambiguous diff in one short spoken sentence. Never use a model to declare success without fresh evidence.
- **latency:** Verification within 3 seconds for local files, reminders, and browser state; up to 10 seconds for remote page reloads. If verification cannot complete, report 'submitted, unverified' and queue a check rather than claiming completion.
- **cost:** Small local/browser reads on every mutation; occasional low-cost model call only for ambiguous diffs. More reads than today, but far cheaper than an undetected wrong external action.
- **security:** Re-read only the minimum fields needed for the postcondition; do not retain page bodies or secret form values. For destructive or external actions, a failed or ambiguous verification must not trigger an automatic retry. Include source timestamps and provenance in the dashboard, with a redacted spoken summary.
- **missing:** A typed postcondition attached to each plan/action, including target identity, expected before/after fields, and freshness bound.; A cross-surface correlation key linking relay job, Mac action, browser command, and resulting evidence; current IDs do not join durably.; Readback adapters for every mutation target, plus an explicit unknown outcome when the target is not readable.; A receipt state distinct from accepted, such as verified, contradicted, and unverified.


## Changes it proposed to its own stack

### `hardware` — Add a fuel-gauge IC with a thermistor input and an authenticated I2C path to the pendant MCU, plus a low-power interrupt for low-battery thresholds. Publish signed coarse bands (full/medium/low/critical), not raw voltage, to the relay health envelope.
- **owner gets:** The owner can ask whether the wearable will last, and the system can avoid starting a long briefing that will die halfway through. Today there is explicitly no battery gauge, so any battery answer is about the Mac or an unsupported guess.
- effort: Moderate board spin: fuel-gauge selection, I2C wiring, firmware driver/calibration, enclosure and charging validation, then integration with relay scheduling.  ·  risk: Gauge drift or a bad calibration could cause premature deferral or surprise shutdown; recover with conservative thresholds, charger-based recalibration, and a visible 'unknown' state rather than fabricated percentage. I2C failure must not block live audio.
- cost: Roughly $1–4 BOM plus PCB area; tens of microamps to a few hundred microamps depending on gauge and thermistor sampling.  ·  latency: Health sample available in milliseconds; negligible audio-path impact. Low-battery interrupt should wake policy logic without waking the expensive codec continuously.
- security: Coarse signed bands reduce leakage compared with exact battery history; authenticate readings so a stale/spoofed health packet cannot force arbitrary deferrals. No owner content leaves the device.
- depends on: A signed pendant health envelope and relay budget planner; A product pendant revision rather than the current Nordic development kit; The existing delivery ACK and attention arbitration paths


## What it asked for

_Nothing._
## Its own summary

Round 200 produced three non-duplicate changes: (1) a cross-surface failure-loop breaker that preserves the original intent, classifies the failure, bounds retries, and proposes only a currently reachable route; (2) resource-aware wearable delivery that uses signed health, urgency, and queue state to shorten/defer nonurgent audio while reporting queued versus actually played; and (3) a hardware change adding a fuel gauge so battery-aware behavior is truthful rather than inferred. Two other proposals were correctly rejected as restatements of existing delivery assurance and truthful briefing work.

**Biggest unknown:** The product pendant still has no battery gauge or authenticated continuous health envelope, and no durable relay↔Mac↔browser↔audio-item join. I need those product/protocol decisions—not another owner preference—to make adaptive delivery and trustworthy failure recovery real. The owner’s quiet-hours, urgency, and spoken-content policy remain intentionally unset; these proposals must keep them as explicit policy fields rather than invent defaults.

