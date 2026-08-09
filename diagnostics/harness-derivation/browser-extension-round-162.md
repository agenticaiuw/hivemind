# Harness derivation — browser-extension — round 162

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Watch the authenticated pages I choose and tell me only when something materially changed, with a one-sentence explanation on my pendant."
- **useful because:** This is the browser's unique reach turned into a daily benefit: private dashboards, order pages, and account notices can be monitored without making public web search or the Mac pretend it has Safari's login state. The relay ranks changes and the pendant delivers only actionable ones.
- **path:** browser-extension → relay-realtime → mac-planner → relay-realtime
- **model tier:** background model for scheduled page capture/diff and ranking; realtime only when the owner asks a follow-up; pendant playback is local via offline_alert_inbox
- **latency:** Scheduled checks may take 30–90 seconds per origin; urgent alert delivery within 10 seconds after a completed capture.
- **cost:** Low background cost: one cheap extraction/diff call per changed page, with realtime spend only for follow-up questions; network traffic and authenticated page text dominate, not model tokens.
- **security:** Page content leaves Safari for relay processing, so per-origin configuration must be explicit and start empty: read/extract/redact/never-store plus categories may_speak/must_not_speak. Never persist raw page text; encrypt watch tokens and retain only hashes, redacted snippets, and receipts. No submit/click mutation in a watch.
- **missing:** A durable browser watch scheduler that stores per-origin rules and prior normalized snapshots; A semantic diff/redaction worker connected to GET /watches and GET /browser/inspections; A relay-to-pendant alert adapter using the accepted offline_alert_inbox skill; Owner-supplied first origins and speech/persistence categories

### "From my pendant, say “make this web form ready” and have Safari fill the authenticated form from my spoken details, have the Mac validate the fields and show me exactly what will be submitted, then let me approve or edit it by voice before anything is sent."
- **useful because:** It turns the browser's logged-in access into a safe hands-free workflow instead of merely reading pages. The Mac can catch missing or inconsistent fields, while the pendant keeps the owner in control of the final irreversible action.
- **path:** relay-realtime → browser-extension → mac-planner → mac-vision → relay-realtime
- **model tier:** realtime for the short spoken interaction and field-level clarification; background model for validation and summarizing the prepared payload.
- **latency:** Fill within 5 seconds for a known form; validation and spoken preview within 8 seconds. Submission remains an explicit owner action.
- **cost:** Moderate per form: one realtime turn plus one cheap validation pass; DOM snapshots and screenshots are the main context cost.
- **security:** Authenticated DOM and spoken personal data are sensitive. Keep raw DOM local to Safari/Mac where possible, redact secrets before relay, retain only field labels and a hashed preview, and stop before send/delete/purchase. Owner policy says destructive actions require confirmation.
- **missing:** Form schema extraction that maps labels to values without hard-coded site selectors; A browser action transaction with draft/preview/rollback and a final submit command; A cross-surface confirmation event that the pendant can render as a concise diff; Per-origin and per-category rules supplied by the owner

### "Remember the important facts I encounter in my logged-in browser, and later let me ask my pendant “what did that page say?” without reopening or rereading the whole site."
- **useful because:** The browser can see private material no other node can reach, while a local redacted index makes that knowledge useful after the tab is closed. The owner gets answers instead of repeating searches, without storing full page copies.
- **path:** browser-extension → mac-planner → relay-realtime → relay-realtime → browser-extension
- **model tier:** background model creates local structured facts and embeddings; realtime only answers a short retrieval question and cites the originating page.
- **latency:** Index a selected page in under 5 seconds; answer from the local index in under 2 seconds, with a slower fallback only when the source tab is still available.
- **cost:** One extraction/embedding pass per explicitly saved page; retrieval is cheap. Storage and redaction computation dominate; never embed or retain unselected pages.
- **security:** Selection must be explicit (browser command or owner phrase), and each origin needs read/extract/redact/never-store plus speak/persist category rules. Keep raw text on the Mac, encrypt the index, retain URL/title/time and minimal fact spans, and provide “forget this page/origin” deletion receipts.
- **missing:** A browser-side “save this page” command and local encrypted fact store; A redaction-aware fact/embedding pipeline with source-span citations; Voice commands to select, query, and erase indexed pages; Owner configuration for allowed origins and sensitive categories

### "If I say “privacy lockdown” into my pendant, immediately lock my Mac, freeze Safari automation, and close or quarantine authenticated tabs; when I return, let me unlock and restore only the tabs I explicitly choose."
- **useful because:** The owner wears the pendant continuously, so it can be a physical panic button for browser sessions that nobody else can provide. A lost, borrowed, or exposed Mac would not leave private logged-in pages open while preserving a recoverable work state.
- **path:** relay-realtime → mac-planner → browser-extension → mac-vision → relay-realtime
- **model tier:** Realtime handles the short command and acknowledgement; the Mac performs deterministic lock/quarantine operations without an LLM; background work can build the tab manifest for selective restore.
- **latency:** Lock Mac and halt browser commands within 2 seconds of a confirmed pendant event; restore is explicitly interactive and may take 10 seconds.
- **cost:** Negligible model cost after wake-word/command recognition; the main work is local tab/session manifest storage and secure IPC.
- **security:** The lockdown command must work even if relay connectivity is unavailable when the pendant is USB-attached or nearby. Store only encrypted tab origin/title/session identifiers, never page bodies or cookies. Require a physical button chord or spoken confirmation to restore; do not transmit credentials.
- **missing:** A signed pendant-to-Mac emergency channel that works independently of the normal browser queue; A Mac lock/quarantine primitive and encrypted Safari tab manifest; Browser extension suspend/resume semantics for in-flight commands; A recovery UX that prevents accidental restoration of sensitive origins

