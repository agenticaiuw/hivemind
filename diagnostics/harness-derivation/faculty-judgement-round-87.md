# Harness derivation — faculty-judgement — round 87

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Did that actually reach me?” — For any spoken answer, briefing, or Mac job, show whether it was generated, accepted by the relay, downloaded by my pendant, and played; if any link is missing, say exactly which one and keep retrying safely."
- **useful because:** Today a successful Mac/relay receipt can still leave the owner unaware that audio never arrived at or played on the wearable. This gives a trustworthy end-to-end answer instead of conflating 'created' with 'heard', and lets a later retry resume without duplicating a notification.
- **path:** mac-planner → relay-realtime → pendant → unified → faculty-perception → faculty-judgement → faculty-action → dashboard
- **model tier:** Use a cheap background state machine for correlation, retries, and receipt reconciliation; reserve realtime for the owner's immediate spoken status question and for a concise final alert. No expensive reasoning is needed for ordinary state transitions.
- **latency:** Record generation and relay acceptance immediately; pendant acknowledgment should appear within 2 seconds of download/playback. Reconcile missing acknowledgments in the background with exponential backoff, and report a definite unknown after a bounded window rather than claiming failure.
- **cost:** Near-zero model cost for transitions and retries; roughly one short realtime turn only when the owner asks or a policy-selected delivery failure needs explanation. Storage/network dominate: a few hundred bytes of receipt state per artifact plus one small event per lifecycle transition.
- **security:** Receipts must contain opaque artifact IDs and timestamps, not audio or message content. Playback acknowledgment is sensitive presence data; encrypt it, retain it briefly, and expose only to the owner's authenticated surfaces. Never auto-retry an irreversible Mac action—only audio delivery and other explicitly idempotent artifacts.
- **missing:** A durable cross-surface delivery ledger keyed by artifact/job ID with monotonic lifecycle states and idempotency keys.; Relay acceptance and pendant download/playback ACK events, including explicit 'no registered pendant' and offline states.; Pendant firmware event emission and a small local retry/ACK queue that survives a dropped link.; Dashboard and voice formatting that distinguish generated, accepted, downloaded, played, expired, and unknown.

### "“Take me back to what was true when I made that decision.” Show a dated, evidence-linked snapshot of my relevant calendar, mail, browser pages, Mac files, conversations, and pending tasks, then show only what changed afterward and which assumptions are no longer true."
- **useful because:** People routinely lose the context behind decisions: a meeting moved, a price changed, a document was edited, or an email thread evolved. Today the system can read current surfaces and some action receipts, but cannot reconstruct a trustworthy personal state at a past moment. This would let the owner recover intent without relying on memory or searching five systems manually.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → mac-terminal → unified → faculty-perception → faculty-judgement → faculty-action → dashboard
- **model tier:** Use background jobs to capture normalized, permission-filtered state deltas and hashes; use a cheaper model to index and cluster changes. Use the expensive realtime tier only to answer the owner's retrospective question and explain conflicting evidence.
- **latency:** Snapshots should be incrementally maintained with seconds-to-minutes freshness. A retrospective query should return an initial dated outline within 3 seconds, followed by cited evidence and unresolved gaps. Never block the owner waiting for a complete crawl.
- **cost:** Background cost is dominated by storage and periodic local extraction, not model calls. Retain compact metadata, hashes, snippets, and source pointers rather than copies of private pages; invoke a model only for ambiguous change summaries. A query costs roughly one normal reasoning turn plus retrieval.
- **security:** Historical state is more sensitive than current state because it can expose deleted or changed information. Keep raw content on the originating Mac/browser where possible, encrypt the index, enforce per-source retention and deletion propagation, and clearly label reconstructed versus directly observed facts. Do not resurrect deleted secrets or display them without an explicit request.
- **missing:** An append-only, privacy-aware temporal state ledger for permitted Mac, browser, relay, and pendant observations.; Versioned source snapshots or content hashes with timestamps, provenance, and deletion/retention semantics.; A cross-surface diff and contradiction engine that can distinguish changed facts from missing observations.; A user-facing historical query and citation format that states confidence and gaps instead of fabricating a complete past.; A pendant-friendly capture marker so the owner can say “mark this moment” and anchor a later reconstruction to a specific decision.


## Changes it proposed to its own stack

### `firmware` — Add an idempotent audio-delivery receipt protocol to the pendant: the server assigns an opaque artifact/session ID; firmware emits downloaded, playback-started, playback-finished, interrupted, and checksum/error events with a monotonic sequence; a bounded flash ring retries them after reconnect. Add relay-side correlation that merges these events with Mac job receipts and marks explicit terminal states (played, failed, expired, no-pendant, unknown). Keep the device implementation under ~4 KB RAM and a few KB flash metadata, separate from the 24 kHz audio buffers.
- **owner gets:** When the owner asks whether a briefing or answer reached them, they get an honest answer about what was actually heard—not a misleading 'completed' from the Mac. Dropped links become recoverable instead of silent.
- effort: Medium: define event schema and idempotency semantics, firmware ring and reconnect upload, relay/D1 ledger and reconciliation, then exercise loss/duplication/reboot tests across Mac, relay, and pendant.  ·  risk: Clock skew, power loss during playback, duplicate events, and firmware upgrades could create contradictory states. Recover with monotonic sequence numbers, server-side dedupe, explicit unknown states, schema versioning, and never upgrading a partial receipt to played without the pendant event.
- cost: Negligible model/API cost; small D1/R2 metadata and cellular traffic. Firmware flash/RAM impact is metadata only; audio storage is unchanged.  ·  latency: One small event per lifecycle transition and at most a few hundred milliseconds of upload work; user-facing status can remain immediate with 'pending' until the ACK arrives.
- security: Use opaque IDs, authenticated transport, replay protection, and short retention. Do not send audio, transcript, or sensitive content in receipts; playback timing itself should be access-controlled.
- depends on: A pendant link/session identifier and authenticated event-upload endpoint; A durable relay delivery ledger that can join Mac job IDs, TTS artifact IDs, and pendant artifact IDs; The 24 kHz audio path accepting artifact metadata and completion callbacks; A dashboard/voice renderer for explicit played/unknown/no-pendant states

