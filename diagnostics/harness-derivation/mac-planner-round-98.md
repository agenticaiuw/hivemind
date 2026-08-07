# Harness derivation — mac-planner — round 98

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **granted Mac read surfaces** — mac_readonly_inspect and mac_read_sources are granted in schema but currently return 'tool was granted a schema but has no implementation yet'; they cannot inspect apps/tabs or Calendar/Mail this round.
  - evidence: Direct calls to both tools returned implementation-missing errors.

## Capabilities it proposed

### "When I say “save this for later” while I’m looking at a page, capture the page and my spoken note as a sourced, searchable research card; later I can ask the pendant what I saved and have the Mac reopen the exact source."
- **useful because:** This turns an ephemeral browser tab plus a two-second pendant utterance into durable memory with provenance. It works across the surfaces: the browser has the authenticated page, the pendant supplies intent while away from the keyboard, the relay keeps the request alive, and the Mac creates/reopens a human-readable artifact. It is materially safer than an unsourced memory because every claim points back to URL, tab, timestamp, and excerpt.
- **path:** browser-extension → relay-realtime → mac-planner → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Realtime tier only parses the short capture command and acknowledges it. A cheaper background model normalizes the note, extracts a short title/topics, deduplicates against existing cards, and generates a citation-preserving summary. Retrieval is semantic plus exact-topic matching; no model call if the user asks for a title/URL lookup.
- **latency:** Acknowledge the pendant within 500 ms, enqueue capture in under 2 s, and finish the card in 5–15 s. Retrieval should return the top cards in under 2 s and open the chosen source on the Mac in another 1–3 s.
- **cost:** About $0.001–$0.01 per capture depending on page length and summarization; retrieval usually under $0.001. Dominant costs are extracting long authenticated pages and background summarization, so cap captured text and hash unchanged excerpts.
- **security:** Authenticated page content and the spoken note leave the browser/Mac only to the owner's relay and memory store; redact secrets and form fields before persistence. Store URL, title, excerpt hash, and source timestamp by default, with full text opt-in. Never submit forms or alter the page. Reopening a private URL must preserve its browser session and should fail closed if the session is gone. The pendant acknowledgement should not read the captured page aloud in public.
- **missing:** A browser-extension command that returns the active tab's selected/semantic content with URL, tab ID, and stable excerpt locators; A durable research-card schema joining capture key, browser provenance, normalized text, and context-graph entities; A background indexing/deduplication worker and retention controls for private captures; An implementation of the granted Mac read-only inspection/sources tools so retrieval can verify the target tab and calendar context; A relay-to-Mac resumable enqueue/receipt path for captures made while the Mac is temporarily offline

### "Tell me before my important logged-in browser sessions expire or get signed out, and when I’m back at the Mac, open only the affected sign-in pages so I can restore them without exposing page contents."
- **useful because:** Silent session expiry is a recurring failure mode for every authenticated workflow: a morning brief can look empty, a form can be half-filled, or a watch can stop silently. This gives the owner an actionable warning from the pendant while keeping private page contents out of the alert, then uses the Mac only for the narrowly scoped recovery step.
- **path:** browser-extension → relay-realtime → mac-planner → unified → faculty-perception → faculty-action
- **model tier:** No expensive model for detection: a deterministic browser heartbeat/session-state classifier runs on the relay or extension. Use the realtime tier only to understand a spoken request such as “which account needs attention?” and a cheap background model to rank urgency from session age and scheduled watches.
- **latency:** Heartbeat every 5–15 minutes with <1 s relay processing; alert within one heartbeat of an auth transition. On request, enumerate affected sessions in <2 s; Mac opens the recovery pages in 1–3 s.
- **cost:** Near-zero model cost; roughly a few thousand lightweight heartbeat events per month. The dominant cost is relay/browser storage and any optional notification audio, not inference.
- **security:** Transmit only state (session ID, origin, auth-needed/healthy, last-seen), never cookies, tokens, DOM text, screenshots, or typed credentials. Keep an allowlist of origins and let the owner pause monitoring from the pendant. Never auto-enter credentials or submit MFA; opening a sign-in page is the maximum automatic action. Expiry records should have short retention and be deletable.
- **missing:** A browser-extension heartbeat payload that can distinguish healthy, expired, MFA-required, and network-failed without exposing page content; Durable per-origin watch policy with quiet hours and a last-alert fingerprint to prevent repeated alerts; A relay alert queue that can reach the pendant and retain the event while the Mac is offline; A Mac action that opens only the affected origin's re-auth URL and returns a receipt; A small dashboard showing session state and allowing per-origin pause/delete

