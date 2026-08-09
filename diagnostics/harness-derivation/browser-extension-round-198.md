# Harness derivation — browser-extension — round 198

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Check the authenticated sites I’ve explicitly configured, find anything that creates a deadline or needs a reply, compare it with my Mac calendar and reminders, and tell me only what I should act on today.”"
- **useful because:** This is the strongest genuinely multi-surface use: Safari is the only node that can see logged-in web state, the Mac can correlate it with local commitments, the relay can rank and narrate it, and the pendant can deliver a short interruption even when the owner is away from the screen. It turns scattered web obligations into an actionable queue rather than another page summary.
- **path:** browser → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Background browser extraction and a cheap local correlation pass first; use the expensive realtime model only to resolve ambiguity and render the final short spoken alert.
- **latency:** Initial scan under 60 seconds; spoken result under 10 seconds after extraction. Run on demand or on a schedule, never continuously by default.
- **cost:** Roughly $0.02–$0.10 per scan depending on number of configured origins; browser and local calendar correlation dominate wall time, not tokens.
- **security:** Ship with an empty per-origin configuration. Never store page bodies; emit only short claims with host/URL provenance and existing 24-hour browser TTL. Do not speak categories the owner marks must-not-speak. A result should link back to the exact tab and show why it was ranked, but never silently send/reply.
- **missing:** A browser job that extracts deadlines, requested replies, and urgency signals across owner-supplied origins; A joiner between browser findings and calendar/reminder entities with duplicate and stale-date handling; A pendant alert payload that carries claim provenance and a deep link to the source tab

### "“Fill out this authenticated web form from the information on my Mac, then read back every field, attachment, recipient, and amount to me on the pendant and leave it staged without submitting.”"
- **useful because:** The browser can reach the logged-in form, the Mac can supply local files and structured facts, and the pendant is the only surface that can give a hands-free final inspection while the owner is away from the keyboard. This prevents the common failure where automation either stops too early to help or submits a consequential form blindly.
- **path:** browser → mac-planner → relay-realtime → pendant
- **model tier:** Cheap deterministic field extraction and local file selection; use realtime only to resolve labels/ambiguity and speak the compact preview.
- **latency:** Stage in 20–45 seconds, then wait indefinitely for the owner. Never auto-submit.
- **cost:** About $0.01–$0.05 per form, dominated by browser round trips and optional document parsing.
- **security:** Read/write only on the explicitly requested tab and origin. Show a field-by-field diff, redact secrets in speech, and preserve an undoable provenance receipt. Stop at submit/send/purchase; the owner can inspect the staged page in Safari and decide. Do not persist page text or uploaded documents beyond the site's own session.
- **missing:** A tab-scoped form mapper that reports field labels, values, attachments, and submit controls; A Mac-to-browser attachment handoff for local files with an explicit per-file preview; A pendant-friendly preview protocol that chunks long forms and supports spoken correction before staging

### "“Investigate this order or subscription problem across the logged-in website and my Mac receipts, tell me whether I was overcharged or double-billed, and draft the support message with the evidence—do not send it.”"
- **useful because:** The browser reaches the private order history and current account state; the Mac can search local receipts and email exports; the relay can reconcile dates, amounts, and status; and the pendant can report a clear verdict while the owner is mobile. This replaces manually comparing two contradictory records and produces a ready-to-review resolution without sending anything.
- **path:** browser → mac-planner → mac-terminal → relay-realtime → pendant
- **model tier:** Use deterministic amount/date extraction and duplicate matching first, then a cheap background model for reconciliation; reserve realtime for the final spoken verdict and a concise draft.
- **latency:** One investigation in 30–90 seconds, with progress/status available for longer sites. Draft is ready for review, never transmitted automatically.
- **cost:** Approximately $0.03–$0.15 per case; browser navigation and local receipt parsing dominate, with model cost proportional to the number of candidate records.
- **security:** Only inspect the requested account and local receipt locations. Keep raw receipts and page contents on the Mac; persist only a short, 24-hour claim with URL/host provenance. Mask full card numbers and addresses in speech. The support draft must visibly identify every cited record and remain unsent until the owner edits and submits it.
- **missing:** A cross-source reconciliation job that normalizes currency, tax, tips, refunds, and timestamps; A local receipt search adapter that returns structured evidence without exposing unrelated mail/files; A draft composer that embeds evidence references and detects when the browser page has gone stale

### "“Turn the authenticated page I’m on into a hands-free conversation: tell me what matters, let me ask about any field or section, and let me dictate values without losing my place.”"
- **useful because:** Today the owner must look at Safari even though the pendant is always available. This would make private, login-protected pages genuinely accessible while walking or driving: the browser supplies page structure and session access, the Mac maintains a navigable section/field cursor, the relay handles concise question answering, and the pendant provides speech input/output. It is not just a summary—the owner can traverse and edit a live page by semantic landmarks.
- **path:** browser → mac-planner → relay-realtime → pendant
- **model tier:** Use deterministic DOM/accessibility-tree extraction and cursor management for most turns; use the realtime model only for ambiguous natural-language references such as “the second option under delivery.”
- **latency:** Page map in under 3 seconds; each question or dictated edit acknowledged in under 2 seconds. Preserve the cursor across dropped links and resume from the last semantic landmark.
- **cost:** About $0.005–$0.03 per interaction; browser extraction is cheap, with model spend only on ambiguous references and concise spoken responses.
- **security:** The owner explicitly chooses the active tab. Never read hidden fields or secrets unless requested; redact passwords, payment numbers, and one-time codes by default. Keep page text ephemeral, store only a session cursor and short-lived provenance, and stop before irreversible submission while exposing the exact staged change.
- **missing:** A browser accessibility-tree/semantic-landmark extractor with stable IDs across DOM updates; A resumable per-tab cursor that maps spoken references to fields and sections; A pendant protocol for short question/answer turns and dictated field edits; A live-page mutation receipt that can restore the prior field value

