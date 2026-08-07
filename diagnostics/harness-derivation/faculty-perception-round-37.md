# Harness derivation — faculty-perception — round 37

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-input-and-browser-state-2026-08-07T10:53Z** — Mac agent is online (v0.5.0, fullControlMode and llmPlanner enabled), but AI Pendant Agent still lacks Accessibility and Screen Recording: /observe reports trusted=false, eventsPost=false, inputReachability=failed, uiActionsWillReachTheScreen=false; /ops/status says requiredMissing=[] yet ready=false. Browser extension home-chrome is offline with 3 pending commands. Relay is reachable and mac bridge online.
  - evidence: Fresh parallel GET /observe, /ops/status, and /pipeline responses at 2026-08-07T10:53:49Z.

## Capabilities it proposed

### "“Did you actually do it?” — give me a truthful spoken answer, with what was observed on the Mac, browser, relay, and pendant, and say plainly when an action could not have reached the screen."
- **useful because:** Today the Mac reports UI actions as successful even when synthesized input is discarded. A cross-surface attestation would prevent false completion claims: it combines Mac input reachability and foreground evidence, browser heartbeat/tab evidence, relay job receipts, and pendant delivery/playback telemetry, distinguishing planned, attempted, reached, and verified.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use deterministic status/evidence aggregation first; use a cheap background text model only to summarize conflicting receipts. Reserve realtime for the spoken response when the owner asks live.
- **latency:** Under 1 second for cached status and receipts; up to 3 seconds for fresh Mac/browser probes. The spoken answer should begin with the verdict, then one sentence of evidence.
- **cost:** Near-zero model cost for typed aggregation; roughly $0.001–$0.01 only when a background model is needed to summarize a large evidence set. Storage and probes dominate.
- **security:** Do not expose page contents or secrets in the spoken receipt; return source class, app/tab identity, timestamps, and hashes/snippets only. A fresh probe may reveal foreground app metadata and must be retained briefly. Never infer success from an executor's optimistic response when /observe says input is unreachable.
- **missing:** A signed, correlated cross-surface attestation schema linking plan/action/job IDs to Mac /observe, browser heartbeat/result, relay receipt, and pendant playback acknowledgement.; A hard policy gate in judgement that maps evidence states (planned/attempted/reached/verified/failed/unknown) and prevents 'done' language for unknown or failed.; Browser reconnect reconciliation for the 3 currently pending commands when home-chrome returns online.; Reliable Accessibility and Screen Recording grants to the exact running AI Pendant Agent binary; current probes still show trusted=false, eventsPost=false, and inputReachability=failed.

### "“What was I looking at when I said that?” — show me the exact work context around a spoken moment, including the Mac app or browser tab I was using, a redacted visual snapshot when permitted, and the pendant audio timestamp."
- **useful because:** People speak to the pendant while switching between documents, tabs, and conversations, then lose the referent. Today these surfaces have separate timestamps and logs but no privacy-preserving, owner-queryable moment join. A synchronized moment record would let the owner recover context without having to repeat the task or remember which screen was active.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use deterministic timestamp correlation, app/tab metadata, and local screenshot redaction first. Use a cheap background model only for OCR/redaction and concise indexing; use realtime only when the owner asks for the moment during a live conversation.
- **latency:** Capture metadata within 250 ms of the button/voice event; upload or persist a visual snapshot asynchronously. A query should return the matched moment in under 2 seconds on the Mac, or clearly report metadata-only when the Mac was unavailable.
- **cost:** Usually negligible model cost; background OCR/redaction may cost roughly $0.001–$0.02 per captured snapshot. Local encrypted storage and optional relay retention dominate operational cost.
- **security:** Default to metadata-only and do not retain screenshots or raw audio unless explicitly enabled. Redact passwords, payment details, private browser fields, and other sensitive regions locally before any relay upload. Require an obvious pendant gesture or setting for visual capture, show retention duration, and provide deletion by moment ID. Never claim a screenshot represents the moment unless its timestamp and source are verified.
- **missing:** A clock-synchronization and correlation protocol spanning pendant monotonic time, relay receipt time, Mac observation time, and browser tab activity.; A local Mac capture service that records the foreground app, active tab, and consent-gated screenshot with sensitive-region redaction before upload.; A pendant event marker carrying button/utterance start and end timestamps even when the LTE link is down.; An encrypted, searchable moment index with short configurable retention and deletion receipts.; A cross-surface query endpoint that returns provenance and confidence rather than blending separately timed observations into a false exact snapshot.


## What it asked for

_Nothing._
