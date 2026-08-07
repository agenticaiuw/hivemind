# Harness derivation — browser-extension — round 134

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser target correctness** — Safari is online with 3 tabs; active tab 901786 is example.com, while the default browser session is pinned to Gmail tab 901464. POST /execute browser_list_tabs succeeds, proving live tab enumeration, but default-session targeting can differ from what the owner is looking at.
  - evidence: GET /browser/status and GET /browser/sessions, followed by POST /execute browser_list_tabs at 2026-08-07T18:19Z

## Capabilities it proposed

### "“Save this page for me.” From the pendant or voice, capture the exact Safari page and my place in it, make it a resumable handoff, and later say “resume that” to reopen the same tab and continue from the saved heading or form field."
- **useful because:** The owner can move between walking, Mac work, and browser sessions without losing context. It uses the one thing this node uniquely sees—authenticated pages—and turns a fleeting tab into a reliable, cited handoff rather than another generic bookmark.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → dashboard
- **model tier:** Realtime model only interprets the short voice command; a cheaper background model extracts a compact page capsule and matches a later resume request.
- **latency:** Capture acknowledgment under 2 seconds; extraction under 10 seconds; resume navigation under 5 seconds.
- **cost:** About $0.002–$0.02 per save/resume, dominated by page extraction and optional screenshot/OCR; storage is a few KB plus optional image.
- **security:** Capsules may contain private page text, URLs, and form contents. Encrypt at rest, inherit browser session sensitivity, redact passwords/payment fields, and never auto-submit a resumed form.
- **missing:** A browser action that captures a stable semantic anchor (heading/field/scroll position) and screenshot plus DOM metadata; A durable handoff-capsule store with per-capsule expiry and deletion; Pendant voice intents for save/resume and a spoken disambiguation when several capsules match

### "“Tell me if any of my logged-in accounts look compromised.” Have Safari inspect security/settings and notification pages I already have access to, detect new-device alerts, changed recovery details, unexpected sessions, or forced re-authentication, and alert me through the pendant with evidence and the safest next step—without changing anything."
- **useful because:** This is a high-consequence job no public search can do: only the browser extension can inspect private account security surfaces. It replaces the owner’s need to manually audit scattered accounts and can surface a real incident while it is still containable.
- **path:** browser-extension → relay-realtime → relay-realtime → pendant → dashboard → mac-planner
- **model tier:** Background model performs scheduled extraction and change classification; realtime model is used only when the owner asks follow-up questions or needs a concise alert.
- **latency:** Scheduled checks can take 1–3 minutes; an urgent security finding should reach the pendant within 30 seconds of detection.
- **cost:** Roughly $0.01–$0.08 per account audit, dominated by authenticated page extraction and classification; no model call when normalized security fingerprints are unchanged.
- **security:** The detector itself handles extremely sensitive security data. Store hashes and minimal snippets, not full pages; never expose tokens/passwords; require explicit owner confirmation before logout, password reset, recovery-email change, or contacting support.
- **missing:** Named account security-watch recipes with site-specific URLs and semantic selectors; A normalized security-event schema and deduplication across repeated alerts; A high-priority pendant notification route with evidence links and suppression/acknowledgment state

### "“Is this page or message legitimate?” While I’m viewing a logged-in page, inspect the current tab’s sender, links, domains, redirects, and requested permissions, compare them with public authoritative information, and give me a risk explanation with the exact suspicious evidence—without clicking anything dangerous."
- **useful because:** A public search cannot see the owner’s private message or current tab, while a browser-only reader cannot independently verify domains and claims. Combining authenticated page evidence with public research gives the owner a fast phishing/scam check before they click or disclose information.
- **path:** browser-extension → relay-realtime → mac-planner → pendant
- **model tier:** Cheaper background model extracts links and metadata; realtime model handles the owner’s spoken question and returns a short risk explanation. Escalate only ambiguous cases to the expensive tier.
- **latency:** Initial verdict in 5–12 seconds; never perform a click or navigation unless explicitly requested.
- **cost:** About $0.01–$0.06 per check, mainly public-source retrieval and page extraction; link parsing and domain checks are local/cheap.
- **security:** Private message text and URLs leave the browser only to the authenticated relay for analysis. Redact unrelated content, avoid submitting credentials, treat redirects/downloads as hostile, and show evidence rather than claiming certainty.
- **missing:** A current-tab browser_read_page plus link/redirect extraction that returns DOM anchors and visible sender metadata; A safe URL reputation/authoritative-source resolver with redirect sandboxing; A result schema expressing confidence, evidence spans, and recommended safe actions

