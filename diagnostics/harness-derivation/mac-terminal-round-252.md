# Harness derivation — mac-terminal — round 252

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Make the pendant voice sound natural end to end: stream 24 kHz superwideband replies, and tell me plainly when the path is not actually delivering that quality."
- **useful because:** This is the core reason to wear the device. Today the pendant decodes 24 kHz frames but the ESP32 bridge is hard-locked to SBC 44.1 kHz and the uplink is 16 kHz; the owner needs one truthful quality path rather than a nominal codec setting. A single spoken quality check should distinguish real 24 kHz playback from resampling, starvation, or fallback.
- **path:** pendant → relay → mac-bridge → dashboard → Mac
- **model tier:** Realtime only for the conversational turn; a cheap background watchdog computes packet loss, decode CPU, resampler underruns, and negotiated A2DP mode. No LLM is needed for telemetry.
- **latency:** First audio packet under 250 ms; 60 ms frame cadence; quality verdict under 2 seconds after a 10-second probe.
- **cost:** Negligible model cost for normal calls; roughly one short realtime turn for an explicit probe. Engineering dominates: Opus/transport negotiation, ESP32 buffering, and a product bridge or codec that supports a true 24 kHz path.
- **security:** Audio remains on the existing authenticated relay and local bridge. Store only aggregate counters and negotiated format, never the probe audio. Require no confirmation because it is diagnostic and non-destructive.
- **missing:** A bridge/audio path that can preserve 24 kHz instead of the current SBC-only 44.1 kHz A2DP source; A compact cross-device audio health frame carrying negotiated rates, underruns, decode time, and turn ID; Relay transcoding and fallback policy that labels every downgrade instead of silently resampling; An automated Mac bench harness that exercises both USB-connected chips and emits a pass/fail artifact

### "If a Mac task failed or was interrupted, say “resume that” and have the pendant continue only the safe unfinished steps, then tell me exactly what it did."
- **useful because:** Today a restart leaves jobs stuck as processing, cancellation cannot stop a running shell, retries do not exist, and the ledger is not joined to the job ID. The owner should not have to inspect JSON or reconstruct a half-completed task; the wearable should turn an uncertain Mac state into a safe, comprehensible continuation.
- **path:** pendant → relay → Mac → dashboard
- **model tier:** Use a cheap background/state-machine model to reconcile receipts and ledger steps; use realtime only to resolve an ambiguous reference such as “that.” Do not spend the realtime tier planning every retry.
- **latency:** Acknowledge the request in under 500 ms; reconstruct state in under 3 seconds; resume steps sequentially and speak a one-sentence result after each completed batch.
- **cost:** Near-zero per resume when receipts are structured; occasional small realtime turn for ambiguity. Engineering cost is in durable process supervision and idempotency, not inference.
- **security:** Never replay a step whose receipt is unknown or whose effect is non-idempotent; report it as needing the owner. Preserve the owner's maximum-access policy, but expose command, cwd, exit code, and whether the step was actually executed. Do not persist inherited secrets; store a redacted environment digest.
- **missing:** Boot-time reconciliation of processing jobs and orphaned child processes; A real job-to-ledger join and guaranteed ledger close on every terminal path; Shell process-group IDs and exit codes, with cancellation wired to the child signal; A typed resume planner that classifies each unfinished action as safe-to-retry, inspect-only, or manual; A pendant intent packet for resume/cancel that survives a dropped link and rejects duplicate job IDs

### "Read me the four newest items in my Safari Reading List, with the title and one-sentence reason each might matter."
- **useful because:** The owner has asked this repeatedly and it currently fails. A wearable is ideal for triaging saved reading without opening a screen: the Mac has the authenticated Safari data, the relay can rank and summarize it, and the pendant can speak a short digest while the owner is moving.
- **path:** pendant → Mac → browser → relay → dashboard
- **model tier:** Use a cheap background extractor for title/URL/date and deduplication; use realtime only to speak the final short digest or answer a follow-up about one item. Do not send full page text to the expensive model unless requested.
- **latency:** Return the four titles in under 5 seconds; stream the spoken list as each item is summarized. If Safari is locked or unavailable, say so within 1 second rather than reporting an empty list.
- **cost:** Low: metadata-only extraction and four short summaries, with model spend proportional to requested summaries. The Mac/browser integration is the main work.
- **security:** Reading List metadata and URLs are private browser data; keep them on the Mac until the relay has an authenticated, expiring request. Do not fetch page contents automatically; require a follow-up for full text. Record source URL with each spoken claim.
- **missing:** A Mac action to enumerate Safari Reading List entries with title, URL, and saved date; A browser/relay request type for metadata-only reading-list retrieval, separate from ordinary tab snapshots; A bounded summarizer that returns four citations and handles paywalled or unavailable pages honestly; Offline caching of the last successful list and its age on the pendant, without caching page text

