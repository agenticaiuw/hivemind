# Harness derivation — faculty-judgement — round 232

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Before I accept this meeting or commitment, tell me what it will displace, which promises become risky, and the safest alternative—without changing anything."
- **useful because:** This would be the system's highest-value judgement capability: it turns scattered calendar/mail/reminder/browser state into a concrete tradeoff before the owner commits, rather than merely reporting a schedule after the fact. It must distinguish observed facts from inferred risk and remain read-only until the owner explicitly chooses an action.
- **path:** pendant → relay → mac → browser
- **model tier:** Background/cheap model for extraction and ranking; realtime model only to answer the owner's spoken follow-up. Deterministic policy evaluation and cross-surface preflight gate all proposed mutations.
- **latency:** Initial read-only answer within 8 seconds; spoken first sentence within 2 seconds using cached state, then a cited refinement. No mutation in this mode.
- **cost:** Roughly $0.01–$0.05 per invocation, dominated by mail/browser extraction and one reasoning pass; cache unchanged sources and only re-run stale ones.
- **security:** Read-only by default. Mail and authenticated browser content may contain private material; return names and deadlines minimally, redact spoken content, attach evidence references, and require explicit confirmation before creating a reminder, declining a meeting, or sending anything. Calendar emptiness must be treated as unreadable when EventKit permission is unknown, never as a clear day.
- **missing:** A typed what-if impact route that accepts a candidate event/commitment and returns displaced items, risk explanations, alternatives, and evidence refs; Reliable read access to local reminders/notes and a corrected EventKit permission/emptiness verdict; A durable cross-surface join between relay jobs, Mac jobs, browser evidence, and resulting actions

### "When you get something wrong about me, let me say 'that's not right' once, and have the correction replace the bad assumption everywhere it was used—then show me what changed."
- **useful because:** Today a fact can be copied into memory, the context graph, a briefing, and a pending action with no reliable cascade. A correction should be a single owner-visible act that retracts the source claim, updates derived projections, marks affected plans stale, and gives a concise before/after receipt. This prevents yesterday's wrong assumption from quietly driving tomorrow's actions.
- **path:** pendant → relay → mac → browser
- **model tier:** Cheap deterministic matcher and provenance graph for propagation; use the expensive model only to resolve ambiguous references such as 'that' and to write the spoken explanation.
- **latency:** Acknowledge the correction in under 2 seconds; complete propagation and report affected artifacts within 10 seconds. If a destination is offline, retain a clearly marked pending revocation rather than claiming completion.
- **cost:** About $0.005–$0.02 per correction, mostly one ambiguity-resolution call; storage and propagation dominate engineering cost, not inference.
- **security:** Only owner-originated corrections may retract claims. Never silently rewrite an external source such as mail or a web page; mark it as contradicted locally. Secrets and private values must not be repeated in the spoken before/after. External actions already submitted cannot be undone by deleting their supporting claim; show that boundary and require separate reversal confirmation.
- **missing:** A durable provenance edge from every derived memory fact, graph entity, briefing item, and prepared action back to its evidence capsule/source; One cross-store retract-and-recompute service covering facts, context graph, fleet memory, browser provenance, briefing queue, and pending plans; A stale-plan invalidation hook that consumes a correction before any queued Mac/browser mutation; Owner-facing correction endpoint with an idempotency key and a compact impact receipt

### "Learn how much briefing I can absorb right now: if I interrupt, skip, replay, or finish an item, make the next brief shorter or more detailed for this situation—not permanently unless I tell you to."
- **useful because:** The pendant can finally become attentive to the owner's actual attention rather than delivering a fixed-length monologue. A walking owner who repeatedly skips technical detail gets a compact version; a seated owner who replays a source gets the citation and nuance. This is a closed loop no Mac-only assistant can provide because it depends on physical playback behavior and delivery ACKs.
- **path:** pendant → relay → mac → browser
- **model tier:** Use deterministic features first (interruptions, playback position, finish rate, time of day, wearing/availability); use a cheap background model to select compression level and a realtime model only for the next spoken response. Never infer a permanent preference from one event.
- **latency:** Adaptation decision under 100 ms from local ACK when possible; next-item rendering under 2 seconds. If telemetry is delayed, use the last signed local profile and label it provisional.
- **cost:** Under $0.01 per briefing session when summaries are cached; the expensive part is occasional re-summarization of a source at a new detail level, not the policy calculation.
- **security:** Playback behavior is personal attention telemetry. Store coarse counters, short-lived by default, with an owner-visible reset. Do not use interruption as consent for an external action. Source text remains subject to the existing confidentiality gate; a request for more detail must still pass sensitivity and audience policy.
- **missing:** A semantic briefing-item manifest with stable item IDs, source refs, detail levels, and a resumable cursor shared by relay and Mac; A profile learner that separates transient context (walking, meeting, noisy) from durable owner preference and exposes why it changed; A server-side renderer that can re-encode one item at compact/standard/deep levels without losing citations; A privacy-preserving aggregation of record_pendant_delivery_event plus barge-in/next/previous events

