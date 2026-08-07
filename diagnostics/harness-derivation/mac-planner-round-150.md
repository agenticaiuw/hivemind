# Harness derivation — mac-planner — round 150

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“When I tap the pendant twice, save the thing I’m looking at for later.”"
- **useful because:** This is the single most useful everyday bridge: a physical, low-friction capture gesture turns the currently active Safari page (including a logged-in page), the relevant browser evidence, and my spoken note into a durable, searchable Mac capsule. It works today over USB even though the pendant is not LTE-registered, and syncs to the relay when connectivity returns.
- **path:** pendant → mac-bridge → browser → relay → dashboard
- **model tier:** Realtime only for an optional spoken note; deterministic extraction, hashing, and storage should be background/cheap model or no model.
- **latency:** Acknowledge the tap locally/over USB in under 300 ms; create the capsule and return a receipt within 3 seconds.
- **cost:** Usually <$0.01 per capture; dominated by optional speech transcription/summarization, not page capture.
- **security:** Logged-in page content can be private. Store redacted metadata by default, encrypt local capsule contents, preserve tabId/URL/time/source hashes, and require an explicit spoken phrase to include page body or secrets. Never submit or alter the page.
- **missing:** A pendant USB-serial event reader and double-tap debounce path; A Mac bridge endpoint that atomically snapshots active-tab context and writes a capsule; A durable capture schema with encrypted body, source citation, retention and later relay sync; A browser command for active-tab extraction with bounded content and redaction

### "“Put me in focus mode until I tap again, but let truly urgent things through.”"
- **useful because:** A pendant gesture can change the owner's interruption policy without opening an app: Mac Shortcuts and notifications enter a quiet mode, Safari watches and relay jobs continue in the background, and only scored urgent events produce a haptic/audio alert. A second tap restores the prior state and reports anything deferred.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Cheap background classifier for urgency; realtime model only when the owner asks why an alert was allowed through.
- **latency:** Mode transition under 1 second over USB; urgent-event decision under 5 seconds; restoration must be immediate.
- **cost:** <$0.005 per event with rules-first filtering; model calls only for ambiguous notifications.
- **security:** Do not read notification bodies or browser content unless the owner has enabled that source. Keep an auditable allow/defer log, preserve the exact prior Focus/Shortcuts state, and fail open to the owner's prior state on disconnect.
- **missing:** Firmware gesture event over the currently connected serial link; A Mac Focus/notification state adapter with save-and-restore transaction; Relay-to-Mac urgent event push and deduplication; A shared urgency policy and deferred-event queue

### "“If the pendant is plugged into my Mac, let it be my offline command button; run the command locally and sync the receipt later.”"
- **useful because:** The pendant is physically real now but LTE registration is not. This makes that limitation useful rather than blocking: taps or short button codes can launch a Shortcut, open a known file, start a work routine, or capture a note with no relay round trip. When the relay returns, it uploads signed receipts and reconciles duplicates.
- **path:** pendant → mac-bridge → relay → dashboard
- **model tier:** No model for known button mappings; background cheap model only to reconcile a free-form queued note.
- **latency:** Known command execution begins within 500 ms and receipt is durable before acknowledgment; reconnect reconciliation within 10 seconds.
- **cost:** Near-zero API cost for mapped commands; <$0.01 only for optional note interpretation.
- **security:** Restrict offline commands to an owner-configured allowlist and show a physical LED/audio acknowledgment. Include monotonic event IDs, replay protection, and durable receipts. Do not expose arbitrary shell or browser mutations through an unpaired serial device.
- **missing:** Pendant serial framing, pairing key, monotonic event counter, and local acknowledgment; Mac daemon/bridge that maps signed events to Shortcuts and /execute actions; Relay upload/reconciliation endpoint for offline receipts; Dashboard UI for configuring mappings and reviewing failed/replayed events

### "“If you’re about to say something private out loud, keep it off the speaker and show me the safe way to access it.”"
- **useful because:** Today the system can speak through the relay or Mac, but it cannot reliably distinguish a private message, account detail, or page content that should not be audible around other people. This capability would classify sensitivity before delivery, route ordinary content to audio, and route sensitive content to a private Mac panel or a short haptic code that I can expand deliberately. The owner gets useful ambient assistance without accidental disclosure.
- **path:** relay-realtime → mac-bridge → browser → pendant → dashboard
- **model tier:** Realtime model may identify conversational sensitivity; deterministic redaction and routing should run locally/cheaply, with no sensitive text sent to another model after classification.
- **latency:** Decide the route within 150 ms of response generation; private panel ready within 2 seconds.
- **cost:** Negligible for rules-based classification; <$0.002 for occasional ambiguous sensitivity classification.
- **security:** Sensitive text must never be placed in audio buffers, logs, or telemetry when the private route is selected. Keep the classifier conservative, expose a visible private-mode indicator, and allow an owner-configured vocabulary of never-speak fields.
- **missing:** A pre-output sensitivity classifier and policy engine shared by relay and Mac; A private Mac display/notification channel that does not steal focus; A pendant haptic/LED code and expansion gesture; End-to-end tests proving sensitive values do not enter TTS or receipts

