# Harness derivation — unified — round 217

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Is the pendant ready for a real conversation right now, and if not, fix whatever is safe to fix?”"
- **useful because:** This is the single most useful daily trust capability: before the owner relies on the device, it correlates pendant/relay/Mac/browser health, runs the already-triggered audio fixture and 24 kHz validation, distinguishes a stale bridge from a real audio failure, performs only idempotent repairs, and returns one spoken READY/DEGRADED/BLOCKED verdict with evidence instead of making the owner debug five surfaces.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic checks and repair planning first; background model only to summarize correlated evidence and explain the verdict. Realtime is unnecessary unless the owner asks during an active conversation.
- **latency:** 5 seconds for snapshot and verdict; up to 30 seconds for an explicitly requested fixture/fault check. Never block a live call on the check.
- **cost:** Usually near-zero model cost because checks are typed; roughly $0.01–$0.05 only when a background model turns raw evidence into a concise explanation. Dominant cost is hardware fixture time and relay/database reads.
- **security:** Read-only diagnostics by default. Repairs must be limited to idempotent bridge/browser wake and stale-lease cleanup, with a receipt; never silently change audio profile, send browser commands, or expose page contents. A deliberate confirmation is required for anything beyond those safe repairs.
- **missing:** A typed readiness orchestrator that correlates fixture results with incident diagnostics and repair receipts; A stable health contract mapping raw counters to READY/DEGRADED/BLOCKED; An owner-visible dashboard card and spoken summary; A hardware-trigger adapter for the existing explicit audio diagnostic fixture

### "“The connection dropped—continue exactly where we left off without making me repeat myself.”"
- **useful because:** A dropped link currently risks a silent half-turn: the owner may have spoken, the model may have answered, or audio may have been accepted by the relay but never heard. This capability would resume at the last mutually acknowledged turn, replay only missing text/audio, and state plainly when a turn is ambiguous. It makes the wearable dependable during travel rather than merely reconnectable.
- **path:** pendant → relay-realtime → mac-bridge → dashboard
- **model tier:** Deterministic sequence/receipt reconciliation and bounded replay; a cheap background model may compress the last acknowledged turn into one sentence. Use the realtime tier only for the new live utterance after continuity is established.
- **latency:** Reconcile in under 2 seconds after reconnect; replay at most one missing response automatically. If delivery is ambiguous, ask one short spoken clarification rather than guessing.
- **cost:** Near-zero for reconciliation; $0.01–$0.03 when a summary is needed. Network and bounded audio replay dominate, not model inference.
- **security:** Persist opaque turn IDs, hashes, timestamps, and delivery states—not raw audio by default. Never replay an unacknowledged command or browser action. Require confirmation before resuming an action with replaySafety unrepeatable/unknown; expired sessions must fail closed.
- **missing:** A durable per-conversation turn watermark shared by pendant, relay, and Mac; A reconnect protocol that distinguishes relay acceptance, pendant receipt, playback start, and playback completion; A bounded replay endpoint for one missing 24 kHz artifact; A policy for ambiguous speech capture (discard or ask, never duplicate silently)

### "“If you miss part of what I said or I miss part of your answer, repair just that piece instead of making us start over.”"
- **useful because:** Packet loss today can turn a fluent exchange into a wrong transcription or an answer with a missing clause, while both sides continue as if nothing happened. A bounded, sequence-aware repair asks for one missing 60 ms audio frame (or one short uplink span), marks the turn uncertain when repair is impossible, and prevents silent hallucination or needless full-turn repetition.
- **path:** pendant → relay-realtime → mac-bridge → dashboard
- **model tier:** Deterministic sequence-gap detection, Opus artifact lookup, and bounded retransmission; use the realtime model only to regenerate a response when the repaired transcript materially changes intent.
- **latency:** Detect gaps within one frame window and repair within 500 ms when the artifact is retained. Never hold a response indefinitely; after one retry, speak a concise uncertainty cue and continue conservatively.
- **cost:** Very low: one bounded packet retransmission and receipt write; model cost only on a materially changed transcript, typically under $0.01.
- **security:** Only retransmit artifacts bound to the current opaque turn/session and verify checksum plus epoch. Do not retain routine audio beyond the existing delivery policy; if the artifact is unavailable, report uncertainty rather than searching unrelated recordings.
- **missing:** A bidirectional gap/negative-ack envelope for pendant and relay; A short-lived relay cache keyed by turn and frame hash, with strict expiry; A policy that marks STT and TTS turns uncertain instead of silently proceeding; A compact owner-facing cue for unrepaired loss

