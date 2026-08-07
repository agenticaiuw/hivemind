# Harness derivation — unified — round 78

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“I was offline—catch me up on anything important, and tell me which actions finished, failed, or still need my approval.”"
- **useful because:** The pendant is the only surface continuously with the owner, but LTE-M drops and the Mac/browser can continue independently. A bounded, spoken catch-up that merges durable relay jobs, browser receipts, Mac results, and locally spooled pendant events prevents silent loss and makes reconnect useful without replaying private content indiscriminately.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** background for event normalization and deduplication; realtime only to answer the spoken catch-up request and prioritize urgent items
- **latency:** On reconnect, index events asynchronously in under 10 seconds; spoken answer should begin within 2 seconds and be at most 30 seconds unless the owner asks for detail.
- **cost:** Usually one small background summarization call plus one short realtime turn; roughly $0.01–$0.05 per catch-up, dominated by summarization/audio generation. Storage is small append-only event metadata; retain payloads only under existing retention policy.
- **security:** Do not put raw email, page text, or secrets into the pendant spool. Store opaque event IDs, sensitivity labels, status, timestamps, and short redacted summaries; fetch full evidence only after an explicit follow-up. Never execute pending destructive actions; identify approval gates clearly.
- **missing:** A durable cross-surface event envelope with source, sensitivity, timestamp, causal/job ID, and approval state; Pendant reconnect/clock-safe spool and acknowledgement protocol; A merged catch-up query over job receipts, browser command results, and Mac relay jobs; A spoken urgency/privacy policy for which events may interrupt versus wait

### "“Pack what I’ll need for the next few hours onto the pendant so I can ask about it without a connection.”"
- **useful because:** Today the pendant becomes largely blind when LTE-M drops. A deliberate offline capsule would let the owner access a small, current subset of their agenda, approved notes, travel details, and selected logged-in page summaries during travel or dead zones, then reconcile harmless annotations after reconnect. This is different from a later catch-up report: it is proactive, owner-chosen context available while offline.
- **path:** pendant → mac-planner → browser-extension → relay → dashboard
- **model tier:** Background model on the Mac/relay to select and compress requested material; deterministic firmware lookup and small realtime responses offline. No expensive model call for direct indexed retrieval.
- **latency:** Build in under 60 seconds for a normal capsule; transfer over the local bridge in under 15 seconds; offline answers should start in under 500 ms.
- **cost:** Roughly $0.01–$0.08 per pack, dominated by one background summarization pass. Storage is bounded by an owner-selected size cap; no recurring model cost for offline lookup.
- **security:** The capsule contains private calendar, notes, files, or authenticated-page excerpts and must be encrypted at rest with a device-bound key, expire automatically, and support immediate remote revocation on reconnect. The owner must choose categories or approve an automatically suggested manifest. Never cache passwords, payment data, or unrestricted page HTML; show provenance and capture time for every answer.
- **missing:** An encrypted, expiring offline-capsule format and key lifecycle spanning Mac, relay, and pendant SD; Mac/browser exporters that produce redacted records with source URLs, timestamps, and sensitivity labels; A bounded on-device index/query path that fits the pendant’s current RAM and survives power loss; A sync protocol for owner-created offline annotations, with conflict handling and no automatic external side effects; Dashboard controls to inspect, revoke, expire, and erase a capsule


## Changes it proposed to its own stack

