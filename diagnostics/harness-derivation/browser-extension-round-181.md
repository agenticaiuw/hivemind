# Harness derivation — browser-extension — round 181

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser live state** — Safari extension is online with 9 tabs; active tab is X at https://x.com, tabId 1163292, no pending commands. Browser is no longer tabless and can be used for authenticated work.
  - evidence: GET /browser/status returned online=true, tabCount=9, tabUrl=https://x.com, tabId=1163292, pendingCommands=0.

## Capabilities it proposed

### "“While I’m on a logged-in webpage, explain what I’m looking at and guide me through the next safe step without taking over.”"
- **useful because:** The browser is the only node that sees the owner’s authenticated page, while the pendant is the only node available when their eyes are busy. A low-latency page companion can turn dense dashboards and forms into spoken, contextual guidance, with the Mac/browser performing only the reversible navigation requested.
- **path:** browser-extension → mac-vision → mac-planner → relay-realtime → pendant
- **model tier:** Realtime for short DOM/accessibility summaries and spoken turn-taking; background model for long-page semantic indexing and cheaper local rule extraction.
- **latency:** Under 1.5 s for an explanation after a page/scroll change; under 3 s for a suggested next step.
- **cost:** Realtime usage only while explicitly companion mode is active; roughly $0.01–$0.05 per minute depending on screenshot frequency. DOM extraction and diffing should be local and dominate no API cost.
- **security:** Page content leaves the Mac only for the active turn unless the origin policy says otherwise. Default to accessibility tree and selected text rather than screenshots; redact passwords, payment fields, tokens, and configured categories. Never click a submit/send/purchase control without an explicit spoken command, and show the target label first.
- **missing:** A browser companion stream that emits page accessibility deltas and viewport context, rather than one-shot reads; A relay-realtime conversation mode that binds each utterance to the current tab and DOM snapshot; A visible overlay/pendant protocol for citing the current control and stopping on high-impact controls

### "“When you answer a question from one of my logged-in websites, prove exactly where it came from and let me say ‘show me’ to return to that spot.”"
- **useful because:** Authenticated answers are otherwise unverifiable summaries. A compact provenance receipt lets the owner trust or challenge an answer, and the browser can reopen the exact origin, tab, heading, and selector while the pendant speaks a concise citation. This is valuable for bills, policies, work dashboards, and any page where a wrong number matters.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Cheaper background model creates structured citations from extracted DOM; realtime only resolves follow-up questions and executes the owner’s ‘show me’ navigation.
- **latency:** Citation attached within 2 s of extraction; ‘show me’ should focus the original tab/control within 3 s.
- **cost:** Usually under $0.01 per page because structured DOM spans and hashes are small; no model call for deterministic selector/URL/timestamp receipts.
- **security:** Persist only URL origin, title, heading path, selector, timestamp, and a salted content hash by default—not page text or screenshots. Per-origin rules can disable persistence entirely. Do not expose query strings, account IDs, or secrets in spoken citations. Reopening a page is reversible; mutations remain confirmation-required by product policy.
- **missing:** A stable provenance schema shared by browser results, relay replies, and job receipts; Selector validation/fallback when the page changes, with explicit ‘source changed’ reporting instead of silently pointing elsewhere; A pendant action phrase and browser command to focus/highlight the cited span

### "“Keep an authenticated page open as a private watch, and tell me on the pendant only when a meaningful thing changes—then let me inspect the before/after without storing the page.”"
- **useful because:** The owner should not have to repeatedly visit portals to notice a changed appointment, price, deadline, or account status. The browser keeps the session; a relay-side semantic diff filters cosmetic changes; the Mac can reopen the page and the pendant delivers an offline-capable alert. This turns login-bound information into an actionable signal without making the cloud a copy of the site.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → mac-vision
- **model tier:** Background/scheduled model or deterministic DOM diff for polling and semantic change classification; realtime only when the owner asks follow-up questions or requests a page reopen.
- **latency:** Polling cadence set per origin (5 minutes to daily); alert generation under 10 s after a detected meaningful change; spoken follow-up under 2 s.
- **cost:** Low: DOM hashing and field-level diffs are local; batch semantic classification roughly $0.001–$0.02 per check. Browser polling and relay storage are the main non-model costs.
- **security:** Ship empty per-origin configuration and require the owner to choose origins, cadence, fields, and read-aloud categories. Store only redacted change summaries plus before/after hashes; never persist raw page text by default. Pause watches when the session expires, report that state, and never auto-submit a resulting action.
- **missing:** A durable authenticated page-watch scheduler using browser sessions and originFanOut/redaction policy; Meaningful-change classification that understands dates, amounts, status, and deadlines while ignoring ads/layout churn; A watch-to-pendant delivery bridge and a ‘reopen/compare’ browser action

