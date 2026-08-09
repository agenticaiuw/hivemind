# Harness derivation — browser-extension — round 209

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser tab identity integrity** — Safari is online with 6 tabs. A POST /execute browser_read_page request carrying tabId 3658596 returned content from tabId 3709209 (active ChatGPT tab), while the response claimed success. Browser results must be identity-checked before any summary or mutation.
  - evidence: Live POST /execute at 2026-08-08T23:10:02Z: requested tabId=3658596, response browser.tabId=3709209 and URL chatgpt.com.

## Capabilities it proposed

### "Watch this authenticated page for me for the next week; when a meaningful change appears, summarize only the changed claims and put an alert on my pendant, with a link I can open in Safari."
- **useful because:** It turns a logged-in browser session into an always-useful monitoring service for pages that have no API—ticket status, account notices, dashboards, or private work queues—without reading the whole page aloud or repeatedly waking the expensive voice model.
- **path:** browser-extension → relay-realtime → pendant → mac-planner
- **model tier:** Scheduled/background extraction and cheap semantic diffing; realtime only when the owner asks follow-up questions from the alert. Use the relay as the durable scheduler and the pendant’s offline_alert_inbox for delivery across a dropped Mac link.
- **latency:** Polling cadence chosen per page (5 minutes to daily); a detected change becomes an alert within 60 seconds. Follow-up answer under 2 seconds if the page remains available.
- **cost:** Roughly $0.001–$0.02 per check depending on page size and model use; semantic diff should run locally/cheaply and only changed claims should reach a model.
- **security:** Default to an owner-triggered watch with an explicit expiry, no screenshots or page bodies persisted, 24-hour browser-fact TTL, host/URL provenance, and redaction of secrets. Alerts should contain only the changed claim and a deep link; never speak categories the owner later marks private. Pause on login expiry or unexpected origin change.
- **missing:** A durable browser watch scheduler with expiry and backoff; A semantic claim-diff route that builds on browser findings rather than storing page text; A notification route from relay/browser jobs into offline_alert_inbox

### "I’m switching tasks—give me a 30-second spoken handoff of the useful things across the tabs I have open, and leave each source as a one-tap link so I can return to it later."
- **useful because:** Safari currently has multiple unrelated authenticated/public tabs. The browser can see them, but today the owner must manually revisit each one. A temporary cross-tab handoff would turn scattered browsing into an actionable briefing without saving whole pages or requiring a new research session.
- **path:** browser-extension → relay-realtime → pendant → mac-planner
- **model tier:** Local extraction and cheap clustering first; a small background model makes the cross-tab topic/priority summary. Realtime speaks only the final compressed handoff and answers a follow-up about one cited tab.
- **latency:** Read six to ten tabs in under 8 seconds, produce a 30-second summary within 3 seconds after extraction, and let the owner ask about a cited tab in under 2 seconds.
- **cost:** About $0.01–$0.03 per handoff; browser reads and context transfer dominate, so cap extracted text per tab and summarize incrementally.
- **security:** Never include page text from tabs the owner did not explicitly select; default to titles/URLs plus a short claim sample. Treat ChatGPT, Discord, X, and work tabs as potentially sensitive. Keep the handoff ephemeral, do not write page bodies to memory, and expose provenance for every spoken bullet. A link opens the tab but does not submit or mutate anything.
- **missing:** A multi-tab selection/read action that preserves tab identity and ordering; A transient context-pack object with per-claim provenance and expiry; A pendant affordance for replaying one cited source without rereading the entire handoff

### "If a browser task gets stopped by a login timeout, tell me on the pendant, let me re-authenticate in Safari, and resume exactly where you left off without repeating or losing the work."
- **useful because:** Authenticated browser work fails today at the least visible point: a session expires, the automation reports an error, and the owner must reconstruct what was read or typed. Durable task continuation would make private sites dependable rather than one-shot scripts, especially for long forms, dashboards, and multi-step workflows.
- **path:** browser-extension → relay-realtime → pendant → mac-planner
- **model tier:** Background/local state machine detects login walls and preserves a structured task checkpoint; realtime is used only to explain the interruption and confirm resume. No model call is needed for every browser action.
- **latency:** Detect the expired session within one browser action; pendant alert within 10 seconds. After re-authentication, resume within 3 seconds and replay no irreversible action.
- **cost:** Under $0.01 per interruption; most work is browser polling and encrypted checkpoint storage, not inference.
- **security:** Never store passwords, MFA codes, cookies, or page bodies. Checkpoints contain only action state, field identities, and short-lived redacted claims. Bind the checkpoint to the original origin and tab identity, invalidate it if the origin changes, and stop before any irreversible action whose page state may have changed.
- **missing:** A browser session-expiry detector that distinguishes a login wall from an ordinary page error; Encrypted, expiring task checkpoints shared between browser extension and relay; A pendant alert/resume protocol carrying the paused task ID; Origin and tab identity validation before checkpoint replay

