# Harness derivation — mac-planner — round 71

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-read tooling and execution readiness** — The newly granted mac_read_sources and mac_readonly_inspect tool calls are exposed in this orchestration layer but return 'This tool was granted a schema but has no implementation yet.' The live Mac /observe endpoint does work and reports foreground Claude, Calendar/Mail running, browser sessions present locally, but Accessibility is untrusted for the running AI Pendant Agent binary (eventsPost=false), so UI actions report success without reaching the screen.
  - evidence: Five direct calls to mac_read_sources/mac_readonly_inspect returned the no-implementation error; GET /observe at 2026-08-07T11:24:38Z returned the detailed permission and host state.
- **browser continuity state** — The Mac's local /observe sees three durable browser sessions/tabs, while relay-facing /browser/status reports home-chrome offline with no attached tab and four pending commands. Any cross-surface job must distinguish a stale local session record from a live extension lease and must not execute against it.
  - evidence: GET /observe at 11:24:38Z lists tabs default/probe-form/probe-form2; GET /browser/status reports online:false, tabId:null, pendingCommands:4.

## Capabilities it proposed

### "I'm heading out—check whether I’m going to be late or forget anything, and leave me a short spoken checklist on the pendant."
- **useful because:** A departure check is different from a morning brief: it reacts to the owner's actual leave-now moment, reconciles the next calendar event with current travel/appointment/account information, and produces only actionable items. It can still complete in degraded mode and resume browser-dependent checks when the extension reconnects.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background for calendar/mail/browser collection and prioritization; realtime only for the pendant's short acknowledgement; deterministic rules for time windows, conflicts, and checklist formatting.
- **latency:** Acknowledge the pendant within 1 second; deliver a 20–30 second checklist within 10 seconds when Mac and browser are online. If browser is offline, speak the calendar/mail-only result immediately and append a clearly marked browser check later.
- **cost:** Usually <$0.01 per invocation: deterministic schedule/conflict logic plus one small background-model call; realtime cost is limited to the acknowledgement. Browser extraction and TTS dominate latency, not reasoning.
- **security:** Calendar/mail stay within the pre-authorized Mac read scope. Authenticated browser data leaves the browser only as redacted, cited fields. Do not expose full message bodies or account secrets in audio; require explicit confirmation before any navigation, booking, or sending. Record which sources were unavailable.
- **missing:** A pendant departure trigger (button/voice event) that starts a relay job without opening a microphone continuously; Implemented mac_read_sources and mac_readonly_inspect adapters (the granted tool schemas currently return 'no implementation yet'); A durable cross-surface job state that can resume browser checks after extension heartbeat/reconnect; A small audio-queue handoff from relay to pendant with partial-result and retry semantics; Browser extension reconnect/lease restoration; current home-chrome is offline with four pending commands

### "Before I send or upload this, check that it is going to the right person/site and that I am not accidentally exposing anything sensitive."
- **useful because:** Today the system can draft or fill things, but it cannot perform a unified last-mile safety review across the Mac draft, the browser's authenticated destination, and the owner's durable privacy rules. This capability would catch wrong-recipient, wrong-account, secret-in-attachment, and audience-mismatch mistakes before an irreversible send or upload, while still letting the owner make the final decision from the pendant.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic classifiers and destination/account checks first; a background model explains ambiguous findings and compares them with the owner's explicit sensitivity rules. Realtime only narrates the compact result and collects the owner's final approval.
- **latency:** Produce a preflight report in under 5 seconds for a normal email/form/upload. Never delay opening or editing a draft; block only at the final send/upload boundary until the owner has heard or viewed the report.
- **cost:** Typically under $0.02: local structured extraction and deterministic secret-pattern checks dominate; one small background-model call handles ambiguity. No expensive realtime reasoning beyond a short voice exchange.
- **security:** The checker itself must not exfiltrate the very secrets it is protecting. Keep raw files and message bodies local where possible; send only hashes, labels, and redacted excerpts to the relay. Destination identity must be read from the live browser tab or mail compose window, not inferred from a URL or typed text. Store reports briefly with explicit deletion and never auto-send after a timeout.
- **missing:** A local, content-aware preflight API for drafts, attachments, and upload selections; A browser-side destination identity/result contract that exposes signed-in account, recipient, origin, and form target without returning unrelated page contents; An owner-controlled sensitivity and audience policy store with explainable rules; A final-send/upload interception point shared by Mac Mail/apps and the browser extension; A pendant confirmation protocol that binds approval to the exact report hash, destination, and payload version


## Changes it proposed to its own stack

