# Harness derivation — faculty-judgement — round 221

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Make my morning brief happen once, at the right time, and tell me when it could not honestly read something."
- **useful because:** The live state has two daily morning briefs at 07:00 and another at 07:30, while remembered timezone evidence disagrees with the Mac's authoritative routine zone. Today this can double-speak, and calendar/Reminders empty results can mean either 'clear' or 'not readable'. This capability gives one owner-visible decision instead of silent duplicate or fabricated all-clear output.
- **path:** relay → mac → browser → pendant
- **model tier:** background for schedule reconciliation and brief composition; realtime only for the one-sentence spoken exception or owner choice
- **latency:** Under 2 seconds to detect and coalesce schedules; 10-30 seconds for the actual brief; never speak until source readability and delivery state are explicit
- **cost:** About $0.01-$0.05 per brief depending on mail/browser reading; dedupe and permission checks are deterministic and nearly free
- **security:** Read-only by default. Calendar, mail, and browser content remain on the Mac/browser until the existing redaction and delivery policy permits speech. Changing or deleting a routine requires explicit owner confirmation. Every 'unknown' source must be labeled unknown, never converted to clear.
- **missing:** A semantic routine-deduplication and repair operation that can preview the two existing 07:00/07:30 jobs, preserve the owner's chosen one, and disable the other only after confirmation; A truthful EventKit readability result wired into the briefing path (not merely the Automation TCC report); An owner choice for whether 07:00 or 07:30 wins, and whether America/New_York or the owner's separately remembered America/Chicago should govern routines

### "Tell me which thing I keep asking for but never actually got, and offer the safest next step."
- **useful because:** The owner has repeated the same news-brief request many times and has also repeatedly asked for phone-harness probes that failed. A person should not have to remember whether an assistant silently dropped a request. This is a repair surface: it distinguishes a completed result, a failed attempt, an unavailable capability, and a request that was never executed, then offers one concrete read-only retry or a reviewable draft rather than pretending success.
- **path:** relay → mac → browser → pendant
- **model tier:** cheap background classifier over receipts and request text; realtime model only when converting the finding into a short spoken explanation
- **latency:** Runs after a job/request completes or once daily; under 3 seconds for a bounded 30-day scan; spoken answer under 1 second from cached findings
- **cost:** Usually under $0.01 per scan; the dominant cost is optional web/browser retry, not classification
- **security:** Do not infer a promise merely from a repeated phrase; require request evidence plus a missing/failed receipt. Never retry mutating actions automatically. Browser and mail contents stay on their source surface. Any repair that sends, deletes, buys, or changes a routine is a prepared action requiring owner confirmation. Retain only request fingerprint, outcome class, and source receipt IDs, with short TTL.
- **missing:** A durable join from spoken/request intent to relay job, Mac job, browser command, and receipt IDs; current IDs meet only in unindexed telemetry; A bounded outcome taxonomy and owner-facing 'retry / draft / stop' action, with deterministic policy evaluation before retry; A small scheduled scanner or post-request hook; current job records do not recover orphaned processing jobs

### "Give me a three-sentence news delta: only what changed since my last brief, with a source I can ask you to read."
- **useful because:** The owner's repeated request is not just for headlines; it is for a compact, trustworthy answer that does not replay yesterday's story. A delta brief saves attention, makes freshness visible, and lets the owner expand one item without losing the spoken queue. It can continue to work when the pendant is offline by leaving a cited, playable item for later.
- **path:** relay → mac → browser → pendant
- **model tier:** background model for clustering and summarization; deterministic timestamp/source checks first; realtime model only for follow-up questions about one cited item
- **latency:** Fetch and compare within 30 seconds of a scheduled run; three-sentence spoken result under 8 seconds; follow-up source read under 5 seconds if browser is online
- **cost:** Roughly $0.02-$0.08 per run, dominated by fetching and summarizing 8-15 source pages; unchanged-source clustering is cheap
- **security:** Use public-source allowlists and retain URLs, publisher, publication time, and a short redacted digest rather than full article bodies. Never imply a source was read if browser connectivity or publication time is unknown. Do not read logged-in pages for news unless explicitly requested. Speech contains headlines only; sensitive page text stays in the browser.
- **missing:** A durable digest fingerprint store with source URL, publisher, publication time, observed time, and prior-brief membership; A source freshness and correction check that can mark an item stale, updated, or conflicting instead of treating search rank as truth; An item-level link from the digest to the existing spoken brief playback and provenance explanation, including a safe 'read this source' follow-up

### "Before I put it on, tell me whether the pendant is actually ready today: audio, link, queued work, and privacy state."
- **useful because:** The pendant is physically testable over USB today but is not LTE-registered, and several failures would otherwise look like a normal quiet device. A two-minute preflight gives the owner a truthful go/no-go: codec acceptance numbers, UART anomalies, stale queued audio, privacy latch state, and whether the shipping relay path is reachable. It prevents wearing a device that records but cannot deliver, or speaks with an unverified queue.
- **path:** mac → relay → pendant
- **model tier:** deterministic diagnostics and policy checks; no expensive model unless converting failures into a concise explanation
- **latency:** Bench preflight under 30 seconds; spoken verdict under 3 seconds; never block normal conversation on a background health run
- **cost:** Negligible API cost; one local diagnostic pass and a small relay status read. Optional draft generation costs under $0.01
- **security:** UART logs may contain identifiers or speech-adjacent metadata; keep raw logs local and send only metrics, hashes, and reviewed bug drafts. Never upload microphone PCM. A failed privacy-latch or stale auth state is a hard no-go. Filing an issue remains a draft until owner approval.
- **missing:** A single typed preflight that combines Mac USB serial discovery, the measured audio acceptance criteria, privacy-latch state, outbox/inbox counts, and LTE registration status; A device-side signed health snapshot so the Mac can distinguish current metrics from stale UART output; A clear wearable-vs-bench verdict: USB diagnostics are valid for development but must not be presented as proof that the LTE-M shipping path works

