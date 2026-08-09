# Harness derivation — browser-extension — round 161

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“I’m looking at a webpage—tell me what matters, and if I ask, fill in the next steps without sending anything.”"
- **useful because:** This is the browser node’s uniquely valuable interaction: the pendant supplies a hands-free question, Safari supplies the owner’s authenticated page, the Mac planner turns page structure into an answer, and the pendant speaks it back. It avoids the owner copying URLs or screenshots and can safely prepare reversible edits while leaving the final submit visible and under the owner’s control.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → dashboard
- **model tier:** Realtime for the short spoken question and answer; a cheaper background model for page extraction and form-field mapping; no expensive model for raw DOM cleanup.
- **latency:** 2–5 seconds for active-tab extraction and a concise answer; up to 15 seconds for multi-field drafting.
- **cost:** About $0.01–$0.05 per interaction, dominated by page text and a small synthesis call; cache the page capsule within one interaction to avoid resending it.
- **security:** Page text may contain private mail, financial, or work data. Send only the active tab’s extracted, redacted content to the relay; keep raw DOM local to Safari/Mac, do not persist it by default, and show the exact proposed field values before any irreversible submit. Per-origin read/redact/never-store rules must be owner-configured and initially empty.
- **missing:** A working production browser action invocation path exposed to the planner (POST /execute works live, but the granted wrapper tools do not resolve); Active-tab request correlation from a pendant utterance to one browser session; A local redaction-and-page-capsule contract and a spoken preview of staged form mutations

### "“Keep an eye on the private web task I’m in and tell me if it gets stuck—login expired, a deadline moved, a draft was lost, or the site needs me.”"
- **useful because:** Long web tasks fail silently when a session expires or a tab redirects. A browser-local sentinel can watch the tab constellation and draft checkpoints, while the relay classifies only actionable state transitions and the pendant delivers a short offline alert. The Mac can reopen the right origin and restore the last safe checkpoint, something neither a browser alone nor a wearable alone can do.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Background/cheap model for change classification and deduplication; realtime only when the owner asks for the current state or responds to an alert.
- **latency:** Detect within 30–60 seconds; speak an alert in under 3 seconds after classification; restore/reopen in under 10 seconds.
- **cost:** Under $0.01 per poll/change in the normal case; costs are dominated by extracting changed regions, not unchanged pages. Keep DOM and drafts local, sending hashes and small changed snippets.
- **security:** Never transmit full authenticated pages or form values by default. The origin policy must let the owner choose read/extract/redact/never-store per origin; alerts should say “session expired on a private site” rather than expose sensitive text. Restoration must reopen only and never submit or send.
- **missing:** A durable browser watch/checkpoint state machine spanning multiple tabs and redirects; A local-only draft checkpoint store with origin-scoped encryption and expiry; Relay event routing from browser state transitions into offline_alert_inbox

### "“Check these private pages against each other and tell me if anything conflicts—don’t change anything.”"
- **useful because:** The browser can see authenticated sources that the relay cannot, but it cannot reliably reason across tabs without the planner. A cross-tab consistency check can catch a calendar invite that conflicts with a portal deadline, an order page that disagrees with an email, or a changed account status, then speak the conflict and cite which tab said what. This turns browser access into dependable personal verification rather than another page reader.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → dashboard
- **model tier:** Cheap background extraction first; use the realtime tier only to resolve an ambiguous conflict after the owner asks. Deterministic field normalization should precede any model call.
- **latency:** 5–12 seconds for two to five tabs; up to 20 seconds for a large tab set.
- **cost:** Roughly $0.02–$0.08 per check, dominated by sending extracted snippets from multiple tabs. Deduplicate identical text and retain only local hashes plus the final user-approved finding.
- **security:** This necessarily joins private data across origins, so default to an ephemeral in-memory comparison and disclose the origins being compared. Redact account numbers, message bodies, and secrets before relay transmission; never persist raw page text. The owner must explicitly choose the tabs/origins for each check; no silent sweeping.
- **missing:** A browser action that extracts several explicitly selected tab IDs in one correlated request; A schema for normalized claims with source-tab citations and confidence; An ephemeral cross-origin comparison worker with strict deletion on completion

