# Harness derivation — mac-terminal — round 201

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Make the pendant sound like a real telephone, not a narrow-band robot voice, and keep it intelligible if the link or CPU cannot sustain the best mode.”"
- **useful because:** This is the owner's explicitly scheduled deliverable and is testable today with the nRF9160 and ESP32 attached over USB. A negotiated 24 kHz superwideband path would make every conversation materially easier to understand, while a measured downgrade prevents stalls instead of merely claiming a codec is enabled.
- **path:** pendant → relay-realtime → mac-planner → new-surface
- **model tier:** Realtime only for codec/session negotiation and short spoken replies; background/bench analysis uses a cheaper model or deterministic signal metrics.
- **latency:** Under 120 ms mouth-to-ear in the steady state; mode negotiation under 500 ms; downgrade within one frame-budget violation and recovery only after 2 seconds of clean timing.
- **cost:** Negligible inference cost for negotiation; bench work is dominated by firmware/DSP engineering and USB capture storage. LTE bandwidth and battery use rise in 24 kHz mode and should be measured rather than guessed.
- **security:** Audio remains sensitive. USB captures must be explicitly labeled and auto-expire; relay receives only encoded frames and session metadata, not raw diagnostic audio, unless the owner requests a capture.
- **missing:** End-to-end 24 kHz codec/framing implementation on nRF9160 and ESP32 bridge; Capability advertisement and renegotiation messages across the relay; A synchronized loopback/latency and packet-loss test harness; A user-visible mode indicator that does not conflict with existing recording and action-status LED states

### "“When the bench voice test fails, tell me exactly which turn, firmware build, and transport event caused it, and hand me a replayable report.”"
- **useful because:** A raw UART dump is not actionable. Correlating the owner's spoken turn with both chip logs, pipeline frame counters, the Mac job receipt, and the git commit turns an intermittent wearable failure into a report someone can reproduce. It uses the hardware that is physically connected now, not a hypothetical LTE registration.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → faculty-perception → faculty-judgement
- **model tier:** Deterministic timestamp/frame-counter joins first; use a cheap background model only to summarize the causal timeline and suggest the next test. Realtime should not be spent on log summarization.
- **latency:** Start capture within 250 ms of a turn/session start; finalize a report within 10 seconds of failure or explicit stop. Never delay live audio for logging.
- **cost:** Low API cost (mostly local files and integer counter joins). Storage is bounded by rotating compressed UART/audio metadata logs; raw audio should be opt-in and short-lived.
- **security:** Reports may contain spoken private content and source paths. Default to counters, errors, hashes, and short redacted excerpts; require an explicit request to attach raw audio or full UART output. Git diffs and environment values must be scrubbed for secrets.
- **missing:** A common monotonic clock/turn ID injected into nRF, ESP32, pipeline events, and Mac receipts; A host-side bounded dual-UART reader and framing parser (currently only capture shell scripts exist); A report schema with causal links and replay commands, plus a retention/secret-redaction pass; A one-command replay runner that can feed captured frames to the bridge without transmitting them externally

### "“If something I asked the Mac to do fails while I’m away, tell me what actually happened, whether it changed anything, and whether retrying is safe—without making me inspect logs.”"
- **useful because:** Current job status can say failed but cannot expose the exit code, process duration, effective working directory, or whether a partial mutation occurred. A concise spoken postmortem would let the owner decide immediately instead of guessing from a generic error, while preserving the owner's deliberate maximum-access policy.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → faculty-perception → faculty-judgement
- **model tier:** Deterministic receipt extraction and risk/retry classification first; a cheap background model summarizes only ambiguous stderr. Realtime speaks one short sentence when the owner asks or when a queued failure is urgent.
- **latency:** Postmortem available within 2 seconds for completed jobs; no added latency to execution. If a command is still running, report age and live state rather than fabricate failure.
- **cost:** Near-zero inference for structured fields; occasional small summarization call for stderr. Local durable records grow by bounded, redacted receipts rather than full environment dumps.
- **security:** Never speak or persist inherited secrets. Store an environment fingerprint and explicit redaction list, not env values. Mark mutation uncertainty honestly; a failed shell command is not proof that nothing changed.
- **missing:** Capture shell exit code, signal, pid, start/finish/duration, effective cwd, and command hash in the receipt; Join every /execute job to its action ledger and close the ledger on success/failure; Add a bounded failure classifier that distinguishes timeout, signal, missing binary, permission, transport, and nonzero exit; Expose a compact owner-facing postmortem endpoint and let truthful_action_status_beacon announce only states that are actually durable

