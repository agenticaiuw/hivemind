# Harness derivation — faculty-perception — round 123

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac/browser perception state** — At 2026-08-07T18:11Z the Mac bridge and Safari extension are online with 3 tabs and zero pending browser commands; durable sessions include Gmail inbox (14,987 messages), Selenium web form, and httpbin form. The extension's current tab is https://example.com titled 'Failed to open page'. AI Pendant Agent Accessibility and Screen Recording are false; observe reports ui_actionsWillReachTheScreen=false, while AppleScript automation grants are present.
  - evidence: GET /ops/status, GET /browser/status, GET /observe all returned HTTP 200 with these fields.

## Capabilities it proposed

### "“What is actually available right now?” — give me one short, spoken status of my Mac, browser, relay, and pendant, separating live, stale, unavailable, and merely recorded history."
- **useful because:** The owner currently cannot tell that a browser extension is online while its active page is a failed load, or that the relay is healthy while no pendant is registered. A single freshness-labeled answer prevents the mind from planning around imaginary hardware or false UI control.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement
- **model tier:** background for routine snapshots; deterministic assembly from telemetry, escalating to realtime only when the owner asks a follow-up.
- **latency:** Under 2 seconds for a spoken snapshot; use cached telemetry with explicit ages and fetch only the missing surface.
- **cost:** Near-zero when deterministic; at most one small background-model call for natural-language compression. Dominant cost is not model tokens but fresh cross-surface probes.
- **security:** Do not expose private page contents in the spoken status; report only URL domain/title, device identity, permission state, and freshness. Mark historical pipeline telemetry as history, never current.
- **missing:** A unified authenticated device registry that distinguishes physically connected USB hardware from relay-registered devices; A standard freshness/availability envelope for Mac, browser, relay, and pendant telemetry; Relay-side acknowledgement that a pendant is actually connected rather than merely configured

### "“Before you do anything on that website, verify that the tab is really the page I meant, loaded successfully, and still signed in; if not, tell me exactly what is wrong and stop.”"
- **useful because:** The live extension currently reports online while its current tab is a failed page, and durable sessions can outlive a tab's real state. This prevents actions against an error page, wrong account, login screen, or stale tab—especially important when the owner says only “handle this.”
- **path:** browser-extension → mac-planner → relay-realtime → faculty-perception → faculty-judgement
- **model tier:** deterministic checks first (URL/title/error markers, tab/session identity, heartbeat age, login indicators); use background model only to interpret ambiguous page health, never realtime by default.
- **latency:** Under 1 second for known error/auth checks; under 3 seconds for ambiguous semantic validation.
- **cost:** Near-zero for DOM metadata and heartbeat checks; occasional small background call for ambiguous pages. No screenshot upload unless explicitly requested.
- **security:** Inspect only the selected tab and return redacted health facts, not page contents or cookies. Never attempt login or recovery automatically. Require confirmation before switching tabs or reloading a private page.
- **missing:** Browser bridge health schema with explicit pageLoadState, authState, and selected-tab identity; A redaction-safe login/error detector for authenticated pages; A pre-action gate integrated into browser action planning

### "“Bookmark this moment.” When I press the pendant button, capture the last few seconds of what I said, the active browser page, and the Mac app I was using; later say “resume my bookmark” and give me the exact context and next step."
- **useful because:** It creates a durable, human-scale handoff between a worn moment and the machine state that explains it. The Mac alone cannot know the owner's spoken intent, and the pendant alone cannot know which private tab or app was active; the relay can reunite them after a dropped connection.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement
- **model tier:** Deterministic event capture and metadata first; background model summarizes only on resume. Realtime is used only if the owner asks immediately while wearing the pendant.
- **latency:** Button acknowledgement under 150 ms locally; relay upload opportunistically; resume response under 3 seconds when metadata is cached.
- **cost:** Tiny when bookmarking (metadata plus a short compressed audio clip); one background summarization call on resume. Storage and audio transfer dominate, not inference.
- **security:** Encrypt audio and private-tab metadata; retain only a configurable short clip and automatic expiry; redact page body by default and store URL/title plus a user-selected excerpt. Button press is capture consent, but replaying private context requires the owner's authenticated voice/session.
- **missing:** Pendant firmware button event and bounded ring-buffer capture that works offline; Relay endpoint for an append-only, acknowledged context bookmark with conflict-safe reconnect; Mac/browser snapshot endpoint that atomically records foreground app, selected tab/session, URL/title, and observation timestamp; A resume command that cites each component's age and marks missing or stale pieces instead of inventing them

### "“Is this the right account before I do anything?” Have the system compare the identity, organization, and permissions visible across my open private tabs, then warn me if tabs are signed into different accounts or if the requested action would occur under the wrong identity."
- **useful because:** A logged-in browser can be online and readable while silently using the wrong personal, work, or organization account. The owner cannot reliably detect that conflict from a voice command, and an accidental action under the wrong identity can be costly or irreversible.
- **path:** browser-extension → mac-planner → relay-realtime → faculty-perception → faculty-judgement
- **model tier:** Deterministic extraction and account fingerprint comparison first; background model only for ambiguous identity labels. Realtime is unnecessary unless the owner is asking during a live action.
- **latency:** Under 2 seconds for already-open tabs; never wait for broad crawling.
- **cost:** Low: DOM metadata and account-label extraction dominate; one small background call only when labels conflict or are ambiguous.
- **security:** Return a redacted account fingerprint (domain, organization, masked address), never passwords, cookies, or full private page contents. Require explicit confirmation before opening additional account pages.
- **missing:** A browser-bridge identity extraction contract with DOM locators and redaction rules; A per-session account fingerprint and organization scope model; A pre-action identity gate that faculty-judgement can consume

