# Harness derivation — unified — round 42

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **privacy-mode prerequisites** — Mac local agent is reachable and relay bridge online, but Accessibility is untrusted and Screen Recording is not granted; browser extension is offline with 3 pending commands. Any cross-surface privacy latch must fail closed and cannot claim full convergence until these are repaired.
  - evidence: GET /ops/status 200: accessibility.trusted=false, screenRecording.granted=false, browserExtension.online=false, pendingCommands=3; relay.macBridgeOnline=true.
- **audio target gap** — Current pendant audio is asymmetric: I2S capture is 15,625 Hz and Opus uplink is 16 kHz/16 kbps, while playback decodes 24 kHz and resamples to a 31,250 Hz I2S wire clock. This is not yet a true 24 kHz superwideband end-to-end path.
  - evidence: describe(audio): mic 15,625 Hz capture; uplink 16 kHz/16 kbps; playback Opus decode 24 kHz/60 ms and resample to 31,250 Hz; encode/decode consume ~87% of one Cortex-M33 core.

## Capabilities it proposed

### "“I’m in public” (or long-press the pendant), then make the whole system private until I say “privacy off.”"
- **useful because:** A wearable assistant can accidentally expose spoken replies, browser pages, or Mac notifications in public. One explicit gesture/phrase should atomically reduce exposure across every surface, and provide a local confirmation even if the network is unavailable.
- **path:** pendant: long-press toggles a locally persisted privacy latch, mutes playback immediately, and shows a distinct LED pattern → relay-realtime: treats the latch as a policy claim, suppresses cloud audio retention/transcripts and refuses proactive spoken output while latched → mac-planner/mac-terminal: pauses queued and background jobs that could reveal or mutate private data, and records a resumable checkpoint → browser-extension: blanks/locks authenticated tabs or hides sensitive page content and rejects new browser commands until unlocked → Mac host: uses a native privacy action (screen lock or Focus/do-not-disturb) and returns a signed state receipt; unlock requires the explicit phrase or second long-press
- **model tier:** gpt-5.6-luna for policy evaluation and state reconciliation; gpt-realtime-2.1 only for the live phrase detection/confirmation. Firmware handles the immediate latch without a model.
- **latency:** Immediate local mute/LED under 100 ms; relay and Mac/browser convergence under 2 seconds; no cloud call required to enter privacy mode.
- **cost:** Negligible per toggle (one small state event and receipt); avoid realtime inference for button-triggered toggles. Main cost is implementation/testing, not tokens.
- **security:** The latch must fail closed on disconnect, be monotonic until an explicit unlock, and never transmit the trigger audio before local handling. Do not expose tab URLs/content in receipts. Screen lock is safer than attempting to redact arbitrary applications; require confirmation for privacy off if the owner chooses.
- **missing:** Pendant firmware privacy-latch state machine and LED pattern; Relay policy gate that suppresses audio/transcript persistence and proactive delivery; Mac bridge privacy endpoint with signed receipts and checkpoint/resume integration; Browser extension lock/masking command and an offline-safe pending-command policy; End-to-end fault-injection tests for disconnect during enter/exit

### "“What was that thing I just saw/heard?” and get a concise answer reconstructed from the last minute across my pendant conversation, active Mac window, and browser tab—even if I did not explicitly save it."
- **useful because:** People routinely lose a name, number, instruction, or webpage while moving between voice, Mac, and browser. Today these surfaces have separate histories, so the owner must remember where it occurred and repeat the search. A short-lived, source-linked interaction window would make the pendant function as continuous memory without becoming permanent surveillance.
- **path:** pendant: captures the spoken recall request and gives the answer through the existing audio path → relay-realtime: coordinates a short-lived interaction window and returns a concise spoken synthesis, retaining only derived citations/metadata rather than raw audio → mac-planner/mac-vision: reports the active application/window and a bounded, consented snapshot or accessible text from the moment before the request → browser-extension: contributes the active tab title, URL, and selected/readable page region, without exposing unrelated tabs → Mac workspace: writes an optional cited text note only when the owner says “save that”; otherwise the reconstruction expires automatically
- **model tier:** gpt-5.6-luna for cross-source reconciliation and citation selection; gpt-4.1-mini for bounded screen/text extraction; gpt-realtime-2.1 only for the live request and spoken answer.
- **latency:** Under 3 seconds for text-accessible sources; up to 6 seconds when a screenshot or OCR is required. The answer should be one short spoken sentence by default.
- **cost:** One small planner call plus optional vision/OCR call per recall request. Keep a rolling local event index and send only the relevant 60-second excerpts, so token cost stays low; raw audio should not be uploaded merely to support recall.
- **security:** The window may contain passwords, private messages, or secrets. Keep raw audio and screenshots in volatile local storage with a strict expiry; redact likely secrets before relay; require explicit “save that” to persist anything; never inspect background tabs or unrelated windows; return source labels and freshness so the owner can judge confidence.
- **missing:** A shared short-lived interaction ledger spanning pendant, relay, Mac, and browser with timestamps and source IDs; Mac/browser adapters that can provide bounded active-surface evidence rather than unrestricted capture; Local secret redaction and automatic expiry before any relay upload; A spoken recall intent and citation-aware answer formatter; End-to-end tests for clock skew, disconnected browser, and partially available sources


