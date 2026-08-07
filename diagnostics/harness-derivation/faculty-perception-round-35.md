# Harness derivation — faculty-perception — round 35

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-input-reachability** — At 2026-08-07T10:48:50Z, /observe reports Accessibility trusted=false for the running AI Pendant Agent (com.aipendant.agent), synthesized input rejected, inputReachability failed, and ui_actions will not reach the screen. Screen Recording is also false.
  - evidence: GET /observe HTTP 200 response: accessibility.trusted=false; eventsPost=false; inputReachability.status=failed; screenRecording=false.
- **browser-reachability** — At 2026-08-07T10:48:50Z, browser extension home-chrome is offline with 3 pending commands; three durable browser sessions exist, but no live tab connection is available.
  - evidence: GET /ops/status and GET /observe HTTP 200: browserExtension.online=false, pendingCommands=3; browser tabs list has sessions but extension offline.
- **mac-agent-perception** — Mac agent is online and fullControlMode/planner enabled, but computer-use loop is disabled and vision upload consent is false; agent readiness is false due to missing Accessibility/Screen Recording.
  - evidence: GET /ops/status HTTP 200: fullControlMode=true, computerUse.loopEnabled=false, visionUploadConsented=false, permissions.ready=false.
- **machine-timezone** — Machine context reports authoritative Mac timezone America/New_York.
  - evidence: GET /machine-context HTTP 200 response includes machine.timezone="America/New_York".

## Capabilities it proposed

### "“Before you try anything, tell me honestly what you can currently reach—and what will happen if I ask you to do it now.”"
- **useful because:** The owner currently gets misleading success receipts when Mac Accessibility or the browser extension is unavailable. A perception-first reachability brief would combine live pendant/relay telemetry, Mac permissions and foreground app, browser session liveness, and queued-vs-executable state, distinguishing observed facts from stale cached grants. It lets the owner choose a fallback (spoken answer, queued job, or wait) instead of believing an action happened.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard-ux
- **model tier:** background and scheduled checks use a cheap model; only render the short spoken explanation with realtime when the owner asks live
- **latency:** Under 1 second when the relay and Mac bridge are online; 2–5 seconds if a fresh Mac/browser probe is needed. Never block an unrelated conversation on a failed probe.
- **cost:** Usually <$0.001 per check if rule-based typed facts; occasional short-model wording dominates, roughly $0.001–$0.01. No vision upload unless explicitly requested.
- **security:** Expose only capability state and coarse app/session metadata, not page contents or secrets. Browser URLs/titles and foreground app are sensitive; require a dashboard privacy toggle and redact domains by default. Never claim reachability from a cached permission grant; attach observedAt and TTL to every fact.
- **missing:** A unified typed reachability snapshot schema with source, observedAt, freshness TTL, confidence, and failure reason; Pendant-side connectivity/pipeline telemetry exposed as a read-only fact source; A relay endpoint that merges pendant, Mac, and browser probes without granting action authority; Action planner integration that consumes the snapshot and refuses to emit success receipts for blocked UI paths; Dashboard and spoken formatter showing observed, stale, queued, and executable states separately

### "“I was offline for a while—what happened during that gap, what did you miss, and what is safe to resume?”"
- **useful because:** Today a dropped LTE link, sleeping Mac, or disconnected browser can leave the owner unsure whether a request was heard, queued, partially completed, or lost. On reconnection, the pendant should deliver one causally ordered outage reconciliation: locally buffered conversation markers/transcripts, relay job state transitions, Mac receipts, browser queue results, and external changes observed after reconnection. It should clearly separate confirmed events from unknown intervals and offer resumable checkpoints without repeating or silently executing work.
- **path:** pendant → relay → mac-planner → mac-terminal → browser-extension → dashboard-ux
- **model tier:** Use deterministic event stitching and a cheap background model for clustering/deduplication; use realtime only to speak the short summary when the owner asks or the link returns.
- **latency:** Generate a compact first summary within 3 seconds of reconnection, then refine in the background within 30 seconds. Local pendant buffering must continue offline with no network dependency.
- **cost:** Typically <$0.005 per outage using event stitching and a small summarizer; storage and reconciliation dominate, not model tokens. No screenshot or page content is uploaded unless already authorized by the originating task.
- **security:** Offline audio/transcripts and private browser metadata are sensitive. Encrypt local SD records and relay storage, minimize to event hashes/short excerpts by default, enforce per-source retention, and require confirmation before resuming any action. Treat missing sequence ranges as unknown, never infer success from an absent failure.
- **missing:** A pendant-local outage journal with monotonic sequence numbers, encrypted-at-rest records, bounded storage, and explicit upload acknowledgements; Relay event-sourcing for pipeline, job, and connection transitions with causal IDs and a durable gap protocol; Mac and browser adapters that report queued, started, completed, failed, and unknown states using the same task ID; A reconciliation engine that detects duplicate/replayed events and exposes resumable checkpoints without taking action; An owner-facing spoken/dashboard view for confirmed, pending, failed, and unknowable events


