# Harness derivation — mac-planner — round 224

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-accessibility-status** — Live ops snapshot now reports Accessibility and Screen Recording granted for AI Pendant Agent; all listed Automation grants are ready, browser extension online on Safari with 2 tabs, relay reachable, and Mac bridge online.
  - evidence: GET /ops/snapshot returned permissions.accessibility.trusted=true, screenRecording.granted=true, ready=true; browser online tabCount=2; relay reachable=true.

## Capabilities it proposed

### "“Use the page I’m on to get this ready to buy, tell me the total and delivery window on the pendant, and place it only after I say yes.”"
- **useful because:** This is the first genuinely end-to-end action the owner can delegate while away from the keyboard: the browser contributes the authenticated cart and checkout session, the relay turns it into a short spoken decision, and the Mac performs the final transaction and returns a receipt. It avoids making the owner copy addresses, totals, or order numbers into chat.
- **path:** pendant → relay → browser → mac-bridge
- **model tier:** Realtime only for the spoken summary and yes/no turn; use a cheaper background model to extract line items, detect fee/total changes, and format the receipt.
- **latency:** Read current page and summarize in 3–8 seconds; after spoken confirmation, submit in under 5 seconds and speak the order number when the receipt is visible.
- **cost:** About one short realtime turn plus a small text extraction call; browser and Mac actions dominate latency, not tokens.
- **security:** Never infer consent from silence or a prior conversation. Show merchant, items, total, delivery address nickname, and irreversible step in the spoken preview; require a fresh pendant confirmation tied to a hash of those fields. Do not send page body or payment details to the relay; browser-side redaction must pass only the normalized preview and receipt. Missing: a transaction-intent/confirmation digest carried from browser to Mac and a typed browser checkout/receipt command.
- **missing:** browser command to extract a redacted purchase preview and stable page-state digest; relay confirmation token bound to that digest and expiry; Mac executor action for submit-and-capture-receipt with idempotency key

### "“I just pressed remember—save exactly what I was looking at, where my Mac was focused, and the time as a private note I can search later.”"
- **useful because:** The pendant’s offline bookmark currently records only a moment. Adding the Mac/browser context at the moment the relay receives it turns an otherwise cryptic timestamp into a useful memory: URL/title, foreground app, and a short redacted snapshot are packaged into a durable note without requiring the owner to stop and dictate.
- **path:** pendant → relay → browser → mac-bridge
- **model tier:** Use a cheap background model to title and deduplicate the event; no realtime model is needed except an optional spoken acknowledgement.
- **latency:** Acknowledge the bookmark immediately; enrich it within 10 seconds when the Mac/browser are online. If either is offline, retain the bookmark and enrich later without losing event order.
- **cost:** Small summarization call per bookmark; storage and two read-only inspections dominate reliability rather than API cost.
- **security:** Capture only the active tab’s URL/title and foreground app by default, with page text opt-in and redaction before relay storage. Never snapshot password/payment fields. Bind enrichment to the pendant bookmark ID and timestamp so retries cannot create duplicates. Missing: a bookmark-enrichment route and a redacted browser page-context response.
- **missing:** relay endpoint accepting offline_moment_bookmark IDs and idempotently attaching context; browser read command returning active tab metadata plus redacted selected/page text; durable note writer that stores the owner-visible provenance and source timestamps

### "“Run the pendant-and-audio-bridge bench test now and give me one report saying whether capture, Opus, USB transport, playback, and Bluetooth all passed.”"
- **useful because:** The hardware is physically attached to this Mac today even though LTE registration is not available. A single spoken request should turn the accepted diagnostic fixture into a bounded test run, correlate both chips’ serial output, and leave a dated report that tells the owner whether the wearable is trustworthy before they put it on.
- **path:** pendant → mac-bridge → relay
- **model tier:** Use a cheap background model or deterministic parser for counters and pass/fail thresholds; use realtime only if the owner asks for an immediate spoken explanation.
- **latency:** Start within 2 seconds, run the fixed fixture for its measured duration, and return a report within 30 seconds. A failed or disconnected serial leg must be reported as unknown, never silently passed.
- **cost:** Near-zero model cost if thresholds are deterministic; Mac USB capture and report storage are the work.
- **security:** Only allow the fixed diagnostic commands and approved serial device paths; never transmit microphone content because the fixture is synthetic. Include firmware/build hashes, timestamps, and raw-counter excerpts in a local receipt, with a redacted summary sent to relay. Missing: the granted bounded USB read capability is not yet resolved in the live inventory, and no typed two-device capture/parse action or exit-code receipt exists.
- **missing:** resolved mac_usb_serial_diagnostics/list_ports plus bounded read for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; typed fixture trigger and deterministic parser for both serial streams; receipt schema containing command, exit status, firmware hash, thresholds, and artifact paths

