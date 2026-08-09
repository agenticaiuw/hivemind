# Harness derivation — mac-planner — round 218

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I press the bookmark button, package what I was looking at on my Mac and in the browser into a dated evidence note I can ask for later."
- **useful because:** A physical bookmark captures the moment without requiring me to stop and type. When the pendant is USB-attached today (and later over LTE), the relay correlates the bookmark timestamp with the active Mac app, browser tab metadata, nearby Calendar/Mail context, and an optional short spoken label, then writes a local Markdown/JSON packet. It turns fleeting discoveries into retrievable evidence rather than another inbox item.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** background for correlation and summarization; realtime only to acknowledge the button press and read back the packet title
- **latency:** LED acknowledgement immediately; packet within 10 seconds of Mac/browser observations; spoken retrieval under 2 seconds from an indexed packet
- **cost:** About $0.01-$0.04 per packet depending on whether summarization is requested; most cost is one small background extraction call, not realtime inference
- **security:** Browser URLs, page titles, calendar/mail snippets, and any user-supplied label leave the Mac only when explicitly enabled. Default to metadata and redaction, never capture passwords or full page bodies, and require an explicit retrieval query for sensitive packets. The local packet should be encrypted and have a retention limit.
- **missing:** A correlation API that accepts a pendant bookmark timestamp and atomically requests Mac/browser snapshots; A browser inspection result with redacted title/URL and optional selected text; An encrypted, searchable packet store with retention and per-packet sensitivity

### "When I say on the pendant that I will do something, turn it into a private commitment that follows up only when there is evidence I did it or when it is genuinely at risk."
- **useful because:** Spoken commitments disappear into notes. The pendant can capture the promise while it is fresh; the relay can extract the action, due window, and confidence; Mac can create a reminder or a draft next step; Calendar, Mail, and browser sessions can later provide evidence without nagging on a fixed timer. The owner gets fewer forgotten promises and fewer pointless reminders.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** realtime for transcription/confirmation of the short promise; background model for commitment extraction, evidence matching, and escalation wording
- **latency:** Acknowledge and repeat the parsed commitment within 3 seconds; background evidence checks every 30-60 minutes; only surface an alert when confidence or deadline threshold is crossed
- **cost:** Roughly $0.02-$0.08 per commitment over its lifetime; transcription and extraction dominate, while most evidence checks are deterministic filters
- **security:** Commitments can contain confidential names and deadlines. Store the minimal structured fields, hash or redact message/page evidence, never send full email or page content to the pendant, and make each commitment's evidence sources visible and revocable. Creating external messages must remain a draft unless the owner explicitly asks to send.
- **missing:** A durable commitment record distinct from generic captures, with due-window, evidence-source, confidence, and lifecycle fields; A cross-surface evidence matcher for Calendar/Mail/browser observations; A follow-up policy engine that suppresses reminders when evidence is strong and expires stale commitments

### "Run a full pendant health check while it is plugged into my Mac, then tell me in plain language whether the microphone, 24 kHz speaker path, radio link, and queues are healthy."
- **useful because:** The hardware is physically present and testable now even though LTE registration is not. A single command should arm the pendant's existing diagnostic fixture over USB, collect bounded serial counters from both chips, correlate them with relay pipeline state, and produce a pass/fail report with the failing layer and the next recovery action. This prevents an owner from guessing whether silence is a radio problem, codec problem, bridge problem, or stale queue.
- **path:** pendant → relay → mac-planner → dashboard
- **model tier:** Deterministic checks and thresholds first; use a cheap background model only to turn the structured result into owner-facing language. No realtime model is needed unless the owner asks for a spoken result during a call.
- **latency:** Start acknowledgement under 2 seconds; fixture and report within 30 seconds; abort on button press or serial timeout and preserve a partial receipt
- **cost:** Under $0.01 per run; the cost is Mac/USB execution and relay storage, not model tokens
- **security:** The fixture must never capture or retain microphone content, only synthetic frames and counters. USB commands must be allowlisted and bounded by duration/bytes; serial logs may contain identifiers and should be redacted in dashboard output. Do not auto-flash firmware or alter modem settings.
- **missing:** A real bounded USB-serial bench runner for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; the attempted resolver still has no implementation; A diagnostic command/receipt schema tying pendant fixture sequence numbers to relay pipeline IDs; A health evaluator with explicit thresholds for packet loss, decode time, underruns, queue durability, and bridge forwarding

