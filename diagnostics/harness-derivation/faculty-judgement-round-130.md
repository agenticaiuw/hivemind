# Harness derivation — faculty-judgement — round 130

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Before I submit this form or send this message, tell me exactly what personal information it would reveal, remove anything unnecessary, and let me approve the smallest safe version.”"
- **useful because:** Logged-in sites routinely ask for more data than a task needs. This would turn the pendant into a practical privacy advocate: inspect the actual destination, compare fields with the user's stated goal, redact optional/sensitive data, and make consent understandable before an irreversible action.
- **path:** browser-extension → mac-vision → mac-planner → relay-realtime → pendant → unified
- **model tier:** Use the cheaper background/planner tier to inventory fields and classify necessity; reserve realtime only for the short spoken explanation and approval dialogue.
- **latency:** 10–20 seconds to inspect and prepare; under 2 seconds for the spoken risk summary after preparation.
- **cost:** Roughly $0.02–$0.10 per preparation, dominated by page extraction and one classification pass; negligible cost for local field diffing.
- **security:** Page contents and proposed field values leave the Mac only to the authenticated relay/model path. Never transmit secrets not needed for classification; mask values in logs; require explicit confirmation for sensitive fields (identity, financial, health, credentials) and for final submit. Existing owner policy already requires confirmation before sending mail or buying.
- **missing:** A privacy-specific field classifier and data-minimization planner; Browser extraction of form labels, required/optional state, destination, and current values with provenance; A reversible redaction/edit staging layer and a spoken approval packet

### "“I’m about to leave. Based on what changed today, my calendar, and my open browser work, give me a five-minute departure plan: what I must take, who needs an update, and the one thing I should do first.”"
- **useful because:** The owner gets a decision-ready transition rather than another inbox summary. It joins physical presence (the worn pendant), time/place constraints on the Mac, and unfinished authenticated web work into one small plan, reducing forgotten items and abandoned tasks at the exact moment plans change.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-vision → unified
- **model tier:** Background planner assembles evidence and ranks actions; realtime model only handles the owner's brief spoken departure request and clarifying question.
- **latency:** Prepare in 5–15 seconds; answer in one short spoken turn, with optional detail on demand.
- **cost:** About $0.03–$0.12 per plan, dominated by cross-source extraction; local calendar/time arithmetic is effectively free.
- **security:** Use only explicitly authorized calendar, reminders, and currently open browser tabs; do not infer or announce location to others. Keep private-page snippets out of durable logs. No external messages or calendar edits without confirmation.
- **missing:** A departure trigger (button, geofence, or explicit voice intent) and a local packing/context signal; Cross-source temporal/spatial constraint resolver (calendar, reminders, active tabs, recent notes); A compact spoken plan format with evidence links and stale-data warnings

### "“When I say ‘I can’t deal with this right now,’ put the current problem into a safe holding pattern: capture what it is, preserve the exact browser/Mac state, suggest a next reminder time, and give me one sentence I can use to explain the delay.”"
- **useful because:** Overwhelm is a real failure mode that ordinary task managers ignore. The pendant can provide an immediate low-friction escape while the Mac/browser preserve the evidence needed to resume, and the relay schedules a humane follow-up instead of losing the thread or forcing a rushed decision.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-terminal → unified
- **model tier:** Realtime handles the empathetic one-sentence response and captures the owner's words; a cheaper background planner packages state, drafts the delay message, and schedules the follow-up.
- **latency:** Acknowledge and capture in under 2 seconds; state snapshot and draft within 15 seconds; no blocking while the owner walks away.
- **cost:** $0.01–$0.08 per invocation; model cost is mostly the optional state summary, while local snapshots and reminder creation are cheap.
- **security:** Do not send the drafted explanation automatically. Preserve only the tabs/files relevant to the named problem, encrypt sensitive snapshots, set a short retention, and show exactly what will be retained. Cancel or delete must be available from a pendant gesture or voice command.
- **missing:** A durable interruption/holding record tying voice, active project, browser session, and pending jobs together; Atomic browser/Mac checkpoint and restore metadata (not just screenshots); A follow-up scheduling and draft-message generator with explicit retention/deletion controls

