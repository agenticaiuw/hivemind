# Harness derivation — browser-extension — round 174

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Check the authenticated page I name, and tell me what changed since last time—in one spoken sentence, with the exact section I can open.”"
- **useful because:** This turns the browser's unique access into a dependable owner-facing answer: Safari reads behind-login content, a background relay compares against a redacted prior snapshot, and the pendant delivers only the actionable delta. The owner need not hand the Mac a screenshot or keep the page open.
- **path:** browser-extension → relay-realtime → mac-planner → pendant
- **model tier:** background for scheduled capture/diff and cheap extraction; realtime only when the owner asks for the spoken answer
- **latency:** Scheduled checks under 30 seconds; on-demand answer under 8 seconds, dominated by Safari navigation and authenticated DOM extraction.
- **cost:** Roughly $0.01–$0.04 per check depending on page length; browser and diff dominate latency, not model tokens.
- **security:** Content stays on the Mac/relay only long enough to diff; per-origin configuration must explicitly choose extract/redact/never-store and ship empty until the owner sets it. Never speak or persist configured secret categories. A changed login or MFA page must be reported as 'needs attention', never guessed through.
- **missing:** A durable per-origin watch configuration and redacted snapshot store; A scheduler that can dispatch browser commands while Safari is online; A stable section/anchor locator returned with each extraction; An offline-alert-inbox delivery adapter for the pendant

### "“Fill out this private web form, then read me the exact fields and total it would submit; I’ll approve or cancel from the pendant.”"
- **useful because:** The browser can reach authenticated forms while the pendant is the safest place for a terse final review. This prevents accidental purchases, messages, or destructive account changes without forcing the owner to inspect a tiny Safari window, while still doing all tedious entry automatically.
- **path:** browser-extension → mac-vision → relay-realtime → pendant → mac-planner
- **model tier:** mac-vision/browser automation for field mapping; cheap structured extraction for totals and fields; realtime only for the final spoken review and button decision
- **latency:** Populate and collect preview in 10–25 seconds; spoken review starts within 3 seconds of the preview being ready.
- **cost:** $0.02–$0.08 per preflight, mostly vision/DOM extraction; approval/cancel should cost no model call.
- **security:** The exact outbound payload must be retained only in encrypted volatile state until approval, with origin and expiry bound to it. Never press the final submit/send button before a fresh approval; if the page changes, invalidate the preview. Redact passwords, card numbers, and configured never-speak fields while still showing a safe confirmation such as last four digits.
- **missing:** A browser action transaction scope that can stage but not submit mutations; A canonical form-payload extractor with page-version/hash binding; A pendant approval/cancel event routed back to the waiting browser job; A clear expiry and invalidation mechanism for stale previews

### "“If the private site logs me out while you’re working, pause, tell me which Safari tab needs attention, and resume the exact task after I log back in.”"
- **useful because:** Authenticated browser automation currently fails opaquely when cookies expire or MFA appears. This makes long-running work recoverable: Safari remains the only holder of credentials, the relay preserves a non-secret task checkpoint, and the owner gets a spoken, actionable interruption instead of a silent failure or a dangerous retry.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** cheap classifier for login/MFA/error-page detection and checkpoint serialization; realtime only to announce the interruption and resume result
- **latency:** Detect within one browser poll (under 5 seconds); resume within 10 seconds after the owner completes login.
- **cost:** Under $0.01 per checkpoint/detection; browser polling and DOM capture dominate, with no model call for ordinary steps.
- **security:** Persist only task intent, origin, DOM locator hashes, and redacted field state—never cookies, tokens, passwords, or page text. MFA is always completed by the owner in Safari. Resume only when the origin and page hash match, otherwise re-plan from a fresh read and show the owner what changed.
- **missing:** A browser workflow checkpoint/resume protocol spanning command results; A typed detector for login, MFA, consent, and bot-challenge pages; A pendant-to-browser 'resume/cancel' event path; A redacted, encrypted checkpoint store with TTL and origin binding

