# Harness derivation — faculty-judgement — round 170

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "After a briefing, tell me what I actually heard, what I missed, and offer only the next unread item when I press the pendant."
- **useful because:** Scheduled work currently records generation, not whether the owner downloaded or finished listening. This closes the loop between a useful briefing and what the owner actually received, preventing repeated or silently lost information.
- **path:** relay-realtime → pendant → relay → mac-planner
- **model tier:** background for reconciliation and summaries; realtime only for the owner's follow-up utterance
- **latency:** Under 2 seconds for a spoken status query; reconciliation can run after each delivery event and before the next briefing.
- **cost:** Low: deterministic joins dominate; one short background summary call only when there are multiple missed items, roughly $0.001-$0.01.
- **security:** Speak only item titles and delivery state by default, never raw private content. Evidence must link to artifact IDs and ACKs; no claim of hearing unless playback_finished exists. Owner confirmation required before replaying sensitive items aloud.
- **missing:** A read-side delivery-history route/query over the persisted pendant ACK events; A stable join from scheduled briefing item IDs to audio artifact IDs; A scheduler hook that runs the reconciliation before the next briefing

### "When I interrupt a spoken brief and say 'make that actionable', turn the exact current item into a reviewable reminder, note, or draft without losing my place."
- **useful because:** The pendant can currently interrupt, but the valuable follow-through is still a new ambiguous request. Binding the utterance to the current item prevents the system from acting on the wrong headline and lets the owner continue listening afterward.
- **path:** pendant → relay-realtime → relay → mac-planner → browser-extension
- **model tier:** Realtime for binding the short utterance to the current item; background for extracting dates, entities, and a draft.
- **latency:** Pause and acknowledge in under 500 ms; prepare the reviewable result in under 3 seconds; never block playback longer than the owner's interruption.
- **cost:** Usually one short realtime turn plus optional background extraction, roughly $0.002-$0.02.
- **security:** The current item is evidence, not authorization. Deterministic policy must classify create_note/create_reminder/append_to_draft as prepare or queue; external sends and destructive actions require confirmation. Sensitive item text must remain local or be redacted before TTS.
- **missing:** A production read/write semantic cursor for the active audio item (the granted tool is the contract but its side-effect branches are not all live); An idempotent bridge from prepared item actions to Mac reminder/note/draft stores; A spoken-safe rendering path outside briefingTriage.redactForDelivery

### "At the end of the day, tell me which important things were delivered, deferred, or lost because I was offline, busy, or never finished listening—and let me ask for one compact replay."
- **useful because:** This is the system's most distinctive end-to-end job: it knows the owner's attention state, the Mac's scheduled work, the relay's jobs, and the pendant's actual playback. Today those facts are disconnected, so the owner cannot distinguish 'I ignored it' from 'it never reached me'.
- **path:** pendant → relay-realtime → relay → mac-planner → browser-extension
- **model tier:** Background deterministic aggregation; realtime only to answer a follow-up or start the selected replay.
- **latency:** Generate during idle windows or before the evening routine; spoken answer under 2 seconds, replay starts at the next safe audio boundary.
- **cost:** Low per day: mostly database joins and policy evaluation; optional summary model roughly $0.002-$0.01.
- **security:** Default to counts, titles, timestamps, and reasons; do not expose mail/calendar contents to bystanders. Every statement needs provenance from job receipts, attention decisions, and pendant ACKs. Replay of private items requires explicit owner request and passes the speech disclosure gate.
- **missing:** Durable delivery ACK read/query and offline replay deduplication; A common correlation key between routine run, briefing item, audio artifact, and pendant event; A persisted attention-arbitration decision record, not only an in-memory response; An evening scheduler hook and an owner-configurable retention policy

### "When I say “I don’t remember,” reconstruct what happened across my pendant, Mac, browser, and scheduled work, separating observed facts from inference and showing me the shortest trustworthy timeline."
- **useful because:** Today the system can record isolated jobs, captures, browser evidence, and audio events, but it cannot answer an ordinary human question about a past episode. This would recover the owner’s lived timeline rather than merely searching logs.
- **path:** pendant → relay-realtime → relay → mac-planner → browser-extension
- **model tier:** Background evidence assembly with a small realtime model only to explain the finished timeline conversationally.
- **latency:** Initial timeline in under 5 seconds; follow-up narrowing under 1 second from the assembled evidence packet.
- **cost:** Low to moderate: deterministic joins and excerpts dominate; one concise explanation call, roughly $0.005-$0.03.
- **security:** Default output is local and provenance-first. Raw audio, page text, mail content, and secrets remain withheld unless the owner explicitly asks for the relevant span. Every inferred transition must be labeled inference, never presented as an observed event.
- **missing:** A cross-surface event index with a shared episode identifier; Read access to pendant delivery history and Mac/browser action timelines in one query; A durable distinction between observed, reported, and inferred events

### "Notice when my routines are quietly making my life worse—unfinished briefings, repeated interruptions, recurring deadline collisions, or work I keep deferring—and suggest one change with evidence, not a generic productivity lecture."
- **useful because:** The system currently runs routines and triage independently. It cannot recognize a persistent cost imposed by its own schedule or distinguish a one-off miss from a harmful pattern. This would make the assistant accountable for the attention it consumes.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Background analytics and anomaly detection; realtime only when the owner asks for the explanation.
- **latency:** Analyze during idle time or once daily; answer an explanation request in under 2 seconds.
- **cost:** Low: rolling statistics and policy rules are deterministic; optional language explanation roughly $0.002-$0.01 per daily report.
- **security:** Use counts, durations, categories, and source references by default, not message bodies. Never silently reschedule or disable a routine. Recommendations must identify the measured pattern, confidence, and the exact reversible change requiring owner approval.
- **missing:** A durable cross-surface history of interruption, playback completion, deferral, and routine outcomes; A causal-safe analysis layer that reports correlation rather than claiming causation; A reversible routine-change proposal and approval path

### "Before I enter a consequential situation, give me a private, time-bounded rehearsal: what I know, what I am assuming, what could surprise me, and the one question or document I should obtain before acting."
- **useful because:** The current system can inspect sources and execute plans, but it does not help the owner prepare under uncertainty. A compact rehearsal would turn scattered evidence into better judgment without pretending to know the future or taking action for them.
- **path:** pendant → relay-realtime → relay → mac-planner → browser-extension
- **model tier:** Background evidence synthesis; realtime delivery and owner questioning only.
- **latency:** Prepare in under 5 seconds from a named situation; spoken version under 30 seconds, with drill-down on request.
- **cost:** Moderate only when invoked: roughly $0.01-$0.05 for multi-source synthesis; no recurring cost when unused.
- **security:** The rehearsal must expose source age, conflicts, and uncertainty. Sensitive content is summarized privately and never spoken by default. It cannot send messages, submit forms, or create commitments; any resulting reminder or draft requires explicit preparation/confirmation under autonomy policy.
- **missing:** A typed rehearsal artifact with claims, assumptions, unknowns, expiry, and evidence references; A way to bind the owner’s named situation to relevant mail, browser, calendar, notes, and prior actions; A private delivery mode that guarantees sensitive content is not spoken aloud


## What it asked for

_Nothing._
