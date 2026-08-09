# Harness derivation — faculty-perception — round 243

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac and browser readiness** — At 2026-08-09T02:11Z, GET /ops/status reports AI Pendant Agent permissions ready: Accessibility trusted, Screen Recording granted, all listed automation grants present; browser extension online with 2 tabs and 0 pending commands; relay reachable, D1-backed, and Mac bridge online. This supersedes earlier 'permissions denied' assumptions.
  - evidence: Authenticated GET /ops/status returned status.permissions.ready=true, accessibility.trusted=true, screenRecording.granted=true, browser.online=true, relay.reachable=true, relay.payload.store='d1', relay.payload.macBridgeOnline=true.

## Capabilities it proposed

### "Before you do it, can you tell me whether this request is actually verifiable right now—and what would count as success?"
- **useful because:** The system currently starts actions while quietly lacking a live browser, permission, relay, or playback fact. This gives the owner a plain-language preflight: which surface will act, what fresh observation supports it, what is stale or unavailable, and the exact postcondition that can later be checked. It prevents confident actions built on the wrong machine, tab, or old pipeline trace.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** background for the initial evidence scan; realtime only to phrase the short answer
- **latency:** Under 2 seconds when all surfaces are online; 5 seconds if browser and relay freshness probes are needed
- **cost:** Usually <$0.01; dominated by one cheap structured scan, not a realtime generation
- **security:** Read-only by default. Return hashes/identifiers instead of page text; never expose cookies or protected browser content. Require confirmation before any probe that opens a page or changes a session.
- **missing:** A typed preflight endpoint that accepts intent plus required postconditions and returns evidence, freshness, conflicts, and an execution plan; The requested faculty-action verifier keyed by operation_id/step_id; A standard freshness policy per source (browser tab, relay job, Mac permission, pipeline trace)

### "Show me every place the system disagrees about what is true right now."
- **useful because:** A single 'online' label hides distinct realities: the Mac bridge can be live while no pendant is registered, the browser can be online while holding a stale tab, and a pipeline can say completed without playback evidence. This gives the owner a compact disagreement matrix instead of a falsely unified status, with each claim's source, timestamp, scope, and confidence. It is perception—not an action—and remains useful even when no surface can execute.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** background structured comparison; realtime only when the owner asks verbally
- **latency:** 1–3 seconds from cached status; up to 6 seconds for fresh browser and relay reads
- **cost:** <$0.01 per scan; mostly local JSON and HTTP reads, with no large prompt payload
- **security:** Do not copy page bodies, audio, tokens, or private app contents into the matrix. Use opaque IDs, hashes, status enums, and timestamps. Scope each claim (Mac-resolved vs owner/location vs device-reported) so it cannot imply facts beyond its authority.
- **missing:** A disagreement-matrix route that normalizes claims from /ops/status, /ops/snapshot, /pipeline, /browser/status, and relay /v1/devices/status; Explicit authority/scope metadata on each status claim (especially Mac-resolved timezone versus owner location); A freshness contract and monotonic snapshot timestamp shared across relay, Mac, browser, and future pendant

### "Is the pendant I plugged in actually healthy end to end, or is it only powered?"
- **useful because:** Today a bench-connected nRF9160 and audio bridge can be physically present while the relay has no registered pendant and historical pipeline audio looks deceptively healthy. This gives the owner one honest verdict that separates USB presence, firmware boot, serial health frame, relay registration/heartbeat, WebSocket acknowledgement, audio loopback, and the exact failing boundary—something no single node can establish.
- **path:** mac-planner → relay-realtime → pendant → dashboard
- **model tier:** background deterministic probe and measurement; use realtime only to explain the final verdict
- **latency:** 15–30 seconds for a bounded serial exchange plus relay and audio checks
- **cost:** <$0.02 per run; dominated by no-model serial/HTTP probes and a short known-tone audio test
- **security:** Bench-only, read-only except for an explicit test-tone request. Restrict serial paths to the two known USB devices, cap bytes/time, redact firmware keys and serial numbers, and require confirmation before transmitting audio or altering firmware.
- **missing:** A live mac_usb_serial_diagnostics capability that can perform bounded reads on the nRF9160 and ESP32 ports (the requested grant is not yet callable); A pendant diagnostic response containing the accepted offline-reality-beacon frame and a nonce-correlated relay acknowledgement; A relay endpoint that reports device registration and WebSocket handshake by nonce, not merely stale registry rows; A deterministic audio test route with measured packet loss, decode timing, and playback/bridge evidence

### "Before you use my logged-in browser or send anything, can you ask me on the pendant exactly what data will leave and get a one-time confirmation?"
- **useful because:** The owner gets a real, comprehensible consent boundary at the moment of risk instead of trusting a buried permission or a vague 'okay'. The pendant can state the destination, fields, and action scope; the relay can bind the approval to one operation; the Mac/browser can refuse any broader request. This is a genuinely cross-surface capability: the browser has the secret session, the Mac performs the action, the relay mints the short-lived authority, and the worn device is where the owner can approve or deny.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Realtime only for the short spoken consent prompt; deterministic policy enforcement and token checking everywhere else
- **latency:** A consent prompt in under 1 second; approval expires after 60 seconds and authorizes exactly one operation
- **cost:** Negligible model cost; one short realtime turn, with most work in signed token validation
- **security:** Never read or summarize secrets to obtain consent. Show destination, data classes, exact fields, and irreversible effects; default deny on timeout, replay, scope widening, or device mismatch. Store a hash-only consent receipt, not the private payload or audio.
- **missing:** A relay-issued, single-use capability token bound to operation_id, destination, field set, expiry, and pendant session; Pendant firmware/UI for a concise spoken prompt plus physical accept/reject and nonce echo; Browser and Mac executors that enforce the token rather than merely logging approval; A typed policy describing which actions always require owner confirmation

