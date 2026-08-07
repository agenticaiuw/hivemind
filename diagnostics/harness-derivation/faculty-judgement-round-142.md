# Harness derivation — faculty-judgement — round 142

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Test my pendant audio.”"
- **useful because:** The owner gets a trustworthy pass/fail answer about the device they wear, rather than discovering a broken microphone or clipped 24 kHz path during an important conversation. It can identify whether the fault is in the nRF pendant, USB serial transport, ESP32 bridge, or relay playback and leave a reproducible report.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal
- **model tier:** background for DSP analysis and report generation; realtime only for the short spoken result
- **latency:** Under 60 seconds for a complete wired test; spoken verdict within 5 seconds of the final sample
- **cost:** Usually <$0.01 per invocation; most work is local serial capture and deterministic DSP, with model tokens only for interpreting anomalies
- **security:** Raw test audio should remain on the Mac and be deleted after metrics; only aggregate SNR, packet-loss, latency, and a fault report leave the device. No microphone test without an explicit spoken/button start.
- **missing:** A privileged Mac serial/audio test runner for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; A loopback/test-tone command in pendant and ESP32 firmware; A typed /pipeline/audio diagnostic result schema and a report route

### "“I just finished that meeting—turn what I said and what is in my notes into the follow-ups, but don't send anything.”"
- **useful because:** Within two minutes of a meeting, the owner receives a prioritized, reviewable set of action items with owners, dates, source quotes, and ready-to-edit drafts. The pendant can read the three highest-impact items while the Mac gathers local Notes/Calendar context and the browser checks private project pages; no one has to reconstruct commitments later.
- **path:** pendant → mac-planner → browser-extension → relay-realtime
- **model tier:** Background model for extraction and reconciliation; realtime model only to narrate the resulting queue or answer a follow-up
- **latency:** A first queue in 90 seconds, with later browser enrichment arriving asynchronously
- **cost:** About $0.03–$0.10 per meeting depending on transcript length and number of private pages; local note extraction dominates no API cost
- **security:** Meeting audio/transcript and private page data stay on the Mac unless the owner explicitly enables relay processing. Drafts are never sent; creating a reminder is allowed, but assigning work or sending mail requires confirmation. Every item needs a source pointer and confidence.
- **missing:** A local meeting-end trigger tied to Calendar and a transcript/Notes collector; Cross-surface action-item schema with source spans and uncertainty; A pendant queue player with per-item accept/edit/reject controls

### "“I’m starting a 25-minute focus sprint—keep me on track and only interrupt me if something truly urgent happens.”"
- **useful because:** One physical press creates a coherent focus mode instead of a collection of settings: the Mac quiets nonessential notifications and opens the exact work set, the browser pauses selected page watches, and the relay holds a ranked urgent queue. At the end, the pendant gives a brief progress/result check and restores what was changed, so the owner can work without negotiating with every surface.
- **path:** pendant → mac-planner → browser-extension → relay-realtime
- **model tier:** Background model chooses the work set and urgency ranking; realtime model handles only interruption speech
- **latency:** Focus starts in 2 seconds; interruption decision under 5 seconds; end-of-sprint recap under 10 seconds
- **cost:** <$0.02 per sprint; scheduling and notification state are local/deterministic, with model use only for ranking ambiguous events
- **security:** Never hide safety or direct human escalation. Store only mode timestamps and event categories, not message contents by default. Browser watches must be paused transactionally and restored from a before-state; any outbound action still needs confirmation.
- **missing:** Pendant long-press mode event and offline state latch; A Mac notification/focus-mode adapter with reversible before-state receipts; A relay urgency policy and browser-watch pause/resume contract

