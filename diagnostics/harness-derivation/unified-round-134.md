# Harness derivation — unified — round 134

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I’m in a meeting, let me say “mark that” or press the pendant button; capture the last few seconds of conversation, identify the decision/commitment, and prepare a reminder or note with the meeting and source timestamp—without sending anything."
- **useful because:** The owner can record a commitment at the exact moment it happens instead of trying to remember it later. The Mac knows the meeting and calendar context, the browser can supply the meeting page, and the pendant supplies a private physical marker and audio.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** background for transcript extraction and classification; realtime only for the spoken acknowledgement
- **latency:** Button acknowledgement under 300 ms; draft note in 10–30 s after the meeting segment is available.
- **cost:** ~$0.01–$0.08 per marked segment depending on audio duration and transcription; storage and Mac CPU dominate for long clips.
- **security:** Audio leaves the Mac only when explicitly marked; retain a short encrypted local ring buffer and upload only the selected window. Never auto-send messages or create external commitments; reminder creation can remain reversible.
- **missing:** pendant-local rolling audio marker and secure clip export; meeting audio source selection and consent UX; timestamped cross-surface context joiner; commitment extraction endpoint with provenance

### "When I say “bring me back to what I was doing,” use the pendant to identify my last active Mac project, open tabs, unsent drafts, and unfinished jobs, then speak one concise resume plan and put the exact workspace back on my Mac."
- **useful because:** Interruption recovery is the highest-frequency failure in daily computer work. It requires the worn device to identify the request, the relay to retain continuity while the owner is away, and the Mac/browser to restore the real state rather than merely summarize it.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** background model builds a compact interruption checkpoint; realtime model only interprets the request and confirms the selected checkpoint
- **latency:** Spoken answer within 2 s; workspace restoration within 15 s, with a visible list of every reopened tab and resumed job.
- **cost:** ~$0.005–$0.03 per recovery; mostly local Mac work, with model cost only for checkpoint ranking.
- **security:** Checkpoint data may include private tabs and drafts. Encrypt at rest, expire snapshots quickly, and require confirmation before reopening or exposing sensitive tabs on a shared display. Never submit drafts.
- **missing:** cross-surface interruption checkpoint schema; safe tab/draft redaction and restore policy; pendant request-to-checkpoint identity binding; idempotent Mac/browser workspace restore

### "While I’m wearing the pendant, tell me when a time-sensitive change occurs in my logged-in work or travel pages, explain why it matters in one sentence, and let me ask “show me” to open the exact authenticated page and evidence on my Mac."
- **useful because:** A daily digest is too late for a gate change, expiring approval, or urgent work item. The browser holds credentials, the relay can watch while the Mac sleeps intermittently, and the pendant can interrupt only for high-confidence, high-impact changes.
- **path:** relay-realtime → browser-extension → mac-planner → pendant → dashboard
- **model tier:** cheap background model for polling/diffing and severity ranking; realtime only for the owner’s follow-up conversation
- **latency:** Detect within the configured cadence (1–15 min); speak only after confidence and urgency thresholds pass; open evidence within 5 s of “show me.”
- **cost:** ~$0.02–$0.20/day for a handful of pages; browser session time and polling dominate rather than realtime tokens.
- **security:** Use explicit site allowlists and quiet hours; never infer urgency from untrusted page text alone. Include URL, timestamp, and before/after excerpt; do not click destructive controls without confirmation.
- **missing:** always-awake authenticated watcher independent of Mac polling; semantic diff with urgency/confidence policy; pendant interruption budget and quiet-hours enforcement; evidence deep-link from alert to browser tab

### "When I press the pendant and say “remember this,” save a synchronized snapshot of what I’m hearing, the Mac camera sees, my active browser context, and the current time; later I can ask “what was that thing I remembered?” and get the original evidence, not an AI paraphrase."
- **useful because:** This gives the owner a searchable memory for fleeting real-world moments—an object, whiteboard, receipt, or conversation—without requiring them to stop and organize it. No single node can capture the physical audio cue, Mac visual context, authenticated page, and durable retrieval together.
- **path:** pendant → mac-vision → browser-extension → relay-realtime → dashboard
- **model tier:** Realtime only for the short confirmation; a cheaper background model indexes and labels the captured bundle.
- **latency:** Confirmation under 500 ms; capture under 3 s; later retrieval under 2 s for indexed memories.
- **cost:** ~$0.01–$0.10 per memory depending on image/audio duration; local capture dominates and cloud indexing is the main API cost.
- **security:** The owner explicitly marks capture, but bystanders may be recorded. Show recording state on the pendant, encrypt media, apply short default retention, and provide one-command deletion. Never silently capture on wake words.
- **missing:** synchronized pendant/Mac capture clock and bundle format; Mac camera capture route with explicit foreground consent; multimodal memory index retaining original evidence links; physical capture indicator and deletion control

