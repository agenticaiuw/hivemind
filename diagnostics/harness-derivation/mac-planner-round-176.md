# Harness derivation — mac-planner — round 176

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “fill this out, but don’t submit,” inspect the authenticated browser page, complete the safe fields on my Mac, then let me approve submission with one deliberate pendant button press."
- **useful because:** It turns the wearable into a physical consent key for consequential web actions while preserving the convenience of browser automation. The owner can dictate a form workflow without trusting an invisible click at the end; the relay can read back the exact site, fields, and final total before the button press.
- **path:** browser-extension → relay-realtime → pendant → mac-planner
- **model tier:** Use a cheap background model for field extraction and validation; use realtime only for the spoken read-back and the short approval exchange.
- **latency:** Field discovery and draft completion under 5 seconds; read-back under 1 second; submission immediately after the next deliberate button event.
- **cost:** Roughly $0.01–$0.05 per form depending on page length; browser DOM extraction and Mac actions dominate latency, not model tokens.
- **security:** Never transmit passwords or full payment data to the model; redact sensitive DOM values. Submission must be bound to a page/session hash, field hash, and short expiry so an old approval cannot be replayed on a changed page. The current FULL_CONTROL path has no gate, so this needs an explicit policy entry and a new pendant approval event rather than assuming existing execution is safe.
- **missing:** browser command that returns a redacted field schema and final-page hash; relay approval state machine binding a physical pendant event to that hash; a firmware event route for one-shot approval (the existing bookmark button event is not sufficient without a new semantic payload); Mac executor support for browser actions that can pause before submit

### "When I start a pendant conversation, make the Mac temporarily quiet and restore exactly what was playing when we finish."
- **useful because:** The owner can speak naturally without Spotify, Zoom, notification sounds, or a browser video competing with the wearable reply. Exact restoration means the system does not leave the Mac muted or at the wrong volume after a dropped call.
- **path:** pendant → relay-realtime → mac-planner
- **model tier:** No expensive model: deterministic relay events and a local Mac state machine are sufficient; realtime is only the existing voice session.
- **latency:** Duck audio within 150 ms of call start and restore within 300 ms of call end or disconnect.
- **cost:** Near-zero API cost; implementation is local state capture plus two executor calls. The main engineering work is crash-safe restoration.
- **security:** Capture only app audio state and volume, never microphone data. Persist a short-lived recovery receipt locally so a Mac restart cannot cause a permanently muted system. It needs an explicit owner policy entry because current FULL_CONTROL_MODE bypasses approval and the routine mutates audio state.
- **missing:** relay lifecycle events with a stable conversation id and guaranteed end/disconnect notification; Mac action to snapshot per-app/system audio state, not only set global volume; idempotent restore keyed by conversation id with a timeout watchdog; policy configuration for unattended audio mutations

### "Turn the page I’m looking at into a local, cited decision packet: capture the relevant browser content, compare the options, save a Markdown and PDF summary in my workspace, and open it on the Mac."
- **useful because:** The owner gets from browsing to a durable artifact without copying tabs, losing source URLs, or asking the wearable to recite a long answer. It combines the browser’s authenticated view with the Mac’s filesystem and gives a reviewable document that survives the conversation.
- **path:** browser-extension → relay-realtime → mac-planner
- **model tier:** Use a background/standard model for extraction, comparison, and citation formatting; realtime only acknowledges the request and reports completion.
- **latency:** Capture in 1 second, draft in 10–20 seconds for a handful of pages, then open the packet immediately; large pages should stream progress rather than block the owner.
- **cost:** About $0.03–$0.15 per packet, dominated by page text and PDF generation; local file writing and opening are negligible.
- **security:** Only capture the explicitly selected tab or a bounded list of tabs; redact passwords, tokens, and form values before model submission. Save sources and generated artifacts under an owner-configured workspace, and write atomically so partial packets are never mistaken for complete ones.
- **missing:** browser bridge operation for explicit-tab content extraction with URL/title/source anchors and redaction; relay job that holds extracted pages and emits a typed artifact plan; Mac-side PDF rendering from Markdown without arbitrary shell access; completion receipt containing hashes, source URLs, and the opened file path

### "When I’m on a login page, let me approve filling the credential with the pendant, while the password stays inside macOS Keychain and never enters the model, relay, or browser command log."
- **useful because:** This would make authenticated browser automation usable without asking the owner to paste secrets or expose them to the AI. The pendant supplies deliberate physical presence; the Mac performs the Keychain lookup and clears the field after the page is submitted or abandoned.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** No model should inspect the secret. A small realtime model may identify the site and explain the requested account, but credential retrieval and insertion must be deterministic local code.
- **latency:** Site/account read-back under 1 second; Keychain fill within 300 ms of the pendant approval; automatic field clearing on cancellation or navigation.
- **cost:** Near-zero API cost. The work is macOS Keychain integration, browser message passing, and a short-lived approval token.
- **security:** The model receives only origin, account label, and success/failure—not the password or field contents. Bind approval to origin, tab/session id, field selector, and a 30-second nonce; reject cross-origin navigation and never persist the secret in receipts, screenshots, relay logs, or crash reports. This needs an explicit owner policy because current FULL_CONTROL_MODE has no effective gate.
- **missing:** a local Keychain broker callable by the Mac agent without returning secret bytes to the planner; browser-extension protocol for an origin-bound secret-fill request and acknowledgement; a new pendant physical-approval event distinct from moment bookmarks; redacted audit receipts that prove what origin was filled without recording the credential

