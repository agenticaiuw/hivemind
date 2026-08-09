# Harness derivation — mac-planner — round 293

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Before I send this, check the draft I am composing against my calendar and existing commitments, then tell me on the pendant if I promised an impossible time, duplicated work, or exposed sensitive information."
- **useful because:** A language model can polish prose, but the valuable check is whether the promise is feasible and safe in the owner's real schedule. It combines the live Mac draft with Calendar/Mail evidence and gives a private, short warning before an irreversible send.
- **path:** pendant → mac-bridge → relay → dashboard
- **model tier:** Use a small background model for extraction and conflict classification; reserve realtime only for the spoken warning after the owner asks.
- **latency:** Draft and calendar read in under 4 seconds; a one-sentence pendant warning within 2 seconds after analysis. Never delay the actual send unless the owner explicitly asks for a gate.
- **cost:** About $0.003–$0.02 per check, dominated by sending the draft and bounded calendar context to the classifier; no cost when not invoked.
- **security:** Drafts can contain highly sensitive material. Default to local extraction/redaction on the Mac, send only commitments, dates, recipients, and detected secret patterns, and never archive the draft. The result should be advisory and must not silently send, edit, or delete mail.
- **missing:** A Mac read action for the current Mail/Message draft and its recipient fields without screen scraping; A relay intent that binds one draft hash to one calendar/mail snapshot so stale checks cannot be mistaken for the current draft; A pendant response format for concise private warnings and a dashboard audit showing only the rule triggered, not the draft body

### "I say “find the document I was looking at about X,” and the system searches my local files, recent browser pages, Mail, and Calendar, ranks the candidates with evidence, then opens the selected one on the Mac after I choose by voice."
- **useful because:** People lose work across Finder, authenticated web sessions, attachments, and meeting records. A wearable query plus cross-surface evidence is faster than manually searching four places, while keeping the final open action explicit.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use deterministic filename/full-text and metadata search first, then a cheap background model to rank semantic matches and explain the evidence. Realtime is only for the short disambiguation exchange.
- **latency:** Return the first three candidates in 5 seconds; open the chosen candidate within 2 seconds after the owner's selection.
- **cost:** $0.001–$0.01 per query; local indexing and browser inspection dominate, with model cost limited to ranking snippets.
- **security:** Do not upload whole files or page bodies by default. Return redacted names, domains, dates, and short snippets; honor authenticated browser-session boundaries; require an explicit selection before opening or downloading anything.
- **missing:** A unified search adapter spanning allowlisted Mac files, Mail attachments, Calendar attachments, and active authenticated browser pages; A relay response schema for numbered candidates small enough for pendant speech; A safe open-by-stable-ID operation so a changed search result cannot open the wrong file or URL

### "I say “secure my desk” to the pendant, and the system locks the Mac, blanks the display, clears the clipboard, closes or signs out of authenticated browser sessions, and tells me exactly what it could not secure."
- **useful because:** The existing pendant privacy latch protects the wearable's microphone and speaker, but it does not protect an unattended Mac or browser session. A single spoken command would make leaving a desk or a shared room safe across every surface.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use deterministic Mac/browser actions and a receipt aggregator; no model is needed except optional natural-language explanation of partial failures.
- **latency:** Begin within 1 second, lock the Mac and mute pendant locally immediately, and return a complete per-surface receipt within 5 seconds.
- **cost:** Effectively zero API cost; the work is local actions and browser session acknowledgements.
- **security:** This is intentionally high impact: locking and terminating sessions can lose unsaved work. The policy must be owner-configured, with a dry-run status mode and an explicit choice between close-tabs, sign-out, or merely revoke tokens. Never claim success without per-action receipts, and keep secrets out of the dashboard.
- **missing:** A relay fan-out command with idempotency and ordered receipts across Mac and browser; A Mac action for lock-screen/clipboard clearing plus a way to detect unsaved-work failures; A browser operation that revokes authenticated sessions rather than merely closing a tab; A local pendant confirmation state that remains private if the Mac is unreachable

