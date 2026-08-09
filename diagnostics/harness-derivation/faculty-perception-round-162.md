# Harness derivation — faculty-perception — round 162

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac observability and permissions** — At 2026-08-08T02:47Z, /ops/snapshot reports AI Pendant Agent v0.5.0, full-control and computer-use loop enabled, Accessibility and Screen Recording granted, requiredMissing empty and permissions.ready=true. /observe independently reports inputReachability.status=verified and uiActionsWillReachTheScreen=true.
  - evidence: GET /ops/snapshot and GET /observe both returned HTTP 200; /observe checkedAt 2026-08-08T02:39:26.656Z.
- **live browser and pendant state** — At 2026-08-08T02:47Z, Safari browser bridge is online with 9 tabs, foreground tab https://x.com, zero pending commands and zero spool; the relay device inventory has no pendant, only home-macbook-bridge online and cloudflare-contract-test offline. Therefore browser availability is fresh, but pendant presence/hearing remains unknown and cannot be inferred from historical pipeline audio.
  - evidence: discover(devices) returned Safari on MacIntel online, home-macbook-bridge online, cloudflare-contract-test offline; GET /ops/snapshot and GET /browser/status show browser online, tabCount 9, pendingCommands 0; prior authoritative registry context says no nRF pendant registered.

## Capabilities it proposed

### "“Before I rely on that, reality-check it across everything you can see and tell me exactly what is observed, what is inferred, and what remains unknown.”"
- **useful because:** This would be the system’s most trustworthy answer mode: it would refuse to turn a Mac-side completion, a browser tab, or relay acceptance into a fact about the owner’s world. It would correlate independent surfaces, expose contradictions (for example browser online while a relay job is stale), attach freshness and provenance, and give the owner a short verdict plus drill-down evidence.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → unified → faculty-perception
- **model tier:** Use a cheap structured extraction/judgement model for per-source normalization and contradiction detection; reserve realtime for the owner-facing spoken summary only. No expensive model call is needed when the source facts agree.
- **latency:** 1–3 seconds for live checks; return partial results at 3 seconds with explicit unknowns, then refresh asynchronously if a source is slow.
- **cost:** Usually <$0.01 per check; dominant cost is model judgement over normalized records, not the GETs. Cache unchanged source snapshots by observedAt/content hash.
- **security:** The response may contain private browser URLs, tab titles, filesystem paths, and app state. Keep raw evidence local, send only redacted summaries/hashes to relay, require confirmation before exposing secrets or using an observation to authorize an action, and never call an action route from this capability.
- **missing:** A single authenticated cross-surface observation contract with source, observedAt, freshness deadline, confidence, and unknown reason; A relay-side correlation ID/content hash for relay browser reads; A real pendant-originated playback/health event when a pendant exists; today the registry shows no pendant and completed jobs do not prove hearing; A mounted Mac browser-provenance route so capsule links can be returned consistently

### "“Is my pendant physically connected, electrically healthy, and capable of carrying a conversation right now—not merely registered in the cloud?”"
- **useful because:** The current live registry can truthfully say only that no nRF pendant is registered; it cannot distinguish unplugged USB, bootloader mode, a serial device that is alive but unregistered, or a dead audio bridge. A one-command tether test would prevent hours of believing historical pipeline audio is live device telemetry.
- **path:** mac-planner → mac-terminal → pendant → relay-realtime → faculty-perception → faculty-action
- **model tier:** Deterministic serial/protocol probes and relay GETs first; a cheap model only translates the structured results into plain speech. Do not use realtime for the diagnostic itself.
- **latency:** Under 10 seconds: enumerate the two known USB serial paths, issue non-destructive version/health queries, run a short audio loopback checksum, and compare with relay heartbeat freshness.
- **cost:** Near-zero API cost; local serial reads and a few relay requests dominate. A future 5–10 second loopback consumes negligible cloud inference.
- **security:** Serial probing must be read-only and constrained to the known device paths; never flash, reset, or write SD. Audio loopback should use synthetic tones or a locally generated phrase, not upload owner speech. Surface the fact that the cloud registry has a 90-second online threshold and that no pendant row exists today.
- **missing:** A read-only Mac route that enumerates /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA and captures bounded serial replies; A firmware diagnostic command with build ID, boot/session ID, monotonic clock, codec mode, packet counters, and ESP32 bridge state; A deterministic local audio loopback/CRC test with an explicit pass/fail/unknown result; A device registration/heartbeat path that does not require the pendant to send the relay admin key

