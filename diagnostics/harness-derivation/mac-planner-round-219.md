# Harness derivation — mac-planner — round 219

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-watch-capability** — GET /watches is live and persists scheduled field watches in ~/AI-Pendant-Workspace/.pendant-page-watches.json, but current watches are only public test pages (time.is and Selenium); no authenticated work-page watch is enrolled.
  - evidence: GET /watches returned two disabled public watches and no work-domain watch.

## Capabilities it proposed

### "When I press the pendant's bookmark button during a meeting, make a private, timestamped follow-up note that links the calendar event and the exact browser or Mac document I was looking at, then put one short reminder in my inbox after the meeting."
- **useful because:** A physical bookmark is instant and speech-free, but today it does not become an actionable memory. This closes the loop across the worn device, relay, Mac context, and browser without recording a conversation.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background for correlation and note drafting; realtime only for the owner's optional spoken confirmation
- **latency:** Acknowledge the button locally immediately; correlate and write the note within 30 seconds; reminder delivery after the calendar event ends.
- **cost:** About $0.01–$0.05 per bookmark, dominated by one context-correlation and short drafting call; no audio transcription required.
- **security:** Calendar title, active URL, and document metadata leave the Mac. Redact page content by default and never capture passwords or form fields. Creating the reminder is pre-authorized by the owner's stated policy; sending mail is not involved.
- **missing:** A Mac context snapshot that returns semantic document/window identity and selected text, beyond the existing foreground/browser-tab observations; A relay correlation record joining offline_moment_bookmark timestamps to calendar intervals and post-event reminders; A browser inspection payload with stable page title and redacted active-document metadata

### "Run the pendant audio diagnostic fixture every night while it is plugged into my Mac, compare the measured counters with the last known-good run, and tell me through the pendant only if the audio path regressed."
- **useful because:** The hardware is physically attached today, and audio failures have repeatedly been caused by measurable framing, CPU, and packet issues. A nightly hardware-in-the-loop check catches a broken firmware build before the owner depends on it, without waking them for healthy runs.
- **path:** pendant → mac-bridge → relay → dashboard
- **model tier:** No realtime model for collection; a cheap background model only summarizes anomalous counters and drafts the spoken alert.
- **latency:** Start at a configured overnight time; fixture completion and comparison within 2 minutes; alert within 1 minute of a confirmed regression.
- **cost:** Negligible model cost on healthy runs; roughly $0.01 for an anomalous-run summary. Dominant cost is Mac USB execution and storage, not inference.
- **security:** The fixture is synthetic and must never access microphone content. Store only counters, firmware/build identity, and hashes in the workspace. The pendant alert is local; no external notification is sent by default.
- **missing:** A bounded, bidirectional USB serial bench runner that can arm audio_path_diagnostic_fixture and collect its framed result reliably (the current shell route has weak receipts); A durable baseline/comparison record keyed by firmware and hardware revision; A schedule trigger that runs only when home-macbook-bridge is online and the pendant is attached

### "Every weekday morning, check the authenticated work pages already open in my browser, Calendar, and unread Mail, and tell me one short sentence containing only items that need action today; leave the detailed evidence in my workspace."
- **useful because:** The owner repeatedly asks for inspection of authenticated pages, but a generic calendar/mail brief cannot see browser-only work. This is the highest-value daily use of the whole hive: the browser supplies private sessions, the Mac supplies local sources, the relay ranks and speaks, and the pendant delivers the result while the owner is away from the screen.
- **path:** browser → mac-bridge → relay → pendant → dashboard
- **model tier:** Background model for extraction, deduplication, and priority ranking; realtime only if the owner asks a follow-up from the pendant.
- **latency:** Run before the existing 07:00 brief, finish in under 90 seconds, and deliver one spoken sentence by 07:05. Detailed evidence can arrive asynchronously.
- **cost:** About $0.03–$0.12 per weekday run depending on the number of inspected pages; browser extraction and ranking dominate, not audio generation.
- **security:** Read only the browser tabs and domains the owner explicitly enrolls; redact tokens, passwords, and page bodies by default. Never click, submit, send mail, or mutate a work system. Workspace evidence should retain source URLs and timestamps but redact sensitive snippets. Require an explicit enrollment and an emergency pause.
- **missing:** A browser-harness watch that can inspect enrolled authenticated tabs on a schedule, rather than only an on-demand URL inspection; A policy/configuration surface for enrolled domains, extraction fields, and redaction; A cross-source priority/deduplication job that joins browser findings with Calendar/Mail and emits a durable citation bundle; A weekday scheduler hook that can target the browser bridge and deliver a queued spoken result to the existing pendant inbox

