# Harness derivation — browser-extension — round 121

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“What am I looking at?”"
- **useful because:** The pendant should answer about the page currently open in Safari, including the important fields, deadlines, or instructions, without making the owner copy a URL or narrate which tab they mean. This is the browser's uniquely valuable reach turned into a hands-free interaction: Safari supplies private content, the Mac selects the active tab and extracts it, the relay/model summarizes, and the pendant speaks a short answer with a link and source title.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use a cheap text model for extraction/summarization; reserve realtime only for the spoken follow-up conversation.
- **latency:** 3–8 seconds for a first answer; active-tab selection and extraction should be immediate, with a terse spoken result before any deeper follow-up.
- **cost:** ~$0.002–$0.02 per request depending on extracted page length; browser and Mac work dominate latency, not tokens.
- **security:** Page text leaves Safari and reaches the local Mac/relay model, so redact passwords, payment fields, hidden inputs, and session tokens before relay. Never perform clicks or submissions from this read-only utterance. Show the source URL/title in the companion Mac receipt.
- **missing:** A first-class active-tab browser_read_page action triggered from a pendant utterance; A local redaction/length-bounding step before page text is sent to the relay; A response schema carrying source title, URL, and quoted evidence back to the pendant

### "“Save this page for my commute.”"
- **useful because:** From any authenticated Safari tab, the system should capture a bounded, readable snapshot plus the owner’s selected quote, preserve the source URL and capture time, and make it available as an audio item when the pendant is disconnected. Unlike a generic briefing, this is an intentional handoff of one private page into an expiring offline capsule, so the owner can read/listen later even when LTE or Safari is unavailable.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Use a cheap background model only to clean headings and produce a 30–90 second spoken digest; no realtime model unless the owner asks a follow-up.
- **latency:** Capture confirmation under 2 seconds; normalization/audio generation may complete asynchronously within 30 seconds and should show a playable queue item.
- **cost:** ~$0.005–$0.04 per capsule; audio generation and storage retention dominate more than summarization.
- **security:** Authenticated page data must be encrypted at rest, scoped to the paired owner, and auto-expire (for example 24 hours). Strip passwords, forms, account numbers, and tracking parameters; do not capture the full DOM or screenshots by default. Explicitly tell the owner the URL and expiration.
- **missing:** A browser-to-relay encrypted capsule endpoint with per-item expiry; A pendant offline audio queue/index that can sync over USB today and LTE later; A local content sanitizer that removes credential-like fields before upload; A user-facing 'save current tab' intent and playback control

### "“Help me finish this login.”"
- **useful because:** For a login or 2FA page already open in Safari, the browser agent can identify the one-time-code field, read only the visible challenge state, and ask the owner to dictate or confirm the code through the pendant; it can then fill the code but stop before the final sign-in click. This makes the browser, worn interface, and Mac cooperate on a task that otherwise requires moving attention between screens, while preserving a deliberate boundary around account entry.
- **path:** browser-extension → mac-planner → pendant → relay-realtime
- **model tier:** Use deterministic local browser parsing for field discovery and a small text model for ambiguity; use realtime only to transcribe the owner’s dictated digits and confirm them.
- **latency:** Under 2 seconds to announce the page state; under 5 seconds after dictated code to fill the field and report exactly what was entered.
- **cost:** ~$0.001–$0.01 per attempt; realtime transcription is the main model cost.
- **security:** Never read or retain passwords, recovery codes, cookies, or hidden inputs. Treat OTPs as ephemeral memory with zero relay persistence, redact them from logs/receipts, and require an explicit spoken confirmation immediately before filling. Never submit the login, change recovery settings, or approve a device automatically.
- **missing:** A field-aware browser inspection result that distinguishes OTP inputs from passwords and recovery codes; An ephemeral secret channel from pendant/realtime to the local Mac that bypasses durable logs; A browser fill action with masking and a hard stop before submit; A spoken confirmation protocol for the exact number of digits, without echoing the full code into persistent UI

### "“Make a safe proof of what this account page says that I can share with support.”"
- **useful because:** The owner should be able to turn a logged-in Safari page into a selectively redacted evidence packet: the exact relevant claim, source URL and capture time, and a verifiable page snapshot or hash, while excluding names, addresses, account numbers, cookies, and unrelated rows. The pendant can announce what will be disclosed; the Mac/browser produce it locally; the relay can store an expiring handoff link. This solves a real private-browser problem that ordinary copy/paste cannot: proving an account state without leaking the whole account.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Use a low-cost text model only to identify the requested claim and suggest redactions; perform field removal, hashing, and packet construction deterministically on the Mac. Realtime is unnecessary except for the owner’s spoken request and receipt.
- **latency:** A disclosure preview in 5 seconds; packet construction under 15 seconds. The owner must explicitly approve the final disclosed fields before any relay upload or share link creation.
- **cost:** ~$0.003–$0.03 per packet, dominated by optional model-assisted claim extraction; local hashing and storage are negligible.
- **security:** Never upload the raw page. Redaction must happen before relay access, with a deny-by-default secret detector and a complete preview of fields, excerpts, URL, and expiry. Bind links to the paired owner, expire them quickly, support immediate revocation, and never send the packet to support automatically. A cryptographic hash proves packet integrity, not that the site itself is truthful, so label that clearly.
- **missing:** A deterministic local redaction and disclosure-preview engine for authenticated page captures; A signed packet format that preserves source URL/time and a content hash without retaining raw DOM; An expiring, revocable relay share object and dashboard preview; A pendant confirmation flow that speaks the exact disclosure set and receives approval

