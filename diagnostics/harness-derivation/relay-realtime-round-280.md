# Harness derivation — relay-realtime — round 280

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If I’m offline, record a short bookmark about what I was doing and sync it later with the related job or note."
- **useful because:** It captures context at the moment it’s most useful—when the owner is away from the Mac—and stitches it to the right place later, reducing rework and forgetting.
- **path:** pendant → relay → mac-bridge → browser
- **model tier:** Realtime for capture; background tier on Mac/browser to reconcile and attach bookmarks to the right artifact.
- **latency:** Capture must be immediate; reconciliation can happen later when connectivity returns.
- **cost:** Small: short audio/text payload plus a matching pass over recent jobs/notes/tabs.
- **security:** Bookmarks may contain sensitive content; store encrypted at rest, and only attach to destinations the owner has access to. Confirm before attaching to external services.
- **missing:** A general typed OUTBOX item for bookmarks (not a new queue); A reconciliation service that matches a bookmark to a job/note/tab using context graph and recent activity

### "“While I’m away from my Mac, keep an eye on the exact document or webpage I was working on, and when I come back ask one clarifying question before continuing—then let me resume by saying ‘continue where I left off.’”"
- **useful because:** The owner can leave a half-finished task without losing the relevant artifact, state, or intent. This is more useful than a generic completion alert because it reconstructs the interrupted work and prevents an unattended Mac from acting on stale assumptions.
- **path:** pendant → relay → mac-planner → mac-vision → browser → dashboard
- **model tier:** Realtime handles the short spoken handoff and clarification; a cheaper background model builds a compact state checkpoint from Mac and browser evidence and resolves it when the owner returns.
- **latency:** Acknowledge the handoff in under 1 second; checkpoint in under 10 seconds; resume answer in under 3 seconds after the next button press.
- **cost:** About $0.01–$0.05 per handoff depending on screenshot/document summarization; background checkpointing dominates, while the realtime turn stays short.
- **security:** The checkpoint may contain document text, browser content, and window titles, so it must be encrypted and scoped to the owner/session. Never resume a mutation silently: report the proposed next step and require the existing owner policy/confirmation semantics for irreversible work.
- **missing:** A durable cross-surface task-checkpoint schema containing artifact identity, selection/cursor, visible UI state, last action, unresolved ambiguity, and freshness; Mac-vision support for a compact, redacted state capture rather than only action execution; A relay endpoint that binds the checkpoint to a voice session and resolves ‘continue where I left off’ against the freshest artifact; Pendant-side resume affordance that distinguishes a new request from resuming the last checkpoint

### "“Tell me, in one sentence, what changed across my Mac and my logged-in browser since the last time I checked, and include the source when you’re unsure.”"
- **useful because:** Today the owner must separately inspect apps, browser tabs, and relay jobs. A wearable answer that compares a known baseline with current evidence turns the system into an ambient change detector without pretending that a page being unavailable means nothing changed.
- **path:** pendant → relay → mac-planner → mac-vision → browser → dashboard
- **model tier:** Use a cheap background diff/index model for snapshots and a realtime model only to select the highest-value change and speak it. Vision is invoked only when semantic UI comparison is necessary.
- **latency:** Maintain snapshots opportunistically; answer within 2 seconds on request, with a hard 5-second fallback that says which source is unavailable.
- **cost:** Roughly $0.005–$0.03 per check; incremental snapshot hashing is cheap, while OCR/vision of changed regions dominates.
- **security:** Logged-in browser content and private Mac windows must remain on the owner’s machines or encrypted relay storage. Store hashes and redacted excerpts by default, disclose source/app/site in the spoken answer, and distinguish ‘unchanged’ from ‘could not inspect.’
- **missing:** A unified timestamped evidence ledger for Mac windows, browser pages, and relay jobs with provenance and availability state; Incremental screenshot/DOM diffing in the Mac and browser harnesses; A voice route that can query the ledger without re-sending the entire context every turn; Retention and redaction rules for private windows and authenticated pages