### "“Before I rely on the pendant, certify that the whole voice path is healthy and tell me what it can sustain right now.”"
- **useful because:** Today the owner can start a conversation, but cannot obtain a trustworthy preflight verdict across the worn chip, ESP32 audio bridge, Mac USB path, relay pipeline, and speaker/microphone timing. A one-command spoken certification would catch a bad cable, clock drift, underruns, excessive round-trip latency, or a codec mode that only appears healthy until conversation starts. It would make the system dependable rather than merely available.
- **path:** pendant → relay-realtime → mac-terminal → mac-planner → faculty-perception → faculty-judgement
- **model tier:** Deterministic local signal tests and counter thresholds do the certification; use a small background model only to translate failures into a short diagnosis. Realtime is used only to speak the final verdict.
- **latency:** Cold certification under 15 seconds; a quick health check under 2 seconds. It must not open or record the microphone beyond a generated test signal and an explicitly bounded loopback sample.
- **cost:** Minimal model cost; local CPU and a few seconds of USB/radio airtime. Persist only aggregate metrics and a short certificate, not raw test audio.
- **security:** The test must use generated tones or synthetic speech, never silently capture the owner's surroundings. Certificates may contain device identifiers and network quality, so retain them locally with expiry and redact identifiers from spoken output.
- **missing:** A cross-device test protocol with a nonce, monotonic timestamps, frame counters, and signed result packets; A Mac-side bounded serial/USB harness that can drive and read both currently connected chips; the granted diagnostic schema is unresolved because no serial capability is implemented; A deterministic acceptance matrix for latency, jitter, loss, underruns, clock drift, and microphone/speaker loopback; A preflight certificate route consumed by the relay and pendant, with explicit stale/unknown semantics rather than optimistic health

### "“When I’m in a meeting or presenting, keep the pendant from speaking aloud, queue the answer, and let me release it when it is socially safe.”"
- **useful because:** A wearable that suddenly speaks a private answer in a conference room is unusable. The Mac can infer a meeting/presentation state from the active app, calendar context, and browser session without opening a microphone; the relay can hold the response; the pendant can truthfully indicate queued audio and release it on an explicit button action.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → faculty-perception
- **model tier:** Deterministic state and calendar/app signals first; realtime only handles the live response. No model is needed to decide a configured privacy state.
- **latency:** Privacy state changes within 1 second of a reliable Mac/browser event. Queued responses must remain bounded and expire rather than replay unexpectedly.
- **cost:** Negligible inference cost; small durable queue and event traffic. The owner may opt into calendar metadata, but no meeting audio or page contents are required.
- **security:** Meeting detection must be privacy-minimal and fail closed for speech output when state is unknown during a suspected call. Never infer or transmit meeting content. Explicit release is required for queued private responses.
- **missing:** A shared privacy-state protocol with states quiet, meeting, presenting, safe-to-speak, and unknown; Mac/browser event producers for active call/presentation state and a lease with freshness/expiry; Relay-side response escrow keyed to turn ID with cancellation and expiry; A pendant release/readout interaction that coexists with recording and existing truthful status patterns

### "“Run the task with full Mac access, but when you report back through the pendant, automatically remove credentials and tokens while keeping the complete result available locally.”"
- **useful because:** Maximum execution access and safe spoken disclosure are compatible. Today an unattended shell/browser result can flow into a short spoken reply with secrets, while the owner has no clear distinction between raw local evidence and relay-safe narration. A local redaction boundary would let the agent remain powerful without turning the wearable into a credential leak.
- **path:** mac-terminal → mac-planner → browser-extension → relay-realtime → pendant
- **model tier:** Deterministic pattern and source-aware redaction first; a cheap model may label an ambiguous fragment locally, but must never be the only secret detector. Realtime receives only the sanitized summary.
- **latency:** Under 100 ms for ordinary command output; bounded streaming redaction for large results. Never delay or alter the local command itself.
- **cost:** Near-zero model cost; local CPU and a bounded encrypted/raw-result store. Retention and disk usage should be configurable and short by default.
- **security:** The raw result stays on the Mac and is never sent to the relay by default. Redaction must cover API keys, bearer tokens, cookies, SSH material, private email snippets, and credential-shaped browser fields, while preserving enough context to be useful. The system must say “redacted” rather than inventing a value.
- **missing:** A provenance-tagged result boundary distinguishing raw local stdout/browser evidence from relay-safe narration; Deterministic secret detectors with configurable owner-specific patterns and false-positive tests; A local-only raw artifact viewer with expiry and hash-linked receipts; Relay and pendant contracts that reject unsanitized result payloads, including failures and partial output


## What it asked for

_Nothing._
## Its own summary

Round 201 produced three new owner-facing capabilities: (1) negotiated 24 kHz superwideband voice with measured downgrade/recovery, explicitly tied to the owner's scheduled deliverable and today's USB-connected chips; (2) a replayable bench-failure report correlating turn IDs, nRF9160/ESP32 UART frames, pipeline events, Mac receipts, and git revision; (3) a spoken unattended-Mac postmortem that reports what changed and retry safety rather than merely saying “failed.” All three were recorded. I also tested the granted USB diagnostic schema: it is still unresolved because no serial capability exists in the live inventory, so it performed no read.

**Biggest unknown:** The exact end-to-end audio frame/codec contract and clock domain between the nRF9160, ESP32 bridge, /pipeline audio routes, and relay are still unknown. The immediate practical need is a real bounded host serial reader/framing parser (or a deliberately approved shell-based bench harness) plus synchronized monotonic timestamps; without those, 24 kHz validation and causal failure reports remain specifications rather than executable tests.

