# Harness derivation — browser-extension — round 155

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser live availability** — Safari extension is online with 9 tabs and active tab https://x.com (tabId 1163292), but every granted browser enqueue wrapper remains unresolved at tool resolution, so this agent cannot read or act on those tabs yet.
  - evidence: GET /browser/status returned online:true, tabCount:9, active tab; browser_enqueue_command_implemented(list_tabs) returned resolution: unresolved with nearest GET /browser/poll.

## Capabilities it proposed

### "“When I say ‘what changed in my signed-in accounts?’, check the browser pages I have explicitly enrolled, compare them with their last approved snapshot, and give me only actionable changes; put urgent ones in my pendant inbox.”"
- **useful because:** This is the highest-value browser-only service: it turns authenticated sessions into a quiet, cross-site attention stream without reading public pages or requiring the owner to remember which tabs to inspect. The browser supplies login-gated evidence, the relay schedules and ranks it, and the pendant delivers urgent changes even if the Mac link drops.
- **path:** browser-extension → relay-realtime → mac-planner → pendant
- **model tier:** Background/scheduled extraction and semantic diff use a cheap model; realtime is used only when the owner asks a follow-up. Deterministic DOM normalization and redaction run locally before model input.
- **latency:** Scheduled checks under 60 seconds per enrolled origin; on-demand spoken answer under 8 seconds, with urgent alert enqueue immediate after the diff.
- **cost:** Roughly $0.01–$0.08 per origin check depending on page size; dominated by semantic diff tokens. Local DOM filtering avoids paying for unchanged content.
- **security:** Only owner-enrolled origins are eligible; configuration must explicitly specify read, extract, redact, never-store, and may-speak rules and ships empty until supplied. Page text stays on the Mac/browser path, while the relay receives redacted change facts; alert payloads expire and are not persisted as raw text. Never auto-submit or message.
- **missing:** owner-authored per-origin and per-category policy; durable browser watch scheduler with tab/session affinity; local semantic snapshot/diff store with encrypted expiration; relay adapter that converts ranked diffs into offline_alert_inbox events

### "“Save what I’m looking at right now for later.” (Then, from the pendant: “Read back the thing I saved about this.”)"
- **useful because:** A physical bookmark gesture bridges the browser’s private authenticated context to the wearable without making the owner dictate a URL or copy sensitive text. Later retrieval can reopen the exact tab/session, detect that the page changed, and speak a concise summary with the original title and link.
- **path:** browser-extension → pendant → relay-realtime → mac-planner
- **model tier:** No model for capture beyond local title/URL/selection extraction; a small background model summarizes on retrieval. Realtime only handles the short spoken retrieval request.
- **latency:** Capture under 500 ms; retrieval under 5 seconds if the tab remains open, under 15 seconds if a refresh and summarization are needed.
- **cost:** Near-zero for capture; $0.002–$0.02 per retrieval summary, dominated by page excerpt tokens.
- **security:** Capture stores an encrypted pointer plus a short redacted excerpt, never an entire page. The owner configures origins/categories that may be retained; private or disallowed content becomes URL/title-only or is rejected with a local LED cue. Retrieval must verify the same browser session and should expire pointers automatically.
- **missing:** browser command that returns active tab, selection, and stable tab/session identifier in one typed result; firmware integration of the existing offline_moment_bookmark event with browser capture; encrypted expiring bookmark store and spoken retrieval intent; page-change warning and origin-policy enforcement at retrieval

### "“What am I looking at, and what should I notice?” while a private page is open in Safari."
- **useful because:** The pendant becomes a hands-free reader of authenticated dashboards, receipts, charts, and dense web forms. Unlike ordinary page extraction, it combines the visible screenshot, accessibility tree, and current tab identity, so it can answer spatial questions such as which row is overdue or what changed visually without exposing the page to a public web service.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** A local Mac vision model handles screenshot/accessibility grounding first; realtime receives only the cropped, redacted evidence needed for the owner’s immediate question. Use a cheaper model for a full-page summary and reserve realtime for short follow-ups.
- **latency:** First answer under 6 seconds; follow-up questions under 3 seconds while the tab snapshot is cached for a brief session.
- **cost:** About $0.01–$0.06 per visual question, dominated by image tokens; accessibility-first answers can be substantially cheaper than full screenshots.
- **security:** Evidence is scoped to the active Safari tab and a short-lived session; password fields, payment fields, and owner-configured origins are masked before inference. Nothing is persisted by default. The extension must visibly indicate capture and the pendant should refuse to read categories marked must-not-speak.
- **missing:** browser_snapshot result containing screenshot plus accessibility geometry and tab/session id; local redaction of password/payment/owner-defined regions before model dispatch; relay voice intent that preserves a short-lived visual context across follow-up turns; pendant UX for indicating private visual capture and cancelling it

