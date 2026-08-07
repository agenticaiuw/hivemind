# Harness derivation — mac-planner — round 85

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-read-tools** — The newly granted mac_readonly_inspect and mac_read_sources tools are not implemented in this environment; both return an explicit schema-but-no-implementation error. AppleScript automation is granted for Calendar, Mail, Safari, Chrome, Finder, System Events, and other apps, so a bounded adapter is feasible without Accessibility.
  - evidence: Direct calls to mac_readonly_inspect foreground_app/running_apps/browser_tabs and mac_read_sources calendar_today/mail_unread returned the same implementation error; GET /ops/status reports automation grants true and Accessibility/Screen Recording false.
- **browser-reconnect-risk** — Browser bridge is offline with five pending commands; status reports home-chrome last seen and offline. Commands must be fenced by extension/session epoch and quarantined on reconnect rather than replayed.
  - evidence: GET /browser/status and GET /ops/status both report online=false and pendingCommands=5; peer browser-extension observed a command repeatedly claimed while offline.

## Capabilities it proposed

### "“I’m stepping away—save where I am. When I come back, put me back into this work and tell me the next three things.”"
- **useful because:** A durable work-state checkpoint prevents losing the thread across a Mac, authenticated browser tabs, and the pendant. It is different from a morning brief: it captures the exact interrupted task, marks browser data as fresh or stale, and can restore the reversible desktop state later without pretending that a disconnected browser was inspected.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Relay text model for checkpoint normalization and resume ranking; no realtime model unless the owner asks by voice. Use a cheap background model for extracting a compact task capsule; deterministic AppleScript and route handlers collect state.
- **latency:** Tap acknowledgement under 300 ms from pendant/relay; checkpoint completion 3–8 s in the background. Resume should acknowledge immediately, then reopen apps/URLs and speak the ranked next steps within 5 s.
- **cost:** About $0.001–$0.01 per checkpoint/resume depending on model tokens; most cost is optional summarization, not collection. Storage is a small encrypted JSON capsule plus hashes, not page bodies by default.
- **security:** Capsules may contain private app names, URLs, calendar subjects, and authenticated-tab identifiers. Store redacted metadata by default, encrypt at rest, bind browser facts to extension device/session and freshness epoch, and never replay stale queued browser commands. Reopening a URL is reversible; sending/submitting anything is out of scope and must never be inferred from resume.
- **missing:** A real implementation of the newly granted mac_readonly_inspect and mac_read_sources tools (currently they return 'schema but no implementation') or an equivalent bounded AppleScript read adapter; A pendant double-tap/offline checkpoint event and reconnect-safe relay ingestion; A browser lease/epoch fence and stale-command quarantine; browser is currently offline with 5 pending commands; A compact capsule schema with per-fact timestamp, source, sensitivity, and expiry; A deterministic resume executor that can reopen apps/URLs and report receipts without Accessibility

### "“Before I leave for an appointment, check my private calendar, recent mail, and logged-in reservation pages against each other; tell me only if the details conflict, and prepare a corrected itinerary I can review.”"
- **useful because:** Today the surfaces can produce separate calendar/mail/browser summaries, but the owner cannot get a single, provenance-linked contradiction check: time-zone drift, changed address, duplicate booking, missing confirmation, or a cancellation that disagrees across sources. The useful result is an exception-only alert with the exact conflicting evidence and a reviewable itinerary, not another generic briefing.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use a cheap background model for entity matching and conflict classification; reserve realtime only to speak the already-computed exception when the owner asks. Deterministic parsers should normalize dates, locations, confirmation numbers, and cancellation states before model judgment.
- **latency:** On-demand request: 5–15 seconds for Calendar/Mail plus authenticated tabs, with a fast spoken acknowledgement. A scheduled pre-departure check can run in the background; no polling alert should fire when normalized facts are unchanged.
- **cost:** Roughly $0.005–$0.03 per appointment check, dominated by browser extraction and model reconciliation; store compact evidence hashes/snippets rather than full page bodies. No cost for unchanged scheduled checks if fingerprints match.
- **security:** This combines highly sensitive calendar, mail, and logged-in reservation data. Scope by the single upcoming appointment, redact unrelated messages and account identifiers, retain source URLs/snippet hashes with short TTL, and require explicit review before creating or changing any itinerary, reminder, booking, or message. Never submit reservations or send mail.
- **missing:** A cross-source normalization and contradiction engine with typed fields, confidence, and source timestamps; A scheduler keyed to the next appointment plus quiet-hours and travel-time policy; Authenticated browser extraction that is session-bound and safe after reconnect; offline tabs must be reported as unavailable, not treated as empty; A reviewable itinerary artifact in the dashboard and a relay speech path that cites each conflict; Owner-configurable definitions of meaningful conflict (time, timezone, address, cancellation, attendee, reservation status)


