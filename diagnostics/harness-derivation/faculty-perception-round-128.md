# Harness derivation — faculty-perception — round 128

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live device and Mac observability at round 128** — Current live device discovery shows Safari browser online with 3 tabs and home-macbook-bridge online; no nRF9160 pendant or ESP32 bridge registered. /ops/status reports Mac agent v0.5.0, browser extension online, relay reachable, but Accessibility and Screen Recording false and inputReachability failed; AppleScript automation grants are present. /pipeline history includes 24 kHz PCM rendered and relay-accepted audio, but these are historical runs, not live pendant delivery.
  - evidence: discover(devices) round 128; GET /ops/status 200 observed 2026-08-07T18:27:39Z; GET /observe 200; GET /pipeline 200
- **timezone contradiction** — Machine context reports timezone America/New_York, while owner memory projection says authoritative owner timezone America/Chicago. Do not schedule or interpret timestamps as local owner time until authoritative timezone semantics are resolved.
  - evidence: GET /machine-context 200 returned timezone America/New_York; discover(owner) remembered block says timezone America/Chicago.

## Capabilities it proposed

### "“What is actually true about my request right now?” Give me a fresh, evidence-linked answer across the Mac, Safari, relay, and (when present) pendant: what was observed, what merely was planned, what changed, and what remains unknown."
- **useful because:** This is the single most useful perception capability: it stops the system from claiming success because a job was queued or a UI action returned a nominal receipt. The owner gets one short spoken truth report with timestamps, source surface, freshness, and explicit uncertainty.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use the cheap background/text model to assemble and reconcile structured observations; reserve realtime only for the spoken question and final short reply.
- **latency:** 3–8 seconds for a fresh cross-surface snapshot; immediately say “checking” on the pendant if browser or Mac observations are still arriving.
- **cost:** Usually <$0.01 in model/API cost; dominated by zero/low-cost authenticated reads and optional browser extraction, not inference.
- **security:** Private tab titles/content and local job metadata must stay in the owner’s relay scope; quote only the minimum evidence. Never infer that a destructive action happened without a postcondition observation. Ask confirmation only if the owner turns the report into an action.
- **missing:** A typed cross-surface observation snapshot with source/timestamp/freshness/confidence and contradiction handling; A read-only correlator joining requestId, pipelineId, relayJobId, local job, browser command, and postcondition; Pendant registration and delivery acknowledgements for live wearable evidence

### "“Did that actually happen?” For the last request I made, reconstruct a causal timeline from my spoken command through relay, Mac planning, browser/UI execution, receipts, and an independent observation; tell me exactly where it stopped or became unverifiable."
- **useful because:** Status endpoints answer what a component says; they do not answer whether the owner’s intended outcome exists. This capability turns ambiguous failures into an actionable truth: queued, planned, attempted, completed, observed, contradicted, or unknown, with the missing proof named.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Cheap structured reconciliation first; realtime only converts the already-built timeline into one concise spoken answer.
- **latency:** Under 5 seconds for recent jobs; up to 15 seconds when a fresh browser read or Mac observation is required.
- **cost:** <$0.02 typical; most cost is one targeted page read or AppleScript verification, with no vision model unless the only proof is visual.
- **security:** Do not expose private page contents in relay logs; retain hashes/snippets and redact secrets. Treat nominal UI receipts as untrusted while accessibility is false, and explicitly mark that limitation rather than claiming completion.
- **missing:** A durable causality index and outcome-state vocabulary across pipeline/jobs/browser; Independent postcondition probes for common Mac and browser actions; A way to attach observation evidence to an existing request without mutating it

### "“I plugged in the pendant—prove the whole path works.” Detect the nRF9160 and ESP32 serial devices, run a non-destructive USB/UART identity and audio loopback test, verify 24 kHz PCM framing and relay acceptance, then give me a pass/fail report with the first failing boundary."
- **useful because:** The hardware is physically testable over USB even though no pendant is currently registered. Instead of waiting for an LTE registration and guessing from historical pipeline rows, the owner gets a repeatable end-to-end proof from cable and firmware through Mac bridge, relay, and audio payload.
- **path:** pendant → mac-bridge → relay → dashboard
- **model tier:** No expensive model needed for detection, framing checks, and test verdict; use a cheap model only to summarize failures, realtime only if the owner asks by voice.
- **latency:** 30 seconds for serial discovery and identity; 2 minutes for an audio loopback plus relay round trip.
- **cost:** Near-zero API cost; local serial/UART and PCM checks dominate. Hardware test must not upload microphone content—use a generated tone or fixture PCM.
- **security:** Never capture or upload live microphone audio during a diagnostic. Use a generated test tone, cap payload size, and record only hashes/telemetry. Pairing or firmware flashing requires explicit confirmation; diagnostics must be read-only.
- **missing:** Mac serial-port probe and safe UART protocol adapters for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; A relay diagnostic endpoint that acknowledges device identity and test payload separately from production speech; Firmware test commands for deterministic generated-tone capture/playback and 24 kHz framing counters

