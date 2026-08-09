# Harness derivation — mac-terminal — round 206

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### ""Is the pendant-and-audio-bridge bench healthy? If not, tell me exactly which chip or link failed and what I should do.""
- **useful because:** This turns today's physically connected but relay-unregistered hardware into something the owner can trust before wearing it. A single answer should test both UARTs, framing/heartbeats, audio-clock timing, and the Mac-side relay process, then speak a diagnosis through the available audio path rather than making the owner inspect logs.
- **path:** pendant → mac-planner → relay-realtime → faculty-perception → faculty-judgement
- **model tier:** background for capture/parsing and cheap classifier; realtime only to phrase the final spoken diagnosis
- **latency:** under 10 seconds for a bounded 2-second capture; never leave a serial reader running indefinitely
- **cost:** well under $0.01 per check; dominated by one short model call only when raw diagnostics are ambiguous
- **security:** UART output can contain firmware logs and identifiers. Keep raw logs on the Mac, send only parsed health facts and short evidence excerpts to relay; require no mutation or flashing for this read-only check.
- **missing:** a resolved bounded serial-reader capability or a typed host action that can invoke the existing dual_chip_autocapture scripts; a framing parser for nRF9160 and ESP32 health/audio counters; a relay response route that can deliver the diagnosis to the pendant while LTE is absent (USB bench audio fallback)

### ""Even with LTE and the relay offline, let me press the pendant, speak, and hear a short answer through the attached audio bridge.""
- **useful because:** The owner can use the wearable today while it is USB-attached, instead of treating an unregistered relay as a total outage. It makes the current bench setup a real offline continuity mode: pendant button and mic, Mac-local speech/model processing, and bridge playback, with no cloud round-trip.
- **path:** pendant → mac-planner → relay-realtime → faculty-perception → faculty-action
- **model tier:** small local speech-to-text and local/cheap text model for offline turns; reserve realtime cloud for when the transport is healthy
- **latency:** audio acknowledgement under 250 ms; transcript-to-first-audio under 2 seconds; hard-stop after 15 seconds offline processing
- **cost:** near-zero API cost when local models are installed; modest one-time disk/RAM cost for models
- **security:** Offline audio and transcripts remain on the Mac unless the owner explicitly enables relay sync. Show a local-only indicator and discard raw audio after the turn unless saved.
- **missing:** Mac host audio/serial bridge service that consumes the existing USB captures and emits framed audio; offline speech recognition and TTS models or a local inference endpoint; a transport selector that routes pendant USB audio without requiring LTE registration; a small durable turn journal so reconnect can optionally sync only the final transcript

### ""When something I asked the Mac to do fails, tell me what it was trying to change, show me the relevant evidence, and suggest the safest next step — without rerunning it.""
- **useful because:** Today a failed shell/UI action collapses into a short message, while the useful context is scattered across receipts, journal, focused app, and browser provenance. This gives the owner an immediate, evidence-backed explanation and prevents accidental duplicate side effects.
- **path:** mac-planner → browser-extension → relay-realtime → pendant → faculty-perception → faculty-judgement
- **model tier:** cheap background classifier to extract failure facts; realtime only to speak the concise result when the owner is waiting
- **latency:** under 1 second from job completion for structured evidence; under 3 seconds for a spoken explanation
- **cost:** <$0.01 per failure; most work is deterministic receipt/provenance joining, with model use only for synthesis
- **security:** Never send full env, secrets, or arbitrary stdout to relay. Redact tokens and limit browser evidence to provenance records and the failing origin. No automatic retry or mutation.
- **missing:** a job-failure evidence joiner that links job, action receipt, journal, browser provenance, and current context; structured exit code and signal fields for run_shell failures; a relay event carrying a bounded failure capsule to the pendant; a stable browser provenance correlation ID on actions that cause Mac work

### ""Did that actually take effect in the outside world? Don't just tell me the Mac or browser finished — prove the final state changed, or tell me that you cannot prove it.""
- **useful because:** A dispatched click, successful shell exit, or browser command receipt is not the same as an external side effect. The owner needs a postcondition verdict for consequential work: message sent, appointment changed, purchase submitted, file synchronized, or nothing proven. This is a new trust boundary between the wearable's spoken request and reality.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** background deterministic postcondition checker first; use the expensive realtime tier only to answer the owner's follow-up aloud
- **latency:** return an initial dispatched result immediately, then produce a verified/unverified verdict within 5 seconds of the action's receipt
- **cost:** <$0.01 per verification when structured postconditions exist; browser re-reads and external confirmation dominate, not model tokens
- **security:** Verification may revisit private authenticated pages and inspect sent-mail/calendar/file state. Keep evidence capsules on the Mac, transmit only the verdict and minimal citation to relay, and require explicit confirmation before any compensating action.
- **missing:** a required postcondition contract on each consequential action, expressed as typed checks rather than free text; a browser/Mac verifier that can re-read the relevant external state and distinguish unchanged, changed, and ambiguous; a durable evidence capsule joining the original request, action receipt, verification observation, and timestamp; a pendant/relay status event for verified, unverified, and verification-failed states

