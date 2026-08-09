# Harness derivation — faculty-judgement — round 205

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Give me a 60-second trust report for today: what you told me, what I actually heard, what you changed, what failed, and what is still unresolved.”"
- **useful because:** The owner currently has jobs, receipts, spoken audio, browser work, and pending items scattered across surfaces. This creates a single honest end-of-day account that distinguishes generated from delivered and delivered from completed, so the owner can catch silent failures without interrogating the system.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Background model for aggregation and concise narration; deterministic joins and counts first, expensive model only for the final 60-second summary.
- **latency:** Under 10 seconds on demand; scheduled generation under 60 seconds. Spoken output remains one short sentence unless the owner asks for detail.
- **cost:** Roughly $0.01–$0.05 per report; dominated by the final summarization, not reads.
- **security:** Do not speak private subjects or credentials. Default to counts, titles classified by the existing sensitivity classifier, and provenance IDs; require dashboard confirmation to reveal sensitive details. A report must say unknown rather than infer completion.
- **missing:** A durable cross-surface join from relay job ID to Mac/browser job IDs; A queryable delivery-ACK projection for downloaded/played audio; A read-only report route that joins jobs, receipts, journal, pending briefings, and delivery events; A policy field for which categories may be spoken aloud

### "“If I missed part of a briefing, give me only the items I did not hear, in priority order, and let me say ‘save that’ or ‘remind me’ without restarting the briefing.”"
- **useful because:** A generated briefing is not the same as a heard briefing. The pendant's delivery and playback acknowledgements make a trustworthy spoken cursor possible; the owner gets recovery instead of repetition, and can bind a short utterance to the exact missed item.
- **path:** pendant → relay → mac → dashboard
- **model tier:** Deterministic item/cursor selection and deduplication; background model only compresses missed items. Realtime handles the owner's short barge-in utterance.
- **latency:** Resume list in under 2 seconds after an ACK sync; save/remind action acknowledgement under 1 second.
- **cost:** Usually under $0.01; model cost only when multiple missed items need compression.
- **security:** Never infer that downloaded means heard: require playback_started/finished evidence. Expired or ambiguous cursors must ask rather than attach a reminder to the wrong item. Spoken content passes the existing redaction path; sensitive items default to dashboard-only.
- **missing:** A durable briefing-item manifest with byte/time ranges and stable item IDs; A server-side projection of record_pendant_delivery_event with offline replay and duplicate suppression; A cursor-aware recovery endpoint that can enumerate unheard items; An owner-configurable rule for sensitive spoken items

### "“After you act, prove the result: check the world changed as intended, and tell me if it did not—before you call it done.”"
- **useful because:** Today a Mac/browser command can be accepted or receipted without a typed, user-facing postcondition. This capability turns ‘done’ into an observed fact: for example, verify the reminder exists, the file has the requested contents, or the page now shows the intended state, and stop safely when it drifted.
- **path:** relay → mac → browser → pendant → dashboard
- **model tier:** Deterministic postcondition checks and policy evaluation; use the realtime model only to explain a mismatch in one sentence.
- **latency:** Add at most 3 seconds for reversible local checks; up to 15 seconds for browser rereads. Never block an emergency stop.
- **cost:** Under $0.01 for deterministic checks; model explanation is occasional and <$0.02.
- **security:** Postconditions must be read-only and least-privilege. Revalidate before every mutation, bind checks to immutable target identity, and never treat a receipt as proof. If verification is unavailable, report ‘accepted, not verified’ rather than success.
- **missing:** A typed postcondition schema and read-only checker for Mac files/apps, browser pages, reminders, and pipeline state; A durable plan record linking pre-state, action, postcondition, and evidence; Executor integration that automatically pauses on failed or stale verification; Owner-visible explanation of which evidence established the result