### "When a meeting, deadline, or reservation changes in one place, tell me what other commitments it breaks and prepare the coordinated cleanup across my Mac, browser, and pendant—updated calendar details, draft notifications, and the exact tabs/files to close or reopen."
- **useful because:** Today the surfaces are isolated: a changed calendar event does not reconcile the email thread, authenticated booking page, open documents, reminders, or the owner's spoken plan. This would maintain a live dependency map of commitments and prepare one coherent recovery packet instead of making the owner discover each consequence manually.
- **path:** relay-realtime → mac-planner → browser-extension → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use a cheap background model for entity resolution and dependency/risk ranking; use realtime only when the owner asks for the impact or wants the prepared cleanup read aloud. Deterministic connectors should detect source changes and produce diffs before any model call.
- **latency:** Detect changes within 2–5 minutes for watched sources, generate an impact packet within 30 seconds, and speak a concise alert on the next available pendant connection. Preparing Mac/browser drafts should take under 10 seconds after the owner requests it.
- **cost:** Roughly $0.005–$0.03 per meaningful change, dominated by resolving related messages/pages and generating a short impact summary; unchanged polling should be deterministic and nearly free.
- **security:** The dependency graph contains sensitive relationships between calendar, mail, private browser pages, and local files. Keep raw content on the Mac where possible; send the relay only normalized event IDs, titles, times, and redacted impact facts. Never send or delete anything automatically. Any calendar edit, email send, booking change, or file deletion remains a separately previewed action under the owner's maximum-access policy.
- **missing:** A cross-source commitment/dependency graph with provenance, confidence, and expiry rather than isolated per-surface records; Change feeds or reliable polling adapters for Calendar/Mail and authenticated browser watches, with normalized before/after diffs; A planner that maps one changed commitment to affected drafts, reminders, files, tabs, and pending jobs; A single review packet format that the relay can summarize on the pendant and the Mac can render with source links and prepared actions; Idempotent reconciliation actions and receipts so a partially completed cleanup can resume without duplicating drafts or edits


## Changes it proposed to its own stack

### `mac-harness` — Implement the two newly granted bounded read-only Mac tools rather than exposing schema-only stubs: mac_readonly_inspect should call a signed local helper for running apps, foreground app, browser tab metadata, accessibility state, UI snapshot, and allowlisted directory listings; mac_read_sources should use AppleScript/read-only EventKit/Mail queries for calendar and mail, enforce account_scope, redact by default, cap result sizes, and emit source timestamps plus receipts. Keep them separate from mac_run_actions and do not grant arbitrary shell access.
- **owner gets:** The assistant can currently act on the Mac but cannot reliably see what is open or read a bounded calendar/mail brief through the granted interfaces. Implementing these makes “what am I looking at?”, meeting preparation, and recovery from failed browser jobs dependable without scraping or mutating anything.
- effort: Medium: local helper adapters, permission/error normalization, redaction and tests for each source; browser tabs require extension bridge integration. UI snapshots remain unavailable until the owner grants Screen Recording/Accessibility to the correct binary.  ·  risk: Calendar/Mail queries could leak private content if scoping or redaction fails; mitigate with snippets-only defaults, strict size limits, account allowlists, audit receipts, and explicit unavailable states. UI inspection must never fall back to mouse or keystrokes. Recover by returning a typed permission/offline error, not guessed state.
- cost: Low ongoing API cost; bounded local reads are cheaper than model vision. Engineering cost is the main expense. UI snapshots may add local image storage/transport cost and should be opt-in.  ·  latency: Typically 100–800 ms for app/tab/source metadata; UI snapshots may take 1–3 s and should be requested only when needed.
- security: Read-only boundary materially reduces risk, but browser URLs/titles and mail/calendar snippets are sensitive. Keep data local where possible, redact by default, and attach provenance/TTL to every returned fact.
- depends on: mac_readonly_inspect and mac_read_sources granted schemas need real implementations; A signed localhost helper with the existing bearer-token boundary; Owner TCC grants only for UI snapshot features; non-visual app/browser/source reads should work without them


## What it asked for

_Nothing._
## Its own summary

Round 98 discovery found the new grants are schema-only: mac_readonly_inspect and mac_read_sources both return “granted a schema but has no implementation yet,” so no live app/tab/calendar/mail state could be verified. I recorded that finding. I proposed two owner-useful directions: a provenance-preserving browser-to-pendant research capture (noted as somewhat close to the existing resume/bookmark work), and a distinct authenticated-session expiry sentinel that alerts without page contents and opens only re-auth origins. I also proposed implementing the bounded Mac read tools with strict redaction, scoping, receipts, and typed permission errors.

**Biggest unknown:** Whether the browser extension can currently report authentication state (healthy/expired/MFA/network failure) without DOM content, and whether a relay-to-pendant alert queue exists. The granted Mac observation/source tools also need actual implementations before I can inspect the owner's live state.

