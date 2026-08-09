# Harness derivation — browser-extension — round 244

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser live dispatch state** — Safari on MacIntel is online with 2 tabs, but every granted enqueue wrapper currently fails resolver resolution because browser_list_tabs is ambiguous with browser_list_sessions; no browser command was executed this round.
  - evidence: discover(devices) reported Safari on MacIntel · browser · Safari · 2 tab(s) · online; browser_enqueue_command(list_tabs) returned unresolved ambiguity between action:browser_list_tabs and action:browser_list_sessions.

## Capabilities it proposed

### "“What are the four latest items on my Safari Reading List, and read me the first one’s key points?”"
- **useful because:** The owner has repeatedly asked this exact question and currently gets failures. Safari’s Reading List is private browser state, not a public web-search problem. A browser extension API could enumerate the list, open only the selected item in the existing authenticated session, extract a short cited summary, and send it to the pendant for playback.
- **path:** browser → mac-bridge → relay → pendant
- **model tier:** Use deterministic Safari Reading List enumeration and a cheap summarizer; invoke the realtime model only for an interactive follow-up such as “skip this and read the next.”
- **latency:** List enumeration under 2 seconds; selected-page extraction and summary under 15 seconds, with a queued audio result if navigation or login refresh is slow.
- **cost:** About $0.005–$0.03 per selected article; list enumeration itself is negligible. Token usage is bounded by extracting only the selected article’s relevant text.
- **security:** Reading List titles/URLs and article text are private. Keep them on-device where possible, do not persist article bodies, and retain only a short 24-hour claim with URL provenance if the owner asks follow-up questions. Never mark items read, delete entries, or share/send anything without an explicit separate command.
- **missing:** Safari extension permission/API for Reading List enumeration (the current page-action bridge cannot see browser chrome state); A stable read-only endpoint exposing ordered Reading List metadata to the browser tier; A result handoff that can stage summarized audio for the pendant

### "“Fill out this logged-in web form from my notes, check every field and tell me exactly what would be submitted—do not submit it.”"
- **useful because:** This combines the browser’s private session with the Mac notes/files tier and the pendant’s concise spoken confirmation. The system can do the tedious field mapping and validation, expose a complete preflight diff, and leave the owner with a ready form rather than risking a blind submission. It is useful for applications, support forms, and reimbursement pages where the browser session is the only authenticated route.
- **path:** browser → mac-bridge → relay → pendant → dashboard
- **model tier:** Use a cheap structured extraction model for note-to-field mapping and deterministic DOM validation; realtime is reserved for answering a field-level spoken question. No model should invent a missing value.
- **latency:** Initial field inventory in 5–10 seconds; fill and validation in under 30 seconds. The dashboard and spoken result should show unresolved fields rather than waiting indefinitely.
- **cost:** About $0.02–$0.10 per form depending on fields and note context. Browser round trips and screenshot/DOM extraction dominate; keep screenshots ephemeral and avoid sending them to a cloud model when DOM labels suffice.
- **security:** Read and reversible field edits are allowed by the owner, but the workflow must have a hard pre-submit boundary: no click on submit, send, purchase, delete, or equivalent. Show field, value, source note, and validation status; redact secrets from receipts and retain only provenance plus a user-approved draft. The owner’s existing destructive-action confirmation policy remains the final boundary.
- **missing:** A form-schema extractor that reports submit controls and equivalent high-impact buttons before filling; A draft/undo journal for browser field mutations, including the originating note and exact old value; A spoken and dashboard preflight renderer that can enumerate long forms without leaking sensitive values

### "“Compare the options in these logged-in tabs, tell me which is best under my constraints, and leave the chosen option open without buying or booking.”"
- **useful because:** The browser can see private prices, availability, account-specific offers, and policy text that public search cannot. It can normalize several tabs into a spoken comparison, preserve the exact evidence links, and position Safari on the recommended option while stopping before the irreversible purchase or booking step.
- **path:** browser → relay → pendant → dashboard
- **model tier:** Use deterministic extraction for price, dates, fees, and cancellation terms; a cheap reasoning model ranks options against the owner’s stated constraints. Realtime is only for a follow-up such as changing the budget.
- **latency:** Collect 3–8 tabs in 20–45 seconds; speak a compact recommendation as soon as the comparison is complete, with a longer evidence table available in the dashboard.
- **cost:** About $0.03–$0.15 per comparison depending on tabs and text length. DOM extraction and navigation are the main latency costs; deduplicate repeated headers before model input.
- **security:** Do not expose account identifiers or persist page bodies. Keep only normalized claims and source URLs with short browser TTL. Never click purchase, reserve, accept terms, or equivalent; show the exact target and total before any future action. The owner’s maximum-access policy permits browsing, while destructive confirmation remains applicable to committing the transaction.
- **missing:** A multi-tab capture coordinator with stable tab IDs and per-tab provenance; A constraint-aware comparison schema for totals, fees, dates, and cancellation terms; A reliable browser command resolver; current granted wrappers ambiguously match browser_list_tabs/browser_list_sessions and cannot execute; A dashboard view for evidence and an explicit commit handoff