### `integration` — Implement the newly granted mac_read_sources and mac_readonly_inspect tools as real read-only adapters over the Mac local agent, with bounded schemas, redaction, source timestamps, and explicit unavailable/permission states. Add a single 'departure-check' job coordinator that snapshots Calendar/Mail, requests browser facts when the extension lease is live, writes a cited checklist artifact on the Mac, and publishes a short audio result or a resumable partial result to the relay/pendant.
- **owner gets:** The owner can ask for a departure check and get a trustworthy answer instead of a silent failure or an automation guess. It will tell them exactly what was checked, what could not be checked, and continue the browser portion after reconnection.
- effort: Medium: implement two local-agent adapters, a durable job state machine with source-level completion, redacted evidence records, and relay audio-queue integration; add contract tests for offline Mac, offline browser, and missing permissions.  ·  risk: Read adapters could leak private snippets if redaction boundaries are wrong; use field-level allowlists, default snippets, and no body access unless explicitly requested. A resumed browser job could act on a stale tab; bind to extensionId/tab identity and expire the job before any mutation. Recover by keeping partial results and marking stale sources rather than guessing.
- cost: Small ongoing storage and one background-model call per departure check; no realtime model call beyond acknowledgement. Engineering cost is concentrated in adapters and durable resume tests.  ·  latency: Calendar/Mail can be returned in under a few seconds; browser reconnection may add arbitrary delay, but it should never block the initial partial spoken checklist.
- security: Improves security by making source scope, redaction, freshness, and unavailable permissions explicit; no new write authority is needed. Browser mutations remain outside this job and require a separate explicit request.
- depends on: The granted Mac read tools need implementations, not only schemas; Browser heartbeat/poll must restore a valid tab lease and reject stale tab identities; Relay needs a resumable audio/result queue with source citations

### `mac-harness` — Add an executable-identity readiness handshake: on startup, the Mac agent must verify Accessibility trust for the exact running bundle/executable, run a harmless zero-delta input probe, and mark UI actions unavailable (rather than reporting success) when the trust belongs to a different binary. Provide a one-click System Settings deep link and recheck after relaunch; keep read-only AppleScript sources available independently.
- **owner gets:** The owner will no longer be told that a click or keystroke happened when it silently did nothing. Browser/calendar/mail reads can still work, while GUI tasks clearly explain the one permission that is missing and how to fix it.
- effort: Small to medium: identity-aware permission probe, action-result propagation, dashboard status card, and launch/recheck flow; add tests for stale grants after app replacement and for read-only operation with UI disabled.  ·  risk: A false negative could temporarily disable UI automation after an update; recover with explicit recheck and a visible manual retry. Never auto-grant or weaken macOS permissions.
- cost: Negligible runtime/API cost; one local probe at startup and after permission changes.  ·  latency: Milliseconds at startup; avoids wasted 25-step computer-use loops and false receipts.
- security: Positive: prevents untrusted or misidentified binaries from being treated as authorized, without expanding permissions.
- depends on: Owner must grant Accessibility to the exact AI Pendant Agent app currently running, or the app must preserve its signed identity across updates

### `integration` — Create a cross-surface outbound-preflight protocol. The Mac and browser facets independently produce a canonical payload manifest (destination identity, account, attachments, fields, redacted content labels, and hashes); the relay reconciles them with the owner's sensitivity policy and returns a signed report hash. The executor must require that exact hash at send/upload time and invalidate it whenever the payload or destination changes.
- **owner gets:** The owner gets a meaningful final safety check instead of a generic confirmation: “this exact file, to this exact account, containing these flagged fields.” A stale approval cannot accidentally authorize a changed draft or tab.
- effort: Medium to high: define the manifest schema, add Mail/app and browser interception adapters, implement policy evaluation and hash binding, and provide a compact dashboard/pendant explanation.  ·  risk: Overly aggressive rules could create confirmation fatigue; begin with high-confidence secrets, external recipients, and account mismatches, with per-rule muting. If one surface cannot produce a trustworthy manifest, fail closed for sending/uploading but preserve editing and draft creation.
- cost: Low recurring cost; mostly local hashing and deterministic policy evaluation, with occasional small background-model calls for ambiguous classification.  ·  latency: Adds roughly 1–3 seconds before an irreversible send/upload; no impact on ordinary editing or browsing.
- security: Strongly positive: minimizes raw-data movement, binds approval to immutable payload evidence, and prevents confused-deputy actions across stale browser tabs or changed files.
- depends on: Local draft/attachment manifest extraction; Browser destination identity contract; Owner sensitivity-policy storage; Send/upload interception points; Pendant approval bound to a report hash


## What it asked for

_Nothing._
