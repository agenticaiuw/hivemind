# Harness derivation — mac-planner — round 266

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-accessibility-and-browser-state** — Live Mac observation at 2026-08-09T01:00:37Z shows AI Pendant Agent is Accessibility-trusted, synthesized input posts successfully, Screen Recording is enabled, and Safari/browser bridge has four durable sessions. The active foreground app is AI Pendant; current exposed tabs include USPS tracking and Google News. mac_readonly_inspect browser_tabs is resolver-ambiguous between action:browser_inspect and POST /browser/inspect, so it could not be invoked through that tool call.
  - evidence: mac_readonly_inspect foreground_app and running_apps calls both resolved GET /observe and returned accessibility.trusted=true, eventsPost=true, screenRecording=true, browser.sessions=4; browser_tabs call returned resolver ambiguity with nearest action:browser_inspect, POST /browser/inspect, and action:browser_list_tabs.

## Capabilities it proposed

### "“I pressed the pendant bookmark while I was researching—save exactly what I was looking at so I can ask about it later.”"
- **useful because:** The current bookmark is only a timestamp. This would turn a physical moment into a trustworthy cross-surface memory: the pendant supplies the intentional marker, the Mac supplies the active Safari tab and foreground app, and the relay binds them into one resumable capsule. It solves the common failure where 'that page' is lost among tabs and does not require the microphone to be open.
- **path:** pendant → mac-bridge → browser → relay → dashboard
- **model tier:** Background model for normalization and capsule labeling; realtime only when the owner asks a follow-up.
- **latency:** Acknowledge the button locally immediately; capture and upload within 2 seconds while the Mac is online. Later lookup under 1 second from indexed capsules.
- **cost:** Small background extraction call per bookmark, roughly $0.001–$0.01 depending on page text; most cost is capped page extraction, not model inference.
- **security:** Only an explicit button press creates a capsule. Default payload is URL, title, timestamp, active tab id, and a short redacted text excerpt; exclude password fields, form values, cookies, and hidden DOM. The owner should be able to delete a capsule. Browser-session data leaves the Mac only for this named capsule.
- **missing:** A relay event consumer that joins offline_moment_bookmark to a same-time Mac/browser observation; A bounded browser capture endpoint that returns active-tab metadata and owner-visible excerpt with redaction; A durable capsule index and a voice lookup route

### "“Before you send this message, submit this form, delete that file, or buy something, stage it and let me approve it with one deliberate press of the pendant.”"
- **useful because:** The owner’s stated rule is confirm before sending mail, deleting files, or buying, but today FULL_CONTROL_MODE has no approval gate. This creates a physical, unambiguous approval channel that works when the Mac is in another app: the server presents a compact spoken summary, the pendant shows a pending state, and only the matching button press releases the exact action manifest to the Mac/browser. A stale or changed page cannot silently consume approval.
- **path:** relay-realtime → pendant → mac-bridge → browser → dashboard
- **model tier:** Realtime model summarizes the proposed action in one short sentence; deterministic code—not a model—binds the nonce, action hash, target tab/resource, expiry, and one-time approval.
- **latency:** Stage acknowledgement under 300 ms; approval-to-execution under 2 seconds. Expire unanswered proposals after 2 minutes.
- **cost:** Negligible model cost (one short summary, usually under $0.01); engineering cost is the signed nonce ledger and browser/Mac enforcement.
- **security:** The approval must be bound to an exact canonical action hash, resource fingerprint, browser tab/session generation, and expiry. Any edit, navigation, reconnect, or retry invalidates it. Never speak or store full secrets in the approval prompt. This is specifically for high-impact mutations; ordinary reads and reversible actions remain direct.
- **missing:** A real enforcement seam in the Mac FULL_CONTROL executor (currently actionRisk is bypassed); Pendant firmware event handling for a one-shot approval/reject press using the existing button and LED without confusing recording/bookmark states; Browser-side preflight that returns a page fingerprint before submit/click; A relay approval ledger with replay protection and an execution receipt