### "“What can you hear, see, read, or control right now?” Give me a live privacy-and-reachability report across the pendant, Mac, browser, and relay: active microphones/cameras, accessible tabs, granted automation, queued commands, recording/upload state, and exactly what is unavailable."
- **useful because:** The owner cannot currently obtain one honest answer about the system’s present sensory reach. This would expose dangerous false assumptions—such as UI receipts that do nothing, historical audio mistaken for live audio, or a private browser session being reachable when it is not—before they trust an action.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use deterministic local/relay probes and a cheap summarizer; realtime is needed only to speak the compact result.
- **latency:** 2–5 seconds for local and relay state; clearly label any component whose status is older than the freshness threshold.
- **cost:** Under $0.01 per request; dominated by authenticated status reads, with no page content or audio sent to a model.
- **security:** This report itself is sensitive. Return capability categories and redacted tab origins, not page contents, microphone data, tokens, or command payloads. Require owner authentication and never let the report itself execute anything.
- **missing:** A unified, freshness-bounded capability/permission snapshot schema across all surfaces; Pendant microphone/playback and relay upload-state telemetry that distinguishes live from historical records; Browser session capability metadata that reports read/control scope without exposing content

### "“Only tell me when two independent sources agree that something important happened.” Let me define an event—such as a meeting cancellation, payment, delivery, or account alert—and have the system corroborate it across my authenticated browser, Mac apps, relay messages, and (when available) pendant, reporting conflicts instead of guessing."
- **useful because:** Single-source automation is brittle: an email can be delayed, a calendar can be stale, and a UI receipt can be false. Cross-surface corroboration would give the owner high-confidence alerts while surfacing genuine contradictions for human review.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Cheap background workers normalize and compare structured evidence; use a slower model only to explain a conflict, and realtime only for the final spoken alert.
- **latency:** Event-driven sources within 10 seconds; scheduled authenticated checks within the owner’s chosen window. Do not wake the expensive model for unchanged or one-source events.
- **cost:** Typically <$0.02 per corroborated event; browser reads and background polling dominate, not model inference.
- **security:** Private account data must remain scoped to the owner and be reduced to hashed fields, timestamps, and source labels. Never treat two copies of the same upstream source as independent. Sending, purchasing, deleting, or changing records remains confirmation-gated.
- **missing:** A source-independence model and normalized event schema; Event subscriptions or bounded polling for Mac apps and authenticated tabs; Conflict retention and owner acknowledgement semantics across relay and offline pendant delivery

### "“Before I trust this system, let me run a private end-to-end challenge.” Generate a harmless test question and expected answer, deliver it through the available surface, verify each boundary independently, and show me a tamper-evident report proving what was transmitted, observed, and played—without using my real microphone, accounts, or data."
- **useful because:** Today the owner can test isolated components, but cannot establish that the complete personal AI chain is truthful without risking private content or relying on self-reported success. A synthetic challenge gives them a repeatable trust check whenever firmware, relay, browser, or Mac software changes.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** No expensive model: use deterministic synthetic payloads and cryptographic checks; a cheap model may summarize failures. Realtime is unnecessary except if the owner starts the challenge by voice.
- **latency:** Under 60 seconds for Mac/relay/browser; under 3 minutes when a registered pendant must receive and play the challenge.
- **cost:** Near-zero API cost; small relay storage and local serial/audio test overhead. Use generated tones and fixed text, never recorded speech.
- **security:** The challenge must use synthetic data, a disposable browser page/session, and short-lived nonces. Do not open authenticated pages, upload microphone audio, or expose cryptographic tokens. Any pairing, firmware update, or persistent setting change requires confirmation.
- **missing:** A deterministic challenge protocol with nonce, expected transcript/audio hash, and per-boundary attestations; A disposable browser test session and a relay route that returns signed receipts; Registered pendant delivery/playback acknowledgement and, for USB testing, safe firmware test commands