### "“Listen for commitments in this meeting and keep a private action-item list.” The pendant should capture only the owner’s meeting audio, the relay should transcribe it, and the Mac should match names, dates, calendar events, and existing tasks—then leave proposed follow-ups for review without sending anything."
- **useful because:** Today the owner must remember commitments manually and later reconstruct which person, date, and project each sentence referred to. The pendant has the physical presence and audio context, while the Mac has the calendar and task systems; neither node can do this alone.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → faculty-perception → faculty-judgement
- **model tier:** Realtime only for live, low-latency partial transcription if requested; background speech-to-text and extraction for ordinary meetings, with a cheaper model matching entities and dates afterward.
- **latency:** A private live transcript may lag 1–2 seconds; action-item extraction can finish within 30 seconds after the meeting. Do not block normal conversation on it.
- **cost:** Audio upload and transcription dominate; background extraction is modest. Retain compressed audio briefly and delete it after verified transcript extraction unless the owner explicitly saves it.
- **security:** Meeting capture requires an explicit physical start/stop indication and a visible local recording state; do not record by default. Encrypt in transit and at rest, isolate other speakers’ content, redact secrets, and require approval before creating tasks, reminders, or messages.
- **missing:** A pendant-local recording mode with explicit start/stop and offline buffering; Relay audio segmentation, transcription, and deletion acknowledgements; Speaker/owner-channel separation or an owner-only capture policy; A Mac connector that resolves transcript entities against Calendar, Reminders, Notes, and Mail without sending changes; A review queue for proposed commitments with source timestamps

### "“Read me the important part of this private page, but do not leave the page text anywhere.” Have the browser extract only the requested passage, the relay speak it to my pendant, and then return a verifiable deletion receipt showing that the raw page content was not persisted."
- **useful because:** The owner can access private pages in Safari, but sending their full contents through durable logs, model context, or audio queues creates unnecessary exposure. This would make private, spoken access possible while constraining what leaves the browser and proving cleanup afterward.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → faculty-perception → faculty-judgement
- **model tier:** Deterministic DOM selection and redaction first; use a small background model only to identify the requested passage. Realtime is appropriate only for immediate spoken playback.
- **latency:** 3 seconds for a short passage; longer extraction may run as a bounded background job with an expiry.
- **cost:** Low to moderate: private-page extraction and speech generation dominate; no durable storage should be used for raw text.
- **security:** The browser must send an ephemeral, purpose-scoped payload rather than a page dump; relay and TTS must enforce TTL deletion and prevent transcript/log retention. Show source URL and passage boundaries, and require confirmation for highly sensitive categories.
- **missing:** End-to-end ephemeral payloads with no raw-content logging at browser, relay, model, or audio layers; A deletion receipt that covers every intermediate store and cache; Browser-side semantic extraction constrained to the requested region; Pendant playback acknowledgement and interruption controls


## Changes it proposed to its own stack

### `integration` — Make UI action receipts truth-preserving: when /observe reports accessibility.trusted=false, screenRecording=false, or inputReachability.status=failed, classify click/type/menu/press actions as blocked_or_unverified rather than success; after any UI action, require a postcondition observation (focused element, URL/title change, or DOM/value delta) before emitting completed. Keep AppleScript and browser-DOM actions separately labeled as verified when their own acknowledgements succeed.
- **owner gets:** The owner will stop being told that something happened when the agent visibly did nothing—a dangerous failure mode for sending, editing, or navigating—and will get a precise explanation of what permission or postcondition is missing.
- effort: Medium: receipt schema/status changes, postcondition probes, and regression tests across Mac and browser action paths.  ·  risk: Some existing jobs will become 'unverified' instead of 'completed'; recover by exposing the raw receipt and offering a safe retry only after reachability or a DOM acknowledgement is available. Never infer success from the action call alone.
- cost: Negligible API cost; one lightweight observation per UI action or action batch.  ·  latency: Adds roughly 100–500 ms for a local postcondition check; avoids expensive planner retries caused by false success.
- security: Improves safety by preventing silent UI mutations; does not grant new permissions or exfiltrate screen data.
- depends on: GET /observe reachability fields; GET /browser/status and browser result acknowledgements; Existing job receipts/undo routes

### `model-routing` — Add a perception preflight to every planner task that references 'now', 'this tab', 'my Mac', or device availability: fetch a compact, timestamped observation bundle and expose hard states (offline, failed page, permission-blocked, historical telemetry) as non-negotiable constraints. If required evidence is stale or absent, the planner must answer 'unknown' or ask for a fresh probe instead of filling the gap from memory.
- **owner gets:** Requests about the current world will stop producing confident answers based on yesterday's pipeline records or an online extension whose selected page failed to load. The owner gets honest answers and fewer actions aimed at the wrong surface.
- effort: Medium: classify temporal/device-referential prompts, compile a small evidence envelope, and add planner contract tests for stale and contradictory telemetry.  ·  risk: Adds a probe to some requests and may produce more 'I can't verify that' responses. Recover with a clearly offered refresh action and a deterministic fast path for fresh data.
- cost: Small probe overhead; likely reduces expensive planner retries and hallucination-driven actions. No additional model call when deterministic preflight resolves the question.  ·  latency: ~100–700 ms for local/relay reads; parallelize probes and skip for timeless questions.
- security: The planner receives metadata and provenance, not page bodies; preserve existing sensitivity labels and do not broaden browser access.
- depends on: GET /ops/status; GET /observe; GET /browser/status; GET /pipeline; A typed freshness/confidence envelope shared across surfaces


## What it asked for

_Nothing._