### "“Keep a live truth lease on anything you tell me—warn me when the browser, Mac, relay, or pendant evidence is stale or contradictory before you let me act on it.”"
- **useful because:** Most dangerous errors here are temporally plausible: a Safari tab was online seconds ago, a Mac job completed while playback was still in flight, or a relay device row is stale. A truth lease would make freshness a first-class property, automatically downgrade expired observations to unknown, and prevent yesterday’s evidence from silently authorizing today’s action.
- **path:** relay-realtime → mac-planner → mac-vision → browser-extension → pendant → faculty-perception → faculty-judgement → faculty-action
- **model tier:** No model for lease evaluation: deterministic source-specific TTLs, monotonic timestamps, and contradiction rules. Use a small model only to summarize the resulting state in speech.
- **latency:** Continuous low-rate checks (15–60 seconds depending on source); zero added latency when a lease is valid. On a lease miss, one bounded refresh attempt, then immediate unknown.
- **cost:** <$0.001 per refresh when local; relay requests and optional spoken warning dominate. Hash-based unchanged snapshots avoid model and storage cost.
- **security:** A lease is a safety gate, not permission to act. Never infer presence or owner hearing from freshness alone. Keep source-specific TTLs visible (browser heartbeat, Mac job receipt, relay 90-second online threshold, device playback acknowledgment), redact private tab content, and require explicit confirmation after a lease expires.
- **missing:** A shared observation envelope with observedAt, expiresAt, source clock, monotonic sequence, and reason-for-unknown; A judgement/action contract that refuses stale evidence instead of merely displaying it; A source-specific clock-skew policy and contradiction precedence rules; A pendant playback event and relay reader so a fresh socket write cannot be mislabeled as fresh hearing

### "“What changed in my digital life since the last time you looked—across my browser, Mac, relay, and pendant—and show me only changes you can prove?”"
- **useful because:** Today the system can inspect many surfaces but cannot produce a trustworthy, cross-surface before/after diff. This would turn observations into a personal change ledger: newly arrived messages or calendar changes, altered browser state, changed files/jobs, relay events, and device health transitions, each with an exact prior snapshot, current snapshot, timestamp, and confidence. It would catch silent changes without pretending that a current view explains history.
- **path:** browser-extension → mac-planner → mac-vision → relay-realtime → pendant → faculty-perception → unified
- **model tier:** Deterministic canonicalization, hashes, and structural diffs first; a cheap text model clusters and summarizes only the changed fields. Realtime is unnecessary except for a spoken summary.
- **latency:** A snapshot should return in under 2 seconds from local caches; first observation or a full browser/Mac sweep may take 10–30 seconds and should yield incremental progress.
- **cost:** Typically <$0.01 per sweep; storage and local hashing dominate. Model cost is limited to summarizing material diffs.
- **security:** Snapshots could retain private page titles, filenames, messages, and account metadata. Store bodies locally with field-level redaction, hash sensitive values, encrypt the change ledger, apply per-source retention, and require confirmation before sharing a diff or acting on it.
- **missing:** A durable versioned observation store with per-field redaction and content hashes; Canonical serializers for browser tabs, Mac jobs/files/calendar, relay state, and pendant health; A cross-surface diff API that distinguishes added, removed, changed, and unobserved; A first-baseline flow that tells the owner exactly what was not observed before the comparison