### "“The meeting just ended. Turn what happened into the smallest useful follow-up: extract decisions and owners from my notes, compare them with the open threads in Mail and browser, draft the needed messages and reminders, and show me the send list.”"
- **useful because:** Most meeting assistants stop at a transcript. This closes the loop without silently contacting anyone: the pendant gives a spoken summary, the Mac reconciles notes/calendar, and the browser finds the authoritative project state so follow-ups are complete rather than generic.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-terminal → unified
- **model tier:** Use a cheap background planner for extraction and reconciliation; realtime is only for the owner's brief request and approval of the final send list.
- **latency:** Draft within 30 seconds for a normal meeting; speak a three-item result immediately, with detailed evidence available afterward.
- **cost:** $0.05–$0.20 per meeting, dominated by transcript/note and private-page reconciliation; local reminder creation is negligible.
- **security:** Treat meeting notes and drafts as sensitive. Never send or create external commitments automatically; display recipients, claims, and source snippets, and require one explicit approval. Expire raw transcript access after the drafts are accepted.
- **missing:** Meeting boundary and note-source resolver across Calendar, Notes, Mail, and browser tabs; Decision/owner/date extraction with contradiction detection; A grouped draft-and-reminder review screen and spoken approval protocol

### "“Coordinate this with everyone without making me the middleman: find a time that works from the information I’m allowed to use, prepare each person a different message that reveals only what they need to know, and show me the complete coordination plan before anything is sent.”"
- **useful because:** Scheduling a real group event currently forces the owner to manually reconcile calendars, time zones, constraints, and privacy. This would let the pendant capture the goal conversationally, the Mac and authenticated browser gather only authorized availability, and the relay produce a minimal-disclosure plan and tailored drafts without exposing anyone’s private details to the group or sending prematurely.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-vision → unified
- **model tier:** Use a background planner for availability intersection, time-zone arithmetic, and message generation; use realtime only to clarify constraints and present the short approval summary.
- **latency:** 30–60 seconds for a small group; immediate spoken acknowledgement and a concise proposed slot while the full plan is prepared asynchronously.
- **cost:** Approximately $0.05–$0.30 per coordination round, dominated by reading private calendar/mail sources and resolving conflicts; local time-zone computation is negligible.
- **security:** Availability, identities, and message drafts are sensitive. Use per-person disclosure policies, never reveal one person’s calendar details to another, mask private event titles, require approval before every outbound message or calendar hold, and expire raw availability after the coordination closes.
- **missing:** A multi-party availability resolver spanning private Calendar, Mail, and authenticated web sources; Per-recipient disclosure policy and message compiler that can prove why each field is included; A staged coordination transaction supporting approval, partial acceptance, counteroffers, cancellation, and full audit/undo

### "“Translate this conversation as we go, quietly: tell me in my ear what the other person said, and give me a short translation of my reply before I say it.”"
- **useful because:** A wearable translator would help the owner participate in travel, appointments, and everyday conversations without handing a phone back and forth. The pendant supplies the always-present microphone and private audio, realtime relay handles low-latency turn taking, and the Mac/browser can supply terminology or document context when explicitly requested.
- **path:** pendant → audio → relay-realtime → mac-planner → browser-extension → unified
- **model tier:** Realtime speech translation is appropriate for the low-latency dialogue; a cheaper model can build a temporary domain glossary from an explicitly selected document or webpage. Never use background processing for live microphone audio.
- **latency:** Target 500–1,500 ms from a completed utterance to the whispered translation; allow interruption and a visible/physical mute state.
- **cost:** Roughly $0.01–$0.08 per conversational minute depending on audio-token pricing; bandwidth and continuous transcription dominate.
- **security:** Microphone audio is highly sensitive. Make capture visibly and physically controllable, default to no recording or retention, encrypt transport, disclose when cloud translation is active, and require an explicit mode switch before using a private browser document as context. Translation must never send messages or speak aloud to the other party without confirmation.
- **missing:** Verified bidirectional 24 kHz audio capture/playback and jitter buffering on the pendant/bridge; A streaming speech-to-speech translation session with barge-in, language detection, and turn boundaries; A local mute/offline fallback and clear recording/translation indicator on the wearable; Optional terminology context handoff from a selected Mac/browser page


## Changes it proposed to its own stack

### `integration` — Add a post-meeting closure pipeline: when a Calendar event ends, collect only the linked Notes/Mail/browser evidence, extract decisions/owners/deadlines, reconcile against existing reminders and project entities, and create a review bundle containing drafts, proposed reminders, contradictions, and source citations. Keep all writes staged until the owner approves the bundle from voice or Mac.
- **owner gets:** They leave every meeting with an actionable, trustworthy follow-up package instead of a vague transcript and a pile of forgotten promises.
- effort: High: Calendar/Notes/Mail correlation, browser session provenance, entity reconciliation, staged mutation UI, and voice approval.  ·  risk: Wrongly attributing an owner or deadline could create embarrassing drafts or reminders; mitigate with source quotes, confidence thresholds, no auto-send, and undo for approved writes.
- cost: About $0.05–$0.20 per meeting for extraction/reconciliation; storage grows with short-lived source references, not raw audio.  ·  latency: 30 seconds or less for ordinary meetings; processing runs asynchronously so the owner is not blocked.
- security: Private notes and mail are processed; redact unrelated participants/content, encrypt bundles, and expire raw evidence after acceptance or a short TTL.
- depends on: A Calendar event-to-source linking convention; Staged multi-action approval/commit primitive across reminders and drafts; Reliable Notes/Mail read routes and browser tab provenance