### "“Before I accept this site’s permissions, tell me what I’m giving it and set the safest options.”"
- **useful because:** On a logged-in page with a cookie, OAuth, notification, or data-sharing consent dialog, the owner should get a plain spoken inventory of requested scopes, retention or sharing language, and preselected defaults. The browser can uncheck nonessential options and prepare the dialog, while the pendant reports the exact final choices and stops before the irreversible Accept/Authorize click. This is a practical use of private-page access that protects the owner at the moment consent is requested, rather than merely summarizing a page afterward.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use deterministic DOM parsing for checkbox/radio labels and a cheap model for legal-language compression; use realtime only for the short spoken explanation and owner’s choice.
- **latency:** 3–6 seconds to inspect and explain the dialog; another 2 seconds to apply reversible unchecks. Never wait on a background job for the preview.
- **cost:** ~$0.002–$0.02 per consent dialog, with token usage proportional to the policy text.
- **security:** The assistant must not infer that “essential” means safe: show the original labels and linked policy URL. Do not click authorization, account-link, purchase, or cookie-consent completion controls without explicit confirmation. Keep the captured policy text local by default and exclude tokens or form values from logs.
- **missing:** A consent-dialog detector with scope/label/control classification across Safari DOMs; A policy-text compressor that retains citations and uncertainty; A reversible browser action that unchecks only named optional controls and returns before/after state; A spoken confirmation receipt that distinguishes prepared settings from accepted consent

### "“Is this page safe before I enter anything?”"
- **useful because:** The owner should be able to ask the pendant for a pre-entry safety check on the currently open Safari page. The browser extension supplies the real origin, redirect chain, certificate/security indicators available to Safari, form destinations, suspicious lookalike text, and whether the page is asking for credentials or payment. The Mac and relay compare those signals against public reputation information, then the pendant gives a short risk explanation and highlights the exact fields not to fill. This catches phishing at the private-session boundary where a generic web search cannot see the live page.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Deterministic local checks first; a cheap background text model can explain suspicious wording and public reputation results. Realtime only speaks the concise verdict.
- **latency:** Under 4 seconds for local origin/form checks and under 10 seconds with reputation lookup; the browser remains untouched while analysis runs.
- **cost:** ~$0.001–$0.02 per check, mostly optional reputation/search and explanation tokens.
- **security:** Never transmit form values, cookies, page secrets, or full authenticated content to reputation services. Treat every check as advisory, distinguish “unknown” from “safe,” and never auto-fill or navigate because a page scored low risk. Preserve the evidence locally for the owner to review.
- **missing:** A browser inspection schema for origin, redirects, form action URLs, and security indicators; A privacy-preserving reputation lookup that sends domains rather than page contents; A phishing-risk rule set with calibrated unknown/low/high outcomes; A pendant alert/receipt path that names evidence and does not expose private page text


## Changes it proposed to its own stack

### `browser-harness` — Add an ephemeral secret-handling lane to the browser bridge: classify DOM fields and extracted text as public, private, credential-like, or one-time-secret locally; never enqueue credential-like values or OTPs into durable browser command records, relay jobs, receipts, screenshots, or page-watch baselines. Permit a one-shot masked fill command whose value is held only in process memory, expires after one result/30 seconds, and returns only metadata such as field type and success. Keep normal page reads and owner-approved reversible fills unchanged.
- **owner gets:** The owner can use the browser assistant for logins and private sites without accidentally creating a searchable record of passwords or one-time codes, while still getting ordinary page help and automation.
- effort: Medium: DOM heuristics plus explicit bridge schemas, in-memory TTL store, redaction tests across Safari extension and local agent, and audit-log field allowlisting.  ·  risk: A false classification could prevent a legitimate fill or, worse, leak a secret. Recover by defaulting uncertain values to secret, exposing a clear retry path, and adding local-only diagnostics that never include the value. Existing queued browser commands need migration handling.
- cost: Negligible API cost; small local memory overhead (under 1 MB for bounded ephemeral values).  ·  latency: Adds roughly 10–50 ms of local classification; no extra model round trip.
- security: Materially reduces credential/OTP exposure in the Mac job file, relay, dashboard, and receipts. It does not make a compromised browser safe; pair it with extension origin and tab binding.
- depends on: The existing browser command queue and receipt schemas (chg-14accc01 and chg-5fc73ce3); A field-aware browser inspection result; An explicit ephemeral fill action distinct from ordinary browser_type


## What it asked for

_Nothing._
## Its own summary

Fresh discovery shows Safari is genuinely online with 3 tabs (active tab 901786, currently an example.com failure page) and no pending browser commands. I recorded four new directions: hands-free “what am I looking at?” over the active authenticated tab; an expiring private-page-to-pendant offline audio capsule; a carefully bounded OTP/login assist that stops before submit; and an ephemeral secret-handling lane in the browser bridge that keeps credentials and OTPs out of jobs, receipts, screenshots, and relay storage. The most important missing piece is not browser connectivity now, but local field-aware redaction plus a one-shot secret fill path. The page capsule additionally needs encrypted expiring storage and a pendant queue.

**Biggest unknown:** Whether the newly granted/acted-on harness already has active-tab extraction, encrypted capsule storage, or field-aware browser inspection hidden behind routes not yet inventoried; the live bridge is available to test, but the current active page is only an error page.

