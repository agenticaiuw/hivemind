# Harness derivation — faculty-perception — round 207

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac permissions and browser** — At 2026-08-08T23:51Z the Mac agent reports Accessibility and Screen Recording granted, all required automation permissions granted, browser extension online in Safari with 2 tabs, current YouTube tab, and zero pending browser commands.
  - evidence: GET /ops/status HTTP 200 and GET /machine-context HTTP 200; response fields permissions.ready=true, accessibility.trusted=true, screenRecording.granted=true, browser.online=true, tabCount=2, pendingCommands=0.
- **live relay and pendant presence** — Relay is configured/reachable and D1-backed; mac bridge is online, but the live device inventory contains no nRF pendant. Current live cross-surface export is truncated and cannot be treated as a complete archive.
  - evidence: GET /ops/status HTTP 200 payload relay.reachable=true, store=d1, macBridgeOnline=true; discover devices returned home-macbook-bridge and cloudflare-contract-test only. read_continuity_snapshot resolved and invoked GET /ops/snapshot with truncated=true.

## Capabilities it proposed

### ""What actually changed while I was away, and which parts are only assumptions?""
- **useful because:** The current continuity export is a truncated snapshot, while pipeline completion can mean only that the Mac acted and browser/relay records have different retention. A change-oriented witness would compare bounded watermarks across relay, Mac, browser, and pipeline, report concrete transitions, and label each gap as unknown instead of silently treating absence as zero.
- **path:** relay-realtime → mac-planner → browser-extension → unified → faculty-perception
- **model tier:** background for snapshot diffing; realtime only to narrate the already-computed result
- **latency:** Under 2 seconds for a normal bounded diff; no model call for collection or classification
- **cost:** Usually <$0.01, dominated by one cheap structured summarization call; collection is local HTTP and browser metadata
- **security:** Do not export page bodies or secrets; compare IDs, timestamps, statuses, hashes, and explicit retention bounds. Mark truncated/count-capped sources as unknown. Require confirmation before exposing sensitive browser titles.
- **missing:** A durable per-source high-water mark and tombstone cursor (the existing snapshot is truncated and not a diff); A relay endpoint that returns cursor-valid changes rather than only current state; A browser event cursor for tab/command transitions

### ""Is the pendant really connected and usable right now, or am I only looking at the Mac bench?""
- **useful because:** Today the relay registry can omit a pendant structurally, while source-level USB assumptions can be mistaken for a live wearable. This owner-facing answer would perform a bounded USB identity probe, read the firmware health frame, cross-check relay registration/heartbeat, and return one of bench-only, connected-not-registered, registered-but-stale, or end-to-end-ready with timestamps and evidence.
- **path:** mac-terminal → mac-planner → relay-realtime → faculty-perception → unified
- **model tier:** No LLM for probing; cheap text model only to explain the structured verdict
- **latency:** 3 seconds for serial probes and relay status; fail closed if either side is unavailable
- **cost:** Negligible API cost; local serial reads dominate
- **security:** Read-only, bounded allowlisted ports and byte counts; never transmit raw serial logs or firmware secrets. USB presence is not owner location and must be labelled bench-only.
- **missing:** The granted mac_usb_serial_diagnostics capability must be implemented as an actual bounded Mac action (it is not in the current route/action inventory); Firmware health frame transport for the currently absent nRF device and ESP32 bridge; A relay-side join key tying a firmware session/build ID to a registered device without using the admin key

### ""When you say there was nothing waiting for me, what did you actually check?""
- **useful because:** The system currently conflates an empty result with an unreadable or count-capped source. A negative-evidence receipt would list the exact stores, cursors, query limits, and freshness used, distinguish none-found from not-readable, and preserve a compact receipt the owner can inspect later. This is perception of absence, not another catch-up digest.
- **path:** faculty-perception → relay-realtime → mac-planner → browser-extension → unified
- **model tier:** Deterministic structured collection and comparison; use a cheap model only to phrase the receipt
- **latency:** Under 1 second from already-live snapshots; remote checks bounded to 3 seconds
- **cost:** Near-zero API cost; bounded metadata receipt under a few KB
- **security:** Receipt contains metadata only: no page bodies, message text, or secrets. Access must follow the source's existing scopes; disclose when a source was skipped or truncated.
- **missing:** Standard result semantics across continuity readers: found, none, unreadable, truncated, expired, and not-applicable; A compact durable receipt store with source cursors and query bounds; Relay/browser APIs must expose their applied limits and freshness in machine-readable form

