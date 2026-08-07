# Harness derivation — unified — round 82

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“What happened while I was away?” Give me one concise, time-ordered account of anything the pendant heard or queued, anything the relay completed or failed, and anything the Mac/browser actually did, with links/evidence and clear unresolved items."
- **useful because:** Today each surface can report its own status, but the owner has no trustworthy single answer after sleep, a dropped connection, or a long-running task. This turns fragmented receipts, audio, browser work, and Mac jobs into an auditable spoken handoff without pretending failed or unobserved work succeeded.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use the cheap background model to assemble and normalize the timeline; reserve realtime only to answer the spoken follow-up. Use deterministic route data for events and a small model pass for grouping and plain-language summary.
- **latency:** Under 3 seconds when recent indexed events exist; up to 15 seconds for a cold reconciliation. Stream the first five events to the pendant, then append late receipts.
- **cost:** Usually under $0.02 per request; dominated by summarizing event metadata, not raw audio. Never resend full transcripts when hashes, excerpts, and typed receipts suffice.
- **security:** The timeline may expose private mail, browser URLs, reminders, and audio snippets. Keep raw content local/on the authenticated Mac, project only minimum excerpts and sensitivity labels to relay, redact secrets, and require confirmation before opening sensitive evidence or replaying audio. Mark every item observed, attempted, completed, failed, or unknown.
- **missing:** A durable cross-surface event index with a monotonic sequence/receipt cursor and clock normalization; Adapters for pendant audio/interaction receipts and relay delivery state; A typed evidence bundle linking each summary item to a Mac job receipt, browser command/tab result, or local pendant record; A compact spoken timeline endpoint and dashboard drill-down with late-arriving-event updates

### "“Keep this thread with me, and bring it back when I’m looking at the relevant app or page.” The pendant should capture my spoken intent, then later recognize the matching Mac project or authenticated browser page and give me a one-sentence reminder with the original evidence and my unfinished next step."
- **useful because:** Important ideas and commitments disappear between a spoken moment and the later computer context where they matter. This would make the wearable an intent bookmark: capture is immediate and private, resurfacing is contextual rather than another noisy scheduled briefing. No single surface can do this—the pendant hears the moment, the relay preserves it, and the Mac/browser identify where it belongs.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use realtime only for the initial spoken capture and a brief confirmation. Use a cheaper background model to extract the intent, entities, and next step; use deterministic app/tab/project matching first and invoke a model only for ambiguous semantic matches.
- **latency:** Capture confirmation under 1 second. Context matching should happen locally on Mac/browser within 300 ms of an app or tab transition; spoken resurfacing under 2 seconds and suppressed unless confidence is high.
- **cost:** A few cents per captured thread at most; most future matches are local string/entity comparisons. Relay storage is small metadata plus a short owner-approved excerpt, not continuous audio.
- **security:** Do not retain raw microphone audio by default. Store sensitivity, source, timestamp, and an encrypted short transcript; never copy authenticated page contents to the relay. Require explicit opt-in per thread for browser matching, respect private-window boundaries, redact secrets, and let the owner inspect, edit, snooze, or delete each bookmark.
- **missing:** A first-class intent-bookmark schema with lifecycle states (captured, matched, resurfaced, completed, snoozed, expired); Mac app/project focus and browser tab transition events with stable, privacy-filtered identifiers; A local semantic matcher that can cite the originating capture and target page without exporting page contents; Pendant delivery and acknowledgement receipts for contextual reminders, plus dashboard controls for retention and opt-in scope


## Changes it proposed to its own stack

### `browser-harness` — Add a failure-aware resume coordinator above the browser and Mac queues. For every multi-step request, persist a checkpoint containing the last verified browser tab/page fingerprint, action idempotency key, evidence hash, and owner-visible side-effect state. Classify failures as offline, stale tab/session, transient navigation, authentication wall, semantic mismatch, or unknown; retry only transient cases with bounded backoff, never replay a side-effecting step without an unchanged precondition, and surface a pendant-sized 'paused—needs you' receipt. When connectivity returns, reconcile extension pending commands against relay/Mac receipts before resuming, eliminating duplicate execution such as repeated browser_navigate attempts.
- **owner gets:** A dropped browser connection currently leaves the owner unsure whether work happened and can repeat failed commands six times. They get safe continuation instead of duplicate purchases/messages/forms, and a short spoken explanation of exactly where work stopped.
- effort: Medium-high: shared checkpoint schema, classifier, idempotency/precondition checks, recovery worker, and pendant/voice receipt integration; validate against offline Safari and stale-tab fixtures.  ·  risk: A wrong classification could either retry too much or pause harmless work. Default unknown to pause; keep immutable receipts, bounded retries, and an explicit resume command. Recovery is safe because side-effecting steps require a fresh precondition match.
- cost: Negligible API cost for deterministic classification; occasional small model call for semantic mismatch only (roughly <$0.01). Storage is small per step (metadata and hashes, not page content).  ·  latency: Adds tens to hundreds of milliseconds for checkpoint writes; resumed work waits for backoff or extension heartbeat, but owner gets immediate status.
- security: Persist only redacted evidence hashes, tab/session identifiers, and sensitivity labels in relay; keep DOM/text local to the authenticated browser. Never place form contents or secrets in retry logs.
- depends on: Durable browser job runner and result stream (chg-16bc5dee, still missing persistence/retry wiring); Working browser extension heartbeat/enqueue path (currently offline with pending commands); Existing Mac job receipts/undo and request-id/tab-affinity work (chg-14accc01, chg-5fc73ce3)