### "While I am talking to the pendant or in a meeting, let only genuinely urgent things interrupt me; queue everything else and give me a spoken, ranked catch-up when I become available."
- **useful because:** Today each surface can produce alerts, but none of them shares a live attention state. The owner gets either interruption noise or misses something important. A wearable, Mac, browser session, and always-awake relay together can make interruption a deliberate decision: know what the owner is doing, classify urgency, suppress low-value notifications, and restore them with their source and age.
- **path:** pendant → relay → Mac → browser → dashboard
- **model tier:** A cheap background classifier handles ordinary notification ranking and deduplication; realtime is reserved for ambiguous or high-consequence messages and for the short spoken catch-up. The pendant should enforce the current attention mode locally when the link is down.
- **latency:** Urgent interruption decision under 1 second; suppression immediate; catch-up available within 3 seconds after the conversation or meeting ends. Never delay the live voice path for ranking.
- **cost:** Low ongoing cost if ranking uses structured metadata and rules, with a small model call only for borderline items. Engineering dominates: shared attention leases, notification ingestion, and reliable restoration.
- **security:** Mail, browser alerts, meeting titles, and notification text are sensitive. Keep raw content on the Mac/browser where possible, send the relay only a short urgency capsule, expire capsules quickly, and never auto-send replies or dismiss alerts. The owner must be able to override with a physical button or spoken “interrupt me.”
- **missing:** A shared attention lease emitted by the pendant and Mac with start, end, source, and confidence; Mac notification ingestion and reversible audio/visual suppression with exact restoration receipts; Browser hooks for authenticated-site alerts and source URLs, not just the active tab; Relay-side urgency arbitration that deduplicates the same event across Mac, browser, mail, and calendar; A pendant-local queue mode that preserves urgent metadata offline and announces only the highest-priority item; A dashboard showing what was suppressed, why, and whether it was later delivered

### "Move this task to my iPhone and leave it exactly where I stopped on the Mac, then tell me when the handoff is complete."
- **useful because:** The owner should not have to repeat a search, copy a URL, or explain which form field was in progress when leaving the desk. The pendant supplies an unambiguous handoff intent, the Mac knows the active app and browser session, and the iPhone-mirroring surface can open the same authenticated destination and verify that it is ready.
- **path:** pendant → Mac → browser → iOS → relay
- **model tier:** Use a deterministic handoff planner for URL, app, tab, selection, and typed-but-unsent state; use realtime only to resolve “this” when more than one task is active. No model should transmit passwords or replay an irreversible submit.
- **latency:** Acknowledge in 300 ms and complete ordinary URL/app handoffs in under 5 seconds. If verification fails, report the exact stopping point rather than claiming success.
- **cost:** Low per use; mostly local Mac/iOS actions and a small state capsule. Engineering cost is session-state extraction and post-handoff verification.
- **security:** Never copy credentials, cookies, or unsent sensitive form contents into the relay. Keep state on the Mac and pass only an expiring handoff token to the iPhone surface. Require confirmation before replaying any submit, purchase, send, or delete action.
- **missing:** A cross-surface handoff record with source window, destination target, cursor/selection, and owner intent; Mac active-app/browser state extraction that can distinguish safe location from sensitive unsent input; iOS Mirroring actions to open and verify the destination without leaking credentials; Relay correlation and expiry so a late duplicate handoff cannot reopen or submit the task; A pendant completion/failure report that names the destination and age

### "When you say something is done, give me a short spoken proof of what changed and where it was verified; if you cannot prove it, say it is unverified."
- **useful because:** A completion sentence is not enough for a wearable assistant controlling several surfaces. The Mac may have executed an action, the browser may have shown a stale page, and the relay may have lost the reply. A compact proof chain would let the owner trust results without opening a dashboard, especially for reminders, browser updates, and file operations.
- **path:** pendant → relay → Mac → browser → dashboard
- **model tier:** Use deterministic receipts and state comparisons first. A cheap model can compress several receipts into one sentence; realtime is only for the owner's follow-up question. Never let a language model upgrade missing evidence into success.
- **latency:** Speak an initial dispatched/verified/unverified state within 500 ms, then stream final verification within 3 seconds of the action. Evidence must remain queryable after the spoken response.
- **cost:** Very low model cost because the input is structured receipt metadata; engineering cost is adding before/after probes and cross-surface correlation.
- **security:** Proof capsules should contain hashes, app/site names, timestamps, and minimal excerpts—not secrets or full page content. For destructive actions, expose the evidence and preserve the owner's existing confirmation policy. A failed verification must not retry a mutation automatically.
- **missing:** A common proof-capsule schema linking relay request, Mac job, browser provenance, and pendant turn ID; Before/after state probes for files, reminders, browser records, and app settings; A verifier that distinguishes executed, observed-after, stale, and unverifiable outcomes; Spoken compression rules that name the evidence source and age in one sentence; Durable retention and redaction controls for proof records


## What it asked for

_Nothing._
## Its own summary

This round produced three distinct owner-facing capabilities. The highest-value one is a truthful end-to-end 24 kHz audio path: the current pendant decodes 24 kHz, but the bridge is SBC-only 44.1 kHz and the uplink is 16 kHz, so quality must be negotiated, measured, and reported rather than claimed. I also proposed spoken “resume that” recovery for interrupted Mac work, and a Safari Reading List digest (a repeated owner request that currently fails). I verified that the newly granted mac_usb_serial_diagnostics schema still has no live implementation, so it cannot yet inspect the two physically connected chips.

**Biggest unknown:** Whether the audio hardware can be changed to preserve a true 24 kHz playback path, and how Safari Reading List data can be enumerated through the Mac/browser harness. I still need a real bounded serial diagnostic implementation, a Reading List metadata route, and an audio telemetry/negotiation frame; without those, bench results and spoken quality claims remain ungrounded.

