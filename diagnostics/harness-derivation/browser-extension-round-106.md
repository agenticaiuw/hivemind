# Harness derivation — browser-extension — round 106

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Save this page to my notes."
- **useful because:** The browser is the only node that can see the owner's logged-in page, while the Mac is the only node that can reliably create a local rich note and the pendant is the fastest way to invoke it. The owner gets a useful capture of private research or account context without copying URLs or text by hand.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → mac-terminal → dashboard
- **model tier:** deterministic extraction and routing first; use background gpt-4.1-mini only to turn extracted page text into a concise title/summary when requested. Realtime should only handle the spoken command and confirmation.
- **latency:** Under 3 seconds for title/URL capture and note creation; up to 8 seconds if the owner asks for a generated summary. No confirmation needed for creating a note under the owner's stated policy.
- **cost:** Near-zero for title/URL-only capture; roughly one background-model call (about 2k prompt tokens) for an optional summary. Dominant cost is page extraction context, capped to the selected text or 6k characters.
- **security:** Read only the active tab and optional user-selected text; do not send cookies, hidden form values, or unrelated tabs to the model. Store the source URL and timestamp in the note, redact secrets, and require confirmation if the requested destination is an external/shared note rather than local Notes.
- **missing:** A browser action to return active-tab metadata plus user selection in one typed result; A cross-surface capture contract carrying tabId, URL, title, selected text, timestamp, and sensitivity; A Mac note action that accepts provenance and optional summary without exposing browser credentials; A short pendant response and dashboard receipt linking the created note to its source tab

### "Read this logged-in page to me, and let me say 'next heading', 'back', or 'open that link' as you listen."
- **useful because:** Today the owner can ask for a one-off page read, but cannot use the pendant as an eyes-free, conversational reader for a private Safari page. This would make inaccessible or information-dense authenticated sites usable while walking or away from the screen, using the browser session that only the extension can reach.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → dashboard
- **model tier:** Use a deterministic DOM accessibility-tree extractor and local heading/link pagination for ordinary pages; use background gpt-4.1-mini only when the owner asks for a plain-language explanation of a selected section. Keep realtime for low-latency voice control and playback coordination.
- **latency:** First spoken chunk within 2 seconds; next/back/open-target commands within 1 second when the page is already indexed. A complex explanation may take up to 6 seconds.
- **cost:** Near-zero for extraction, pagination, and navigation; optional explanation costs one background call with a capped 4k-character section. Audio bandwidth and page extraction dominate, not model inference.
- **security:** The extension must build the accessibility tree locally and send only the currently requested chunk, never cookies, hidden inputs, password fields, or the complete page. 'Open that link' may navigate but must not submit forms or activate destructive controls; require the existing owner confirmation policy for any irreversible action. Expire the temporary page index when the tab changes or after 15 minutes.
- **missing:** A Safari-extension command/result pair for semantic page indexing (headings, landmarks, links, current focus) and stable element handles, performed locally; A relay session protocol for chunked private text/audio with sequence numbers, interruption, and resume after a dropped pendant link; A pendant voice navigation state machine that keeps current page/tab, chunk, and focused element without relying on a full planner turn; A browser-side safe-navigation classifier that distinguishes ordinary links from submit/delete/purchase/send controls and reports the target before activation; A local transcript/receipt record that stores only page URL, title, and navigation events, not page contents


## Changes it proposed to its own stack

### `browser-harness` — Add an offline-safe browser command ledger: every queued browser command gets a client-generated idempotency key, target session/tab, creation time, and expiry (default 10 minutes); the poll endpoint returns only unexpired commands, and reconnecting Safari receives a compact stale-count event rather than replaying expired navigation/click/type commands. Persist terminal results (success, timeout, expired, cancelled) and expose GET /browser/queue/status plus a one-shot cleanup endpoint. Preserve read-only navigation/read commands for explicit replay, but never replay browser_type/click/submit after expiry.
- **owner gets:** Safari outages will no longer cause a later reconnect to execute old clicks or form typing unexpectedly, while the owner gets a truthful explanation of what was skipped and can retry the current task. This directly addresses the live queue holding 10 commands while no browser device is online.
- effort: Medium: browserBridge queue schema/migration, poll filtering, reconnect event, result bookkeeping, and a small dashboard/voice status formatter; add tests for disconnect/reconnect, duplicate result posts, and expiry.  ·  risk: A command that expires during a legitimate slow task may be skipped; report it clearly and allow explicit retry. Migration must preserve currently pending work by marking existing entries as legacy with a short grace period, not silently deleting them.
- cost: Negligible API cost; a few KB of local JSON/D1 queue metadata and occasional status reads.  ·  latency: No added latency to execution; poll filtering is local. Reconnect may spend one extra round reporting skipped commands.
- security: Reduces stale-command replay risk and records tab/session binding. Do not include page contents or typed secrets in queue status; redact action payloads and retain only type/target/hash.
- depends on: Safari extension heartbeat must include a stable device/session identity when online; Existing browserBridge command/result path and /browser/status route; A small owner-facing formatter for skipped/expired browser work

### `new-surface` — Create a private 'page companion' channel between the Safari extension and the pendant: the extension locally converts the active tab's accessibility tree into numbered semantic chunks, sends only the requested chunk through the relay, and accepts voice commands (next heading, back, focus link N, stop). The relay maintains a short-lived per-tab cursor with sequence/ACK and interruption semantics, so TTS can be stopped and resumed without re-reading or resending the page.
- **owner gets:** The owner can consume and navigate a logged-in web page hands-free, with fast, reliable spoken chunks rather than a single opaque page dump or repeated full-model requests. It works specifically because Safari has the private session and the pendant is always available.
- effort: Large cross-surface feature: extension accessibility-tree extraction and safe element handles, relay cursor/stream protocol, pendant command state, and Mac receipts/tests for tab changes and dropped links.  ·  risk: Dynamic pages may invalidate element handles; detect DOM changes and re-index, then announce that the page changed. Never expose password/hidden fields. If the link target is classified as submit/send/delete/purchase, speak the target and stop before activation.
- cost: Low ongoing model cost because ordinary paging is deterministic; relay stores only a small cursor and transient chunks. Optional summaries invoke the cheaper background model.  ·  latency: First chunk depends on local extraction (target under 2 seconds); subsequent chunks and stop/next commands should be sub-second. A dropped link resumes from the last acknowledged chunk.
- security: Page text remains transient and chunk-scoped; use per-device/tab capability tokens, redact sensitive form controls, and expire the cursor on tab close, URL change, or 15 minutes.
- depends on: A stable Safari extension heartbeat and active-tab identity; An implemented browser command enqueue/result path; Relay support for bidirectional chunk ACKs and interruption; Pendant firmware support for a small navigation state machine and streamed audio control


## What it asked for

_Nothing._
## Its own summary

Fresh discovery found the live browser bridge offline with 10 pending commands, while three persisted sessions still point at old Safari tabs. I recorded a queue-expiry/idempotency change (though the ledger flagged it as close to existing lease-fencing work) and proposed a cross-surface 'Save this page to my notes' flow, explicitly identifying the missing active-tab/selection capture contract and provenance-aware note action. I also alerted mac-planner and unified to the offline/stale-queue defect.

**Biggest unknown:** Safari's real extension is not heartbeating in this round, so I cannot verify whether the persisted sessions can be reattached or whether the 10 pending commands are safe to replay. I still need an online Safari tab/heartbeat (and an implemented enqueue path rather than the currently stubbed granted wrappers) to perform authenticated page work.

