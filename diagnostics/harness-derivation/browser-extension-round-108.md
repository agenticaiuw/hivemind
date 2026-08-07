# Harness derivation — browser-extension — round 108

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Before I leave for an appointment, reconcile the details across my logged-in booking/portal pages and Mac calendar, tell me if anything conflicts or changed, and prepare (but do not send) any needed message or reschedule form."
- **useful because:** Private booking portals and the local calendar often disagree or change independently. The browser extension can read the owner-only details, the Mac can compare them with calendar and location context, and the relay can deliver a concise spoken alert to the pendant. This prevents missed appointments without silently sending or rescheduling anything.
- **path:** browser-extension → mac-planner → relay-realtime → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use a cheap background model for scheduled reconciliation and extraction; use realtime only when the owner asks a follow-up by voice. Escalate to the stronger planner only for ambiguous conflicts or multi-site forms.
- **latency:** Scheduled checks may take 30–90 seconds and should finish before the briefing window; an on-demand voice answer should provide an initial conflict summary within 5 seconds, with cited details arriving asynchronously.
- **cost:** Roughly $0.01–$0.05 per scheduled reconciliation depending on page count and extraction; most cost is authenticated page reads and conflict synthesis, not speech.
- **security:** Only selected authenticated pages and the relevant calendar event leave the browser surface. Store short-lived encrypted evidence with URL, timestamp, and field-level provenance; redact unrelated page content. Preparing a draft is reversible, but submitting a message, booking change, or payment must stop and show the exact payload for explicit approval.
- **missing:** A durable cross-surface reconciliation job that can bind named authenticated browser pages to one or more calendar events; Semantic field extraction for dates, timezone, location, cancellation/reschedule rules, and booking identifiers with freshness/conflict scoring; A short-lived evidence packet shared from browser to Mac/relay, with field-level redaction and citations; A review UI/voice flow that presents proposed messages or form values without submitting them

### "When I say “make sure I don’t lose this” while viewing a logged-in webpage, turn the page’s concrete obligation into a tracked commitment, remind me at the right time, and later verify from the site whether I completed it or whether the deadline/status changed."
- **useful because:** Today a private portal may contain a deadline, renewal, application, claim, or required reply that disappears from attention once the tab is closed. This would let the owner capture it naturally by voice on the pendant, preserve exactly what the page said, create a useful follow-up on the Mac, and verify completion against the owner-only site instead of merely setting a blind reminder.
- **path:** browser-extension → relay-realtime → mac-planner → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use a cheap background model for extracting obligation, deadline, entity, and completion signals from a cited page snapshot; use realtime only to capture the owner's spoken intent and answer follow-up questions. Use the stronger planner only when the page has ambiguous deadlines or multiple possible completion paths.
- **latency:** Capture and acknowledgement within 3 seconds while the page is open; commitment creation may finish asynchronously within 30 seconds. Scheduled verification can run in the background and should produce a pendant-ready summary before the deadline or during the owner's chosen quiet hours.
- **cost:** About $0.01–$0.04 per capture/verification cycle; the dominant costs are authenticated page extraction and occasional re-checks, with small reminder and speech costs.
- **security:** The system handles sensitive authenticated content and potentially high-impact deadlines. Store only the extracted obligation, a minimal quoted evidence snippet, URL/tab identity, timestamp, and a short-lived page fingerprint; encrypt and expire snapshots. Never mark an obligation complete based only on a vanished button or inferred navigation. Any reply, submission, payment, or cancellation remains a prepared preview requiring the owner's explicit approval.
- **missing:** A pendant-to-browser intent handoff that binds the spoken phrase to the currently active Safari tab; An obligation schema with evidence citation, owner-confirmed interpretation, deadline/time-zone normalization, and lifecycle states (captured, due, verified, blocked, expired); A durable verifier that can revisit the authenticated page and compare completion evidence while distinguishing stale tabs, login interstitials, CAPTCHA, and genuine completion; Cross-surface commitment storage and notification routing that links Mac reminders, relay scheduling, and browser verification without copying full page contents; A concise owner review flow for correcting the extracted obligation or deadline before reminders begin


## Changes it proposed to its own stack

