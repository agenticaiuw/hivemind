# Harness derivation — browser-extension — round 191

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser live state** — Safari extension is online with two tabs: ChatGPT conversation “NY vs Taipei Experience” (tab 1323211) and active YouTube video “Inside Taiwan's New World Record Bridge…” (tab 1419527). POST /execute browser_list_tabs and browser_read_page work now, despite the earlier no-tab state.
  - evidence: POST /execute browser_list_tabs returned 2 tabs and browser_read_page for tab 1419527 returned page text and evidence capsule.

## Capabilities it proposed

### "When I say “check this against the real source,” compare the page I’m looking at in Safari with a second authoritative source, tell me exactly what conflicts, and put only the unresolved discrepancy on my pendant."
- **useful because:** The browser is the only node with my logged-in page, while the relay can query public sources and the pendant can interrupt me. This turns silent stale or contradictory information—orders, travel status, account notices—into a short actionable warning instead of a confident wrong answer.
- **path:** browser-extension → relay-realtime → mac-planner → pendant → dashboard
- **model tier:** Background model for extraction and comparison; realtime only for the final spoken discrepancy.
- **latency:** Under 20 seconds for a manual request; no polling unless explicitly enabled.
- **cost:** Roughly $0.01–$0.05 per comparison, dominated by two page extractions and one structured comparison; speech is negligible.
- **security:** Authenticated page content leaves Safari only as extracted claims, not HTML. Public-source fetches must be provenance-linked. Never speak or persist categories marked must_not_speak/never-store; show source URLs and hashes in the dashboard.
- **missing:** A user-supplied per-origin configuration (ship empty) identifying which authenticated pages may be compared and which categories may be spoken or retained.; A structured two-source comparison job that accepts a browser tab and a public URL/search result and emits claim-level conflicts.; A pendant alert payload carrying the conflict and provenance.

### "When I’m looking at a long authenticated document, let me ask “what changed since I last checked?” and hear only new or materially changed sections, with the exact section I can reopen in Safari."
- **useful because:** A page watch that merely says a page changed is noisy. Section-level diffs let the owner monitor a work dashboard, policy, ticket, or account page without rereading it, while the browser preserves the deep link and the pendant provides a glance-free summary.
- **path:** browser-extension → relay-realtime → pendant → mac-planner → dashboard
- **model tier:** Background model computes normalized section diffs and a concise summary; realtime speaks only when the owner asks or a high-priority configured change occurs.
- **latency:** Manual diff in 10–30 seconds; scheduled checks can run asynchronously.
- **cost:** About $0.02–$0.08 per diff depending on extracted text length; storage is small because only hashes, section labels, and short claims are retained.
- **security:** Do not save page bodies or screenshots. Store short-lived claim deltas with host, URL, section anchor, and evidence hash. The owner must be able to delete a watch and all derived findings. Never act on changed content automatically.
- **missing:** Section-aware canonicalization and diffing in the browser harness, including stable anchors across navigation.; A watch scheduler that can invoke browser sessions while Safari is online and mark checks missed when it is not.; A compact page-delta alert format understood by the existing offline_alert_inbox.; An empty per-origin/category policy configuration supplied by the owner later.

### "When I say “pick up where I left off,” inspect my open Safari tabs, reconstruct the unfinished task and its current draft, and tell me the next reversible step on the pendant; prepare that step on the Mac, but never submit or send it."
- **useful because:** Today the owner has to remember which tab, draft, and context he abandoned. This is a genuinely cross-node handoff: Safari contributes session state, the relay resolves intent, Mac prepares a reversible action, and the pendant gives a concise continuation without forcing the owner back to a desk.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → dashboard
- **model tier:** Realtime model classifies the spoken continuation request; background model reconstructs task state and produces a bounded next-step plan; Mac executes only reversible preparation.
- **latency:** First spoken answer within 5 seconds; preparation within 30 seconds, with a resumable job if slower.
- **cost:** Approximately $0.03–$0.12 per handoff, dominated by reading 1–3 tabs and planning; Mac execution is local.
- **security:** Draft text may contain secrets. Keep raw page content ephemeral, persist only short claims and provenance, and expose a before/after preview in the dashboard. No form submission, message send, purchase, deletion, or external share is included in the prepared action.
- **missing:** A browser task-state extractor that recognizes drafts, selected records, and incomplete forms without assuming a site list.; A cross-surface continuation record linking tab IDs, browser evidence, and a Mac job.; A pendant response schema for next-step plus “open/preview” follow-up.; Owner-configured origin and category rules, initially empty.

### "Before I submit this web form, tell me exactly what data it will send, which organizations receive it, what fields are hidden or prefilled, and whether anything differs from what I asked for. Never submit it."
- **useful because:** The owner can inspect a logged-in form through Safari but cannot reliably see hidden fields, tracking recipients, prefilled defaults, or scope creep. A pendant-sized preflight turns an opaque click into an understandable decision without requiring the owner to copy sensitive form data elsewhere.
- **path:** browser-extension → relay-realtime → pendant → mac-planner → dashboard
- **model tier:** Background model parses the form DOM and network targets; realtime model answers the owner’s short question and speaks the material findings.
- **latency:** Under 8 seconds for ordinary forms; complex forms can return a staged result within 30 seconds.
- **cost:** Approximately $0.02–$0.10 per preflight, dominated by DOM normalization and structured analysis; no cost for submission because submission is explicitly excluded.
- **security:** Form values are highly sensitive. Keep raw values ephemeral, redact secrets before model transmission where possible, persist only field names/categories and a content hash, and never send data to any destination. The result must distinguish visible, hidden, disabled, and script-generated fields.
- **missing:** A browser-side form introspection action that returns field metadata, hidden values, validation rules, submit targets, and third-party destinations without submitting.; A sensitive-field classifier and owner-editable redaction policy.; A pendant response format for field-count, recipient, and anomaly summaries.; A dashboard preview that lets the owner inspect the exact proposed payload locally.

