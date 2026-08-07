# Harness derivation — faculty-perception — round 75

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-agent-observation-2026-08-07-r75** — Live Mac observation at 2026-08-07T12:58Z: AI Pendant Agent is running, relay reachable and mac bridge online, but Accessibility and Screen Recording are not granted; inputReachability is failed and UI actions cannot be trusted. Browser extension home-chrome is offline with 7 pending commands. Three durable browser sessions exist (UTC time.is plus two Selenium form probes).
  - evidence: GET /ops/status, GET /observe, GET /browser/status all returned 200; /observe explicitly reports trusted=false, screenRecording=false, uiActionsWillReachTheScreen=false, browser online=false and pendingCommands=7.
- **audio-pipeline-observation-2026-08-07-r75** — The relay and Mac bridge have completed 24 kHz mono s16le PCM rendering for a prior response (75,734 bytes, 1,578 ms, 0 clipped samples), and the pendant pipeline records 24 kHz TTS delivery. The pendant capture remains 15,625 Hz/16 kbps Opus while playback is 24 kHz; measured LTE-M half-duplex contention previously dropped 388 uplink packets (~7.8 s) during simultaneous speech.
  - evidence: GET /pipeline live response includes TTS done metadata sampleRate=24000, format=s16le, clippedSamples=0 and relay_result done; get_hardware_spec(audio/network) reports capture/playback paths and measured contention.
- **timezone-conflict-2026-08-07-r75** — The owner memory projection says authoritative timezone America/Chicago, while live Mac /machine-context reports America/New_York. Any schedule interpretation must treat the owner timezone as Chicago until explicitly reconciled; the Mac timezone is not safe as the authority.
  - evidence: discover(owner) remembered.timezone=America/Chicago; GET /machine-context returned machine.timezone=America/New_York.

## Capabilities it proposed

### "Before I rely on it, tell me what the pendant, Mac, relay, and browser can actually verify right now, what is stale or disconnected, and which parts of my request are blocked—then keep watching until the truth changes."
- **useful because:** Today the system can return convincing success receipts while the Mac cannot reach the screen, and browser commands can queue while the extension is offline. A cross-surface reality report prevents the owner from acting on fiction and turns reconnection or permission changes into a useful notification.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** background / deterministic aggregation first; use the expensive realtime model only to phrase a short spoken answer when the owner asks. No LLM is needed to classify route health, timestamps, permissions, pending queues, or audio metadata.
- **latency:** On demand under 1 second from cached observations; refresh Mac and relay probes within 3 seconds. Re-check on bridge heartbeat, browser heartbeat, pipeline event, pendant telemetry, and permission-status change; quiet notification only after a state transition, not every poll.
- **cost:** Near-zero API cost for aggregation and event-driven checks; occasional short realtime phrasing is under roughly $0.01 per spoken report. Storage is a small append-only state/transition record per surface.
- **security:** Expose only capability state, timestamps, error classes, and provenance—not page contents, account data, audio, or secrets. Browser session URLs may be sensitive and should be redacted by default. Never infer that an action happened from a queued command or optimistic receipt; require a typed result or device acknowledgement.
- **missing:** A single typed observation schema spanning pendant telemetry, relay reachability, Mac permissions/inputReachability, browser heartbeat/queue, and pipeline delivery acknowledgements; State-transition subscription or inexpensive polling scheduler that expires stale observations and labels them stale; Dashboard and voice response that distinguish verified, stale, queued, failed, and unknown

### "Prepare the sensitive action everywhere, but do not let it happen until I physically confirm on my pendant; show me exactly what is waiting, and tell me if the confirmation expired or was used somewhere else."
- **useful because:** Today approval is chiefly a dashboard/software event, while the pendant is the one surface physically with the owner. A short-lived, device-bound confirmation would let the owner approve a prepared mail, purchase, browser submission, or Mac change without trusting a possibly stale screen, and would make replay or accidental approval materially harder.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard → unified
- **model tier:** Background deterministic orchestration for nonce creation, state, expiry, and receipt verification; realtime only speaks the concise pending/confirmed status. No expensive model should decide whether a cryptographic confirmation is valid.
- **latency:** Prepare work asynchronously; confirmation should propagate in under 2 seconds when LTE-M is available. Expire a challenge after 60 seconds or on disconnect, and surface a clear pending state rather than guessing.
- **cost:** Negligible model/API cost; small durable relay records for challenge, target hash, expiry, and one-time receipt. Hardware bill is unchanged if the existing button is used, aside from firmware work.
- **security:** Bind each challenge to an exact normalized action plan, target account/session, device identity, and monotonic expiry; sign or MAC the pendant response and reject reuse, cross-session forwarding, and altered plans. Do not put secrets or full page contents on the pendant. Require an explicit spoken/dashboard preview before arming; destructive actions remain confirmation-required.
- **missing:** A per-pendant key identity and secure challenge-response primitive (secure element or protected modem/TF-M storage); Firmware support for a deliberate long-press/chord confirmation with local LED/audio distinction between arm, confirm, reject, and expired; Relay protocol and durable one-time challenge ledger; Mac/browser action executors that consume only a verified challenge receipt and expose the exact target hash in their audit receipt; Recovery UX for LTE outage, lost pendant, and duplicate button events