### "“Forget everything the browser has learned about me since I left home, everywhere—not just the current page—and tell me when it is gone.”"
- **useful because:** A browser agent can accumulate private claims across authenticated sites, relay jobs, provenance, and pending audio. The owner needs a single spoken emergency wipe that is stronger than deleting one finding: revoke queued browser work, erase browser-derived memory and evidence capsules, clear staged summaries, and confirm each surface’s completion. A physical pendant action provides a trustworthy fallback when the Mac is unattended.
- **path:** pendant → browser → relay → mac-bridge → dashboard
- **model tier:** Deterministic deletion and receipt generation only; no model call is needed. Realtime is used solely to answer a follow-up about what categories were removed.
- **latency:** Acknowledge immediately, complete within 10 seconds for local stores and within 60 seconds for queued relay/browser work. If a surface is offline, show it as pending rather than claiming success.
- **cost:** Negligible token cost; dominated by storage deletion and delivery receipts.
- **security:** This is intentionally destructive and must require an explicit spoken confirmation or a dedicated long press. It must distinguish browser-derived facts from owner-authored notes, preserve only an audit tombstone saying a wipe occurred, and avoid logging the deleted values in command receipts. A pending offline surface must remain visibly unresolved.
- **missing:** One coordinated browser-privacy wipe operation spanning memory, provenance, spool, jobs, and staged audio; A pendant emergency-wipe gesture and authenticated status response; Per-surface deletion receipts with offline retry and no sensitive payloads; Dashboard controls showing exactly what was and was not erased

### "“Why did you tell me that? Show me the exact private page evidence, what has changed since you read it, and whether I should still trust the answer.”"
- **useful because:** Private web facts expire quickly and can be wrong after a page changes. This capability would let the owner audit a spoken answer without rereading an entire site: revisit the source in the existing authenticated session, compare the captured claim with the current DOM, report changed fields, and downgrade or retract the answer when necessary.
- **path:** browser → relay → pendant → dashboard
- **model tier:** Use deterministic provenance lookup and field diffs first; a cheap model explains the difference. Realtime handles only the owner’s conversational “what changed?” follow-up.
- **latency:** Return provenance immediately from stored receipts; refresh and compare the source within 15 seconds, or clearly label it unverified if navigation fails.
- **cost:** About $0.01–$0.05 per refresh, usually less when the claim has expired or the page is unchanged. Store compact field-level diffs rather than page copies.
- **security:** Never speak or persist unrelated page content while auditing. Restrict the refresh to the original origin and tab/session, redact account identifiers, and keep only the claim, URL, timestamp, and changed-field summary under the existing short browser TTL.
- **missing:** A claim-level evidence capsule with selector or semantic-anchor information sufficient to locate the same field again; A current-versus-captured browser diff engine that can distinguish changed content from layout churn; A pendant-friendly citation token so the owner can ask about a spoken claim without repeating sensitive text

### "“If the site changes or logs me out while you are working, recover safely, tell me exactly where you stopped, and let me resume from the same point later.”"
- **useful because:** Long authenticated browser tasks currently fail opaquely when a session expires, a tab closes, or a page changes shape. A resumable browser transaction would checkpoint intent, tab identity, extracted non-sensitive state, and the last completed reversible step, then notify the pendant and offer a precise resume rather than restarting or guessing.
- **path:** browser → relay → pendant → mac-bridge → dashboard
- **model tier:** Use deterministic checkpoints, selectors, and session-state checks; use a cheap model only to re-identify a changed page region. Realtime is reserved for resolving an ambiguous resume choice with the owner.
- **latency:** Detect failure on each browser result; announce a failure within 2 seconds. Resume should take under 15 seconds when the session remains valid, and otherwise stop at the login wall.
- **cost:** Roughly $0.005–$0.04 per resumed task; most checkpoints are metadata-only. Costs rise only when a changed page requires semantic re-identification.
- **security:** Never checkpoint passwords, tokens, full page text, or screenshots. Bind checkpoints to origin, tab/session, and task hash; invalidate them after the existing browser-fact TTL or on logout. Resumption must not silently cross origins or pass a submit/purchase boundary.
- **missing:** A durable browser transaction/checkpoint format with reversible-step receipts; Session-expiry and tab-loss detection in the extension bridge; A resume protocol that can revalidate origin and page state before continuing; Pendant and dashboard controls for pause, discard, and resume


## Changes it proposed to its own stack

### `browser-harness` — Publish and resolve a single exact browser action contract matching the live executor: browser_list_tabs, browser_navigate, browser_read_page, browser_snapshot, browser_click, browser_type, browser_wait_for, browser_select, browser_scroll, and browser_press_key. Remove near-synonym candidates such as browser_list_sessions from the resolver’s browser action namespace, and return structured command results including tabId, URL, title, and error class.
- **owner gets:** Browser control would stop failing before it reaches Safari. The owner could actually ask for Reading List research, logged-in page extraction, or form preflight today instead of receiving an ambiguous-tool error despite Safari being online with two tabs.
- effort: Small-to-medium: action manifest cleanup, resolver thresholds/tests, and one result-schema adapter; then exercise navigate/read/click against the live Safari extension.  ·  risk: A wrong mapping could send a click or keystroke to the wrong tab. Recover by defaulting ambiguous tab targeting to read-only inspection, requiring an explicit tabId for mutations, and preserving current command receipts/undo where available.
- cost: Negligible API cost; a few engineering hours and no hardware cost.  ·  latency: Removes a failed round trip; successful commands still use the extension poll interval and up to the existing 45-second wait.
- security: No new authority; this makes existing browser authority observable and deterministic. Keep the owner’s existing stop-before-submit behavior.
- depends on: A live Safari extension heartbeat (currently online with two tabs); POST /execute browser action dispatch; An explicit resolver inventory that excludes ambiguous aliases


## What it asked for

_Nothing._