### "Later, let me say “open the page where we saw that price” or “which tab had the refund policy?” and have Safari return to the exact authenticated source from our earlier conversation."
- **useful because:** Browser sessions are otherwise a pile of titles and URLs. Linking a spoken claim to the exact tab and conversation moment lets the owner recover sources naturally, even after switching tasks, without asking the assistant to reread or guessing among similar pages.
- **path:** browser-extension → relay-realtime → pendant → mac-planner
- **model tier:** Cheap local claim/entity matching over short-lived browser evidence; realtime only resolves ambiguity when several tabs match and speaks the result. No full-page reprocessing is required.
- **latency:** Resolve a unique source in under 2 seconds; if ambiguous, ask one short clarification and open immediately after the answer.
- **cost:** Less than $0.01 per lookup; the dominant cost is retaining compact claim-to-tab links, not model inference.
- **security:** Store only short claims, host, URL, tab identity, and expiry—not page bodies or screenshots. Require origin validation before reopening; private claims should remain task-scoped and never enter unrelated voice context. Opening is reversible and read-only; do not automatically submit or mutate the page.
- **missing:** A conversation-to-browser evidence link with an expiry longer than a single command; Natural-language source resolution across browser provenance and conversation context; A safe reopen action that verifies the tab URL/origin before focusing it

### "While you are helping in Safari, let me edit the page myself; notice when I change something, explain the conflict briefly, and continue from my version instead of overwriting it."
- **useful because:** Browser automation and human editing currently compete for the same live page. A cooperative mode would let the owner take over naturally—correcting a field, changing a selection, or navigating—without stale automation undoing the change or silently acting on an obsolete form.
- **path:** browser-extension → relay-realtime → pendant → mac-planner
- **model tier:** The extension and local harness detect DOM/navigation divergence deterministically; a small model summarizes only genuine conflicts. Realtime is reserved for a short pendant clarification when the owner’s change makes the next step ambiguous.
- **latency:** Detect divergence on the next action or within 1 second of a navigation; speak a conflict summary within 3 seconds; resume within 2 seconds after clarification.
- **cost:** Near-zero for ordinary edits; approximately $0.005–$0.02 only when a conflict needs semantic comparison.
- **security:** Never capture keystrokes globally or store full field values. Observe only the task’s declared selectors/fields, redact secrets, bind state to origin and tab, and stop rather than overwrite when a changed field is sensitive or ambiguous.
- **missing:** A task-scoped DOM mutation/navigation observer in the extension; A versioned browser task state with owner-vs-agent provenance for each field; A resume protocol that can accept owner edits as authoritative


## Changes it proposed to its own stack

### `browser-harness` — Make every browser action carry an immutable tabId and verify the extension result’s tabId, URL, and title against it before returning success; if they differ, fail closed with the requested and observed tab identities and do not create a memory finding. Add a recovery option that re-lists tabs and asks the planner to choose, rather than silently using the active tab.
- **owner gets:** Today a request aimed at one tab can return content from another: a live read addressed tab 3658596 but the result contained the active ChatGPT tab 3709209. Without this guard, the assistant could summarize or fill the wrong logged-in page while claiming success.
- effort: Medium: propagate tabId through browserBridge/browserPage and extension result validation; add mismatch receipts and planner recovery.  ·  risk: Some existing commands omit tabId and would need explicit default semantics; recovery may add one round trip. Roll back by warning-only logging if extension versions cannot echo identity.
- cost: Negligible API cost; a failed/mismatched command costs one extra browser round trip.  ·  latency: ~0.1–0.5 s verification; mismatch recovery adds 1–3 s.
- security: Strongly positive: prevents cross-tab data confusion and wrong-origin mutations. Do not persist mismatch content.
- depends on: Safari extension must echo the requested tabId/windowId in every browser result; POST /execute receipt schema must expose requested vs observed identity


## What it asked for

_Nothing._
