# Harness derivation — mac-planner — round 86

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **granted read adapters** — The newly granted mac_read_sources and mac_readonly_inspect tools are schemas without implementations in this round; every attempted calendar/mail and Mac inspection call returned the same schema-only error. They cannot yet provide live evidence for meeting continuity.
  - evidence: Five parallel calls in Round 86 returned: "This tool was granted a schema but has no implementation yet. Report what you would have done with it."

## Capabilities it proposed

### "“Before my next meeting, get me ready; after it ends, leave me the follow-ups.”"
- **useful because:** This goes beyond a static meeting brief: the always-awake relay joins calendar timing with private Mail and authenticated browser context, the Mac assembles local files/notes, and the pendant delivers a short pre-meeting audio cue plus captures a post-meeting follow-up request. It turns a meeting into a bounded before/after workflow without sending messages or submitting forms.
- **path:** relay-realtime → mac-planner → browser-extension → mac-vision → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Background/scheduled work uses a cheaper model for calendar/mail/browser extraction and deduplication; realtime is used only for the owner's explicit pendant request and a concise audio handoff.
- **latency:** Pre-meeting packet ready 10 minutes before start; 5–15 seconds for the spoken summary on demand; post-meeting draft within 2 minutes after the owner taps the pendant or says “done.”
- **cost:** Roughly $0.01–$0.05 per meeting when browser extraction is needed, dominated by model summarization; negligible cost for calendar-only meetings. Audio synthesis and relay storage are secondary.
- **security:** Mail snippets, calendar attendees, local filenames, and authenticated-page excerpts leave the Mac only as a minimized, redacted evidence bundle. Never send mail, edit calendar, submit browser forms, or create external tasks automatically. Require explicit owner confirmation for any outbound follow-up; retain packet evidence briefly and delete it with the job.
- **missing:** A durable cross-surface meeting state machine keyed by event ID (preflight, in-progress, ended, follow-up); A real implementation of the newly granted mac_read_sources and mac_readonly_inspect adapters (both currently return schema-only errors); Browser watch/session reattachment and durable job runner still missing per chg-16bc5dee; A pendant-side event/button skill for “meeting ended / capture follow-up” that works when the Mac link is briefly unavailable; A relay audio queue that can deliver the generated pre-meeting and post-meeting clips reliably

### "“Only interrupt me when something is important enough to break my focus; otherwise queue it and catch me at the next good moment.”"
- **useful because:** Today the Mac, browser, relay, and pendant can each produce alerts or briefs, but none arbitrate them as one attention system. This would combine the owner’s live foreground app and calendar state with authenticated browser changes, Mail/Calendar urgency, and queued relay audio so the owner gets fewer interruptions and does not miss genuinely time-sensitive items.
- **path:** faculty-perception → mac-planner → browser-extension → relay-realtime → unified → faculty-judgement → faculty-action
- **model tier:** Use a cheap background classifier for deduplication, urgency, and quiet-window scheduling; reserve realtime for the one-sentence pendant interruption and owner replies.
- **latency:** Urgent events should be classified in under 30 seconds; nonurgent items should be grouped at the next calendar-aware attention window. The spoken interruption should begin within 2 seconds after the decision.
- **cost:** Approximately $0.005–$0.03 per event batch, dominated by classification and optional speech generation; most events should be handled with deterministic rules and no model call.
- **security:** Only send a minimized title, sender/domain, deadline, and evidence link to the relay/model; keep message bodies and private page contents on the Mac unless explicitly needed. Never auto-reply, submit, delete, or alter calendar entries. Provide a visible/audible reason for each interruption and a one-tap mute or defer control.
- **missing:** A shared attention ledger with event identity, urgency rationale, deduplication, expiry, and delivery state across Mac, browser, relay, and pendant; Live Mac foreground-app/activity and calendar-busy signals implemented as a read-only adapter; the granted inspection/read schemas currently have no implementation; Browser change events emitted into the same ledger rather than isolated page-watch results; A pendant-local defer/mute/urgent override protocol that survives a dropped link; A relay scheduler that can select the next delivery window and collapse multiple audio items into one short digest


## Changes it proposed to its own stack

