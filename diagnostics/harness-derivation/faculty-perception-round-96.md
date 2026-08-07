# Harness derivation — faculty-perception — round 96

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live-device-registry** — At 2026-08-07T14:16Z, reachable devices are home-macbook-bridge (mac_bridge, online), home-chrome (browser, offline), and cloudflare-contract-test (mobile, offline); no pendant/nRF9160 device is registered.
  - evidence: discover devices returned exactly these three devices; /ops/status relay payload says macBridgeOnline=true.
- **mac-perception** — Mac local agent is running v0.5.0 in full-control mode, but Accessibility and Screen Recording are not trusted for AI Pendant Agent; /observe reports synthesized UI events will do nothing and ui_actions_will_reach_the_screen=false. Automation grants are present.
  - evidence: GET /ops/status and GET /observe at 2026-08-07T14:16Z.
- **browser-perception** — Browser extension home-chrome is offline with 9 pending commands; durable browser sessions exist (3 tabs), including UTC time.is and two selenium/httpbin probe tabs, but no live extension connection.
  - evidence: GET /browser/status and GET /observe.
- **machine-timezone** — Mac machine context reports timezone America/New_York.
  - evidence: GET /machine-context.

## Capabilities it proposed

### "“If I approve this, keep watch across every surface until you can prove it actually reached the right place—and if something silently diverges, tell me exactly where the handoff broke.”"
- **useful because:** Today the system can report that a Mac job or relay upload was accepted, but the owner cannot obtain one end-to-end, independently evidenced answer spanning approval, relay admission, Mac execution, browser mutation, and (when present) pendant delivery/playback. This capability would replace false confidence with a single, human-readable chain of custody and a precise break point.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified → dashboard
- **model tier:** Use deterministic event correlation and hashes for the chain; reserve the realtime model for a short spoken explanation when the owner asks. No expensive model is needed for monitoring.
- **latency:** Normal actions remain unchanged; evidence updates asynchronously within seconds. On a live pendant, a delivery/playback verdict should arrive within one heartbeat interval, with an explicit timeout rather than waiting indefinitely.
- **cost:** Near-zero incremental inference cost; small relay storage and event-indexing cost dominate. A spoken exception uses one short realtime turn only when requested.
- **security:** Evidence must be owner-scoped and redact page contents, tokens, and audio; retain hashes, event types, timestamps, device IDs, and minimal snippets. Any retry or compensating action requires a fresh confirmation, never an automatic replay of an irreversible step.
- **missing:** A tamper-evident cross-surface event envelope carrying one correlation ID, plan hash, approval counter, and monotonic sequence; Relay-to-Mac and relay-to-pendant delivery acknowledgements with durable timeout semantics; Browser mutation receipts that include session/tab identity and before/after field hashes; A dashboard/voice query that reconciles the envelopes instead of treating local success as end-to-end success; A physical pendant to emit authenticated receipt events when one is paired


## Changes it proposed to its own stack

### `context` — Add a cross-surface Reality Boundary / liveness reconciler. It continuously joins the authoritative device registry, Mac /ops status, browser heartbeat, and pipeline event timestamps. It labels every observation as live, recently-seen, historical, or unverifiable, detects contradictions (for example pipeline records mentioning nRF9160 while no pendant is registered), and publishes a compact evidence object with source, observedAt, freshness deadline, and reason. Action and judgement layers must consume this object rather than infer presence from historical pipeline rows.
- **owner gets:** The assistant will stop claiming that a pendant heard or played something merely because an old pipeline record says so. It can honestly say what is connected right now, avoid unsafe approval prompts when the wearable is absent, and explain stale/offline failures in one sentence.
- effort: Medium: relay/device-registry adapter, Mac route poller, pipeline timestamp classifier, contradiction tests, and a small typed endpoint consumed by judgement/action.  ·  risk: A clock or registry outage could mark healthy devices unknown and make the system conservative; recover by exposing source-level evidence and allowing read-only answers while blocking only claims/actions that require liveness.
- cost: Negligible API cost; polling can be event-driven from heartbeats plus low-rate status refresh. Small D1/storage footprint for latest evidence only.  ·  latency: Under 100 ms for cached reads; refresh asynchronously so voice response is not held up.
- security: No new secrets; evidence may reveal device presence and timing, so scope it to the owner and avoid exposing private tab URLs in the evidence summary.
- depends on: Authoritative relay device registry and delivery acknowledgments (currently requested but not yet returned); A typed context projection consumed by judgement/action; Explicit freshness thresholds per source

### `relay` — Create an append-only cross-surface handoff ledger, distinct from each surface's existing job/pipeline logs. Every approved plan receives a correlation ID, canonical plan hash, approval counter, and per-hop signed receipt. The relay reconciler records admission, Mac start/finish, browser before/after hash, relay upload, and pendant delivery/playback (when paired), with monotonic sequence numbers and explicit expiry. A verdict endpoint returns complete, failed-at-hop, or unverifiable; local success must never be promoted to complete without the downstream receipt.
- **owner gets:** They can ask one question—“did it really happen?”—and receive an honest answer with the exact handoff that failed, instead of piecing together unrelated receipts or trusting a stale “accepted” status.
- effort: High: shared envelope schema, signing/key rotation, adapters in relay, Mac job runner, browser bridge, and future pendant firmware; reconciliation and failure-injection tests across offline/reconnect cases.  ·  risk: Clock skew, retries, or lost receipts can create temporary unverifiable verdicts; recover with monotonic counters, idempotent receipt keys, and a visible distinction between failed and unknown. Never retry irreversible actions automatically.
- cost: Low ongoing model cost; modest D1/object storage and event-indexing overhead. Retain compact hashes/metadata by default, with bounded raw evidence retention.  ·  latency: No blocking on normal execution; verdict becomes complete asynchronously after downstream receipts. Voice answers may need to say “still unverified” rather than wait.
- security: Receipt signatures and scoped device keys prevent one compromised surface from fabricating completion. Do not put page text, secrets, or raw audio in the ledger; hash and redact them.
- depends on: A relay-owned device key registry and receipt authentication; Browser bridge mutation receipts with before/after hashes; Pendant firmware lifecycle telemetry once a pendant exists; A judgement/action policy that treats unverifiable as non-complete


## What it asked for

_Nothing._
## Its own summary

Fresh perception is now recorded: the Mac bridge is online, but no pendant/nRF9160 is registered; the browser extension is offline with 9 queued commands; three durable browser tabs exist but are not a live extension connection; Mac Accessibility and Screen Recording remain false, so UI receipts are untrustworthy even though AppleScript automation is granted; machine timezone is America/New_York. I proposed a Reality Boundary liveness reconciler to prevent historical pipeline rows being mistaken for current device presence. I still need authoritative relay device presence/delivery acknowledgements, continuity-event retention/ack semantics, and browser-read provenance once those pending grants/context responses arrive. Accessibility/Screen Recording still requires the owner manually, not this orchestrator.

**Biggest unknown:** Whether any future pendant connection can be observed with end-to-end delivery/playback acknowledgements; currently the relay has no registered pendant, so historical nRF9160 pipeline events cannot establish present reality.

