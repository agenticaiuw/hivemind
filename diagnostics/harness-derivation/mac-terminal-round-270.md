# Harness derivation — mac-terminal — round 270

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### ""Make my pendant and Mac run a 60-second audio acceptance test, then tell me in one sentence whether the wearable path is good enough to use.""
- **useful because:** This is the fastest path from prototype claims to truth: it exercises the actual nRF9160 capture, Opus uplink, relay transcode, 24 kHz playback, ESP32 resampling and Bluetooth output together, instead of declaring success from separate component logs. It can name the failing segment and leave a timestamped report when the answer is no.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** background for test orchestration and scoring; realtime only to speak the final one-sentence result
- **latency:** Start within 2 seconds; run for 60 seconds; final verdict within 5 seconds of capture end
- **cost:** Usually <$0.01 in relay/model cost; dominant cost is 60 seconds of audio transport and local disk logs, not inference
- **security:** The test records a short microphone sample and may expose it to the relay; require an explicit spoken confirmation for the first run, redact audio from durable reports by default, and retain only metrics plus hashes. Never claim Bluetooth headphone truth unless the Mac/bridge reports it.
- **missing:** A bounded dual-chip serial test runner that can open the two currently attached USB ports and collect framed counters (the granted serial schema is still unresolved); A loopback or synthetic test tone mode so microphone speech need not leave the Mac; Per-segment counters for capture, encode, relay receipt, decode, I2S, ESP32 resample, A2DP queue and audible sink; A report route that stores metrics and a compact verdict, rather than dumping raw UART logs into the model

### ""When I ask what I saved to Safari Reading List, find the newest four items, read their titles and URLs, and tell me which one I should open first; if the browser extension cannot see Reading List, use the Mac to recover it instead of saying it failed.""
- **useful because:** The owner has repeatedly asked this and received failures. It turns a reachable-but-unexposed Safari store into a dependable wearable query, with a graceful second path through the Mac rather than a dead-end browser error.
- **path:** pendant → relay → browser → mac-bridge
- **model tier:** background for extraction and ranking; realtime only for the short spoken answer
- **latency:** Under 10 seconds when Safari is open; under 20 seconds when Mac recovery is needed
- **cost:** <$0.01 per request; dominated by one browser snapshot/read and optional local Mac lookup, not model tokens
- **security:** Reading List URLs/titles are private browsing data. Do not send full page contents or cookies to the relay; return only title, URL, host and saved timestamp if available. Opening a selected item must be a separate explicit action, and destructive Reading List edits require confirmation.
- **missing:** A Safari Reading List adapter (extension API or a narrowly scoped local Mac bridge) that returns item metadata without page contents; A capability probe that distinguishes 'empty list' from 'store inaccessible' from 'extension lacks permission'; A deterministic fallback that asks the Mac agent for the same metadata and reports which source was used; A durable short-lived cache so a transient extension disconnect does not turn a known list into 'none'

### ""Tune the wearable audio for my actual headphones: play a short calibration signal, measure the pendant-to-ESP32 delay and clipping, then save the best 24 kHz playback profile and use it on future calls.""
- **useful because:** The current path spends roughly 87% of one core on encode/decode and crosses 15,625 Hz capture, 24 kHz decode, 31,250 Hz I2S and 44.1 kHz A2DP. A per-device calibration can remove audible clipping, underruns and excessive latency instead of treating fixed constants as universally correct.
- **path:** pendant → mac-bridge → relay → dashboard
- **model tier:** background deterministic DSP/calibration; no expensive model needed except an optional spoken explanation
- **latency:** One-time calibration in 30 seconds; profile application adds no conversational latency
- **cost:** Near-zero API cost; local CPU and a few kilobytes of profile storage dominate
- **security:** Use a synthetic tone by default, not microphone speech. The calibration profile contains device identifiers and timing, not conversation audio. Require confirmation before changing a live call profile and retain the previous profile for rollback.
- **missing:** A synchronized test-tone and timestamp marker emitted at the nRF9160 and observed at the ESP32/A2DP sink; Counters for Opus encode/decode budget, I2S FIFO depth, resampler underruns, clipping and Bluetooth queue delay; A versioned profile store shared by pendant firmware and Mac bridge, with CRC and rollback; An audio calibration route that can run outside an active conversation and publish a compact report

### ""I can't find my iPhone—make it play a distinctive sound, and keep guiding me from the pendant until I confirm I've found it.""
- **useful because:** This is a genuinely physical, everyday problem that no cloud voice agent or Mac-only assistant can solve reliably: the pendant is already on the owner, the Mac can reach the paired iPhone through iPhone Mirroring, and the relay can keep the interaction alive while the owner walks. It turns the hive's distributed reach into a useful recovery action rather than a status report.
- **path:** pendant → relay → mac-bridge → iOS → dashboard
- **model tier:** Realtime for the short interactive guidance loop; deterministic device control and distance/confirmation state should run locally on the Mac and pendant, with no background model needed.
- **latency:** Start the sound within 3 seconds; pendant feedback every 1–2 seconds; stop within 1 second after owner confirmation.
- **cost:** Negligible model cost for a normal use; the Mac/iPhone control and pendant tones dominate. Optional speech guidance is only a few short realtime turns.
- **security:** The command must target only the owner's paired iPhone and never expose its location to the relay. Require a physical button press or spoken confirmation before stopping the alarm if accidental cancellation matters. Do not unlock the phone, send messages, or alter settings as part of recovery.
- **missing:** A typed iOS action that invokes the paired phone's local Find/alert sound through macOS iPhone Mirroring or an approved Apple device-control API; A pendant-local confirmation protocol: button press stops the search, while timeout and link loss leave the sound safely running or retrying according to policy; A low-latency Mac-to-pendant signal for search state and a distinctive non-conversation tone pattern; A session state machine that correlates the exact phone target, start, stop, timeout, and owner confirmation without routing device identifiers through the model


## What it asked for

_Nothing._
## Its own summary

This round produced three distinct owner-facing capabilities. The highest-value one is a one-minute end-to-end wearable audio acceptance test spanning pendant capture, relay Opus, 24 kHz playback, ESP32 resampling, and Bluetooth, with a truthful verdict and failing segment. I also proposed a reliable Safari Reading List query with Mac fallback (because the owner has repeatedly asked and it failed), and per-headphone audio calibration using synthetic tones, timing, FIFO, clipping, and underrun metrics. A shell flight-recorder proposal was rejected as a duplicate of an existing durable execution capsule idea, so I did not rephrase it.

**Biggest unknown:** The attached USB chips are still not inspectable through the granted mac_usb_serial_diagnostics schema: the live inventory has no serial capability. I still need an implemented bounded serial reader or a typed shell-backed bench runner to collect nRF9160/ESP32 counters. I also need the actual /workbench/contexts contract inventoried before treating it as a dependency, and firmware/bridge instrumentation for synchronized tone markers, FIFO/underrun/clipping counters, and 24 kHz path measurements.

