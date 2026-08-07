# Harness derivation — faculty-perception — round 11

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-agent-capabilities-2026-08-07** — The live Mac agent is healthy at version 0.5.0; capabilities manifest generated 2026-08-07T09:31:05.534Z reports 120 routes, Bearer auth token configured, and active pipeline audio traces, browser bridge, evidence capsules, page watches, execution journal, and ops snapshot groups.
  - evidence: GET /health returned 200 ok service AI Pendant Mac Local Agent version 0.5.0; GET /capabilities returned matching version/timestamp, routeCount 120, tokenConfigured true, and listed groups.
- **pendant-audio-hardware-current** — Current hardware description still reports I2S microphone capture at 15,625 Hz and Opus uplink at 16 kHz/16 kbps, while the owner goal is an end-to-end 24 kHz superwideband path; LTE-M is half-duplex in practice.
  - evidence: get_hardware_spec(audio) and network/owner projections: audio summary says 15,625 Hz capture and Opus 16 kHz; owner relevant goal says ship 24 kHz superwideband end to end.
- **audio-path-asymmetry-2026-08-07** — The prototype already decodes playback at 24 kHz in 60 ms Opus frames, resampling to a 31,250 Hz I2S wire clock; capture remains 15,625 Hz and uplink 16 kHz/16 kbps. Both encode and decode consume about 87% of one nRF9160 core together (encode ~15 ms and decode ~25.4 ms per 60 ms packet).
  - evidence: get_hardware_spec(audio) returned playback, codec, and source details; status PROTOTYPE.

## Capabilities it proposed

### "“What exactly happened with that request?” Give me a short, evidence-backed timeline from what the pendant heard through the relay, Mac, browser, and final result, including where it stopped if it failed."
- **useful because:** Today a Mac job receipt cannot distinguish a lost utterance, dropped LTE session, relay acceptance, queued Mac work, browser execution, or a final result. A cross-node trace would let the owner trust (or correct) the system without repeating work, especially after walking away or losing connectivity.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic event correlation and summarization on the relay/Mac; use the cheaper background model for a readable timeline, reserving realtime only for the spoken follow-up. No model is needed to establish event facts.
- **latency:** Under 1 second when the trace is already indexed; up to 5 seconds to reconcile delayed LTE/Mac/browser events. The pendant should speak a one-sentence result and offer the detailed receipt on the dashboard.
- **cost:** Negligible per lookup (database reads plus roughly 300–800 background-model tokens only when prose rendering is requested); storage and event indexing dominate, not inference.
- **security:** The trace contains private audio metadata, transcript snippets, logged-in URLs, and action results. Keep raw audio out of the receipt by default; redact secrets and page contents, bind records to the owner's device/session, encrypt relay storage, and require confirmation before exposing sensitive snippets or replaying audio.
- **missing:** A shared correlation/causation ID generated at button press and propagated through relay, pipeline, Mac jobs, and browser commands; Pendant-local event emission for press, capture start/stop, upload acknowledgment, codec/sample-rate, and link loss (with a monotonic sequence number); Relay append-only event schema with delayed-event reconciliation and bounded retention; Mac and browser adapters that attach the correlation ID to pipeline traces, jobs, browser commands, and evidence capsules; A read-only /trace endpoint and dashboard timeline with explicit unknown/gap states