### "Tell me, in plain language, what personal data this system is about to send off my Mac or browser, who will receive it, how long it will be kept, and let me cancel that one operation from the pendant."
- **useful because:** The owner cannot meaningfully consent to a hive whose data crosses a relay, browser session, Mac, and wearable if the boundary is invisible. A live data-flow explanation would make privacy a usable property rather than a settings page nobody reads.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use deterministic provenance and redaction metadata to build the inventory; use a cheap model only to compress field names into a spoken explanation. Never send the unredacted payload to explain it.
- **latency:** Preview within 2 seconds before dispatch; pendant cancellation must stop queued work within 1 second where the destination supports cancellation.
- **cost:** Under $0.01 per preview; costs are dominated by local payload inspection and receipt storage, not inference.
- **security:** The preview itself can leak sensitive field names. Redact values and secrets, hash payloads, bind the preview to an immutable operation ID and expiry, and fail closed when provenance is unknown. Cancellation must not be reported as success until every surface acknowledges it.
- **missing:** End-to-end provenance labels on relay, browser, Mac, and pendant messages; A pre-dispatch interception point for every outbound payload, including browser results and audio metadata; A single cancellation protocol with per-surface receipts and a retention/deletion report

### "If I say “I can't talk” or press the emergency control, send my prewritten check-in to my chosen contact, keep the pendant quiet, and tell me privately whether the Mac, phone, or cellular path delivered it."
- **useful because:** A voice-first wearable is least useful when speaking is unsafe or impossible. This would turn the pendant, relay, Mac/iPhone reach, and delivery receipts into a discreet fallback rather than assuming the owner can hold a conversation or operate a screen.
- **path:** pendant → relay → mac-bridge → iOS → dashboard
- **model tier:** Deterministic phrase/button detection and message dispatch; no generative model should decide the recipient or invent emergency wording. A background model may summarize delivery failures only after the fact.
- **latency:** Local quiet acknowledgement immediately; dispatch within 3 seconds; per-route delivery status within 15 seconds.
- **cost:** Usually less than $0.01 per event, excluding carrier SMS fees; the main cost is maintaining redundant delivery and receipt records.
- **security:** This can cause real-world harm if triggered accidentally or sent to the wrong person. Require an owner-configured phrase/button sequence, fixed recipient allowlist, immutable message templates, rate limits, local cancellation window where safe, and explicit “sent/failed/unknown” states. Do not infer location unless separately enabled.
- **missing:** A reliable emergency trigger that is distinct from recording and bookmark button paths; An iOS/SMS or approved contact-delivery adapter with delivery receipts and offline retry; A relay escalation state machine that does not depend on an active voice session; A private pendant status signal that cannot reveal the event to bystanders


## Changes it proposed to its own stack

### `hardware` — Replace the current one-LED/two-button pendant revision with a low-power two-line e-ink or memory-LCD strip and a secure element with monotonic counter, while retaining the existing audio path and microSD. The display should show a six-to-eight-word action summary, origin, expiry, and success/failure state; the secure element should sign button confirmations and diagnostic receipts.
- **owner gets:** The owner could tell what the pendant is asking them to approve and know whether a remote Mac/browser action actually finished, even in a noisy room or with the Mac display out of sight. A hardware-backed counter also prevents an old approval or receipt from being replayed.
- effort: High: new enclosure, power budget, display driver, secure-element provisioning, firmware UI/state-machine redesign, and relay verification. Prototype on a development board before committing to a wearable revision.  ·  risk: Display burn-in, battery drain, confusing status alongside audio, and provisioning loss could make the device unusable. Recovery requires a factory reset path that cannot erase the owner's queued offline records without an explicit export.
- cost: Roughly $8–$25 added component cost in small volume, plus PCB/enclosure redesign; tens of milliwatts while refreshing, near-zero while static. No per-use API cost.  ·  latency: A confirmation/status screen can update in 100–500 ms; e-ink refresh may be visibly slower than the current LED, so audio acknowledgement remains immediate.
- security: Improves action and receipt authenticity if keys never leave the secure element, but introduces key provisioning and recovery obligations. Screen content must be redacted and should never display secrets.
- depends on: An owner-defined action-approval policy; A relay action-hash/receipt protocol; A firmware UI allocator that arbitrates recording, alerts, privacy, and approval states


## What it asked for

_Nothing._
## Its own summary

This round produced three non-duplicate capabilities: (1) draft-versus-commitment safety checking before sending Mail, (2) cross-surface lost-document finding with explicit selection before opening, and (3) a spoken “secure my desk” fan-out that locks the Mac, protects browser sessions, and reports partial failures. The interruption bookmark and bench audio-check variants were correctly rejected as already covered by existing work.

**Biggest unknown:** The remaining blocker is not model capability: the live system still lacks a callable semantic Mac context reader (window/document/selected text) and a browser effect preview/revocation primitive. I still need those, plus a relay-level idempotent fan-out receipt for the desk-security flow and a bounded Mail-draft reader for the commitment check. The pendant remains physically USB-attached but LTE-unregistered, so bench-only flows must continue to use Mac serial actions rather than assume a registered relay device.

