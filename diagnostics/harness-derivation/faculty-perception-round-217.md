# Harness derivation — faculty-perception — round 217

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **current Mac and relay observability** — The live Mac agent is ready with Accessibility, Screen Recording, and all required automation permissions granted; Safari browser bridge is online with two tabs and zero pending commands; relay is reachable and Mac bridge online. Device inventory still contains only home-macbook-bridge and offline cloudflare-contract-test, not an nRF9160 pendant.
  - evidence: GET /ops/snapshot returned HTTP 200 with permissions.ready=true, accessibility.trusted=true, screenRecording.granted=true, browser.online=true, pendingCommands=0, relay.reachable=true, macBridgeOnline=true; discover(devices) returned only those two devices.

## Capabilities it proposed

### "When I come back, show me only the things that need my attention, and for each one say exactly what was observed, when, and what remains unknown."
- **useful because:** The current catch-up surfaces can say a run completed even when nobody knows whether it was heard, and they mix count-capped history with live state. This is a return-from-away audit with explicit observed/inferred/unknown verdicts, so the owner can trust the boundary instead of receiving a confident fiction.
- **path:** relay-realtime → relay → mac-planner → browser-extension → unified → faculty-perception
- **model tier:** background for collection and classification; realtime only to speak the short final digest
- **latency:** Under 3 seconds after a request; collection is parallel and bounded to 20 recent records per source
- **cost:** About $0.01–$0.04 per audit, dominated by one background classification pass; no model call for already-structured statuses
- **security:** The audit may inspect browser tab titles, relay job metadata, and Mac notifications. Keep page bodies and secrets out of the digest, redact before model use, and require confirmation before exposing sensitive notification text.
- **missing:** A return-from-away event or explicit last-seen timestamp from the owner; A single provenance record joining relay job IDs, pipeline runs, browser commands, and Mac receipts; A defined observed/inferred/unknown verdict schema consumed by the spoken renderer

### "Before you act, tell me whether the exact path is ready — relay, Mac agent, browser session, target app permission, and a reversible verification step — and name the first blocker if it is not."
- **useful because:** A reachable bridge is not the same as an executable action: the system now reports Accessibility and Screen Recording as granted, while browser sessions and relay liveness can change independently. A deterministic preflight prevents wasted actions and tells the owner what must be fixed before an irreversible request is attempted.
- **path:** relay-realtime → mac-planner → mac-vision → browser-extension → unified → faculty-perception → faculty-action
- **model tier:** deterministic checks first; background model only resolves ambiguous target-app or browser intent
- **latency:** Under 1 second for readiness checks, under 3 seconds if a harmless probe is required
- **cost:** Near-zero model cost for structured checks; under $0.01 when ambiguity classification is needed
- **security:** Probes must be read-only and bounded. Do not open sensitive pages or send test messages. Expose permission names and target URLs only at the minimum necessary granularity.
- **missing:** A common readiness schema with per-hop freshness, scope, and blocker codes; A read-only target-app probe that confirms the intended window/control is reachable without changing it; A verification-plan field attached to every planned action

### "Run a bench session on the connected pendant and audio bridge, correlate UART health with the relay pipeline, and hand me a bug report only when a measured failure has a reproducible interval and log excerpt."
- **useful because:** The chips are physically connected to this Mac even though no pendant is registered, and the owner explicitly wanted a pendant that files its own UART bug reports. Today failures in codec, framing, serial transport, and relay stages are observed in separate places; correlating them would turn a noisy bench log into an actionable defect report.
- **path:** mac-terminal → mac-planner → relay-realtime → unified → faculty-perception → faculty-action
- **model tier:** deterministic serial parsing and counter correlation first; background model summarizes only a bounded, redacted failure bundle
- **latency:** Start within 2 seconds; continuously stream counters with no model call; emit a report within 10 seconds of a threshold breach
- **cost:** Under $0.01 per session summary; storage and serial I/O dominate, not inference
- **security:** Restrict reads to the two allowlisted USB serial paths, cap bytes and duration, and never execute arbitrary firmware or shell commands from parsed UART text. Require confirmation before flashing or resetting hardware.
- **missing:** A real bounded USB-serial read action (the granted mac_usb_serial_diagnostics is a build proposal, not callable yet); A correlation adapter that maps UART boot/session and packet counters to relay pipeline IDs; A durable, redacted bench-report artifact with firmware build, timestamps, and reproduction steps

