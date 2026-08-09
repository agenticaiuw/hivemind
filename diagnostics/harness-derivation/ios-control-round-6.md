# Harness derivation — ios-control — round 6

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Before I leave, check my iPhone for unread urgent notifications and my Mac/browser for anything time-sensitive, then tell me the three things I must handle.”"
- **useful because:** This is the strongest unique hive behavior: the phone has private, live notifications while the Mac has mail/calendar/browser sessions, and the pendant is the only always-available voice surface. It prevents the owner from manually checking two worlds.
- **path:** ios-control → mac-planner → browser-extension → relay-realtime
- **model tier:** gpt-5.6-luna for the bounded cross-device synthesis; gpt-4.1-mini for OCR and screen extraction; realtime only to ask and speak the short result
- **latency:** 15–30 seconds when the phone is mirrored and unlocked; if mirroring is paused or the Mac is locked, report that limitation immediately rather than pretending to inspect
- **cost:** About $0.01–$0.05 per invocation, dominated by one vision/OCR pass and synthesis; no cost while idle if explicitly user-triggered
- **security:** Notification contents and logged-in browser data leave the phone/Mac only to the local planner and relay synthesis. Never read arbitrary notification bodies without an explicit request; redact codes and secrets; speaking the result aloud needs a spoken confirmation if it contains private message content.
- **missing:** A granted ios_mirroring_inspect/read-only action that captures the Mirroring window by process/window ID and returns OCR plus pause/locked state; A bounded notification classification schema (urgent/actionable/non-actionable) rather than unrestricted screen scraping; A relay intent that correlates phone and Mac observations into one short briefing

### "“Ask me on my iPhone to approve this before you send it.”"
- **useful because:** Sensitive actions currently force a vague spoken confirmation. A visible approval card on the real iPhone gives the owner the exact recipient, amount, and content, while the Mac/browser performs the action only after a cryptographic one-time approval. This makes voice control trustworthy enough for mail, purchases, and destructive edits.
- **path:** relay-realtime → ios-control → mac-planner → browser-extension
- **model tier:** gpt-5.6-luna prepares a structured preview; no model decides approval; the iPhone UI and relay verify a signed one-time token; mac-planner executes only the approved operation
- **latency:** 2–5 seconds to render the approval request when mirroring is active, plus the owner's tap; expire requests after 2 minutes
- **cost:** Under $0.01 per request; model cost is only preview generation, with negligible relay traffic
- **security:** The phone must display the full target, payload, and scope—not a generic Allow button. Bind the token to operation hash, account, and expiry; reject replay and altered payloads; require confirmation again for changed content. Do not expose secrets to OCR if a dedicated local approval surface can render them.
- **missing:** A small iPhone companion/approval surface reachable through the mirrored phone (or an approved notification action); Relay storage for pending operation hash and one-time signed approval; An execute gate in mac-planner/browser harness that refuses unapproved or stale jobs

### "“Keep watching my phone task until it’s done, and tell me if you need me to pick up the phone.”"
- **useful because:** Phone automation is uniquely constrained: mirroring pauses when the owner picks up the phone, and taps only work frontmost. A cooperative watcher can distinguish success, owner takeover, lock, and UI change, then use the pendant to ask for the smallest next step instead of failing silently or tapping blind.
- **path:** ios-control → relay-realtime → mac-planner → pendant
- **model tier:** gpt-4.1-mini performs cheap periodic OCR/state comparison; gpt-5.6-luna is invoked only on a state transition or ambiguity; realtime speaks the short request
- **latency:** Poll at 1–2 Hz only during an active task; announce state transitions within 3 seconds; stop after 2 minutes or on owner takeover
- **cost:** Roughly $0.01 per short task with local captures; vision/OCR frequency is the dominant cost, so use image hashes and region-of-interest diffs
- **security:** Capture only the Mirroring window, never the whole desktop. Do not infer success from an unlabelled icon alone; require textual confirmation or an app-specific state rule. Abort on lock, pause, window disappearance, or unexpected content.
- **missing:** Read-only iOS mirror capture with explicit states: frontmost, paused-by-owner, locked/no-pixels, window-missing; A foreground-action lease that safely brings Mirroring frontmost for taps and restores the previous Space; A resumable task state machine and relay event push to the pendant

### "“Remember what I’m looking at on my iPhone, with the source and why it matters.”"
- **useful because:** Today the owner must manually screenshot, copy the URL, switch devices, and write context. This would turn a fleeting phone screen into a searchable, contextual note: the mirrored screen capture, OCR text, app/source identity, timestamp, and the owner's spoken explanation are saved together. It is especially valuable for articles, shopping comparisons, directions, and messages that cannot be conveniently transferred to the Mac.
- **path:** ios-control → mac-planner → relay-realtime → browser-extension
- **model tier:** gpt-4.1-mini extracts text and stable metadata from the bounded Mirroring window; gpt-5.6-luna resolves the source and writes a concise note only when the owner supplies an explanation; realtime handles the one-sentence voice capture
- **latency:** Capture acknowledgement under 2 seconds; note completion under 10 seconds. If the phone is paused, locked, or unavailable, preserve the spoken explanation as an incomplete draft rather than inventing screen contents.
- **cost:** Approximately $0.01–$0.04 per capture, dominated by OCR and optional source resolution; storage is tiny for a compressed screenshot plus extracted text
- **security:** Capture only after the explicit phrase and only the Mirroring window. Messages, health data, and authentication screens may be sensitive: detect likely secrets, redact them from indexing, and offer ‘save text only’ or ‘discard image.’ The note must clearly record whether source metadata was verified or inferred.
- **missing:** A user-triggered iOS Mirroring capture that returns the active app/window, OCR, and a privacy classification; A local note/artifact store that accepts screenshot, OCR, provenance, and voice context as one atomic record; A source resolver that can associate a visible URL or app item with a browser tab without assuming that OCR text is a URL; A relay workflow that asks one short follow-up when provenance is ambiguous

