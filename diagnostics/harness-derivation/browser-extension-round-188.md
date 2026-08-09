# Harness derivation — browser-extension — round 188

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser execution is live and uses nested params** — POST /execute successfully navigates Safari when actions use {type:'browser_navigate', params:{url:'...'}}; a top-level url is rejected. Safari currently has two tabs and tab 1403455 is active. browser_read_page on example.com failed with extension frame-access denial, so navigation works but page extraction depends on extension permissions/site context.
  - evidence: POST /execute at 04:49:48Z returned success for nested params navigation; POST /execute at 04:49:51Z returned 'Extension does not have access to this frame' for browser_read_page.

## Capabilities it proposed

### "“Check my currently open authenticated pages, find anything that needs attention, and tell me the top three in plain spoken language.”"
- **useful because:** This is the browser tier’s highest-value job: it can inspect sessions that web search and the Mac planner cannot reach. It turns an arbitrary current work/personal tab into a concise, wearable briefing without hardcoding sites. The relay schedules or receives the request, Safari extracts only configured fields, and the pendant delivers the result even if the Mac link drops.
- **path:** browser-extension → relay-realtime → pendant → mac-planner
- **model tier:** background for page extraction and ranking; realtime only to answer a follow-up or speak an urgent result
- **latency:** Under 15 seconds for up to five open tabs; stream the first result to the relay as soon as one tab is read
- **cost:** ~$0.01–$0.05 per run depending on extracted text; browser I/O and context size dominate, not tool calls
- **security:** Must use an explicit, inspectable per-origin configuration supplied by the owner (empty initially): allowed origins, extractable regions, redaction rules, may-speak and may-persist categories. Never persist full page text; retain only short redacted findings and source URL. Do not submit, send, purchase, or mutate anything.
- **missing:** browser harness action to enumerate tabs and read each tab with stable tab IDs in one job; per-origin extraction/redaction configuration UI; relay-to-pendant alert delivery integration for the resulting short findings; background scheduler invoking browser sessions

### "“Use the text I just highlighted in Safari as context and explain it to me through the pendant.”"
- **useful because:** The owner often knows exactly which sentence is confusing but cannot comfortably dictate or copy it while moving. A Safari content-script can capture the current selection and page title/URL, the relay can answer with minimal context, and the pendant can speak the explanation hands-free. This is a genuinely cross-surface interaction: browser-only access supplies private context while the worn device supplies the low-friction question and answer channel.
- **path:** browser-extension → relay-realtime → pendant
- **model tier:** realtime for the short explanation; use a cheaper background model only if the owner asks for a long comparison
- **latency:** Begin spoken acknowledgement within 1 second and answer within 5 seconds for a selection under 2,000 characters
- **cost:** ~$0.003–$0.02 per question; selected text length and response audio dominate
- **security:** Transmit only the selection, origin, title, and a short surrounding excerpt when explicitly enabled; never the whole page by default. Apply the owner’s per-origin redaction rules before leaving Safari and set a no-persist retention policy. The browser must show a visible capture indicator and the pendant should say the source origin before speaking sensitive content.
- **missing:** extension event/API for reading the user’s active selection and sending it as a relay event; pendant trigger mapping for “ask about current selection” (button or voice event); relay route that accepts browser selection context and returns a short audio response; per-origin no-store/redaction configuration

### "“Tell me when one of my authenticated browser sessions has expired, and open the affected site’s sign-in page on my Mac without entering anything.”"
- **useful because:** Session expiry is a silent failure mode: scheduled browser work appears to find nothing, while the owner assumes the site is unchanged. The browser can detect login redirects and auth-expired markers in the actual session, the relay can queue a short alert for the pendant, and the Mac can open the exact origin for manual reauthentication. This restores useful automation without ever handling passwords or MFA.
- **path:** browser-extension → relay-realtime → pendant → mac-planner
- **model tier:** background/event-driven rules for detection and routing; realtime only if the owner asks why a task failed
- **latency:** Detect on the next poll/page-watch (under 60 seconds); pendant alert within 5 seconds; open the reauth page in under 3 seconds after acknowledgement
- **cost:** Near-zero model cost for URL/status rules; <$0.005 when a model is needed to classify an unfamiliar login page
- **security:** Send only origin, URL path, and a coarse reason such as redirect/login-required; never extract password fields, tokens, cookies, page text, or MFA codes. Require per-origin opt-in configuration, suppress alerts for origins marked never-monitor, and never auto-submit the sign-in form.
- **missing:** browser page-watch event that reports auth redirects and extension/content-script signals; relay durable session-health records and deduplicated alerting; Mac action to open the origin’s reauth URL from a browser event; pendant alert payload and expiry semantics for session-health notices