### `hardware` — Replace the prototype's single nRF9160 audio workload with a production audio front end: add a low-power full-duplex 24 kHz audio codec/DSP on the existing I2S bus (or choose an SoC with a hardware audio accelerator), with onboard mic bias, speaker amplifier, clocking, and hardware AEC/AGC. Keep the nRF9160 responsible for transport/control and expose a compact PCM ring-buffer interface. Preserve a clock mode that can interoperate with the ESP32 bridge, but stop doing simultaneous Opus encode/decode and resampling on the 64 MHz M33.
- **owner gets:** The owner gets intelligible, low-latency conversation instead of a pendant that spends nearly its entire CPU budget encoding and decoding audio, drops frames under network jitter, or cannot sustain the requested 24 kHz superwideband path.
- effort: High: select and prototype a codec/DSP, redesign the small wearable PCB and power rails, update the I2S protocol/firmware, and run acoustic, RF, and end-to-end acceptance tests. The current DK is explicitly only a prototype.  ·  risk: New clock domains, driver bugs, acoustic feedback, and added power draw can create regressions. Keep a bypass path to the current software codec for lab fallback, gate rollout behind loopback/jitter tests, and retain the ESP32 bridge compatibility mode.
- cost: Roughly $3–$12 added BOM in volume (codec/DSP, amplifier, microphones, passives), plus perhaps 10–40 mW active audio power depending on part; saves nRF9160 CPU headroom and may reduce retransmits.  ·  latency: Could remove ~25 ms decode and ~15 ms encode CPU work per frame and reduce jitter; codec buffering target 10–20 ms, with total conversational path still governed by network.
- security: Audio remains in local PCM buffers and the existing encrypted transport; a codec with firmware must support signed updates and disable debug access in production.
- depends on: Authoritative 24 kHz audio target architecture and end-to-end acceptance thresholds; A production pendant hardware definition beyond the nRF9160 DK; Firmware I2S/PCM ring-buffer and bridge clock-negotiation design

### `context` — Add a local intent-bookmark broker that subscribes to Mac frontmost-app/project changes and browser tab metadata, but publishes only privacy-filtered events (app, host, title hash, project id, private-window flag). Match these events against owner-created spoken bookmarks using a typed entity/next-step index; emit at most one pending reminder per context with source citation, confidence, expiry, and acknowledgement state. Keep the transcript and evidence on the Mac, send only a compact reminder receipt through the relay to the pendant, and never use page-body text as a background sensor.
- **owner gets:** The owner can say an idea once while walking and reliably get it back at the moment it becomes useful, without recurring alerts, cloud surveillance of browsing, or having to remember which note contained it.
- effort: Medium: event adapters for frontmost app/browser tabs, local index and matcher, lifecycle/expiry store, relay receipt, and pendant acknowledgement UX; add tests for private windows, duplicate tab transitions, and app crashes.  ·  risk: A false match could interrupt the owner or reveal a sensitive reminder on a shared screen. Start opt-in, require high confidence, suppress in private windows and during focus modes, rate-limit resurfacing, and provide immediate snooze/delete. If the Mac is offline, retain the bookmark until a signed local event arrives.
- cost: Near-zero ongoing API cost; deterministic local matching handles normal cases. Occasional background embedding or semantic disambiguation can stay below $0.01 per bookmark. Storage is a few KB per bookmark and event hash.  ·  latency: Local event matching is sub-second; relay/pendant delivery adds network latency only when the owner has opted into spoken resurfacing.
- security: Improves privacy relative to cloud page watching because raw page text, URLs, and audio remain local. Use encrypted local storage, sensitivity labels, no telemetry for ignored contexts, and a clear per-bookmark retention policy.
- depends on: A Mac/browser context-event feed with stable privacy-filtered identifiers; Intent-bookmark lifecycle and acknowledgement schema; Relay-to-pendant reminder receipt and local privacy controls


## What it asked for

_Nothing._
## Its own summary

Round 82 produced three recorded items: (1) a cross-surface away-mode timeline, (2) failure-aware browser/Mac resume with idempotent checkpoints, and (3) a production audio-front-end/DSP change to make 24 kHz full duplex sustainable. Fresh state confirms Mac/relay are online, pipeline telemetry and 24 kHz TTS work, but browser is offline with 7 pending commands and computer-use remains disabled.

**Biggest unknown:** The owner’s authoritative 24 kHz end-to-end acceptance thresholds and production pendant constraints are still missing; without them, audio hardware and firmware choices cannot be validated. The browser heartbeat/enqueue path and durable browser runner also remain unimplemented, so private authenticated workflows cannot yet be exercised.

