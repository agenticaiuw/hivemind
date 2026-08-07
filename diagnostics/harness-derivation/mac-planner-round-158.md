# Harness derivation — mac-planner — round 158

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Save this for me as a source-backed packet I can pick up later.”"
- **useful because:** A spoken request from the pendant turns the current conversation plus the relevant authenticated browser tabs into a durable, human-readable packet on the Mac: concise conclusion, quoted evidence, links, timestamps, and explicit open questions. The owner can reopen it days later without reconstructing the research, while sensitive page content stays local and nothing is submitted.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → dashboard
- **model tier:** Use realtime only to understand the short voice request; use the cheaper background tier for extraction, deduplication, and packet composition.
- **latency:** Acknowledge on the pendant in under 1 second; finish the packet in 10–30 seconds and notify the owner when the folder is ready.
- **cost:** Low: one short realtime turn plus a background synthesis turn; dominant cost is extracting several authenticated tabs, not Mac file creation.
- **security:** Private tab text and the voice transcript leave the browser/pendant only to the relay for processing; redact secrets and cookies, preserve source URLs and hashes, and never send or submit forms. Creating a local folder is reversible by deleting it; no confirmation is needed under the owner's maximum-access policy.
- **missing:** A durable packet writer with deterministic filenames and source-snippet hashing; Browser extraction that returns citations and tab identity to the relay; A relay-to-Mac completion notification and packet index

### "“I’m heads-down for the next hour—hold everything except genuinely urgent things, and give me one digest when I’m done.”"
- **useful because:** The pendant becomes a physical attention switch rather than another notification channel. The relay classifies incoming work, the Mac enables a Focus mode and queues non-urgent browser/mail/calendar findings, and only a narrowly defined urgent event gets spoken through the pendant. At the end, the Mac opens one ranked digest with links and the reason each item was held.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Realtime handles the short command and urgent interrupt only; a cheaper background model batches and ranks the held items at the end of the window.
- **latency:** Focus mode and pendant acknowledgement under 2 seconds; urgent alerts under 5 seconds; end-of-window digest within 20 seconds.
- **cost:** Low-to-moderate: one realtime command, then a single batched ranking call; polling and OS Focus changes dominate implementation rather than tokens.
- **security:** The urgency classifier must default to silence for ambiguous items, expose why an item interrupted, and keep private mail/browser snippets local to the relay/Mac boundary. Changing Focus mode is reversible. No external reply or meeting decline is ever performed.
- **missing:** A relay attention lease with expiry and explicit urgent predicates; A Mac Focus-mode adapter plus a durable held-item queue; A pendant command/ack protocol that works while USB-tethered and later over LTE

### "“I’m back at my Mac—resume the task I was doing with the pendant.”"
- **useful because:** USB attachment is a concrete presence signal available now. The system finds the last incomplete task, reopens only the relevant Mac files and authenticated browser tabs, reads a compact checkpoint, and gives the owner the next safe step through the pendant instead of making them reconstruct context.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** Use a cheap background model to assemble the checkpoint and select relevant tabs/files; reserve realtime for the spoken acknowledgement and clarification if multiple tasks are unfinished.
- **latency:** Detect attachment and acknowledge within 2 seconds; restore the bounded workspace within 10 seconds.
- **cost:** Low: mostly local inspection and deterministic opens; one small background synthesis call when the checkpoint is stale.
- **security:** Never reopen arbitrary private tabs: restore only the tab/file IDs explicitly recorded in the checkpoint, redact checkpoint text in logs, and leave irreversible actions untouched. If identity or task is ambiguous, show choices rather than guessing.
- **missing:** A durable task checkpoint format that records last step, open resource IDs, and expiry; USB attach/detach events exposed to the Mac agent and relay; A bounded restore executor that can reopen browser tabs and files without submitting anything

### "“If I accept this meeting, what will it disrupt, and what is the least painful alternative?”"
- **useful because:** Instead of merely reporting calendar conflicts, the system simulates the consequences across the owner's calendar, recent mail commitments, and authenticated work pages: travel time, deadlines, focus blocks, and promised follow-ups. It returns a ranked set of alternatives without accepting, declining, or moving anything.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Realtime parses the question and gives the short spoken answer; a cheaper background model performs the multi-source constraint analysis.
- **latency:** Spoken acknowledgement under 1 second; full impact analysis within 15 seconds.
- **cost:** Moderate: calendar and mail reads are cheap, while authenticated-page extraction and cross-source reasoning dominate.
- **security:** Read-only by default. Private commitments remain within the authenticated relay/Mac path, with snippets minimized and source links shown. Any calendar mutation requires a separate explicit request.
- **missing:** A normalized time-and-commitment graph joining Calendar, Mail, and selected browser watches; Travel/availability inference with confidence and explanation; A planner response format that distinguishes facts from assumptions