### "“Why do you believe that, and what could have changed since you learned it?”"
- **useful because:** Today the owner receives a confident answer but cannot inspect whether it came from a current browser fact, an old extracted memory, a Mac observation, or a model guess. This capability provides an on-demand provenance capsule: source surface, observed-at time, freshness/contradiction state, and the smallest recognizable evidence excerpt, then offers to re-check only the bound source before answering. It makes trust inspectable without exposing the entire private context graph.
- **path:** pendant → relay-realtime → mac-bridge → browser → dashboard
- **model tier:** Deterministic provenance and freshness computation first; a cheap background model formats the capsule. Realtime is used only for the owner's follow-up question, not for deciding whether evidence is valid.
- **latency:** Return an existing capsule in under 1 second; a live re-check within 5 seconds. Never delay a normal answer unless the owner explicitly asks for proof.
- **cost:** Near-zero for indexed provenance; $0.01–$0.04 when a live browser/Mac re-check and concise synthesis are required. The dominant cost is source reads, not inference.
- **security:** Evidence is least-privilege and redacted: show only the bound excerpt needed to recognize the source, never full page contents or unrelated graph neighbors. A stale or contradictory source must be labeled, not silently reconciled. Re-checks are read-only unless separately authorized.
- **missing:** A provenance capsule schema shared by memory, browser, Mac observations, and relay events; Freshness and contradiction rules per source type; A read-only endpoint that returns evidence candidates plus redacted excerpts; Dashboard and spoken rendering that can distinguish observed, inferred, stale, and unknown

### "“Before anything from my Mac or browser leaves this device, show me exactly what is going out and remove anything I did not authorize.”"
- **useful because:** The owner currently has no single view of data crossing the pendant, Mac, browser, and relay. A data-egress preview would intercept each cross-surface payload, list fields and destinations, apply owner rules, and let safe metadata pass while blocking or redacting private page text, files, or audio. This is a usable privacy boundary, not a promise hidden in implementation details.
- **path:** pendant → relay-realtime → mac-bridge → browser → dashboard
- **model tier:** Deterministic schema-based classification and redaction; use no model for the allow/block decision. A cheap background model may explain a blocked field in plain language.
- **latency:** Metadata-only requests under 50 ms; interactive previews under 2 seconds. Live speech must not stall: queue the turn and provide a concise blocked reason if policy cannot decide.
- **cost:** Negligible for typed fields and hashes; under $0.01 for occasional explanations. The main cost is maintaining destination-specific adapters and audit receipts.
- **security:** Default deny for unknown destinations and raw audio/page contents; hash rather than copy sensitive values into receipts. Rules must be local and tamper-evident. The preview itself must not leak the very content it protects. Owner confirmation is required for a new destination or category, never for routine approved metadata.
- **missing:** An egress interception point before relay, browser, and Mac payload serialization; A typed data-label vocabulary and owner policy store; A redaction engine that preserves task utility while dropping secrets; A receipt that records destination, labels, policy decision, and hashes without payload contents