### ""If someone else speaks near my pendant, answer them if it is harmless, but never let their voice trigger a Mac, browser, purchase, message, or home-control action as me.""
- **useful because:** The pendant is worn in public and its microphone hears other people. A trusted model must separate conversational help from identity-bearing authority; otherwise an innocent nearby sentence can become an authenticated action through the Mac or browser session.
- **path:** pendant → relay-realtime → faculty-perception → faculty-judgement → mac-planner → browser-extension → faculty-action
- **model tier:** small on-device voice-activity/speaker verifier for the fast reject path; realtime model only after identity confidence is established
- **latency:** local decision under 150 ms before dispatch; no perceptible delay for harmless replies, with uncertain requests answered but not acted on
- **cost:** near-zero per turn after an on-device speaker embedding is enrolled; occasional background recalibration is cheap
- **security:** Speaker embeddings are biometric data and must stay on the pendant or encrypted Mac vault. Never treat voice confidence alone as authorization for high-impact actions; require a second physical signal for low-confidence identity.
- **missing:** an enrollment and revocation flow for the owner's voice embedding; firmware-side feature extraction or a low-power verifier compatible with the pendant's RAM budget; a relay action-intent flag that distinguishes conversational response from authorized side effect; a Mac/browser execution rule that refuses identity-unverified intents while still allowing read-only answers

### ""Stop everything you are currently doing for me, everywhere, and make sure nothing queued wakes up and continues.""
- **useful because:** A single spoken or physical emergency stop should cover Mac jobs, browser commands, relay work, and pendant outbox items. Today cancellation is fragmented and a running shell may continue; queued work can remain elsewhere. This is the one capability that matters when the owner realizes an instruction was wrong or unsafe.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-action → faculty-judgement
- **model tier:** deterministic control-plane operation; no model reasoning is required once the stop signal is recognized
- **latency:** local pendant acknowledgement under 200 ms; revoke new dispatches under 1 second; report each surface's stopped/unknown state within 3 seconds
- **cost:** negligible API cost; dominated by durable revocation records and transport fan-out
- **security:** The stop signal must be authenticated to the pendant/button, survive link loss, and be monotonic so stale completions cannot be accepted afterward. It should stop or quarantine work, not delete evidence; resumption must be a separate explicit act.
- **missing:** a globally ordered revocation epoch shared by relay, Mac, browser, and pendant; abort propagation into child processes and browser commands, rather than cooperative checks only between steps; a durable queue quarantine that covers pendant outbox, relay jobs, Mac jobs, and browser polling; a truthful per-surface stop receipt and stale-completion rejection rule


## Changes it proposed to its own stack

### `mac-harness` — Add a boot-time execution reconciler that reads pendant-jobs.json and the action ledger, closes ledgers in a finally block, marks jobs interrupted with an explicit crash boundary, and emits a resumable plan only for steps whose receipt proves they never started. Attach the real jobId to planMeta and preserve original-vs-rewritten run_shell actions. Do not gate anything: this is recovery and truthfulness, not approval.
- **owner gets:** After a Mac restart or agent crash, the owner gets a truthful answer and a one-click/one-phrase continuation instead of a job that claims to be running forever or blindly repeating a side effect.
- effort: Moderate: ledger lifecycle and boot reconciliation in local-agent; receipt schema migration and tests for rewritten shell actions.  ·  risk: A false 'never started' inference could duplicate a mutation. Recovery must default to 'unknown / do not replay' when dispatch boundary is ambiguous, while allowing read-only or explicitly idempotent steps to resume.
- cost: Negligible API cost; a few kilobytes of durable metadata per step.  ·  latency: Milliseconds at boot; no steady-state impact.
- security: Improves auditability without reducing owner-authorized access. Redact environment values and retain hashes, not secrets.
- depends on: POST /execute remains the execution authority; GET /ledger/interrupted and GET /ledger/:ledgerId/resume need a reliable closed/open distinction; Implement exit-code and dispatch-boundary fields in action receipts


## What it asked for

### `t25-8fk1` (tool) — run_bench_health_check
- why: The chips are physically attached now, but the only way to inspect them is an unstructured run_shell capture with no serial parser or trustworthy result. The owner needs one bounded, read-only health answer before relying on the wearable.

```json
{
  "type": "object",
  "properties": {
    "duration_ms": {
      "type": "integer",
      "minimum": 100,
      "maximum": 5000
    },
    "include_audio_counters": {
      "type": "boolean"
    },
    "save_raw_log": {
      "type": "boolean"
    }
  },
  "required": [
    "duration_ms",
    "include_audio_counters",
    "save_raw_log"
  ],
  "additionalProperties": false
}
```

## Its own summary

Discovered live inventory again: the Mac bridge is online and Safari has two tabs, but the physically attached chips still have no resolved serial capability. I produced three owner-facing proposals: a bounded pendant/ESP32 bench-health diagnosis, offline USB conversational continuity, and evidence-backed failure explanations; I also proposed crash-safe job/ledger reconciliation and queued a typed read-only run_bench_health_check capability (t25-8fk1). The concrete remaining need is not permission or another shell gate: it is a real host implementation that reads the two UARTs, parses health/audio counters, and optionally feeds a USB audio path.

**Biggest unknown:** Whether an existing relay or Mac service already exposes a USB audio fallback or framed UART protocol; I asked relay-realtime. Until that answer or implementation exists, the owner cannot get a trustworthy bench verdict or offline wearable conversation despite the hardware being connected.