### "“When I finish buying something on my iPhone, save the receipt, identify the return deadline, and remind me before it expires.”"
- **useful because:** The purchase confirmation lives on the phone while return policies, email receipts, and reminders live elsewhere. The owner currently has to notice the receipt, transcribe dates, and create a reminder. The hive can connect the phone confirmation to the browser/email session and create a durable, actionable record.
- **path:** ios-control → browser-extension → mac-planner → relay-realtime
- **model tier:** gpt-4.1-mini extracts receipt fields from the bounded phone screen; gpt-5.6-luna reconciles merchant/order/date evidence and computes the return deadline; a cheaper background worker checks the deadline later; realtime asks only for ambiguity or unusual purchases
- **latency:** Initial capture and confirmation in 10–20 seconds; reminder creation after one concise spoken confirmation when the deadline is uncertain. Background checks need not be realtime.
- **cost:** About $0.02–$0.08 per purchase, mainly receipt OCR and cross-source reconciliation; later deadline checks are low-cost scheduled work
- **security:** Never save full card numbers, security codes, or unrelated messages. Store merchant, item, order identifier suffix, price, evidence links, and policy dates with encryption and retention controls. Require confirmation before creating reminders if the deadline was inferred rather than explicitly shown.
- **missing:** A purchase-intent trigger or explicit ‘capture this receipt’ voice command bound to the current Mirroring screen; A structured receipt/return-policy schema with evidence and confidence fields; A reminder route that supports provenance and automatic cancellation when the owner marks an item returned; A cross-source matcher for phone confirmation, browser receipt, and email without exposing full sensitive content

### "“Tell me when the person I’m waiting for has actually arrived, without making me keep checking my phone.”"
- **useful because:** A phone may show a changing rideshare, delivery, or event status while the owner is moving around with the pendant. Combining the phone’s live status screen with browser/order context lets the system announce a meaningful state transition—arrived, delayed, pickup moved—rather than repeatedly reading notifications or requiring manual refreshes.
- **path:** ios-control → browser-extension → relay-realtime → mac-planner
- **model tier:** gpt-4.1-mini performs low-frequency, region-of-interest state extraction; gpt-5.6-luna resolves ambiguous transitions against browser/order context; realtime delivers only the transition announcement
- **latency:** Check only during an explicitly active watch, at 15–30 second intervals, and announce within one interval. Auto-expire after the expected arrival window.
- **cost:** About $0.01–$0.05 per watch session, dominated by vision checks; use screen hashes and text-region diffs to avoid model calls when unchanged
- **security:** Watching must be explicit, time-limited, and visible to the owner. Do not infer physical location beyond what the selected app visibly states. Stop on lock, mirroring pause, or account/logout changes; never announce private details where others may hear them.
- **missing:** A first-class time-limited watch lease with start, stop, expiry, and owner-visible status; App-specific state extractors for delivery/rideshare/event screens that distinguish ETA changes from arrival; A relay scheduler/event channel for low-cost polling and transition-only speech; A privacy mode that suppresses spoken merchant, address, or contact names unless requested


## Changes it proposed to its own stack

### `new-surface` — Add a tiny native iPhone companion approval screen surfaced through an App Intents/Live Activity-style entry point, with a relay-delivered operation preview and explicit Approve/Reject actions. Pair it to the Mac planner using a device key; do not rely on OCR of arbitrary app screens for the security decision.
- **owner gets:** The owner can safely approve a real-world action from the phone they already trust, seeing exactly what will happen instead of trusting a spoken summary or a generic confirmation.
- effort: Medium-high: iOS companion, relay challenge endpoint, key enrollment, planner execution gate, and recovery UX for mirroring paused or phone locked.  ·  risk: A compromised Mac could request misleading previews; bind approval to a canonical operation hash and display all material fields. If the companion is unavailable, fall back to current confirmation and never auto-execute.
- cost: Negligible runtime API cost; roughly one-time iOS engineering effort and minimal relay storage/bandwidth.  ·  latency: 2–5 seconds to deliver/render; owner tap is the dominant latency.
- security: Strongly improves authorization if tokens are signed, single-use, short-lived, and payload-bound. Adds a key lifecycle and revocation surface.
- depends on: A relay pending-challenge route; An iOS companion or system-surface implementation; mac-planner/browser execution gate that validates operation hash; A granted read-only/foreground iOS harness for fallback status


## What it asked for

### `s1-wspm` (skill) — pending-operation-approval
- does: When the relay sends a structured approval challenge, the pendant flashes a distinct pattern and plays a short tone; a short button press accepts and a long press rejects. It returns the challenge ID and button decision, with no payload or secret spoken/displayed on the device.
- must be on-device because: The owner may be away from the Mac/phone screen or unable to touch the iPhone. A physical, local decision survives a dropped audio link and prevents accidental approval from a stale spoken turn.
- trigger: Server push over the active pendant link, followed by the single hardware button event; timeout automatically rejects after 60 seconds.
- storage: Persist only the last challenge ID, decision, and monotonic expiry in a tiny retained record (under 128 bytes); clear it after acknowledgment.
- RAM budget: About 2–4 kB for state, event queue, and timer; comfortably within 211,608 B application RAM, assuming audio buffers remain unchanged.