### "Before I send or publish something, let me press the pendant and ask, 'Is there anything private in this?' Have the Mac and browser inspect the exact draft or form, then read me the risks without sending it."
- **useful because:** Today the owner has to manually inspect a browser form, clipboard, document, and attachments for secrets or personal data. This would make the pendant a fast privacy review surface: the Mac/browser provide the actual outbound payload, a local scanner identifies credentials, personal identifiers, internal URLs, and accidental attachments, and the relay gives a short explanation. It is advisory rather than an automatic approval gate, so the owner keeps the existing maximum-control policy.
- **path:** pendant → mac-planner → browser-extension → relay → dashboard
- **model tier:** Local deterministic scanners for credentials, paths, domains, and known sensitive fields; a cheap background model only for ambiguous semantic classification; realtime only for the short spoken answer.
- **latency:** Capture the target and return a first risk result within 3 seconds; deeper attachment/document analysis may take 10 seconds and must clearly say it is incomplete.
- **cost:** Usually below $0.01 per check; local pattern matching dominates and model use is reserved for ambiguous text.
- **security:** The payload must be inspected locally by default. Send only redacted findings and small excerpts to the relay; never upload passwords, tokens, or full attachments. Do not mutate or submit the browser form. Keep a local receipt that records what was checked, not the secret values.
- **missing:** A Mac/browser primitive that returns the exact pending outbound payload, form fields, attachments, and destination without submitting it; A local secret/PII classifier with stable finding categories and redaction spans; A pendant query trigger and relay response path that can associate the spoken question with one specific browser or Mac target

### "When you mention a source during a pendant conversation, let me say 'show me that' and have my Mac open the right browser tab, jump to the cited passage, and leave a small visible citation note so I can inspect it."
- **useful because:** Spoken answers currently stop at audio. This would bridge the wearable's low-attention conversation to the Mac's high-bandwidth surface: the relay supplies a stable citation and passage anchor, the browser extension resolves it in the owner's authenticated session, and the Mac opens or annotates it without making the owner search by hand. It is especially useful for research, troubleshooting, and checking claims while walking back to the desk.
- **path:** pendant → relay → browser-extension → mac-planner
- **model tier:** Realtime model resolves the owner's short deictic request ('that') against the last spoken citation; deterministic browser navigation handles the URL/anchor; background fallback searches the page only if the anchor has moved.
- **latency:** Acknowledge under 1 second and open the target within 5 seconds; if the passage cannot be located, say so instead of opening an approximate page.
- **cost:** Under $0.01 per handoff; the main work is browser interaction, with a small fallback extraction call only for moved anchors.
- **security:** Never expose authenticated page contents to the relay merely to navigate. Pass a signed citation token containing origin, URL, and a redacted text hash; keep the actual lookup in the browser extension. Do not submit forms or follow navigation outside the cited origin without explicit owner instruction.
- **missing:** A citation token emitted by the speech/research pipeline with URL, quote hash, and expiry; A browser command that can locate a text hash in the current authenticated page and report exact/ambiguous/not-found; A Mac-side handoff that opens the resolved tab without stealing focus unexpectedly and records a receipt


## Changes it proposed to its own stack

### `browser-harness` — Add a signed, origin-scoped citation handoff protocol between the spoken relay and the browser extension. Each spoken source reference becomes a short-lived token containing the canonical URL, quote hash, optional DOM anchor, and redaction policy. The extension resolves the token locally, reports exact/ambiguous/not-found, and can highlight only an exact match; it must refuse cross-origin or form-submission actions.
- **owner gets:** The owner can move from hearing an answer on the pendant to seeing the exact supporting sentence on the Mac, without hunting through tabs or exposing authenticated page text to the relay.
- effort: Medium: token schema and relay emission, extension-side text hashing/anchor resolution, and a small Mac handoff/receipt path.  ·  risk: Dynamic pages, paywalls, and changed text will produce not-found or ambiguous results; fail closed and offer the URL without pretending the citation was verified. A compromised extension could still see page content, so keep the token origin-scoped and log only hashes.
- cost: Negligible API cost; one small background extraction only when a citation lacks a stable anchor. No new hardware cost.  ·  latency: Usually 1-5 seconds from spoken request to highlighted passage; slower pages need a visible pending state.
- security: Improves security by keeping authenticated content in the browser, but requires strict token expiry, origin binding, and redacted receipts.
- depends on: A citation token emitted by the speech/research pipeline; A browser-extension command for exact text/DOM-anchor resolution; A Mac handoff action that opens the resolved tab without submitting or mutating forms


## What it asked for

_Nothing._
## Its own summary

This round produced three owner-facing cross-node capabilities: (1) a pendant bookmark that captures redacted Mac/browser/calendar context into a dated evidence packet, (2) spoken commitments that become evidence-aware follow-ups rather than blind reminders, and (3) a USB-attached pendant/bridge health check using the shipped diagnostic fixture and structured receipts. The third is immediately relevant because the hardware is live on this Mac despite no LTE registration. I still need implementation of a bounded USB-serial bench runner, a durable encrypted evidence-packet store/correlation API, and a commitment lifecycle/evidence matcher. I also flagged to mac-terminal that the serial runner is the critical blocker.

**Biggest unknown:** Whether the live Mac agent has any bounded serial action hidden behind an undocumented route; current resolver evidence says no implementation, but the complete route inventory has not exposed one.

