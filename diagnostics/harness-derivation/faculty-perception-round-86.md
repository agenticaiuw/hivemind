# Harness derivation — faculty-perception — round 86

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live-fleet** — At 2026-08-07T13:36Z the Mac bridge and relay are reachable, but no pendant is registered; the only mobile device cloudflare-contract-test is offline. Browser extension home-chrome is offline with 9 pending commands.
  - evidence: discover(devices) live table; GET /ops/status and GET /browser/status at 2026-08-07T13:36Z
- **mac-ui-trust** — AI Pendant Agent is not operationally ready for UI automation: Accessibility and Screen Recording are both ungranted; /observe reports synthesized UI events will do nothing although receipts may report success. AppleScript automation grants are present.
  - evidence: GET /ops/status and GET /observe, observedAt 2026-08-07T13:36:15Z
- **pipeline-history-vs-live** — Pipeline history contains generated 24 kHz PCM marked 'waiting for the pendant' and an nRF9160 offline alert event, but current device table has no pendant. These are historical records, not evidence of current delivery or playback.
  - evidence: GET /pipeline events for pipeline job_309f... and job_276... plus live discover(devices)
- **browser-evidence-boundary** — Local GET /evidence is live and read-only, but explicitly reports that cloud-relay/serverBrowser.js read_web_page never reaches this process and mints no evidence capsule; local browser reads do have capsule IDs on receipts. GET /browser/inspections currently has zero inspections.
  - evidence: describe(GET /evidence) live response at 2026-08-07T13:36:37Z; describe(GET /browser/inspections) live response

## Capabilities it proposed

### "Before you act, tell me what parts of my setup are actually reachable and trustworthy right now—and if something reconnects later, reconcile what was queued or only recorded without silently repeating it."
- **useful because:** Today the system can have an offline browser extension, no pendant, or UI automation that returns a success-shaped receipt while doing nothing. The owner needs a truthful preflight and replay-safe handoff rather than confident action based on stale telemetry.
- **path:** relay-realtime → mac-planner → browser-extension → mac-terminal → faculty-perception → faculty-judgement → faculty-action
- **model tier:** background for periodic/device-state snapshots; cheap text model to summarize the map; realtime only when the owner asks by voice. No expensive model is needed to collect reachability facts.
- **latency:** Preflight under 500 ms from parallel health probes; reconnect reconciliation within one heartbeat; spoken summary under 10 seconds.
- **cost:** Usually <$0.01 per preflight (mostly existing local HTTP calls and a short summary); no vision or audio inference unless explicitly requested.
- **security:** Expose only coarse online/offline and trust state, never page contents or secrets. Pending browser commands must be held, deduplicated by command/idempotency key, and require confirmation before any irreversible replay. Historical pipeline records must be labeled historical.
- **missing:** A single typed, timestamped reachability/trust snapshot spanning relay, Mac bridge, browser extension, pendant registry, and UI permission state; A reconnect reconciler that can classify pending browser commands as safe-to-replay, expired, or requiring owner review; A hard action gate that rejects UI actions when /observe says inputReachability failed, instead of accepting misleading receipts

### "Tell me when the system's own story contradicts itself before I rely on it—for example, when a response says it is waiting for my pendant even though no pendant is connected, or when a browser action is queued while the extension is offline. Show me the conflicting claims, which one is live, and what I can safely trust."
- **useful because:** The owner cannot currently distinguish a live fact from a plausible historical status. Contradictory telemetry can make an unavailable device sound reachable or make an unexecuted browser action sound merely delayed. A contradiction alarm prevents false confidence without requiring the owner to inspect logs.
- **path:** faculty-perception → relay-realtime → mac-planner → browser-extension → unified → faculty-judgement
- **model tier:** Cheap background rules and a small text model for explanation; realtime is used only to speak an urgent contradiction to the owner. No vision or expensive reasoning is required.
- **latency:** Evaluate on every status/event update within 1 second; explain a detected contradiction in under 5 seconds when surfaced by voice.
- **cost:** Near-zero incremental inference for typed rules; <$0.01 only when a text explanation or spoken alert is requested. Storage is a small append-only claim index.
- **security:** Store claim metadata, timestamps, source, and hashes rather than private page/audio contents. Do not infer that an action happened from a receipt alone. Suppress alerts during known test/simulation runs, and require owner confirmation before any corrective replay or cancellation.
- **missing:** A cross-surface claim ledger that normalizes status statements from relay, device registry, pipeline, Mac, and browser into typed claims with freshness and source; Contradiction rules distinguishing historical pipeline records from current reachability and distinguishing accepted, executed, and delivered states; An owner-facing alert and review surface that presents both claims and a conservative trust verdict without taking action


