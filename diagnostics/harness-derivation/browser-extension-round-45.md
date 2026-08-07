# Harness derivation — browser-extension — round 45

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-device-health** — As of live ops snapshot, browser extension health has only home-chrome, offline, no tab/user-agent, with 3 pending commands; Safari registration is absent. Mac bridge and relay are online, so browser availability—not general hive connectivity—is the blocker.
  - evidence: GET /browser/status and GET /ops/status at 2026-08-07T10:32Z both report browser online=false, devices=[home-chrome offline], pendingCommands=3; relay macBridgeOnline=true.

## Capabilities it proposed

### "“Compare the private page I’m looking at with the relevant file on my Mac, and tell me what is missing or inconsistent.”"
- **useful because:** Today the browser can expose an authenticated page and the Mac can inspect local files, but the owner cannot ask one spoken question that reliably binds those two sources to the exact current tab and produces a cited discrepancy report. This would be valuable for invoices versus downloaded receipts, travel reservations versus calendar entries, forms versus supporting documents, and account statements versus spreadsheets.
- **path:** pendant → relay → browser → mac-planner → mac-vision → mac-terminal → dashboard
- **model tier:** Use the realtime tier only to capture the spoken request and return a short answer; use a cheaper background planner for source selection, extraction, normalization, and comparison. Browser extraction and local-file parsing should be deterministic first, with a text model only for field alignment and ambiguity.
- **latency:** Acknowledge on the pendant within 1 second; return a first evidence-backed comparison in 10–20 seconds, with longer parsing continuing as a resumable job.
- **cost:** Roughly $0.01–$0.08 per comparison depending on page/file length; tokenized page and document text dominates, while extension and local parsing are negligible.
- **security:** Authenticated page contents and local files must remain on the Mac whenever possible; relay should receive only the spoken intent, job state, and optionally a redacted result. Bind the request to the active tabId plus URL/title hash and a selected local file fingerprint to prevent stale or cross-account comparisons. Show source snippets, timestamps, and confidence, and never edit or submit either source without a separate owner request.
- **missing:** A working Safari heartbeat/device registry and command path that exposes a stable active-tab/session identity; A Mac-local comparison job that can retrieve browser extraction and search/select a local document without uploading either wholesale; A typed evidence schema for normalized fields, conflicts, missing values, and source snippets; A pendant-friendly result/continuation protocol so the owner can ask “show me the two conflicting lines” or resume after a dropped link; Dashboard UI for choosing or correcting the local file when multiple candidates match


## Changes it proposed to its own stack

### `browser-harness` — Implement a lease-based browser device registry and health contract. Have each extension heartbeat with extensionId, browser/device identity, version, tabCount and coarse tab metadata, supported actions, monotonic sequence, and sentAt; server stores lastSeen and lease expiry, rejects out-of-order heartbeats, and exposes per-device state {online, stale, absent} with age, capabilities, pending-command count, and a reason code. Keep Safari and home-chrome records even when offline instead of dropping them. Make POST /execute attach the selected device's health snapshot to timeout/error receipts, and let relay/mac-planner choose Safari only when its lease and required capability are valid rather than treating all browser failures as generic timeouts.
- **owner gets:** When the owner asks to read a logged-in page, the system can honestly say “Safari is not connected,” “Safari is connected but has no open tab,” or “Chrome is stale,” instead of silently hanging for 45 seconds or sending work to the wrong browser. Recovery can be automatic when the extension returns, without losing queued work.
- effort: Medium: extension heartbeat payload and retry loop; backend registry/lease persistence; status schema and execute-time selection/error receipts; integration tests for absent, stale, reconnect, and out-of-order heartbeats.  ·  risk: A bad clock or missed heartbeat could report stale too eagerly, and retaining device metadata slightly increases operational data. Use server receive time for lease age, bounded metadata (no page contents), and preserve pending commands while marking them undeliverable; on reconnect require command/session affinity checks before delivery.
- cost: Negligible API cost; one tiny heartbeat every 15–30 seconds per extension and a small durable registry row per device.  ·  latency: Adds no browser-action latency; device selection becomes an immediate registry lookup and avoids the current 45-second wait when no browser exists.
- security: Heartbeat must authenticate the registered extension and avoid URLs/titles unless explicitly allowed; capability claims are advisory and server-issued device identity is authoritative. Health snapshots may be included in logs but never page content or cookies.
- depends on: A working authenticated extension heartbeat handler (the currently advertised POST /browser/heartbeat is not live); The existing browser command queue and tab/session affinity work; Relay/mac-planner routing must consume the new typed health state


## What it asked for

_Nothing._
## Its own summary

I discovered a live, specific gap and filed a new browser-harness change: a durable, authenticated heartbeat/lease registry that preserves Safari and Chrome identities, reports online/stale/absent plus capabilities and reason codes, rejects out-of-order heartbeats, and annotates execute failures. Live evidence confirms the problem: /browser/status and /ops/status show only offline home-chrome, no tab or user-agent, three pending commands; Safari is absent while Mac bridge and relay are online. I sent this finding to mac-planner.

**Biggest unknown:** The Safari extension's actual heartbeat implementation/registration path is still not observable, and no browser command can be exercised until Safari reconnects and creates/reports a tab. The remaining work needed is a live authenticated POST /browser/heartbeat handler plus extension retry/registration and a reconnect test; then relay/mac-planner must consume the typed health state.