### "During a meeting, quietly keep a decision witness: separate what I said from what other people said, detect decisions and open questions, and at the end ask me to confirm only the commitments that are actually mine."
- **useful because:** The owner gets a trustworthy meeting memory without turning every utterance into a task or falsely attributing someone else's promise to them. It bridges the worn microphone, the Mac's local processing, and the relay's judgement; no single surface can both hear the room, know the owner's identity, and safely turn ambiguity into an owner-approved follow-up.
- **path:** pendant → relay → mac
- **model tier:** Realtime local/relay model for diarization and low-latency candidate extraction; a cheaper background model clusters decisions and unresolved questions after the meeting. No external action is taken until the owner confirms the candidate list.
- **latency:** Candidate chips within 3 seconds of a decision; end-of-meeting digest within 20 seconds. Audio should be discarded after local feature extraction unless the owner explicitly requests a transcript.
- **cost:** Approximately $0.10–$0.40 per hour of meeting, dominated by transcription/diarization; local VAD and feature extraction reduce uplink and inference volume.
- **security:** Other people's speech is highly sensitive and may not be recorded without consent. Default to on-device transient buffering, visible recording state, no raw audio upload, and no third-party names in spoken output. Require owner confirmation before reminders, notes, or messages; preserve uncertainty when speaker attribution is weak.
- **missing:** A local or relay speaker-attribution pipeline that can identify the owner without storing other speakers' raw audio; A typed decision-candidate record with speaker confidence, quoted-span expiry, meeting/session ID, and owner-confirmation state; A consent and recording-state protocol spanning pendant LED, Mac UI, and relay, including a hard stop that erases transient meeting material; An owner review surface that distinguishes owner commitments, delegated commitments, decisions, and unresolved questions

### "When two sources disagree, show me the disagreement as a small argument: what each source actually supports, which assumption causes the conflict, what evidence would settle it, and whether you want me to decide."
- **useful because:** The owner should not receive a single confident synthesis when mail, a web page, a calendar entry, or an earlier memory conflict. This is different from citing a source: it exposes the competing claims and gives the owner a cheap way to resolve only the consequential ones.
- **path:** pendant → relay → mac → browser
- **model tier:** Cheap deterministic claim extraction and date normalization first; use the expensive judgement model only when claims genuinely conflict or the proposed resolution could cause an external effect.
- **latency:** For cached sources, under 3 seconds to speak the conflict headline and under 15 seconds for the full argument. Stale sources should be labeled rather than silently refreshed.
- **cost:** About $0.02–$0.08 per conflict, dominated by fetching authenticated browser/mail evidence and one structured comparison; unchanged claims can be content-addressed and reused.
- **security:** Read only until the owner chooses. Quote the minimum needed, redact secrets and private content from speech, preserve source sensitivity and freshness, and never resolve a conflict by overwriting a source. Any resulting reminder, plan, or external action requires the existing policy/confirmation gate.
- **missing:** A normalized claim/contradiction graph with temporal validity, source freshness, and explicit support/contradiction edges; A resolver that can request one targeted missing observation instead of asking the owner for a vague decision; A compact owner-facing argument format with source-linked evidence and a durable 'resolved by owner' record; Propagation rules that mark plans stale when a premise is contradicted

### "Give me a private end-of-day account of where my attention went, what I advanced, and what I repeatedly avoided—without turning it into a productivity score or sending the analysis anywhere."
- **useful because:** The owner gets a humane reflection over actual interactions rather than a gamified dashboard: time spent in conversations, unfinished decisions, repeated deferrals, and meaningful progress across the Mac, browser, and pendant. The important judgement is separating observable behavior from a story about motivation and letting the owner correct that story.
- **path:** pendant → relay → mac → browser
- **model tier:** Background model over coarse local event summaries; realtime model only when the owner asks a follow-up. Deterministic aggregation supplies durations and counts, while the model may phrase hypotheses but must label them as hypotheses.
- **latency:** Generate in under 30 seconds at the scheduled end of day, with a one-sentence spoken summary and optional private screen detail. It must still work if one surface was offline by showing coverage gaps.
- **cost:** Roughly $0.03–$0.10 per day, dominated by summarizing event clusters; raw audio, page bodies, and keystrokes should never be sent for this feature.
- **security:** This is intimate behavioral data. Keep it local by default, short-lived, encrypted at rest, and never use it to make employment, health, or financial inferences. Do not claim emotional states or productivity from absence; show observation coverage and let the owner delete the day's report and derived claims.
- **missing:** A cross-surface coarse activity ledger that records categories and intervals without raw content or keystrokes; A coverage-aware summarizer that distinguishes observed attention from unavailable/offline periods; An explicit owner review/delete boundary for derived reflection reports and their source events; A scheduler and private delivery mode that cannot leak content through pendant speech when the owner is in public


## What it asked for

_Nothing._
## Its own summary

This round produced three distinct owner-facing capabilities. The most useful is a read-only what-if commitment simulator that explains what a new meeting or promise displaces before acting. I also proposed one-shot correction propagation across every derived claim and an adaptive briefing loop that learns transient attention from physical playback behavior and delivery ACKs. The correction proposal was recorded with a similarity warning, so it should be treated as a narrowly scoped correction/retraction workflow, not a second generic memory system.

**Biggest unknown:** I still need the owner to decide policy values that cannot be inferred safely: quiet windows, what qualifies as an emergency, whether notification content may ever be spoken, trusted destinations, and which classes (calendar detail, client names, credentials, files) require confirmation before leaving the Mac. Technically, the largest missing pieces are durable provenance links, a cross-store retraction cascade, a semantic briefing cursor, and a typed what-if impact route. I do not need another permission request this round; Accessibility/Screen Recording and USB-as-product-transport remain explicitly unavailable.