### `context` — Introduce a 'claim ledger' for owner-facing briefs: every asserted decision, deadline, or obligation must carry an immutable source pointer, extraction timestamp, confidence, and an explicit state (observed, inferred, owner-confirmed, completed, disputed). Briefs should refuse to present inferred claims as facts and surface conflicts as questions.
- **owner gets:** They can trust a short spoken brief without having to remember whether it came from an actual message or an AI guess, and can correct one bad fact without poisoning future plans.
- effort: Medium-high: typed persistence, source adapters, conflict resolution, and changes to briefing/research/pipeline rendering.  ·  risk: Over-cautious briefs may ask too many questions; use confidence and freshness thresholds, allow the owner to confirm or dismiss claims by voice, and preserve an audit trail.
- cost: Small per-claim storage and one cheap normalization pass; saves expensive model context by reusing compact claims instead of replaying entire pages.  ·  latency: Adds milliseconds for local lookup and a few seconds only when sources need reconciliation.
- security: Source pointers may reveal sensitive URLs or message IDs; encrypt them, project only the minimum snippet, and support per-claim deletion.
- depends on: A durable typed context projection service; Source adapters that return stable citations for Mail/Calendar/Notes/browser; Briefing and spoken interaction support for confirm/dispute/delete

### `hardware` — Add a physically latching microphone-disconnect switch to the pendant audio path, with a high-visibility mechanical indicator and a separate low-power haptic/LED state. The switch must sever mic power or the ADC input before firmware, survive resets and USB reconnects, and expose its state to the relay when re-enabled. Add a short local chime/haptic on transition, but no software path may override the off position.
- **owner gets:** They can wear an always-listening assistant in public, at work, or near private conversations with confidence that a compromised process, bug, or cloud outage cannot capture audio while the switch is off.
- effort: Medium hardware/firmware revision: insert a latching analog or load-switch stage, route state sensing to an available GPIO, revise enclosure, and add automated tests for reset/USB/radio reconnect behavior.  ·  risk: A damaged switch or false state could make the pendant appear muted when it is not, or make voice interaction unavailable. Use a fail-closed electrical design, a visible indicator powered independently of the application MCU, and a startup self-test that refuses to claim listening when state is unknown.
- cost: Approximately $1–$4 in components and enclosure changes at prototype quantity; under 1 mA additional indicator/sense draw when active, essentially zero when off.  ·  latency: No meaningful online latency; local mute takes effect electrically within milliseconds.
- security: Strongly reduces microphone-surveillance risk and gives the owner a trustworthy local boundary; the relay must treat muted state as authoritative and discard any queued audio rather than replaying it.
- depends on: Confirm available pendant GPIO/audio power path and enclosure/button layout; Verified end-to-end audio pipeline so the reported hardware state is tested rather than inferred; Firmware protocol field for physical-mute state and a relay policy that refuses audio capture while muted


## What it asked for

_Nothing._
## Its own summary

Round 130 produced five owner-facing/system proposals. The strongest is a privacy firewall for every browser form or outgoing message: inspect the real destination, identify unnecessary/sensitive fields, stage the smallest safe version, and require approval. I also proposed a departure-plan capability joining pendant, calendar, unfinished browser work, and recent changes; an overwhelm holding-pattern handoff that preserves resumable Mac/browser state; post-meeting closure that turns decisions into cited drafts/reminders; and a claim ledger so briefs distinguish observed facts from inference. The implementation changes include a staged post-meeting pipeline and provenance/confidence states for every brief claim.

**Biggest unknown:** The collective still needs the missing primitives rather than more route wiring: a durable cross-source evidence/claim store with source citations and expiry; atomic checkpoint/restore for Mac plus authenticated browser sessions; and a staged multi-action approval transaction that can be approved by voice and undone. Accessibility remains unavailable, so GUI-only inspection/action cannot be assumed. The pendant is physically testable over USB, but LTE registration and reliable end-to-end 24 kHz audio acceptance remain unverified.

