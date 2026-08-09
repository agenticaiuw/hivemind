# Harness derivation — faculty-judgement — round 228

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Make my morning brief a reliable promise: before it speaks, check that it is the one intended brief, its calendar/mail sources were actually readable, and the pendant received and played it; if anything failed, tell me one short honest sentence and leave the full brief queued for later."
- **useful because:** Today several daily routines can produce overlapping briefs, and a successful server job does not prove the pendant downloaded or played the audio. This gives the owner one dependable morning moment instead of silent duplicates or confident all-clear reports.
- **path:** relay → mac → pendant → dashboard
- **model tier:** background for source collection and deduplication; realtime only for the one-sentence failure explanation
- **latency:** Evaluate and reconcile within 30 seconds of the scheduled run; spoken result under 5 seconds once ACKs arrive. Do not hold the owner waiting for slow mail/calendar reads—queue with a clear pending state.
- **cost:** Low: one deterministic policy/reconciliation pass plus existing source reads; model cost only for composing the short failure sentence. Dominant cost is existing mail/calendar I/O, not inference.
- **security:** Do not speak source content when validation fails; expose only statuses and provenance IDs by default. Calendar emptiness must be treated as unreadable unless corroborated. Require explicit owner policy before changing or disabling existing routines.
- **missing:** A durable briefing_run_id linking the selected routine, source-read receipts, generated artifact, and pendant delivery ACK; A scheduler-side single-flight/idempotency guard so duplicate routines cannot both speak; A small dashboard status view for pending/failed/played with retry controls; An automatic retry/escalation policy that uses the owner's future briefing preferences

### "Learn how much help I actually want in each situation: after I accept, dismiss, postpone, or undo a suggestion, show me a weekly pattern report and use it to recommend—not silently change—how proactive you should be for that kind of task."
- **useful because:** A fixed autonomy threshold cannot fit a real life: the owner may want aggressive help with deadlines but no interruptions during research. Turning real outcomes into reviewable recommendations reduces nagging without silently taking away agency.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Cheap deterministic aggregation for outcome statistics; background model only for the weekly explanation and suggested policy edits; realtime is unnecessary.
- **latency:** Record each outcome immediately with no interruption. Weekly report generated in under 1 minute and available as a short spoken summary or dashboard detail.
- **cost:** Very low inference cost; mostly local aggregation over existing receipts and physical approval/stop events. A small background summary is the dominant model cost.
- **security:** Never infer consent from silence, playback completion, or lack of undo. Keep recommendations separate from active policy; changing autonomy, interruption, or disclosure rules requires explicit owner confirmation. Aggregate by coarse action class, not sensitive content or third-party names.
- **missing:** An outcome event schema joining proposal, policy decision, owner response, physical approval/stop, execution receipt, and undo; A privacy-preserving aggregation store with expiration and a dashboard review surface; A typed endpoint that returns recommended policy deltas without applying them; A reliable way to distinguish 'not seen' from 'seen and declined' using pendant delivery ACKs and attention state

### "When I interrupt you, keep a small recovery card: what I was hearing, where I stopped, what decisions remain, and the safest next options. At my next free moment, offer only that card instead of replaying the whole brief or losing the thread."
- **useful because:** A stop gesture protects attention, but today stopping can strand context or cause the same item to return as a duplicate. A durable, source-linked recovery card turns interruption into control: the owner can resume, defer, or dismiss without reconstructing what happened.
- **path:** pendant → relay → mac → dashboard
- **model tier:** Realtime only to acknowledge the interruption; deterministic cursor/state handling does the durable work; background model makes a compact card from the existing item and provenance.
- **latency:** Acknowledge stop immediately; write the card in under 500 ms. Offer it only at the next attention-approved window, with no unsolicited content replay.
- **cost:** Low: cursor and receipt writes dominate; background summarization is at most one short call per interrupted item and can be skipped for already-short text.
- **security:** The card must contain opaque source references and redacted text by default, never secrets or raw third-party content. It must expire and honor revocation. A recovery card may not authorize an action; any mutation still passes autonomy policy and physical approval where required.
- **missing:** A durable recovery-card store linked to the semantic audio cursor, context handle, and provenance sources; A state machine for interrupted/resumable/expired/dismissed cards with idempotent transitions; A single resume offer integrated with attention arbitration so multiple surfaces cannot replay it; A redaction-aware card renderer for spoken versus dashboard output

