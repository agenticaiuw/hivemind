# Harness derivation — faculty-perception — round 38

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-input-perception** — As of 2026-08-07T10:56:48Z, Mac agent observation reports Accessibility trusted=false, screenRecording=false, inputReachability failed, and synthesized events from com.aipendant.agent are not accepted; ui actions may report success while doing nothing. AI Pendant Agent is running at /Users/evanliu/Applications/AI Pendant Agent.app.
  - evidence: GET /observe HTTP 200: accessibility.trusted=false; eventsPost=false; inputReachability.status=failed; consequence says receipts cannot be trusted.
- **timezone-conflict** — The owner memory says timezone America/Chicago, while live Mac /machine-context reports timezone America/New_York. This is an unresolved context conflict that can affect scheduled routines and spoken time answers.
  - evidence: discover owner remembered.text says timezone: America/Chicago; GET /machine-context HTTP 200 reports machine.timezone America/New_York.
- **browser-observability** — At 2026-08-07T10:56:xxZ the browser extension home-chrome is offline with no attached tab, while the Mac agent reports 3 pending browser commands. Authenticated browser actions cannot currently be verified through the extension.
  - evidence: GET /ops/status HTTP 200: browserExtension.online=false, devices home-chrome online=false, pendingCommands=3; GET /browser/status established same offline state.

## Capabilities it proposed

### "“Before you tell me something happened—or schedule anything—tell me if the devices disagree about whether it really happened or what time zone I mean.”"
- **useful because:** Today the Mac agent can emit a successful UI receipt even when Accessibility rejects the input, and owner memory says America/Chicago while the Mac says America/New_York. A contradiction-aware truth brief prevents silent false completion and mis-timed reminders. It is genuinely hive-native: pendant supplies the user's local acknowledgement, relay retains a durable contradiction, Mac supplies OS permissions/time, and browser supplies session/action evidence.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use deterministic checks and a cheap background model to classify contradictions; reserve realtime only to explain a live warning over the pendant.
- **latency:** For an action, <300 ms preflight from cached health/evidence; live warning within one spoken turn. Background reconciliation can run hourly or on every new receipt.
- **cost:** Near-zero for typed comparisons and hashes; roughly $0.001–$0.01 per background reconciliation depending on model use. Dominant cost is context/evidence storage, not inference.
- **security:** Store only typed status, timestamps, timezone identifiers, permission state, and receipt hashes—not page contents or secrets. Never expose captured secrets in a warning. Require explicit owner confirmation to change timezone authority or treat an untrusted UI action as completed.
- **missing:** A shared evidence/contradiction ledger with source, observedAt, confidence, TTL, and severity; A hard integration from Mac action receipts to /observe permission state so 'success' is downgraded when inputReachability fails; An owner-facing timezone resolution flow: spoken choice on pendant plus persisted authoritative timezone and audit trail; A durable relay event/ack protocol so warnings survive offline periods and are acknowledged exactly once

### "“What can you currently know for sure?” — give me a short spoken list of facts that are mutually corroborated, plus the few important things that are contradictory or unverified."
- **useful because:** Today the system can expose raw health and action data, but cannot turn disagreement among the pendant, relay, Mac, and browser into a trustworthy answer. This gives the owner an immediate confidence boundary: what actually happened, what merely claims to have happened, and what needs attention. It is not a daily briefing, page watch, action receipt, or undo feature; it is an on-demand epistemic status report across the whole hive.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic evidence aggregation and conflict scoring first; use a cheap text model only to compress the resulting typed facts into one short spoken response. Realtime is needed only when the owner asks during a live pendant conversation.
- **latency:** Under 500 ms from cached evidence; up to 2 seconds when fresh Mac or browser probes are available. Offline pendant requests should queue and receive the report when the relay reconnects.
- **cost:** Usually below $0.002 per request; typed comparisons dominate and model cost is only the final compression.
- **security:** Never include secrets, page contents, or raw credentials in the report. Facts need source labels, freshness, confidence, and sensitivity. Contradictions involving account data should be summarized without reproducing private values; owner confirmation is required before changing an authority or retrying an action.
- **missing:** A shared evidence schema and conflict resolver spanning pendant telemetry, relay jobs, Mac observation, and browser heartbeat/action results; A durable freshness and provenance ledger with redaction and sensitivity handling; A pendant/relay response path for queued epistemic queries during connectivity loss; A concise spoken renderer and dashboard drill-down showing why each fact is trusted or disputed


## Changes it proposed to its own stack

### `context` — Add a signed, source-ranked contradiction ledger consumed by every planner and receipt renderer. Each fact carries source (owner, Mac, pendant, browser), observedAt, TTL, confidence, and conflict group. When /observe says inputReachability failed, automatically rewrite any UI-action success to 'unverified' and attach the exact cause; when timezone sources differ, block relative-time scheduling and ask the pendant owner to choose an authority.
- **owner gets:** They stop hearing “done” when nothing reached the screen, and stop receiving reminders at the wrong local time. The warning is actionable and concise instead of requiring the owner to debug machine state.
- effort: Medium: typed schema and resolver in shared context service, receipt middleware, relay persistence, pendant acknowledgement UI, and regression tests for stale/offline evidence.  ·  risk: A stale permission probe could over-warn or block harmless actions; use short TTLs, distinguish hard vs soft conflicts, and allow read-only results while blocking irreversible actions. Recovery is a fresh probe plus owner acknowledgement.
- cost: Negligible runtime/API cost; small D1/local JSON storage growth for evidence records.  ·  latency: <100 ms for cached ledger evaluation; fresh probes may add 0.5–2 s only before GUI actions.
- security: Improves safety by preventing unverified claims; ledger must redact URLs, page text, and secrets and expose only typed metadata.
- depends on: Mac permission/input reachability probe must be callable with authenticated freshness; Shared typed context projection and durable relay event acknowledgements; Pendant spoken confirmation/input for choosing authoritative timezone


## What it asked for

_Nothing._
