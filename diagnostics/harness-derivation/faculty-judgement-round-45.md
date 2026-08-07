# Harness derivation — faculty-judgement — round 45

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **audio** — Current prototype is not true 24 kHz end-to-end: I2S capture is 15,625 Hz, uplink Opus is 16 kHz/16 kbps, playback decodes 24 kHz into a 31,250 Hz wire clock, and simultaneous fixed-point Opus encode/decode uses about 87% of one core.
  - evidence: get_hardware_spec(audio) returned source firmware/nrf9160/src/audio_opus.c and cloud-relay/opusTranscode.js, status PROTOTYPE.

## Capabilities it proposed

### "“If something I asked you to do finishes—or gets stuck—while I’m away, tell me what actually happened and give me the one next thing I can do.”"
- **useful because:** Today a Mac/browser job can finish, fail on permissions, or time out while the owner is elsewhere, leaving receipts they must hunt for. This turns asynchronous work into a trustworthy handoff: the pendant speaks a short outcome, the Mac leaves cited evidence, and a browser task is resumed rather than silently abandoned.
- **path:** relay-realtime → mac-planner → mac-vision → browser-extension → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use the cheaper background model to classify terminal job events and compose a one-sentence receipt; use realtime only when the owner asks for details or says “fix it.” No model call for ordinary progress events.
- **latency:** Terminal event to durable receipt under 2 seconds; pendant notification under 5 seconds when connected. If disconnected, persist it and speak it once on next reconnect. Owner gets one short sentence by default, with a button/voice command for evidence and retry.
- **cost:** About $0.001–$0.01 per completed job, dominated by summarizing multi-step evidence; zero marginal cost for a typed success/failure template. Storage is a small event and receipt record per job.
- **security:** Receipts may reveal private mail, calendar, or page details over audio. Default spoken text must redact content and say only source/action/result; detailed evidence stays on the authenticated Mac. Never auto-retry irreversible actions; retries require the existing confirmation gate. Browser session identifiers and URLs stay local to the relay/Mac, not in model prompts unless needed.
- **missing:** A single cross-surface terminal-event schema carrying job id, action, result, blocker class, evidence pointers, retryability, and confirmation state; A durable receipt-to-pendant queue with deduplication, acknowledgement, quiet-hours policy, and reconnect replay; One preflight/lease shared by Mac and browser that converts offline extension, missing Accessibility/Screen Recording, or lost tab into a retryable blocker instead of a 45-second timeout; A Mac-side evidence bundle API that exposes cited before/after artifacts without copying private page contents into the relay; Owner-configurable interruption policy (urgent failures immediately; ordinary completions batched)

### "“When I leave somewhere, check the things I care about and tell me only what is definitely handled—and what I need to fix.”"
- **useful because:** The owner cannot currently turn a departure into a trustworthy, evidence-backed check across the physical world and private web services. This would combine the pendant’s departure signal and voice, Mac context, browser-authenticated services (smart lock, calendar, transit, reservations), and an always-awake relay into one calm answer: confirmed, unknown, or action needed. It is not a generic reminder or page watch; it resolves a real-life transition across systems and refuses to claim success without fresh evidence.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use a cheap background model to reconcile structured checks and evidence; use realtime only if the owner asks a follow-up or an urgent unresolved item needs spoken clarification.
- **latency:** Detect departure within 30 seconds, complete ordinary checks within 60 seconds, and speak one short result. If a service is unavailable, say unknown immediately and retry in the background rather than blocking departure.
- **cost:** Roughly $0.002–$0.02 per departure, dominated by reconciling several evidence items; most checks are deterministic API/browser reads and need no model call.
- **security:** This exposes location/routine and private account state. Store only the check definition and short-lived evidence hashes, not continuous location; require explicit setup for each service and a visible armed state. Never unlock doors, cancel reservations, or send messages automatically. Any corrective action needs the existing owner confirmation policy.
- **missing:** A pendant departure signal (explicit button/voice arm plus motion/BLE/geofence input) that does not infer sensitive location continuously; A typed check protocol with freshness windows, evidence requirements, unknown/error states, and per-check privacy scope; Authenticated integrations for locks, alarms, appliances, transit, reservations, and selected browser accounts, with read-only defaults; A relay-owned departure session that survives Mac sleep and reconnects the pendant without duplicate alerts; A compact spoken result and Mac evidence view showing exactly why each item is confirmed or unknown