### "When I say 'save this moment', can you preserve the exact conversation, what was on my active browser tab, and what the Mac was showing—so I can revisit it without pretending those sources said the same thing?"
- **useful because:** Today capture, browser state, and pipeline audio are separate and can be overwritten or lose their join. A user-visible moment object would let the owner recover the context of a decision or idea, with each component independently labeled as captured, unavailable, stale, or redacted. It is useful precisely because it does not collapse a browser claim, spoken audio, and Mac UI into one false transcript.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Background deterministic assembly; use realtime only to confirm the bookmark name
- **latency:** Acknowledge in under 1 second; finalize the bundle within 5 seconds
- **cost:** <$0.01 per bookmark; storage and hashing dominate, not model tokens
- **security:** Explicitly exclude passwords, cookies, hidden browser fields, and arbitrary screen recording. Let the owner choose audio-only, tab-only, or full bundle. Encrypt private audio and page excerpts, provide expiry and deletion, and expose source-by-source provenance instead of a blended summary.
- **missing:** A durable cross-surface moment schema joining captureId, pipeline/audio range, active browser tab snapshot, Mac observation, and relay turn ID; An atomic coordinator that records near-simultaneous snapshots with per-source timestamps and unavailable markers; Owner-facing retention/redaction controls and a replay view that keeps evidence boundaries visible


## Changes it proposed to its own stack

### `context` — Add a provenance firewall before contextProjection emits the pinned Owner block: for machine-origin preferences and high-confidence facts, run a read-only contradiction check against authoritative live sources (for example /etc/localtime via machine-context and current device/relay status). If contradicted, keep the stored fact untouched but emit it in a quarantined 'machine claim conflicts with live fact' section with source, age, and override reason; never inject it into the cacheable Owner head until the owner confirms it.
- **owner gets:** The owner stops receiving a wrong, machine-authored fact as if it were their own preference. Today the stale America/Chicago timezone is pinned at confidence 0.99 and injected into every prompt despite the Mac being America/New_York. Quarantine makes the disagreement visible without silently rewriting the owner's memory.
- effort: Moderate: contradiction rules, a quarantine projection section, and tests for provenance/source.origin; no new storage schema required.  ·  risk: A live source can itself be stale or scoped incorrectly; show both claims and timestamps rather than deleting either. Recovery is owner confirmation or an explicit override. Avoid running arbitrary network probes during prompt construction.
- cost: Negligible runtime cost for local facts; one cheap structured check per projection, no model call.  ·  latency: Tens of milliseconds locally; cache the check briefly and invalidate on machine-context refresh.
- security: Improves safety by preventing untrusted machine claims from becoming owner intent. Keep raw sensitive fact values out of telemetry; record only source and conflict class.
- depends on: The existing source.origin field and contextProjection path; GET /machine-context and its authoritative timezone observation; An owner-confirmation route or existing memory fact edit flow

### `interaction` — Add a 'safe handoff' mode that turns a long-running Mac/browser operation into an owner-visible state machine: the Mac pauses at the next irreversible boundary, the relay sends a compact state summary to the pendant, and the owner can resume, narrow, or cancel with a physical button. Every resume carries a new scoped lease; an old voice turn or stale browser command cannot continue it.
- **owner gets:** The owner can walk away from a fragile multi-step task without wondering whether it kept clicking, sent a message, or got stuck. They can resume from the pendant with a truthful checkpoint and cancel even when they are not at the Mac.
- effort: High: add pause points and lease enforcement to Mac/browser executors, relay state transitions, pendant control frames, and a dashboard showing the checkpoint.  ·  risk: A pause may leave an external site in a partially completed state; only pause at declared safe boundaries and expose the last confirmed side effect. Recover with idempotency keys and an explicit cancel/undo path where available.
- cost: Low ongoing API cost; a few relay state writes per step. Engineering cost is in executor instrumentation and firmware controls.  ·  latency: Sub-second control response when connected; offline pendant commands must be queued with expiry and never blindly replayed.
- security: Improves safety by making continuation leases device-bound, single-use, and expiring. Never let a stale queued command resume a privileged browser session.
- depends on: A common operation state/lease contract across /jobs, browser commands, and relay jobs; Pendant control/ack frames and offline queue semantics; Existing action ledger and job receipts being exposed as checkpoint evidence


## What it asked for

_Nothing._
## Its own summary

Established fresh live truth: Mac Accessibility and Screen Recording are now granted and permissions.ready=true; browser extension is online with two tabs and no pending commands; relay is reachable on D1 and Mac bridge is online. Proposed (1) typed verifiable preflight, (2) cross-surface disagreement matrix, (3) end-to-end USB pendant health verdict, and a context provenance firewall for contradictory machine-origin facts. I still need a callable bounded USB serial reader, nonce-correlated pendant diagnostic/relay handshake evidence, and the typed operation-step verifier with postconditions and provenance. The pendant itself still has no relay registration/heartbeat, so I cannot claim it is healthy from current relay state.

**Biggest unknown:** Whether the physically connected nRF9160/ESP32 bench hardware is emitting the expected health frames; the granted serial capability is not yet callable, so USB presence and firmware state remain unobserved.

