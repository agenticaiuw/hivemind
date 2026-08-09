# Harness derivation — mac-planner — round 267

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac accessibility and browser state** — Live /observe now reports AI Pendant Agent Accessibility trusted, Screen Recording true, synthesized events verified; 4 browser sessions are open, with USPS tracking and Google News active sessions. mac_readonly_inspect browser_tabs remains resolver-ambiguous, but host observation exposes tabs.
  - evidence: mac_readonly_inspect running_apps resolved GET /observe at 2026-08-09T01:04:09Z; accessibility.trusted=true, screenRecording=true, inputReachability.status=verified, browser.sessions=4.

## Capabilities it proposed

### ""What are the four latest things in my Safari Reading List?" Then read me a four-item answer and, if I say 'save them', put a dated shortlist in my workspace."
- **useful because:** The owner has asked this repeatedly and it currently fails. It combines the browser session that can actually see authenticated Safari state, the relay that can rank and summarize, and the Mac that can write a durable note; no single node has all three reaches.
- **path:** browser-extension → relay-realtime → mac-planner → pendant
- **model tier:** Background model for extraction and ranking; realtime model only for the short spoken answer and save confirmation.
- **latency:** 5-10 seconds to inspect and rank; under 1 second to speak the result once ready.
- **cost:** About $0.01-$0.05 per request, dominated by page extraction and summarization; note creation is negligible.
- **security:** Reading-list URLs and titles leave the browser only as redacted metadata. Never send page bodies by default. Saving is a local note mutation and must follow the owner's existing destructive-action policy (not destructive, but explicit 'save them' remains the trigger).
- **missing:** A browser-harness operation that enumerates Safari Reading List items (not just open tabs or the active page); A stable browser result schema for title/url/date-added with truncation and redaction; A Mac note-write receipt linked to the browser extraction id

### ""Mark this moment." The system should join my pendant bookmark with the current browser tab, foreground Mac app, and a one-line note draft, so later I can ask what I was doing at that moment."
- **useful because:** The pendant already captures an offline moment, but a timestamp alone is not useful enough. This creates a searchable cross-surface breadcrumb while the owner is actually switching between browser and Mac work; it is specifically valuable when the link is intermittent because the pendant event can arrive later and still be joined by time.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → mac-vision
- **model tier:** Cheap background model for event joining and one-line labeling; realtime tier only if the owner asks for an immediate spoken confirmation.
- **latency:** LED acknowledgement immediately; join and draft within 3 seconds after the bookmark upload; no blocking on the browser or Mac.
- **cost:** Roughly $0.005-$0.02 per bookmark, mostly one short classification call; local observation and note drafting are cheap.
- **security:** Store URL/domain and app name by default, not page text or keystrokes. Private windows, secure-input fields, and secrets must be represented as redacted markers. The note remains a draft until the owner asks to save; expired unmatched events should be discarded.
- **missing:** A relay event-correlation record keyed by device timestamp plus upload receipt; A browser snapshot route that returns the active tab's metadata without page body; A Mac note-draft endpoint that can attach the correlation id and expose an undo receipt

### ""Give me a one-sentence attention brief." Combine today's calendar and unread mail with active browser sessions, Mac health, and pending pendant alerts, and mention only the highest-priority action."
- **useful because:** The existing calendar/mail brief does not know that the owner is blocked in a browser task, offline from the pendant, or low on Mac connectivity. A single ranked sentence is the useful cross-node product: it prevents the owner from hearing five disconnected status reports.
- **path:** relay-realtime → mac-planner → browser-extension → pendant
- **model tier:** Background model builds the ranked attention object on schedule; realtime model speaks only the final sentence when requested or at the scheduled brief.
- **latency:** Scheduled precompute before 07:30; on-demand response under 2 seconds if cached, under 8 seconds on a refresh.
- **cost:** About $0.02-$0.08 per refresh, dominated by ranking and summarization; most inputs are small metadata snippets.
- **security:** Mail bodies remain redacted unless the owner has already enabled body reads. Browser data is URL/title/domain only. Never speak secret tokens or unrelated inbox content. The ranking must show its source labels in the durable brief so a wrong priority can be corrected.
- **missing:** A pendant-inbox read/export route for pending alert metadata; A single server-side attention-ranking endpoint that accepts Calendar/Mail/browser/Mac/device facts with provenance; A freshness contract so stale browser or device observations cannot outrank fresh mail/calendar deadlines

