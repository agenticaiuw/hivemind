# Harness derivation — faculty-perception — round 89

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac UI input reachability** — At 2026-08-07T13:44:23Z, AI Pendant Agent is running but Accessibility is untrusted and Screen Recording false; zero-delta probe failed, eventsPost=false, uiActionsWillReachTheScreen=false. UI actions may report success while doing nothing. Automation grants are present for listed apps, but full-control readiness is false.
  - evidence: GET /observe returned readOnly=true, accessibility.trusted=false, inputReachability.status=failed, consequence explicitly says ui_click/ui_menu/type_text/press_keys receipts cannot be trusted; GET /ops/status permissions.ready=false.
- **Browser bridge liveness** — At 2026-08-07T13:44:23Z, browser extension home-chrome is offline with tabless state and 9 pending commands. Local durable observation still lists 3 browser sessions/tabs, including time.is/UTC and two selenium/httpbin probes, but they are not currently reachable through the extension.
  - evidence: GET /browser/status online=false, tabId/windowId null, pendingCommands=9; GET /observe browser.sessions=3 with stored tabs.
- **Pendant presence** — The Mac agent's live relay payload says mac bridge online and relay capabilities include pendant pipeline telemetry, speech, persistent state, and durable audio, but no live pendant registration is exposed by this Mac agent route. Pipeline entries labeled nrf9160 are historical records and do not establish current connectivity.
  - evidence: GET /ops/status relay.payload.macBridgeOnline=true and capabilities; GET /pipeline contains old nrf9160 events; GET /v1/devices/status returned 404 on this agent.
- **Briefing permission freshness** — The latest stored workday briefing (generated 11:30Z) says calendar and mail were not read because Automation grants were needed, while the 13:44Z /ops/status snapshot reports cached grants for Calendar and Mail and automationMissing=[]; the briefing's permission claim is stale or from an earlier snapshot and must not be treated as current.
  - evidence: GET /briefing/latest generatedAt=2026-08-07T11:30:00Z note says calendar/mail need grant; GET /ops/status observed later lists Calendar and Mail granted from grant cache and requiredMissing/optionalMissing empty.

## Capabilities it proposed

### "“Did that actually happen?” — Give me an evidence-backed answer about whether the requested change really occurred, including what each surface observed and what remains uncertain."
- **useful because:** Today the system can hold contradictory truths: a job receipt may say success while the screen was untouched, a browser tab may be stored locally while the extension is offline, and a briefing may report old permissions. The owner needs a single perception answer that distinguishes planned, attempted, observed, delivered, and physically confirmed instead of trusting any one component's status.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background for routine reconciliation and receipt indexing; realtime only when the owner asks during a live voice turn
- **latency:** Under 2 seconds for an existing job using cached evidence; up to 10 seconds when a fresh Mac/browser/pendant observation is required
- **cost:** Usually <$0.01 per query when deterministic evidence joins suffice; occasional background model call dominates ambiguous reconciliation, roughly 2k–5k input tokens. No realtime call for stored-job checks.
- **security:** Private page contents and device telemetry must remain scoped to the relevant job and user session. Never treat an untrusted UI receipt as proof. Destructive or privacy-sensitive verification should require confirmation before opening new pages or replaying an action. Retain hashes and provenance rather than full screenshots/audio by default.
- **missing:** A cross-surface reality ledger with an append-only event vocabulary: intended, accepted, started, completed, observed, delivered, acknowledged, contradicted, expired; Per-event evidence links to the exact observation timestamp, device identity, tab/session identity, and permission/liveness snapshot; A contradiction resolver that marks a claim unknown or contradicted instead of choosing the most recent success-looking receipt; A read-only owner-facing endpoint and concise spoken rendering for “Did that actually happen?”; A first-class live pendant registration and acknowledgment protocol so pendant delivery can be distinguished from relay acceptance


## Changes it proposed to its own stack

### `integration` — Add a perception preflight and truth-state gate to Mac/browser execution: immediately before any ui_click, ui_menu, type_text, press_keys, or browser_* action, read the cached /observe and /browser/status liveness snapshots. If Accessibility/inputReachability is failed, or the browser lease is offline/stale/tabless, do not execute and do not emit a success receipt; return a typed blocked_precondition result with the exact observed timestamp and remediation. Re-check after reconnect before releasing queued commands, and quarantine the existing 9 browser commands rather than replaying them blindly.
- **owner gets:** The owner stops receiving receipts that claim actions happened when the screen or browser never changed. Failed actions become immediately understandable, and stale browser commands cannot unexpectedly run after a reconnect.
- effort: Medium: shared preflight middleware plus typed receipt/status changes and tests for stale lease, reconnect, and offline pendant/Mac states.  ·  risk: A transient false-negative could refuse a safe action; recover by retrying after a fresh heartbeat/observe snapshot. It must never infer success from an HTTP 200 alone.
- cost: Negligible API cost; one local state read per action. No new data leaves the Mac beyond existing telemetry.  ·  latency: Adds roughly 10–50 ms for cached local checks; avoids 30–45 s browser timeout failures.
- security: Improves safety by preventing actions under an untrusted input path and fencing stale browser identities; does not grant permissions or expose page content.
- depends on: A single shared typed liveness/precondition schema for /observe and browser heartbeat state; Browser lease fencing/quarantine for the 9 currently pending commands


## What it asked for

_Nothing._