### "When something goes wrong, show me the exact cross-device timeline of what the pendant, relay, Mac, and browser each knew at the moment—not a rewritten summary—and identify the first unverified claim."
- **useful because:** The system spans asynchronous devices and currently mixes live observations, stale queues, optimistic receipts, and delayed audio. The owner cannot today audit why an answer or action was believed. A replayable evidence timeline would make failures diagnosable and let them trust only claims with a source and freshness boundary.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard → unified
- **model tier:** Deterministic event storage, clock alignment, hash chaining, and gap detection first; use a cheaper background model only to summarize a selected incident. Realtime is unnecessary except for a short spoken explanation requested by the owner.
- **latency:** Append transport and action evidence without delaying the hot path (target under 5 ms locally and fire-and-forget relay upload). Produce a replay in under 3 seconds for a normal turn; explicitly mark missing intervals instead of reconstructing them.
- **cost:** Low API cost; compact metadata is much cheaper than retaining raw audio or screenshots. A configurable 7-day incident ring buffer would be on the order of megabytes per day depending on event rate; retain payloads only when the owner pins an incident.
- **security:** Hash-chain metadata and redact secrets, page bodies, raw audio, and screenshots by default. Store sensitive evidence locally where possible, encrypt relay records, and require explicit pin/export before sharing an incident. Device clocks are not trusted: preserve monotonic sequence and receipt time alongside wall time.
- **missing:** A common event envelope with source identity, monotonic sequence, observed-at and received-at times, freshness/verification class, and parent operation ID; Clock-offset and reconnect-gap tracking across pendant, relay, Mac, and browser; Tamper-evident append-only incident ring buffers with retention and owner export/delete controls; A dashboard replay UI that distinguishes observed, acknowledged, inferred, queued, and failed states; Firmware and browser adapters that emit acknowledgements and explicit negative evidence rather than only success events


## Changes it proposed to its own stack

### `relay` — Add an adaptive half-duplex audio scheduler shared by pendant firmware and relay: relay advertises downlink playback windows and frame budget before sending 24 kHz PCM; pendant pauses or lowers uplink Opus capture during those windows, buffers only a bounded pre-roll, then resumes with an explicit gap marker. Relay records per-turn uplink loss, downlink backlog, and playback acknowledgements, and falls back to text/short TTS when the LTE-M budget is exceeded. Mac bridge supplies the existing 24 kHz duration/size metadata and pipeline events.
- **owner gets:** The owner can hear complete replies without sacrificing the next spoken turn. The current measured link dropped about 7.8 seconds of uplink when speaking over playback; this makes a wearable conversation feel deaf exactly when it matters.
- effort: Medium-high: protocol versioning and firmware/relay integration, with a simulator test matrix for interruption, reconnect, and bounded buffering.  ·  risk: A bad scheduler could clip the owner's first words or deadlock after reconnect. Recover with a watchdog, sequence-numbered gap markers, maximum 2-second buffering, and a legacy mode negotiated per connection. Do not claim speech completeness unless both sides acknowledge frame ranges.
- cost: No material API cost; modest LTE airtime reduction. Firmware RAM impact should stay under ~8–16 kB for a bounded PCM/Opus queue and counters, but must be measured against 211,608 B application RAM. Cloud storage adds only compact per-turn telemetry.  ·  latency: Adds one scheduling/control exchange (target <100 ms) and may delay playback a fraction of a frame; improves effective conversational latency by avoiding retransmission and missing speech.
- security: Only sequence numbers, codec metadata, and transport counters leave the device beyond existing audio. Keep raw audio retention unchanged; authenticate scheduler control frames with the existing WebSocket session.
- depends on: Pendant firmware 24 kHz playback path and frame acknowledgements; Relay durable audio and pipeline telemetry; Mac bridge 24 kHz TTS metadata; A simulator test for simultaneous uplink/downlink contention


## What it asked for

_Nothing._
## Its own summary

Round 75 established fresh cross-surface facts: relay and Mac bridge are reachable; the Mac agent is running but Accessibility and Screen Recording remain false, so UI receipts are untrustworthy; Chrome extension is offline with 7 queued commands; 24 kHz PCM TTS delivery is verified (75,734 bytes, 0 clipped samples), while LTE-M contention has previously lost ~7.8 seconds of uplink. I recorded those facts and the Chicago-vs-New-York timezone conflict. I proposed a connective reality report and a new adaptive half-duplex audio scheduler to prevent speech loss during playback.

**Biggest unknown:** I still cannot directly verify current pendant firmware state, live radio/audio counters, offline continuity acknowledgements, or whether the queued browser commands eventually execute; the granted server-side views expose history and bridge state but not authoritative device-local truth. The owner must also resolve the Mac TCC grant manually before any screen interaction can be believed.