## Changes it proposed to its own stack

### `integration` — Add a privacy-state protocol spanning pendant, relay, Mac bridge, and browser bridge: signed monotonic enter/exit events with a fail-closed TTL, relay-side retention/proactive-output gate, Mac job pause checkpoints, browser lock command, and a single convergence receipt listing each surface's observed state without URLs or content.
- **owner gets:** One gesture would reliably stop the assistant from speaking, listening, showing private pages, or continuing queued work when the owner walks into a public or sensitive setting—and let work resume without losing its place.
- effort: Medium-high: shared protocol/schema, firmware hook, relay policy middleware, Mac/browser endpoints, and disconnect/replay tests.  ·  risk: A stale or forged unlock could expose data, or a failed lock could create false confidence. Use monotonic counters, authenticated pairing, fail-closed expiry, local LED confirmation, and expose per-surface state so the owner can see incomplete convergence.
- cost: Negligible API cost; a few small D1/job-state writes per transition. No new hardware if the existing button and LED are sufficient.  ·  latency: Local mute is sub-100 ms; remote convergence typically under 2 s. Paused jobs add no latency until explicitly resumed.
- security: Improves privacy by default, but requires careful key management and no sensitive data in receipts/logs. Unlock must be explicit and never inferred from ordinary speech while latched.
- depends on: local_privacy_latch firmware skill; Mac bridge privacy endpoint; browser extension lock/masking endpoint; relay retention/proactive-output policy gate; durable job checkpoint/resume policy

### `context` — Create an ephemeral, source-addressed interaction ledger: each pendant utterance, relay response, active Mac surface, and active browser surface emits a timestamped event with sensitivity classification and a 60–90 second expiry. A recall query retrieves only events in that window, intersects them by monotonic device time, and produces source citations; no raw audio or screenshots leave the Mac unless the query explicitly requires them.
- **owner gets:** The owner can recover something they just encountered without manually remembering which device saw it, while ordinary moments disappear instead of silently becoming a permanent personal archive.
- effort: Medium: event schema and clock synchronization, local ring buffer, Mac/browser adapters, sensitivity redaction, and a recall planner with partial-source handling.  ·  risk: Clock skew could join unrelated events, and overly broad extraction could expose secrets. Use signed timestamps, narrow windows, source confidence, local-only default processing, and a visible “saved” transition requiring explicit owner intent.
- cost: Low ongoing storage and negligible relay cost; most requests use compact metadata/text. Vision and relay calls occur only when accessible text is insufficient.  ·  latency: Adds roughly 0.5–3 seconds for ledger query and source reconciliation; no impact on ordinary conversation or browsing.
- security: Reduces retention by design, but introduces a sensitive transient index. Encrypt it locally, exclude password fields and secure inputs, expire aggressively, and omit raw content from logs.
- depends on: A shared pendant/Mac/browser event schema; Local secret-redaction classifier; Bounded active-window and active-tab evidence adapters; Clock synchronization or monotonic event IDs


## What it asked for

### `s7-tz08` (skill) — local_privacy_latch
- does: On a long press of sw0, immediately mute playback, stop microphone capture, set a persistent privacy-latched flag, and drive a distinctive LED pattern. A second long press clears it only after a local confirmation pattern; the flag survives link loss and reboot until explicitly cleared. Emit only a tiny enter/exit state event when LTE-M is available.
- must be on-device because: Muting capture/playback and preventing a hot-mic leak must happen before any relay round trip and must remain effective offline or during a dropped LTE-M link.
- trigger: Long press of the existing user button; optional server push may request lock but never unlock. A short press remains conversation start/end and is ignored while latched.
- storage: One flag plus monotonic transition counter and last-transition timestamp in a small FATFS/NVS record (<256 B); do not store audio.
- RAM budget: ~2–4 kB code/data, <256 B persistent state, and no additional audio buffers; comfortably within 211,608 B application RAM, though Opus already consumes most CPU during duplex.

### `t9-4s7o` (tool) — privacy_convergence_check
- why: The proposed privacy latch needs a read-only, cross-surface verification after a local button press; existing Mac/browser action tools do not provide a single authenticated receipt proving that capture, playback, relay persistence, queued jobs, and browser exposure are all stopped.

```json
{
  "type": "object",
  "properties": {
    "latchId": {
      "type": "string"
    },
    "includeDiagnostics": {
      "type": "boolean",
      "default": false
    }
  },
  "required": [
    "latchId"
  ]
}
```

