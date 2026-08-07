# Harness derivation — faculty-perception — round 94

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-input** — At 2026-08-07T14:04Z, AI Pendant Agent is running but Accessibility and Screen Recording are not trusted; inputReachability is failed and ui_actions will report success without reaching the screen. System Events and app automation grants are present.
  - evidence: GET /observe HTTP 200: accessibility.trusted=false, screenRecording=false, inputReachability.status=failed, uiActionsWillReachTheScreen=false; GET /ops/status shows automation grants and permissions.ready=false.
- **fleet-live-state** — At 2026-08-07T14:04Z the Mac bridge is online and relay reachable; browser extension home-chrome is offline with 9 pending commands; no pendant is registered/online in the live device table.
  - evidence: discover devices: home-macbook-bridge online; cloudflare-contract-test offline; home-chrome offline. GET /ops/status reports browserExtension.online=false, pendingCommands=9, relay.macBridgeOnline=true.
- **audio-history** — The pipeline contains historical pendant/nRF9160 events and completed 24 kHz mono PCM rendering, but these are recorded pipeline runs, not evidence of a currently connected pendant. A historical nRF9160 run remains processing and cites offline-store alert delivery.
  - evidence: GET /pipeline HTTP 200 lists source=nrf9160 event at 07:22 and cloud-relay audio-native runs; discover devices has no nRF9160/pedant device.
- **model-routing** — Observed routing has 7 requests: 57% off planner, 30,887 estimated tokens saved; planner baseline ~8,837 tokens and 2,527 ms, while recent routine/brief requests use deterministic or background tiers.
  - evidence: GET /routing HTTP 200: saved.requests=4, saved.percentOfRequestsOffPlanner=57, baseline.tokensPerRequest=8837, baseline.latencyMs=2527.

## Capabilities it proposed

### "“Did that actually reach me, and where did it stop?” Give me one trustworthy, evidence-linked timeline for a request across the relay, Mac, browser, and pendant: received, understood, planned, action accepted, action executed, response rendered, delivered, and actually acknowledged/heard—clearly separating facts from inferred or stale states."
- **useful because:** Today a queued browser command, a successful-looking but unreachable Mac UI action, a relay acceptance, and an old pendant pipeline record can all look like completion. The owner needs a single answer that identifies the exact last verified boundary instead of claiming success or making them investigate four surfaces.
- **path:** pendant → relay → mac-planner → browser-extension → faculty-perception → faculty-judgement → faculty-action → dashboard
- **model tier:** Use deterministic event correlation and evidence classification first; use the background tier only to summarize the correlated timeline. Reserve realtime for a spoken “where did it stop?” query and never let the model promote an unverified event to success.
- **latency:** Under 500 ms for an existing job; under 2 s if a fresh Mac, browser, relay, or pendant acknowledgment probe is required. Spoken response should begin immediately with the last verified boundary and then provide detail.
- **cost:** Usually near-zero model cost for correlation; roughly 500–1,500 summary tokens only when events need explanation. The dominant cost is storage/indexing and occasional cross-surface probes, not inference.
- **security:** Private URLs, action receipts, and device identifiers must remain scoped to the owner and be redacted in spoken output. Never expose page contents merely to explain delivery. A “heard” state requires a signed pendant playback acknowledgment, not inference from upload or queue acceptance; destructive actions still require the existing approval path.
- **missing:** A durable cross-surface event envelope with one correlation ID and monotonic timestamps; Explicit state transitions for accepted, executed, rendered, delivered, played, and acknowledged, each carrying source and freshness; A signed pendant playback/acknowledgment protocol and live device registry; Browser command completion events tied to tab/session and Mac action receipts tied to actual reachability; A dashboard and voice endpoint that render the evidence chain and the last verified boundary rather than a generic job status

### "“Where did I last have my phone, keys, or headphones?” Have the pendant detect the tagged item nearby, the Mac record the last reliable room/location association, and the relay retain a privacy-preserving last-seen trail so I can ask from anywhere—even when the item and Mac are no longer connected."
- **useful because:** The owner gets a practical answer to a daily physical-world problem that no current browser, Mac planner, or cloud chat can answer. It should say “last seen beside the Mac at 8:14” or “not observed,” never fabricate a current location.
- **path:** pendant → mac-planner → relay-realtime → unified → faculty-perception → faculty-judgement
- **model tier:** Deterministic BLE/UWB sightings and confidence calculation; background model only for natural-language explanation. Realtime is appropriate for the spoken query, not for sensing or history computation.
- **latency:** Local proximity result within 2 seconds; remote last-seen answer within 1 second from relay storage.
- **cost:** Negligible inference cost; storage is small (timestamp, tag ID, coarse location, confidence). Hardware dominates: roughly $20–$80 for BLE/UWB tags and potentially $30–$100 for a UWB-capable pendant revision.
- **security:** Location history is highly sensitive. Store coarse zones rather than continuous coordinates, encrypt tag identifiers, retain only a configurable rolling window, and require explicit pairing. Never allow another device or account to query the owner’s item history.
- **missing:** A pendant with BLE scanning and, preferably, UWB ranging; the currently observed fleet has no live pendant; A paired-tag protocol with rotating identifiers and battery telemetry; Mac-side zone calibration using known anchors or owner-confirmed locations; Relay storage and authenticated query endpoint for last-seen sightings; A perception model that reports confidence, age, and “not observed” without interpolation


## Changes it proposed to its own stack

### `integration` — Add a perception preflight envelope consumed by judgement/action before every computer or wearable operation. It should snapshot (with timestamp and TTL) Mac inputReachability, Accessibility/Screen Recording, app automation grants, browser-extension connectivity and pending-command count, relay/bridge status, and pendant registration. Classify each intended action as reachable, automation-only, queued-but-unconfirmed, or impossible; prohibit UI-action success receipts when inputReachability is failed, and explicitly label pipeline/audio records as historical unless a live device delivery acknowledgment exists. When UI is unavailable, suggest only an actually granted AppleScript/API route or ask the owner to reconnect/grant permissions.
- **owner gets:** The owner stops hearing “done” when clicks or typing never reached the screen, and stops mistaking old pendant audio or queued browser commands for live delivery. Safe alternatives can still run through granted app automation instead of silently failing.
- effort: Medium: typed schema, TTL/caching, planner/action middleware, receipt changes, and tests for stale/offline states across relay, Mac, browser, and future pendant.  ·  risk: A stale or overly conservative snapshot could block a valid action; recover by short TTL, explicit refresh, and a visible “recheck” path. Never infer live pendant presence from historical pipeline events.
- cost: Negligible API cost; a few hundred tokens of compact state per action, reducing expensive planner retries and false-action recovery.  ·  latency: ~50–150 ms local preflight; avoids multi-second failed UI loops.
- security: Improves safety by preventing unverified side effects; state includes permission/connectivity metadata but no page contents or secrets.
- depends on: An action-receipt gate/precondition hook (not present in the current receipt-only implementation); A live pendant device-registration and delivery-ack route when hardware exists; Browser extension heartbeat/reconnect behavior for queued commands


## What it asked for

_Nothing._