### "After you do something in a logged-in website, prove to me that it actually took effect by checking the resulting page or confirmation state, and tell me if the site silently failed, redirected me to login, or applied a different value."
- **useful because:** A Mac action receipt proves that a command ran, not that the remote service accepted it. Closed-loop browser verification prevents false confidence around appointments, settings, support tickets, and account changes while keeping submission under the owner’s control.
- **path:** mac-planner → browser-extension → relay-realtime → pendant → dashboard
- **model tier:** Cheap background verifier compares pre-action and post-action page claims; realtime speaks only the final success, mismatch, or authentication-expired result.
- **latency:** Verify within 10 seconds of a reversible or owner-approved action; retain a pending verification job if Safari is temporarily unavailable.
- **cost:** Roughly $0.01–$0.06 per verification, mostly one post-action page read and claim comparison.
- **security:** Verification must not repeat an action or follow arbitrary redirects. Limit it to the expected origin and declared confirmation selectors/claims. Store only the confirmation claim and provenance, with existing short browser retention.
- **missing:** A postcondition contract attached to each browser/Mac action: expected origin, selector or claim, and failure states.; A browser wait-and-read operation that can observe redirects and session expiry without clicking.; A mismatch classifier distinguishing accepted, not accepted, partially applied, and unknown.; A pendant status packet and dashboard timeline tying the remote result to the local action receipt.

### "Warn me when an authenticated Safari task has become unsafe to continue because my session expired, the site changed underneath me, or I was redirected to a different origin—before any prepared action uses the page."
- **useful because:** Today a stale or redirected tab can look normal to the automation layer. A short pendant warning prevents the owner from trusting a login page, expired checkout, or changed workflow, especially when the Mac is preparing an action in the background.
- **path:** browser-extension → relay-realtime → mac-planner → pendant → dashboard
- **model tier:** Local browser rules detect origin/session/DOM transitions; a background model explains ambiguous changes; realtime is reserved for the spoken warning.
- **latency:** Detect on the next page event or within 2 seconds of a prepared action; speak only high-confidence hazards.
- **cost:** Near-zero for local transition checks; under $0.01 for occasional ambiguous classification.
- **security:** Do not expose page text in alerts. Speak only origin, session state, and the blocked preparation. Treat same-origin navigations as potentially changed until revalidated, and never automatically reauthenticate or bypass MFA.
- **missing:** A browser event stream or reliable before/after snapshot hook for navigation, origin, login-form, and DOM-schema changes.; A hazard state machine shared by the browser and Mac planner.; A pendant alert type for ‘stale/redirected page’ with an explicit resume command.; Dashboard visibility into why a prepared action was paused.


## Changes it proposed to its own stack

### `browser-harness` — Add a first-class browser task capsule: on every read-only browser job, record tab URL/title, a short model-produced task label, section anchors, content hash, and expiration, then let a later “pick up where I left off” request retrieve only that capsule and re-read the live page before acting.
- **owner gets:** The owner can abandon a task for hours and resume it by intent rather than remembering a tab, URL, or draft. It also prevents the system from acting on stale page text.
- effort: Medium: schema plus extraction and revalidation in browserSessions/pageWatch, with tests across SPA navigation.  ·  risk: Bad task labeling could resume the wrong tab; require a live re-read and show the selected tab/title before any Mac preparation. Recover by deleting the capsule and starting fresh.
- cost: Small storage and one extra extraction; roughly $0.01–$0.04 per resume.  ·  latency: Adds 1–3 seconds for live revalidation.
- security: Persist only short labels, anchors, hashes, and provenance; never raw HTML, screenshots, or full drafts.
- depends on: An empty owner-supplied per-origin/category policy configuration; Cross-surface continuation record linking browser evidence to a Mac job

### `dashboard-ux` — Build a browser evidence-diff view that displays old/new claim text, source tab and URL, timestamps, content hashes, confidence, retention expiry, and the exact action/voice alert derived from each claim; include one-click delete for a watch and its findings.
- **owner gets:** When the system warns about a changed authenticated page, the owner can verify what changed and why it was spoken instead of trusting an opaque summary. This is especially valuable for financial, travel, and work pages.
- effort: Medium: UI over existing provenance/inspection/receipt records plus a compact diff renderer.  ·  risk: Showing sensitive claims in the dashboard could expose them to someone nearby; default to redacted values and require an explicit reveal gesture. Recovery is immediate deletion of the evidence capsule.
- cost: No meaningful model cost; local rendering only.  ·  latency: None in the alert path; loading the evidence view may take a browser round trip.
- security: Reuse existing 24-hour browser TTL and 200-character cap; do not introduce page-body persistence.
- depends on: Section-aware canonicalization and claim-level diffing; A provenance endpoint inventory confirming the exact live route names


## What it asked for

_Nothing._