### "“If you lose connection while I’m talking, keep my request and finish it when you’re back—don’t make me repeat myself. Tell me exactly what you captured and when the answer is ready.”"
- **useful because:** A wearable is most valuable away from reliable Wi‑Fi, yet a dropped LTE-M link currently turns an utterance into an ambiguous failure. Offline capture with later reconciliation would make the pendant dependable during commutes, basements, travel, and network handoffs: the owner gets an immediate local acknowledgment, then a completion notification and answer when the rest of the hive is reachable.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use firmware and relay logic for capture, integrity, deduplication, and delivery state; use a cheaper background model to execute and summarize the deferred request. Reserve realtime for the brief acknowledgment when connected again.
- **latency:** Immediate local acknowledgment within 250 ms of button release; queue confirmation within 1 second when offline; resume within 10 seconds of link restoration, subject to Mac/browser availability. No realtime model call is needed while disconnected.
- **cost:** Small per-request storage and event-index cost; deferred requests use the cheaper background tier (typically a few thousand tokens depending on the task). The dominant cost is retained audio/transcript data and browser/Mac execution, not the offline queue.
- **security:** Pending requests may contain private speech and authenticated-site intent. Encrypt the local queue and relay copy, use a per-request owner/device key, expire unsubmitted requests, show queued text/audio length before transmission when feasible, and preserve the existing confirmation barrier for sending, deleting, purchasing, or other irreversible actions. Never replay a stale request after its deadline or changed account context.
- **missing:** A pendant-side encrypted outbox with monotonic sequence numbers, bounded size, retry/backoff, battery-aware retention, and a clear local queued/expired indication; A resumable relay upload protocol with packet hashes, exactly-once request IDs, conflict handling, and a signed receipt proving whether the complete utterance arrived; A scheduler that can hold a request until both the Mac bridge and browser session are available, then resume at the last safe step rather than rerunning completed work; A notification path from relay to pendant for queued, needs-confirmation, completed, and expired states; A dashboard review view for inspecting, editing, cancelling, or setting an expiry on deferred requests before execution


## Changes it proposed to its own stack

### `integration` — Add a signed, end-to-end media contract negotiated at conversation start and attached to every audio packet: capture rate, playback rate, Opus mode/bitrate, frame duration, I2S clock, resampler path, firmware build, and measured encode/decode CPU headroom. The pendant, relay, and Mac pipeline must acknowledge the same contract; if any hop falls back from 24 kHz, mark the conversation degraded and expose the exact boundary instead of silently labeling it superwideband.
- **owner gets:** The current prototype can play 24 kHz while capturing at 15,625 Hz/16 kHz, and codec work already uses roughly 87% of one core. This gives the owner an honest answer about whether a conversation was truly 24 kHz, catches overload before it becomes clipped or delayed speech, and makes the end-to-end audio objective testable rather than a configuration claim.
- effort: Medium-high: define a versioned contract, add firmware and relay headers/acknowledgments, correlate it with Mac pipeline traces, add CPU/underrun sampling, and render a small dashboard/audio badge plus a spoken degraded-mode notice.  ·  risk: Old firmware or relay versions may reject the contract; negotiate a backward-compatible minimum and retain the legacy path. Clock drift or noisy measurements could cause false degradation; use hysteresis and preserve raw metrics for diagnosis. Recovery is automatic fallback to the last known-good profile with a visible reason.
- cost: Negligible API cost; a few dozen bytes of metadata per stream and small D1/event storage. Firmware engineering and test effort dominate.  ·  latency: One extra handshake round trip at conversation start (target under 150 ms on LTE-M); no per-frame model latency. Metrics sampling should be asynchronous.
- security: Contract metadata is low sensitivity but identifies firmware/build and timing; authenticate it to prevent false capability claims and do not include raw audio or transcript in telemetry.
- depends on: A shared correlation ID across pendant, relay, and Mac pipeline; Firmware telemetry for underruns, sample-rate selection, and codec CPU headroom; Relay/Mac pipeline trace ingestion and a read-only dashboard badge


## What it asked for

_Nothing._
## Its own summary

Established and recorded: Mac agent is healthy v0.5.0 with 120 routes and token configured; its pipeline/evidence/browser-watch infrastructure is present. Hardware truth is asymmetric: playback is 24 kHz, but capture/uplink remain 15.625/16 kHz, and combined codec work consumes ~87% of one nRF9160 core. Proposed a cross-node request trace (button→relay→Mac→browser) and a signed media contract that reports actual negotiated audio quality and degradation boundaries.

**Biggest unknown:** I still need the already-requested authenticated Mac diagnostics, pendant/firmware observability, current 24 kHz implementation status, and playback-lifecycle telemetry. Without those I cannot establish whether the live system is meeting the prototype’s stated playback path, where audio jobs currently fail, or whether browser-offline is a stale heartbeat versus a real disconnected extension.

