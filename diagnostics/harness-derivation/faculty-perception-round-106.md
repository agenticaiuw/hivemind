# Harness derivation — faculty-perception — round 106

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **current-system-truth** — At 2026-08-07T14:52Z, the Mac bridge and relay are reachable, but browser extension home-chrome is offline with 12 pending commands. /ops/status reports Calendar and Mail automation granted from cache while latest workday briefing says both need grants; these are contradictory and the briefing should not be treated as current authorization truth.
  - evidence: GET /ops/status HTTP 200 and GET /browser/status HTTP 200 and GET /briefing/latest HTTP 200 in Round 106.
- **current-system-truth** — The pipeline contains a stale-looking nRF9160 run with status processing and alert_delivered from pendant-offline-store, while the live device registry has no registered pendant; this is historical telemetry, not evidence of a connected pendant.
  - evidence: GET /pipeline Round 106 plus established live device table showing only home-macbook-bridge online and no pendant.

## Capabilities it proposed

### "Before you brief me or act, tell me what is genuinely live and trustworthy right now—what device is connected, whether my browser is reachable, which permissions are current, and which queued results are stale or contradictory."
- **useful because:** The system currently exposes mutually inconsistent truths: cached Mac grants conflict with the latest briefing, the browser is offline with 12 commands queued, and historical pendant telemetry looks like a processing run despite no pendant being registered. A short truth audit prevents the owner hearing a confident but false status and explains exactly what needs reconnecting or rechecking.
- **path:** relay-realtime → relay → mac-planner → browser-extension → dashboard-ux → pendant
- **model tier:** background / cheap model for reconciliation; realtime only speaks the final one-sentence result when asked
- **latency:** 5–15 seconds for an on-demand audit; no polling faster than each source's freshness budget
- **cost:** About $0.01–$0.05 per audit, dominated by reconciliation context; most inputs are small typed status JSON and should be cached
- **security:** Reads permission state, device presence, browser session metadata, and job summaries but not page contents or secrets. Redact URLs/tokens; never treat offline or historical telemetry as live. Require confirmation before draining queued browser commands or changing permissions.
- **missing:** A typed cross-surface truth ledger with source timestamps, TTLs, contradiction detection, and an explicit historical-vs-live classification; A relay endpoint that joins device registry and delivery acknowledgements with Mac /ops/status and browser status; A policy that suppresses stale briefing claims and labels uncertainty in spoken output

### "When you tell me something is done, connected, or safe, let me ask “why?” and get a compact evidence card showing what was observed, when, on which surface, what was only cached or historical, and any conflicting report—without exposing private page contents."
- **useful because:** Today the owner cannot distinguish a live observation from a stale briefing or historical pendant telemetry. An evidence card makes the assistant accountable: it can say “Chrome was last seen offline at 14:42; 12 commands remain; no pendant has registered” instead of presenting an unsupported status as fact. This is different from an action receipt: it explains the perception behind a claim, including contradictions and freshness.
- **path:** relay-realtime → unified → faculty-perception → faculty-judgement → dashboard-ux → relay → mac-planner → browser-extension → pendant
- **model tier:** Cheap background model to normalize and summarize structured evidence; realtime only handles the owner's short “why?” and reads the already-prepared card.
- **latency:** Under 2 seconds for a recent claim; up to 10 seconds when collecting fresh cross-surface observations. No page-content fetch unless explicitly requested.
- **cost:** About $0.005–$0.03 per card; dominated by optional reconciliation, with most cards generated from compact cached status records.
- **security:** Evidence must contain statuses, timestamps, source IDs, and hashes—not page text, cookies, bearer tokens, or secret values. Redact URLs and sensitive metadata. Cards are read-only and must never trigger queued commands or permission changes.
- **missing:** A claim/evidence-ID contract linking every spoken assertion to its source observations; A durable evidence store with retention, freshness TTLs, contradiction edges, and historical-vs-live classification; A relay endpoint to retrieve a card from the pendant or voice session and a dashboard renderer with expandable provenance; Planner/TTS policy that declines definitive wording when the evidence card is contradictory or expired


## Changes it proposed to its own stack

### `context` — Add a read-only Truth Reconciler between source routes and spoken briefings. For each claim (device online, browser reachable, permission granted, job complete), retain source, observedAt, freshness TTL, and evidence class (live, cached, historical). When sources disagree—such as /ops/status grant cache versus /briefing/latest's missing-grant note—emit a contradiction object, downgrade confidence, and prevent the claim from entering a definitive spoken sentence. Historical pipeline events must never satisfy a live pendant-presence predicate. Expose a compact /truth/snapshot for judgement and dashboard display.
- **owner gets:** The owner stops receiving polished but wrong answers and gets a plain explanation like “Chrome is offline; 12 commands are waiting; Calendar permission has conflicting reports, so I did not claim it is readable.”
- effort: Medium: schema plus source adapters, TTL policy, and briefing/planner integration; no new hardware required.  ·  risk: Over-quarantining could make the assistant too cautious or surface harmless cache differences. Recover with source-specific TTLs, explicit 'last known' wording, and an owner-visible evidence drill-down.
- cost: Negligible runtime cost; a few hundred bytes of structured state per source and one cheap reconciliation call when claims are assembled.  ·  latency: Adds roughly 50–300 ms for local joins; background reconciliation can be cached.
- security: Improves security by preventing stale authorization claims. Store hashes and statuses rather than page contents; keep bearer tokens and private URLs out of the snapshot.
- depends on: A typed source-status schema and freshness policy; Briefing generation consuming /truth/snapshot instead of raw cached permission strings; Relay device registry exposing authoritative registration and delivery timestamps

### `browser-harness` — Implement an offline-command quarantine: when the browser heartbeat goes offline, stop presenting pending commands as runnable, attach an expiry and originating request/session to each queued item, and require a fresh heartbeat plus tab/session revalidation before release. Mark the existing 12 home-chrome commands as quarantined rather than silently replaying them after reconnect; provide a single 'discard stale / review individually / release safe reads' decision.
- **owner gets:** If Chrome reconnects after hours or a tab changes, the assistant will not unexpectedly click or submit old requests. The owner gets a clear queue they can safely review instead of a misleading 'browser ready' state.
- effort: Medium: queue state transition, heartbeat gate, expiry metadata, dashboard controls, and relay acknowledgement.  ·  risk: Legitimate long-running reads may expire. Preserve them for review with their original intent and never auto-execute after expiry; safe release can be manually selected.
- cost: Minimal storage and no model call for the gate; one cheap reconciliation only when reviewing ambiguous items.  ·  latency: Reconnect adds one heartbeat/session validation round trip, typically under 1 second.
- security: Reduces replay and stale-tab risks; do not retain page contents in queue metadata, only request IDs, session IDs, action class, and timestamps.
- depends on: Reliable browser command queue with request IDs and tab/session affinity; Browser heartbeat status and authenticated session registry; Dashboard review controls for queued commands


## What it asked for

_Nothing._
## Its own summary

Established a new perception failure: live status and generated briefings disagree on Calendar/Mail permissions; Chrome is offline with 12 queued commands; historical nRF9160 pipeline telemetry is being retained as processing despite no pendant registered. Recorded these facts, notified judgement, and proposed a truth reconciler plus offline browser-command quarantine.

**Biggest unknown:** Authoritative relay device registration/delivery acknowledgements and the policy for resolving conflicting cached versus live permission claims.

