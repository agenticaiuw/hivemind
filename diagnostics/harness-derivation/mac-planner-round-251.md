# Harness derivation — mac-planner — round 251

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Before my next calendar meeting, prepare a tiny cockpit: open the relevant document or authenticated browser tab if one is confidently associated, show me the last related note or mail, and tell me through the pendant the meeting title plus one unresolved item. If confidence is low, do nothing except tell me what is missing."
- **useful because:** It removes the five-minute scramble before meetings while avoiding the dangerous behavior of guessing which document to open. The wearable supplies the timely prompt; the Mac and browser supply the private working context.
- **path:** relay → pendant → mac-planner → browser-extension → dashboard
- **model tier:** Cheap background planner for retrieval/ranking; realtime model only for the short spoken sentence.
- **latency:** Prepare 2–5 minutes before start, with a visible Mac result within 5 seconds and a spoken brief under 15 seconds.
- **cost:** Roughly $0.02–$0.08 per meeting, mostly ranking and one short synthesis; browser and Calendar reads are local.
- **security:** Reading authenticated tabs and opening files is sensitive. Default to titles/metadata, never page bodies; opening or editing requires an owner-configured policy entry. Do not send mail or create external changes automatically.
- **missing:** Calendar-triggered routine trigger with a lead-time field; A confidence-scored association between event attendees/title and local files/browser tabs; A policy-aware open recommendation that can stop cleanly when confidence is low

### "Run a pendant bench check from my Mac when I say “locked diag”: exercise both audio directions over the USB-connected hardware, collect the UART counters, save a dated report in ~/AI-Pendant-Workspace, and give me a one-sentence verdict plus the exact failing metric."
- **useful because:** The pendant and ESP32 bridge are physically attached today even though LTE registration is not. This makes the already-accepted diagnostic fixture useful now and catches the exact audio regressions that previously shipped unnoticed.
- **path:** pendant → mac-planner → relay → dashboard
- **model tier:** Deterministic local test runner and cheap parser; no realtime model is needed except optional spoken delivery.
- **latency:** Start within 3 seconds of the command; finish in 1–3 minutes; verdict immediately after the UART report is complete.
- **cost:** Near-zero API cost; local USB test execution and report parsing dominate.
- **security:** USB commands must be restricted to the signed diagnostic fixture, never arbitrary firmware flashing or serial writes. Reports may contain paths and device counters; redact them before cloud upload and keep the full report local.
- **missing:** A bounded Mac action that invokes the fixture on /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; A stable UART report parser with pass/fail thresholds from scripts/audio-quality-probe.mjs; A job receipt linking the spoken verdict to the saved report

### "When I ask through the pendant “what am I looking at?”, identify the foreground Mac app and active browser page by title and URL, read only the visible page heading or selected text when I explicitly ask, and answer in one sentence. If the browser is not the foreground app, say so instead of guessing."
- **useful because:** The wearable can hear me anywhere, but currently cannot explain the private screen in front of me. This is a small, high-frequency bridge between voice and the Mac's authenticated browser session without sending page content to the relay by default.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** Deterministic extraction for app/title/URL; cheap model only to compress a retrieved heading or selected text into one sentence.
- **latency:** Under 3 seconds for app and page identity; under 8 seconds when reading visible text.
- **cost:** Near-zero for metadata; about $0.005–$0.02 only when summarizing text.
- **security:** URL, title and selected text are private. Keep raw values on the Mac, send only the minimal answer, redact query strings/password-like fields, and require an explicit second utterance before reading page text. Never expose cookies or DOM contents wholesale.
- **missing:** A real semantic Mac context read for foreground window/document identity and selected text (the existing inspect operation does not reliably provide these fields); A browser bridge response that returns title, URL, visible heading and selection with redaction; A voice intent classifier distinguishing identity requests from explicit read-text requests

### "After you change anything on my Mac or in the browser, let me ask the pendant “what changed?” and get a concise before/after account: the exact files, tabs, or settings touched, what succeeded, and how to undo it. For actions without a safe undo, say that plainly."
- **useful because:** Today a successful action receipt does not give the owner a trustworthy human explanation across Mac and browser surfaces. This makes automation legible after the fact, especially when the owner was not watching the screen.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic action ledger and resource diff first; cheap model only to compress the result into one sentence.
- **latency:** Answer in under 5 seconds for recent actions; under 15 seconds for a multi-step job.
- **cost:** Near-zero for ledger queries and diffs; roughly $0.005–$0.02 for synthesis when many actions are involved.
- **security:** Receipts may contain private paths, URLs, and text. Keep full details on the Mac, redact secrets and query strings, and expose only the requesting owner’s own job history. Never claim reversibility unless an actual inverse is available.
- **missing:** A cross-surface append-only action ledger with stable resource identifiers; Before/after snapshots for browser and Mac mutations; An inverse-action registry that distinguishes genuinely reversible work from merely documented work; A voice query route that joins Mac, browser, and relay receipts

### "When I ask “where did that come from?”, open the exact source on my Mac and highlight the cited passage or browser result that supports the last spoken answer. If the source is no longer available or the answer was inferred, tell me that instead of opening a vaguely related page."
- **useful because:** A spoken answer is hard to audit while walking. Exact source return turns the pendant from a one-way answer device into a bridge back to evidence in the owner’s private browser and workspace.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** Cheap citation resolver and deterministic URL/highlight action; realtime model only for the initial answer if needed.
- **latency:** Resolve the source in under 3 seconds and open/highlight it within 8 seconds.
- **cost:** About $0.005–$0.03 per request; most work is local lookup and browser navigation.
- **security:** Do not send page bodies or authenticated content to the relay merely to cite them. Store citation hashes and local source handles; redact tokens and query parameters. Opening a source is read-only, but highlighting selected private text must remain local.
- **missing:** Citation provenance attached to every spoken answer and research result; A local browser action that navigates to a source and highlights a stable passage; A fallback representation for transient or inferred sources; A relay intent for source-return requests

### "Let me ask the pendant “what did you do today?” and receive a short, accurate accounting of actions taken across the Mac, browser, relay routines, and pendant—not a summary of conversations. Include completed, failed, and still-running work, with a way to open the detailed receipt on the Mac."
- **useful because:** The owner currently has to remember which surface performed an action and inspect separate job records. A single daily action account would make the hive understandable and expose silent failures before they become surprises.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic aggregation, status normalization, and deduplication; cheap model for the final spoken compression.
- **latency:** Under 5 seconds for a day’s ledger; detailed receipt opens within 8 seconds.
- **cost:** Near-zero for aggregation; roughly $0.005–$0.02 for summarization.
- **security:** This is a sensitive activity history. Default to categories and app names, redact contents, URLs, mail subjects, and file paths unless explicitly requested, and retain the owner’s existing destructive-action confirmation policy.
- **missing:** A common event envelope and clock across pendant, relay, Mac, and browser; Cross-surface deduplication of retries and handoffs; A daily ledger query and retention/redaction policy; A dashboard deep link from spoken entries to full receipts


## What it asked for

_Nothing._
