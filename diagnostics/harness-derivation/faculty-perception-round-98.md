# Harness derivation — faculty-perception — round 98

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser liveness** — At 2026-08-07T14:23Z, /browser/status reports home-chrome offline with no tab/window metadata and 10 pending commands; /ops/status agrees browser.online=false.
  - evidence: GET /browser/status HTTP 200 and GET /ops/status HTTP 200 in Round 98.
- **Mac control readiness** — At 2026-08-07T14:23Z, the Mac bridge is online and relay reachable, but /ops/status reports Accessibility trusted=false, Screen Recording granted=false, and permissions.ready=false; AppleScript automation grants are cached and requiredMissing is empty.
  - evidence: GET /ops/status HTTP 200 in Round 98.
- **timezone inconsistency** — The live machine context reports timezone America/New_York, while the owner's remembered preference says America/Chicago. Time-sensitive scheduling or interpretation cannot safely choose between them without an authoritative resolution.
  - evidence: GET /machine-context HTTP 200 reports machine.timezone America/New_York; discover(owner) remembered.text says timezone America/Chicago.
- **UI input reachability** — At 2026-08-07T14:24Z, /observe reports inputReachability.status=failed and uiActionsWillReachTheScreen=false; synthesized UI events from com.aipendant.agent are not accepted, so click/type receipts cannot be trusted. Foreground app is Claude.
  - evidence: GET /observe HTTP 200: accessibility.trusted=false, eventsPost=false, inputReachability.failed.
- **browser session distinction** — The browser extension is offline with 10 pending commands, but the local agent still has 3 persisted browser sessions (default time.is/UTC last used 06:26Z; two selenium/httpbin probes). These sessions are not evidence of an owner-live browser connection or current page state.
  - evidence: GET /browser/status, GET /observe, and GET /browser/sessions HTTP 200 at Round 98.
- **briefing freshness and grants** — Latest workday briefing was generated 2026-08-07T11:30Z and says calendar and mail were not read due to Automation grants, despite /ops/status reporting cached Calendar and Mail grants; the briefing is stale/internally inconsistent and must not be presented as a fresh mail/calendar read.
  - evidence: GET /briefing/latest HTTP 200 and GET /ops/status HTTP 200 in Round 98.

## Capabilities it proposed

### "“Is that information current, and did you actually reach the device or browser?”"
- **useful because:** Today the system can confuse persisted probe tabs with a live browser, stale briefings with fresh mail/calendar reads, and historical pendant pipeline events with current delivery. This gives the owner a direct, evidence-backed freshness and delivery answer before they rely on it.
- **path:** relay-realtime → faculty-perception → faculty-judgement → mac-planner → browser-extension → mac-vision → mac-terminal
- **model tier:** Use the cheap background/local tier to collect and normalize status; reserve realtime for the owner's short spoken question and final one-sentence answer. No expensive model is needed to compare timestamps and liveness flags.
- **latency:** Under 500 ms from cached local observations; if a live heartbeat or browser poll is needed, say 'checking' and complete within 3 seconds, otherwise report unavailable rather than waiting indefinitely.
- **cost:** Near-zero model cost for the normal path (local JSON/status comparison); at most a few hundred context tokens. A remote check only costs the existing relay request.
- **security:** Return metadata, source, age, and delivery state without page contents, URLs containing secrets, or account data. Never treat a successful synthetic UI receipt as proof when /observe says inputReachability failed. Require confirmation only if the owner then asks to retry a world-changing action.
- **missing:** A shared freshness vocabulary and TTL policy for live extension, persisted sessions, briefings, pipeline events, and device heartbeats; A delivery receipt that distinguishes relay accepted, device acknowledged, and audio played; An authoritative timezone source to resolve America/New_York versus remembered America/Chicago