### "“Read me the four newest things in my Safari Reading List, tell me which are worth my time, and queue the summaries so I can listen on the pendant.”"
- **useful because:** The owner has asked this exact question repeatedly, but the current browser inventory exposes tabs, not Reading List contents. Safari is the one place the Mac can reach authenticated reading-list data, while the relay can rank and compress it and the pendant can deliver it without making the owner sit at the screen. This turns an otherwise stranded request into a low-friction commute briefing.
- **path:** browser → mac-bridge → relay-realtime → pendant → dashboard
- **model tier:** Cheap background model for extraction, deduplication, and ranking; realtime is only for the spoken follow-up question.
- **latency:** Fetch and prepare in under 30 seconds for four items; first audio item playable within 5 seconds after the owner asks. Cache source text and summaries for 24 hours unless deleted.
- **cost:** About $0.02–$0.15 per run depending on article length and whether pages require extraction; browser retrieval and Opus delivery dominate wall time, not the ranking call.
- **security:** Reading List URLs and content are private browser data. Keep retrieval on the Mac/browser bridge, send only capped article text and metadata to the relay, redact account identifiers and paywall/session tokens, and never follow page instructions as commands. Do not automatically mark items read or remove them without an explicit request.
- **missing:** A Safari Reading List read-only bridge operation (including item order, URL, title, and saved date); A bounded article extraction/readability route that handles authenticated pages without exposing cookies; A scheduled or on-demand summarizer that emits a four-item ranked audio queue; A pendant queue label so the owner can skip or replay one item offline

### "“Seal my work session.”"
- **useful because:** At the end of a work block, the owner should be able to leave without manually hunting through tabs and documents. The pendant provides an intentional physical endpoint; the Mac records the exact apps, browser tabs, drafts, and unsent work; the relay turns that into a compact private handoff; and the browser/Mac close only the sensitive surfaces the owner has configured. Next time, the owner can see what was deliberately left open versus what was merely forgotten. This is an end-of-session boundary, not a passive bookmark or an always-on activity log.
- **path:** pendant → mac-bridge → browser → relay → dashboard
- **model tier:** Deterministic manifest collection first; a cheap background model writes a short handoff and separates unfinished work from noise. Realtime is unnecessary unless the owner asks for the spoken recap.
- **latency:** Local acknowledgement immediately; manifest and draft checkpoint within 3 seconds; spoken recap available within 10 seconds. If the Mac or relay is offline, retain the sealed manifest locally and upload later.
- **cost:** Usually $0.005–$0.03 for the short handoff; most work is bounded metadata collection and atomic local checkpointing. No article-sized context should be sent by default.
- **security:** This must never silently transmit document contents. Default to app/tab titles, URLs, file paths, dirty-state indicators, and draft hashes; require an explicit per-folder policy before including text. Closing tabs or apps is reversible only in some cases, so the owner chooses close, leave open, or lock-sensitive-tabs behavior. A seal is append-only and signed so a later resume cannot confuse a new session with the old one.
- **missing:** A first-class end_session/seal event from the pendant or relay, distinct from privacy pause and moment bookmark; A Mac/browser snapshot API that reports dirty documents and draft identity without scraping their contents; An atomic cross-surface session manifest with per-resource retention and redaction policy; A resumable handoff view and a deterministic policy for which sensitive tabs/apps may be closed or locked


## What it asked for

_Nothing._
## Its own summary

This round produced three distinct cross-surface capabilities: (1) a physical pendant bookmark that captures the active Safari/app context into a resumable capsule, (2) exact-hash, one-shot pendant approval for high-impact Mac/browser mutations, and (3) a Safari Reading List concierge that ranks the four newest items and queues spoken summaries. The approval channel is the highest-value safety/usefulness change: it fills the real gap that FULL_CONTROL_MODE currently has no enforcement gate. Live observation also established that Accessibility, Screen Recording, and synthesized input are now working on AI Pendant Agent, with four browser sessions online.

**Biggest unknown:** The system still lacks a confirmed Safari Reading List read-only route and a bounded article extractor. The browser inspection tool is currently resolver-ambiguous (action:browser_inspect vs POST /browser/inspect), and the approval proposal still needs an actual executor enforcement seam plus pendant approval-event firmware. I do not need another generic Mac permission grant; those permissions are live.

