# Harness derivation — browser-extension — round 89

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser bridge live state** — As of round 89, all five granted browser enqueue wrappers still return 'schema but has no implementation'. POST /execute browser_navigate timed out; GET /browser/status reports online:false, only stale home-chrome, and pendingCommands=8. Existing browser sessions are stale records, not proof of live tabs.
  - evidence: Tool calls in this round: browser_command_enqueue(list_tabs) and browser_enqueue_command_implemented(list_tabs) both implementation errors; POST /execute browser_navigate no response within 20s; GET /browser/status returned online:false and pendingCommands:8; GET /browser/sessions returned old tabs last used 2026-08-07T06:26Z.

## Capabilities it proposed

### "Save the appointment/order/delivery date on this logged-in page to my calendar."
- **useful because:** The browser is the only node that can see dates behind the owner's existing logins; the Mac is the only node that can write a calendar/reminder; the pendant provides the natural spoken trigger and confirmation, while the relay can continue if the Mac briefly drops offline. This turns a page the owner is looking at into a useful personal action without copying details by hand.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → dashboard
- **model tier:** Use realtime only to capture the short spoken intent and ask a concise clarification if the page has multiple dates; use a cheaper background model to extract date/time/timezone/title/location from browser text and produce a confidence-scored structured event.
- **latency:** Read the active page and return a proposed event in under 8 seconds; calendar/reminder creation in under 5 seconds after the owner says save. If the browser or Mac is offline, retain the extracted candidate and resume rather than silently dropping it.
- **cost:** Roughly one small background extraction call plus one short realtime turn; typically <$0.01 per invocation, dominated by page-text tokens. Avoid sending unrelated page content by extracting only date-bearing regions and a short citation.
- **security:** Authenticated page text may contain private order or health information; keep extraction and citations local to the Mac/relay, redact unrelated text, and show the exact title/date/time/timezone/location before writing. Creating a reminder is reversible, but never submit forms or send messages as part of this workflow.
- **missing:** A browser-to-event extractor that returns normalized ISO date/time, timezone, title, location, source URL and evidence text; A durable pending-event record linking the browser tab/session to the Mac reminder receipt; A resume path when the Safari extension or Mac bridge is offline


## Changes it proposed to its own stack

### `browser-harness` — Add a browser-command lease and reconnect reconciler. Every queued browser command gets createdAt, intended device/tab/session, idempotency key, and expiresAt (short default for reads; explicit longer lease for a user-requested workflow). When the extension is offline or returns, discard expired commands and mark them stale instead of replaying them; on reconnect, return a compact reconciliation listing applied, expired, and still-pending commands. Expose a one-call purge for stale pending commands and include the lease state in browser status.
- **owner gets:** The owner will not have an old navigation, click, or form-fill unexpectedly execute hours later when Safari reconnects. Today the live bridge is offline with 8 pending commands, so this is an immediate safety and predictability problem even under the owner's maximum-access/no-gates policy.
- effort: Medium: extend browserBridge command records, poll/result handling, status serialization, and add tests for offline timeout, reconnect, duplicate result, and tab mismatch.  ·  risk: An actually desired long-running read could expire; callers can request an explicit lease. A command could be marked stale after execution but before its result arrives; reconcile by accepting late typed results keyed by idempotency key. Recovery is visible status plus manual retry, never silent replay.
- cost: Negligible API cost and storage (a few hundred bytes per command plus bounded audit metadata).  ·  latency: No added latency while online; offline commands are resolved immediately as pending/expired rather than waiting for the 45-second browser result timeout.
- security: Reduces delayed-action and wrong-tab risk. Keep page content out of reconciliation records; retain only command type, target/session hash, timestamps, and result status.
- depends on: A working extension enqueue/poll path must report device identity and tab/session affinity; The existing DELETE /browser/commands/:commandId? cancellation route should share the same state machine; Existing browser result receipts should persist idempotency keys

### `browser-harness` — Build a local, policy-driven page-minimization layer in the Safari extension. Before authenticated page content leaves the browser, the extension should extract only the requested semantic fields (for example: dates, sender, subject, amount, status, or visible form labels), redact passwords, payment details, tokens, health identifiers, and unrelated DOM regions, and attach the source URL plus a short DOM citation. The relay/model receives the minimized typed payload rather than an entire page dump. If extraction confidence is low, return a redacted preview and ask the owner to name the needed field instead of escalating to full-page transfer. Maintain an owner-visible audit record of what fields crossed the boundary.
- **owner gets:** Today the owner cannot safely use the browser tier for many authenticated pages: answering a simple question may transmit an entire private page, including secrets or unrelated personal data. This would let them use the pendant to get precise answers from logged-in sites while keeping most of the page inside Safari, without adding an approval gate to ordinary actions.
- effort: High: extension-side DOM semantic extraction and redaction rules, a typed request contract from the planner, per-origin rule storage, citation generation, and end-to-end tests across dynamic pages and iframes. Requires changing the extension protocol and the browser bridge, not merely prompt instructions.  ·  risk: A redaction rule can hide a field or misclassify sensitive text; fail closed for unknown sensitive-looking regions, expose extraction confidence, and permit an explicit owner-selected field expansion. Dynamic sites may defeat selectors; fall back to accessibility-tree fields and retain only the minimum requested region. Recovery is a clearly labeled local preview, never silent full-page upload.
- cost: Small additional extension CPU and storage cost; lower model/API cost because fewer tokens leave the browser. No hardware cost. Rule updates and audits require engineering and maintenance.  ·  latency: Adds roughly 100–500 ms for local extraction on ordinary pages; it should reduce model latency substantially by shrinking context. Complex pages may take a few seconds and should report progress.
- security: Strongly improves privacy by enforcing data minimization before the relay/model boundary. Keep credentials and raw DOM local; encrypt and rotate the field-level audit log; never include redacted values in diagnostics or failure traces.
- depends on: A real browser enqueue implementation and extension protocol capable of typed extraction requests/results; A planner contract that declares the minimum fields needed for each browser question; Extension-side secure storage for per-origin redaction/extraction policies; A relay-side schema validator that rejects unexpected fields


## What it asked for

_Nothing._
