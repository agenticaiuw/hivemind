# Harness derivation — mac-planner — round 27

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac action readiness and browser reachability** — At 2026-08-07T08:58Z relay and Mac bridge are reachable, but Mac agent ready=false: Accessibility is not trusted for the actual com.aipendant.agent process (events rejected), Screen Recording is missing, and browser extension is offline with no pending commands. /observe explicitly warns ui_* receipts are false-success and cannot be trusted.
  - evidence: GET /ops/status and GET /observe live probes

## Capabilities it proposed

### "“Keep me focused: watch my Mac and logged-in browser notifications, suppress routine noise, and tell me on the pendant only when something genuinely urgent needs me.”"
- **useful because:** No single node sees the whole interruption surface: the Mac knows foreground app and local notifications, Safari holds authenticated web alerts, and the pendant is the only channel that can reach the owner without pulling them out of focus. It would prevent notification overload while preserving time-sensitive items.
- **path:** mac-bridge → browser → relay → pendant → dashboard
- **model tier:** Background classification with a cheaper text model; realtime only for the owner's spoken follow-up. Use deterministic rules first (sender/site, deadlines, calendar conflicts), then model ranking for ambiguous items.
- **latency:** Routine polling every 2–5 minutes is acceptable; urgent alerts should reach the pendant within 30 seconds of ingestion. Focus-state changes should propagate in under 2 seconds.
- **cost:** Roughly $0.01–$0.05 per day for low-volume classification; dominated by model calls on ambiguous notifications. Deterministic filtering and local deduplication should make the common path free.
- **security:** Notification text and authenticated-page snippets may leave the Mac for classification; default to local redaction of message bodies, sender/title/domain plus deadline cues, and configurable allowlists. Never auto-reply, click, or submit. Require explicit owner configuration for which browser sessions and notification sources are watched; urgent delivery itself can reveal sensitive metadata to anyone hearing the pendant.
- **missing:** A read-only macOS notification-center/source adapter with notification IDs, timestamps, app, title, and redacted body; current mac_read_sources covers Calendar/Mail only.; A browser notification/page-watch ingestion path that works when the Safari extension is online, with durable cursors and semantic deduplication.; A shared focus-state contract (foreground app, calendar focus blocks, manual pendant toggle) and interrupt policy persisted at relay.; A pendant alert queue with quiet-hours, escalation, acknowledgement, and replay semantics.; A dashboard to configure sources, urgency rules, redaction, and inspect why an item was or was not surfaced.

### "“When I walk away from my Mac, remember exactly where I was across my apps and logged-in browser tabs; when I come back, give me a spoken two-sentence resume and restore only the windows I choose.”"
- **useful because:** Today a work interruption loses context across the Mac's documents, browser sessions, and the owner's memory. The pendant can detect the departure/return interaction, the Mac can capture local app and window state, the browser can preserve authenticated tab identity without exposing page contents, and the relay can retain a compact resume capsule while the Mac is asleep. This is a continuity primitive rather than another briefing or task runner.
- **path:** pendant → mac-bridge → browser → relay → dashboard
- **model tier:** Use deterministic local state capture and hashing first; use a cheap background model only to turn the selected checkpoint into a concise resume sentence. Realtime is needed only if the owner asks a spoken follow-up.
- **latency:** Checkpoint in under 3 seconds after an explicit pendant double-press or idle departure; resume capsule available within 2 seconds of return. Restoration is owner-selected and should complete within 10 seconds.
- **cost:** Usually near-zero API cost because state is local metadata; under $0.01 per checkpoint when summarization is needed. Storage is a few KB per checkpoint plus optional encrypted thumbnails, which should be off by default.
- **security:** Authenticated browser URLs, document names, and window titles are sensitive. Keep content and screenshots local by default; send only encrypted opaque tab/session IDs and user-approved labels to the relay. Never reopen a private tab or alter a document without an explicit return-time selection. Provide per-app exclusions, retention limits, and a visible delete/export history.
- **missing:** A pendant departure/return event or reliable paired-presence signal with explicit user override.; A Mac checkpoint adapter that records app/window/document identity, unsaved-change indicators, and reopenability without taking screenshots by default.; A browser checkpoint API that records tab/session identity and safe titles while preserving authenticated session affinity.; An encrypted, expiring relay resume-capsule store and a Mac-side restore planner with a preview UI.; A dashboard timeline showing checkpoints and allowing the owner to choose what is restored.