### "“Compare the information in these logged-in tabs, tell me where they disagree, and give me the one decision I need to make.”"
- **useful because:** Important personal decisions often span several authenticated pages—policy terms versus an account dashboard, an appointment portal versus an email confirmation, or two internal systems. No single node can see all those sessions. The browser gathers the selected tabs, the Mac structures fields, and the relay turns contradictions into one short spoken decision brief instead of a page-by-page dump.
- **path:** browser-extension → mac-vision → mac-planner → relay-realtime → pendant
- **model tier:** Background model extracts normalized facts and conflict sets from each tab; realtime model only handles the owner’s follow-up and speaks the final ranked decision brief.
- **latency:** Initial comparison in 10–20 s for up to six tabs; follow-up under 2 s. Show progress rather than blocking on a slow portal.
- **cost:** Roughly $0.03–$0.20 per comparison depending on page volume; DOM extraction, deduplication, and conflict detection should be local before model use.
- **security:** The owner explicitly selects tabs or origins for each comparison. Never merge unrelated sessions automatically. Apply existing per-origin redaction and do not persist raw page text; keep only normalized claims, source anchors, and expiry. Spoken output must omit configured private categories. Any resulting action is presented as a draft and not submitted.
- **missing:** A multi-tab selection and capture operation with stable tab IDs; A normalized claim/conflict representation with source anchors and freshness/expiry; A relay brief that can speak uncertainty and ask which source to trust

### "“Lock down my browser right now.”"
- **useful because:** If the owner loses the Mac, suspects an exposed session, or simply wants to leave a shared environment, they need an immediate physical escape hatch. A pendant command would pause queued browser work, close or quarantine authenticated tabs, revoke the bridge’s browser lease, and report completion over the speaker—even when the owner cannot reach the Mac keyboard.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** Deterministic control path; no expensive model call. Realtime is only needed to disambiguate a spoken request such as ‘lock browser’ versus ‘lock the Mac’.
- **latency:** Begin within 1 second and confirm state within 5 seconds.
- **cost:** Negligible API cost; implementation is local bridge/extension work.
- **security:** This is deliberately a high-impact defensive action, so it needs an unmistakable physical button chord or spoken challenge phrase, plus a local confirmation tone. It must not delete cookies or stored passwords by default; it should suspend tabs, cancel browser commands, and invalidate the extension lease. Recovery requires explicit local unlock or a pendant-held recovery code.
- **missing:** A pendant-to-browser emergency command with offline queuing; An extension endpoint that cancels in-flight commands and quarantines authenticated tabs; A browser-session lease/revocation state shared with the relay and Mac agent

### "“Find the thing I need to do on this website, and keep working through the site until it is ready for me to review.”"
- **useful because:** Many authenticated tasks are not one action: locate a buried form, gather values from several pages, fill a draft, handle pagination, and stop at the final irreversible step. The owner should be able to hand this to the browser while doing something else, receive progress on the pendant, and resume after an expired tab/session rather than starting over.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → mac-vision
- **model tier:** Background model for multi-step planning and page interpretation; realtime only for progress updates, interruptions, and owner decisions.
- **latency:** Start in under 3 seconds; progress every 30–60 seconds; checkpoint after each page; recovery after a session interruption within 15 seconds.
- **cost:** Approximately $0.05–$0.50 per complex task, dominated by model interpretation of changing pages; deterministic navigation and field extraction should be local.
- **security:** Persist a task plan and checkpoints, not page text. Existing origin/redaction rules must apply at every checkpoint. Stop before submission, payment, deletion, or sending a message and speak the exact pending action. The owner can cancel from the pendant, which must invalidate the browser lease and discard sensitive drafts.
- **missing:** Durable browser task checkpoints with tab/session reattachment; A progress and interruption protocol from browser to relay to pendant; A reliable final-action boundary that exposes the exact pending mutation without submitting it

### "“Make this website usable by voice: move to the next meaningful control, tell me its purpose, and let me activate it.”"
- **useful because:** Authenticated web apps often bury critical controls in dense tables, unlabeled icon buttons, or inaccessible custom widgets. A semantic voice cursor would let the owner operate those sites hands-free through the pendant without requiring a visual computer-use loop, while still exposing the exact control before activation.
- **path:** browser-extension → relay-realtime → pendant → mac-vision
- **model tier:** Local accessibility-tree parsing and deterministic focus movement for ordinary controls; realtime model only interprets ambiguous natural-language targets and speaks concise descriptions.
- **latency:** Focus/description response under 700 ms; ambiguous target resolution under 2 seconds.
- **cost:** Near-zero for accessibility-tree traversal; occasional realtime turns under $0.01 each.
- **security:** Never infer a destructive action from vague speech. Announce role, label, and nearby context before activation. Respect origin redaction and avoid speaking field values marked private. Maintain a visible Safari focus ring and a pendant cancel action.
- **missing:** Extension support for accessibility-tree extraction and semantic focus targets; A browser action for focus-next/focus-by-role/focus-by-label; A compact spoken-control protocol and cancellation behavior on the pendant


## What it asked for

_Nothing._
