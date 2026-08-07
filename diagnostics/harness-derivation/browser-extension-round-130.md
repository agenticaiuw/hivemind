# Harness derivation — browser-extension — round 130

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser** — Safari bridge is online with 3 tabs; authenticated Gmail tab 901464 is readable via browser_snapshot (80 interactive elements, Inbox 14,987 unread), while browser_read_page on Gmail failed due extension frame access.
  - evidence: POST /execute browser_list_tabs and browser_snapshot at 2026-08-07T18:05:50Z

## Capabilities it proposed

### "When I say “save this web task,” remember the exact authenticated page, what I was trying to do, the fields already filled, and the next safe step; later, “resume that task” restores the tab and briefs me from the pendant before changing anything."
- **useful because:** The owner can pause a logged-in application, support case, or checkout without losing the fragile browser state, then resume days later from a wearable command. Safari supplies private session reach, the Mac preserves local context, and the relay/pendant make the task resumable when the laptop is closed.
- **path:** browser-extension → mac-planner → relay-realtime → relay-realtime
- **model tier:** Background model extracts a compact task capsule; realtime model only handles the short spoken save/resume exchange.
- **latency:** Save in under 5 seconds; resume spoken confirmation in under 3 seconds, with tab restoration allowed to continue asynchronously.
- **cost:** About $0.01–$0.05 per save/resume depending on DOM extraction; browser and Mac work dominate, not model tokens.
- **security:** Capsule contains authenticated URL, page snippets, and possibly typed secrets. Encrypt at rest, redact passwords/payment values, bind to the Safari session, expire by default, and require confirmation before any submit/send/purchase step.
- **missing:** Durable browser task-capsule schema with encrypted/redacted field state; Extension support for restoring scroll position and unsent form state; Mac/relay lookup by a spoken task name

### "Read this private web page to me."
- **useful because:** The owner can consume an authenticated article, dashboard, ticket, or long document while walking, without copying it into another app or exposing it to public web search. Safari reads the page behind its login, the relay produces a concise spoken version, and the pendant delivers it through the audio bridge.
- **path:** browser-extension → relay-realtime → relay-realtime → mac-planner
- **model tier:** Use a cheaper background model for extraction, chunking, and summary; use realtime only for interruption, pause, and follow-up questions.
- **latency:** Start speaking a 1–2 sentence orientation within 4 seconds; stream subsequent sections while extraction continues.
- **cost:** Roughly $0.02–$0.15 per long page, dominated by speech synthesis/audio transfer; short pages should stay under $0.03.
- **security:** Authenticated content leaves Safari for processing. Show source title/domain, avoid retaining raw HTML, redact obvious secrets, encrypt temporary audio, and delete after playback unless the owner asks to save it.
- **missing:** A page-content extraction path that works reliably on Gmail and other iframe-heavy pages; Streaming page chunks into the audio pipeline with pause/resume offsets; Pendant playback controls mapped to current document position

### "Before I submit this form or send this web message, check the details against my email, calendar, and local files, then tell me in one sentence what—if anything—looks wrong. Do not submit it."
- **useful because:** This is the system’s highest-value safety net: it catches wrong dates, names, amounts, account numbers, and stale instructions at the moment they matter. The browser sees the private form, the Mac can inspect the owner’s local records and mail/calendar, the relay reconciles evidence, and the pendant gives an immediate warning while leaving control with the owner.
- **path:** browser-extension → mac-planner → relay-realtime → relay-realtime → mac-planner
- **model tier:** Background model performs structured field extraction and cross-source comparison; realtime model speaks only the concise discrepancy report.
- **latency:** Under 8 seconds for ordinary forms; if sources are large, return a quick “checking” cue on the pendant and finish within 30 seconds.
- **cost:** About $0.03–$0.20 per check, mostly local/browser extraction and context size; no cost for a form that has no related records.
- **security:** This joins highly sensitive form data with private mail/files/calendar. Keep raw values local where possible, send only field hashes or minimal excerpts to the relay, never log secrets, and treat submit/send/purchase as an explicit owner-controlled final action.
- **missing:** A browser snapshot of current form values and the exact pending submit target; Local structured readers for mail/calendar/files with provenance and field-level redaction; A reconciliation engine that reports discrepancies without becoming an execution gate; Pendant UI/audio cue for “verified”, “uncertain”, and “mismatch”

### "Use my pendant as the physical key for private browser work: when I say “private mode,” only the Safari session paired to the pendant may be read, and pause all private-page work immediately if the pendant disconnects or I say “lock.”"
- **useful because:** Today the browser bridge can reach authenticated pages, but there is no owner-visible, hardware-bound boundary around that access. This would let the owner safely use private Gmail, finance, health, and work sites through the hive without leaving an unattended relay job able to continue reading them.
- **path:** browser-extension → relay-realtime → mac-planner → relay-realtime
- **model tier:** No model is needed for the lock/unlock decision; realtime handles the short voice command and a background model may summarize only after the hardware session is authenticated.
- **latency:** Lock locally in under 250 ms on disconnect or button press; unlock and announce readiness within 3 seconds after a fresh pendant challenge.
- **cost:** Negligible per-use model cost; one-time engineering for cryptographic pairing, extension messaging, and relay session binding.
- **security:** The pendant must never transmit page contents as its credential. Use a per-device key and nonce challenge, rotate session tokens, wipe queued browser commands and cached excerpts on lock, and require an explicit physical button gesture plus voice for unlock. This is a boundary and audit signal, not a guarantee against a compromised Mac.
- **missing:** Hardware-backed or securely stored pendant identity key and pairing flow; Browser extension API for lock-state enforcement and queue cancellation; Relay/session middleware that binds every browser read and result to the live pendant lease; Visible and spoken lock-state indicator on Mac and pendant


## What it asked for

### `s13-0xuw` (skill) — audio_reading_bookmark
- does: While a browser page or briefing is being spoken, a short press pauses playback and stores the current document capsule/chunk offset; a double press resumes from that offset, and a long press records a local “ask about this section” marker for the next relay turn.
- must be on-device because: Pause/resume and bookmark must work with no LTE or relay round trip, including when the pendant is USB-attached to the Mac and the audio stream briefly drops.
- trigger: Pendant playback button events and local audio-buffer underrun/resume events.
- storage: Persist one active bookmark and four recent bookmarks in pendant flash/NVS; approximately 1–2 KB total. Do not persist page text.
- RAM budget: Approximately 2 KB state plus under 1 KB event buffer, well within the 211,608 B application RAM budget; audio buffers remain owned by the existing playback path.

## Its own summary

Safari is now genuinely online (3 tabs); I verified the authenticated Gmail tab via browser_snapshot, though browser_read_page still fails on its frame. I recorded three new owner-facing capabilities: resumable authenticated web-task capsules, hands-free spoken reading of private pages, and cross-checking a pending web form/message against local mail/calendar/files before submission. I also queued an offline pendant audio bookmark skill so pause/resume survives a dropped link. A proposed iframe fallback was correctly rejected as already covered, so I did not rephrase it.

**Biggest unknown:** The remaining product gap is not browser availability but reliable extraction from protected/iframe-heavy pages and a durable, encrypted cross-surface task state; the granted browser enqueue tools remain schema stubs, although POST /execute is currently usable directly.

