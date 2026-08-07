# Harness derivation — faculty-judgement — round 139

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“The meeting just ended—turn what happened into follow-through.”"
- **useful because:** The owner often remembers commitments only after the context is gone. The pendant supplies an immediate spoken debrief, while Calendar, Mail, Notes, and authenticated tabs provide corroboration. The system would produce a private, reviewable aftermath packet: decisions, owners, dates, unanswered questions, and prepared drafts/reminders, without sending or creating commitments silently.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** background for transcript extraction and cross-source reconciliation; realtime only for the brief spoken debrief and clarifying questions
- **latency:** Capture must begin in under 2 seconds; a useful packet within 3 minutes of the meeting ending; no need for low-latency background work
- **cost:** About $0.03–$0.15 per meeting depending on transcript length and number of private pages; browser/Mac reads and storage dominate operational cost, not model inference
- **security:** Meeting audio and private mail/browser content leave the device only to the relay/model; default to a short-lived transcript, show every cited source, and require explicit approval before creating reminders or sending drafts. Support a spoken 'discard debrief' command.
- **missing:** A meeting-aftermath orchestrator that joins a just-ended Calendar event to a pendant debrief and gathers only the relevant Mail/Notes/browser evidence; A review UI/audio queue for accepting individual follow-ups; A reliable post-meeting trigger from Calendar plus a pendant button/voice event

### "“Before I meet someone, remind me who they are and what I owe them—without making me search.”"
- **useful because:** The owner gets relationship context at the moment it matters, not a generic morning digest. The system would combine the upcoming Calendar attendee, recent owner-approved notes/captures, prior correspondence, and open follow-ups into a 30-second spoken card on the pendant, with uncertainty clearly marked and no invasive unsolicited profiling.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** background compilation shortly before the event; a cheap realtime model only formats the final short spoken card
- **latency:** Compile 5–15 minutes before a meeting; playback should start within 2 seconds when the owner asks 'who am I meeting?'
- **cost:** Roughly $0.01–$0.06 per briefing; calendar/mail retrieval and privacy filtering dominate, with a compact model summary
- **security:** Only use explicitly selected contacts and owner-created notes, never infer sensitive traits, and cite the exact message/note/date behind each claim. Keep the card local/ephemeral by default; require confirmation before saving a new relationship fact.
- **missing:** A relationship-context store with explicit source, expiry, sensitivity, and owner correction; Calendar attendee-to-contact resolution across Mac and authenticated browser sessions; A pre-meeting scheduler and pendant delivery acknowledgement

### "“I’m stuck. Look at what I’m doing and give me one concrete next move, then do the reversible part.”"
- **useful because:** This turns the pendant from an answer box into an escape hatch from paralysis. The Mac can inspect the active project, open tabs, recent files and current machine context; the owner gets one deliberately small next action rather than a long plan, and the reversible portion can be carried out immediately. It is useful precisely when the owner cannot explain the whole task.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** realtime for the short spoken triage; background/local planner for inspecting context and selecting a bounded next move
- **latency:** Acknowledge in under 2 seconds and offer one next move in under 20 seconds; execution must pause for confirmation if it changes external state
- **cost:** About $0.02–$0.10 per invocation; local context gathering is cheap, while vision or authenticated-page inspection is the main cost
- **security:** Context inspection must be scoped to the active project/window and visibly list what was read. Never infer permission to send, purchase, publish, or delete from 'I'm stuck'; reversible actions can run, irreversible ones require a separate approval and evidence receipt.
- **missing:** A context-scoped stuck-state detector and one-next-action selector; A Mac route that returns active project/window/tab/file context without broad screen capture; A pendant interaction that can accept/reject the proposed move offline and reconcile when USB/LTE returns

### "“Help me learn what actually gives me energy or drains me, without turning my life into a surveillance dashboard.”"
- **useful because:** The owner can make better choices from patterns they cannot notice in the moment. After a lightweight pendant check-in or spontaneous voice note, the system can privately relate mood/energy to calendar load, meeting types, travel, sleep notes, and work context over weeks—then surface only cautious, owner-reviewable hypotheses such as “afternoon calls seem costly.” It must ask before retaining sensitive observations and allow correction or deletion.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** A cheap background model performs periodic aggregation and hypothesis generation; realtime is used only for an optional one-question check-in
- **latency:** Check-in acknowledgement under 2 seconds; weekly pattern review can take minutes and must never interrupt the owner
- **cost:** Approximately $0.02–$0.10 per weekly review, dominated by private-context retrieval and storage; daily check-ins can be compact and low cost
- **security:** Energy, mood, health-adjacent observations are highly sensitive. Keep raw audio ephemeral, use explicit opt-in categories, segregate derived hypotheses from source facts, show provenance and confidence, never share externally, and provide a physical/voice erase command that works offline.
- **missing:** A consented longitudinal wellbeing journal with separate raw, derived, and deleted states; A privacy-preserving correlator for pendant check-ins and selected calendar/context signals; A review surface that presents hypotheses as questions rather than diagnoses, with correction and deletion controls; An offline-capable erase latch on the pendant that can queue deletion until relay reconnection