### "“When something went wrong, show me the exact chain of evidence the hive had at that moment, what it inferred, and where the truth diverged.”"
- **useful because:** The owner cannot currently audit a false 'delivered to the pendant' or stale calendar/browser claim after the fact. Existing logs are per-surface and mix historical pipeline events, cached permissions, persisted tabs, and live status; they do not reconstruct one time-ordered, cross-device account of what the system knew or why it trusted it. This would turn silent hallucinated completion into an explainable incident the owner can correct.
- **path:** relay-realtime → faculty-perception → faculty-judgement → faculty-action → mac-planner → mac-terminal → browser-extension
- **model tier:** Use deterministic local event normalization and rule evaluation for the evidence chain; use a cheaper background model only to summarize an incident. Realtime is needed only when the owner asks verbally for the explanation.
- **latency:** Normal operation adds no perceptible latency because events are appended asynchronously. An incident reconstruction should return a compact timeline within 2 seconds from local records, or explicitly mark missing intervals.
- **cost:** Small local append-only records (roughly 1–5 KB per job plus bounded retention); near-zero model cost for collection and comparison, with a few cents at most for an optional natural-language summary.
- **security:** Store hashes and minimal metadata by default, not page bodies, audio, secrets, or message content. Encrypt sensitive evidence, apply per-field TTLs, redact account identifiers, and require owner confirmation before exporting an incident bundle off-device. The ledger must be append-only for audit integrity and must distinguish an absent observation from a negative observation.
- **missing:** A shared cross-surface event schema with monotonic sequence, wall-clock timestamp, source, freshness, observation/inference distinction, and confidence; Immutable correlation IDs linking voice request, relay job, Mac job, browser command, pipeline event, device heartbeat, and final acknowledgment; A rule-evaluation record that explains why stale or contradictory evidence was accepted, rejected, or downgraded; A bounded local incident-replay store and a read-only owner-facing timeline endpoint


## Changes it proposed to its own stack

### `context` — Add a perception truth ledger and freshness gate before any agent emits a device-, browser-, or time-sensitive claim. On each request, collect compact snapshots from /ops/status, /browser/status, /machine-context, and the latest /pipeline event; label each observation live/stale/absent with observedAt and source, detect contradictions (especially remembered timezone versus machine timezone), and prevent historical pipeline events from being presented as current pendant delivery. Expose the reconciled snapshot to judgement/action and require an explicit uncertainty sentence or fallback when the required surface is offline.
- **owner gets:** The owner will stop hearing confident but false statements such as an answer being 'waiting for the pendant' when no pendant is connected, or reminders being scheduled in the wrong timezone. They get a short honest status and a useful fallback (Mac playback, queued result, or review later) instead.
- effort: Medium: typed snapshot schema, freshness windows, contradiction rules, and a small pre-response guard in relay/judgement; add fixtures for offline browser, absent pendant, stale pipeline, and timezone disagreement.  ·  risk: A strict gate could add uncertainty or block an otherwise useful answer; recover by allowing claims with explicit source and age, and by treating non-device tasks as independent of pendant liveness. No world-changing action should be blocked solely by a stale optional surface.
- cost: Negligible API cost if snapshots are local JSON; roughly 300–600 tokens of compact context per turn. No new hardware or storage beyond a bounded latest-snapshot record.  ·  latency: About 50–150 ms for local status reads; avoid remote polling when cached observations are fresh.
- security: Status metadata only; do not copy page contents or secrets into the ledger. Apply existing sensitivity/TTL rules and redact URLs and account data.
- depends on: An authoritative owner timezone decision (currently America/Chicago memory conflicts with live machine America/New_York); A defined pendant registration/heartbeat contract so absent and stale can be distinguished; Existing /ops/status, /browser/status, /machine-context, and /pipeline routes


## What it asked for

_Nothing._
## Its own summary

Round 98 established several live truths: the Mac bridge and relay are reachable, but UI input is not actually reachable (Accessibility and Screen Recording are false), so GUI success receipts are untrustworthy. The browser extension is offline with 10 queued commands; three persisted browser sessions are stale/probe artifacts, not proof of live tabs. The latest briefing is stale and conflicts with current cached grant status. Machine timezone (America/New_York) conflicts with remembered owner timezone (America/Chicago). I recorded these findings, notified faculty-judgement, and proposed a freshness/provenance gate plus an owner-facing currentness-and-delivery check. No pendant is registered; pipeline audio events are historical, not evidence of current delivery.

**Biggest unknown:** The authoritative timezone and a real device-delivery acknowledgment contract remain unresolved. I also still need the owner to decide whether to grant Accessibility/Screen Recording to the exact AI Pendant Agent binary before any GUI automation can be considered real; this cannot be fixed inside the orchestrator.