### "“Watch the private account pages I specify and tell me only if a number, status, or recipient changed unexpectedly—never read the underlying values aloud or send the page text anywhere.”"
- **useful because:** This gives the owner a privacy-preserving form of authenticated monitoring that is impossible with public search. Safari can inspect pages behind existing logins, but the model and relay receive only a local comparison result such as “changed” plus a redacted label. The pendant becomes an early-warning device for account, order, or reservation changes without exposing balances, messages, or identifiers in speech.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Prefer deterministic browser-local extraction and comparison; use a background model only to classify an explicitly configured field when selectors change. Realtime is unnecessary except for an owner follow-up.
- **latency:** Check on the owner’s chosen schedule or page revisit; alert within 5 seconds of detecting a change. Configuration should complete in under 30 seconds from a selected field.
- **cost:** Near-zero cost for stable selectors and hashes; occasional ~$0.01–$0.05 background classification when a page layout changes.
- **security:** The owner must select the exact fields or regions and choose whether each may be spoken, persisted, or only compared locally. Store salted hashes and coarse labels, not values or page text. Never transmit cookies, tokens, credentials, or full DOM. Require an explicit baseline before alerts begin and show the owner what category is being monitored.
- **missing:** browser UI/action to select and locally extract a field or region from an authenticated page; local comparison and baseline store with salted hashes and change categories; relay event carrying only a redacted change signal; pendant alert routing for privacy-limited findings; owner-facing per-origin and per-field retention/speech configuration

### "“Compare the profile and shipping details across the authenticated sites I choose, and tell me where they disagree—do not change anything.”"
- **useful because:** Stale addresses, names, and contact details cause real failures, but each site is private and inaccessible to ordinary search. The browser extension can inspect the owner’s already-authenticated sessions, normalize only explicitly selected fields locally, and report a disagreement such as “two sites have an older address” without exposing full values through the relay or pendant.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Background model for field normalization and ambiguity resolution; deterministic comparison first; realtime only for a spoken clarification.
- **latency:** Under 30 seconds for five configured origins; speak a concise discrepancy as soon as two origins are available.
- **cost:** ~$0.01–$0.08 per comparison depending on page layouts and normalization; most runs should be local and free.
- **security:** Never infer or compare unconfigured fields. Extract values in Safari, normalize locally, and send only field name, disagreement count, and redacted origin labels. Do not persist raw addresses or profile values. Read-only by default and never offer an automatic correction without a separate owner request.
- **missing:** cross-origin browser job with stable per-origin field selectors; local normalization/comparison service that can operate without exporting raw values; owner configuration for fields, origins, redaction, and retention; spoken discrepancy format and optional local report view

### "“I think this device is exposed. Sign me out of the selected open web services now, show me which tabs succeeded or failed, and do not touch anything else.”"
- **useful because:** The browser is the only node holding the owner’s live authenticated sessions, so it can perform an emergency containment action that the relay, pendant, and Mac cannot reproduce safely. A single spoken request can close selected sessions, while the pendant reports a terse success/failure receipt and the Mac can preserve a local audit trail.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → faculty-action
- **model tier:** Realtime intent parsing and result narration; deterministic browser actions for logout navigation/clicks; no background model needed.
- **latency:** Start within 2 seconds and report each origin within 15 seconds; continue independently if one site is slow or unavailable.
- **cost:** ~$0.005–$0.03 for intent parsing and narration; browser execution dominates latency, not API cost.
- **security:** Require the owner to name or preconfigure the origins; never interpret “everything” as every browser tab without an explicit origin list. Do not capture credentials, logout tokens, or page contents. Record only origin, timestamp, success/failure, and a reversible? No—logout may not be reversible, so state that clearly before execution in the spoken acknowledgement.
- **missing:** browser workflow that discovers and executes an origin’s logout action without submitting unrelated forms; origin allowlist and emergency-action configuration; parallel action execution with per-tab receipts and timeout isolation; pendant emergency command/acknowledgement and concise result delivery


## Changes it proposed to its own stack

### `browser-harness` — Add an origin-scoped “session health and recovery” state machine to browserSessions/pageWatch: classify a tab as healthy, login-required, MFA-waiting, blocked, or unknown from redirect chains and DOM signals; emit one deduplicated event with origin, safe return URL, and the suspended job ID. On a successful return to the prior origin, emit a resume event but never replay the mutation automatically.
- **owner gets:** The owner stops losing hours to silent expired logins. The pendant can say exactly which site needs attention, the Mac can open the right sign-in page, and the paused browser task can continue from where it stopped once the owner has logged in.
- effort: Medium: browser signal collection, durable state transitions, deduplication, and resume correlation; no model required for known origins.  ·  risk: False positives could produce annoying alerts; unknown pages must be classified conservatively and suppress auto-resume. Recover by exposing the event receipt and allowing the owner to dismiss or disable an origin.
- cost: Negligible API cost; small local storage for per-origin state and one short event per transition.  ·  latency: Detection on the existing poll/watch interval; no meaningful added latency to ordinary reads.
- security: Only origin, coarse status, safe return path, and job ID leave the browser. Exclude cookies, tokens, form values, passwords, and page text. Configuration must be per-origin and inspectable.
- depends on: browser page-watch/inspection events; relay durable alert routing to offline_alert_inbox; Mac open-URL action; a resume token that invalidates after navigation or timeout


## What it asked for

_Nothing._
