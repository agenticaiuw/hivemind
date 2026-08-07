# Harness derivation — browser-extension — round 81

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-extension live state** — At 2026-08-07T12:52Z, /browser/status reports Safari absent/offline; only home-chrome is registered and offline with null tab, while pendingCommands=7. /browser/sessions contains three stale sessions last used around 06:26Z (time.is and probe forms), so session records do not imply a reachable browser.
  - evidence: GET /browser/status HTTP 200 and GET /browser/sessions HTTP 200 in this round

## Capabilities it proposed

### "“Take the important details from the logged-in page I’m looking at and put them into the right Mac app — show me what you found and what you’re about to create first.”"
- **useful because:** The browser is the only surface that can see the owner’s private web session, while the Mac is the only surface that can create a native reminder, note, calendar item, or local file. This turns a private-page fact into useful local follow-through without asking the owner to copy/paste or expose the whole page. A cited preview prevents transcription mistakes and makes the handoff auditable.
- **path:** browser-extension → faculty-perception → faculty-judgement → mac-planner → mac-vision → relay-realtime → pendant
- **model tier:** Use the cheaper background model for DOM extraction, field normalization, and drafting the native action; use realtime only if the owner is speaking live or asks a follow-up. mac-planner executes the short typed native action after the preview; browser-extension never sends the full page when selected fields suffice.
- **latency:** About 3–6 seconds for extraction and preview while Safari is online; native creation another 1–3 seconds after the owner’s spoken approval. If Safari is offline, report that immediately rather than replaying against a different tab.
- **cost:** Roughly one background-model call plus existing browser/Mac action calls, typically cents or less; latency is dominated by the extension poll/result round trips, not tokens.
- **security:** Only selected fields and short source snippets should cross the browser-to-Mac boundary, with URL, tab ID, timestamp, and a content hash attached. Redact passwords, session tokens, and payment data. Show the exact native fields before creation. Creating a reminder/note/file is reversible; sending a message, submitting a form, or changing a remote account must stop at a draft/preview. The owner’s maximum-access policy means this is not an undifferentiated gate, but irreversible browser mutations remain preview-only.
- **missing:** A first-class browser-to-native handoff object containing typed fields, citations, redaction labels, and expiry; Field extraction that can identify the target native app/schema from the owner’s goal rather than caller-supplied values alone; A unified preview that pairs source evidence with the exact Mac action payload; Cross-surface completion receipt linked to the browser evidence and native job receipt

### "“When I press the pendant button, tell me the one or two things on the private page I’m currently viewing that are most important — without me naming the site or copying anything.”"
- **useful because:** Today the owner must identify the site, navigate the assistant, and explain what to inspect. This would make the pendant a genuinely ambient companion to authenticated browser work: one physical gesture answers “what matters here?” from the page already in front of them, including pages that public search cannot reach. It is distinct from scheduled page watching or preparing a form: it is an on-demand, active-tab question with no persistent watch and no mutation.
- **path:** pendant → browser-extension → relay-realtime → faculty-perception → faculty-judgement
- **model tier:** Use a small/cheap extraction model for page structure and candidate facts; use the realtime tier only to turn the result into a short spoken answer and handle a follow-up. Keep full-page interpretation local to the Mac/browser bridge where possible.
- **latency:** Target 2–4 seconds from button press to spoken summary; return a clear “page unavailable” response within 1 second if the extension is offline.
- **cost:** One small extraction/inference call plus existing extension and relay traffic, generally cents or less per press. The dominant cost is sending page text, so cache only a short-lived local DOM representation and transmit selected passages rather than the whole page.
- **security:** The extension must explicitly identify the active tab and redact passwords, tokens, payment fields, hidden inputs, and cross-origin frames before extraction. Attach URL, title, timestamp, and source spans to every claim; never retain page text after a short TTL. Do not click, type, submit, or send anything. If the page contains highly sensitive content, say so and provide only metadata unless the owner explicitly asks for a specific field.
- **missing:** A low-latency active-tab snapshot stream or button-triggered browser command that works against the real Safari extension; A local sensitive-field/redaction pass before any page material reaches the model or relay; A page-to-speech response contract with cited source spans and a strict read-only action schema; Pendant button routing that binds the request to the current browser device/session and returns a spoken result


## Changes it proposed to its own stack

### `browser-harness` — Add an offline-safe browser command inbox and reconciliation protocol. Every queued browser command gets an intent ID, originating session/tab affinity, enqueue time, TTL, and resumability class. When /browser/status loses the real Safari heartbeat, stop dispatching new commands, mark in-flight work as uncertain, and move queued work to parked/expired instead of leaving opaque pending commands. On reconnect, require a fresh heartbeat and tab identity match before replaying only resumable reads; never replay stale clicks/types/submits automatically. Emit a compact status event to relay/pendant (offline, parked count, uncertain command IDs, reconnect/review outcome), and expose idempotent discard/retry endpoints. This is reconciliation beyond the durable runner: it handles the currently observed 7 pending commands and stale browser sessions.
- **owner gets:** The owner will not have an old command unexpectedly run minutes later in a newly opened logged-in tab, and can hear exactly whether a browser task completed, was parked, or needs reopening Safari. Long authenticated tasks become recoverable instead of silently lost or dangerously replayed.
- effort: Medium: browserBridge queue metadata/state machine, heartbeat-loss handling, session/tab revalidation, two small status routes, and relay event wiring; add crash/reconnect tests.  ·  risk: A real read may be parked or an uncertain result may be reported rather than completed; recover with explicit retry after the owner reopens Safari. The protocol must persist state atomically so a worker crash cannot duplicate a mutation.
- cost: Negligible API cost; a few D1/local JSON state writes and small relay events. No page content leaves the device beyond existing browser result paths.  ·  latency: No added latency while online; reconnect adds one heartbeat/tab-validation round before replay.
- security: Improves security by preventing stale commands from landing in a different logged-in tab. Preserve the existing maximum-access/no-confirmation policy; this is affinity and expiry, not an approval gate.
- depends on: chg-16bc5dee durable browser job runner; chg-14accc01 request IDs and tab/session affinity; the existing GET /browser/status, GET /browser/poll, POST /browser/result/:commandId, and DELETE /browser/commands/:commandId routes


## What it asked for

_Nothing._
## Its own summary

Discovered the live browser is not usable right now: Safari is absent/offline, home-chrome has no tab, there are 7 pending commands, and the three stored sessions are stale. Recorded this finding and proposed (1) an offline-safe browser inbox that expires/parks stale work and revalidates tab affinity before replay, and (2) a cross-surface cited handoff that extracts selected private-page fields into a Mac reminder/note/file preview. I told unified and mac-planner what remains. The browser product gaps still outstanding are a real enqueue implementation, live Safari heartbeat/tab, account/origin registry, web-content urgency scoring, draft generation, and a drafts store.

**Biggest unknown:** Whether the Safari extension can be brought online with a real tab in this round; without that, authenticated extraction and the proposed browser-to-Mac handoff cannot be tested end to end.