### "“Give me a physical away-mode lease: keep doing the safe work while I’m gone, and stop cleanly when I take the pendant back.”"
- **useful because:** The owner cannot have a trustworthy boundary between 'continue while I’m away' and 'stop because I am back.' A pendant-held lease would let relay, Mac, and browser run a bounded plan under an explicit physical presence token. Removing or tapping the pendant ends the lease, freezes drafts and queued mutations, and returns a precise reconciliation when the owner returns. This is different from merely running a background job: the wearable is the live authority for the work interval.
- **path:** pendant → relay-realtime → mac-bridge → browser → dashboard
- **model tier:** Cheap background planner for safe steps and reconciliation; realtime only for starting, stopping, or explaining the lease conversationally.
- **latency:** Lease start/stop acknowledgment under 500 ms over USB or 2 seconds over relay; stop propagation under 3 seconds.
- **cost:** <$0.01 per bounded plan; dominated by browser extraction or optional summarization.
- **security:** Lease must be short-lived, signed, monotonic, and scoped to named apps/sites/actions. Disconnect should pause rather than silently continue. Never treat a lost link as approval to send, purchase, delete, or publish.
- **missing:** Pendant presence-token protocol with expiry and revocation; Relay lease coordinator and stop propagation; Mac/browser workers that checkpoint and pause at safe boundaries; A dashboard showing exactly what ran, what was held, and why

### "“When I am near my Mac, let the pendant silently tell it which mode I am in; when I leave, make the Mac stop surfacing private context.”"
- **useful because:** The owner should not have to repeat privacy and attention instructions every session. A physically present pendant can establish a local, short-lived presence mode—private, shared-room, or away—and the Mac/browser/relay can adapt display, spoken output, and page-context retention accordingly. This turns physical context into an enforceable privacy boundary rather than a preference buried in prompts.
- **path:** pendant → mac-bridge → browser → relay-realtime → dashboard
- **model tier:** No model for presence and mode propagation; background model only to suggest a mode from calendar/location-like signals, never to override the physical setting.
- **latency:** Mode propagation under 1 second locally and under 5 seconds to relay; stale modes expire automatically.
- **cost:** Near-zero API cost; only optional mode suggestions incur model cost.
- **security:** Use proximity/USB attestation rather than microphone or camera. Expire modes, show current mode on Mac and pendant, and ensure leaving/serial loss removes private page text from new spoken responses and browser captures.
- **missing:** Local pendant-to-Mac presence attestation and mode buttons; A shared privacy-mode state with TTL and disconnect semantics; Output routing and browser extraction hooks that honor the mode; A dashboard control and audit trail


## Changes it proposed to its own stack

### `firmware` — Add a signed, monotonic USB-serial event protocol for the physically attached nRF9160 pendant: button-down/up, double-tap classification, battery level, firmware version, event counter, CRC, and local LED/beeper acknowledgment. Buffer a small ring of events through transient disconnects and expose pairing status.
- **owner gets:** The owner can use the pendant as a reliable physical control surface today while LTE is unavailable, instead of the device being inert whenever it is not registered.
- effort: Medium: firmware framing/debounce/ring buffer plus a Mac serial reader and test fixture.  ·  risk: Bad debounce could create duplicate actions; replay protection and idempotent event IDs prevent repeats. If the bridge disappears, the pendant should acknowledge queued-but-not-executed rather than pretending success.
- cost: No API cost; under 16 KB flash and 4 KB RAM target, negligible power increase.  ·  latency: Local classification <50 ms; USB delivery typically <200 ms.
- security: Pair the pendant to the Mac with a device key and authenticate frames; never accept arbitrary commands from the Mac without a paired identity.
- depends on: A Mac serial reader/bridge process; A shared event schema and replay-deduplication store

### `integration` — Create a cross-surface 'capsule transaction' that snapshots active Safari tab metadata and bounded redacted text, stores it locally with a source hash and retention deadline, then asynchronously uploads only the encrypted capsule and receipt to relay when reachable.
- **owner gets:** A single tap or spoken phrase gives the owner a trustworthy later reference to exactly what they saw, rather than an untraceable note or a broken link after the tab changes.
- effort: Medium-high: browser extraction, local encrypted store, retention worker, relay sync and dashboard viewer.  ·  risk: Private content could be over-collected; default to title/URL/selection and require an explicit include-body command. Handle tab closure and relay outages without losing the local capsule.
- cost: <$0.01 per optional summary; storage and hashing dominate otherwise.  ·  latency: Local receipt in <3 s; summarization/upload deferred.
- security: Encrypt at rest and in transit; redact email addresses, tokens, and payment identifiers; bind evidence to tabId, URL, timestamp, and hash.
- depends on: Authenticated browser extraction for the active tab; A durable local capsule store with retention; Relay upload/reconciliation route


## What it asked for

_Nothing._
## Its own summary

Round 150 established that the Mac agent, browser extension, and relay are online, with Safari exposing Gmail plus two failed example.com tabs; there are no pending browser commands. Accessibility and Screen Recording remain unavailable, while AppleScript automation is granted. I recorded three non-duplicate cross-surface capabilities: pendant double-tap capture of the active private page into an encrypted capsule, a pendant-controlled focus mode with urgent-event escape, and an offline USB pendant command plane with later relay receipt reconciliation. I also proposed the required signed serial firmware protocol and capsule transaction integration, and notified unified.

**Biggest unknown:** The missing implementation boundary is the physical serial bridge: whether the current Mac host can read and authenticate the nRF9160 USB serial stream and whether the pendant firmware can emit button events. That determines how quickly the offline command and capture capabilities can become runnable.