### "“Check my private orders and calendar, and tell me if any delivery, appointment, or deadline conflicts with my day.”"
- **useful because:** This creates a genuinely cross-surface answer the owner cannot get from the browser or Mac alone: authenticated order portals provide delivery windows and status, while Calendar provides commitments. The owner hears one concise conflict warning on the pendant instead of manually comparing several logged-in sites.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Scheduled reconciliation uses a cheap background model after deterministic date/time extraction; realtime is only used for an on-demand question or a high-priority spoken alert.
- **latency:** A scheduled reconciliation completes within two minutes; an on-demand answer within 10 seconds.
- **cost:** Approximately $0.01–$0.05 per enrolled portal check, mostly from extracting and normalizing page content; unchanged pages should be skipped locally.
- **security:** The owner must explicitly enroll origins and define which order categories may be retained or spoken. Keep only normalized event facts (date, time window, source label), never raw page text or addresses unless explicitly allowed. Conflicts are advisory; no rescheduling, cancellation, or purchase occurs automatically.
- **missing:** owner-provided origin/category policy; browser page extraction with stable session affinity and date/time normalization; Mac Calendar event reader joined to browser-derived event facts; conflict-ranking job and pendant alert delivery

### "“Make me a verifiable packet showing what this logged-in page said at the time I checked it.”"
- **useful because:** For expenses, support disputes, insurance, or compliance, a spoken summary is not enough. The browser can capture the authenticated evidence while it is visible, and the Mac can create a local packet with source URL, timestamp, selected excerpts, and hashes so the owner can later prove exactly what was observed without keeping an entire private page in the cloud.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Local deterministic capture and hashing do the core work; a cheap model optionally labels excerpts and produces a one-sentence spoken index. Realtime is not needed except to acknowledge completion.
- **latency:** Capture and packet creation under 5 seconds; spoken confirmation under 2 seconds.
- **cost:** Typically below $0.01 per packet; local storage and hashing dominate, with optional summarization adding a few cents at most.
- **security:** Packets remain in the owner’s local workspace by default and are never uploaded by the relay. Origin policy controls whether screenshots, excerpts, or metadata are allowed; secrets and payment fields are redacted before hashing or storage. Sharing/export must be an explicit separate command.
- **missing:** atomic browser evidence capture with URL, timestamp, selection and screenshot; local redaction and content-addressed packet format; workspace index and later lookup by spoken label/date; pendant completion receipt and safe export workflow

### "“Tell me if one of my important logged-in sites has silently signed me out or is waiting for a security check, and guide me to fix it.”"
- **useful because:** Silent expiry currently makes browser automations fail only after the owner asks for something. An authentication-health monitor would notice login expiry, MFA challenge, consent renewal, or a blocked session early, then tell the owner which origin needs attention and open it to the exact recovery step—without attempting to defeat MFA.
- **path:** browser-extension → relay-realtime → mac-planner → pendant
- **model tier:** Local deterministic detectors classify login forms, MFA prompts, and HTTP/session failure markers; a cheap model handles unfamiliar layouts. Realtime only answers the owner’s recovery question.
- **latency:** Detection within one polling interval (under 30 seconds); opening the recovery page under 5 seconds; no automatic credential or MFA action.
- **cost:** Near-zero for known DOM/signals; occasional $0.005–$0.03 layout classification for an unfamiliar origin.
- **security:** Never capture passwords, OTPs, recovery codes, or cookies. Store only origin, state (healthy/expired/challenge), and timestamp. The owner explicitly enrolls origins; opening a recovery page is reversible, but entering credentials and approving MFA remains owner-driven.
- **missing:** per-origin login-health detectors in the extension; typed browser result that distinguishes login, MFA, consent, and ordinary error pages; relay alert deduplication and pendant delivery; recovery deep-link navigation with an owner-visible reason


## Changes it proposed to its own stack

### `browser-harness` — Add a single browser_snapshot action that atomically returns active tab identity, URL/title, accessibility tree with bounding boxes, viewport screenshot, selected text, and a redacted form-field map; include a short-lived snapshot token so follow-up voice questions can refer to the same view without resending the entire page.
- **owner gets:** The owner can ask the pendant about the exact private page, chart, or row currently visible and get a grounded answer instead of a generic extraction or a guess about which tab was meant.
- effort: Medium: extension content/background capture, typed result schema, local redaction, and a short-lived snapshot cache in the Mac agent.  ·  risk: Screenshots could capture secrets or stale content. Mask sensitive fields before leaving the Mac, expire tokens within minutes, show capture state, and fall back to accessibility-only output if capture fails.
- cost: Low recurring storage cost; modest per-question vision token cost only when the owner asks. No new hardware.  ·  latency: Adds roughly 0.5–2 seconds to first visual answer; follow-ups become faster because the snapshot token is reused.
- security: Improves security by making capture scoped, typed, expiring, and redacted rather than passing arbitrary page HTML. Requires owner-configured per-origin rules.
- depends on: working browser command enqueue path; extension support for browser_snapshot result; local-agent/redaction.js policy integration


## What it asked for

_Nothing._
## Its own summary

Discovered live Safari (9 tabs, active X tab) and confirmed the remaining practical blocker: the granted browser enqueue wrappers still do not resolve, so I cannot read or control tabs even though the extension is online. I produced three non-duplicate browser capabilities: enrolled authenticated change digests delivered to the pendant inbox, a physical page bookmark/retrieval bridge, and visual voice Q&A over the current private tab. I also proposed an atomic redacted browser_snapshot action and notified mac-planner.

**Biggest unknown:** Which concrete live action can replace the unresolved wrappers—especially browser_read_page and browser_snapshot—so authenticated tab work can actually be executed this round.

