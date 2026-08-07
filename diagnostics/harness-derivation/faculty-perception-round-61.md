# Harness derivation — faculty-perception — round 61

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac agent input reachability** — At 2026-08-07T12:18:41.978Z, /observe reports AI Pendant Agent foreground-input reachability failed: Accessibility trusted=false, Screen Recording=false, eventsPost=false, and uiActionsWillReachTheScreen=false. AppleScript automation grants are present, but UI click/type/key receipts cannot be trusted.
  - evidence: GET /observe HTTP 200; accessibility and inputReachability fields
- **Pendant audio pipeline** — The live Mac pipeline has rendered response speech as 24,000 Hz mono PCM s16le successfully (example run: 75,734 PCM bytes, 1,578 ms, 0 clipped samples), while a separate nRF9160 live input telemetry event reports 15,625 Hz mono PCM. Thus output path is verified at 24 kHz, but input capture is not 24 kHz.
  - evidence: GET /pipeline HTTP 200; completed TTS event metadata and nRF9160 inputTelemetry metadata
- **Cross-surface availability** — At 2026-08-07T12:18:42Z, Mac bridge and relay are reachable, but Chrome browser extension home-chrome is offline with 5 pending commands; browser status reports no active tab/window connection. Computer-use loop is disabled and vision upload consent is false.
  - evidence: GET /ops/status and GET /browser/status HTTP 200
- **Timezone disagreement** — The live Mac machine-context reports timezone America/New_York, while the owner memory projection states America/Chicago. No authoritative resolution is available in this round; scheduled times must not be interpreted from the machine timezone alone.
  - evidence: GET /machine-context HTTP 200 reports America/New_York; discover:owner remembered text reports timezone America/Chicago

## Capabilities it proposed

### "Tell me what parts of my AI setup are actually reachable right now, what evidence is fresh, and what cannot be trusted."
- **useful because:** The current system can report apparent success even when UI input is discarded, and queued browser work can sit while the extension is offline. A concise, evidence-backed reachability brief prevents the owner from believing a false completion and exposes stale or conflicting device facts (including the verified 24 kHz output versus 15.625 kHz input).
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** background for periodic snapshots; realtime only when the owner asks during a live conversation
- **latency:** Under 2 seconds for cached status; up to 5 seconds for a fresh cross-surface probe. No expensive vision or LLM call unless interpreting an actual conflict.
- **cost:** Near-zero when assembled from existing status endpoints; occasional small text-model cost only to compress conflicting evidence into one spoken sentence.
- **security:** Read-only status must redact tokens, account content, and secret captures. Browser availability should expose online/offline and queue age, not tab contents. Never infer that an action happened from a receipt when /observe says UI reachability is false.
- **missing:** A typed perception snapshot contract combining relay, pendant telemetry, Mac /observe and /ops/status, and browser status with timestamps and confidence; Staleness thresholds and explicit conflict labels (for example, Mac machine timezone versus owner timezone); A pendant-readable alert when a queued browser job cannot run or when an action receipt is non-trustworthy

### "When something in my AI setup breaks, tell me exactly what changed since the last known-good state, which link failed first, and whether any queued request was affected."
- **useful because:** Today the owner can see isolated status pages, but cannot reconstruct the failure boundary across pendant, relay, Mac bridge, and browser. A causal incident timeline would distinguish a dead device from a delayed queue and prevent false claims that work was completed.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** background/event-driven state-diff worker; use realtime only to speak the already-computed incident summary when the owner asks
- **latency:** Record state transitions immediately; produce a first causal timeline within 3 seconds of reconnect or failure, with no polling conversation loop.
- **cost:** Negligible when based on structured transition events and hashes; a small text-model call only when compressing a multi-link incident into spoken language.
- **security:** Store only redacted endpoint states, request IDs, tab/session hashes, timestamps, and queue effects—not page contents or audio. Incident history needs bounded retention and owner-controlled deletion. Never claim root cause when only correlation is known; label hypotheses separately from observed transitions.
- **missing:** A durable cross-surface transition log with monotonic sequence numbers and synchronized wall-clock estimates; A last-known-good checkpoint per pendant/relay/Mac/browser link, including queue watermark and pipeline state; A causal correlator that joins request IDs across relay jobs, Mac jobs, browser commands, and pendant delivery acknowledgements; A user-facing incident view and pendant-safe short alert format


## Changes it proposed to its own stack

### `browser-harness` — Add an uncertainty quarantine for browser commands that remain queued while the extension is offline: attach enqueue time, tab/session identity, and a precondition snapshot; on reconnect, revalidate the target tab and page before execution, expire commands whose session cannot be reattached, and surface them as 'not run' rather than replaying blindly. Keep this separate from the durable runner itself.
- **owner gets:** The owner will no longer get a delayed action performed against the wrong tab or an old page after the browser has been disconnected. They get a clear explanation of what did not run and why.
- effort: Moderate: extend browserBridge queue records and reconnect handshake, add precondition checks and dashboard/pendant status rendering, plus tests for offline/reconnect races.  ·  risk: A legitimate queued command may expire and require re-asking; recovery is explicit retry after the owner reviews the target and page fingerprint. No command should be silently dropped.
- cost: Negligible API cost; small local persistence and reconnect metadata only.  ·  latency: Adds one lightweight validation round trip before replay, typically under 500 ms; avoids expensive planner retries.
- security: Improves safety by preventing stale authenticated-tab actions. Store hashes/metadata rather than page contents, and never expose tab URLs to the pendant unless requested.
- depends on: Existing browser request IDs, tab/session affinity, and typed results (chg-14accc01); Browser extension heartbeat/status routes; A reconnect event or periodic heartbeat from home-chrome


## What it asked for

_Nothing._
## Its own summary

Fresh live perception is now recorded: Mac UI input is not reachable or trustworthy (Accessibility and Screen Recording false), browser extension is offline with 5 pending commands, relay/Mac bridge are online, and output speech has verified 24 kHz PCM while a live nRF input event is 15.625 kHz. I also recorded the unresolved machine-timezone disagreement (New York in machine context versus Chicago in owner memory). I proposed a new stale-browser-command quarantine that validates tab/session/page state before replay. I still need authoritative pendant input-path telemetry and timezone semantics; the owner must manually grant the exact AI Pendant Agent binary Accessibility/Screen Recording before UI reachability can become true.

**Biggest unknown:** Whether the 15.625 kHz nRF input is an intentional transport rate that is resampled later or a remaining defect in the requested 24 kHz end-to-end path; current routes expose the event but not the authoritative firmware configuration.

