# Harness derivation — faculty-judgement — round 268

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Make sure I actually receive the important things. If a briefing or alert was generated but I never downloaded or heard it, tell me and retry it at the next safe moment.”"
- **useful because:** Today generation/acceptance receipts can falsely feel like delivery. This closes the human loop: the system knows whether the pendant downloaded, started, finished, or lost an item, and can distinguish ‘served’ from ‘heard’. It is the most valuable trust feature for a wearable assistant because missed information becomes visible instead of silently disappearing.
- **path:** relay → pendant → mac-bridge → dashboard
- **model tier:** Background model classifies urgency and chooses a concise retry; realtime is used only for the owner’s spoken query. Deterministic delivery state and deduplication must remain non-model logic.
- **latency:** Under 2 seconds to acknowledge a delivery event; retry decision within 30 seconds of an interruption or reconnect. No model call for ordinary ACKs.
- **cost:** Near-zero for ACK ingestion and dedupe; roughly $0.001–$0.01 per exceptional retry summary, dominated by TTS/model generation.
- **security:** ACKs contain opaque artifact IDs and timing, not audio or transcript. A retry must obey attention_arbitrate and autonomy_policy_evaluate; never repeatedly interrupt. Expired or private items must be re-authorized rather than replayed.
- **missing:** A durable delivery-state join from artifact to briefing item/job; Retry scheduler that consumes record_pendant_delivery_event; A user-visible ‘heard/not heard’ history and idempotent retry policy; Pendant firmware implementation of the already-accepted audio_delivery_ack_queue

### "“Before my morning brief, verify that the sources and the audio path are healthy. If calendar or mail is unreadable, or the pendant cannot play, say exactly what is missing and give me the best degraded version instead of pretending the day is clear.”"
- **useful because:** The current scheduled routines can complete while EventKit silently returns an empty calendar, permissions disagree, or audio never reaches the owner. This is an owner-facing reliability contract: every brief is either source-backed and heard, or explicitly degraded with a reason and a recovery path.
- **path:** relay → mac-bridge → pendant → dashboard
- **model tier:** Cheap background evaluator performs deterministic source/permission/audio checks and composes a short status; realtime only answers follow-up questions.
- **latency:** Run 1–2 minutes before a scheduled brief; allow 10 seconds for checks and 20 seconds for fallback generation. Never delay an urgent alert beyond its deadline.
- **cost:** Usually <$0.002 per run for checks and a short fallback; normal brief generation/TTS remains the dominant cost.
- **security:** Do not infer calendar access from Automation-TCC. Empty EventKit results require the existing corroboration rule. Health results should expose provenance without leaking mail/calendar contents; private source failures are summarized, not quoted.
- **missing:** A scheduler hook before each routine/briefing; Typed health adapters for EventKit-readability, mail-readability, browser state, and pipeline readiness; Degraded brief templates and a durable reason code attached to the briefing receipt; Automatic handoff from failed Mac delivery to relay/pendant inbox

### "“After a meeting, turn my spoken fragments and the meeting’s related messages into a private follow-up packet: what I promised, what others owe me, draft replies and reminders, and the evidence for each. Do not send anything.”"
- **useful because:** The owner can capture a thought hands-free but currently has to reconstruct context later. This joins the pendant’s moment/audio evidence with Mac calendar and mail, then produces reviewable drafts and reminders. It turns fleeting spoken context into useful work without crossing the dangerous boundary of sending on the owner’s behalf.
- **path:** pendant → mac-bridge → browser → relay → dashboard
- **model tier:** Background model extracts candidate obligations and drafts from bounded, redacted evidence; realtime handles capture and a concise confirmation. Deterministic policy blocks sending and requires provenance for every claim.
- **latency:** Capture acknowledgment under 1 second; packet available within 2 minutes after the meeting or reconnect. Draft creation is asynchronous and reviewable.
- **cost:** About $0.02–$0.10 per meeting packet, dominated by transcript/evidence synthesis and draft TTS if requested; no cost for deterministic reminders/receipts.
- **security:** Meeting content and third-party names are private by default. Store short-lived derived claims linked to source capsules; no raw quotes in relay memory. Require explicit confirmation for any reminder due date inferred from speech and prohibit send_email/mutations until owner approval.
- **missing:** A meeting-boundary trigger and correlation key joining calendar event, voice note, and mail; A read-safe EventKit calendar adapter with the empty-result corroboration fix; A provenance-linked obligation extractor and packet store; Review UI and explicit prepare/approve handoff for drafts and reminders