### "“Give me the top world and US headlines from the last 12 hours—but if you cannot establish that freshness and coverage, say that plainly instead of filling the gap with old or guessed news.”"
- **useful because:** This is the owner's most repeated unmet request. A headline list is only useful if its publication times, source coverage, and retrieval success are honest; the pendant should not turn a failed web fetch into confident spoken news.
- **path:** relay → browser → mac → pendant
- **model tier:** Cheap background model clusters and deduplicates retrieved headlines; realtime model only formats the final three spoken sentences. Deterministic freshness/coverage checks must gate generation.
- **latency:** Under 20 seconds for a live brief; if sources fail, speak the failure in one sentence within 5 seconds rather than retrying indefinitely.
- **cost:** $0.02–$0.10 per brief, dominated by web retrieval and clustering; no model call when the freshness gate fails.
- **security:** Public-news retrieval only by default. Preserve source URLs and publication timestamps; do not let arbitrary page text become owner memory. Browser-authenticated sources require an explicit source policy and must not be read aloud merely because the tab is open.
- **missing:** A freshness-and-coverage receipt containing retrieval time, publication-time bounds, source identities, and failed-source reasons; A deterministic news retrieval route with bounded retries and deduplication across sources; A spoken fallback that distinguishes no coverage, stale coverage, and conflicting coverage; A scheduled-news routine that is not duplicated with the existing daily routines

### "“When you are about to speak something private and another person may be nearby, keep it silent and put a neutral prompt on my Mac; tell me what was withheld only after I explicitly ask.”"
- **useful because:** Today the system can classify secrets but the pendant speech path has no confidentiality gate and no bystander awareness. The owner should be able to wear it in a meeting, shop, or shared room without accidentally broadcasting a private subject, client name, or reminder.
- **path:** pendant → relay → mac → dashboard
- **model tier:** On-device deterministic acoustic classifier for probable nearby speech plus deterministic sensitivity routing; no realtime model needed unless the owner asks for an explanation.
- **latency:** Under 150 ms from detecting overlapping speech to ducking or replacing sensitive audio; false-positive review on the Mac can happen later.
- **cost:** <$0.01 per event. Hardware retrofit roughly $10–$30 for a directional/near-field output path or paired earpiece; power cost is modest but must be measured on the pendant.
- **security:** The device must retain no room audio and must not transmit raw bystander speech. Use only short-lived acoustic features and a conservative fail-closed rule. Never claim to identify a person; say only that nearby speech was detected. Owner must configure whether neutral text may appear on the Mac.
- **missing:** An on-device overlap/nearby-speech detector that emits only a boolean and confidence; A mandatory sensitivity gate in pendantSpeech/audioBrief, not only briefingTriage; A private-output target or durable silent queue for withheld items; An owner policy for neutral fallback wording and false-positive tolerance

### "“Before you say yes to a plan that will make my day impossible, show me the collision in human terms and offer the smallest change that preserves the important commitment.”"
- **useful because:** The current system can rank calendar/reminder material and detect some transitions, but it does not reason about the owner's finite travel, preparation, recovery, or attention budget. The owner needs a negotiation, not a calendar dump: identify the bottleneck, propose one reversible adjustment, and leave the original untouched until approved.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Background model for extracting preparation/travel assumptions from already-authorized evidence; deterministic interval and budget checks first; realtime only for the short negotiation.
- **latency:** Under 5 seconds for an on-demand collision; no unsolicited mutation. A proposed adjustment must remain a draft until physical or explicit owner approval.
- **cost:** $0.02–$0.08 per collision, dominated by structured interpretation of notes/mail/calendar context.
- **security:** Do not infer travel location or personal capacity from sensitive data without policy. Never move/cancel an appointment or send a message automatically. Explain every assumption and let the owner reject the model's estimate.
- **missing:** A typed capacity model for preparation, travel, recovery, and focus—not just event overlap; Readable calendar/reminder evidence with the existing unauthorised-empty safeguard; A reversible proposal object that can compare alternatives before mutation; An owner-editable preference for what commitments outrank others