## Changes it proposed to its own stack

### `integration` — Make the packaged AI Pendant Agent the single stable Accessibility identity: stop launching a different embedded Node executable identity, preserve the bundle signing identity across updates, and add a startup self-test that compares the granted bundle/team identity with the actual event-posting process. If mismatched, show a one-click System Settings repair path and mark UI actions unavailable rather than returning false-success receipts.
- **owner gets:** GUI automation would either work reliably or clearly say it cannot; today receipts can claim ui_click/type success while nothing reaches the screen because Accessibility is granted to a different binary. This is the immediate blocker to trustworthy Mac action.
- effort: Medium: packaging/launchd/signing changes, permission diagnostics, migration UX, and regression tests across updates.  ·  risk: An update may invalidate the existing Accessibility grant and require one-time reauthorization. Recover by retaining the old launch path during migration and providing a clear repair screen; never attempt to silently alter privacy settings.
- cost: No meaningful API cost; engineering-only. Potential one-time owner setup of under a minute.  ·  latency: Negligible startup self-test, likely under 200 ms; avoids futile 45-second UI/browser timeouts.
- security: Improves security truthfulness by preventing untrusted or mismatched binaries from presenting as the granted automation host; does not reduce the owner's maximum-access policy.
- depends on: A stable signed app/host packaging decision; A permission migration test on the current macOS version

### `integration` — Ship the implementations behind the already-granted mac_read_sources and mac_readonly_inspect interfaces, with a capability/version handshake that reports 'implemented' versus schema-only. Calendar/Mail reads should use bounded native APIs and redaction; inspection should expose running apps, foreground app, browser sessions, accessibility state, and approved directory listings. Return structured errors instead of silently routing callers to UI automation.
- **owner gets:** The owner could receive reliable briefs and truthful machine state even while Accessibility, Screen Recording, or Safari extension access is unavailable. Today these tools appear granted but fail at invocation, forcing expensive and misleading GUI/browser attempts.
- effort: Small-to-medium: implement adapters, tests, and route/tool registration; validate account scope and redaction behavior.  ·  risk: Calendar/Mail account or permission errors; mitigate with empty/error states and no body content by default. Directory inspection must preserve approved-path boundaries even though FULL_CONTROL actions remain unrestricted.
- cost: Negligible API cost for bounded reads; lower model cost by avoiding failed retries and UI loops.  ·  latency: Typical reads under 1–3 seconds; removes 45-second browser/UI timeout paths for tasks that only need local sources.
- security: Read-only, scoped, redacted access reduces exposure. Keep account_scope explicit and audit source, timestamp, and redaction state in receipts.
- depends on: Implementations for the two currently schema-only tools; Stable tool registration/health endpoint; Automation grant verification rather than cached grant claims


## What it asked for

_Nothing._
## Its own summary

Round 27 established three concrete blockers and two new proposals. Live probes show relay/Mac bridge reachable, but Accessibility is granted to a different binary than the running agent and Screen Recording is missing; /observe warns UI receipts are false-success. Safari/browser bridge is offline (pendingCommands=0). The newly granted mac_read_sources and mac_readonly_inspect tools are schema-only and return implementation errors, so bounded Calendar/Mail and inspection reads are not yet usable. I proposed (1) a cross-surface focus firewall that combines Mac/browser notifications, relay ranking, and pendant urgent-only delivery, and (2) stable signed host identity plus truthful permission self-test, plus implementation of the read-only tools. I notified perception/action/unified/browser peers and recorded the live state.

**Biggest unknown:** Whether the owner can repair Accessibility/Screen Recording and enable Safari's bridge now, and whether the orchestrator will implement the two granted read-only tools. Until then I can safely inspect via /ops/status and /observe, but should not claim GUI actions, browser actions, Calendar/Mail reads, or reliable audio validation.