## Changes it proposed to its own stack

### `relay` — Make relay-side read_web_page mint a signed, redacted evidence capsule with source URL/tab/session, retrieval time, content hash, sensitivity classification, TTL, and request/job ID; return the capsule ID alongside extracted text and forward a compact receipt to the Mac evidence store when the job crosses the bridge. Add an explicit 'unverifiable relay read' state when forwarding fails, rather than presenting the text as equally evidenced.
- **owner gets:** When private browser research is performed by the always-awake relay, the owner can currently receive text with no local provenance while Mac-side reads are auditable. This makes it possible to tell which account/page/time a claim came from and to revoke or expire it consistently.
- effort: Medium: relay D1 schema/API, redaction/hash implementation, bridge receipt ingestion, and dashboard rendering; no pendant hardware required.  ·  risk: Capsules may leak URL or sensitive metadata if redaction is incomplete; use allowlisted metadata, encrypted storage, short TTLs, and never store raw page text in the capsule. If relay-to-Mac forwarding fails, retain a clearly marked relay-only capsule and do not silently claim local verification.
- cost: Small D1 storage and one hash/redaction pass per read; roughly <$0.001 per read, dominated by existing browser/model work.  ·  latency: ~20–80 ms local hashing/redaction plus bridge write; text response need not wait for dashboard indexing, but must carry a provisional/unforwarded state.
- security: Improves auditability but expands provenance metadata across relay and Mac. Encrypt capsule fields, minimize URL/query retention, bind capsules to job IDs, and support owner revocation.
- depends on: Existing local /evidence capsule schema and revocation semantics; relay serverBrowser.js read_web_page route; Mac bridge ingestion endpoint for relay evidence receipts; Existing browser job/request IDs and session affinity

### `integration` — Introduce a monotonic delivery-state ledger shared by relay, Mac bridge, browser bridge, and device registry. Every job/event gets separate states for accepted, planned, executed, uploaded, device-acknowledged, and played; each transition carries source and timestamp, and impossible regressions or claims (such as 'waiting for pendant' without a registered pendant) are emitted as contradiction records for review instead of being flattened into one status string.
- **owner gets:** The owner gets an honest answer to 'did it happen?' rather than a misleading success or waiting label. Stale historical events cannot masquerade as current delivery, and the system can explain exactly what remains unconfirmed.
- effort: Medium-high integration work across relay D1, Mac pipeline/job records, browser command receipts, and dashboard/voice rendering; schema migration and replay tests are required.  ·  risk: Older records may not have enough information to classify; preserve them as unknown rather than inventing transitions. Clock skew and retries can create apparent regressions, so use server sequence numbers and idempotency keys. Never auto-replay an ambiguous action.
- cost: Small D1/local JSON overhead and rule evaluation; no per-event model call. A one-time migration and modest storage growth dominate.  ·  latency: Sub-100 ms ledger write on local events; relay acknowledgment may add one network round trip only when a durable cross-surface transition is required.
- security: Keep payloads out of the ledger; store opaque job IDs, hashes, source classes, and timestamps. Access must follow existing bearer/session authorization, with sensitive browser evidence referenced by capsule ID only.
- depends on: Relay and Mac job IDs with idempotency keys; Device registry reachability timestamps; Browser command receipts and local evidence capsule IDs; Dashboard/voice renderer capable of showing unconfirmed and contradictory states


## What it asked for

### `c8-gmhq` (context) — relay browser-read provenance
- why: Live /evidence says relay serverBrowser.js read_web_page mints no local capsule, which is a concrete cross-surface trust gap. I need to know whether relay already has any signed request/job IDs or retention policy before treating this as a new missing bridge.
- would change: If relay already emits verifiable IDs, I will record the existing contract and avoid proposing duplicate schema work; if not, I will keep the relay capsule bridge as an explicit missing dependency for judgement/action.

## Its own summary

Fresh live truth established: Mac bridge and relay are reachable, but no pendant is registered; Chrome extension is offline with 9 pending commands. Mac UI automation is not trustworthy (/observe inputReachability=failed; Accessibility and Screen Recording are false), despite AppleScript grants. Pipeline 'waiting for pendant' entries are historical, not live delivery evidence. Local browser evidence capsules exclude relay-side read_web_page, and browser inspections are empty. I recorded these facts, alerted faculty-judgement, proposed a relay evidence-capsule bridge, and proposed reachability-aware action gating (noting it is close to existing backlog).

**Biggest unknown:** Whether relay-side read_web_page already has an internal signed request/job identity and retention policy; I queued context request c8-gmhq. Operationally, the remaining blockers are owner-granted Accessibility/Screen Recording, a real pendant registration, and browser extension reconnection—not discoverable from this process.