### `integration` — Add a durable Meeting Continuity Orchestrator keyed by Calendar event ID. It schedules a preflight job, fans out bounded reads from Calendar/Mail/local workspace and the authenticated browser, stores source-cited packet sections and a redacted digest, emits a short audio item, then transitions on event end or a pendant “done” signal into a follow-up draft job. Persist idempotent checkpoints and receipts so a Mac sleep, relay restart, or duplicate trigger cannot create duplicate drafts. Keep outbound mutations as explicit draft-only outputs.
- **owner gets:** The owner gets one dependable “ready me / wrap this up” experience instead of separate calendar, browser, notes, and audio features that each work only when manually invoked.
- effort: Medium-high: a server-side state machine and scheduler, Mac read adapter implementation, browser job persistence/reattachment, and a small pendant event protocol; most extraction and speech primitives already exist.  ·  risk: Wrong event matching or stale browser content could produce an irrelevant packet; mitigate with event-ID binding, freshness timestamps, source links, confidence labels, and a “no packet” fallback. Duplicate triggers are handled by idempotency keys. Outbound actions remain drafts and require explicit confirmation.
- cost: About $0.01–$0.05 per meeting for background summarization/browser extraction; storage is small redacted JSON plus short audio with TTL. No continuous realtime model spend.  ·  latency: Preflight runs asynchronously and should be ready 10 minutes before the event; post-meeting draft target is under 2 minutes. No impact on normal pendant conversation.
- security: Private calendar/mail/browser evidence is minimized and redacted before relay persistence; authenticated pages are read only. No email/calendar/browser submission without owner confirmation; packet/audio retention should default to 24 hours.
- depends on: Implementation (not just schemas) for mac_read_sources and mac_readonly_inspect; Durable browser job runner and result stream (chg-16bc5dee remaining gap); A pendant offline-safe meeting-ended/follow-up capture event; Relay audio queue with retry and expiry

### `interaction` — Create a cross-surface Attention Ledger and delivery arbiter. Normalize every candidate interruption (mail, calendar changes, browser watches, Mac jobs, relay jobs) into an event with source evidence, urgency, deadline, confidence, duplicate keys, expiry, and delivery history. Join it with current activity/meeting state and owner-set quiet windows, then choose one channel (pendant audio, Mac notification, queued digest) or defer. Add a pendant-local override: urgent-only, mute, and deliver-now, with local state replayed when connectivity returns.
- **owner gets:** The owner can stay focused without manually silencing several agents, while time-critical changes still reach them through the one device they are wearing. Deferred information arrives once, grouped and explained, rather than as repeated alerts.
- effort: High integration effort: event schema and durable ledger, adapters from existing job/browser/briefing systems, deterministic policy plus lightweight ranking, relay scheduler, and a small offline pendant state machine.  ·  risk: Bad urgency ranking could suppress something important or interrupt unnecessarily. Mitigate with conservative deadlines/sender rules, visible rationale, expiry, an urgent override, replayable receipts, and a daily audit showing what was deferred. Recovery is ledger replay after restart or link loss.
- cost: Low ongoing storage (small event records with short TTL); roughly $0.005–$0.03 per batch for ranking, with deterministic rules handling the common case. No continuous realtime inference.  ·  latency: Urgent candidates classified within 30 seconds; delivery under 2 seconds after classification. Digest generation is asynchronous and does not delay normal conversation.
- security: Ledger stores redacted metadata and hashes rather than full message/page bodies by default. Source content stays on the Mac/browser session unless the owner asks for detail. No outbound mutation is permitted by the arbiter.
- depends on: An implemented read-only Mac activity/calendar adapter rather than the currently schema-only grants; A common event-ingestion API for browser watches, Mac job receipts, Mail/Calendar reads, and relay jobs; Pendant-local mute/defer/urgent override with reconnect replay; Relay audio queue with deduplication, expiry, and retry


## What it asked for

_Nothing._
## Its own summary

Round 86 produced a new cross-surface Meeting Continuity capability and an integration change: event-ID keyed preflight and post-meeting workflow joining Calendar/Mail/local Mac files, authenticated browser context, relay scheduling/audio, and a pendant “done/capture follow-up” signal. It is explicitly draft-only for outbound actions, idempotent across sleep/restarts, and evidence/TTL bounded. I also verified that the newly granted mac_read_sources and mac_readonly_inspect are schema-only and unusable this round, and recorded that finding.

**Biggest unknown:** Whether the orchestrator can implement the granted read adapters and the missing durable browser runner/pendant event/audio retry pieces; without them, this remains a well-defined integration rather than an end-to-end working flow.

