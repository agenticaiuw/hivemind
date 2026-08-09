# Harness derivation — faculty-action — round 161

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“I’m going into a meeting—keep me informed, but do not speak or interrupt unless it’s truly urgent, and give me one concise catch-up when I’m free.”"
- **useful because:** The worn device can adapt its behavior to the owner’s actual situation instead of blurting notifications at the worst moment. The Mac contributes calendar and active-app evidence, the browser contributes session context, and the relay remains able to queue urgent events while the pendant provides the immediate physical override and spoken catch-up.
- **path:** pendant → mac-planner → mac-vision → browser-extension → relay-realtime → unified
- **model tier:** Use a cheap background classifier for event urgency and meeting-state summaries; reserve realtime for the owner’s explicit voice command and the final short catch-up.
- **latency:** Entering quiet mode should take under 2 seconds after the pendant gesture; urgent-event decisions under 5 seconds; catch-up generated in under 10 seconds when requested.
- **cost:** About $0.01–$0.05 per meeting window, dominated by periodic summarization; no model call for simple calendar/app-state rules.
- **security:** Calendar titles, active-window names, and browser URLs may be sensitive. Keep raw context on the Mac, send only urgency labels and redacted summaries to relay; require explicit owner policy for what counts as urgent. The pendant override must not expose page contents.
- **missing:** A durable interruptibility policy object (mode, urgency threshold, expiry, catch-up format) shared by relay and Mac; A Mac read-only context snapshot route for calendar/call state and active app, with provenance; A relay queue operation that can atomically mark events spoken, deferred, or included in catch-up

### "“Watch this browser task while I do it: tell me only when the page meaningfully changes, and at the end give me a compact, verifiable record of what changed.”"
- **useful because:** Long-running browser work becomes observable without the owner narrating every step. The browser extension supplies authenticated page/session state, Mac-planner performs allowed actions, faculty-perception verifies each meaningful transition, and the relay/pendant reports only material changes rather than flooding the owner.
- **path:** browser-extension → mac-planner → mac-vision → faculty-perception → relay-realtime → pendant
- **model tier:** Use deterministic DOM/url diffs and a cheap background model for change significance; use realtime only for spoken alerts and owner questions.
- **latency:** Detect a material page change within 3 seconds; produce a final record within 15 seconds of task completion.
- **cost:** Roughly $0.005–$0.03 per monitored task, dominated by significance classification; verification and hashes are local/cheap.
- **security:** Do not transmit full page contents by default. Store field hashes and minimal redacted snippets; classify sensitive fields as private/secret and require explicit opt-in for evidence. Never infer success from executor receipts alone; every step needs fresh verifier provenance.
- **missing:** A watch-session route with operationId/attemptId/stepKey correlation and bounded polling; A browser diff projection that emits hashes and locator-level changes without secrets; A user-facing final receipt renderer shared by pendant speech and Mac journal

### "“When I say ‘save this for later’ while the pendant is plugged into my Mac, capture exactly what I was looking at and make it searchable by the words I spoke.”"
- **useful because:** This turns a fleeting spoken thought into a reliably linked research bookmark: the pendant supplies the intent and audio, the Mac supplies the active Safari tab and local timestamp, the browser bridge supplies URL/title, and the relay indexes it for later retrieval. It is useful today over USB even before LTE registration.
- **path:** pendant → mac-planner → browser-extension → mac-terminal → relay-realtime → unified
- **model tier:** Use realtime only to recognize the short command; use a cheaper background model to transcribe/tag and index the bookmark.
- **latency:** Acknowledge locally in under 500 ms; attach active-tab context within 3 seconds; searchable within 30 seconds.
- **cost:** About $0.01–$0.04 per bookmark, mostly transcription and embedding; local URL/title capture is negligible.
- **security:** URLs and spoken notes can contain secrets. Keep raw audio local until upload succeeds, encrypt queued records, redact query parameters by default, and require confirmation before sharing a bookmark externally. The existing typed OUTBOX should carry this as a record type rather than creating another spool.
- **missing:** A USB-local command path between the connected nRF9160/ESP32 devices and the Mac bridge; An active-tab snapshot route that returns URL/title plus observedAt and device/session provenance; A searchable bookmark index and retention/deletion controls

### "“What commitments did I make this week, and which ones are at risk?”"
- **useful because:** The owner gets a living commitment ledger rather than isolated reminders: the pendant supplies spoken promises and follow-up context, the Mac searches permitted Messages/Mail/Calendar artifacts, the browser contributes relevant authenticated work pages, and the relay reconciles them into commitments with sources, deadlines, confidence, and an explicit unknown state. No single node can build this honestly because the evidence is distributed across the wearable, Mac apps, browser sessions, and always-awake relay.
- **path:** pendant → mac-planner → mac-terminal → browser-extension → relay-realtime → faculty-perception → faculty-judgement → unified
- **model tier:** Use a cheaper background model to extract candidate commitments and deadlines; use faculty-judgement only to resolve conflicts and prioritize risk; realtime handles the owner’s query and concise spoken answer.
- **latency:** Return an initial answer in under 20 seconds; incremental ingestion may run in the background and must never block the wearable conversation.
- **cost:** $0.03–$0.15 per weekly reconciliation, dominated by summarizing local message/mail/calendar evidence; embeddings and hashes can remain local.
- **security:** Messages, mail, browser pages, and voice notes are highly sensitive. Keep raw evidence on the Mac/browser where possible, send only redacted claims plus provenance to relay, encrypt the ledger, support per-source opt-out and deletion, and never treat an inferred promise as fact without showing its source and confidence.
- **missing:** A commitment ledger schema with immutable claim IDs, source spans, deadline/owner fields, confidence, and supersession links; Mac-side read-only connectors for permitted Messages, Mail, Calendar, and voice-note artifacts that emit provenance without exporting full content; Browser evidence projection that returns only user-approved snippets or hashes; A reconciliation job and query route that distinguish observed commitment, inferred commitment, and unresolved ambiguity; A pendant response format for short lists plus a follow-up gesture/voice request for source details

