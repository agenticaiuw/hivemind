# Harness derivation — mac-planner — round 72

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-planner live cross-surface readiness** — Relay and Mac bridge are reachable, but browser extension is offline with 4 pending commands; Mac FULL_CONTROL_MODE is enabled yet Accessibility trusted=false and Screen Recording granted=false. mac_read_sources and mac_readonly_inspect are exposed as tools but have no implementation.
  - evidence: GET /ops/status returned relay reachable/macBridgeOnline true, browser online false, permissions accessibility trusted false and screenRecording granted false; GET /browser/status returned online false and pendingCommands 4; both newly granted read tools returned 'schema but has no implementation yet'.

## Capabilities it proposed

### "When a meeting is 10 minutes away, get me ready: summarize the event and relevant mail, gather context from my already-open work tabs, save what I was doing, and after it ends restore my workspace and give me the follow-ups."
- **useful because:** This is a real cross-device transition rather than a Mac-only macro: the pendant/relay can notify at the right moment, Calendar/Mail provide personal context, the browser contributes authenticated portal context, and the Mac preserves/restores the exact working set. It prevents lost context before meetings and turns the return to work into a deliberate handoff.
- **path:** relay-realtime → mac-planner → browser-extension → unified → faculty-perception → faculty-judgement → faculty-action → dashboard
- **model tier:** Background/cheap model for scheduled detection, deduplication, and first-pass extraction; realtime model only for the pendant's brief spoken alert and follow-up questions. Escalate to realtime if the owner asks for an interactive briefing.
- **latency:** Schedule tick within 30 seconds of the 10-minute window; prepare in under 20 seconds using bounded Calendar/Mail and up to 4 already-open tabs. Restore workspace in under 10 seconds after the owner confirms they are back.
- **cost:** Roughly $0.01–$0.05 per meeting, dominated by model summarization of mail/tab excerpts; scheduling and state capture are near-zero. No model call if there is no upcoming event or no changed context.
- **security:** Only read the selected calendar event, bounded mail snippets, and explicitly already-open browser tabs; do not search the whole browser or upload credentials. Redact secrets and keep citations locally. Saving/restoring windows and opening tabs is reversible, but sending messages or creating commitments requires an explicit owner instruction. The owner should be able to disable monitoring or exclude calendars/tabs.
- **missing:** A real implementation for mac_read_sources and mac_readonly_inspect (both currently return no implementation yet); Browser endpoint that returns bounded, cited text from already-open authenticated tabs plus stable tab/session IDs; A durable meeting-transition job with idempotency, deadline scheduling, and a workspace snapshot/restore store; Pendant event and relay delivery for a scheduled, non-microphone alert; A structured evidence ledger linking each summary claim to its source and recording restore success/failure; Dashboard controls for calendar scope, tab allowlist, lead time, retention, and pause

### "If I lose connection, quit the wrong app, or a browser form is about to disappear, warn me and save a private recovery capsule so I can say 'restore what I was doing' from the pendant later."
- **useful because:** Today the Mac, browser, and pendant do not share a loss-aware safety net. This would protect unfinished work across app boundaries: a draft in a browser, an unsaved document, and the surrounding task context could be recovered without the owner remembering filenames, URLs, or which window mattered.
- **path:** mac-vision → mac-planner → browser-extension → relay-realtime → unified → faculty-perception → faculty-judgement → faculty-action → dashboard
- **model tier:** Use deterministic local watchers and a small background model only to label task context and rank recovery candidates. Use the realtime model solely when the owner asks the pendant to locate or restore a capsule; never run realtime continuously as a monitor.
- **latency:** Local change detection under 1 second; warning within 2 seconds of a risky disappearance. Capsule lookup under 5 seconds and restoration under 10 seconds, with a compact spoken result.
- **cost:** Near-zero for detection and encrypted local snapshots; approximately $0.005–$0.02 only when the owner asks for semantic recovery across several capsules. Storage and model costs are bounded by age/size quotas.
- **security:** Never upload raw keystrokes, passwords, cookies, or full sensitive documents. Capture only app identity, file path, tab/session identifier, redacted title, and explicit draft snapshots from allowlisted apps/sites. Keep raw capsules encrypted on the Mac, send the relay opaque IDs plus summaries, and require an explicit restore request before reopening or replacing anything.
- **missing:** A Mac event/watch layer that detects app/window disappearance and unsaved-document state without scraping keystrokes; A browser extension protocol for encrypted, opt-in draft checkpoints and stable form/session identifiers; A local encrypted capsule store with quotas, expiration, deduplication, and crash-safe writes; Relay APIs for capsule indexing, pendant lookup, and reconnect-safe delivery; A restore executor that can recreate tabs/files while reporting exact postconditions and conflicts; Owner controls for per-app/site inclusion, retention, and a hardware-level pause switch


## Changes it proposed to its own stack

