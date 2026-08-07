# Harness derivation — browser-extension — round 110

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-extension live bridge** — The real Safari device is currently absent/offline: GET /browser/status reports online=false, only home-chrome with tabCount null and pendingCommands=10. Server-side browser sessions still reference three historical tabs, and two disabled watches retain old observations.
  - evidence: GET /browser/status 200: {online:false, devices:[home-chrome offline], pendingCommands:10}; GET /browser/sessions 200 lists default/probe-form/probe-form2; GET /watches 200 lists two enabled=false test watches.

## Capabilities it proposed

### "“Save this page for me with the important details and remind me what I need to do next.”"
- **useful because:** The owner can turn an authenticated page they are already viewing—an invoice, appointment, support case, or work item—into a durable, sourced handoff without copying text or losing the login context. The pendant can confirm the short summary, while the Mac keeps the evidence and creates only the requested follow-up.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use the cheaper background tier for page extraction, normalization, and reminder drafting; use realtime only to interpret the spoken request and read back a concise confirmation.
- **latency:** Capture and first summary within 10–20 seconds while the tab is available; reminder creation follows immediately after the owner confirms the extracted due date or next action.
- **cost:** Low: one browser read/extract plus one background summarization and optional reminder write; dominant cost is page text sent to the model, capped to the relevant region rather than the whole DOM.
- **security:** The page may contain private or financial data. Keep raw page text on the Mac, send only selected excerpts/fields to the model, attach URL/tab/timestamp and content hash as provenance, and never include cookies or hidden form fields. Creating a reminder is reversible; do not submit forms or send messages.
- **missing:** A first-class browser-to-capture handoff that binds the active tab/session to a durable case record; Field-level redaction and excerpt selection before model submission; A cited spoken summary plus reminder draft linking back to the captured page; Working browser enqueue implementation and a live Safari heartbeat (currently offline with 10 pending commands)

### "“Put me back exactly where I left off in Safari and tell me what changed since then.”"
- **useful because:** Today, closing a laptop or losing a tab destroys the owner's working context—even when the site is still logged in. This would restore the specific authenticated task, not merely reopen a URL: the right tab, scroll position, focused control, selected text, and an optional locally encrypted unsent draft, then explain only changes relevant to that task. It is especially valuable for long-running applications, support cases, and forms that cannot be safely represented by a bookmark.
- **path:** browser-extension → mac-planner → mac-vision → relay-realtime → pendant
- **model tier:** Background model compares the saved task snapshot with a fresh page and produces a compact change summary; realtime only handles the owner's spoken 'resume that' request and reads back the result. mac-vision is used only when normal tab restoration cannot restore scroll/focus and a visual repair is needed.
- **latency:** Restore the tab immediately, then provide the change summary within 15 seconds; visual repair may take up to 30 seconds and must report uncertainty rather than guessing.
- **cost:** Low to moderate per resume: one authenticated page snapshot and a bounded diff; cost is dominated by changed page text or screenshot tokens. Local snapshot storage is negligible.
- **security:** Task snapshots can contain private account data and typed-but-unsent secrets. Store them encrypted on the Mac, exclude passwords/payment fields and sensitive DOM attributes by default, redact before model submission, and never sync raw drafts through the relay. Restoration must never press submit, send, purchase, or otherwise commit a form.
- **missing:** A browser extension task-context capture protocol for tab identity, scroll/focus/selection, viewport, and safe form-draft metadata—not just URL/session records; Encrypted durable task snapshots with explicit owner naming and retention/deletion controls; A semantic changed-since-snapshot diff that can distinguish task-relevant edits from timestamps, ads, and volatile counters; A reconnect-safe restore operation spanning Safari extension, Mac planner, and optional mac-vision visual correction; Pendant affordances for naming, resuming, and deleting saved task contexts


## Changes it proposed to its own stack

### `browser-harness` — Add an offline/reconnect command-lease reconciler to the Safari browser bridge. When an extension heartbeat disappears, mark all pending browser commands as suspended (not runnable); expire navigation/read commands after a short configurable lease and preserve only explicitly resumable read steps. On reconnect, require a tab fingerprint (extensionId, tabId/windowId, URL origin, title hash) match before resuming; otherwise return typed 'stale_target' results and leave the queue untouched. Add GET /browser/commands?state=... and a compact reconciliation receipt so the Mac/relay can tell the owner what was skipped, expired, or safely resumed. This complements (rather than repeats) the existing request IDs/idempotency and missing progress/resumable polling work.
- **owner gets:** If Safari sleeps, is closed, or the owner switches tabs, queued browser work will not unexpectedly run against a different logged-in page when the extension returns. Long reads can resume safely, while stale actions become visible instead of silently disappearing; the owner gets an accurate spoken status rather than a false 'done'.
- effort: Medium: browserBridge state machine and lease metadata, heartbeat transition handling, tab fingerprint comparison, one inspection/status route, and relay/journal wiring; test offline, reconnect, tab replacement, and duplicate result cases.  ·  risk: A legitimate long-running read may expire and need restarting; resumable steps are limited to idempotent navigation/read/extract. Recovery is explicit restart from the reconciliation receipt. No browser content needs to leave the Mac beyond existing result paths.
- cost: Negligible API cost; a few bytes of queue metadata per command and occasional heartbeat/status requests.  ·  latency: No added latency while online; reconnect adds one heartbeat plus fingerprint check before resumption.
- security: Improves safety for authenticated sessions by preventing stale commands from replaying on a changed tab. Fingerprints should hash title/URL rather than persist page text; never log cookies or extracted secrets.
- depends on: chg-14accc01 request IDs/tab affinity and future progress/resumable polling; Existing GET /browser/status and POST /browser/heartbeat; Existing GET /browser/sessions and journal/action receipts


## What it asked for

_Nothing._
## Its own summary

Discovered the live browser bridge is offline: Safari is not reporting, home-chrome is offline, and 10 commands are pending; historical sessions and two disabled watches remain on disk. I recorded this finding, informed mac-planner, and proposed a new heartbeat-aware stale-command reconciler that suspends/leases queued work and verifies tab fingerprints before reconnect replay. I also proposed a cross-surface 'save this authenticated page and remind me' workflow, but the backend explicitly notes it is connective work across existing routes rather than a missing primitive.

**Biggest unknown:** I still cannot inspect an authenticated page or validate the new queue behavior until the real Safari extension heartbeats again and one of the granted browser enqueue tools has a working implementation. The remaining concrete need is the bridge implementation plus a live tab; no additional owner context request is needed this round.