### "“I think I left my pendant somewhere—lock down anything it can access and tell me the last trusted handoff.”"
- **useful because:** A lost wearable should not become a lost credential or an ambiguous privacy event. The relay marks the device untrusted, stops new audio delivery, revokes its active session, records the last confirmed Mac/relay contact, and gives the owner a recovery checklist. When the pendant returns, re-pairing is explicit and auditable.
- **path:** pendant → relay-realtime → mac-planner → dashboard
- **model tier:** Realtime handles the urgent spoken command; deterministic security logic performs revocation and status checks, with no expensive model required.
- **latency:** Disable delivery within 2 seconds and return a status within 5 seconds.
- **cost:** Very low per invocation; the main work is device/session-state implementation, not inference.
- **security:** This is intentionally fail-closed for audio and command delivery, but must not destroy locally queued captures. Keep encrypted quarantine data until the owner explicitly recovers or wipes it; expose every revoked session and device identifier.
- **missing:** Device-specific credentials and revocation state in the relay; A secure re-pair flow requiring a physical pendant gesture plus Mac presence; Last-contact and queued-data status reporting across relay and Mac

### "“These two pages disagree—tell me exactly what conflicts, which source should govern, and what I should do next.”"
- **useful because:** The owner gets a decision-quality answer rather than a blended summary. The system compares selected authenticated tabs or documents field by field, quotes the contradictory evidence, checks freshness and authority signals, and explicitly marks unresolved conflicts instead of silently choosing one.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → dashboard
- **model tier:** Use a cheaper background model for extraction, normalization, and contradiction detection; use realtime only to state the conclusion and ask for clarification when authority is genuinely ambiguous.
- **latency:** Identify the conflict in under 10 seconds and provide a cited answer within 30 seconds for up to six sources.
- **cost:** Moderate: DOM extraction and evidence normalization dominate; the final synthesis can use a lower-cost tier.
- **security:** Only inspect tabs the owner names or explicitly authorizes. Preserve URL, tab identity, timestamp, and quoted snippets; never infer authority from login status alone, and never mutate either page as part of reconciliation.
- **missing:** A typed claim/evidence representation with timestamps and source authority metadata; A contradiction detector that distinguishes true disagreement from different scopes or versions; A browser-to-pendant citation format that can be spoken concisely and reopened on the Mac


## Changes it proposed to its own stack

### `integration` — Ship a USB-tethered continuity lane for the physically connected nRF9160 pendant and ESP32 bridge: a small serial protocol with device/session IDs, monotonic capture sequence numbers, CRC, resumable chunk upload, and explicit ACKs. The Mac agent watches both known USB serial paths, forwards queued pendant events/audio to the relay when available, and writes a local failure receipt when the relay is down; reconnect resumes without duplicates.
- **owner gets:** The pendant is genuinely usable today even though LTE registration is absent: a button press, spoken capture, or queued reply will not disappear when the radio is unavailable, and reconnecting the cable will catch up automatically.
- effort: Medium: firmware framing and queue persistence, a Mac serial watcher, relay ingestion endpoint, and an end-to-end disconnect/reconnect test fixture.  ·  risk: Bad framing or duplicate replay could repeat audio/events. Bound the queue, validate CRC and sequence IDs, make ingestion idempotent, and expose a clear LED error pattern plus a local receipt; recovery is reconnect/resume or manual queue purge.
- cost: Negligible API cost; development-only firmware/storage work. No new hardware required because both USB serial links are live now.  ·  latency: Local ACK under 100 ms; relay delivery depends on network, but it no longer blocks capture.
- security: USB serial is treated as an authenticated local transport only while the pendant is physically attached; encrypt queued payloads at rest and do not log raw audio in serial diagnostics.
- depends on: A relay ingestion route that accepts idempotency keys and chunked payloads; A Mac background serial watcher with permission to access /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; A bounded on-device queue and replay semantics

### `hardware` — Add a small I2C secure element and a physical recovery contact/short-range pairing interface to the production pendant, using the currently free I2C bus. Bind device identity and session keys to the secure element; require a deliberate physical gesture while the pendant is near the owner's Mac for re-pairing after revocation.
- **owner gets:** If the pendant is lost, stolen, or replaced, the owner can disable it confidently without turning recovery into a support exercise. A recovered or replacement pendant can prove physical possession and rejoin without exposing long-lived credentials in firmware.
- effort: Medium hardware revision plus firmware key provisioning, relay device registry, and a Mac pairing utility. Validate recovery and wipe behavior before production enclosure design.  ·  risk: A failed secure-element or pairing flow could strand the owner. Keep a second enrolled recovery device or one-time recovery code, support factory reset with an unmistakable LED pattern, and test battery/USB behavior before rollout.
- cost: Roughly a few dollars per production unit plus PCB/enclosure changes; negligible runtime power when the secure element is idle.  ·  latency: Milliseconds for local challenge-response; no measurable impact on ordinary conversation.
- security: Substantially improves resistance to cloned firmware and stolen credentials. Key provisioning becomes a manufacturing responsibility and recovery codes become highly sensitive.
- depends on: Relay device registry with per-device revocation; Mac-side physical-presence pairing flow; A defined factory-reset and encrypted-queue recovery policy


## What it asked for

_Nothing._