### "“Emergency stop my browser.” One physical pendant action should immediately cancel queued browser commands, stop any in-progress browser workflow, navigate every controlled tab to a neutral blank page, and tell me which sessions were stopped."
- **useful because:** If a page starts behaving unexpectedly, a prompt appears, or the owner realizes the wrong account is open, they get a fast physical escape hatch without finding the Mac or speaking a long command. This is protection unique to a worn device paired with the browser bridge.
- **path:** pendant → browser-extension → relay-realtime → mac-planner → dashboard
- **model tier:** Firmware handles the immediate local trigger; relay performs cancellation and fan-out; no expensive model call is needed except an optional spoken summary.
- **latency:** Local trigger acknowledgment under 200 ms; command cancellation and tab neutralization within 2 seconds.
- **cost:** Near-zero model cost; small relay and extension messages only.
- **security:** The action must be unmistakable and physically hard to trigger accidentally, such as a long press plus vibration confirmation. It must not claim to revoke website sessions or undo already-submitted actions; report those limitations clearly. Keep audit metadata without retaining page contents.
- **missing:** A privileged pendant emergency event route that works while ordinary voice transport is unavailable; A browser-bridge cancel-all-for-device operation and atomic command invalidation; An extension operation to navigate controlled tabs to a neutral local page without opening a new session

### "“Which account am I about to act as?” Before I click, type, or navigate in a logged-in workflow, compare the visible identity and organization across the target tab, related open tabs, and the owner’s known account identities, then speak a concise identity confirmation or mismatch warning."
- **useful because:** Many costly mistakes are not phishing: they are sending from the wrong Gmail account, editing the wrong workspace, or changing a personal account instead of a work one. The browser can see identity indicators that the Mac and relay cannot, while the pendant can warn before the mistake.
- **path:** browser-extension → pendant → relay-realtime → mac-planner
- **model tier:** Use deterministic DOM/site adapters first; a cheaper model resolves unfamiliar identity labels. Realtime is reserved for the spoken warning.
- **latency:** Identity check under 1 second for known sites and under 5 seconds for an unfamiliar site.
- **cost:** Usually under $0.005 per check; model cost only for unfamiliar layouts.
- **security:** Identity labels are sensitive. Keep only normalized account fingerprints and site origin, not full page text. Never change account or submit an action as part of the check.
- **missing:** A site-independent identity extraction contract with confidence and visible evidence; A pre-action interception hook that can inspect identity without blocking ordinary read actions; A compact owner-controlled identity registry with aliases and sensitivity labels

### "“Bring me the official copy of this.” From an authenticated page, locate the authoritative downloadable statement, receipt, certificate, or policy version, verify it belongs to the right account and date, save an encrypted copy to my Mac with source URL and retrieval time, and tell me exactly where it was stored."
- **useful because:** The owner often needs a trustworthy artifact, not a summary: a receipt for reimbursement, an insurance document, a school record, or a current policy. The browser can reach private downloads behind existing logins; the Mac can store and organize them; the pendant can confirm completion.
- **path:** browser-extension → mac-planner → mac-terminal → relay-realtime → pendant
- **model tier:** Background model identifies candidate documents and metadata; deterministic checks verify account/date/source; realtime only reports the result.
- **latency:** Typical retrieval in 10–30 seconds; if several documents match, ask one concise clarification rather than guessing.
- **cost:** About $0.01–$0.05 per retrieval, dominated by document classification; local encrypted storage has no model cost.
- **security:** Documents may contain financial, health, or identity data. Encrypt in transit and at rest, redact previews, apply retention/expiry, and never upload the file to a third-party model. Stop before any consent or purchase flow.
- **missing:** A browser download interception and verified-file return path; A local encrypted artifact vault with provenance, retention, and user-visible deletion; Cross-surface document metadata linking source tab, account identity, date, and hash


## Changes it proposed to its own stack

### `browser-harness` — Make every browser command carry an explicit target policy and resolve it at execution time: active tab, pinned session tab, or tabId. Before dispatch, return the chosen tabId/title/URL; reject silently falling back to the default Gmail session when Safari’s active tab differs. Persist the target in the receipt and verify the result came from that same tab.
- **owner gets:** When the owner says “read this,” the pendant will read the page they are actually looking at, not a stale Gmail tab. This prevents private information from the wrong tab being spoken back and makes browser control trustworthy.
- effort: Medium: update browserBridge target resolution, browserSessions metadata, extension command payload, and receipts; add tests for active-tab changes between planning and execution.  ·  risk: A stale or closed tab may cause a clear retry instead of an answer. Recover by offering the known tab list and re-pinning only after an explicit choice; existing session-pinned workflows remain supported.
- cost: Negligible API cost; a few hundred bytes of target metadata per command and receipt.  ·  latency: Adds one lightweight live-tab validation, typically under 0.5 seconds.
- security: Positive: prevents cross-tab data leakage and makes the privacy boundary explicit. Do not log page contents in target diagnostics.
- depends on: A functioning extension-side active-tab/list-tabs response (currently POST /execute browser_list_tabs works); Browser session target semantics for default vs pinned tabs


## What it asked for

_Nothing._
