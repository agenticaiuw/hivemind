# Harness derivation — browser-extension — round 222

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“While I’m looking at this authenticated page, make me a private evidence card of the exact decision, deadline, and responsible person I’m seeing, then put a reminder on my Mac—but do not send or submit anything.”"
- **useful because:** The owner can turn a moment of browsing into a trustworthy follow-up without copying text between devices. Safari supplies session-bound context, the model extracts only the requested commitments, the Mac creates a reversible reminder, and the pendant can read the resulting card later. This is not generic web search: it preserves page URL and evidence provenance while acting on the owner’s authenticated view.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Cheap structured extraction model for the page and deadline; realtime model only to clarify ambiguous wording. Use the Mac action tier for reminder creation, not the expensive conversational model.
- **latency:** Extract and present a preview in 5–15 seconds; reminder creation within another 2 seconds after the owner confirms the extracted fields. Never submit forms or send messages in this flow.
- **cost:** About $0.01–$0.05 per card, dominated by page extraction and one structured extraction call. Reminder creation and provenance storage are negligible.
- **security:** Only run from the explicitly selected active tab and only extract fields the owner names. Store claims, URL, timestamp, and a short evidence capsule—not page HTML or screenshots—using the existing browser retention limits. Show the exact reminder title/date before creating it; redact account numbers and credentials. Keep the card host-scoped and expire it after 24 hours unless the owner explicitly saves it.
- **missing:** A browser_read_page/extract action that accepts an explicit tab ID and a field schema, rather than returning an unbounded page dump; A structured evidence-card schema with claim-level URL/selector/quote provenance and expiry; A confirmation/preview handoff from browser extraction to mac_run_actions create_reminder; A pendant-readable card index and a way to ask for the source claim later; An undo link joining the created reminder to the browser evidence card

### "“Before I submit this authenticated form, check it against my calendar and the details I’ve already told you, point out contradictions, and give me a corrected preview—without submitting.”"
- **useful because:** Authenticated forms are where a small unnoticed mismatch creates real cost. Safari can see fields no other node can reach; the Mac can inspect calendar and local context; the relay can explain discrepancies through the pendant. The result is a concrete, reversible preflight rather than an approval gate: the owner still has maximum control and can submit manually.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Structured/cheap model for field extraction and deterministic comparisons; realtime model only for ambiguous natural-language fields or spoken follow-up. Do not use the expensive tier for ordinary date/email/amount validation.
- **latency:** Capture and compare in 3–8 seconds after the owner asks; show a field-by-field diff and corrected draft before any mutation. Never click submit, send, or purchase.
- **cost:** Approximately $0.005–$0.03 per preflight, mostly extraction and one comparison call; local calendar lookup and diffing are negligible.
- **security:** The owner explicitly invokes it on the active tab. Use an action allow-set containing only read/extract and calendar-read operations. Treat payment, health, employment, and identity fields as configurable categories; redact them from persistence by default. Keep the corrected preview ephemeral, record only a short audit receipt, and make no automatic form mutation or submission.
- **missing:** A browser form-field extractor that returns labels, values, requiredness, and DOM provenance without sending keystrokes; A local calendar/context query with field-level matching (date, location, attendee, amount); A deterministic discrepancy engine plus model fallback for semantic matches; A side-by-side preview surface on Safari or dashboard and concise pendant summary; Per-category ephemeral/redaction policy for sensitive form fields

### "“I’m leaving this Safari task for later. Remember the exact tab, what I was trying to do, and the next safe step; when I say ‘resume my browser task,’ bring me back to it and explain where I left off.”"
- **useful because:** This makes authenticated browser work survive sleep, travel, and interruptions. The browser holds the login and exact tab, the relay holds a tiny task checkpoint, and the pendant provides a hands-free resume command. It avoids storing page bodies while eliminating the costly cognitive reset of finding the right page and reconstructing intent.
- **path:** browser-extension → relay-realtime → mac-planner → pendant → dashboard
- **model tier:** Cheap background model to summarize the owner’s explicit task into a short checkpoint; realtime model only to interpret a spoken resume request. Navigation is deterministic and does not need a large model.
- **latency:** Checkpoint in under 3 seconds; resume should navigate Safari and speak the checkpoint in under 8 seconds. If the tab/session is gone, report that plainly instead of guessing.
- **cost:** Under $0.01 per checkpoint/resume, mostly one short summarization call; storage and navigation are negligible.
- **security:** Persist only tab origin, title, timestamp, owner-supplied intent, and a short next-step label—never page content, cookies, screenshots, or form values. Make checkpoints host-scoped, expire after 24 hours by default, and let the owner delete them. Resuming may navigate but must not click, type, or submit.
- **missing:** A first-class browser task checkpoint object distinct from page findings and browser job receipts; A browser extension event that reports stable tab identity/title after sleep or tab replacement; A deterministic resume action that navigates the matching Safari tab or creates it if absent; A pendant command and spoken checkpoint listing; Expiration, deletion, and conflict handling when a saved tab no longer exists