### "“When you notice that I keep abandoning the same kind of task, do not nag me—tell me the likely hidden blocker, ask one useful question, and change the next attempt accordingly.”"
- **useful because:** A task can be repeatedly deferred because it needs another person, a missing login, an unrealistic estimate, or an emotional/context switch—not because the owner forgot. Today jobs, reminders, watches, and failures are separate; the owner gets repeated prompts rather than a diagnosis and a changed strategy.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Background model over bounded, redacted task-history features; deterministic streak and failure detection; realtime only for the single clarifying question.
- **latency:** Daily or after a configurable number of deferrals; the question itself should take under 10 seconds to answer.
- **cost:** $0.01–$0.05 per diagnosis; mostly local aggregation, with model use only when the pattern is ambiguous.
- **security:** Treat the blocker as a hypothesis, never a fact. Do not psychoanalyze or expose private task text aloud. Keep derived blocker claims short-lived, owner-visible, retractable, and excluded from external actions until confirmed.
- **missing:** A task identity that survives reminder/job/browser renames without merging unrelated work; A deferral/abandonment event stream across reminders, jobs, watches, and browser attempts; A hypothesis record with expiry, confidence, owner correction, and no-action-until-confirmed semantics; A small owner-facing question/answer route that updates the next attempt


## Changes it proposed to its own stack

### `hardware` — Add a private-output accessory path to the pendant audio system: a proximity-worn mono earpiece or directional near-field transducer with a hardware mute/route signal, so sensitive speech can be physically routed away from bystanders. The relay must negotiate a capability bit and the pendant must fail closed to silence when private output is unavailable; the existing speaker remains the public route.
- **owner gets:** They can receive private reminders, names, and action confirmations while walking or sitting with other people instead of losing useful information or broadcasting it. This creates a real privacy boundary rather than trusting classification alone.
- effort: New audio accessory, enclosure/mechanical integration, firmware route negotiation, bridge support, and a measured acoustic-leakage test in quiet and noisy rooms. Medium-to-high hardware effort.  ·  risk: Accessory loss, pairing failures, or false route state could silently expose content. Recovery is fail-closed: private-class audio is withheld unless the pendant receives an authenticated private-route-ready signal; provide a neutral public fallback.
- cost: Approximately $15–$60 in prototype components/accessory, plus enclosure and certification work; added audio power likely tens of mW while active, to be measured.  ·  latency: Negligible route selection latency; pairing or route verification may add 0.5–2 seconds before private speech, during which it must remain silent.
- security: Improves physical confidentiality, but requires authenticated route capability and no raw-room-audio retention. It complements—not replaces—the sensitivity classifier and owner policy.
- depends on: A mandatory sensitivity gate in pendant speech synthesis; An authenticated private-route capability handshake between pendant, bridge, and relay; Owner-configurable policy for whether private content may be spoken at all


## What it asked for

_Nothing._
## Its own summary

Round 205 produced three owner-facing proposals: (1) a daily trust report that distinguishes generated, delivered, heard, completed, failed, and unresolved work; (2) missed-brief recovery keyed to authenticated playback cursors, so the owner hears only unheard items and can save/remind the exact item; and (3) postcondition verification, so actions are not called done from acceptance receipts alone. I also explored a freshness-gated news brief, but the recorder correctly noted its named retrieval pieces already exist; the genuinely missing part is the freshness/coverage receipt and failure gate, not another research route.

**Biggest unknown:** The owner still has not set the policies that determine what may be spoken aloud, quiet/interruption windows, trusted destinations, and sensitive-content handling. I will not invent those. Technically, the largest missing joins are a durable relay↔Mac/browser ID mapping, a queryable pendant delivery projection, and typed postcondition records/checkers. The owner's timezone evidence also conflicts (memory says America/Chicago while authoritative Mac routine policy is America/New_York), so any time-sensitive judgement should use reconcile_personal_state before promising behavior.

