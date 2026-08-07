# Harness derivation — browser-extension — round 127

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“What am I looking at?” (while a private webpage is open)"
- **useful because:** A single pendant button would let the owner get a short spoken explanation of the active logged-in page without dictating a URL or exposing the whole browser session. The browser reads the visible region, the Mac strips unrelated UI, relay summarizes, and the pendant speaks it.
- **path:** pendant → browser-extension → mac-planner → relay-realtime
- **model tier:** Realtime for the one-sentence spoken summary; use a cheaper background model only if the owner asks for detailed extraction.
- **latency:** Under 5 seconds from button press to speech; browser capture and local redaction should take under 1 second.
- **cost:** About $0.002–$0.02 per invocation depending on captured text/audio; browser and local processing dominate latency, not API cost.
- **security:** The active page may contain private mail, health, or financial data. Capture only the rendered viewport or owner-selected element, redact passwords/payment fields locally, send the minimum text to relay, and never click or submit. Show a tiny on-device/browser indicator while capture is active.
- **missing:** A pendant button/event routed to a browser-context request; An extension command that captures the active tab's visible DOM/selection with tabId and bounded size; Mac-side sensitive-field redaction and viewport cropping; A relay route that accepts browser context and returns a spoken summary

### "“Fix the page that failed to open, but don’t change any account data.”"
- **useful because:** When Safari shows a blank/error page or the extension loses frame access, the system would diagnose it instead of making the owner retry blindly: browser reports the failing URL and tab state, Mac checks connectivity and extension health, relay classifies the failure, and the pendant gives one clear explanation plus a repaired read-only tab when safe.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Cheap background model for error classification and retry selection; realtime only for the owner's short status reply.
- **latency:** Initial diagnosis in 3 seconds; one safe recovery attempt within 10 seconds; never loop more than twice.
- **cost:** Typically under $0.005 per incident; most work is local tab inspection and Mac health checks.
- **security:** Never replay a pending click/type/submit command during recovery. Preserve the original tab, open a separate tab for retries, restrict automatic actions to navigation/reload, and include URL/origin in the spoken receipt so a malicious redirect cannot be silently accepted.
- **missing:** A browser error taxonomy that distinguishes extension frame denial, navigation failure, auth expiry, and network failure; A read-only recovery action that opens a fresh tab while retaining the original tab and pending-command queue; Mac connectivity/extension health facts exposed to the relay; A pendant event and concise recovery receipt

### "“Privacy pause.” (or double-press the pendant)"
- **useful because:** The owner should be able to instantly stop the browser agent from reading or acting, even if a long job is running or the Mac is unattended. The pendant would send a physical panic signal; the relay cancels in-flight browser work, Safari disables new commands and obscures private tabs, and the Mac locks or hides the browser. A spoken confirmation says whether anything was already submitted.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** No model is needed for the safety action; use realtime only to explain the resulting receipt if the owner asks.
- **latency:** The pendant-to-relay stop signal should take effect locally in under 500 ms and reach the relay/Mac within 2 seconds. It must work during a dropped LTE link by freezing locally first.
- **cost:** Negligible API cost; modest firmware and extension work. Battery impact is effectively zero if implemented as an interrupt and existing heartbeat channel.
- **security:** This is an emergency stop, not an approval gate. It must be authenticated to the paired pendant, idempotent, and fail-safe: on uncertain link state the extension remains paused. Do not delete tabs or data automatically; preserve a local encrypted receipt and require a later explicit resume. The relay should report any command that crossed the stop boundary.
- **missing:** A dedicated pendant button/gesture interrupt and persistent paused bit in firmware; A signed stop/resume protocol understood by relay, Safari extension, and Mac agent; Extension-side local command freeze that does not depend on relay reachability; A Mac privacy action (hide/lock) and a durable boundary receipt; An explicit resume gesture or spoken command with device authentication