### "“Tell me if the system lost a sense or a route I relied on.” Maintain a personal reachability baseline and alert me when a microphone, browser session, Mac automation grant, relay link, pendant registration, or playback path degrades—state what changed, when, and which requests are now unsafe to claim as complete."
- **useful because:** A capability can silently regress while the assistant continues speaking as if it works. The owner should learn about a lost browser heartbeat, revoked permission, stale relay, or missing wearable before a consequential request depends on it.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic probes and a cheap background classifier; realtime only delivers the alert through the currently healthy route.
- **latency:** Detect local permission/browser changes within 30 seconds and relay/device changes within 1–2 minutes; queue the alert if every live route is unavailable.
- **cost:** <$0.01 per day of normal monitoring; costs are periodic authenticated probes and small durable state, not model calls.
- **security:** Store only capability states, timestamps, and redacted identifiers. Do not turn permission monitoring into hidden surveillance. Alerts must not include private tab content or audio.
- **missing:** A per-owner reachability baseline with freshness and degradation semantics; Persistent change detection across Mac permission probes, browser heartbeat, relay registry, and pendant playback; A durable alert queue with explicit acknowledgement and fallback delivery rules


## Changes it proposed to its own stack

### `interaction` — Add a spoken “proof mode” response contract: every answer about an action must include one of five observable states (not started, accepted, attempted, independently verified, contradicted), the freshest timestamp, and one sentence naming the missing boundary when verification is impossible. The relay/mac planner should refuse completion language when only a nominal receipt exists or when /observe says UI input is unreachable.
- **owner gets:** The owner will stop hearing confident lies such as “done” when Accessibility is false, a browser command is merely pending, or audio is only historical. They get a useful next step instead of a vague failure.
- effort: Medium: define state contract, add planner output validator, and add read-only evidence lookup; no new model required.  ·  risk: Over-cautious wording could annoy the owner for harmless actions. Recover with per-action verification policies and a terse default; never block reversible actions solely because proof is unavailable.
- cost: Negligible inference increase; one compact evidence projection may add a few hundred tokens.  ·  latency: Adds <500 ms for local reads; fresh browser/Mac probes remain opt-in.
- security: Improves privacy by returning evidence summaries/hashes instead of raw private page content.
- depends on: A typed mapping from request IDs to pipeline/jobs/browser commands; Explicit distinction between nominal receipts and independent observations

### `hardware` — Add a dual-chip USB diagnostic mode: when the Mac sees both configured serial paths, it sends a generated-tone challenge to the ESP32 audio bridge and a framed identity/status challenge to the nRF9160, then records UART byte counts, CRCs, sample-rate declarations, and firmware versions locally. Only a compact signed verdict may be uploaded to the relay.
- **owner gets:** Plugging in the real hardware becomes a one-minute answer—cable, firmware, audio bridge, framing, and relay boundary each pass or fail—without risking microphone privacy or requiring LTE registration.
- effort: High: implement deterministic test commands in both firmware images, a Mac serial harness, and a relay diagnostic acknowledgement route.  ·  risk: A malformed test command could wedge audio or leave a chip in diagnostic mode. Require a timeout, watchdog recovery, explicit exit frame, and never alter production pairing or audio settings.
- cost: No recurring model cost; roughly $0–$30 of existing test fixtures, negligible added power during USB tests.  ·  latency: 30–120 seconds only when invoked; no impact on normal voice path.
- security: Generated tone only; upload hashes/telemetry, not microphone PCM. Pairing keys remain local.
- depends on: Serial-port discovery and safe protocol adapters; Deterministic generated-tone test command in nRF9160 and ESP32 firmware; Relay route that acknowledges diagnostics separately from production speech

### `relay` — Create an append-only boundary ledger for each request: record ingress receipt, transcription/audio integrity, relay forwarding, Mac acceptance, action attempt, postcondition evidence, and wearable delivery/playback acknowledgement as separate immutable facts with monotonic sequence numbers. Expose a compact read-only “last request proof” projection.
- **owner gets:** When something fails, the owner can hear whether the words arrived, the Mac acted, and the answer reached the wearable—instead of receiving one blended status that hides the first broken boundary.
- effort: High: schema and retention policy, event emission at each boundary, deduplication, and a read-only projection route.  ·  risk: Events can be duplicated or arrive out of order; use idempotency keys and monotonic per-request sequence numbers, and mark gaps rather than inventing order. Keep short retention and redact payloads.
- cost: Small D1/R2 storage and egress increase; no meaningful model cost.  ·  latency: Sub-100 ms event writes asynchronously; projection usually <1 s.
- security: Store hashes, sizes, status, and timestamps—not raw audio, transcript, or private page data. Restrict access to owner scope.
- depends on: Authoritative device registry and delivery acknowledgements; Playback lifecycle telemetry; Cross-surface request correlation identifiers


## What it asked for

_Nothing._