### "“I’m late to this browser-based meeting—quietly tell me who is speaking, what decision is currently pending, and the one thing I need to contribute; capture only decisions I explicitly mark.”"
- **useful because:** A browser session can see the authenticated meeting room and chat while the Mac knows the calendar event and the pendant can deliver a private catch-up without forcing the owner to read a screen. This is a late-arrival rescue and decision aid, not a generic meeting transcript or page watcher.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Realtime model for the short spoken catch-up; a cheaper streaming classifier for speaker labels, agenda state, and explicitly marked decisions. Avoid full transcript retention.
- **latency:** Initial catch-up within 8 seconds; updates within 2 seconds of an explicitly marked decision or agenda transition. No unsolicited continuous narration.
- **cost:** $0.02–$0.10 per meeting catch-up, dominated by short context extraction and realtime speech; substantially less if the owner asks only once.
- **security:** Run only when invoked for the active meeting tab. Do not persist audio, transcript, participant names, or chat by default. A decision capture requires an explicit owner mark and stores only a short claim with meeting URL/time and a 24-hour expiry. Never send chat messages or alter meeting state.
- **missing:** Meeting-page adapters that identify current speaker, agenda, chat, and decision affordances across authenticated providers; A low-latency browser extraction stream rather than whole-page polling; An explicit pendant gesture or spoken marker for 'capture this decision'; Audio/context fusion between browser page state, Mac calendar event, and relay speech; Strict ephemeral transcript handling and provider-specific redaction rules

### "“Has this authenticated contract or policy page changed since I last reviewed it? Show me only the clauses that changed, explain the practical consequence, and keep the original page out of memory.”"
- **useful because:** Owners routinely revisit terms, policies, and agreements behind logins where public search cannot reach. A version-aware browser reader could distinguish meaningful clause changes from layout noise and explain consequences without retaining sensitive documents.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Background model for normalization, clause alignment, and change classification; realtime model only for the owner’s spoken question about a particular changed clause.
- **latency:** First comparison in 10–30 seconds depending on page length; a spoken explanation in under 5 seconds after the owner selects a clause.
- **cost:** $0.03–$0.20 per comparison, dominated by two page-normalization/extraction passes; unchanged pages should be skipped using a local content fingerprint.
- **security:** Never store source documents, screenshots, or full clauses. Keep only bounded redacted hashes, clause identifiers, a short owner-requested consequence, URL, and expiry. Require explicit invocation on the active authenticated tab and never accept or acknowledge revised terms.
- **missing:** A private, local comparison buffer for two authenticated page reads; DOM-aware clause segmentation that survives layout and navigation changes; A semantic diff that labels legal/financial impact separately from cosmetic edits; A dashboard view with expandable source evidence that expires with the buffer; A deletion/expiry path that removes both comparison buffers and derived claims


## Changes it proposed to its own stack

### `interaction` — Add a pendant-triggered browser privacy interrupt: a deliberate long press sends a signed high-priority event through the relay to Safari, which immediately replaces authenticated pages with a neutral lock screen, cancels queued browser commands, and freezes new page extraction. A second deliberate action restores the tabs without submitting or closing them. The extension must acknowledge completion and the pendant must report failure if Safari is unreachable.
- **owner gets:** If the owner steps away from a Mac displaying private authenticated pages, one physical action on the wearable can hide them immediately. This is a tangible safety feature no browser-only or relay-only node can provide, and it works even when the owner cannot reach the keyboard.
- effort: Medium-high: firmware event and acknowledgement, signed relay event, Safari extension lock/unlock state, command cancellation, and recovery after Safari restart. Test per-tab restoration and stale-command invalidation.  ·  risk: A false trigger could interrupt active work; make the gesture deliberately distinct and preserve tabs in memory. If the Mac or relay is offline, the pendant must give an unmistakable failure indication rather than claim privacy. Recovery must not replay commands queued before the lock.
- cost: Negligible API cost; approximately $10–$30 engineering/hardware test cost if a dedicated physical input or LED feedback change is needed. No material power impact beyond one radio event.  ·  latency: Target under 500 ms from relay receipt to Safari lock; under 2 seconds end-to-end on a connected Mac. Offline failure is immediate and local.
- security: Improves confidentiality but creates a security-critical command path. Use device-bound signatures, monotonic event IDs, replay protection, and an extension-side deny-all state. Never transmit page contents during lock or unlock.
- depends on: A real pendant-to-relay event path while the pendant is USB-attached or LTE-registered; Safari extension support for a lock overlay and browser command cancellation; A durable command epoch so commands queued before the interrupt cannot execute afterward; A deliberate button gesture that does not conflict with existing playback and bookmark controls


## What it asked for

_Nothing._
