# Harness derivation — faculty-judgement — round 126

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“When a meeting ends, ask me what I actually decided, turn my answer into the right notes and follow-ups, draft any messages, and check back only if a commitment is still unresolved.”"
- **useful because:** Meetings currently evaporate into vague memory. This closes the loop from calendar event to durable decision, assigned follow-up, and later verification without making the owner operate a task system.
- **path:** relay-realtime → pendant → mac-planner → browser-extension → relay
- **model tier:** Realtime for the 10-second spoken debrief; background model for extracting decisions, filing notes, drafting follow-ups, and later checking status.
- **latency:** Prompt within 2 minutes of calendar end; spoken debrief under 3 seconds; filing/drafting under 60 seconds; follow-up checks asynchronous.
- **cost:** ~$0.01–$0.05 per meeting, dominated by transcription and background extraction; zero-cost local calendar event detection.
- **security:** Meeting audio should be transient and deleted after extraction; drafts never send without confirmation; private attendee and note data stays on the Mac/relay account.
- **missing:** calendar-end event hook; a post-meeting audio capture/debrief route; decision-to-note/task compiler with provenance; follow-up watcher that understands completion evidence

### "“I just agreed to something—save the last minute as a private, sourced note, tell me what commitments you found, and let me correct them before you create reminders or drafts.”"
- **useful because:** People remember that a commitment happened but not its exact wording. A wearable-triggered rewind makes the system useful in the moment, while explicit review prevents false commitments and avoids storing entire conversations.
- **path:** pendant → relay-realtime → relay → mac-planner
- **model tier:** Realtime for the short rewind transcription and confirmation; cheaper background model for structured extraction and linking to existing notes/calendar.
- **latency:** Wake on a button or phrase, return a transcript/commitment candidates in 5 seconds, then file approved items asynchronously.
- **cost:** ~$0.01–$0.03 per capture, dominated by speech transcription; local ring-buffer extraction minimizes upload volume.
- **security:** Never upload or retain the rolling audio unless the owner invokes save; show exactly what excerpt and derived fields will persist; third-party speech requires an audible/private-mode indicator.
- **missing:** bounded local audio ring buffer and save marker; timestamped source excerpt storage; owner correction/approval interaction on pendant; commitment extraction and duplicate detection

### "“Before I commit to a purchase, booking, or cancellation, compare the logged-in options, check my calendar and existing commitments, explain the real trade-offs, and hold the best reversible draft until I approve.”"
- **useful because:** The expensive part of personal admin is not clicking—it is noticing conflicts, hidden cancellation terms, and timing trade-offs across accounts. This gives the owner a decision, not an unexamined transaction.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → relay
- **model tier:** Background model gathers and normalizes options; realtime model only answers the owner’s clarifying questions and reads the final concise comparison.
- **latency:** Initial comparison in 2–5 minutes; spoken summary under 30 seconds; no irreversible submission without explicit approval.
- **cost:** ~$0.05–$0.30 per comparison, dominated by authenticated page extraction and model synthesis; reuse cached page evidence where fresh.
- **security:** Private account pages and calendar data leave the browser/Mac only for this job; mask payment and credential fields; drafts are isolated and expire; booking/cancellation always requires confirmation.
- **missing:** cross-account option normalization schema; calendar/commitment conflict evaluator; terms and cancellation extraction with citations; transaction draft sandbox with expiry and approval checkpoint

### "“Before I say yes to this invitation or request, tell me the true time, money, and attention cost against my existing commitments, then give me a one-sentence accept, decline, or counteroffer I can approve.”"
- **useful because:** The owner needs help deciding before commitments become obligations. It combines calendar reality, travel time, pending work, and account context rather than treating a request as an isolated message.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → relay
- **model tier:** Background model computes the trade-off and drafts alternatives; realtime model gives the brief spoken recommendation and handles clarification.
- **latency:** Under 20 seconds for a spoken recommendation when context is already cached; under 2 minutes when browser/account evidence must be fetched.
- **cost:** ~$0.02–$0.10 per decision, dominated by authenticated evidence extraction and synthesis.
- **security:** Private calendar, messages, and task data are combined only for this decision; never send a response automatically; expose the evidence behind the recommendation and let the owner discard it.
- **missing:** cross-source attention-cost model; invitation/request intent extraction; travel and preparation-time estimator; staged counteroffer/response composer

### "“Read this message or draft before I send it as the other person would: point out ambiguity, accidental commitments, privacy leaks, and likely emotional impact, then show me two safer rewrites without sending anything.”"
- **useful because:** The owner can avoid avoidable misunderstandings and oversharing at the exact moment they matter. This is not merely a send gate: it gives recipient-perspective critique and alternatives while preserving the owner's voice.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → relay
- **model tier:** Realtime model for a fast spoken critique; background model for nuanced recipient-perspective analysis when the message is long or high stakes.
- **latency:** 5 seconds for short messages, 30 seconds for long messages; no outbound action until explicit approval.
- **cost:** ~$0.01–$0.08 per review, mostly proportional to message length.
- **security:** Message text is highly sensitive; process in the authenticated local context where possible, retain no copy by default, redact secrets, and never infer or reveal private recipient data.
- **missing:** send-intent interception across Mail/browser; recipient-perspective risk taxonomy; local redaction and ephemeral review buffer; side-by-side rewrite presentation and approval