## Changes it proposed to its own stack

### `integration` — Implement the granted mac_readonly_inspect and mac_read_sources tools in the local agent as bounded, redacted adapters. Use AppleScript/JXA through the already-granted per-app automation permissions for foreground/running apps, Safari/Chrome tab metadata, Calendar, and Mail; return typed records with timestamps and source app. Add a capability/status field so callers can distinguish implemented, unavailable, and permission-denied instead of receiving a generic tool error.
- **owner gets:** The owner can ask for a truthful work brief or resume a task without the agent guessing from stale machine-context data. It also lets the pendant hear what is actually open while the owner is away, without screen recording or Accessibility.
- effort: Medium: local-agent route handlers, allowlisted scripts, redaction tests, timeout handling, and contract tests for empty/denied accounts. No model work required.  ·  risk: AppleScript can expose sensitive subject lines or URLs; default to metadata/snippets and redact bodies. A hung app can block collection, so enforce per-source timeouts and return partial results. Recovery is retrying one source; never mutate apps in these handlers.
- cost: Negligible API cost; local CPU only. A few hundred bytes to a few KB per query, depending on tab/mail counts.  ·  latency: Roughly 0.2–2 s for app/tab metadata and 1–4 s for Calendar/Mail, with parallel collection and hard timeouts.
- security: Read-only allowlists, account_scope validation, body exclusion by default, URL/query redaction, and audit receipts. No Accessibility or Screen Recording grant is needed for the initial implementation.
- depends on: The local agent's existing AppleScript automation grant cache; A documented response schema for mac_readonly_inspect/mac_read_sources; Browser lease/epoch fencing before authenticated tab data is trusted

### `browser-harness` — Add reconnect fencing for the browser bridge: every heartbeat issues a device epoch and lease token; poll claims must include that epoch; commands claimed by an offline or expired extension are quarantined, never replayed automatically, and require explicit reattachment to the same session/tab before retry. Expose pending, quarantined, expired, and replayed counts in /browser/status and dashboard.
- **owner gets:** The owner will not accidentally navigate or submit an old command when Chrome reconnects after sleep, a crash, or extension replacement. Today the bridge is offline while five commands remain pending and one has been repeatedly claimed, so reconnect behavior is unsafe and opaque.
- effort: Medium: schema fields and atomic claim/update logic in browser queue, heartbeat/poll/result validation, migration for existing pending records, and dashboard state labels.  ·  risk: A legitimate command may be quarantined and need retry. Provide a one-click or spoken 'reattach this browser session' operation, preserve the command and reason, and never delete it silently.
- cost: Tiny D1 read/write increase per heartbeat and command claim; no model calls.  ·  latency: Adds one token/epoch validation per poll/result, normally sub-10 ms; reconnect may take one heartbeat before work resumes.
- security: Improves session binding and prevents cross-device replay. Store only hashes of lease tokens in D1; invalidate all leases on extension identity change or prolonged offline interval.
- depends on: Existing GET /browser/status; GET /browser/heartbeat; GET /browser/poll; POST /browser/result/:commandId; POST /browser/sessions; The command queue and browser session records already identified by chg-14accc01


## What it asked for

_Nothing._
## Its own summary

Round 85 produced two concrete additions: (1) a cross-surface “save where I am / resume this task” capability using pendant→relay→Mac→browser state, with explicit freshness and no action replay; (2) implementation of the granted but currently nonfunctional read-only Mac inspection/source tools. I also proposed browser lease/epoch fencing because the live bridge is offline with 5 pending commands and stale claims. Current Mac status: relay and Mac bridge reachable, full-control mode on, AppleScript automation broadly granted, but Accessibility and Screen Recording are unavailable; browser extension is offline.

**Biggest unknown:** Whether the orchestrator will implement the two read-only tools and browser fencing, and what exact pendant event/API will represent an offline-safe checkpoint. Until then I cannot truthfully inspect foreground apps, tabs, Calendar, or Mail through the newly granted tool surfaces.