### "After you do anything in my logged-in browser, give me a tamper-evident spoken receipt: which origin and tab were used, what fields changed, what was not sent, and a link or snapshot I can verify later."
- **useful because:** Today a browser automation result can be an opaque success message. A concise, verifiable receipt makes private-session automation trustworthy and lets the owner catch an unintended tab or field before it becomes a problem.
- **path:** browser-extension → mac-planner → relay-realtime → mac-vision → browser-extension
- **model tier:** Deterministic local code computes tab identity, action sequence, DOM-field diff, and hashes; a cheap model compresses it into one spoken sentence; realtime is only for follow-up questions.
- **latency:** Receipt generated within 1 second after each action batch and spoken within 3 seconds; full visual verification can be requested asynchronously.
- **cost:** Very low model cost; hashes and structured event logs are local. Optional screenshot OCR is the dominant compute and storage expense.
- **security:** Receipts must redact values by category and never store passwords, tokens, or raw page text. Bind each receipt to an origin, tab ID, monotonic action sequence, and signed local timestamp; expose deletion by receipt ID. A receipt proves what the harness observed, not that a remote server accepted a submission.
- **missing:** A browser action event ledger with tab/session affinity; Local signing and receipt verification exposed to the relay; Structured field-diff extraction for browser actions; A pendant-friendly receipt renderer and retention/deletion controls

### "Describe the chart, map, or image currently visible in my logged-in Safari tab, read its key values aloud, and let me ask follow-up questions about a highlighted region without uploading the whole page."
- **useful because:** Authenticated dashboards often hide their meaning in canvas charts and images that ordinary page extraction misses. The browser can see the private tab, Mac vision can inspect pixels, and the pendant can make the result usable while walking or away from the screen.
- **path:** browser-extension → mac-vision → relay-realtime → mac-planner
- **model tier:** Mac vision performs local crop/OCR/chart grounding; realtime turns the grounded result into a short spoken answer and handles follow-ups. Use a cheaper background model for non-urgent chart transcription.
- **latency:** Initial crop description in 4 seconds; region follow-up in 2 seconds; never block the browser on a full-page upload.
- **cost:** Moderate only when invoked: one local vision pass plus a short realtime turn. Cropping before inference keeps tokens, bandwidth, and privacy exposure low.
- **security:** Send only the selected viewport crop or accessibility tree, not the entire authenticated page. Apply origin/category redaction before any relay call, do not retain pixels by default, and show the source tab title and timestamp in the spoken answer. Clicking or exporting remains a separate action.
- **missing:** Extension command to capture a user-selected viewport rectangle and tab metadata; Mac-local chart/OCR/vision result schema with coordinates and confidence; Region selection through the pendant (or an on-screen highlight cue); Relay prompt path that accepts grounded visual results without raw-page persistence


## Changes it proposed to its own stack

### `firmware` — Ship a true 24 kHz superwideband path end to end: capture at 24 kHz (or a hardware-supported 24 kHz equivalent) into the nRF9160 encoder, negotiate an explicit 24 kHz Opus mode through cloud-relay/opusTranscode.js, and keep the existing 31,250 Hz I2S bridge only as the final playback wire conversion. Add a capability handshake and a fallback to today's 15,625 Hz capture/16 kHz uplink when CPU or link budget is exceeded.
- **owner gets:** The owner's speech and the assistant's replies would sound less tinny and less fatiguing, especially for music, names, and noisy environments; the fallback means a weak link still works instead of failing.
- effort: High: firmware audio clock/capture changes, Opus mode and relay negotiation, ESP32 bridge clock validation, and acoustic regression tests. Prototype on the connected nRF9160 and ESP32 over USB before changing the enclosure.  ·  risk: The nRF9160 currently spends roughly 87% of one core when encode and decode overlap; 24 kHz capture may overrun buffers or starve LTE/audio tasks. Recover by capability negotiation, watchdog-protected ring buffers, and automatic downgrade to the known-good mode. Validate clock drift and packet loss before enabling by default.
- cost: No immediate component cost for the USB prototype; a product may need a better audio codec/clock and roughly $5–15 BOM increase. Higher bitrate and DSP raise radio airtime and battery use, likely 10–30% during active speech.  ·  latency: Potentially +10–25 ms encode buffering unless the capture pipeline is optimized; playback latency can remain near the current 60 ms frame cadence.
- security: No new data class or endpoint; audio remains encrypted in transit. Capability negotiation must not log raw audio or persist codec metadata tied to speech content.
- depends on: Owner's requested 24 kHz superwideband target; nRF9160/ESP32 USB-connected test harness; cloud-relay/opusTranscode.js changes; A measured CPU/RAM budget for simultaneous encode/decode; An end-to-end audio quality and fallback test


## What it asked for

_Nothing._
## Its own summary

Round 162 produced four new recorded items: a configurable authenticated-page change radar feeding the pendant, a voice-driven browser form drafter with Mac validation and explicit final approval, a true negotiated 24 kHz superwideband audio path with fallback, and an opt-in local fact index for private pages. Discovery confirms Safari is now online with 9 tabs, but every granted browser enqueue wrapper still fails resolver ambiguity and /browser/inspect is not a usable GET route. I told mac-planner. To make the browser ideas real, I still need a working action:browser_list_tabs/browser_read_page/browser_snapshot resolution, durable per-origin rules supplied by the owner, and watch/index persistence. For audio, I need the connected USB prototype to measure CPU, clock drift, buffer headroom, and battery impact before enabling 24 kHz.

**Biggest unknown:** The owner has not supplied the first real authenticated origins or which categories may be spoken/persisted; any automation must therefore ship with empty, explicit configuration rather than guessed sites or sensitivity rules.

