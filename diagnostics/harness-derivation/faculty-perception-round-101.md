# Harness derivation — faculty-perception — round 101

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live browser bridge state** — At 2026-08-07T14:33Z, home-chrome is offline with no tab/window and 10 pending commands; browser actions cannot currently run.
  - evidence: GET /browser/status returned online:false, tabId:null, tabCount:null, pendingCommands:10; GET /ops/snapshot matched this.
- **live Mac automation reachability** — At 2026-08-07T14:33Z, Mac bridge is online and relay reachable, but Accessibility and Screen Recording are not granted; automation grants are cached for listed apps and permissions.ready=false.
  - evidence: GET /ops/snapshot status.agent.permissions: accessibility.trusted=false, screenRecording.granted=false, automation entries granted=true, ready=false; relay.macBridgeOnline=true.
- **latest stored workday brief** — The latest workday brief (2026-08-07 11:30Z) says no files changed; calendar and mail were not read because they need an Automation grant, and nothing was sent.
  - evidence: GET /briefing/latest returned generatedAt 2026-08-07T11:30:00Z with sections Files touched: Nothing changed; Not read: calendar/mail need Automation grant; sent:false.
- **input action trustworthiness** — At 2026-08-07T14:34Z, synthesized UI events from com.aipendant.agent are rejected; inputReachability failed and uiActionsWillReachTheScreen=false. UI action receipts must not be treated as proof of effect.
  - evidence: GET /observe returned accessibility.trusted=false, eventsPost=false, inputReachability.status=failed, uiActionsWillReachTheScreen=false, consequence stating ui_click/type_text/press_keys may report success while doing nothing.
- **browser observation contradiction** — The read-only observer still lists 3 durable browser sessions with stale tabs (last used 05:40–06:26Z), while the live browser bridge reports offline with no current tab; these sessions are not evidence of live browser reachability.
  - evidence: GET /observe browser.sessions=3 with stale tab timestamps; GET /browser/status online=false, tabId=null, tabCount=null.
- **reachable device inventory** — Current device discovery shows only home-macbook-bridge online; home-chrome and cloudflare-contract-test are offline. No pendant device appears in the reachable inventory.
  - evidence: discover(devices) returned home-macbook-bridge online, home-chrome offline, cloudflare-contract-test offline; no nRF9160/pendant entry.

## Capabilities it proposed

### "Before you act, tell me whether each route to me is actually reachable right now—and if not, what evidence proves why."
- **useful because:** The system currently has stale browser tabs, an offline extension, missing UI permissions, and historical pendant pipeline records that can look live. A concise reachability verdict prevents the owner from believing an action happened when it could only have produced a receipt. It is useful for deciding whether to wait, switch surfaces, or fix one concrete dependency.
- **path:** relay-realtime → mac-planner → browser-extension → mac-vision → faculty-perception → faculty-judgement → faculty-action
- **model tier:** deterministic first: faculty-perception gathers /ops/snapshot, /observe, /browser/status, relay/device registry and latest pipeline timestamps; background model only summarizes contradictory evidence into one short spoken report. Realtime is unnecessary unless the owner is actively asking.
- **latency:** Under 2 seconds for local checks; under 5 seconds if relay/device freshness must be fetched. Never claim reachable from a stale session or historical pipeline event.
- **cost:** Usually $0 model cost for typed checks; roughly 2–4k background tokens only when contradictions need narration. Dominant cost is relay round-trip, not inference.
- **security:** Expose only capability names, freshness, and failure reasons—not URLs, page contents, account data, or secret memory. Treat stale success receipts as untrusted. Ask confirmation before any recovery action such as enabling an extension or retrying a write.
- **missing:** A relay route that returns the authoritative registered-device status and last delivery acknowledgement to the Mac agent; A shared freshness/contradiction schema so /observe and /browser/status cannot be merged as if equally live; A deterministic pre-action gate consumed by faculty-judgement/action (read-only; it must not silently block)

