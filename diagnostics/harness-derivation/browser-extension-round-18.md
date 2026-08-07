# Harness derivation — browser-extension — round 18

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser bridge live state** — Safari browser bridge is currently offline with no registered devices, while one command remains pending; all browser enqueue wrapper tools fail before dispatch. This leaves authenticated-page work unavailable and risks orphaned queue state.
  - evidence: GET /browser/status returned HTTP 200: {"online":false,"devices":[],"pendingCommands":1}; browser_command_enqueue returned 'This tool was granted a schema but has no implementation yet.'

## Capabilities it proposed

### "“Check my logged-in accounts for inconsistent personal details, upcoming expirations, or duplicate subscriptions, and prepare a concise fix list without changing anything.”"
- **useful because:** Private account portals often contain stale addresses, payment details, insurance/identity records, and overlapping subscriptions that public web search cannot see. A cross-site comparison catches costly or disruptive mismatches and gives the owner a single reviewable checklist while preserving full control.
- **path:** browser → mac-bridge → dashboard
- **model tier:** Use the background tier for scheduled crawling and normalization; use realtime only if the owner asks follow-up questions. The authenticated Safari bridge extracts only explicitly selected account pages, and the Mac workbench compares normalized fields and links back to evidence.
- **latency:** For an on-demand check, 1–3 minutes depending on the number of portals; scheduled scans can run in the background and notify only on new discrepancies. The UI should stream progress per site and tolerate an unavailable tab.
- **cost:** Roughly $0.05–$0.30 per invocation for extraction/normalization depending on page count; browser time and model tokens dominate, with no need for realtime inference.
- **security:** Account pages and sensitive identifiers leave Safari only to the local Mac agent and the configured model path; redact secrets and payment numbers before comparison, store hashes plus source snippets rather than raw pages, and let the owner choose which sites/fields are included. Never edit or submit; any later fix remains a separately reviewed action.
- **missing:** A durable multi-site authenticated browser job runner with tab/session reattachment and explicit site allowlists; A schema for normalized fields (identity, contact, billing, renewal date, subscription) with sensitivity labels and conflict explanations; A local discrepancy workbench with evidence links, redaction, retention controls, and export/undo-free read-only results; A working browser command enqueue implementation and reliable Safari heartbeat/device registration


## Changes it proposed to its own stack

### `browser-harness` — Add a browser-bridge self-healing lease protocol: each Safari heartbeat carries a device nonce, extension version, tab inventory, and last-applied command sequence; the Mac agent expires orphaned pending commands, replays only unacknowledged idempotent commands after reconnect, and emits a distinct stale/aborted result for commands that cannot safely replay. Add a local 'reconnect extension' diagnostic surfaced in the dashboard rather than leaving pendingCommands stranded.
- **owner gets:** When Safari sleeps, updates, or loses its extension connection, the owner should not be left with a silently failed private-web task or an action that may execute later unexpectedly. Reconnection would resume safe reads and clearly stop ambiguous mutations, making browser automation dependable in daily use.
- effort: Medium: extension heartbeat/ack changes, queue state machine and migration, stale-command cleanup, dashboard diagnostics, and fault-injection tests for disconnects during each browser operation.  ·  risk: A replay bug could duplicate a click or form mutation. Default replay must be limited to reads/navigation with idempotency keys; ambiguous mutations become aborted with evidence, and queue recovery can be manually cleared. Roll back by disabling replay while retaining expiry diagnostics.
- cost: Negligible API cost; small local persistence (under 100 KB for queue metadata) and no meaningful power change beyond the existing heartbeat.  ·  latency: Reconnect adds one heartbeat round trip; normal commands unchanged. Safe read recovery may add up to one poll interval, while ambiguous writes stop promptly.
- security: Device nonce prevents stale extension instances from consuming commands; do not include page contents in heartbeats. Persist only command IDs/status and rotate the nonce on extension reinstall.
- depends on: A working browser command enqueue implementation and extension heartbeat path; The existing reliable browser queue/result receipts (chg-14accc01); A clear command idempotency classification for browser reads versus mutations


## What it asked for

_Nothing._
## Its own summary

Discovered the Mac agent is healthy, but the browser bridge is not: GET /browser/status reports online=false, no devices, and one stranded pending command; every granted enqueue wrapper still returns an implementation error. I sent mac-planner this diagnosis, recorded it, proposed a new cross-account read-only discrepancy/expiry checker, and proposed a self-healing browser lease/replay protocol. To make the browser capability useful, I still need a functioning enqueue implementation, Safari heartbeat/device re-registration, and orphan-command cleanup; the durable authenticated job runner, normalized sensitive-field schema, and evidence workbench are also needed for the proposed workflow.

**Biggest unknown:** Why the real Safari extension stopped reporting (extension process, bridge transport, or server registration) and whether the stranded pending command is safe to expire. I cannot inspect or recover that from this browser facet while enqueue is stubbed.

