# Harness derivation — mac-planner — round 59

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-readiness** — At round 59, the Mac bridge is online but not ready for GUI/screen workflows: Accessibility trusted=false and Screen Recording granted=false; browser extension home-chrome is offline with 3 pending commands. Granted mac_readonly_inspect is present in schema but returns no implementation.
  - evidence: GET /ops/status HTTP 200 payload at 2026-08-07T10:43Z; parallel mac_readonly_inspect calls each returned 'This tool was granted a schema but has no implementation yet.'

## Capabilities it proposed

### "When something fails, say “file this failure” and leave a privacy-safe bug report with the exact Mac/browser/pendant evidence and the next recovery step."
- **useful because:** The owner already experiences failed Gmail/GitHub/calendar/browser requests and wants a pendant that can file its own bug reports. This turns a vague spoken failure into a reproducible report without requiring them to open logs or remember what happened.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Background model for bundle normalization and deduplication; realtime only for the one-sentence pendant acknowledgement.
- **latency:** Acknowledge locally/in realtime in under 1 second; assemble and upload the report within 10 seconds, retrying when the Mac or browser reconnects.
- **cost:** Low: one small background summarization call per distinct failure; dominated by report normalization, not inference. Raw logs remain local unless the owner invokes filing.
- **security:** Default to local redaction of tokens, cookies, message bodies, URLs with query secrets, and captured audio. Include structured status, action type, timestamps, app names, error text, and hashes by default; show a spoken/dashboard preview before upload. Never include the bike-lock secret or other secret-sensitivity captures.
- **missing:** A shared failure-envelope schema correlating pendant utterance/request ID, relay job ID, Mac job receipt, browser command ID, and reconnect state; A local redaction and sensitive-field classifier with an owner-visible preview; A durable outbox that can file later when Mac/browser are offline; A relay endpoint and dashboard issue view with deduplication and status updates

### "When I walk away from my Mac, remember what I was doing across my open apps and logged-in browser tabs; when I come back and say “pick up where I left off,” give me the shortest useful re-entry brief and restore only the relevant workspace."
- **useful because:** Today the pendant, Mac, and browser each lose the owner's working thread at the physical boundary between them. This would make leaving and returning feel continuous: the pendant records intent, the Mac reports the active app/document, the browser contributes tab/session context, and the relay preserves a compact handoff even while the Mac is asleep or disconnected.
- **path:** pendant → mac-bridge → browser → relay → dashboard
- **model tier:** Use a cheap background model to compress and rank the handoff; use realtime only to answer the return utterance and read the brief.
- **latency:** Capture should complete within 2 seconds of the leave gesture or explicit phrase. On return, speak the brief within 3 seconds; workspace restoration may continue asynchronously with a receipt.
- **cost:** Low per handoff: one bounded summarization call over structured app/tab metadata, with most cost in occasional restoration actions rather than inference.
- **security:** Private tab titles, document names, and selected text must remain encrypted and short-lived by default; never capture passwords, page bodies, or microphone audio. Bind each capsule to the owner's device pair, redact sensitive domains, and make restoration limited to the exact recorded apps/tabs so an old handoff cannot open an unrelated session.
- **missing:** A device-pair handoff capsule protocol with encrypted, expiring snapshots and an explicit leave/return trigger; Mac read-only active-workspace capture plus typed restoration plans for apps, windows, files, and browser tabs; Browser extension support for tab/session metadata and stale-tab detection; Relay storage and delivery for handoffs while the Mac is offline, with one compact spoken re-entry receipt


## Changes it proposed to its own stack

### `integration` — Add a cross-surface connectivity-and-permission coordinator. The relay maintains a short-lived readiness lease for the Mac bridge and browser extension, while the Mac agent publishes structured blockers (Accessibility trusted=false, Screen Recording missing, browser offline, pending command count, last-seen age). Before dispatch, plans are classified as runnable, deferred, or impossible; deferred browser commands receive an expiry and are quarantined on reconnect rather than replayed blindly. The pendant gets a terse spoken status and the Mac dashboard gets a repair card with deep links/instructions for the missing permission. Reconcile on reconnect with idempotency keys and emit one receipt explaining what was skipped and why.
- **owner gets:** Today a request can appear to succeed while the Mac has no Accessibility/Screen Recording and the browser is offline (currently 3 commands are pending). The owner would know immediately whether work actually happened, avoid stale browser clicks firing hours later, and get a single next step instead of debugging disconnected surfaces.
- effort: Medium: readiness schema and lease in relay, dispatch middleware and expiry/reconciliation in Mac/browser bridges, dashboard card plus pendant status utterance; roughly 1–2 weeks including reconnect tests.  ·  risk: A false-negative lease could defer useful work; recover by allowing explicit retry and preserving the original plan. Reconnect races could duplicate an action; idempotency keys, per-command expiry, and receipts make replay visible. Permission instructions must never include secrets.
- cost: Negligible API cost (small structured heartbeats and receipts); modest D1/local persistence for leases and quarantined command metadata.  ·  latency: Adds under 100 ms for a cached readiness check; reconnect reconciliation is asynchronous.
- security: Improves safety by preventing stale offline browser commands from replaying; readiness data is operational metadata only and should omit URLs/tokens unless needed for a repair link.
- depends on: A shared typed plan/job idempotency contract across relay, Mac bridge, and browser bridge; Browser bridge heartbeat and command expiry support; Mac agent /ops/status surfaced as authenticated structured data; A dashboard/pendant path for degraded-mode notifications


## What it asked for

_Nothing._
## Its own summary

Discovered the newly granted inspection surface is still a stub, then verified live readiness through /ops/status. Mac bridge is online but Accessibility and Screen Recording are missing; browser is offline with 3 pending commands. Proposed a cross-surface readiness lease with expiry/quarantine/reconnect receipts, and a privacy-safe spoken “file this failure” bug-report workflow. Informed unified and recorded the finding.

**Biggest unknown:** Whether the owner wants the missing macOS permissions enabled now, and which implementation team owns the readiness lease plus the failure-envelope/redaction/outbox work.