### "I was away while the assistant was disconnected—what did it try, what never ran, what is still queued, and what needs me to retry? Reconcile it without repeating any action."
- **useful because:** The owner currently has offline browser commands, failed jobs, stale tabs, and historical pipeline events spread across separate stores. They cannot safely tell whether an instruction was skipped, failed before changing anything, or is awaiting a surface. A bounded reconciliation prevents duplicate sends, retries, or false confidence when they return.
- **path:** relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement → faculty-action → unified
- **model tier:** Deterministic event and receipt reconciliation first; use a cheap background model only to compress the resulting state into the owner's preferred one-sentence spoken summary. Realtime is unnecessary unless the owner asks live.
- **latency:** Under 3 seconds from local job/pipeline/browser stores; explicitly label any relay state older than its freshness window. Never auto-retry during reconciliation.
- **cost:** No model cost for typed reconciliation; approximately 1–3k background tokens only for natural-language compression. Storage/indexing is the main implementation cost.
- **security:** Show only the minimum command labels and effect states; redact page content, URLs, message bodies, and secrets. Treat all writes as potentially duplicated until an idempotency key and receipt prove otherwise. Require explicit confirmation for any retry or cancellation.
- **missing:** A durable cross-store event index joining relay job IDs, local job IDs, pipeline IDs, browser command IDs, and action receipt IDs; A formal effect-state vocabulary distinguishing not-started, queued, running, failed-before-effect, completed, unknown, and expired; Stable idempotency keys propagated from spoken request through Mac, browser, and relay layers; A reconciliation endpoint that can cite evidence and freshness without executing actions


## Changes it proposed to its own stack

### `context` — Add a read-only Perception Evidence Ledger that normalizes every surface observation into {surface, capability, observedAt, freshnessDeadline, status, evidenceRefs, contradictions}. It must explicitly downgrade historical pipeline claims such as “the nRF9160 can now download” when the live device registry has no pendant, and mark browser sessions stale when /browser/status is offline. Faculty-judgement reads this ledger; faculty-action receives the verdict and evidence IDs, never raw optimistic receipts.
- **owner gets:** You get an honest answer about what the assistant can reach and what really happened, instead of a green-looking receipt for an action that could not touch the screen or a response waiting for a device that is not connected.
- effort: Medium: typed schema, freshness rules, adapters for existing observation routes, and tests for the two observed contradictions; no new model required.  ·  risk: A bad freshness threshold could produce false “stale” warnings or hide a briefly disconnected device. Recover with conservative defaults, visible evidence timestamps, and never deleting raw observations.
- cost: Negligible storage and CPU; deterministic processing. Optional short background narration costs a few thousand tokens only when the owner asks.  ·  latency: Adds tens of milliseconds for local aggregation; relay registry check may add up to one round trip.
- security: Ledger must redact URLs, page text, and secrets; persist only capability-level facts and opaque evidence references.
- depends on: Authoritative relay device registry and delivery-acknowledgment route (currently missing); Shared typed freshness/contradiction schema; Faculty-judgement/action integration to consume evidence verdicts


## What it asked for

_Nothing._
## Its own summary

Round 101 established and recorded four current facts: only the Mac bridge is online (no pendant in device inventory); the browser bridge is offline with 10 queued commands despite three stale durable tabs; UI input from com.aipendant.agent is not reaching the screen because Accessibility/Screen Recording are missing; and the latest brief could not read calendar/mail and sent nothing. I also established that historical pipeline claims must not be treated as live device delivery. I proposed an evidence ledger that joins /observe, /ops/snapshot, /browser/status, /pipeline, and relay state with freshness and contradiction markers, then informed judgement/action/unified.

**Biggest unknown:** I still need an authoritative relay endpoint for registered pendant presence plus per-response delivery/playback acknowledgements, and a shared freshness/contradiction contract consumed by judgement/action. Without those, I can prove local reachability failures but cannot prove whether a relay-accepted response was ever delivered or heard by a real pendant.

