# Harness derivation — faculty-perception — round 183

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac and browser reachability** — At round 183 live diagnostics report AI Pendant Agent permissions ready: Accessibility and Screen Recording trusted, all listed automation grants present. Relay is reachable and Mac bridge online. Browser bridge is offline with zero devices and zero pending commands. The relay registry still lists only home-macbook-bridge online and cloudflare-contract-test offline; no pendant is registered.
  - evidence: GET /ops/status liveResponse; GET /browser/status liveResponse; read_continuity_snapshot(include relay,pipeline) body.status and body.status.relay.payload

## Capabilities it proposed

### "Before you act, tell me whether the evidence is trustworthy: is the Mac current, is my browser session reachable, is the pendant actually connected, and are any facts contradictory or stale? If not, explain exactly what is unknown."
- **useful because:** This is the single most important perception capability: it prevents the system from presenting a successful Mac-side receipt, a stale preference, or a relay socket write as reality. Today the live Mac is permission-ready and relay-reachable, but the browser is offline and no pendant is registered; an owner-facing trust verdict would stop confident lies before action.
- **path:** relay → mac → browser → pendant → dashboard
- **model tier:** background for assembling the bounded evidence frame; realtime only to phrase the one-sentence verdict during a live voice turn
- **latency:** Under 500 ms from cached health frames; at most 2 s when a fresh relay and Mac read are required
- **cost:** Near-zero model cost when rule-based; one short realtime turn only if spoken. Dominant cost is the existing bounded HTTP reads, not inference.
- **security:** Return status and provenance, not page contents, secrets, or bearer tokens. Treat machine-origin facts separately from owner-stated facts; never silently repair contradictions. Any action whose trust gate is unknown requires owner confirmation.
- **missing:** A signed, freshness-bounded common health envelope from relay, Mac, browser bridge, and pendant; A contradiction scanner for projected memory facts (including machine-origin timezone); A policy hook in planner/action that refuses to promote unknown or stale evidence into completed claims

### "When a conversation goes wrong, give me a forensic timeline of one utterance: button press, capture quality, uplink gaps, relay receipt, transcription, response generation, downlink packets, and bridge playback—then name the first failed stage and what evidence is missing."
- **useful because:** The owner currently gets a vague failed/completed result and cannot distinguish 'the pendant never captured me' from 'LTE dropped it' or 'the bridge never played the response.' A compact causal timeline turns an invisible wearable failure into one actionable diagnosis, and works as a bench test over USB before LTE registration exists.
- **path:** pendant → relay → mac → dashboard
- **model tier:** background/cheap model for correlating numbered events and thresholds; realtime is unnecessary except for a terse spoken diagnosis
- **latency:** Under 3 s after an utterance ends; raw telemetry remains local and only a small event summary crosses the relay
- **cost:** Very low inference cost; dominant work is firmware counters and event correlation. USB bench runs have no API cost.
- **security:** Use opaque utterance/session IDs, monotonic sequence numbers, and redact audio/transcript by default. Do not upload raw PCM or page content unless explicitly requested. Mark any inferred stage as inferred, never as observed.
- **missing:** A shared utterance correlation ID propagated by firmware, relay job, Mac pipeline, and ESP32 bridge; Bridge-originated playback start/finish/interruption counters, not merely relay sent-bytes; A bounded event joiner that reports first-loss stage and explicit unknowns

### "For my morning brief or any scheduled routine, show me a truth receipt: which sources were actually read, when each was read in New York time, which were unavailable, what was inferred, and whether the spoken brief was generated or delivered."
- **useful because:** Several scheduled routines report completed while the browser is offline or while a relay job only proves bytes were written. This lets the owner distinguish a complete brief from a plausible-sounding partial one without exposing all of their mail or files.
- **path:** mac → relay → browser → dashboard
- **model tier:** cheap background model or deterministic formatter; no realtime reasoning needed unless the owner asks a follow-up
- **latency:** Available within 1 s after a routine; generating the routine itself need not slow down. Historical lookup under 2 s.
- **cost:** Low: receipts are compact metadata and can be assembled without another model call. Storage is bounded per routine run.
- **security:** Store source names, timestamps, freshness, hashes/counts, and failure reasons—not message bodies, URLs with secrets, or credentials. Keep owner confirmation for actions triggered by a routine. Clearly label relay socket delivery versus device playback.
- **missing:** Routine-run stage schema with per-source observed/unavailable/inferred states; A receipt writer spanning Mac routine execution, relay run records, browser reachability, and pendant playback evidence; Dashboard/voice rendering that does not call a routine 'complete' when required sources are unknown

