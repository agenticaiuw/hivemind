# Harness derivation — faculty-judgement — round 270

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Make my morning brief happen once: combine overlapping daily brief routines, tell me exactly which sources were readable, and make it available on the pendant until I actually hear it."
- **useful because:** The owner currently has two separate 07:00 routines that both request a morning brief, plus a 07:30 battery routine and a separate research brief. This would stop duplicate interruptions and stop treating a generated job as delivered: the answer is not complete until the pendant reports playback. If Calendar/EventKit is unreadable, it says so instead of claiming a clear day.
- **path:** relay → mac → pendant → dashboard
- **model tier:** background model for source gathering and semantic routine coalescing; realtime model only for a one-sentence spoken status if the owner asks
- **latency:** Generate by the scheduled window; source reads may take up to 30 seconds. Playback remains queued without interrupting. Dashboard delivery state should update within one relay round-trip.
- **cost:** Roughly $0.01–$0.05 per daily run depending on mail/research volume; model summarization dominates, while dedupe and delivery reconciliation are deterministic.
- **security:** Never claim a source was read from an empty unauthorised EventKit result. Speak only the redacted briefing; keep mail/calendar detail on the Mac unless the owner's policy permits it. Coalescing must preserve each routine's provenance and allow the owner to inspect or disable one. No external mutation without confirmation.
- **missing:** A semantic routine-coalescer that groups equivalent commands before execution; A durable routine-to-brief artifact mapping and one idempotency key across relay/Mac/pipeline; A scheduler hook that waits for record_pendant_delivery_event playback_finished (or explicitly marks queued/unheard) before considering delivery complete; A writer from the Mac bridge into fleet memory or another durable shared delivery projection; Relay job leases/requeue so a crashed coalescer cannot leave a brief permanently processing

### "When I ask 'what changed?', give me only new or materially changed things since my last heard brief, with a link back to the evidence and a reason something was included."
- **useful because:** Repeated briefings waste attention and make it impossible to tell whether a new alert is genuinely new. A source-linked delta brief would remember the last delivered evidence cursor per source, suppress unchanged mail/page/calendar items, and surface conflicts or newly unreadable sources instead of replaying stale prose.
- **path:** relay → mac → browser → pendant → dashboard
- **model tier:** Cheap background model for clustering and wording; deterministic hashing, timestamps, source cursors, and novelty checks should do most of the work. Realtime is used only if the owner interrupts with a follow-up.
- **latency:** A pull request should return a short delta in 5 seconds when cached; a scheduled run can gather for up to 30 seconds. The pendant should receive a compact queued item and not interrupt unless attention_arbitrate says so.
- **cost:** About $0.005–$0.03 per delta, dominated by summarizing genuinely changed content; unchanged sources should cost no model call.
- **security:** Store hashes and source IDs by default, not raw mail/page text. Redact before speech. Evidence links must honor revocation and expiry; if a source was revoked, say 'evidence unavailable' rather than reconstructing it from a derived fact. Browser credentials and full page bodies never enter the pendant payload.
- **missing:** A durable per-source delivery cursor tied to the actual playback_finished ACK, not merely generation time; A common change-set normalizer for mail, calendar, reminders, page watches, and research briefings; A revocation-aware delta store that links every summary claim to evidence capsules or source refs; A read path for the live fleet-memory events, plus a writer from Mac/browser so cursors survive node changes

### "If you spoke while I was out of range or the audio failed, recover it automatically: tell me what I missed when I reconnect, without replaying things I already heard."
- **useful because:** A generated answer is not useful if the pendant never downloaded it, playback was interrupted, or the owner was not wearing it. This makes the system honest about the difference between generated, delivered, started, and finished, then gives one compact catch-up rather than silently losing the conversation or repeating it.
- **path:** relay → pendant → mac → dashboard
- **model tier:** Deterministic event reconciliation first; a cheap background model compresses missed items into a short catch-up. Realtime is only needed for an explicit spoken 'what did I miss?'
- **latency:** ACK ingestion should be sub-second when connected. On reconnect, identify missed items within one relay round-trip and synthesize a catch-up in under 5 seconds; queue it rather than interrupting if the owner is speaking or focused.
- **cost:** Usually under $0.01 per reconnect; most work is event joins and deduplication, with model cost only for multiple missed items.
- **security:** Use opaque artifact IDs and signed device sessions; do not put raw audio or sensitive text in ACKs. Apply the same speech redaction gate as briefings. A playback_started ACK must not count as heard; only playback_finished (or an explicit owner acknowledgment) advances the cursor. Expired or revoked evidence is omitted with a provenance explanation.
- **missing:** A durable relay-side delivery ledger keyed by artifact and owner/session, with monotonic sequence handling and offline duplicate suppression; A reconnect hook that turns undelivered or interrupted artifacts into one catch-up item and marks it claimed only after playback_finished; A pendant-to-relay authenticated event endpoint wired to the already-accepted firmware ACK queue; A policy for retention of generated audio versus spoken text after delivery

