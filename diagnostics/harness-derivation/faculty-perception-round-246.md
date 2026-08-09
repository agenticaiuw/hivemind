# Harness derivation — faculty-perception — round 246

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac and relay observability at 2026-08-09T03:21Z** — Mac agent is fully ready: Accessibility, Screen Recording, and all listed Automation grants are true; browser extension online on Safari YouTube; relay reachable and D1-backed. Local /v1/devices/status is not a Mac-agent route (404), while device discovery shows nrf9160-pendant offline with lastSeenAt 2026-08-09T02:56:31Z. Pipeline truth explicitly says recent audio was accepted by relay but heard is unknown because no device_playback event exists.
  - evidence: GET /ops/status 200, discover(devices), GET /pipeline 200 (job_909... delivery.heard=unknown), GET /v1/devices/status 404 on localhost:8000

## Capabilities it proposed

### "“Prove that answer.” (For any recent answer, show me exactly what source it used, what changed since it was read, and whether it reached my ears.)"
- **useful because:** Today the system can show a Mac action completed or relay bytes were accepted, but it cannot join a relay/browser reading to a durable source capsule, and it cannot distinguish accepted audio from heard audio. This gives the owner an honest, inspectable answer instead of a confident reconstruction.
- **path:** browser → mac → relay → pendant → dashboard
- **model tier:** background for capsule joining and change comparison; realtime only to answer the spoken question
- **latency:** Under 2 seconds for an existing capsule and pipeline record; under 10 seconds if it must refetch the page.
- **cost:** Usually <$0.01 per proof; dominated by one browser fetch or a small background comparison, not the realtime model.
- **security:** Redaction must happen before hashing or persistence; secret page regions remain withheld. Never claim playback from relay acceptance. Require confirmation before exposing sensitive source text on the pendant.
- **missing:** Relay read_web_page must return a stable read ID and content hash, then a Mac bridge must mint the existing evidence capsule (no new schema).; The pendant must emit the already-granted audio_delivery_ack_queue playback events, and the relay/pipeline reader must join them to the answer artifact.; Mount browser provenance routes so grounded claims can be inspected rather than leaving the evidence store as a passive file.

### "“Only interrupt me if it is worth it.”"
- **useful because:** A wearable assistant should know the owner is already in a meeting, watching a video, speaking, or offline before it speaks. This is not a quiet-hours schedule: it is a live, cross-surface interruption decision that prevents a routine brief or low-priority relay announcement from talking over the owner while preserving genuinely urgent items.
- **path:** pendant → mac → browser → relay → dashboard
- **model tier:** cheap background classifier/rules for the interruption score; realtime model only for urgent spoken escalation
- **latency:** Decision within 300 ms of a pending announcement; no model call on the normal path.
- **cost:** Near-zero per event with rules and a compact state frame; occasional <$0.001 classifier call only for ambiguous context.
- **security:** Active-window titles, browser URLs, calendar state, and pendant VAD are sensitive. Keep raw titles local, send only coarse states (in_call, media_playing, owner_speaking, idle). Never silently suppress safety-critical alerts; show suppressed items in the dashboard and replay them only after a policy-defined recovery point.
- **missing:** A Mac-side active-media/meeting state feed that does not require scraping screenshots; AppleScript can cover supported apps, while Screen Recording is now granted for the fallback.; The pendant offline-reality-beacon and capture-integrity-sentinel frames must be connected to a live interruption policy; the beacon currently has no relay registration in this run.; A relay announcement policy evaluator that can hold, downgrade, or escalate items based on urgency and the owner's stated interruption budget.; A durable suppressed-item ledger with an explicit reason and expiration, distinct from the existing bytes-to-socket delivered state.

### "“Do this even if the network goes away, and finish it when you come back—exactly once.”"
- **useful because:** Today an offline utterance can be captured or a relay job can be queued, but the owner cannot know whether a delayed request was merely stored, partially executed, or executed twice after reconnection. This would make intermittent LTE a tolerable condition instead of a source of duplicate reminders, notes, or purchases.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** small deterministic reconciliation worker for identifiers, ordering, and receipts; use the expensive realtime model only for the initial ambiguous intent
- **latency:** Local capture acknowledgement under 200 ms; reconciliation within 5 seconds of reconnect; destructive or financial continuation still pauses for confirmation.
- **cost:** Usually <$0.002 per deferred request; storage and reconciliation dominate, not inference.
- **security:** The pending intent must be encrypted at rest on the pendant and Mac, bound to the owner/session, and expire. Never replay a destructive browser or Mac action solely because connectivity returned; require a fresh confirmation if the original confirmation window expired.
- **missing:** A durable intent envelope with a monotonic device sequence, idempotency key, expiry, and explicit execution phase—not just an audio file or relay job.; A relay/Mac exactly-once reconciliation protocol that can prove accepted, executed, or unknown after a crash and never infer success from a socket write.; Browser and Mac action endpoints must accept and persist the idempotency key through their receipts, including the current pending-approval state.; A user-visible recovery inbox that explains deferred, resumed, skipped, and uncertain work in one place.