### "“When two parts of you disagree, give me the smallest incident packet that lets me understand and resolve the disagreement without rereading the whole system.”"
- **useful because:** A browser can be online while a command is stale; a Mac job can be complete while playback is unknown; a relay can report acceptance while the device is absent. Today these contradictions are scattered across logs and silently collapsed into one status. This capability would preserve both claims, align their clocks, identify the exact conflicting fields, and tell the owner whether the disagreement is resolvable, awaiting a device, or a genuine failure.
- **path:** faculty-perception → faculty-judgement → faculty-action → mac-planner → browser-extension → relay-realtime → pendant
- **model tier:** Use deterministic schema validation and clock alignment for the packet; a small reasoning model can classify the conflict and draft the owner-facing explanation. Realtime is only for urgent spoken escalation.
- **latency:** Under 1 second when the conflicting receipts already exist; under 5 seconds if one bounded refresh is safe. Never block an unrelated action indefinitely waiting for a missing surface.
- **cost:** <$0.005 per incident; most work is local record assembly. Model cost is only for novel conflict classification.
- **security:** Incident packets may expose private URLs, filenames, or action parameters. Redact values by sensitivity class, retain hashes and locators where possible, restrict packets to the owner, and make 'unresolved' a safe terminal state rather than guessing which subsystem is right.
- **missing:** A durable contradiction record keyed by operationId/attemptId and source event IDs; Clock-skew and freshness normalization across Mac, relay, browser, and pendant monotonic clocks; A standard conflict taxonomy separating stale, missing, contradicted, and failed; A user-facing packet viewer with source links and redacted evidence excerpts

### "“What did you actually know at 3pm yesterday, before anything was changed or cleaned up—reconstruct the answer from the evidence that existed then.”"
- **useful because:** Today records are count- or byte-capped, relay jobs expire, announcements are inconsistently retained, and current status overwrites the past. The owner cannot reliably distinguish what the system knew at a moment from what it learned later. An append-only, redacted observation timeline with explicit capture times would make retrospective answers honest: it could say 'known then,' 'learned later,' or 'not observed,' rather than projecting today’s truth backward.
- **path:** faculty-perception → relay-realtime → mac-planner → browser-extension → pendant → unified
- **model tier:** Use deterministic timestamped event storage and as-of queries; a cheap model summarizes the selected interval only after the evidence set is fixed. Realtime is not needed for historical reconstruction.
- **latency:** Under 2 seconds for a bounded day; under 10 seconds for a multi-week interval. If retention is incomplete, return the gap immediately rather than inventing continuity.
- **cost:** <$0.01 per query; storage and redaction are the main costs. Keep only compact metadata/hashes by default and fetch bodies on demand.
- **security:** A historical ledger could become a sensitive behavioral record. Encrypt it locally, separate content from metadata, redact secrets before persistence, expose retention/deletion controls, and show exactly which sources were missing or pruned. Never claim that absence from the ledger means absence in the world.
- **missing:** A durable append-only observation ledger with source clocks, capture clocks, retention and deletion semantics; As-of query semantics that never use a later observation to answer an earlier question; Cross-surface event IDs and causal links for Mac, browser, relay, and pendant records; A retention policy the owner can choose, with visible coverage gaps and cryptographic integrity checks


## What it asked for

_Nothing._
## Its own summary

Established fresh truth: the Mac agent is v0.5.0 with Accessibility, Screen Recording, and input reachability verified; Safari bridge is online with 9 tabs and zero pending/spooled commands; no nRF pendant is present in the live device inventory, so historical audio telemetry is not live pendant evidence. Proposed three capabilities: cross-surface reality-check with explicit observed/inferred/unknown verdicts; a read-only USB tether and audio-health bring-up test; and freshness leases that downgrade stale evidence to unknown before action. The second proposal was recorded with a similarity warning, so it should be treated as a near-duplicate of existing pendant-connectivity work, not repeated.

**Biggest unknown:** The granted read_continuity_snapshot tool still cannot resolve at runtime (nearest routes /ops/snapshot and /pipeline), so there is no single authenticated cross-surface continuity read. Also the two physical serial devices cannot yet be probed by an available tool, and no pendant-originated playback event exists.

