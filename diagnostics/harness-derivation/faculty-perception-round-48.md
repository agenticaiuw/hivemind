# Harness derivation — faculty-perception — round 48

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac UI input reachability and permissions** — At 2026-08-07T11:35:32Z, /observe reports Accessibility trusted=false, synthesized events not accepted from the running com.aipendant.agent binary, inputReachability.status=failed, and uiActionsWillReachTheScreen=false. /ops/status independently reports permissions.ready=false, Screen Recording false, despite automation grant cache.
  - evidence: GET /observe and GET /ops/status both returned HTTP 200 with these fields.
- **Current audio output acceptance evidence** — Latest cloud-relay pipeline run rendered 24 kHz mono signed-16 PCM: 164,650 bytes, 3,430 ms, 1,806 ms render time, peak 69.1%, RMS 10.9%, clippedSamples 0, truncated=false; relay accepted the response for nRF9160 playback.
  - evidence: GET /pipeline at 2026-08-07T11:35Z, pipelineId job_165a9c9a-e5e3-4e29-b500-2fad63115ab9, tts done and relay_result done events.
- **Live cross-device state** — At 2026-08-07T11:35Z Mac bridge and browser extension are online; relay reachable and paired; browser has 3 durable sessions but Chrome currently reports 0 tabs and 4 pending browser commands. Audio pipeline has an older processing run and latest spoken reply run completed rendering/upload but pipeline status remains processing.
  - evidence: GET /ops/status, GET /browser/status, GET /browser/sessions, GET /pipeline.
- **Browser liveness contradiction** — At the same observation window, /ops/status reported browser online=true while direct /browser/status reported online=false for home-chrome (lastSeen 11:34:33Z), tabId null, tabCount null, and 4 pending commands. The direct status is the authoritative contradiction to resolve; browser readiness must not be inferred from aggregate ops status.
  - evidence: GET /browser/status at 2026-08-07T11:35Z returned online=false; GET /ops/status in parallel returned browser.online=true.

## Capabilities it proposed

### "Before doing anything, tell me whether the whole system can safely carry this out right now—and if not, exactly which link, permission, session, or device fact is stale."
- **useful because:** Today each node can report a local status, but judgement/action can accidentally trust a green relay while Mac input is unreachable, or trust a browser session whose tabs disappeared. A single fresh, evidence-cited readiness answer prevents silent no-ops and makes the pendant honest about what it can currently do.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Background/cheap model assembles typed evidence; realtime is used only to phrase the short spoken result when the owner asks on the pendant. No expensive reasoning is needed for routine health checks.
- **latency:** Under 2 seconds for parallel probes; up to 5 seconds if a browser heartbeat or pendant link round-trip is needed. Each fact carries observedAt and a TTL, with explicit UNKNOWN when a node cannot be reached.
- **cost:** Usually <$0.001 per check if rule-based; occasional small-model summarization <$0.01. Dominant cost is not tokens but LTE round trips and browser heartbeat latency.
- **security:** Do not collect page contents, screenshots, microphone audio, or credentials for readiness. Return capability-level facts only (e.g. accessibility=false, tab session stale). Any probe that would alter state requires confirmation and must be excluded from the health check.
- **missing:** A typed cross-node evidence schema with source, observedAt, TTL, confidence, and contradiction handling; Relay endpoint to request a parallel pendant/bridge/mac/browser snapshot and return an immutable evidence bundle; Mac /observe must expose a stable readiness contract rather than success-shaped-but-untrusted UI receipts; Browser extension must acknowledge command queue state and bind it to a tab/session identity; Pendant firmware must emit link/playback queue depth and last-ack telemetry, including offline-store age

### "When something I asked the pendant to do did not happen, let me ask 'what happened?' and get a short, chronological explanation showing where it stopped, what was actually acknowledged, and whether anything was changed—without trying it again."
- **useful because:** Today a queued browser command, a misleading UI receipt, a dropped LTE utterance, and a completed relay job can look like the same outcome. The owner needs post-incident truth, not another attempt or a vague failure message. This is especially valuable for reminders, messages, purchases, and other actions where duplicate retries are harmful.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Rule-based correlation should assemble the timeline and determine terminal states; use a small background model only to compress it into plain language. Realtime is needed only when the explanation is spoken immediately through the pendant.
- **latency:** Return a first structured timeline in under 2 seconds from retained receipts; allow up to 5 seconds for a missing node to reconnect. Never wait indefinitely for a device that is offline.
- **cost:** Usually under $0.002 per incident; the dominant cost is durable event storage and occasional reconnect polling, not inference.
- **security:** Persist identifiers, timestamps, state transitions, and capability-level errors—not microphone audio, screenshots, page contents, or credentials by default. Sensitive action details should be redacted in spoken output. Never replay or retry an action as part of diagnosis; require explicit confirmation for any recovery action.
- **missing:** A durable cross-node incident record keyed by one request ID from pendant press/audio through relay, Mac planner, browser session, and final acknowledgment; Explicit terminal states distinguishing accepted, executed, observed, failed, expired, cancelled, and unknown; A monotonic event sequence with device clock offset estimation and duplicate-event suppression; A privacy-aware owner-facing explanation endpoint and pendant command such as 'explain last action'; Retention and redaction policy for incident metadata, with local/offline buffering on the pendant and eventual relay upload


## Changes it proposed to its own stack

### `relay` — Make readiness aggregation fail closed on contradictory node reports: retain per-source observations with timestamps, never collapse /browser/status=false and /ops/status=true into online=true, and expose a typed contradiction requiring a fresh heartbeat before browser actions are considered reachable.
- **owner gets:** The owner gets an honest 'browser unavailable/uncertain' answer instead of commands queued into a dead extension and receipts that look successful but never reach a tab.
- effort: Small-to-medium: schema change, aggregator logic, heartbeat reconciliation, and regression tests for stale-vs-live reports.  ·  risk: A transient heartbeat loss may conservatively pause a harmless action; recover automatically after one authenticated heartbeat and preserve queued commands.
- cost: Negligible compute/storage cost; avoids wasted model calls and repeated failed browser actions.  ·  latency: Adds at most one heartbeat round trip (typically <1–2 s) when sources disagree.
- security: Improves safety; status-only metadata is retained, with no page content or credentials collected.
- depends on: Typed source/observedAt/TTL fields in relay status responses; Browser heartbeat acknowledgment bound to extensionId and session identity


## What it asked for

_Nothing._