### ""Before you use my browser or speak something aloud, show me exactly what data would leave this Mac, where it would go, and prove afterward what actually left.""
- **useful because:** Today browser reads can cross the Mac/relay/model boundary without a unified, owner-visible disclosure receipt. The Mac has redaction and evidence primitives, but relay browser reads have no stable ID or hash, and announcement storage can retain page-derived speech without source provenance. This capability gives the owner a real data-flow boundary rather than a generic privacy promise.
- **path:** browser-extension → mac-planner → relay-realtime → unified → faculty-perception → faculty-judgement
- **model tier:** Deterministic policy and hashing first; use the realtime model only to explain a blocked or permitted transfer in plain language
- **latency:** Preview under 300 ms for local browser data; remote transfer is blocked until the receipt is committed. Post-transfer verification under 1 second.
- **cost:** Near-zero model cost for normal cases; bounded metadata receipts under a few KB. Hashing and redaction are local CPU work.
- **security:** The preview must never contain the very secret it is protecting. Redaction must happen before preview persistence; sensitive destinations require explicit confirmation. Receipts need access control and must record hashes/field classes, not raw page text or audio.
- **missing:** A cross-surface data-flow receipt protocol with transfer ID, source, destination, classification, redaction result, content hash, and disposition; Relay browser reads must return a stable ID and hash and must attach that ID to any routine, speech, job, or announcement derived from the read; Mac and browser provenance stores must be mounted into the live routes and joined to relay receipts; A policy decision point that can pause relay/model transfer until owner confirmation for sensitive classifications

### ""If I tell you to forget something, prove where it went and remove or quarantine every copy you made.""
- **useful because:** There is no end-to-end revocation: browser evidence has tombstones, but relay announcements are never deleted, audio retention is not automatically swept, and Mac jobs/pipeline records have separate caps. The owner needs a propagation-aware erasure result, not a claim that one local memory row was deleted.
- **path:** relay-realtime → mac-planner → browser-extension → unified → faculty-perception → faculty-action
- **model tier:** Deterministic locator and deletion workflow; cheap model only to summarize the receipt, never to decide whether a secret should be erased
- **latency:** Preview under 1 second; execution and verification under 5 seconds where all surfaces are online, otherwise return an explicit pending/quarantined state
- **cost:** Near-zero model cost; storage and verification are bounded metadata scans
- **security:** Erasure requests are irreversible and require confirmation, strong owner authentication, and an immutable minimal audit receipt containing only hashes and destination classes. Offline nodes must not silently report success.
- **missing:** A content lineage ID connecting browser capsules, relay reads, spoken announcements, audio, jobs, memory facts, and pipeline records; Authenticated delete/quarantine endpoints on relay and Mac for every retained artifact, including announcement and audio stores; A durable erasure ledger with retry state and honest verification semantics; A policy for backups, model-provider retention, and already-heard audio that cannot be physically recalled

### ""Take that answer apart: what independent evidence supports it, what contradicts it, and what would change your mind?""
- **useful because:** Current context projection can elevate a machine-written, pinned preference above live machine truth, while completion and delivery states have different meanings. The owner cannot currently trigger an adversarial review of one claim across its independent sources. This capability would expose provenance conflicts before they become actions.
- **path:** faculty-perception → faculty-judgement → mac-planner → browser-extension → relay-realtime → unified
- **model tier:** Cheap structured contradiction pass over source records; reserve realtime reasoning for genuinely conflicting high-impact claims
- **latency:** Under 2 seconds for local claims; remote source checks bounded to 4 seconds
- **cost:** Usually <$0.01; dominated by structured source reads, not generation
- **security:** Do not reveal hidden memory or private browser content merely because a claim is challenged. Return source class, timestamp, hash, and access-controlled excerpts. A contradiction must lower confidence, not trigger autonomous deletion or action.
- **missing:** A claim identity and provenance graph shared by memory, browser evidence, relay jobs, pipeline stages, and device events; Independent-source quorum rules that distinguish corroboration from duplicated copies of the same assertion; A user-facing claim review route that records the challenge, revised confidence, and unresolved alternatives


## Changes it proposed to its own stack

### `context` — Add a perception freshness firewall: before judgement or action consumes a machine, browser, relay, or memory fact, attach an observedAt/source/cursor and classify it fresh, stale, contradicted, or structurally unavailable. Block high-impact actions when the required fact has no current witness; allow low-risk narration with an explicit uncertainty label.
- **owner gets:** It prevents the system from acting on a stale timezone preference, a browser tab that changed, a Mac job marked complete before playback, or a relay device row that disappeared because of caps. The owner gets fewer confident-but-wrong actions, not merely a nicer dashboard.
- effort: Medium: shared structured envelope plus adapters around perception and judgement; no new model training  ·  risk: Over-blocking when a source is temporarily offline. Recover with a user-visible reason, a bounded recheck, and an explicit confirm-to-proceed path; never downgrade unknown to false.
- cost: Near-zero API cost; one small structured validation pass. Storage is bounded cursor metadata, not page content.  ·  latency: Adds roughly 50-150 ms for local freshness checks; remote rechecks only when a high-impact action needs them.
- security: Improves least disclosure because validators can pass hashes/statuses instead of raw browser content; provenance metadata still needs access control.
- depends on: A durable source/cursor contract for the proposed away-diff witness; Mount browser provenance routes and return capsule/hash metadata for relay browser reads; Define a real pendant playback event and device-originated health identity


## What it asked for

_Nothing._