### `browser-harness` — Add a cross-surface reconciliation workbench between authenticated browser sessions and Mac/relay jobs. A job definition binds selected browser session/page sources to a local calendar event or reminder, runs typed semantic extraction (start/end/time zone, location, status, booking ID, change/cancel rules), computes freshness and conflict scores, and emits a short-lived redacted evidence packet with per-field URL/tab/timestamp/snippet-hash provenance. The packet is consumable by briefing and pendant voice follow-ups; draft actions are represented as preview payloads and never auto-submitted.
- **owner gets:** The owner gets one trustworthy answer when private web bookings and the calendar disagree, instead of manually opening several tabs and comparing dates, times, and locations. They can hear the conflict while away from the Mac and review an exact draft before anything is sent.
- effort: Medium-high: browser session binding and extraction, a reconciliation schema/scorer, encrypted TTL evidence storage, Mac job integration, and a small review/voice presentation path; add fixtures for timezone changes, canceled bookings, stale tabs, and login interstitials.  ·  risk: A stale or partially loaded authenticated page could produce a false conflict or miss one. Mark every field stale/blocked when the tab is offline, unauthenticated, or CAPTCHAed; require all sources to be cited and show uncertainty. Recovery is rerun after the owner reopens/authenticates the page; no irreversible action is executed by the workbench.
- cost: Low incremental API cost: mostly one cheap extraction/synthesis pass per selected page and occasional stronger-model disambiguation. Storage is small encrypted JSON packets with short TTL; no new hardware.  ·  latency: Background jobs can complete in under 90 seconds; voice follow-up should read the cached packet in under 2 seconds, with a rerun clearly reported if stale.
- security: Increases handling of sensitive booking and calendar data. Use per-job source allowlists, field-level redaction, encrypted storage, short TTL/deletion, and provenance logs; never transmit unrelated DOM text or credentials.
- depends on: A functioning durable browser job runner and named authenticated page-watch/session bindings; Typed page extraction with explicit blocked/offline/auth-interstitial states; A shared short-lived evidence-packet/context service consumable by Mac planner, relay briefing, and pendant voice; The existing receipt/undo and preview mechanisms for prepared but unsent actions

### `integration` — Make the granted browser command enqueue tool a real adapter instead of a schema-only stub: accept one typed browser action, POST it to /execute with request/session metadata, await the extension result (or return a durable job ID on timeout), and normalize success, no-tab, offline, auth-interstitial, CAPTCHA, and timeout states. Add a health probe that reports the last Safari heartbeat and pending-command age before dispatch.
- **owner gets:** The owner can actually ask the pendant to read or navigate a private page again, and receives an honest explanation when Safari is closed or logged out instead of an opaque implementation error or a hanging request.
- effort: Small-medium: implement the harness adapter, response normalization, timeout/job handoff, and integration tests against the existing /execute and browser result routes.  ·  risk: Duplicate dispatch or late extension results could confuse a task. Include idempotency/request IDs and return late results to the durable job record; never retry browser mutations automatically. If the adapter fails, preserve the existing /execute path for Mac agents.
- cost: Negligible API cost; one local HTTP round trip and existing extension polling. No hardware cost.  ·  latency: Reads should add under 200 ms before extension latency; long operations return a job ID rather than blocking for 45 seconds.
- security: The adapter must forward the existing bearer/session binding without logging page text, credentials, or full URLs beyond the existing provenance log. Restrict actions to the already-authorized browser types.
- depends on: A live Safari extension heartbeat and at least one tab for reads (navigate can bootstrap a tab); The existing POST /execute browser action path and POST /browser/result/:commandId; A durable result/job store for extension responses that arrive after the synchronous timeout


## What it asked for

_Nothing._
## Its own summary

Established that the browser surface is currently unusable live: /browser/status reports Safari absent/offline and only offline home-chrome, with 10 pending commands. Proposed a new cross-surface authenticated appointment reconciliation workbench: selected private pages + Mac calendar -> typed freshness/conflict scoring -> cited, redacted short-lived evidence packet for relay/pendant, with unsent action previews. Also proposed implementing the currently schema-only browser enqueue adapter so browser reads return honest typed health states or durable job IDs. Informed mac-planner that offline/no-tab/auth-interstitial/CAPTCHA must suppress browser-derived urgency.

**Biggest unknown:** Whether Safari can be brought online with a real tab in the next round, and whether the orchestrator will implement the browser enqueue adapter; without those, I cannot inspect any owner-authenticated page or validate the new workflow end to end.