### "“When a website asks for information, tell me exactly what would leave this machine, fill only the minimum necessary fields from my local sources, and leave anything ambiguous blank for me to decide.”"
- **useful because:** The owner should not have to choose between manually retyping everything and blindly revealing a whole profile. A browser session, local Mac files, and the pendant’s deliberate confirmation can provide least-disclosure assistance that no single surface can safely deliver.
- **path:** browser → mac-bridge → relay → pendant → dashboard
- **model tier:** Local deterministic field classifier and redaction policy do the first pass; a background model maps ambiguous fields to candidate sources. Realtime is used only to explain the proposed disclosure and collect a confirmation.
- **latency:** Preview in 5 seconds for ordinary forms; never auto-submit. The owner can approve field groups individually from the dashboard or pendant transaction latch.
- **cost:** <$0.01 for most forms; model cost only for ambiguous labels or unusual schemas.
- **security:** Never send secrets, credentials, or third-party data by default. Show destination, field, value class, source, and retention warning. The browser extension must not expose raw password/OTP fields to the model; submission requires the existing physical approval boundary.
- **missing:** A disclosure manifest that binds each outgoing field to source, destination, sensitivity, and expiry; A field-level minimization and confirmation UI; A browser-to-Mac local-value broker that returns typed candidates without exporting whole files; A post-submit receipt proving exactly which fields were sent

### "“If my pendant disappears or loses its link, keep me covered without pretending it is still connected: route only urgent items to my Mac/browser, pause private audio, show me what was missed, and restore normal delivery when the pendant returns.”"
- **useful because:** A worn device can be out of range, dead, or lost while the relay and Mac continue operating. Today those bodies do not share a coherent absence/recovery policy, so work can be generated into a void or private audio can be retried in the wrong place. This is continuity for a real physical failure, not another notification queue.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic presence/session state machine decides routing and expiry; background model summarizes missed items only after reconnection. Realtime is unnecessary except for an owner query.
- **latency:** Detect absence within 60 seconds; reroute urgent items within 5 seconds; reconcile missed work within 2 minutes of return.
- **cost:** Near-zero for state transitions and routing; <$0.01 for an optional reconnect digest.
- **security:** Absence is not consent to disclose private content on another surface. Default reroute carries only urgency, source class, and a safe short prompt; private content remains queued until the owner authenticates or physically acknowledges. Device-session revocation and panic-wipe epochs must win over stale reconnects.
- **missing:** A signed pendant presence lease and explicit lost/return states; A cross-surface routing policy that separates urgency from disclosure; A durable missed-item reconciliation record; A reconnect handshake that consumes delivery ACKs and revocation epochs

### "“Prepare a handoff for the person I name: the current state, what I need from them, relevant links, and the smallest set of files or messages they need. Let me see exactly what they will receive and approve it from the pendant before anything is sent.”"
- **useful because:** The system can act across the owner’s Mac and browser, but it cannot safely turn that state into a bounded human-to-human handoff. This would make delegation fast without dumping an entire inbox, drive, or browser session onto another person.
- **path:** mac-bridge → browser → relay → pendant → dashboard
- **model tier:** Background model assembles a draft from explicitly selected sources; deterministic audience/redaction policy computes the disclosure set. Realtime only reads a short preview and waits for deliberate approval.
- **latency:** Draft in under 30 seconds; approval is synchronous and physical. Nothing is transmitted before the owner sees recipients, sources, and sensitivity classes.
- **cost:** Roughly $0.02–$0.08 per handoff, dominated by summarization; no model cost for redaction, source enumeration, or approval.
- **security:** Recipient identity and destination must be explicit. No guessed trust relationship. Secrets, credentials, private third-party content, and whole-file attachments are excluded by default. The pendant receives only an opaque approval summary, never the handoff contents.
- **missing:** Audience-scoped disclosure policy with an owner-maintained recipient allowlist; A packet manifest linking every sentence/file to its source and redaction decision; A review renderer that can show the exact outbound payload and its hashes; A send adapter with physical approval and a durable post-send receipt