### "Give me a genuinely private voice mode: when other people are nearby, keep the pendant from speaking the substance of messages and show me only a discreet cue; when I am alone, let normal spoken replies through. Let me override the mode deliberately for one reply."
- **useful because:** The owner carries the device into meetings, shops, and homes where a correct answer can still disclose private mail or calendar content to a bystander. Today the speech path has no bystander/content gate, and a server-side privacy setting cannot react safely when the link is delayed or absent.
- **path:** pendant → relay → mac → dashboard
- **model tier:** A small on-device acoustic classifier handles near-real-time occupancy cues; the relay/Mac apply deterministic content policy and use a background model only to classify ambiguous output. Realtime is reserved for the spoken exchange.
- **latency:** Classify the local acoustic environment within 250 ms and choose silent versus spoken output before playback starts; an override should affect the next reply in under 1 second.
- **cost:** Hardware and firmware dominate: roughly $5–15 for a revised enclosure/sensor path and under a few cents per interaction for occasional classification. No model call is needed for ordinary private/public routing.
- **security:** The device must retain no ambient recordings and transmit only a coarse signed state (alone/uncertain/others-present). Fail closed on uncertainty for sensitive content. The owner’s one-reply override must expire, be auditable, and never authorize external actions. Existing redaction remains a second defense, not the decision itself.
- **missing:** A privacy-presence sensor or carefully validated microphone-only classifier on a future pendant; the current board has no dedicated proximity sensor or haptic/private display; A local playback router that can choose silent cue, short neutral phrase, or full audio before PCM is generated; A policy table mapping sensitivity and destination to allowed output, with owner-editable rules and provenance; A discreet output channel such as a tiny e-ink/LED cue or paired phone display; the current single LED is already overloaded

### "When I say “that’s wrong” or correct a fact, make the correction stick everywhere: acknowledge the exact claim I corrected, show what source caused it, stop using the old value, and tell me if any queued brief or draft still contains it."
- **useful because:** A conversational correction should change future behavior, not disappear with one turn. Today facts, context-graph copies, browser-derived claims, queued audio, and drafts do not share a dependable correction/retraction path, so the owner can hear the same mistake again.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Realtime for resolving the owner’s correction to the current spoken item; deterministic provenance fan-out and tombstoning for propagation; background model only when the correction is ambiguous.
- **latency:** Acknowledge and quarantine the old claim within 1 second; complete the cross-surface scan within 30 seconds and report any unreachable copies instead of claiming success.
- **cost:** Low-to-moderate: deterministic store scans and tombstones dominate; model use is limited to ambiguous reference resolution.
- **security:** Never overwrite a source silently or infer a factual correction from tone alone. Preserve an auditable old-value hash, require confirmation when the correction would mutate an external record, and redact private values in spoken acknowledgements. Revocation must propagate to generated audio and drafts, not merely hide a dashboard row.
- **missing:** A stable claim identifier linking spoken text, evidence capsule, memory fact, graph entity, briefing item, and generated artifact; A transactional retraction protocol spanning Mac stores, relay memory, browser provenance, and pendant queues; A content-addressed scan of queued audio/drafts that can invalidate artifacts without replaying their private text; A disambiguation/confirmation interaction for corrections that refer to more than one claim

### "Each morning, tell me the three unknowns that could most change my day—such as an unreadable calendar, a stale browser session, an unconfirmed deadline, or an offline pendant—and what single check would resolve each. Do not fill gaps with guesses."
- **useful because:** The owner currently gets confident-looking answers from incomplete sources, while important uncertainty is scattered across permissions, jobs, browser state, and delivery status. A ranked uncertainty report lets them spend attention where it changes outcomes instead of discovering failures after a missed commitment.
- **path:** relay → mac → browser → pendant → dashboard
- **model tier:** Deterministic evidence freshness/conflict scoring first; a cheap background model turns the top gaps into three plain sentences. Realtime is not needed unless the owner asks a follow-up.
- **latency:** Build within 20 seconds of the morning trigger and speak in under 30 seconds; each proposed check should be executable or explicitly marked owner-only.
- **cost:** Low: mostly existing status and receipt reads; background summarization is the only material inference cost.
- **security:** Report metadata and uncertainty, not private source contents. Never rank an item as safe merely because a source returned empty; preserve provenance for each gap. Checks that read sensitive mail/calendar or mutate state require the existing policy and confirmation gates.
- **missing:** A typed uncertainty record with evidence age, contradiction, impact, and one resolving check; A ranking model that separates unknown, negative, stale, and inaccessible rather than collapsing them; A spoken/dashboard renderer that exposes why each gap was ranked without leaking source text; A way to mark an owner-declined check so it is not repeatedly nagged


## What it asked for

_Nothing._
## Its own summary

Three new capabilities recorded: (1) an end-to-end morning-brief promise that deduplicates routines and proves source readability plus pendant playback, (2) an outcome-based trust calibration report that recommends—but never silently changes—autonomy settings, and (3) interruption recovery cards that preserve the exact audio cursor and unresolved decisions without replaying content. Fresh discovery also confirms the owner has multiple overlapping daily briefs and a timezone conflict: the owner projection says America/Chicago while Mac-resolved routines are authoritative in America/New_York. I still need explicit owner choices on which brief is canonical, whether brief content may ever be spoken aloud around others, and whether weekly autonomy recommendations are wanted; technically, the missing pieces are durable cross-surface joins and outcome/recovery stores, not another model.

**Biggest unknown:** The owner's intended morning-brief contract: one canonical routine and its desired local timezone, plus whether a failed or unreadable brief should be retried automatically or only queued for manual playback.