### `memory` — Build an append-only temporal evidence ledger that stores compact, permission-filtered observations and deltas from the pendant, relay, Mac, and authenticated browser. Each record gets source, observedAt, validAt, expiry, confidence, content hash, retention class, and deletion tombstone. Add snapshot reconstruction and change-diff queries that refuse to fill gaps with current facts.
- **owner gets:** The owner can recover the actual context behind an old decision and see what changed afterward, rather than receiving a plausible but historically false summary assembled from today's state.
- effort: Large: define temporal fact semantics, local extraction and hashing, encrypted storage, deletion propagation, cross-surface identity resolution, contradiction handling, query citations, and retention controls; test with moved meetings, edited files, changed web pages, and deleted mail.  ·  risk: A historical ledger can become a covert archive of sensitive material or present stale facts as truth. Mitigate with source-level opt-in, short default retention, deletion tombstones, explicit observed-versus-inferred labels, confidence scores, and a hard rule that absent evidence remains unknown.
- cost: Storage and local indexing grow with enabled sources; model cost stays low through delta extraction and on-demand summarization. Browser/private content should remain local unless the owner explicitly asks for cross-surface synthesis.  ·  latency: Incremental capture is asynchronous. Historical queries add retrieval and diff work but can stream an initial outline quickly, with deeper evidence loaded afterward.
- security: Requires encryption at rest and in transit, per-source authorization, audit logs for historical reads, and a prominent “what was retained” control. Deleted source data must be removed or irreversibly redacted from derived records.
- depends on: A durable event/observation schema shared by relay, Mac, browser, and pendant; Local hashing and extraction hooks for files, browser pages, mail, calendar, and voice markers; A retention/deletion policy that applies to derived snapshots as well as source content; A historical query surface in voice and dashboard


## What it asked for

### `s9-vtxc` (skill) — audio_delivery_ack_queue
- does: For each downloaded audio artifact, persist an opaque artifact ID, byte-range/checksum, download completion, and playback start/finish (or interruption) event. Retry unsent ACKs over the link, deduplicate by event ID, and expose a local LED/button-safe status when the queue cannot be uploaded.
- must be on-device because: Only the pendant knows whether bytes arrived intact and whether the owner actually started or finished hearing them. It must preserve that evidence across a dropped cellular/BLE link and report it later without relying on the server staying connected.
- trigger: Server-pushed audio download and local playback start/stop/error events; upload on reconnect or scheduled link opportunity.
- storage: A bounded append-only ring in nonvolatile settings/flash: 32 records of about 96 bytes plus a small upload cursor and schema version (under 4 KB); drop only superseded ACKs after server confirmation.
- RAM budget: About 3 KB worst case for one decoded event, ring serialization, and retry buffer—well below the 211,608 B application RAM budget. Keep audio buffers separate and stream ACKs; do not retain audio in this queue.

### `t23-hkrj` (tool) — record_pendant_delivery_event
- why: The existing job and pipeline receipts stop at server-side generation/acceptance; no current tool can ingest or reconcile a pendant's authenticated downloaded/played ACK, including offline replay and duplicate suppression.

```json
{
  "type": "object",
  "required": [
    "artifactId",
    "deviceSessionId",
    "eventType",
    "deviceSequence",
    "occurredAtMonotonicMs",
    "eventId"
  ],
  "properties": {
    "artifactId": {
      "type": "string",
      "description": "Opaque audio artifact identifier"
    },
    "deviceSessionId": {
      "type": "string",
      "description": "Authenticated pendant session identifier"
    },
    "eventType": {
      "type": "string",
      "enum": [
        "downloaded",
        "playback_started",
        "playback_finished",
        "playback_interrupted",
        "checksum_error",
        "no_audio"
      ],
      "description": "Observed local delivery state"
    },
    "deviceSequence": {
      "type": "integer",
      "minimum": 0
    },
    "occurredAtMonotonicMs": {
      "type": "integer",
      "minimum": 0
    },
    "eventId": {
      "type": "string",
      "description": "Stable deduplication key"
    },
    "bytesReceived": {
      "type": "integer",
      "minimum": 0
    },
    "expectedBytes": {
      "type": "integer",
      "minimum": 0
    },
    "playbackPositionMs": {
      "type": "integer",
      "minimum": 0
    },
    "reason": {
      "type": "string"
    }
  }
}
```