### "“Compare the two private accounts I have open—tell me where their settings, access, or balances disagree, and point me to each discrepancy without copying either account’s raw data into memory.”"
- **useful because:** Today the browser can inspect one page at a time, but cannot safely perform a cross-account consistency check. This would catch silent permission drift, duplicate subscriptions, or a stale account setting while keeping raw authenticated content local and returning only structured discrepancies and evidence locations.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** cheap structured extraction and deterministic field comparison first; use a slower model only to normalize labels across sites; realtime only to speak the short discrepancy list
- **latency:** 15–45 seconds for two to five already-open tabs; spoken result within 5 seconds after extraction completes.
- **cost:** $0.02–$0.10 per comparison, dominated by DOM extraction and normalization; no cost for unchanged structured fields.
- **security:** Never send whole page text to the relay. Extract only owner-approved field paths, hash or locally compare sensitive values, and return categories such as 'different' with masked evidence. Each origin needs explicit read/extract/redact/never-store rules, initially empty. Do not click account-changing controls.
- **missing:** A local multi-tab extraction and comparison worker that keeps raw values on the Mac; Per-origin schemas and a user-editable cross-origin field mapping; A privacy-preserving discrepancy receipt containing only masks, hashes, and anchors; A browser command that focuses the exact tab and field for each discrepancy


## Changes it proposed to its own stack

### `interaction` — Add a 'send this answer to Safari' interaction: every browser extraction result carries an origin, tab identifier, and resilient DOM/text anchor; when the owner presses the pendant's follow-up button, the Mac bridge focuses that tab and scrolls to the cited section instead of merely speaking a paraphrase.
- **owner gets:** When the pendant says something important from a private page, the owner can get to the exact evidence hands-free rather than hunting through nine Safari tabs. It makes spoken answers trustworthy and immediately actionable.
- effort: Medium: extend browser_read_page/snapshot result schema with anchor candidates, persist a short-lived tab/anchor receipt, and dispatch a focus-and-scroll browser command from the pendant event.  ·  risk: Dynamic pages may move or virtualize content; fall back to tab focus plus an on-page text search and clearly say the anchor could not be restored. No form submission is involved.
- cost: Negligible API cost; one extra extraction pass when anchors are ambiguous.  ·  latency: Adds 1–3 seconds only when the owner requests navigation to evidence.
- security: Persist URL origin, tab id, and a short redacted quote only; never store cookies or full private page text. Per-origin never-store rules still apply.
- depends on: A durable browser result receipt carrying tabId/origin/anchor; A pendant follow-up event routed to mac-planner; A browser action for focus_tab plus scroll_to_anchor or find_text

### `mac-harness` — Add a local-only browser redaction boundary: Safari page text, screenshots, and form values are parsed on the Mac into a typed, origin-scoped result; the relay receives only the requested answer fields, confidence, and short-lived evidence handles. Make the boundary visible in each spoken response and fail closed when a page has no approved extraction rule.
- **owner gets:** The owner could finally ask questions about logged-in pages without trusting the cloud with the page itself. Sensitive browser use would be useful by default rather than an all-or-nothing choice between no automation and exporting private content.
- effort: High: implement origin policy evaluation, local DOM/vision extraction, typed result schemas, evidence handles, and a test harness that proves raw page text never enters relay requests.  ·  risk: Over-redaction can make answers incomplete; return 'I could not safely extract that' with a local Safari link rather than guessing. A compromised Mac agent remains in scope and must be reported in the receipt.
- cost: Slightly higher Mac CPU; lower relay token cost because page text is not resent. No hardware cost.  ·  latency: Adds 1–4 seconds for local extraction and policy evaluation; avoids repeated cloud context transmission.
- security: Strongly reduces data leaving the Mac, but requires auditable logs and explicit owner-configured per-origin rules. Never persist raw DOM, screenshots, cookies, or credentials.
- depends on: Per-origin policy configuration UI; Typed browser extraction result schema; Local redaction/inspection worker; Short-lived evidence-handle navigation in Safari


## What it asked for

_Nothing._
## Its own summary

Discovered Safari is online with 9 tabs and the Mac bridge is online. I recorded three new browser capabilities: authenticated change reports with evidence anchors, staged private-form previews approved/cancelled from the pendant, and resumable workflows after login/MFA interruption. I also recorded a concrete interaction change that lets a spoken answer focus Safari and scroll to its cited evidence. The owner can already read/click privately in Safari, but the missing value is durable orchestration and safe state across browser, relay, Mac, and pendant—not another browser enqueue wrapper.

**Biggest unknown:** I still need the owner to supply explicit per-origin rules (which authenticated sites may be read, what may be spoken, and what may be persisted); the system must not invent those. Engineering-wise, the largest missing piece is a real browser workflow checkpoint/approval protocol and a working server-side POST /execute dispatch path that this agent can invoke rather than merely resolve symbolically.

