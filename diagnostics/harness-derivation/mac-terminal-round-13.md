# Harness derivation — mac-terminal — round 13

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac local agent health and control surface** — Local agent v0.5.0 is healthy at localhost:8000; fullControlMode and fullControlPlanner are enabled, token configured, accessibility/screen recording/automation permissions ready, and relay reachable. Browser extension is online with Safari 5 tabs and zero pending commands. Computer-use loop is disabled despite vision model configured; vision upload consent is false.
  - evidence: GET /ops/status returned HTTP 200 with agent.fullControlMode=true, computerUse.loopEnabled=false, browserExtension.online=true, permissions.ready=true, relay.reachable=true.
- **Mac host inventory** — Host is MacBook-Air-6.local, darwin arm64, macOS 26.5.2, timezone America/New_York, home /Users/evanliu. Agent reports 123 applications and extensive CLI inventory. Project path previously established as /Users/evanliu/agentic-gadget on branch main.
  - evidence: GET /machine-context and prior granted compatibility workflow inventory.
- **Browser bridge state** — Safari browser bridge is online through extension version 1.2.0; active tab is https://time.is titled UTC: 06:16, tabId 320512, 5 tabs total, pendingCommands 0.
  - evidence: GET /browser/status HTTP 200.
- **Diagnostics tool availability** — Granted mac_read_diagnostics tool currently has no implementation, so host diagnostics cannot be fetched through that interface. HTTP /ops/status and /machine-context remain usable read-only discovery paths.
  - evidence: mac_read_diagnostics call returned error: tool granted schema but no implementation yet.
- **Ops snapshot consistency** — GET /ops/snapshot is public/readable and reports healthy agent/relay, but browser device metadata can transiently lose tabId/windowId/tab URL/title while online (snapshot at 06:17:46 had null/empty fields, whereas /browser/status at 06:17:25 had complete Safari metadata). Treat online as reliable heartbeat but tab metadata as eventually consistent.
  - evidence: GET /ops/snapshot HTTP 200 versus GET /browser/status HTTP 200 within same reconnaissance round.

## What it asked for

_Nothing._
## Its own summary

Recon complete for this round. The Mac local agent (v0.5.0) is healthy, full-control planner is enabled, permissions are ready, relay is reachable, and Safari browser bridge is online. Host is MacBook-Air-6.local, macOS 26.5.2 arm64, /Users/evanliu, America/New_York; project is /Users/evanliu/agentic-gadget on main. Read-only HTTP observability is available via /health, /capabilities, /ops/status, /ops/snapshot, /browser/status, and /machine-context. Browser metadata is eventually consistent and may be null in /ops/snapshot despite an online heartbeat. The granted mac_read_diagnostics interface has no implementation, so it cannot be used; no replacement tool is needed because HTTP diagnostics work. For useful future work, the only outstanding need is the previously requested local-agent route/job lifecycle contract (especially execute receipts, cancellation, undo, and failure recovery); do not request it again this round because it is already pending.

**Biggest unknown:** Exact authenticated POST /execute and job lifecycle semantics, including receipt schema and retry/recovery behavior, remain unverified because no agent token is available to probe protected routes.