### "If I say “stop everything,” cancel every pending Mac and browser action, stop any queued relay job, and tell me exactly what was prevented or already completed."
- **useful because:** A wearable panic brake gives the owner a reliable way to halt automation while away from the keyboard or when a page behaves unexpectedly. It is broader than undo: it stops queued work before execution and produces one spoken, durable incident summary.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Deterministic cancellation and receipt aggregation; realtime is only needed to parse the short command and speak the result.
- **latency:** Broadcast cancellation immediately, under 250 ms on local Mac/browser links; reconcile all receipts and speak a bounded summary within 2 seconds.
- **cost:** Negligible API cost; the main work is cancellation fan-out, idempotency, and receipt reconciliation.
- **security:** The command must be authenticated to the active pendant session and use a nonce to prevent replay. Cancellation should not delete receipts or silently undo completed external side effects; report completed, canceled, and unknown states separately. It needs a named policy entry because the current executor has no effective action gate.
- **missing:** relay-wide cancellation fan-out keyed by owner/session; Mac endpoint that atomically marks queued jobs canceled before dispatch; browser command cancellation with an acknowledgement and deadline; firmware event semantics for a panic-brake press and a local LED acknowledgement

### "When a browser automation step fails or the page changes, recover automatically: inspect the current page visually and semantically, explain the mismatch through the pendant, and continue only with the still-valid parts of the plan."
- **useful because:** Authenticated sites change constantly. Instead of a brittle failure that leaves half a workflow completed, the owner gets a resilient computer-use loop that can recognize a renamed button, a consent dialog, or a changed layout and preserve the useful work already done.
- **path:** browser-extension → mac-vision → mac-planner → relay-realtime → pendant
- **model tier:** Use a cheaper vision/background model for screenshot-to-UI reconciliation; use realtime only for ambiguity that genuinely needs the owner's spoken decision.
- **latency:** Detect failure within 500 ms, produce a replacement action within 3 seconds, and ask the owner only when confidence is below a configured threshold.
- **cost:** About $0.01–$0.10 per recovery depending on screenshot size and retries; most successful DOM recoveries should avoid a model call.
- **security:** Screenshots and DOM extracts can contain authenticated data; redact known secrets and restrict capture to the active tab. Every replacement action must be linked to the failed action and a fresh page hash, with a bounded retry count to prevent loops. Since Accessibility and Screen Recording are now granted to AI Pendant Agent, this is technically unblocked on this Mac, but it still needs explicit owner policy for unattended continuation.
- **missing:** a typed failure envelope from browser actions containing page/session hash and partial effects; Mac vision inspection that returns stable roles, labels, bounds, and screenshot redaction; planner support for conditional branches and bounded retries rather than a fixed action list; a spoken ambiguity/continue decision that can resume the same browser session


## Changes it proposed to its own stack

### `integration` — Add a USB companion transport in the Mac agent that discovers /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA, frames pendant events and ESP32 audio-bridge status, and exposes the same event schema used by relay-realtime. When LTE is unregistered, the relay can route conversations and diagnostic commands through this Mac bridge; when LTE returns, it must hand off without duplicating queued events.
- **owner gets:** The pendant becomes genuinely usable today while it is worn next to the Mac instead of waiting for cellular registration. The owner can press the real button, hear replies, run the shipped audio diagnostic, and keep bookmarks/retries working through the Mac in a dead cellular zone.
- effort: Medium-high: serial discovery/reconnect, framed protocol, ownership arbitration with firmware flashing, relay session mapping, and end-to-end testing across unplug/replug and LTE recovery.  ·  risk: A reconnect could duplicate audio or bookmarks; use sequence numbers and durable acknowledgements, with the pendant as source of truth. A bad framing bug could interfere with firmware flashing, so reserve a distinct application baud/handshake and provide an explicit maintenance mode. Recovery is automatic reconnect plus the existing offline queues.
- cost: No API cost and no new hardware. A small always-running Mac helper adds negligible CPU; serial traffic is bounded by the existing audio rate.  ·  latency: USB event latency should be under 20 ms; audio adds substantially less jitter than LTE. Handoff to LTE may take seconds and must be announced rather than silently switching.
- security: Serial devices are local-owner trusted but should be pinned by VID/PID/serial and require an explicit companion-mode setting. Do not expose raw microphone bytes to unrelated Mac processes; relay only framed, encrypted application payloads.
- depends on: a real mac_serial_exchange capability or equivalent serial read/write route; a published companion-mode event schema shared by firmware and relay; relay session handoff and deduplication keyed by device sequence number; owner-configured policy allowing the Mac to act as the pendant’s local transport


## What it asked for

_Nothing._
## Its own summary

This round I proposed four owner-visible additions: (1) pendant physical-button approval for a prepared browser form before submission, (2) automatic Mac audio ducking with exact restoration around a pendant call, (3) browser-to-local cited decision packets saved/opened on the Mac, and (4) a USB companion transport so the physically connected pendant and ESP32 work through the Mac before LTE registration. The most important missing capability is the last one: the hardware is live today, but I still cannot exchange serial frames from this harness. I also found the Mac is currently healthy: AI Pendant Agent has Accessibility and Screen Recording, synthesized input is verified, Safari has three sessions/tabs, and Calendar/Mail are available through bounded reads.

**Biggest unknown:** The exact serial framing/protocol and relay handoff contract for the USB-connected nRF9160/ESP32 remain unknown. I still need a real mac_serial_exchange (or equivalent typed serial read/write capability), plus the relay's sequence-number deduplication/session-handoff schema. The existing workbench transaction grant is unresolved in the live inventory, so atomic artifact writing still needs a real implementation path.

