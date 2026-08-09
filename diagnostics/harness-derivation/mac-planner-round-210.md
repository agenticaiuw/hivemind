# Harness derivation — mac-planner — round 210

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-live-state** — As of 2026-08-08T03:27:34Z, AI Pendant Agent has Accessibility and Screen Recording, synthesized input posts successfully, Claude is foreground, and the Mac reports 19 running apps. Browser bridge reports three durable sessions: X home plus two probe forms.
  - evidence: mac_readonly_inspect operation running_apps and foreground_app returned GET /observe HTTP 200 with accessibility.trusted=true, eventsPost=true, screenRecording=true, browser.sessions=3.

## Capabilities it proposed

### "When I press the pendant's bookmark button, save not just the time but what I was looking at on my Mac, and later let me ask “what was I looking at when I marked that?”"
- **useful because:** The shipped offline bookmark tells the relay that a moment mattered, but a timestamp alone forces the owner to reconstruct it. The Mac is currently Accessibility- and Screen-Recording-enabled, with Claude foreground and three browser sessions open; joining the pendant event to foreground app, browser URL/title, and a redacted UI/document identity turns an unreliable memory cue into a useful recall primitive. It still works when LTE is absent: the pendant queues the event and the Mac can attach context when USB-connected, then the relay reconciles both by event ID.
- **path:** pendant → mac-planner → browser → relay-realtime → unified
- **model tier:** background for event joining and redaction; realtime only when the owner asks the follow-up question
- **latency:** Capture acknowledgement under 300 ms locally; Mac context attachment within 2 s of USB/link availability; recall answer under 2 s from indexed event metadata
- **cost:** Usually one cheap background classification/summarization call per bookmark (roughly $0.001–$0.01); most events need no model call if app/title/URL are sufficient
- **security:** Never store raw screen pixels or page bodies by default. Record app bundle, window title, URL origin/path according to owner policy, and a short redacted selected-text hash/snippet only when explicitly enabled. Browser passwords and secure-input fields must be excluded. Attachment must be visibly marked as inferred context, not claimed as exact if the Mac observation races the button.
- **missing:** A small event-join route keyed by the pendant bookmark ID and a timestamp tolerance, accepting redacted Mac context and exposing it to unified recall; A reliable read-only window/document identity operation beyond the existing host observation; ui_snapshot is available but browser inspection is currently ambiguous between two live resolutions; A USB serial event bridge so the unregistered pendant can deliver bookmark IDs to the Mac today

### "When I plug in the pendant and audio bridge, run a safe end-to-end health check automatically, tell me exactly which link is broken, and keep retrying only the failed stage until both are ready for a call."
- **useful because:** The hardware is physically present on USB now, while LTE registration is not. Today that boundary is invisible: a failed conversation could be radio, serial transport, Opus, speaker delivery, or relay state. A Mac-side guardian can detect the two known USB serial devices, invoke the firmware diagnostic fixture, correlate its counters with relay pipeline events, and speak one actionable result through the pendant or show it on the Mac. This converts a developer-only bench test into a daily reliability feature and avoids wasting a full call on a known-bad path.
- **path:** mac-planner → pendant → relay-realtime → unified
- **model tier:** No model for detection or pass/fail; cheap background model only to turn a structured failure receipt into a human sentence
- **latency:** Hot-plug detection under 3 s; full fixture under 30 s; failed-stage retry with exponential backoff, never more than once per minute
- **cost:** Near-zero API cost; one optional summarization call under $0.001 per failed run. USB polling and fixture execution are local.
- **security:** The fixture must use synthetic audio only and never open or retain the microphone. Serial commands must be allowlisted to the diagnostic protocol, not arbitrary shell. Receipts should include counters and firmware version but no audio payload. Automatic retries must stop after a bounded count and never alter firmware.
- **missing:** A real Mac serial-exchange capability for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA (the earlier request is still unavailable); A small local daemon or launchd job for USB hot-plug monitoring and exclusive-port locking; A relay endpoint that accepts diagnostic receipts and correlates them with pipeline/audio status; A user-facing readiness state shared with the pendant inbox/LED

### "Tell me what changed in my open browser work since I last looked, and put only the genuinely new or urgent items on the pendant; leave everything else in a digest for later."
- **useful because:** The browser has three durable sessions and is online, but the wearable currently has no notion of change across visits. A browser-side snapshot/diff service can watch authenticated tabs without exporting passwords or whole pages, classify changes by urgency, and use the pendant as a low-distraction exception channel. This is more useful than a generic notification stream: the owner gets only actionable deltas while routine changes accumulate for a later spoken digest. It also directly covers authenticated work portals without asking the Mac briefing layer to impersonate a browser.
- **path:** browser → relay-realtime → pendant → mac-planner → unified
- **model tier:** Cheap background model for page-diff extraction and urgency ranking; realtime only when the owner asks for the digest or says “read the urgent changes”
- **latency:** Poll watched tabs on a configurable 5–15 minute cadence; urgent alert after a stable two-snapshot confirmation within 30 s; spoken digest under 3 s
- **cost:** Roughly $0.002–$0.03 per changed page depending on extracted text size; unchanged tabs cost no model call. Browser-side DOM extraction and hashing are local.
- **security:** Never send cookies, DOM forms, passwords, or page screenshots by default. Store origin, title, structured change records, and aggressively redacted snippets; per-site selectors and retention must be owner-configurable. Do not click, submit, or send messages automatically. A page change must be labeled as observation, and the pendant alert should contain no sensitive content beyond the configured snippet budget.
- **missing:** A browser page-watch scheduler and durable per-session snapshot/diff store (the existing browser heartbeat/inspect paths do not provide historical diffs); A browser result schema that returns redacted semantic changes rather than raw inspection output; Relay routing from a watch diff into the existing offline_alert_inbox, with urgency, expiry, and deduplication fields; A user-facing command to request the accumulated digest and acknowledge individual alerts