### "“If I ask you to do something in the browser, keep watching the session; if the tab changes, extension disconnects, or the page goes stale, stop and tell me on the pendant instead of acting on an old screen.”"
- **useful because:** Authenticated browser state is the least visible and most dangerous surface. A short-lived lease makes a spoken plan safe against tab navigation, login expiry, extension restarts, and another person using the Mac. The relay can remain conversational while the browser and Mac enforce that the exact tab and page state are still the ones the owner approved.
- **path:** pendant → relay → browser → mac-bridge
- **model tier:** No realtime model for monitoring; deterministic hashes, heartbeats, and a cheap classifier for a human-readable failure reason. Realtime is used only to explain a stop when the owner asks.
- **latency:** Heartbeat every 2–5 seconds during an active plan; abort within one missed heartbeat or page-digest mismatch. Spoken stop notice within 2 seconds.
- **cost:** Negligible model cost; recurring browser heartbeats and a small relay state record dominate.
- **security:** Lease must be scoped to browser device, tab/window ID, URL origin, and a redacted DOM digest, with a short expiry and one-use action nonce. A stale or changed lease must fail closed, and no page contents beyond the digest/reason code should leave the browser. Missing: a browser lease/heartbeat state machine and executor checks that reject an expired or mismatched lease.
- **missing:** typed browser session lease create/renew/revoke route; page-state digest and tab identity in browser command results; Mac execute precondition that verifies lease before each mutating action; pendant alert payload for 'stopped because browser state changed'

### "“Handle the rescheduling for me: find a time that works for both calendars, draft the message in my voice, send it only when the other person’s details and the proposed time are exactly what you read back to me, then keep watching for their reply and update my calendar.”"
- **useful because:** Today the system can read local sources and drive a browser, but it cannot carry a real-world commitment across several asynchronous replies. This would turn the pendant into a delegate rather than a one-shot command interface: it negotiates ordinary scheduling while the owner is away, pauses at the one consequential decision, and closes the loop when the recipient answers.
- **path:** pendant → relay → mac-bridge → browser
- **model tier:** Use a cheap background model for calendar intersection, thread tracking, and extracting proposed times. Use realtime only for the short spoken approval turn and an exception that needs the owner's judgement.
- **latency:** Initial availability search and draft in under 15 seconds; outbound send after approval in under 5 seconds; reply watcher can run asynchronously and wake the pendant only for a changed commitment or ambiguity.
- **cost:** One small planning call per negotiation and inexpensive event-driven extraction per incoming reply; the dominant cost is durable state and polling/webhook delivery, not realtime inference.
- **security:** The draft must remain unsent until a fresh approval binds recipient identity, exact body hash, proposed time zone, and calendar mutation. Never invent availability or silently accept a counterproposal. Store only thread IDs and redacted extracts in the relay; keep full message content on the Mac/mail account. Missing: a durable negotiation state machine, outbound Mail/browser send primitive, approval digest, reply watcher, and calendar write with idempotency.
- **missing:** asynchronous delegation record with states draft, awaiting-approval, sent, counterproposal, resolved, expired; typed outbound message action that returns a provider message ID and immutable body hash; reply watcher across Mail and authenticated browser sessions with deduplication; calendar hold/update operation tied to the approved negotiation ID