### "When something goes wrong, show me the first point where reality diverged from the plan—not just the final error—and let me compare the intended state, each observed transition, and the earliest contradictory observation."
- **useful because:** Today a Mac job, browser command, relay delivery, and pipeline run can each report a locally successful stage while the overall outcome is false or unknowable. An incident reconstruction would expose the first broken handoff (stale browser session, missing receipt, relay disconnect, or unconfirmed device playback) instead of making the owner debug four logs by hand.
- **path:** relay-realtime → mac-planner → mac-vision → browser-extension → unified → faculty-perception → faculty-judgement
- **model tier:** deterministic event ordering and contradiction detection first; background model summarizes the resulting causal graph only when it contains ambiguity
- **latency:** Under 4 seconds for a bounded incident; no model call for a single unambiguous divergence
- **cost:** Typically $0.01–$0.03 per reconstruction; storage/indexing dominates, with inference reserved for ambiguous causal links
- **security:** Event payloads may contain page text, notifications, or command arguments. Hash and redact bodies before correlation, keep sensitive evidence local, and require confirmation before opening any captured page or replaying an action.
- **missing:** A shared event envelope carrying monotonic and wall-clock timestamps, causal parent, surface, operation ID, and observation-vs-claim type; Relay-side persistence of browser-read and audio-delivery transitions with the same operation ID as Mac receipts; A perception-only graph query that returns the earliest contradiction without executing recovery

### "Whenever you tell me a time, say whose clock it came from and whether it is a Mac-local time, relay time, or my actual local time; never silently convert a device timestamp into my location."
- **useful because:** The Mac has an authoritative America/New_York zone, while the pendant has no captured zone and the relay emits UTC timestamps. A machine-written America/Chicago preference is currently pinned and injected into context despite contradicting the Mac. Without temporal provenance, routine times, device freshness, and 'while I was away' answers can be numerically precise but semantically wrong.
- **path:** relay-realtime → mac-planner → unified → faculty-perception → faculty-judgement
- **model tier:** deterministic timezone and provenance normalization; no model call for conversion, only realtime speech rendering
- **latency:** Under 100 ms for normal timestamp rendering; under 2 seconds when reconciling conflicting stored facts
- **cost:** Near-zero model cost; one bounded memory lookup only when a user-location claim is requested
- **security:** Do not infer physical location from IP, timezone, or device clocks. Treat owner location as unknown unless explicitly stated or supplied by a trusted location source.
- **missing:** A typed timestamp contract requiring clock domain, timezone authority, and provenance on every event; A memory write/repair workflow that can quarantine machine-origin preferences that contradict the authoritative Mac zone; An explicit owner timezone or location signal when the owner wants local-to-their-body time

### "When you say nothing happened, tell me whether that means you observed an empty source, the source was unavailable, the record aged out, or the system never emitted the event at all."
- **useful because:** Several current stores are count-capped rather than time-retained, pendant-held inputs are structurally empty, and device_playback has readers but zero writers. A negative-result classifier prevents the most dangerous perception error: turning an unobservable or unwritten event into a claim that the owner experienced nothing.
- **path:** relay-realtime → mac-planner → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** deterministic source-state classification and retention math; background model only compresses multiple qualified negatives into speech
- **latency:** Under 2 seconds for a bounded query across relay and Mac stores
- **cost:** Under $0.01 per query; structured reads dominate and inference is optional
- **security:** Expose source health and retention metadata without leaking retained page bodies or secret event payloads. Never use an unavailable source as a basis for an automated action.
- **missing:** Per-source freshness, retention, and completeness metadata exposed beside each continuity read; Explicit no-writer and structurally-empty markers in pipeline and pendant-source schemas; A query result type distinguishing observed-zero, unavailable, evicted, never-emitted, and unknown


## What it asked for

_Nothing._
## Its own summary

Fresh live truth: the Mac agent is fully ready (Accessibility, Screen Recording, automation), Safari bridge is online with two tabs and no pending commands, relay and Mac bridge are reachable, but no nRF9160 pendant is registered. I recorded three non-duplicate proposals: an observed/inferred/unknown return audit, deterministic action-path preflight, and a bench UART-to-relay failure reporter for the physically connected chips. The privacy-retention audit collided with an existing backlog item and was not restated.

**Biggest unknown:** The pendant-side reality is still unknowable until it registers or a bounded USB-serial reader is built. I still need four concrete bridges: a last-away/return event, a shared provenance join across relay/pipeline/browser/Mac receipts, a common readiness/blocker schema, and a safe allowlisted serial reader plus UART-to-pipeline correlation. Accessibility is no longer a blocker; the live snapshot proves it is granted.