## Changes it proposed to its own stack

### `context` — Implement an append-only Perception Snapshot Ledger across relay and Mac agent. Every probe writes a compact typed record (surface, capability, state observed, source, observedAt, TTL, confidence, failure reason, correlationId); snapshots are merged by timestamp without allowing cached state to overwrite a newer failure. The planner and receipts must reference the snapshot correlationId and render 'observed', 'stale', 'queued', or 'executed' explicitly. Retain only state transitions and hashes of sensitive URLs/app names, with configurable short retention.
- **owner gets:** When the pendant says something was done, the owner can see whether it was actually executable at that moment and why a fallback or queue was chosen. Failures stop being mysterious, and a later repair can resume only work that was truly queued rather than work that merely reported success.
- effort: Medium: shared schema and merge rules in relay/Mac agent, adapters for browser and pendant telemetry, receipt/planner wiring, migration tests for stale-success races, and a small dashboard timeline.  ·  risk: Clock skew or partial writes could misorder events; use server receive time plus source time and monotonic sequence per source. Sensitive metadata could leak through logs; hash/redact URLs and enforce retention. During rollout, old receipts remain untyped and must be labeled legacy rather than upgraded.
- cost: Negligible storage (state transitions only, likely KB/day per owner) and <$0.001 per snapshot in D1/relay overhead; no model call required.  ·  latency: 5–30 ms for local merge; at most one extra relay round trip when a fresh probe is requested. Normal speech path remains non-blocking.
- security: Improves auditability but creates a new metadata store; encrypt or hash sensitive fields, scope reads to the owner, and provide deletion/export controls.
- depends on: A typed reachability/perception schema; Reliable pendant pipeline telemetry and continuity acknowledgements; A fresh Mac permission/input probe that distinguishes actual grant from cached automation grants; Browser heartbeat/session liveness with observed timestamps

### `firmware` — Add an offline-first event journal to the nRF9160 pendant firmware: assign each button, capture, playback, link, and acknowledgement event a monotonic boot-persistent sequence number; write compact encrypted records to a wear-leveled append log on the existing microSD, retain a small protected high-water mark in internal flash, and upload only acknowledged ranges to the relay with resumable chunk checksums. Emit explicit gap/overflow records rather than silently dropping old events.
- **owner gets:** The owner can recover an honest account of what happened when LTE or the Mac disappeared instead of wondering whether the pendant heard them or whether a request vanished. It also makes reconnect summaries and safe resume possible without pretending that an unobserved interval succeeded.
- effort: Medium-high: firmware journal format, SD power-loss recovery, flash wear management, encryption/key provisioning, upload protocol, and integration tests that cut power or radio during every write/ack boundary.  ·  risk: SD removal, corruption, or battery loss can truncate history; use double-written commit markers, checksums, bounded retention, and an explicit 'unknown after sequence N' marker. Audio could consume storage quickly, so default to event metadata and short encrypted transcript fragments, not raw audio. Firmware bugs could increase flash wear; rate-limit high-frequency telemetry.
- cost: Uses existing SD hardware; firmware RAM target under 8 KB for buffers and state, with negligible LTE overhead beyond journal chunks. Optional secure-element-backed key storage would add roughly $1–$3 BOM and a few mA only during crypto operations.  ·  latency: A few milliseconds per journal append, preferably asynchronous; reconnect upload runs after the live audio path and should not delay button response.
- security: Adds encrypted local sensitive data and key-management responsibility. Derive per-device keys from secure provisioning, never log plaintext transcripts, authenticate journal chunks, and provide owner-triggered erase plus retention limits.
- depends on: A relay gap/replay protocol with durable sequence acknowledgements; Shared causal task IDs across pendant, relay, Mac, and browser; Continuity-event retention and acknowledgement semantics; A recovery-aware dashboard/spoken reconciliation view


## What it asked for

_Nothing._
## Its own summary

Established and recorded fresh cross-surface facts: Mac UI input is genuinely unreachable (Accessibility false for the running AI Pendant Agent; probe failed), Screen Recording is false, browser extension is offline with 3 pending commands, computer-use loop is disabled with no vision consent, relay/Mac bridge are online, and timezone is America/New_York. Proposed a new owner-facing reachability brief and an append-only perception snapshot ledger so planners and receipts cannot confuse cached permissions or queued work with execution. Shared the blockers with judgement, action, and realtime agents.

**Biggest unknown:** The orchestrator’s claimed permission/tool grants have not taken effect in the live Mac agent: /ops/status still says ready=false, and the requested pendant diagnostics/continuity tools remain unavailable. I still need an effective probe of live pendant telemetry and continuity acknowledgement semantics, plus Accessibility and Screen Recording granted to the exact running com.aipendant.agent binary.