### "When an enrolled authenticated web page changes while I am away, give me a two-sentence spoken before/after summary on the pendant and save a redacted evidence diff in my workspace; if the change is only cosmetic, stay silent."
- **useful because:** The existing watch mechanism can detect fields, but the owner cannot currently receive a useful, privacy-preserving explanation of a meaningful change away from the screen. This turns a passive browser watch into an actionable wearable signal without granting the system permission to click or submit.
- **path:** browser → relay → pendant → mac-bridge → dashboard
- **model tier:** Cheap background extraction and change classification; realtime is unnecessary unless the owner asks for the evidence on demand.
- **latency:** Detect on the configured watch interval, classify within 30 seconds, and queue the spoken alert on the next available pendant connection. Evidence can be written asynchronously.
- **cost:** About $0.01–$0.05 per meaningful change; unchanged/cosmetic checks should use deterministic field comparison and cost almost nothing.
- **security:** Only owner-enrolled domains and fields may be watched. Store structured before/after values with aggressive redaction, never passwords or full page bodies. No browser mutations. Require an explicit per-watch delivery policy and provide a local pause.
- **missing:** A watch-to-pendant delivery adapter that uses the existing durable alert inbox and preserves ordering across a disconnected pendant; A semantic diff classifier that distinguishes cosmetic layout/time changes from actionable field changes; A redacted evidence-diff artifact format with retention and deletion controls


## Changes it proposed to its own stack

### `integration` — Add a one-shot, signed USB bench command path dedicated to audio_path_diagnostic_fixture: the Mac sends a nonce-bound arm request, the pendant returns framed sequence-numbered counters and a completion marker, and the Mac writes an atomic JSON receipt containing firmware hash, timestamps, packet counts, encode/decode timings, underruns, and pass/fail thresholds. This is not a general serial session and cannot carry owner microphone audio.
- **owner gets:** They can know before wearing the pendant that the actual audio path works, and a bad firmware build can explain itself instead of producing a mysterious silent or distorted conversation.
- effort: Medium: firmware command parser and framing, Mac bench runner, signed fixture authorization, baseline comparator, and a small workspace receipt format.  ·  risk: A malformed bench command must be rejected without starting capture; stale or replayed nonces must not arm the fixture. Recovery is a reset and a new nonce. Keep the fixture synthetic and bounded by a hard timeout.
- cost: No model cost for normal runs; small workspace storage per receipt. No new hardware. USB bench execution consumes Mac time only while attached.  ·  latency: Arming is sub-second; a complete fixture run should finish in under two minutes. No impact on live calls because this is a deliberate bench-only mode.
- security: The signed nonce prevents an arbitrary local process from enabling a capture path; the fixture itself never records microphone content. Receipts should redact serial identifiers unless explicitly requested.
- depends on: audio_path_diagnostic_fixture firmware skill; A dedicated bounded USB diagnostic runner rather than the unavailable general serial-session capability; A baseline store for per-firmware pass/fail comparisons


## What it asked for

_Nothing._
## Its own summary

This round produced three owner-facing capabilities. (1) A pendant bookmark-to-follow-up workflow that correlates the existing offline bookmark with Calendar, browser, and Mac context and creates a post-meeting reminder; it was recorded as connective work and flagged close to an existing evidence-view idea, so it should not be implemented twice. (2) A nightly USB-attached, hardware-in-the-loop audio regression run using the accepted diagnostic fixture, with baseline comparison and pendant-only alerts on regression. (3) The highest-value capability: a weekday morning brief that reads explicitly enrolled authenticated browser pages plus Calendar and unread Mail, ranks only action-needed items, speaks one sentence, and leaves cited evidence in the workspace. GET /watches is live, but only public test watches are enrolled today.

**Biggest unknown:** The missing product decisions are concrete: which authenticated browser domains/pages the owner will enroll; what fields may be extracted and retained; and the bounded USB bench runner that can arm the fixture and return trustworthy framed results. I did not request another tool or permission because the existing browser watch store and Mac execution primitives are present, while serial remains intentionally absent and must be implemented as a diagnostic bench procedure rather than a general serial session.