### "Learn how I actually consume briefings: if I always skip a section or only listen after 9, quietly shorten and retime it, and show me the reason before changing my routine."
- **useful because:** Today schedules are fixed and generation is treated as success even when the owner skips, interrupts, or hears only part of an item. A listening-aware cadence would reduce unwanted speech and put useful information where the owner's real day has room for it, without silently changing the owner's stated routine.
- **path:** pendant → relay → mac → dashboard
- **model tier:** Deterministic statistics over playback_started, playback_finished, interruption, and defer events; use a cheap background model only to group sections by topic and suggest a change. Realtime is unnecessary.
- **latency:** No added conversational latency. Learn over at least 7 comparable occurrences, then present a reviewable suggestion; applying a schedule change should take one explicit owner confirmation.
- **cost:** Well under $0.01 per day; event aggregation is local/relay-side and model calls are occasional topic clustering.
- **security:** Listening history is personal behavioral data: retain only coarse section IDs and counts by default, not audio or transcripts. Never infer consent from skips. Suggestions must be reversible and explain the evidence window and policy field; explicit confirmation is required before changing a routine.
- **missing:** A durable section-level listening ledger joining artifact IDs to routine and briefing-item IDs; A suggestion endpoint that can propose, explain, accept, or reject cadence changes without mutating the routine; A privacy-preserving aggregation and expiry policy for listening behavior; A stable item taxonomy so 'calendar', 'research', and 'battery' sections remain comparable across runs

### "Let me ask, 'what did you tell me about this last week?' and get the exact short answer, when I heard it, whether it finished playing, and the source it was based on."
- **useful because:** The system can generate and sometimes deliver speech, but the owner cannot reliably search their own spoken history or distinguish an answer that was merely generated from one that finished playing. This turns the pendant into a trustworthy memory aid rather than an unsearchable stream.
- **path:** pendant → relay → mac → dashboard → browser
- **model tier:** Cheap background indexing and embedding-free keyword/entity matching; realtime only answers the spoken query after the index returns candidates. Use the stronger model only to disambiguate multiple matching answers.
- **latency:** Return a candidate list in under 3 seconds for the last 30 days; synthesize a one-sentence answer in under 5 seconds. Dashboard can expose the full provenance chain without speaking it.
- **cost:** A few cents per month for indexing if summaries and hashes are retained locally; query-time model cost is under $0.01 unless disambiguation is needed.
- **security:** Spoken history can contain secrets and bystanders. Keep raw audio on the Mac only under existing retention rules, index redacted summaries and opaque evidence IDs, and apply the audio confidentiality gate before replay. A revoked source must show as unavailable, not be reconstructed from an old summary.
- **missing:** A durable conversation-answer index keyed by session, item, topic, and delivery state; A retention and deletion cascade from spoken answer to audio artifact, summary, and evidence links; A read-only query surface available to relay voice and dashboard with different sensitive-detail policies; An explicit 'heard' definition based on playback_finished or owner acknowledgment

### "Tell me when the system says it succeeded but the real-world result did not happen, and prepare a concise bug report with the evidence instead of quietly retrying or claiming success."
- **useful because:** A completed relay job, Mac receipt, or generated audio is not proof that the owner received the result or that an external state changed. The owner should get one trustworthy discrepancy report—what was claimed, what was observed, and the safest next step—rather than discovering failures by accident.
- **path:** relay → mac → browser → pendant → dashboard
- **model tier:** Deterministic invariant checks and receipt joins first; a cheap background model writes the human-readable discrepancy and groups recurring failures. Realtime speaks only a high-severity one-sentence warning.
- **latency:** Check after each job or delivery event in under 2 seconds; batch low-severity anomalies hourly. Never block ordinary reversible work on the explanatory model.
- **cost:** Near-zero for joins and counters; under $0.01 for an occasional grouped report. UART parsing and receipt correlation dominate engineering, not API spend.
- **security:** Bug drafts must strip secrets, page contents, credentials, and private audio. Never auto-submit an issue or retry a possibly irreversible action. Include immutable evidence references and let the owner revoke or delete the draft. Treat a missing pendant ACK as 'unknown delivery', not proof of failure.
- **missing:** A typed expected-effect contract per job, distinguishing generated, accepted, executed, externally observed, and owner-heard states; A cross-surface foreign key joining relay jobs, Mac jobs/actions, browser commands, pipeline artifacts, and pendant delivery events; A durable anomaly ledger with idempotent suppression and severity escalation; A safe draft target that can combine pendant diagnostics, receipts, and provenance without sending externally


## What it asked for

_Nothing._
## Its own summary

This round produced three owner-visible capabilities: (1) a single delivery-aware morning brief that coalesces overlapping 07:00/07:30 routines and reports unreadable sources honestly; (2) a source-linked 'what changed?' delta brief that advances cursors only after playback_finished; and (3) reconnect recovery that distinguishes generated/downloaded/started/finished audio and gives one deduplicated catch-up for interrupted or missed speech. The first two are intentionally related but distinct: one prevents duplicate scheduled jobs, the other prevents unchanged content from returning. I still need implementation of a durable delivery ledger, routine semantic coalescing, a common source-change cursor, and a reconnect hook wired to the accepted pendant ACK queue. I do not need another owner preference request this round; policy remains an explicit owner-set value with conservative defaults.

**Biggest unknown:** Whether the live relay has durable D1 tables and routes for /catchup, /v1/routines, /watches/reports, and delivery events; the current inventory summary did not verify those routes, so they must be checked before implementation claims.