### "“Tune the pendant so speech is clear and comfortable for me, and tell me if the bridge or microphone is the problem.”"
- **useful because:** The shipped 24 kHz path proves codec and framing quality, but it does not personalize acoustic gain, latency, or the ESP32-to-earbud path. A guided calibration would measure the actual pendant/bridge chain, separate clipping, weak mic level, codec loss, and playback imbalance, then store bounded gain/profile values. The owner gets intelligible speech without repeatedly guessing volume or risking a too-loud setting.
- **path:** pendant → mac-bridge → relay-realtime → dashboard
- **model tier:** Deterministic swept-tone/voice fixture analysis and bounded profile selection; background model only summarizes the result. No realtime inference is needed.
- **latency:** A guided run should finish in 30–60 seconds; normal calls remain unaffected. Apply a new profile only at a turn boundary and restore the previous profile automatically if measurements fail.
- **cost:** Near-zero model cost; one short fixture run and a few metadata receipts. Hardware test time and owner attention dominate.
- **security:** Use synthetic tones and owner-spoken calibration phrases only; do not retain raw speech. Enforce hard gain and exposure ceilings, require explicit confirmation before applying a profile, and keep the last-known-good profile for rollback.
- **missing:** A calibration fixture that measures mic level, bridge gain, end-to-end latency, clipping, and packet continuity together; Typed bounded gain/profile controls for pendant and ESP32 bridge; A safe profile apply/rollback protocol at conversation boundaries; A clear non-medical result distinguishing device faults from fit/environment effects


## Changes it proposed to its own stack

### `integration` — Bind the pendant's local_privacy_latch state to a relay-wide privacy barrier: on the authenticated latch-enter event, stop new capture/playback, revoke browser polling and Mac jobs that could expose page contents, mark in-flight browser commands as paused rather than failed, and require a fresh latch-clear event plus privacy_convergence_check before any queued work is released. Add a monotonic latch epoch to every receipt so stale clear/retry events cannot reopen the surfaces.
- **owner gets:** A physical privacy press should mean the whole hive is quiet—not merely that the pendant speaker and microphone stopped while a browser command or Mac job continues reading and acting. The owner gets a single predictable privacy boundary and can safely leave the device on a desk or in a meeting.
- effort: Medium: relay barrier state and epoch, browser/Mac admission checks, pause/release transitions, and integration tests across dropped links and reboot.  ·  risk: A latch event arriving late could leave a surface open; fail closed on missing or out-of-order epochs. Paused jobs may expire and need an explicit owner-visible cancellation rather than silent replay. Recover by showing blocked receipts and requiring a fresh conversation after unlatch.
- cost: Negligible storage and request overhead; one small state record plus receipt fields. No inference cost.  ·  latency: Local pendant mute remains immediate. Relay/browser admission should converge within one polling interval; target under 2 seconds, with no need to wait for the model.
- security: Strongly improves privacy by making the physical latch a cross-surface deny boundary. Must not transmit raw audio or page contents in latch events; use only signed state, epoch, and timestamp.
- depends on: local_privacy_latch; privacy_convergence_check; GET /browser/status; GET /browser/poll; POST /browser/heartbeat; GET /jobs/:jobId; POST /jobs/:jobId/cancel


## What it asked for

_Nothing._
## Its own summary

Recorded three new owner-facing capabilities and one integration change: (1) a typed “is the pendant ready, and fix safe faults” readiness check; (2) exact-turn conversation continuation after a dropped link; (3) bounded repair of individual lost audio spans rather than silent continuation; plus making the physical privacy latch a cross-surface deny barrier for Mac/browser work. The extracted-fact erase interaction was correctly rejected as an existing proposal, so I did not restate it.

**Biggest unknown:** Implementation still needs a durable cross-surface turn watermark and gap/NACK protocol, a typed readiness verdict contract, and privacy-barrier admission hooks in browser/Mac workers. I still need the previously requested browser identity attestation grant (already queued, not re-requested) before I can make browser-target security claims. Owner policy is also still needed for how long ambiguous turns may be held and whether a repaired clip may be replayed automatically; absent that, default to one retry and fail-closed uncertainty.