### "“That sounded wrong—let me correct what you heard before you do anything.”"
- **useful because:** Voice systems fail most dangerously at the boundary between hearing and acting. The pendant can replay or display the short raw utterance, the relay presents a compact transcript with uncertain words highlighted, and a single button gesture accepts the correction or cancels the intent before it reaches Mac/browser execution. This makes voice useful in noisy real life without forcing the owner to repeat an entire command.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Realtime model for low-latency transcription/repair; background model only for resolving domain names or ambiguous entities
- **latency:** Correction prompt within 1.5 seconds; accept/cancel within 3 seconds; no action dispatched until the gate resolves
- **cost:** About $0.005–$0.03 per correction, dominated by audio/transcript tokens; local replay and button handling are free
- **security:** The raw utterance is sensitive and should expire quickly. Never send a low-confidence destructive intent downstream. Require explicit confirmation for mail, deletion, purchases, or messages even after correction.
- **missing:** A transcript-confidence plus alternative-hypotheses event schema; A pendant-local cancel/accept gesture that survives link loss; A pre-execution speech correction gate shared by relay, Mac, and browser

### "“Use my pendant through the Mac while it’s plugged in—don’t wait for LTE.”"
- **useful because:** The wearable becomes useful today in the exact state it is physically in: USB serial carries button events and audio between the pendant/ESP32 and the Mac, while the relay supplies the conversation and the Mac performs local actions. The owner can wear it around the desk and keep continuity instead of silently falling back to a laptop UI whenever cellular registration is absent.
- **path:** pendant → mac-terminal → mac-planner → relay-realtime
- **model tier:** Realtime model for the conversation; deterministic local bridge for framing, buffering, and reconnection
- **latency:** Button-to-audio response under 500 ms on USB; reconnect after cable interruption under 5 seconds
- **cost:** No additional model cost beyond normal voice; local bridge uses negligible CPU and disk for bounded buffers
- **security:** USB pairing must be explicit and tied to the device identity; do not expose serial audio to unrelated local processes. Buffer encrypted audio only transiently, wipe on disconnect, and make a physical cancel gesture always available.
- **missing:** A Mac USB pendant transport that maps both live serial ports into the relay session; Offline-safe framing, reconnect, and backpressure handling for nRF9160↔ESP32 audio; A device registry/session route that treats USB attachment as an authenticated transport even without LTE

### "“Make the pendant adapt to where I am so I can hear and be heard without fiddling with settings.”"
- **useful because:** The owner gets intelligible speech in a café, on a windy walk, or beside a fan without manually changing profiles. The pendant/ESP32 measures local noise, the Mac can provide a calibration reference while tethered, and the relay learns only which acoustic profile worked—not private room audio.
- **path:** pendant → mac-terminal → mac-planner → relay-realtime
- **model tier:** Deterministic DSP and a small local classifier for profile selection; realtime model is not needed for the control loop
- **latency:** Profile change within 300 ms of a sustained acoustic change; no audible interruption longer than one audio frame
- **cost:** Near-zero API cost; local DSP uses a few kilobytes of RAM and modest MCU cycles
- **security:** Never upload ambient recordings. Persist only coarse profile statistics, with an owner-controlled opt-out. A hard physical mute must override adaptation.
- **missing:** Firmware-controlled AGC/noise suppression/echo-cancellation profiles on the nRF9160 and ESP32 path; A bounded ambient-level/quality telemetry event, not raw audio; A Mac-tethered calibration command and relay profile synchronization

### "“Before I click or reply to something suspicious, warn me in one sentence and tell me why.”"
- **useful because:** The owner gets an active phishing and impersonation guard at the moment of risk, not a generic security lecture later. The browser bridge supplies the actual URL, sender, redirect chain, and page context; the Mac can compare it with the owner’s known account context; the pendant speaks a short warning and offers cancel or inspect, while safe pages remain silent.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Cheap background classifier for URL/message risk; realtime model only for the spoken explanation when the risk is high or ambiguous
- **latency:** A preliminary warning in under 400 ms before navigation or submission; deeper inspection may arrive asynchronously but must not block ordinary browsing
- **cost:** Usually <$0.01 per inspected risky event; URL and DOM metadata dominate, not audio
- **security:** Private page content and message text must stay local by default. Never claim a page is safe—report evidence and uncertainty. Blocking a navigation is reversible; sending credentials, mail, or payment data remains confirmation-gated.
- **missing:** A browser pre-navigation/pre-submit interception hook with a cancellable hold; Local URL/identity/redirect reputation and account-context evaluator; A typed risk receipt that the pendant can summarize without exposing page contents