### "Let me say “translate for me” to the pendant during a conversation; speak the other person’s words in my chosen language through the headphones and speak my reply back in theirs, while showing the transcript and a pause/delete control on the Mac."
- **useful because:** The pendant becomes a private, hands-free interpreter in the moment, while the Mac and relay provide the compute and transcript display that the pendant cannot. It is useful in travel, service encounters, and accessibility situations where taking out a phone is disruptive.
- **path:** pendant → relay-realtime → mac-planner → dashboard
- **model tier:** Realtime speech model for low-latency translation; background model only for transcript cleanup and session summary.
- **latency:** First translated phrase within 1.5 s; maintain turn latency below 2 s where the link permits, with explicit “repeat” handling.
- **cost:** ~$0.03–$0.20 per minute depending on language pair and audio duration; realtime audio tokens dominate.
- **security:** Translation requires sending live speech to the relay. Require a physical start gesture, show active-listening state, do not retain audio by default, and provide a hard local mute latch.
- **missing:** language-selection and turn-taking protocol; streaming translation audio path distinct from ordinary answer TTS; local mute/consent state shared across pendant and relay; transcript redaction and zero-retention mode

### "When I say “make this safe to share,” have the browser and Mac inspect the selected document, image, or webpage for secrets and personal data, produce a redacted copy plus a plain-English list of every removed field, and wait for my approval before exporting or sending it."
- **useful because:** The owner can safely share work artifacts without manually hunting for account numbers, private URLs, API keys, or unrelated personal details. Browser credentials, local files, and the pendant’s approval gesture each contribute capabilities that no one surface has alone.
- **path:** pendant → browser-extension → mac-planner → mac-vision → dashboard → relay-realtime
- **model tier:** Background model for content classification and redaction proposals; realtime only for the spoken approval exchange.
- **latency:** Preview in 5–15 s for a normal document or page; never export until the owner approves the exact diff.
- **cost:** ~$0.02–$0.15 per artifact; OCR and document transfer dominate for large files.
- **security:** Sensitive source content must be processed locally whenever possible. Redactions are not irreversible until export; preserve the original, show before/after evidence, and require confirmation for every destination.
- **missing:** local document/image extraction and redaction engine; secret/PII policy configurable per destination; tamper-evident before/after artifact diff; pendant approval bound to the exact redaction hash


## Changes it proposed to its own stack

### `integration` — Add a hardware-in-the-loop “wear test” that opens both live USB serial devices (/dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA), starts a controlled pendant↔ESP32 audio session, timestamps UART/I2S diagnostics, injects spoken test tones and packet contention, and emits a signed report covering 24 kHz decode, 31.25 kHz wire clock, 44.1 kHz A2DP output, underruns, latency, and packet loss. Make it runnable from the Mac agent and attach the report to the relay job receipt.
- **owner gets:** The owner gets a trustworthy answer that the device they are wearing actually works end to end, rather than another software-only green check. It turns the currently connected hardware into a repeatable pre-call test and catches regressions before a real conversation.
- effort: Medium-high: serial discovery, test firmware command, ESP32 telemetry, synchronized clocks, report schema, and Mac job integration.  ·  risk: A bad test command could leave the audio bridge streaming or wedge a serial port; use exclusive locks, bounded timeouts, and a reset/reopen recovery path. Never run while a real call is active.
- cost: No per-call API cost; roughly 1–2 minutes of Mac CPU and USB power per test. Engineering cost is the telemetry and test harness.  ·  latency: No runtime impact; adds 30–120 s before a call when explicitly requested.
- security: UART logs can contain transcripts or identifiers; default to metrics-only, redact payloads, and require explicit opt-in for raw audio/log retention.
- depends on: A Mac serial tool or allowlisted shell intent for the two known USB paths; A firmware diagnostic command that can run loopback/tone tests without LTE registration; ESP32 bridge counters for resampler and A2DP underrun status; 24 kHz acceptance thresholds and report receipt integration

### `hardware` — Replace the prototype pendant enclosure/electronics with a production wearable containing a low-power always-on DSP, dual microphones with beamforming, a vibration motor, a capacitive mute switch, IMU, fuel gauge, and secure-element identity, while retaining the nRF9160 radio as the connectivity module. Expose an encrypted event stream for explicit capture, mute, motion, battery, and haptic acknowledgement.
- **owner gets:** The owner gets intelligible speech in noisy places, a physical privacy guarantee, feedback without looking at the device, reliable battery warnings, and a trustworthy approval/mute action. These are prerequisites for translation, evidence capture, and safe approvals to work outside a desk.
- effort: High: industrial design, RF/audio co-design, firmware drivers, acoustic tuning, certification, and a staged prototype run.  ·  risk: More components create failure modes and battery drain. Keep a fallback single-mic mode, hardware mute that cuts mic power, watchdog recovery, and the existing USB test fixture for bring-up.
- cost: Prototype NRE likely $20k–$80k; early BOM roughly $35–$75 per unit, with an estimated 10–30 mA average draw depending on DSP and radio duty cycle. No additional API cost.  ·  latency: Local wake/mute/haptic acknowledgement can be under 50 ms; beamforming adds less than 10 ms. Battery life may decrease unless the DSP handles always-on detection.
- security: A secure element and physical mute improve device identity and privacy, but add key-management and supply-chain requirements. Firmware updates must be signed and rollback-protected.
- depends on: A finalized 24 kHz audio acceptance target; Production pendant industrial/acoustic design; Firmware event protocol for mute, haptic, capture, and battery telemetry; Relay pairing and device identity lifecycle


## What it asked for

_Nothing._