### `relay` — Add a durable cross-surface event ledger and catch-up index. Normalize pendant reconnect markers, relay job transitions, Mac receipts, browser command results, and approval checkpoints into one append-only envelope (eventId, causalId, source, occurredAt, receivedAt, sensitivity, redactedSummary, state). Maintain per-owner acknowledged cursor and idempotent deduplication; expose a bounded catch-up query that returns only events since the cursor, groups causal chains, and omits sensitive payloads until explicitly requested.
- **owner gets:** After a dropped LTE-M link or while the owner is away from the Mac, they can ask the pendant what matters and receive a trustworthy answer instead of guessing whether work completed or silently repeating it.
- effort: Medium: schema/migrations, adapters for existing job/browser/Mac receipt writers, reconnect cursor protocol, redaction tests, and a compact spoken formatter.  ·  risk: Duplicate or incorrectly ordered events could cause confusion or repeated actions. Recover with causal IDs, monotonic per-source sequence plus received-time ordering, idempotent inserts, and a dashboard replay/repair tool. Never treat a catch-up item as authorization.
- cost: Low D1/R2 metadata overhead; background normalization can use a cheaper model only for ambiguous summaries. No model call needed for ordinary status events.  ·  latency: Reconnect status available in one database read; summarization under 2 seconds for a small queue, with larger histories paginated.
- security: Improves privacy if raw payloads remain behind existing access controls and only redacted summaries enter the pendant channel; requires explicit sensitivity classification and deletion propagation.
- depends on: A stable event envelope and redaction policy; Pendant reconnect acknowledgment/cursor support; Adapters in the Mac job receipt and browser bridge writers

### `hardware` — Add a low-power I2C fuel-gauge and a temperature-compensated RTC (with coin-cell or supercap backup) to the production pendant, exposing battery state, brownout markers, and trusted wall-clock/monotonic correlation to firmware. Keep the nRF9160 modem as the network time source when available, but persist the last correlation and boot/reconnect sequence across power loss.
- **owner gets:** The pendant can warn before an LTE/audio session dies, preserve honest 'since you were offline' ordering, and avoid claiming an action happened at the wrong time after a battery brownout or modem reboot.
- effort: Medium hardware spin plus firmware driver, calibration, and event-schema changes; validate against LTE transmit bursts and SD writes.  ·  risk: Extra BOM and another I2C device can introduce bus contention or inaccurate readings. Recover with conservative thresholds, watchdog-safe fallback to modem time, and treating uncertain timestamps as approximate rather than silently fabricating precision.
- cost: Approximately $2–$6 BOM increase in low volume; fuel gauge typically tens to hundreds of µA active and RTC a few µA or less, materially below LTE burst draw.  ·  latency: Battery/clock reads are sub-millisecond to a few milliseconds; no conversational latency impact.
- security: Clock state is metadata only; protect it from being used as authorization. Do not persist sensitive content alongside it.
- depends on: Production pendant electrical design and enclosure review; A defined reconnect/event timestamp schema; Firmware power-budget and I2C pin allocation

### `integration` — Introduce an encrypted Offline Capsule protocol: the Mac/browser exporters create a signed manifest of owner-approved, redacted records; the relay issues a short-lived capsule key and version; the pendant stores only the encrypted records plus a compact field index on SD, with an expiry and erase-on-revocation flag. On reconnect, sync only annotations and capsule acknowledgements—never execute actions from capsule data automatically.
- **owner gets:** They can leave Wi-Fi/LTE coverage with the exact small set of information they chose and still ask the pendant useful questions, without turning the wearable into an uncontrolled copy of their private computer.
- effort: High: capsule schema and cryptography, browser/Mac export adapters, pendant SD/index/query firmware, bridge transfer, expiry/revocation, and power-loss recovery tests.  ·  risk: A stolen pendant or stale capsule could expose private information, and sync conflicts could lose annotations. Mitigate with device-bound encryption, short TTLs, category-level approval, key revocation, signed manifests, atomic SD writes, and read-only offline semantics.
- cost: Low recurring API cost after packing; modest SD and relay storage. Firmware work is the main cost; no new model call during offline use.  ·  latency: Packing is asynchronous; local lookup remains sub-second. Initial transfer may take seconds over the bridge and should show progress.
- security: Adds a deliberate encrypted data boundary and revocation path, but increases the amount of sensitive data physically present on the pendant. Default to minimal manifests, no secrets/payment data, and automatic expiration.
- depends on: A production pendant key-storage strategy; Mac/browser redaction and provenance exporters; Pendant SD atomic-write and compact-index support; Owner-defined capsule categories, size limit, and expiry


## What it asked for

_Nothing._