### "“I’m about to leave—make a private departure brief: what I need to remember, which delegated tasks are still running, and what will notify me; when I return, give me only exceptions.”"
- **useful because:** The pendant is worn away from the Mac, so the owner needs a reliable boundary between an attended work session and an unattended one. This converts scattered jobs, reminders, and pending alerts into a compact, spoken contract and avoids both notification flooding and silent failures.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Realtime creates the brief and speaks it; background workers reconcile job states, watches, and inbox items while the owner is away. Use a small summarizer for the return exception report.
- **latency:** Departure brief in under 2 seconds; return report in under 3 seconds, with asynchronous alerts for urgent failures.
- **cost:** About $0.005–$0.02 per departure/return cycle; reconciliation is mostly storage queries, with summarization dominating.
- **security:** The brief must not expose sensitive titles in an audible public setting; support a terse mode and redacted item names. It must never claim a task is safe merely because no status was received. Retain the owner’s explicit departure boundary and expire it at return or after a bounded interval.
- **missing:** A first-class away-session state with start/end and audible-safe verbosity; A reconciler that joins jobs, watches, routines, browser availability, and pendant inbox into one exception set; A durable delivery policy that routes only urgent exceptions while away and batches the rest; A return handshake so the relay knows the owner is present again, not merely that the pendant reconnected

### "“When a call comes in, let me handle it from the pendant: tell me who is calling, give me a private live summary of what they say, and let me dictate a reply without exposing the transcript to the room.”"
- **useful because:** The pendant is the one surface the owner has while away from the Mac. This would make phone calls manageable during walking, cooking, or hands-busy work instead of requiring the owner to retrieve a phone or stare at a mirrored screen.
- **path:** pendant → relay → mac-planner → mac-vision → ios → dashboard
- **model tier:** Use a low-latency realtime speech loop for caller transcription, private owner summaries, and dictated responses; use the Mac/iOS control tier for call state and audio routing. A cheaper model can produce a rolling structured transcript and extract decisions.
- **latency:** Identify the caller and offer answer/decline in under 1 second; summaries should trail speech by under 2 seconds; dictated response playback should begin within 1 second after the owner stops speaking.
- **cost:** Approximately $0.03–$0.15 per minute of active call, dominated by bidirectional speech recognition, summarization, and Opus audio relay.
- **security:** This handles highly sensitive third-party speech. Make recording/transcription visibly and audibly disclosed, retain nothing by default, encrypt transient buffers, and provide an immediate physical stop gesture. Never send a reply or change call state without an explicit owner utterance.
- **missing:** A Mac/iOS call-control and audio-bridge surface that can answer, decline, mute, and inject/play audio through iPhone Mirroring; Full-duplex relay audio separate from the existing press-to-talk turn model; A private-owner channel that mixes summaries into the pendant without sending them to the caller; Explicit transient-retention and disclosure controls for third-party conversation audio; A realtime call-session state machine spanning relay, Mac, iOS, and pendant


## What it asked for

_Nothing._
## Its own summary

Recorded four capabilities the owner cannot have today: resumable cross-device work handoffs, evidence-backed change summaries, departure/return exception briefs, and private pendant-mediated phone calls. The most useful is the resumable handoff: it turns an interrupted Mac/browser task into a durable, provenance-bound continuation rather than a completion notification. The required changes are new cross-surface state/checkpoint schemas and reconciliation, not another isolated route; the call feature additionally needs full-duplex private audio and iOS call control.

**Biggest unknown:** Whether the existing Mac/iOS harness can expose live call audio and call controls at all. The established action routes can launch/execute work and inspect state, but no observed route proves bidirectional phone-call media or a private monitoring channel. That capability needs explicit Mac/iOS bridge work, transient third-party-audio retention rules, and a relay session state machine.