### "“Remember this spot in Safari and bring it back tomorrow.”"
- **useful because:** The owner should be able to leave a private webpage mid-task and later return to the exact tab, scroll position, selected passage, and surrounding context by speaking to the pendant. Today a URL alone loses the authenticated tab state and location; this would make the browser a persistent second workspace rather than a disposable session.
- **path:** pendant → browser-extension → relay-realtime → mac-planner
- **model tier:** Cheap background extraction for a short title/anchor; realtime only when the owner asks to recall or jump back.
- **latency:** Save in under 2 seconds; restore in under 5 seconds when Safari is online.
- **cost:** Below $0.005 per save/recall; storage and tab operations dominate.
- **security:** Store an encrypted opaque session reference, not page contents by default. Bind it to the owner and expiry, disclose the origin/title on recall, and invalidate it on logout or tab closure. Never restore a stale form with typed unsent data.
- **missing:** Extension support for stable DOM anchors plus scroll/selection capture; Encrypted, expiring browser bookmarks bound to Safari session/tab identity; A restore operation that reattaches or opens the authenticated tab and verifies origin before scrolling; Pendant voice/button intents for save and recall

### "“Read this private page to me, one useful section at a time.”"
- **useful because:** The owner should be able to consume an authenticated webpage while walking without staring at Safari. The extension would extract semantic headings, lists, tables, and actionable fields, the relay would narrate only the requested chunk, and pendant buttons would advance/back up or say “repeat.” This is more reliable than a giant summary for long portals and preserves the page's structure.
- **path:** browser-extension → relay-realtime → pendant → mac-planner
- **model tier:** Cheap model for structure-preserving chunk selection and compression; realtime only for low-latency narration and button turns.
- **latency:** First chunk in under 4 seconds; next/previous chunk in under 1 second from a cached local queue.
- **cost:** Roughly $0.005–$0.03 per page depending on length; cache each page's redacted chunks so navigation does not resend context.
- **security:** Extract only visible/allowed regions, redact credential and payment fields locally, and show origin/title before narration. Do not speak secrets by default; require an explicit local gesture for a sensitive field. Expire the cache when the tab logs out or closes.
- **missing:** An extension semantic extractor that emits bounded, ordered page chunks; A per-tab encrypted narration cache with invalidation on DOM change; Pendant next/previous/repeat controls and a playback queue protocol; Relay support for chunked browser context rather than one-shot page summaries


## Changes it proposed to its own stack

### `browser-harness` — Add a local “minimum necessary page” compiler in the Safari bridge. Before any browser_read_page/snapshot result leaves the Mac, classify DOM fields and replace password inputs, payment numbers, authentication tokens, personal identifiers, and hidden/offscreen content with typed placeholders. Permit an explicit per-request selector/region allowlist, emit a redaction manifest with tabId, URL origin, and hashes, and fail closed when a page cannot be classified rather than uploading raw HTML.
- **owner gets:** The owner can finally ask the system to inspect private pages without wondering whether a password, token, or unrelated mailbox content was sent to a model. Summaries stay useful while sensitive material remains on the Mac.
- effort: Medium: DOM traversal/classification in the extension/local agent, bounded rules plus tests against Gmail and common forms, and plumbing the manifest through receipts.  ·  risk: Over-redaction could make a page impossible to understand; recover by allowing the owner to select a visible region or explicitly request raw local-only inspection. A classifier bug could miss novel secrets, so never claim perfect protection and keep raw content local.
- cost: No meaningful API increase; may reduce tokens and therefore cost. Local CPU under 100 ms for typical pages.  ·  latency: Adds roughly 50–200 ms before model submission.
- security: Strongly reduces accidental exfiltration of credentials and unrelated private data, while preserving provenance of every redacted field. This is data minimization, not an approval gate.
- depends on: A browser result envelope that carries tabId/origin and bounded extracted text; A model request path that accepts redacted text plus the redaction manifest; Owner-visible indication of whether the result was fully or partially redacted


## What it asked for

_Nothing._
## Its own summary

Three distinct browser contributions this round: (1) a pendant-triggered “What am I looking at?” private-page explanation spanning pendant → Safari → Mac redaction → relay → audio; (2) read-only browser incident triage that diagnoses frame denial/auth/network failures and retries in a fresh tab without replaying pending mutations; (3) a local minimum-necessary DOM compiler that redacts credentials, payment data, tokens, and unrelated/offscreen content before model submission. I also verified the real Safari bridge is online with three tabs, including logged-in Gmail tab 901464. However, reads/snapshots of that Gmail tab currently fail because the extension lacks access to the frame, so the browser is online but not yet useful for authenticated extraction.

**Biggest unknown:** Whether the Safari extension can be granted content-script access to Gmail (or whether recovery must open a fresh same-origin tab). The browser enqueue grants remain schema/stub tools; direct POST /execute works, but a production browser tool should expose the working path and return typed results.