### "“Make this safe to send: collect the document and the relevant browser/email material I’m referring to, remove secrets and private recipients, show me exactly what changed on the pendant, and leave a reviewable redacted package without sending it.”"
- **useful because:** The owner can currently create or move files and inspect sources, but cannot safely assemble a multi-source share packet with verifiable redaction. This would convert an ambiguous spoken reference into a staged artifact, preserving originals while making privacy review a concrete, bounded action instead of a manual scavenger hunt.
- **path:** pendant → relay → mac-bridge → browser
- **model tier:** Use a slower background model for entity/secret detection and cross-source relevance ranking; use realtime only to summarize the diff and answer a clarification about which recipient or document was intended.
- **latency:** Stage a small packet in 10–30 seconds; never send automatically. The owner gets a concise spoken diff and a local folder they can inspect before any outbound action.
- **cost:** One bounded extraction/redaction call per source set; local file staging and hashing dominate. No persistent page body needs to be sent to the relay.
- **security:** Originals are immutable and never overwritten. Redaction must be conservative: uncertain matches are highlighted, not silently removed. The relay receives hashes, classifications, and diff metadata by default; full content stays on the Mac. Missing: a content provenance graph, deterministic secret scanner, review manifest, and a sender that requires the approved manifest hash.
- **missing:** cross-source reference resolver for the owner's spoken 'this'; redaction engine for files, mail snippets, and browser content with locations and confidence; atomic review package containing originals' hashes, redacted outputs, and a machine-readable diff; outbound sender that accepts only an owner-approved package hash


## Changes it proposed to its own stack

### `hardware` — Add a small secure element to the next pendant revision, with a device-unique key and a physical confirmation input path. The relay sends a canonical action digest (recipient, amount, URL origin, calendar time, or message hash); the pendant displays/voices the digest, the owner confirms locally, and the secure element signs it. The Mac/browser refuses mutations whose digest is not signed or has expired.
- **owner gets:** The owner gets a trustworthy “yes” that cannot be forged by a compromised browser session, stale relay plan, or accidental replay. They can approve a purchase, message, or calendar change from the pendant without trusting that the screen still shows the same thing.
- effort: Moderate hardware spin and firmware/relay protocol work: secure-element selection and provisioning, signed-digest format, monotonic nonce/expiry handling, and verification in browser/Mac action paths.  ·  risk: Lost pendant requires revocation and re-pairing; a bad clock or lost nonce could reject valid actions. Recovery is a local re-pair ceremony with a recovery code, never silent key replacement. Prototype first with a software key and fault-injection tests, then enable hardware-backed verification.
- cost: Roughly $1–$4 in component and PCB cost per unit, negligible runtime API cost, and a few milliamps only during signing.  ·  latency: Approximately tens to hundreds of milliseconds for a signature; no perceptible impact on spoken confirmation.
- security: Substantially improves authorization integrity and replay resistance, but requires secure provisioning, revocation, and careful protection of spoken previews from leaking secrets.
- depends on: canonical cross-surface action digest shared by relay, browser, and Mac; typed executor precondition that verifies signature and expiry; owner-defined recovery/revocation flow


## What it asked for

_Nothing._
## Its own summary

Produced four new cross-surface capabilities: browser transaction execution with a confirmation digest, bookmark enrichment into a searchable private evidence note, a live USB-attached dual-chip audio bench report, and short-lived browser session leases that fail closed on tab/page changes. The strongest owner-facing capability is the browser lease plus spoken transaction flow: the pendant can approve only the exact authenticated page state, while the Mac executes and returns a receipt. Fresh discovery also established that Accessibility, Screen Recording, Automation, the browser extension, relay, and Mac bridge are all live now; this is a changed environment, not the previously blocked one. I told mac-terminal that the remaining bench gap is typed bounded serial capture, not a product USB link.

**Biggest unknown:** The live resolver still cannot provide a typed browser page inspection/lease primitive or accessibility_enabled inspection, even though /ops/snapshot reports the permissions as ready. For the hardware bench, mac_usb_serial_diagnostics/list_ports and a two-device bounded capture/parser with exit-code receipts are still absent or unresolved. Those are the concrete things I still need; no further owner permission is needed for Accessibility.