### "“When I tell you I am overloaded, find the smallest set of changes that makes today survivable: defer or reschedule reversible items, prepare concise decline messages, and leave me with one next action on the pendant.”"
- **useful because:** In overload, a long task list is itself a failure. The hive can see commitments across calendar, mail, browser, and Mac, make reversible relief moves, and reduce the owner's cognitive load to one safe next step.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → relay
- **model tier:** Realtime model handles the owner's brief distress statement and chooses the immediate next step; background model performs conflict analysis and prepares reversible changes.
- **latency:** A calming one-sentence response within 3 seconds; relief plan within 60 seconds; changes staged for approval unless explicitly pre-authorized.
- **cost:** ~$0.03–$0.15 per overload episode, dominated by cross-source analysis and draft generation.
- **security:** Overload is sensitive personal data; do not diagnose or share it, preserve original appointments/messages, show every proposed change, and require confirmation for cancellations or external replies.
- **missing:** overload intent trigger and quiet interaction mode; cross-source obligation compression model; reversible rescheduling/defer queue; single-next-action delivery and acknowledgement


## Changes it proposed to its own stack

### `integration` — Add a meeting-close coordinator: subscribe to Calendar event end, open a 90-second private debrief window on relay, accept a pendant button/phrase, then fan out one typed decision packet to Notes, reminders, browser drafts, and a durable follow-up watch. Require owner confirmation for every extracted commitment and expire the packet after 24 hours.
- **owner gets:** The owner leaves a meeting with decisions captured and next steps ready instead of reconstructing them later or forgetting who promised what.
- effort: High: calendar event subscription, debrief state machine, typed packet schema, and adapters for Notes/reminders/browser drafts.  ·  risk: False extraction could create noisy reminders or embarrassing drafts; keep all outputs staged, show source excerpts, and support one-tap discard. If relay is down, retain only a local pending marker and retry.
- cost: Small relay storage and one background extraction per meeting; roughly $0.01–$0.05 per debrief.  ·  latency: A short prompt at meeting end; downstream filing can be asynchronous.
- security: Meeting-derived text is sensitive; encrypt at rest, short retention, and do not retain raw audio after transcript extraction.
- depends on: calendar-end event hook; timestamped audio/debrief capture; decision packet schema; approval and expiry semantics

### `integration` — Create a transaction comparison sandbox spanning authenticated browser tabs and Mac calendar: normalize candidate prices, dates, cancellation terms, and account state into cited evidence; run conflict and regret checks; generate an expiring draft transaction that cannot submit until a fresh spoken approval names the exact target and total.
- **owner gets:** Before spending money or cancelling something, the owner gets a clear comparison that accounts for their actual schedule and commitments—not just the first option the browser shows.
- effort: High: cross-tab extraction recipes, terms parser, calendar conflict model, evidence citations, and a hard approval gate in the browser executor.  ·  risk: Terms may be incomplete or stale; label unknowns, timestamp evidence, re-fetch immediately before approval, and never treat a draft as booked.
- cost: ~$0.05–$0.30 per comparison, mostly authenticated extraction and synthesis.  ·  latency: 2–5 minutes for comparison; final approval check under 30 seconds.
- security: Payment and credential fields must be redacted; private-page content is scoped to the job and drafts auto-delete on expiry.
- depends on: typed browser extraction results; calendar/commitment read interface; transaction draft sandbox; fresh-evidence approval gate

### `interaction` — Add a pendant-native 'save the last minute' gesture that marks the local audio ring buffer without uploading it by default. The relay then requests only the bounded excerpt, returns a transcript with highlighted candidate commitments and source timestamps, and waits for a spoken correction before persisting anything.
- **owner gets:** The owner can recover the exact wording of a promise while it is still fresh, without recording every conversation or opening an app.
- effort: Medium-high: firmware ring buffer/marker, UART protocol, relay upload handshake, transcript UI/voice confirmation, and retention enforcement.  ·  risk: Accidental capture or third-party privacy concerns; require deliberate gesture, audible/private-mode feedback, strict 60–90 second bounds, and automatic deletion on timeout.
- cost: Low device storage/RAM overhead; ~$0.01–$0.03 per approved excerpt for transcription.  ·  latency: 5 seconds to return candidate commitments; filing is asynchronous.
- security: Raw audio is ephemeral and encrypted in transit; only owner-approved transcript/excerpt persists with a short TTL.
- depends on: audio implementation truth; bounded ring-buffer firmware support; capture approval route; commitment extraction and correction flow


## What it asked for

_Nothing._
## Its own summary

Produced three new owner-facing capabilities and three implementation changes: post-meeting decision closure, deliberate last-minute commitment capture from the pendant, and cross-account transaction comparison with a hard approval gate. The key remaining gap is connective orchestration: calendar-end triggers, bounded audio capture/consent, typed decision packets, evidence freshness, and expiring staged drafts. I did not re-request denied macOS TCC permissions or pending tools.

**Biggest unknown:** Whether the live audio/firmware stack can expose a bounded local ring buffer and explicit save marker without disrupting the owner's current 24 kHz audio path; that determines whether the commitment-capture capability can run on the physically connected pendant today.