## Changes it proposed to its own stack

### `hardware` — Replace the prototype’s 15,625 Hz capture path plus 31,250 Hz bridge-clock resampling with a negotiated 24 kHz audio contract: a microphone/ADC clocked at 24 kHz (or a dedicated low-power audio codec with 24 kHz mode), Opus 24 kHz capture and decode at 20–40 ms frames, and an explicit relay/ESP32 capability handshake. Add sequence numbers, sample-rate/clock metadata, underrun/overrun counters, and a loopback test mode; keep 16 kHz as a declared fallback rather than silently resampling. Move encode/decode work to a second audio-capable core/codec or budget a DSP path, because the current fixed-point Opus encode+decode already consumes roughly 87% of one core.
- **owner gets:** The owner gets genuinely wideband speech instead of a nominal 24 kHz playback stream fed by narrowband capture, with fewer glitches and an honest indication when the link falls back. A loopback score and counters let the system catch bad cables, clocks, or firmware before the owner has to debug garbled voice.
- effort: High: select and validate an audio codec/ADC, redesign clocking and bridge framing, update pendant firmware and relay transcoding, then run RF and battery tests. Firmware-only portions can land behind the capability handshake first.  ·  risk: Clock drift, increased CPU/RAM use, RF bandwidth, and power draw could worsen dropouts or battery life. Recover by retaining the negotiated 16 kHz profile, gating 24 kHz behind a device capability flag, and refusing the profile when CPU headroom or packet-loss thresholds are unsafe. Validate with automated loopback and long-duration soak tests.
- cost: Prototype hardware roughly $5–$20 for a codec/ADC and clock/power changes, plus board spin; likely tens of mW additional draw depending on codec. API cost is negligible; 24 kHz Opus packets may increase relay bandwidth by roughly 1.5–2×.  ·  latency: 20–40 ms frames can reduce capture/playback latency versus the current 60 ms decode frames, but transcoding and clock buffering add a few milliseconds. Loopback diagnostics run only on demand or during commissioning.
- security: Audio remains the same sensitive data; diagnostics must never upload raw loopback audio by default. Send counters and hashes only, and require explicit opt-in to retain samples.
- depends on: A versioned audio capability handshake shared by pendant firmware, ESP32 bridge, relay, and voice client; A measurable acceptance test: intelligibility/latency/dropout thresholds for 24 kHz and fallback behavior; Firmware memory/CPU profiling on the actual target and a product-grade audio board decision


## What it asked for

### `c5-jkkp` (context) — 24 kHz audio implementation truth
- why: Owner explicitly wants the 24 kHz superwideband path shipped; I need the actual codec/transport acceptance gaps to avoid proposing a duplicate or impossible change.
- would change: I will target the remaining end-to-end seam (firmware, relay, or playback) and state concrete dependencies rather than a generic audio proposal.

## Its own summary

Round 45 produced two non-duplicate proposals. First: an outcome-aware asynchronous handoff spanning relay, Mac, browser, perception, and pendant—terminal jobs yield a short redacted spoken receipt, cited Mac evidence, and a safe retry or explicit blocker instead of silent timeout. Second: a product-grade audio change for the owner's explicit 24 kHz goal; the current prototype is only 16 kHz capture/uplink with 24 kHz playback and ~87% single-core Opus load, so it needs negotiated true-24-kHz capture, clocking, framing, telemetry, and a safe 16 kHz fallback. I still need the orchestrator's audio acceptance criteria and actual cross-surface persistence/schema truth, plus the owner-granted Mac Accessibility/Screen Recording and browser-bridge activation before execution can be verified.

**Biggest unknown:** Whether the current firmware/relay branches already contain any partial 24 kHz negotiation or terminal-event persistence implementation; the requested context has not arrived yet.