### `integration` — Add a MeetingContextCapsule service spanning relay, Mac, and browser: at a scheduled boundary it creates a versioned, content-addressed snapshot containing the selected event ID, redacted mail/tab citations, open-window/tab identifiers, and focused document metadata; it exposes prepare, handoff, restore, and expire operations with idempotency keys. Restore must verify postconditions (expected app/tab/document present) and return a partial-success receipt rather than silently claiming success.
- **owner gets:** The owner can leave for a meeting and come back to the same work with a trustworthy, short handoff. If the Mac reconnects late or a tab disappeared, they see exactly what was restored and what needs attention instead of losing their place or receiving a fabricated 'done'.
- effort: Medium-high: shared schema and durable store, Mac window/tab snapshot adapter, browser tab identity adapter, scheduler integration, and tests for disconnects, duplicate triggers, and partial restore.  ·  risk: Window restoration can disrupt an active workflow or reopen sensitive tabs. Default to restoring only the captured app/tab set and never closing unrelated work; expire capsules after a short retention period. If restore fails, preserve the capsule and present a manual recovery list.
- cost: Small storage and one background summarization call per prepared meeting; no additional realtime calls unless the owner asks to hear it. Implementation cost is primarily integration and reliability testing.  ·  latency: Snapshot capture should be under 2 seconds; preparation is bounded by source reads and should complete within 20 seconds; restore is parallelized and should complete within 10 seconds.
- security: Keep raw content on the Mac where possible; relay receives only redacted excerpts and opaque citations. Encrypt capsules at rest, scope them to the owner's account, and provide immediate delete/pause controls. Never include passwords, cookies, or full page dumps.
- depends on: Implement mac_read_sources and mac_readonly_inspect rather than schema-only stubs; Stable browser tab/session IDs with bounded authenticated page reads; Durable scheduler and idempotent job execution; Postcondition/evidence receipt contract across Mac and relay

### `dashboard-ux` — Add a live cross-surface readiness panel and preflight API for any planned desktop routine. It should show relay, Mac, browser, Calendar/Mail, Accessibility, and Screen Recording states; classify a plan as ready, degraded, or blocked; list exactly which steps will be skipped; and automatically requeue only the missing browser/read-source steps when their heartbeat returns. Do not fabricate completion from a partial run.
- **owner gets:** Before asking the pendant to prepare a meeting or act on a portal, the owner can see whether it can actually reach the required context. A disconnected browser or missing permission becomes an honest, actionable warning instead of a long failed action and a misleading summary.
- effort: Medium: health aggregation, plan dependency declarations, UI status card, and reconnect-aware retry tests.  ·  risk: Health checks may expose app names, URLs, or account scopes on the dashboard. Redact URLs/titles by default and show details only on demand; cap retries to prevent repeated actions when a bridge reconnects.
- cost: Negligible runtime cost; one small health poll on dashboard open and no model call.  ·  latency: Preflight under 500 ms locally; retries begin on heartbeat rather than polling aggressively.
- security: Readiness metadata must be scoped to the owner and must not include cookies or page content. Treat permission state as sensitive local telemetry.
- depends on: Implementations for mac_read_sources and mac_readonly_inspect; Browser heartbeat with pending-command reconciliation; Plan dependency metadata and idempotent retry keys

### `integration` — Create a crash-safe, privacy-preserving Recovery Capsule protocol: Mac and browser producers write encrypted local checkpoints using a common manifest (producer, timestamp, app/tab identity, content class, redaction status, checksum, expiry); the relay stores only opaque capsule IDs and redacted indexes. A two-phase restore API must first return a dry-run conflict report, then apply only the requested capsule and emit per-artifact postconditions.
- **owner gets:** A dropped connection or accidental close would stop being a permanent loss. The owner could recover a specific unfinished task from the pendant without handing the service passwords or silently overwriting newer work.
- effort: High: OS/app event adapters, browser draft checkpointing, encrypted local storage, relay index/TTL handling, conflict detection, and recovery tests across crashes and reconnects.  ·  risk: A faulty checkpoint could preserve stale or sensitive content, and a restore could overwrite newer work. Use immutable capsules, short retention, checksums, explicit conflict reports, and never overwrite by default; if a producer cannot prove its snapshot is complete, mark it incomplete rather than restoring it.
- cost: Low ongoing API cost; storage is local-first. Engineering cost is substantial because each app/browser form has different save semantics.  ·  latency: Checkpoint writes must be asynchronous and non-blocking; restore adds one local verification pass and should remain under 10 seconds for a bounded capsule.
- security: This is a new sensitive-data surface. Encrypt at rest with a device-bound key, keep raw payloads off the relay, redact before indexing, support immediate purge, and log access without logging payloads.
- depends on: Mac app/window and document lifecycle events; Browser extension draft checkpoint API with explicit site allowlists; Durable encrypted local storage and relay opaque-index endpoints; Typed restore executor with dry-run conflict reporting


## What it asked for

_Nothing._
## Its own summary

Discovered the new grants are present only as schemas: mac_readonly_inspect and mac_read_sources both return 'no implementation yet'. Live status shows relay/Mac bridge reachable, browser offline with 4 pending commands, Accessibility untrusted, and Screen Recording missing. Proposed a cross-device MeetingContextCapsule (scheduled pendant alert, bounded Calendar/Mail + open-tab context, workspace snapshot/restore with postcondition receipts) and a readiness/preflight dashboard that honestly reports degraded dependencies and reconnects idempotently.

**Biggest unknown:** Whether the owner wants to enable Mac Accessibility/Screen Recording and bring the browser extension online; without those, authenticated tab context and reliable workspace inspection cannot be delivered.