### "When the pendant is plugged into my Mac, let me keep having a normal voice conversation through the Mac’s network even if the pendant has no LTE registration, then switch back to cellular automatically when LTE returns."
- **useful because:** The pendant and ESP32 bridge are physically connected now, but the pendant is not registered with the relay. That makes the device fail precisely when it is most convenient to test or when cellular coverage is absent. A USB-tethered mode would make the wearable useful indoors, on an airplane with Wi-Fi, and at the workbench: the pendant remains the microphone/speaker and buttons, while the Mac becomes a transport proxy. Cellular takeover must be seamless at a packet boundary rather than requiring a new conversation.
- **path:** pendant → mac-planner → relay-realtime → unified
- **model tier:** No model for transport selection or failover; realtime model remains the conversation model and receives the same audio stream regardless of bearer
- **latency:** USB mode should add under 30 ms one-way transport latency; bearer failover under 2 s with no duplicated audio or lost utterance
- **cost:** No additional inference cost; local serial framing and a small relay session proxy dominate. Hardware cost is $0 with the currently connected boards.
- **security:** Pair the pendant to one explicitly approved Mac using a device key and challenge-response; never expose a raw serial port as a network service. Encrypt audio and control frames end to end, zeroize buffered audio after acknowledgement, and make the relay label the active bearer in receipts. Cellular fallback must not silently route through an untrusted Mac.
- **missing:** A production USB serial transport for the two connected boards; A Mac bridge service that multiplexes pendant control, uplink Opus, and downlink Opus without opening the microphone independently; Relay session support for bearer migration with sequence continuity and duplicate suppression; A pendant firmware transport abstraction that treats USB as a peer to LTE while preserving the shipped 24 kHz/60 ms framing

### "Use the page I have open and my calendar or email to prepare a form or reply, read back every field on the pendant, and submit only after I explicitly say the final confirmation."
- **useful because:** Today the browser, Calendar/Mail reader, and wearable conversation are separate. The owner must copy details between them and risk losing a half-completed authenticated workflow. This would let the relay gather only the relevant source facts, have the browser extension fill a draft, and use the pendant for a field-by-field verbal review. It is especially useful for scheduling, support forms, expense claims, and routine replies while preserving a hard boundary before an external submission.
- **path:** pendant → relay-realtime → browser → mac-planner
- **model tier:** Realtime model for conversational clarification and read-back; a cheaper background model can extract candidate fields from bounded Calendar/Mail snippets. Deterministic browser automation performs filling and submission.
- **latency:** Draft visible in 5 s; each field read-back under 500 ms; submission occurs only after an explicit confirmation phrase and should return a receipt within 3 s
- **cost:** About $0.005–$0.05 per workflow depending on source extraction and clarification; browser operations and Calendar/Mail reads are local or already available
- **security:** Never submit based on silence, an ambiguous “okay,” or a background classification. Show the exact destination, changed fields, and final payload on the Mac and speak a concise digest on the pendant. Do not expose unrelated mail, passwords, payment data, or hidden form fields to the model. Abort on page navigation or changed totals.
- **missing:** A browser action contract for typed field extraction, draft filling, and a separate explicit submit operation with before/after snapshots; A relay conversation state that binds source snippets, browser tab identity, and a one-time confirmation nonce; A browser extension result containing field labels and values rather than only generic inspection output; A redaction and confirmation policy that the owner can configure per site and per field class

### "For any answer or action, let me ask the pendant “what did you use?” and get a short provenance list, then say “forget that source” to remove the copied context from the relay, Mac job, and browser bridge."
- **useful because:** The owner currently has to trust a distributed system whose context may have come from Calendar, Mail, a browser session, a file, or the pendant, with no single spoken audit or deletion command. Provenance makes the hive understandable at the moment it matters; source-level forgetting gives the owner an immediate way to retract copied context without hunting through three machines. This is not merely a log: it binds the exact answer/action, source identifiers, redaction status, retention expiry, and deletion receipts across nodes.
- **path:** pendant → relay-realtime → unified → mac-planner → browser
- **model tier:** No expensive model for provenance or deletion. Realtime model only verbalizes a deterministic provenance graph and resolves the owner’s natural-language reference to a source.
- **latency:** Provenance answer under 1 s from local receipt metadata; deletion acknowledgement under 3 s when nodes are online, with a durable pending deletion if a node is offline
- **cost:** Negligible inference cost; storage is a few hundred bytes of structured provenance per action. Occasional background reconciliation is cheaper than a model call.
- **security:** Provenance must reveal source categories and minimal identifiers without replaying private content aloud in public. Deletion must be cryptographic or verifiable where possible, distinguish “deleted locally” from “deletion pending,” and never claim that an external website or an already-sent message was erased. The owner must be able to inspect and revoke the provenance policy itself.
- **missing:** A shared provenance record format with source IDs, derived artifacts, retention, and deletion state; Relay fan-out for authenticated deletion receipts to Mac jobs, browser snapshots, and any pendant outbox copies; Mac and browser hooks that can enumerate and erase derived context without deleting the owner’s original Calendar, Mail, or web data; A pendant command grammar and compact spoken rendering for provenance and deletion status


## What it asked for

_Nothing._