### "If I press the pendant while I am offline or the link drops halfway through, let me reconnect later and continue exactly once—tell me what was captured, what was never sent, resume from the last confirmed boundary, and never replay an already-applied command."
- **useful because:** Today a dropped wearable link can leave the owner repeating themselves or wondering whether a command happened. This would make the pendant dependable in elevators, travel, and dead zones: one honest pending turn, one deduplicated continuation, and an explicit unresolved state instead of a false success.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** cheap deterministic reconciliation for sequence numbers, hashes, and idempotency; use the expensive realtime model only to continue an utterance after the owner explicitly asks
- **latency:** Local capture verdict under 200 ms; reconnect reconciliation under 2 s; continuation begins on the next available voice turn
- **cost:** Low for reconciliation metadata; model cost only for turns the owner elects to resume. The dominant device cost is bounded nonvolatile metadata and occasional retransmission, not raw-audio retention.
- **security:** Encrypt pending audio and command envelopes at rest, bind them to a device/session key, expire them, and never execute a queued destructive action without a fresh owner confirmation. Preserve a distinct pending/accepted/applied state; relay receipt alone is not completion.
- **missing:** A pendant-side encrypted ring of incomplete utterance envelopes with monotonic sequence, content hash, and expiry (separate from the SD failure buffer); Relay and Mac idempotency keyed by utterance ID plus an explicit reconcile endpoint that returns accepted, applied, or unknown; Browser command replay protection and a resume UI/voice interaction that exposes the exact unresolved boundary

### "Let me hold the pendant button to revoke every not-yet-applied action from this conversation—browser clicks, Mac jobs, and relay announcements—and give me a physical confirmation that the cancellation reached each surface."
- **useful because:** A wearable should provide a reliable escape hatch when a screen is unavailable or an action looks wrong. Today cancellation is surface-specific and a relay or browser command can remain pending while the owner has no trustworthy physical way to stop it.
- **path:** pendant → relay → mac → browser
- **model tier:** Deterministic protocol and state machine; no model call is needed to revoke. Realtime only speaks the final compact status if the link is alive.
- **latency:** Local pendant cancellation indication within 150 ms; remote revocation fan-out within 1 s when connected; retain a queued revocation for the next reconnect when offline
- **cost:** Negligible model cost. Small protocol and bounded device-state cost; the main engineering cost is making every action executor honor a common revocation token.
- **security:** Require a deliberate hold/chord to avoid accidental cancellation, authenticate the device command, make revocation monotonic and idempotent, and never claim cancellation of an already-applied side effect. Destructive actions still need their normal confirmation policy.
- **missing:** A cross-surface revocation token and state machine shared by relay jobs, Mac action ledger, and browser commands; Firmware hold gesture, local haptic/LED/audio confirmation, and an offline revocation ring; Executor checks immediately before side effects plus an owner-readable per-surface result


## What it asked for

_Nothing._
## Its own summary

Round 183 established live facts: the Mac agent is fully permission-ready (Accessibility, Screen Recording, and automation), the relay is reachable with the Mac bridge online, the browser bridge is offline with no pending commands, and no pendant is registered. I recorded that boundary and sent it to judgement. Three new proposals were recorded: (1) the single most useful pre-action evidence-trust verdict that blocks stale/contradictory claims, (2) an utterance-level forensic timeline that identifies the first failed stage across pendant→relay→Mac→ESP32, and (3) truth receipts for scheduled routines showing observed, unavailable, inferred, generated, and actually delivered stages. I still need engineering—not another read grant—for a signed freshness envelope, shared correlation IDs, and bridge-originated playback telemetry; the owner need not grant permissions now.

**Biggest unknown:** The pendant remains physically absent/unregistered, so no live claim about LTE, capture quality, or actual playback can be verified. The browser is also offline; browser-dependent actions must remain unknown until its heartbeat returns.