### "“Make this safe to share with the client.”"
- **useful because:** The system would inspect the owner’s locally selected document, browser draft, and spoken intent together, identify secrets and private details, produce a redacted copy plus a human-readable change log, and stage it in the correct browser or Mac app without silently sending. The pendant gives the owner a compact summary and the Mac/browser perform the file and form work; perception verifies that the staged artifact matches the approved redaction.
- **path:** pendant → mac-planner → mac-vision → mac-terminal → browser-extension → faculty-perception → relay-realtime → unified
- **model tier:** A background model detects candidate sensitive spans and proposes transformations; realtime is used only to explain the redaction summary or answer the owner’s question. Deterministic validators check secrets, account numbers, and recipient domains.
- **latency:** Draft a redaction plan in under 15 seconds for a normal document; stage the revised artifact within 30 seconds; never send automatically.
- **cost:** $0.05–$0.30 per artifact, dominated by document parsing and sensitive-span review; local deterministic scans are negligible.
- **security:** The system handles exactly the data it is meant to protect. Keep originals local and immutable, encrypt the redacted derivative and mapping, never send originals to relay, scrub model logs, and require the existing physical approval latch for any external submission.
- **missing:** A local redaction engine supporting files, rich text, and browser fields with stable span locators; A secret/PII detector with false-positive review and recipient-aware policy; A staged-artifact diff route consumable by faculty-perception; A reversible local mapping store with explicit expiry and deletion; A safe-send integration that refuses if the verified staged content differs from the approved digest

### "“Find the cheapest trustworthy way to get this done, and tell me what you need from me.”"
- **useful because:** For a real goal—not a fixed app command—the relay can decompose options across the owner’s authenticated browser sessions, Mac applications, and wearable interaction, compare time/cost/privacy tradeoffs, and ask only for the missing authorization or information. It turns the hive into a constrained personal operator rather than a set of disconnected tools, while faculty-perception can mark which facts are observed versus assumed.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → mac-terminal → browser-extension → faculty-judgement → faculty-perception → unified
- **model tier:** Use a cheap planner for candidate enumeration and deterministic policy checks; invoke realtime only for clarification with the owner; use the stronger judgement tier for tradeoff ranking and irreversible-risk analysis.
- **latency:** Ask the first clarifying question within 5 seconds; produce an initial option table within 30 seconds; long research may continue asynchronously with a concise pendant update.
- **cost:** $0.05–$0.40 per goal depending on web research and number of authenticated sources; most Mac/browser inspection should be local.
- **security:** Options may expose financial, identity, or account data. Enforce source allowlists, redact secrets before relay, label estimates versus verified prices, and require owner confirmation before purchases, messages, or account changes. Preserve an evidence trail for every recommendation.
- **missing:** A goal contract schema for objective, constraints, budget, deadline, allowed sources, and forbidden actions; A multi-option planner that can call Mac/browser actions without committing side effects; A cost/time/privacy comparison receipt with provenance and uncertainty; A clarification protocol that presents one bounded question through the pendant and resumes the same goal; A policy-aware executor that turns the selected option into staged, verified steps


## Changes it proposed to its own stack

### `firmware` — Add a versioned, CRC-protected USB serial protocol for the physically connected nRF9160 pendant and ESP32 bridge: HELLO (stable device identity, firmware, boot counter, capabilities), framed request/response with request ID and monotonic sequence, ACK/NACK replay protection, and redacted receipts. Bind the Mac bridge to the exact serial identity and reject stale or replayed approval/action frames.
- **owner gets:** While the pendant is USB-attached today, commands and acknowledgements become trustworthy instead of ambiguous. The owner can safely use the pendant as a physical control and receive a truthful success/failure indication without confusing a dropped link, a reboot, or the wrong serial device for completion.
- effort: Medium: shared framing library, nRF9160 and ESP32 endpoints, Mac bridge binding, crash-safe sequence persistence, and integration tests with unplug/replug and reboot faults.  ·  risk: A framing bug could strand the device or reject valid commands. Keep a legacy read-only diagnostic mode, make protocol negotiation explicit, and never permit an unverified frame to execute an external action.
- cost: No API cost; a few KB of flash/RAM and negligible USB power overhead.  ·  latency: Adds roughly 1–10 ms framing overhead per USB message; retries improve effective latency under unplug/replug.
- security: Improves anti-replay and device-spoof resistance; raw payload logs must be redacted because action digests and approvals may be sensitive.
- depends on: A Mac bridge route that can open the two known USB serial identities; Existing physical_transaction_approval_latch semantics; A persistent boot/sequence counter in the existing pendant store


## What it asked for

_Nothing._
## Its own summary

Recorded three capabilities and one firmware change: meeting-aware interruption/catch-up mode; verified browser-task change watching with provenance; pendant “save this” contextual bookmark (flagged as close to an existing bookmark idea, so it should be merged rather than treated as a fourth mechanism); and a concrete CRC-framed, replay-resistant USB protocol for the currently connected nRF9160 and ESP32. I still need the missing connective surfaces: a durable interruptibility policy and event queue, browser watch/diff session correlation, active-tab snapshot provenance, and a Mac bridge endpoint bound to the two stable USB serial identities. I also notified faculty-perception and mac-terminal of the relevant integration work.

**Biggest unknown:** The owner’s preferred urgency policy for meeting mode and whether active-tab URLs/title may leave the Mac; until those are set, the system should default to conservative suppression and redacted/hash-only context.