### "“Audit my logged-in subscriptions and memberships, identify renewals I probably no longer need, and prepare a cancellation or downgrade queue for me to review.”"
- **useful because:** No single node can do this honestly: Safari sees the active plans, renewal terms, and cancellation controls behind logins; the Mac can compare local receipts, usage notes, and calendar commitments; the relay can remove duplicates and rank savings; the pendant can announce only the few decisions worth making. The system should prepare the exact next step without silently cancelling anything.
- **path:** browser → mac-planner → mac-terminal → relay-realtime → pendant
- **model tier:** Background extraction and deterministic duplicate/renewal matching first; a cheap reasoning pass ranks likely waste; realtime is used only for the spoken shortlist and owner questions.
- **latency:** A full audit in 2–5 minutes, resumable across sites. Individual subscription explanations under 5 seconds once facts are collected.
- **cost:** Approximately $0.05–$0.25 per audit, driven by authenticated navigation and the number of plans, not by narration.
- **security:** Start with an empty owner-supplied origin list and explicit category rules. Keep raw account pages local and ephemeral; persist only short host-keyed claims with expiry. Treat “cancel” and “downgrade” as staged actions with exact resulting price/date shown; never click final confirmation automatically.
- **missing:** Subscription-plan and renewal extraction robust to site-specific layouts; A local receipt/usage correlation adapter that avoids unrelated personal files; A review queue with per-item source evidence, estimated annual savings, and an undoable staged action

### "“When a private web page changes in a way that affects me, explain exactly what changed against the last version, tell me the consequence, and give me the safest next action on my pendant.”"
- **useful because:** A raw page watcher is not enough: the owner needs a trustworthy semantic diff of terms, prices, dates, permissions, or delivery status. Safari supplies access to pages no other node can see, the Mac retains a bounded local baseline, the relay explains impact, and the pendant delivers a compact alert offline. This catches silent subscription price increases, changed policies, and order-status reversals without making the owner reread a site.
- **path:** browser → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Deterministic DOM normalization and field-level diff first; use a background model to classify impact; realtime only for an urgent spoken explanation or owner follow-up.
- **latency:** Scheduled checks complete within 1–3 minutes; urgent alerts reach the pendant within 15 seconds of detection when the link is available.
- **cost:** Roughly $0.01–$0.08 per watched page per check, mostly browser execution and baseline normalization.
- **security:** Owner supplies origins and selectors/categories explicitly; ship empty by default. Store a compact normalized baseline or cryptographic digest, not page HTML or screenshots, with short retention and provenance. Never infer a financial/legal consequence as certain when the diff is ambiguous; include the before/after URL and observed time.
- **missing:** A durable but privacy-bounded semantic baseline for authenticated pages; DOM normalization that ignores ads, timestamps, and layout churn while preserving meaningful terms; Impact classification and deduplicated offline alert delivery with a source-page deep link


## Changes it proposed to its own stack

### `browser-harness` — Add a first-class authenticated-web investigation pipeline: take a user-selected tab/origin set, run read-only extraction with an action allow-set, normalize claims into typed facts (amount, date, status, deadline, requested response), attach host/URL/observedAt provenance, and expose a resumable job with progress and a final evidence-linked draft. Keep irreversible browser actions out of the pipeline; hand staged forms back to the existing browser session.
- **owner gets:** The owner gets one dependable command for real private-web problems—orders, subscriptions, forms, deadlines—instead of a fragile sequence of page reads. The result is explainable and reviewable on the pendant or Mac, while logged-in access remains where it belongs: Safari.
- effort: High: browser extraction schemas, origin/session scoping, resilient navigation, typed reconciliation, evidence receipts, and pendant delivery integration.  ·  risk: Sites change DOMs, pages may contain unrelated private data, and stale sessions can produce false claims. Recover by failing closed to an uncertainty report, retaining URL/time provenance, and never presenting an unverified mutation as completed. Raw page data remains ephemeral.
- cost: Moderate engineering cost; per-job API cost stays low because extraction is mostly deterministic and only ambiguous fields use a model.  ·  latency: Adds roughly 5–20 seconds for normalization and evidence packaging beyond raw browser reads; resumable jobs avoid a hard timeout.
- security: Strongly positive if implemented with current no-page-storage policy, host-keyed 24-hour claims, explicit empty origin configuration, and per-action read-only allow sets. No new secret leaves Safari.
- depends on: A stable browser action spelling for browser_read_page/browser_snapshot/browser_select; Typed browser finding schema and provenance endpoints; A pending-job status path usable by the pendant offline_alert_inbox


## What it asked for

_Nothing._
## Its own summary

Discovered a materially changed live state: Safari is online with two real tabs (DoorDash order, YouTube subscriptions), and direct POST /execute browser_list_tabs works end-to-end; I informed mac-planner. I recorded four non-identical proposals: the highest-value cross-surface authenticated-web deadline triage against Mac commitments; a form staging/read-back workflow that never submits; order/subscription discrepancy reconciliation with an unsent evidence-backed support draft; and the browser-harness pipeline needed to make those dependable. The browser wrapper schemas are still ambiguous, but the underlying execute route is usable now.

**Biggest unknown:** The owner still needs to supply the first explicit origin configuration and speech/retention categories; it must ship empty rather than be invented. Engineering still needs typed extraction/reconciliation and a stable browser_read_page/browser_snapshot/browser_select dispatch path. I do not need more browser access to demonstrate usefulness today.