## Changes it proposed to its own stack

### `relay` — Make every briefing artifact carry a durable delivery contract: artifactId, briefingItemId, source/job IDs, sensitivity, expiry, retry budget, and last authenticated pendant state. Reconcile record_pendant_delivery_event against existing job/pipeline receipts, suppress duplicates, and expose a single ‘generated/downloaded/started/finished/missed’ timeline.
- **owner gets:** The owner can finally trust that ‘done’ means heard, not merely generated. Missed important information becomes an actionable, explainable item instead of silent failure.
- effort: Medium: schema migration, event reducer, reconnect replay tests, and one dashboard/voice status surface.  ·  risk: Out-of-order or forged events could mark audio heard incorrectly; require authenticated device sessions, monotonic sequence checks, and fail closed to ‘unknown’. Recovery is replay from the event log.
- cost: Negligible storage and compute; no model cost for the reducer.  ·  latency: Sub-second event processing; no added latency to ordinary playback.
- security: Improves privacy by keeping opaque artifact IDs while making playback evidence available only to the owner.
- depends on: record_pendant_delivery_event; audio_delivery_ack_queue; A stable join between pipeline artifact IDs and briefing item IDs

### `integration` — Add a pre-brief source-and-output contract to routine execution. Before a scheduled briefing, run the authoritative EventKit/mail corroboration checks, browser/pipeline reachability, and duplicate-routine detection; attach a typed health vector to the briefing. If any required source is unreadable, generate a degraded brief that says so rather than interpreting empty data as ‘clear’.
- **owner gets:** A morning brief stops lying by omission. The owner hears ‘calendar unavailable’ or ‘audio not delivered’ and can choose a fallback, instead of confidently missing a meeting.
- effort: Medium: routine hook, health-vector schema, degraded templates, and tests for unauthorized-but-empty EventKit results.  ·  risk: Checks could delay or over-warn; use deadlines, cached last-known-good state, and attention_arbitrate. Never substitute the Mac timezone for the pendant’s unknown zone.
- cost: Low; mostly local probes, with occasional short model/TTS fallback.  ·  latency: Adds up to 10 seconds before scheduled output, with deadline bypass for urgent items.
- security: Health vectors contain statuses and provenance IDs, not message bodies or calendar titles.
- depends on: reconcile_personal_state; cross_surface_preflight; authoritative EventKit empty-result corroboration; attention_arbitrate

### `context` — Introduce a meeting correlation envelope that can bind one owner capture/moment marker to a calendar event window, nearby mail/browser evidence, and later drafts without copying raw meeting content into relay memory. Every extracted obligation keeps source references and expires unless the owner promotes it.
- **owner gets:** A five-second spoken thought during a meeting becomes a reliable follow-up later, without requiring the owner to remember which meeting or message it belonged to.
- effort: Large: correlation service, source-window rules, capsule-to-fact links, expiration/retraction propagation, and a review packet UI.  ·  risk: Wrongly associating a private conversation with the wrong meeting is worse than missing it. Require confidence thresholds, show competing matches, and keep candidates as drafts until owner review.
- cost: Approximately $0.02–$0.10 per packet for extraction; storage remains bounded by short TTLs.  ·  latency: Capture remains instant; packet synthesis is asynchronous within roughly two minutes.
- security: Third-party names and raw quotes stay local by default; only redacted, source-linked summaries may cross the relay, and sending is prohibited.
- depends on: offline_moment_bookmark; POST /capture; GET /mail/triage; browser provenance mounting; capsuleId linkage into memory facts; POST /prepare and POST /approve


## What it asked for

_Nothing._
## Its own summary

Round 268 produced three owner-facing capabilities and three concrete changes: authenticated heard-vs-generated delivery, preflighted/degraded morning briefs, and provenance-linked post-meeting follow-up packets. The recorder flagged the first two as near existing backlog items, so their genuinely new value is the durable artifact↔item delivery join and typed source-health/degraded receipt; the meeting idea’s new core is the correlation envelope and expiry/retraction behavior.

**Biggest unknown:** Whether the live route inventory already has an undocumented artifact-to-briefing-item join or pre-brief routine hook. I still need that code-level confirmation, plus implementation of the missing durable joins, before promising any of these as shipped.