### "“Give me the answer now, then quietly verify it and only interrupt me if it changed.”"
- **useful because:** The owner currently has to choose between a slow verified answer and an immediate answer with no reliable follow-up. A staged answer makes the wearable useful during motion while preserving accuracy for changing web, calendar, and machine state.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** realtime for the first short answer; cheaper background model plus deterministic source checks for verification
- **latency:** First spoken answer within 1 second; verification within 30 seconds; correction is silent unless material, safety-relevant, or explicitly requested.
- **cost:** First answer uses the normal realtime turn; verification is typically <$0.005 and only runs for claims marked volatile.
- **security:** The first answer must be labeled provisional in the event ledger and never trigger an irreversible action. Background verification must respect browser/session permissions and redact sensitive page content before storing a diff. Require confirmation before speaking a correction in a meeting-sensitive context.
- **missing:** A claim ledger that records the exact claim, volatility class, source snapshot, and verification deadline rather than only a final transcript.; A background verifier that can re-read through the browser bridge or Mac APIs and calculate a meaningful change, not just compare model prose.; A pendant/relay policy for silent correction, audible correction, and dashboard-only correction, with the reason visible to the owner.; A join between verification results and the original spoken turn so a correction cannot be mistaken for a new command.


## Changes it proposed to its own stack

### `relay` — Replace the binary pendant online/offline label with a three-state presence contract: connected (active authenticated WebSocket), recently-heard (last device-originated beacon/heartbeat within a bounded window), and registry-stale (row exists but no device-originated evidence). A converse connection must update a session-scoped lastConnectedAt without pretending it is a heartbeat; the Mac bridge must never author pendant lastSeenAt. Surface the state and evidence source in /v1/devices/status and the dashboard.
- **owner gets:** When the pendant disappears, the owner can tell whether it is powered off, merely has no LTE, or is an old registry row. Today “offline” can mean “never heartbeated,” while a Mac-authored timestamp can look like pendant health; this prevents false reassurance and false outage reports.
- effort: Moderate relay schema/response and firmware beacon integration; retain old fields for compatibility and add evidenceSource, activeSession, and state.  ·  risk: Clients that assume boolean online may mis-handle the new state. Keep online as a deprecated derived field, add contract tests, and make unknown/stale conservative (never claim connected).
- cost: Tiny D1 write on connect/heartbeat and bounded row growth; no model cost.  ·  latency: No added conversational latency; status reads add one small field computation.
- security: Do not expose bearer credentials or raw socket identifiers. Authenticate beacon/heartbeat with the scoped pendant credential rather than the current admin-key WebSocket path.
- depends on: offline-reality-beacon firmware skill; a real nRF pendant registration/heartbeat writer; GET /v1/devices/status on the cloud relay rather than the Mac agent; relay D1 persistence

### `hardware` — Add a low-power skin/proximity presence sensor to the pendant enclosure (for example, capacitive electrode plus a simple contact/ambient baseline), sampled locally and represented as coarse worn / nearby / absent state. Fuse it with the existing offline health frame, but never transmit raw sensor values or treat presence as proof of identity.
- **owner gets:** The system can stop speaking as though the owner is wearing the pendant when it is sitting on a desk or plugged in for bench work, and can choose a Mac/browser fallback without asking the owner to explain why the wearable is not being heard.
- effort: Moderate enclosure/PCB revision, calibration across clothing and charging states, and a small firmware state machine; explicitly not a software-only patch.  ·  risk: False absent/worn readings could suppress a useful response. Recover by using presence only as a confidence signal, retaining an unmistakable manual override, and falling back to Mac delivery rather than dropping content.
- cost: Roughly $1–$4 BOM increase and sub-mW average draw; enclosure and PCB rework dominate cost.  ·  latency: Sensor state available within roughly 1–2 seconds; no conversational model latency.
- security: Local coarse state only; no camera, microphone, biometric identity, or raw capacitance leaves the device.
- depends on: A physical pendant enclosure/PCB revision; offline-reality-beacon frame schema; relay delivery policy that can consume a non-authoritative presence hint


## What it asked for

_Nothing._
## Its own summary

Established fresh live truth: Mac permissions and browser are ready, relay is reachable/D1-backed, nrf9160-pendant appears stale/offline, and pipeline explicitly confirms relay acceptance is not hearing. Recorded three non-duplicate directions: proof-carrying answers, interruption-budget control, and conservative three-state presence.

**Biggest unknown:** Whether the nRF9160 currently has a physical powered session; the registry row is stale and the firmware has no trustworthy heartbeat/playback emitter yet.