### "“When I’m carrying something or driving, let me approve safe things with the pendant and keep everything else pending until I can look.”"
- **useful because:** The owner gets a genuinely hands-free operating mode rather than either unsafe voice automation or total silence. A physical gesture can approve a pre-declared low-risk action such as creating a reminder or opening a page; ambiguous, destructive, or externally visible actions become a compact pending queue that the Mac presents later with full evidence.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Deterministic policy engine for gesture/action classes; background model ranks and summarizes deferred items; realtime model speaks only the immediate confirmation
- **latency:** Gesture acknowledgement under 250 ms; safe action under 2 seconds; deferred queue available on the Mac within 10 seconds of reconnect
- **cost:** <$0.01 per event; most policy and queue work is local/server deterministic
- **security:** Gesture classes must be explicit and learnable, never inferred from a noisy accidental press. No sending, purchasing, deletion, credential use, or irreversible browser action from a blind gesture. Queue records must be encrypted and expire.
- **missing:** A firmware gesture vocabulary with accidental-press rejection and offline persistence; A shared risk-class policy consumed identically by relay, Mac, and browser; A deferred-action inbox with evidence snapshots and reconnect reconciliation


## Changes it proposed to its own stack

### `integration` — Wire a user-invoked wired-pendant diagnostic transaction across the live USB serial devices: the Mac runner sends synchronized tone/record commands to the nRF9160 pendant and ESP32 bridge, POSTs timestamped metrics to /pipeline/audio, and emits one durable receipt containing sample rate, packet loss, round-trip latency, and fault localization. Keep raw samples local and make the transaction cancellable.
- **owner gets:** They can know in under a minute whether the wearable will actually hear and speak before relying on it, and can hand a concrete fault report to support instead of saying “the audio was weird.”
- effort: Medium: serial protocol additions, deterministic DSP, one typed route/result, and a small spoken receipt.  ·  risk: A bad test command could leave the bridge streaming or consume the serial port; use a lease, timeout, and finally-close, with a local reset command. Never treat a missing sample as a healthy zero.
- cost: Negligible API cost; roughly 1–2 minutes of Mac CPU and temporary disk per test.  ·  latency: Adds up to 60 seconds only when explicitly requested; no effect on normal voice.
- security: Raw microphone fixtures remain local and are deleted; aggregate metrics can be retained without personal audio.
- depends on: A serial test protocol for both chips; A /pipeline/audio diagnostic schema; Mac access to the two currently connected USB serial ports


## What it asked for

_Nothing._
## Its own summary

Round 142 produced five owner-facing proposals, including the highest-value immediate one: make the physically connected pendant usable over USB through the Mac even without LTE registration. I also proposed a one-minute end-to-end audio self-test with fault localization, a post-meeting follow-through queue (recorded as close to an existing idea), a reversible focus sprint, and a pre-execution voice correction gate. The audio wiring change was accepted as a concrete integration change. What I still need is implementation of the USB transport/session layer, the pendant+ESP32 diagnostic framing and 24 kHz metrics, and a shared confidence/correction gate before /execute. I do not need Accessibility or Screen Recording for these; AppleScript and the serial-attached hardware are sufficient.

**Biggest unknown:** The exact UART/audio framing and acceptance criteria on the two live serial devices remain unknown. Until those are specified, I cannot honestly claim the USB conversational path or diagnostic can be implemented safely. The browser/Mac surfaces are online, but UI-derived success remains untrusted while Accessibility/Screen Recording stays unavailable.