### "“When you tell me something from a private webpage, tell me exactly where it came from, how fresh it is, and let me ask to see the source without rereading the whole page.”"
- **useful because:** Authenticated pages are the one place this system can see information the relay cannot, but a spoken summary otherwise hides whether a fact came from an email, a sidebar advertisement, or a stale cached panel. A provenance card would let the pendant speak “Gmail, message received 8 minutes ago, paragraph 3” and let Safari highlight that exact evidence on demand. This makes private-web assistance trustworthy and auditable rather than merely fluent.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Cheap deterministic extraction for URL/title/timestamp/DOM-anchor and hashing; a small background model for claim-to-span alignment; realtime only for the owner’s spoken follow-up.
- **latency:** Under 2 seconds to attach provenance to a summary; under 3 seconds to focus/highlight the source span in Safari.
- **cost:** Less than $0.01 per claim after extraction; hashes and DOM anchors are tiny. The expensive part is only alignment for pages whose structure is ambiguous.
- **security:** Never send raw private page text merely to create provenance. Generate anchors and hashes locally, redact surrounding text, and expire cards when the page navigates or the session ends. Highlighting must not reveal a hidden sensitive field; apply the owner’s per-origin redaction and never-store policy.
- **missing:** A claim-to-source-span data contract carried from browser_read_page through the planner and spoken response; A Safari command to focus/highlight an evidence anchor and report when it no longer matches; Short-lived provenance-card storage linked to existing evidence capsule IDs

### "“If I lose my Mac or think someone can see it, let me press the pendant once to freeze and hide every logged-in browser session.”"
- **useful because:** The wearable is the only surface continuously on the owner’s body. A physical panic action can cancel queued browser commands, stop page extraction, blank or close authenticated Safari tabs, and signal the relay, without requiring the owner to find the Mac or unlock a dashboard. This protects private sessions in the moment and is materially different from ordinary browser automation.
- **path:** pendant → browser-extension → mac-planner → relay-realtime → dashboard
- **model tier:** No model for the emergency path: a signed deterministic event and local extension handler. Realtime can optionally speak confirmation afterward; background work is unnecessary.
- **latency:** Cancel queued commands immediately and hide/close tabs within 1–2 seconds while the Mac link is alive; relay records the event when connectivity returns.
- **cost:** Negligible API cost; one small signed event and local browser operations. Battery impact is effectively zero beyond the existing button event.
- **security:** This is intentionally destructive to browser state: unsaved drafts may be lost and closing tabs may sign the owner out. Offer a configurable “blank first, close after N seconds” mode, but never require a cloud round trip to execute the local panic action. Use a hardware-bound key, replay protection, and an unmistakable button gesture; do not let a webpage trigger it.
- **missing:** A pendant emergency event that the firmware can emit and the Mac can receive over the current USB serial link; A local Safari extension panic handler that cancels queued commands, clears page capsules, and blanks/closes authenticated tabs; A durable recovery receipt stating which tabs were hidden, closed, or left untouched


## Changes it proposed to its own stack

### `browser-harness` — Add a Safari “private focus” mode that lets the owner pin one tab and optionally select a DOM region; browser_read_page and browser_snapshot then return only that tab/region with a short-lived capsule ID, origin, timestamp, and redaction report. A pendant utterance can reference the pinned capsule until the owner unpins or it expires.
- **owner gets:** Questions about a page become faster and safer: the owner can say “this section” without exposing an entire inbox or account page, and the assistant can keep a stable reference while the owner navigates. It also makes authenticated browser help practical on the pendant’s small conversational context.
- effort: Medium: Safari extension selection/pinning UI, tab affinity in browserSessions.js, capsule expiry and redaction metadata, plus planner plumbing.  ·  risk: A stale capsule could describe an old page or a selected region could omit crucial context. Show origin/title/time in the spoken answer and invalidate on navigation; fall back to a fresh extraction. Recovery is simply re-pin/re-extract.
- cost: Negligible hardware cost; approximately 1–3 KB metadata per capsule and lower model cost because less page text is sent.  ·  latency: Usually reduces extraction and synthesis latency by 30–70%; selection UI adds under a second.
- security: Improves least-data exposure, but selection is not a guarantee against hidden sensitive text in the DOM. Apply existing per-origin redaction and never-store rules before relay transmission.
- depends on: A working browser_read_page/browser_snapshot action path through POST /execute; Origin-policy configuration supplied by the owner rather than hardcoded; Session/tab affinity in local-agent/browserSessions.js


## What it asked for

_Nothing._
## Its own summary

Three new browser-hive capabilities were recorded: an active-tab pendant copilot for authenticated pages, a session/draft failure sentinel that alerts through the offline inbox, and an explicit multi-tab consistency checker. I also proposed Safari private-focus capsules to reduce page-data exposure. Live verification succeeded: Safari has 9 tabs, and POST /execute with browser_list_tabs and browser_read_page works; the active X tab produced a live evidence capsule in 478 ms. I told mac-planner to use this working path rather than the unresolved enqueue wrappers.

**Biggest unknown:** The browser backend can now read pages, but the production planner still lacks a stable, owner-facing correlation from a pendant utterance to an explicitly selected tab/region. We still need the owner’s per-origin read/redact/never-store policy and confirmation of which private sites or tab sets should be used; I will not invent those.