### "Before I commit to something consequential, show me the likely second-order effects on the rest of my day and give me a reversible way to proceed."
- **useful because:** Today the system can check whether an action is permitted and can preview some immediate changes, but it cannot reason across the owner's calendar, existing obligations, browser state, and pending work to expose what the choice will crowd out. The owner should be able to make an informed choice before accepting a meeting, booking travel, committing money, or sending a consequential message.
- **path:** relay → mac → browser → pendant
- **model tier:** background model for consequence analysis over a bounded evidence bundle; realtime only to explain the top tradeoff aloud
- **latency:** Read-only consequence preview in 5-15 seconds; no external mutation until the owner explicitly confirms
- **cost:** $0.03-$0.15 per preview, dominated by gathering and summarizing cross-surface evidence
- **security:** Default to metadata and redacted excerpts. Never infer financial, medical, or relationship consequences as facts; label them as possibilities with evidence. Sending, purchasing, deleting, or accepting remains confirmation-gated. The owner must be able to discard the analysis and its retained evidence.
- **missing:** A typed consequence graph linking a proposed action to calendar load, obligations, pending jobs, and downstream external effects; A durable but expiring preview artifact that can be revalidated immediately before confirmation; A presentation that distinguishes observed consequences from model-predicted possibilities

### "At the end of the week, tell me where my attention actually went, what I intended to do instead, and one change worth trying next week."
- **useful because:** The system currently records jobs, browser activity, focus sessions, and briefings as separate operational traces, but the owner cannot see a humane account of how their attention was spent. A retrospective turns those traces into agency: it distinguishes observed activity from interpretation and offers one experiment rather than an overwhelming productivity score.
- **path:** relay → mac → browser → pendant
- **model tier:** background model over locally aggregated activity; no realtime model needed unless the owner asks a follow-up
- **latency:** Generate on demand in under 30 seconds; the pendant receives a short optional digest, with detail available on the Mac
- **cost:** $0.02-$0.10 per weekly retrospective; aggregation and bucketing are deterministic
- **security:** Keep raw URLs, message contents, and window titles local. Share only categories, durations, and explicitly selected evidence. Never present inferred attention as psychological truth, and never rank the owner's worth or productivity. Retention must be opt-in and bounded.
- **missing:** A local activity ledger that joins foreground-app intervals, browser sessions, jobs, focus sessions, and spoken interruptions without retaining raw content; An explicit distinction between observed activity, owner-stated intention, and model interpretation; A retention and export control for weekly aggregates, including deletion of the underlying raw intervals

### "Keep my work and personal worlds separate, and warn me before an answer, reminder, or action crosses that boundary."
- **useful because:** The current system has one owner, one memory projection, one browser context, and one spoken channel. A work email, personal reminder, and private note can therefore influence the same answer without an explicit boundary. The owner should be able to enter a named context and have retrieval, speech, routines, and external actions obey it across every body.
- **path:** pendant → relay → mac → browser
- **model tier:** deterministic context firewall and routing policy; background model only classifies ambiguous new material
- **latency:** Context selection and enforcement under 100 ms; ambiguity should produce one short question rather than a silent guess
- **cost:** Negligible per action; occasional classification under $0.01
- **security:** Fail closed on ambiguous context. Never copy content between contexts merely because it is useful. Context labels must not be treated as sensitivity labels; a private work document can still require stronger handling. The owner needs explicit export, merge, and deletion controls.
- **missing:** A durable context namespace attached to memory facts, browser sessions, jobs, routines, audio items, and action receipts; Cross-surface enforcement at retrieval, prompt projection, speech, and mutation—not only a UI mode; A signed context transition event from the pendant or dashboard, with an emergency neutral mode when the owner is unsure


## Changes it proposed to its own stack

### `firmware` — Add a compact signed health snapshot command over the existing development serial protocol and LTE control path. It reports firmware build hash, monotonic snapshot time, radio registration state, privacy-latch epoch, outbox/inbox counts, last audio acceptance metrics, and a snapshot nonce; it never includes PCM or raw UART text. The Mac preflight verifies freshness and signature, while relay status labels USB-bench readiness separately from shipping-path readiness.
- **owner gets:** The owner gets a truthful 'wear / do not wear' answer instead of confusing a healthy USB bench with a working cellular pendant. A stale or privacy-unsafe device is rejected before it can capture or play anything.
- effort: Medium: firmware command and signing key plumbing, Mac parser and verifier, relay status adapter, and a small preflight report. Reuse existing diagnostics and delivery ACK structures.  ·  risk: A bad clock or lost key could produce false no-go. Fail closed, show which field is stale, and allow local bench diagnostics without claiming LTE readiness. Keep signing keys out of UART logs.
- cost: No meaningful API cost; approximately 1-3 KB firmware code and a small response payload. No new hardware.  ·  latency: Adds under 1 second to a manual preflight; no impact on conversational audio path.
- security: Improves integrity and privacy by making latch and delivery state authenticated; exposes only metadata and hashes, not content.
- depends on: An existing device identity/signing-key provisioning decision; The accepted audio_delivery_ack_queue and offline_privacy_panic_wipe firmware work; A Mac-side serial discovery/parser for the two currently connected chips


## What it asked for

_Nothing._
