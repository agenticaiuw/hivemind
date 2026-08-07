# Harness derivation — browser-extension — round 116

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-bridge-health** — The live browser status is offline with 12 pending commands and only an unreported home-chrome device, while the session store still contains three historical tabs. Treat sessions as stale and do not replay until a real Safari heartbeat/device identity returns.
  - evidence: GET /browser/status 200: online false, home-chrome offline, pendingCommands 12; GET /browser/sessions 200: default/probe-form/probe-form2 historical sessions.

## Capabilities it proposed

### "Reconnect my private browser, but do not replay anything stale; once it is really online, tell me what is waiting and let me ask you to continue."
- **useful because:** Today the owner can ask to launch the bridge, yet the bridge can be offline with a backlog and historical tabs that look usable. This gives a safe, useful recovery path for the one surface that can reach logged-in sites: revive the Mac bridge, verify a fresh Safari heartbeat, quarantine old commands, and report a truthful queue summary to the pendant before any page action.
- **path:** pendant → mac-planner → mac-vision → browser-extension → relay-realtime
- **model tier:** Use the cheap background/router tier for heartbeat polling, stale-command classification, and queue summarization; use realtime only to speak the one-sentence status and interpret a follow-up such as 'continue the newest one'.
- **latency:** Initial bridge launch and heartbeat: up to 15 seconds; queue inspection: under 2 seconds after heartbeat. Never wait on a browser command while claiming recovery succeeded.
- **cost:** About $0.001–$0.01 per recovery, dominated by one planner decision and optional Mac app launch; heartbeat/status calls are negligible.
- **security:** Do not expose page text or cookies during recovery. Persist command IDs, enqueue time, originating request, and age only. Mark pre-heartbeat commands stale/quarantined rather than replaying them; continuing one requires the owner's explicit follow-up. Never submit forms, send mail, or purchase as part of recovery.
- **missing:** A Mac action that can reliably launch or foreground the bridge app and report its process/extension readiness; A durable pending-command quarantine with age/lease metadata and an explicit continue operation; A device identity handshake that distinguishes real Safari from the never-seen home-chrome registration; A small recovery orchestrator joining Mac launch, /browser/heartbeat, /browser/status, and queue summary

### "When I walk away from my Mac, automatically protect my logged-in browser: hide sensitive pages and pause browser automation; when I return, restore my session and tell me what was paused."
- **useful because:** The pendant is the one device that can know whether the owner is physically present. Today an authenticated Safari session can remain visible and queued browser actions can continue while the owner is away. Presence-bound browser privacy would protect private work without requiring the owner to remember to lock every tab, while preserving continuity when they return.
- **path:** pendant → browser-extension → mac-planner → relay-realtime
- **model tier:** No expensive model for the security transition: pendant firmware and the extension handle presence and pause/resume deterministically. Use a cheap background model only to summarize paused work when the owner returns; use realtime only for the brief spoken alert.
- **latency:** Lock/hide within 1 second of confirmed departure; resume only after 2–5 seconds of stable return presence to avoid radio flapping. Spoken status in under 2 seconds after reconnection.
- **cost:** Negligible API cost during presence transitions; roughly $0.001 or less for an optional return summary. Main cost is firmware/extension integration and testing across sleep, Bluetooth loss, and Safari crashes.
- **security:** Presence must be cryptographically bound to this pendant, not inferred from Wi-Fi or an arbitrary nearby device. Never transmit page contents to the relay for this feature. On departure, cancel or pause queued browser commands before hiding tabs; do not silently resume irreversible actions. Keep only event timestamps, affected tab IDs, and command IDs. Provide a physical pendant override and a clear return report.
- **missing:** A low-latency authenticated pendant-presence signal exposed to the Mac bridge; Safari extension support for an immediate privacy action (hide/lock selected tabs or window) and command-pause acknowledgement; A cross-surface presence lease with fail-closed expiry and explicit resume state; A small local policy store mapping sites/tabs to sensitive or ordinary protection classes

### "What was that private page I looked at yesterday? Search my recent browser history by what was on the page, not just its URL, and read me the best matches with links."
- **useful because:** The browser can reach the owner's logged-in pages, but today that knowledge disappears after a read and the owner cannot search yesterday's private research by remembered words or topic. A local semantic index would make the browser a durable personal memory without sending page contents to a cloud model.
- **path:** browser-extension → mac-planner → mac-terminal → relay-realtime → pendant
- **model tier:** Use a local embedding/indexing process on the Mac for ingestion and retrieval; use the cheap background tier to rank a handful of local matches and realtime only to speak the concise answer. Do not use the expensive realtime model for indexing.
- **latency:** Index each visited/read page asynchronously in under 3 seconds; return top matches in under 2 seconds for a normal query. If indexing is incomplete, state the coverage window rather than pretending history is complete.
- **cost:** Near-zero recurring API cost if embeddings and search stay local; modest Mac CPU/storage use. Optional cloud reranking would cost under $0.01 per query but should be off by default.
- **security:** Page text, titles, and URLs remain encrypted on the Mac and never enter relay logs by default. Respect per-site exclusions, incognito/private windows, secret-field redaction, retention limits, and a physical pendant command to erase the index. Spoken results should avoid quoting sensitive content unless the owner asks for detail.
- **missing:** A Safari extension event/read hook that captures page title, URL, selected semantic text, and timestamp without requiring an active agent request; An encrypted local full-text/embedding index with retention and per-domain exclusion controls; A query route that searches the local index and returns provenance (URL, timestamp, matched passage) to the planner; A pendant-friendly privacy control for pause, inspect, and erase


## Changes it proposed to its own stack

### `browser-harness` — Implement a browser-bridge recovery state machine: on a recovery request, snapshot pending command IDs and ages, mark all pre-recovery items quarantined with a lease (no deletion/no replay), ask the Mac bridge to foreground/launch Safari extension, require a fresh device-scoped heartbeat with tab inventory, then expose a read-only queue report and an explicit continue(commandId) path. Expire the quarantine lease without replay if heartbeat disappears.
- **owner gets:** When the browser is disconnected, the owner gets an honest 'reconnected / still offline / N items waiting' answer instead of a timeout or accidental execution of an old click or form fill.
- effort: Medium: local-agent queue metadata and state machine, Mac bridge readiness result, and one status/report route; add crash-recovery tests for duplicate heartbeats and stale commands.  ·  risk: A process crash could leave items quarantined; recover by preserving the ledger and offering explicit continue or discard. A false-ready heartbeat could still mislead, so require extension version, device ID, tab count, and monotonic heartbeat age.
- cost: Negligible storage (a few hundred bytes per command) and HTTP calls; no model cost unless the owner asks for a spoken summary.  ·  latency: Adds 1–3 seconds for fresh-heartbeat verification; avoids 45-second browser action timeouts when offline.
- security: Improves safety by preventing silent replay and keeping page contents out of recovery logs; device-scoped identity reduces cross-browser command leakage.
- depends on: Mac bridge open_app/readiness result; durable pending-command lease/quarantine metadata; fresh Safari extension heartbeat carrying stable device identity


## What it asked for

_Nothing._