### ""What exactly changed because of the last thing you did for me?" The pendant should read back a concise, source-linked change receipt for the latest Mac/browser action, including the affected app or URL, files or records touched, whether it succeeded, and the available undo or recovery step."
- **useful because:** Today an action can happen on the Mac while the owner is away from the screen, leaving them to trust an opaque success message. A spoken, source-linked receipt makes automation accountable: the owner can catch a wrong tab, wrong file, or partial failure immediately and recover without returning to the Mac.
- **path:** relay-realtime → mac-planner → browser-extension → pendant
- **model tier:** Cheap background model normalizes action receipts and extracts the one-sentence explanation; realtime tier only speaks it when requested or immediately after a high-impact action.
- **latency:** Receipt ingestion under 1 second after an action; spoken answer under 2 seconds from the owner's question.
- **cost:** Under $0.01 per receipt in normal use; cost is dominated by occasional summarization of multiple receipts, not storage or transport.
- **security:** Redact file contents, message bodies, tokens, and full private URLs; expose only resource names, domains, operation class, result, and recovery pointer. Never claim success without an execution receipt. Destructive actions should say explicitly that no automatic undo exists.
- **missing:** A stable cross-surface receipt envelope with action id, exact touched-resource references, result/error, timestamps, and undo/recovery metadata; Browser-command receipts that can be joined to Mac job receipts without exposing page content; A pendant-facing receipt notification and query path with bounded retention and local privacy-latch behaviour


## Changes it proposed to its own stack

### `browser-harness` — Add a typed, read-only Safari Reading List export operation that returns at most N items with title, URL, date-added, source list, and redaction status; give each extraction a correlation id and make the result consumable by the relay brief and Mac note writer. Keep it separate from active-tab inspection so the owner can finally retrieve the four items they have repeatedly asked for.
- **owner gets:** It directly fixes the one browser question that has repeatedly failed, without requiring page-body scraping or a broad new browser permission.
- effort: Medium: browser extension/native Safari bridge plus one relay schema and tests for empty, private, and unavailable lists.  ·  risk: Safari changes or a missing Reading List permission could return an explicit unavailable result. URL metadata can be sensitive; redact private-window entries and log only counts/hashes. Recovery is read-only retry; no browser mutation.
- cost: Low runtime cost; one small extraction response and a short ranking call when spoken.  ·  latency: About 1-3 seconds for local extraction, plus 2-5 seconds for ranking if the owner asks for a spoken summary.
- security: Read-only metadata scope, no page bodies, no cookies or credentials; owner-visible provenance and a deleteable local receipt.
- depends on: A concrete browser-harness dispatch enum for reading_list; A bounded result schema with title/url/date-added fields; A correlation id accepted by /briefing or the Mac note writer


## What it asked for

_Nothing._
## Its own summary

Established fresh live state: Mac Accessibility and Screen Recording are now trusted for AI Pendant Agent, synthesized input is verified, and four browser sessions are open; the old 'permission denied' premise is no longer true. Recorded three new cross-node capabilities: Safari Reading List retrieval and save, bookmark-to-current-work breadcrumb, and a ranked one-sentence attention brief. Also proposed the concrete browser-harness change that makes the repeatedly failing Reading List request possible.

**Biggest unknown:** The browser harness still lacks a confirmed typed Reading List export operation; until that is added, active-tab inspection cannot answer the owner's repeated Safari Reading List question. The bookmark and attention ideas also need a durable cross-surface correlation/provenance record rather than more UI automation.