### "“Keep an emergency packet for the person I choose, so if I’m unreachable they know what matters—but never give anyone my whole digital life.”"
- **useful because:** In illness, travel emergencies, or loss of the device, a trusted person needs a small, current set of contacts, medical/allergy notes the owner explicitly supplied, household instructions, active obligations, and document locations—not an AI summary of everything. The owner can review the packet periodically on the Mac and confirm its release policy with a physical pendant action.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Background model for deduplication and plain-language compilation; no realtime model is needed except to answer an owner query while reviewing
- **latency:** Updates can compile overnight or after an explicit review; release verification should complete in seconds when an authorized emergency condition is met
- **cost:** Roughly $0.05–$0.30 per packet refresh depending on documents and browser sources; encrypted storage and key management dominate operational complexity
- **security:** This is an extremely sensitive escrow. Require named recipients, explicit field-level inclusion, expiry, revocation, two-person or time-delay release, encrypted client-side packaging, and a physical pendant confirmation for changes. Never infer emergency status from silence alone; log every access and notify the owner when possible.
- **missing:** A field-level emergency-packet vault with encrypted export and revocation; An owner-defined, multi-factor release protocol that survives loss of the Mac and relay; A periodic review workflow that highlights stale or missing fields without exposing the packet; A pendant-held local key or confirmation secret with safe recovery procedures

### "“When I’m about to say yes to something important, show me the real cost to my time and commitments before I agree.”"
- **useful because:** The owner routinely commits in conversation before seeing the downstream collision. The pendant can capture the proposed promise, while the Mac and authenticated browser inspect calendar load, existing deadlines, travel, and known obligations. The system returns a compact “capacity receipt”: what would move, what is uncertain, and a suggested counteroffer the owner can speak or send for review. It does not decide for them or silently decline anything.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Realtime for extracting the proposed commitment and asking one clarification; background/local planning for impact analysis and counteroffer drafting
- **latency:** A preliminary answer in under 10 seconds while the conversation is live; deeper analysis can finish within 2 minutes and remain a review item
- **cost:** About $0.03–$0.20 per analysis; calendar/task/browser retrieval and conflict ranking dominate model cost
- **security:** Commitment content may include private conversations and other people’s data. Keep the captured snippet short, show exactly which sources informed the estimate, avoid treating inferred deadlines as facts, and require confirmation before saving or sending a counteroffer.
- **missing:** A commitment-cost model that maps a proposed promise to calendar capacity and existing obligations without pretending to know unavailable context; A pendant interaction for quick accept/correct/discard of the extracted promise; A reviewable counteroffer composer with explicit source and uncertainty labels


## Changes it proposed to its own stack

### `integration` — Add an event-joiner that correlates Calendar event boundaries, pendant button/voice events, and Mac/browser activity into short-lived 'life episodes'. On meeting end it opens a 90-second debrief window; it attaches only the selected event's attendees, tabs, notes, and mail, then emits a review packet with per-claim citations and item-level accept/discard controls. Expire raw audio and unaccepted claims automatically.
- **owner gets:** The owner can finish a meeting, press once, speak naturally, and receive dependable follow-through instead of losing promises or reconstructing context later.
- effort: Medium-high: Calendar event hooks, pendant event transport, source scoping, evidence joins, review UI/audio queue, and retention tests.  ·  risk: False joins could attach the wrong meeting or expose unrelated private content. Recover by requiring the owner to confirm the event title, showing source boundaries, and making discard/wipe immediate; if any source is unavailable, label the packet incomplete rather than guessing.
- cost: Low recurring API cost for event joins; approximately $0.02–$0.15 per accepted packet depending on transcript and source volume. Storage cost falls with aggressive expiration.  ·  latency: A small local/relay event join is immediate; packet generation takes 1–3 minutes after debrief.
- security: Improves least-privilege scoping but creates a sensitive temporary bundle. Encrypt in transit/at rest, retain raw audio briefly, attach provenance to every claim, and never send or create external actions automatically.
- depends on: A pendant-to-relay event path while USB-connected today and LTE later; Calendar event boundary observation on the Mac; The requested audio delivery acknowledgement and review-queue primitives; An owner-controlled retention policy


## What it asked for

_Nothing._
## Its own summary

This round produced four distinct owner-facing capabilities: (1) after a meeting, a pendant debrief becomes a cited follow-through packet with drafts/reminders held for review; (2) a pre-meeting relationship card drawn only from approved notes and correspondence; (3) an “I’m stuck” mode that inspects the scoped active context, proposes one small next move, and executes only the reversible part; and (4) an integration change joining Calendar boundaries, pendant events, and Mac/browser activity into short-lived, evidence-backed life episodes. I still need the connective pieces rather than more endpoint plumbing: Calendar-to-pendant event triggers, a scoped source/attendee resolver, item-level review and audio acknowledgement, and strict temporary-bundle retention/deletion. The USB-connected pendant is testable now; LTE should remain an optional later transport.

**Biggest unknown:** Whether the current Calendar observation and pendant event stream expose reliable event start/end and button/voice timestamps; without that, the meeting aftermath trigger must be manually initiated.

