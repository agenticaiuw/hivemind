# Harness derivation — mac-planner — round 168

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Test the pendant now and tell me, in one sentence, whether its microphone, radio link, and speaker are healthy.”"
- **useful because:** This is the highest-value thing the owner can get from the currently USB-attached hardware: one deliberate test exercises the real nRF9160 and ESP32 path, the Mac serial bridge collects measured counters, and the relay turns them into a spoken pass/fail with the failing subsystem named. It replaces guessing when audio or connectivity is bad and can automatically leave a timestamped diagnostic artifact in the workspace.
- **path:** pendant → mac-planner → relay-realtime
- **model tier:** Use a cheap background model to interpret the bounded fixture counters and classify pass/fail; reserve realtime only for speaking the result if the owner is in a live session.
- **latency:** 15–30 seconds for fixture execution and serial collection; under 2 seconds to summarize after the receipt arrives.
- **cost:** About $0.01–$0.05 per test, dominated by a short structured summary; no audio transcription is needed because the fixture is synthetic.
- **security:** The fixture must never record microphone content. UART logs may contain identifiers, so redact device IDs before relay upload. Writing a report is local and reversible; any firmware flashing must be a separate explicit operation.
- **missing:** A Mac serial-bridge action that can arm the already-accepted audio_path_diagnostic_fixture over /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA, stream bounded logs, and return a typed receipt.; A relay endpoint that accepts the fixture receipt, applies numeric acceptance thresholds, and generates a short spoken status.; A workspace report writer that atomically stores the receipt and firmware/build identifiers.

### "“Watch this authenticated tab until tomorrow, and tell me only if the page materially changes; when it does, put a one-sentence alert on my pendant with the old and new values.”"
- **useful because:** The browser can see sessions the relay cannot, while the pendant is the only surface that can interrupt the owner without opening a laptop. A scoped diff watcher turns a page that changes silently (status, appointment slot, price, queue position, dashboard metric) into a durable, low-noise alert instead of repeated full-page summaries.
- **path:** browser-extension → relay-realtime → mac-planner → pendant
- **model tier:** Use deterministic DOM/text extraction and hashing first; invoke a cheap background model only to classify whether a changed region is material and phrase the one sentence. Realtime is unnecessary except for immediate delivery.
- **latency:** Poll or extension-push within 1–5 minutes of a page change; alert generation under 3 seconds. Expire automatically at the requested deadline.
- **cost:** Usually under $0.01 per change, with most checks requiring no model call; cost is dominated by occasional classification of a changed snippet.
- **security:** The extension must keep credentials and full page contents local, send only the owner-selected URL/region and redacted before/after snippets, and never submit forms or click. Each watcher needs an explicit expiry and a visible stop control. Alerts may expose sensitive values over the pendant, so provide a private/metadata-only mode.
- **missing:** A browser watcher primitive that can subscribe to an already-open authenticated tab and return a bounded, redacted region diff rather than a full page.; Relay persistence for watcher definitions, last hash, expiry, and deduplication state.; A pendant inbox payload type for before/after summaries with expiry and an acknowledgement action.

### "“After you change something on my Mac, tell me what changed on the pendant and let me undo the last reversible change with one press.”"
- **useful because:** The owner currently has to trust a silent desktop action or ask later what happened. A compact spoken receipt closes the loop across the Mac executor and the worn device; for reversible actions, a physical press can undo without finding the original app, while irreversible actions are reported as final and never offered a fake undo.
- **path:** mac-planner → relay-realtime → pendant
- **model tier:** No expensive reasoning is needed: generate the receipt deterministically from the Mac job result and action ledger. Use realtime only when the owner is already in conversation; otherwise queue a short alert for the existing pendant inbox.
- **latency:** Receipt within 1 second of the Mac job completing; undo dispatch within 2 seconds of a button press.
- **cost:** Near-zero model cost for structured receipts; at most a few cents if natural-language compression is requested.
- **security:** The pendant must expose only a redacted action summary, not file contents or secrets. Undo tokens must be single-use, bound to the job and device, expire quickly, and be offered only where the existing receipt says an inverse is valid. The existing owner rule still applies: sending mail, deleting files, and purchases remain final/confirmation-required rather than pretending reversible.
- **missing:** A relay endpoint to publish Mac job receipts into the pendant inbox with a typed undo token.; A firmware inbox action for acknowledge/undo that does not overload the existing recording button semantics.; A Mac executor endpoint that accepts a validated receipt undo token and invokes only the recorded inverse.

### "“Prepare this form in the browser and my Mac, show me exactly what will be submitted on the pendant, and submit it only when I press the pendant button; afterward verify the server’s response and tell me if it actually took.”"
- **useful because:** Today the browser can hold authenticated sessions and the Mac can act, but there is no trustworthy end-to-end transaction boundary. This would let the owner delegate tedious form completion without surrendering the final decision: the pendant displays a compact, redacted diff, a physical press authorizes exactly that prepared payload, and a fresh read-back verifies success instead of assuming a click worked.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** Use a deterministic planner and DOM/value diff for preparation and verification; use a small background model only to compress long fields into a spoken/pendant summary. Realtime is needed only if the owner is conversing during the final approval.
- **latency:** Preparation in under 10 seconds for a normal form; owner review is unbounded; submission and verification within 5 seconds after the button press.
- **cost:** Typically $0.01–$0.05 per transaction, mostly for summarizing changed fields; browser and Mac operations dominate wall time rather than inference.
- **security:** Never transmit passwords or full sensitive fields to the relay; keep them in the browser session and display masked values. Bind the approval token to tab/session, URL origin, exact field hashes, expiry, and one submission. A changed page, navigation, or server-side value mismatch must invalidate the token. Purchases, mail sends, and other high-impact actions remain explicitly classified so the owner’s existing confirmation preference is honored.
- **missing:** A browser transaction journal that can freeze a prepared form’s origin, field hashes, and submit action without clicking it.; A relay-issued, single-use approval token that the pendant firmware can present and return on a physical button event.; A browser-side post-submit verifier that performs a bounded read-only confirmation and reports the resulting record/status.; A cross-surface diff renderer that can safely summarize arbitrary form fields while redacting secrets.


## Changes it proposed to its own stack

### `integration` — Add a USB-serial transport adapter that treats the physically attached nRF9160 pendant as a first-class local relay link while LTE-M is unregistered. It should exchange the existing durable inbox/outbox manifests (bookmarks, alerts, retryable audio receipts), use sequence numbers and acknowledgements, deduplicate by event UUID, and expose link state separately from cellular registration. The Mac adapter must never pretend this proves over-the-air behavior; it should label receipts usb_serial and preserve the same payload limits.
- **owner gets:** The owner can use the worn device’s offline capture and alert behavior today, at their desk, instead of waiting for a cellular registration that does not exist. A bookmark or queued alert becomes testable end to end now, and later cellular sync can consume the same records without losing or duplicating them.
- effort: Medium: a local serial framing/daemon integration, relay transport selection, and a small interoperability test against both live USB ports.  ·  risk: A reconnect or partial write could duplicate or corrupt queue items; use UUID-based idempotency, length/checksum framing, atomic manifest updates, and keep unacknowledged records on the device. Do not route microphone audio through an unbounded serial buffer. Recovery is automatic retry and a visible transport label in receipts.
- cost: Negligible API cost; roughly 1–2 weeks engineering. No hardware cost or meaningful power change while USB-connected.  ·  latency: Sub-second for bookmarks and alert manifests; audio remains bounded and may take seconds depending on serial throughput.
- security: USB access exposes device events to the trusted Mac. Keep the serial channel authenticated or physically scoped, redact event text in logs, and never treat USB presence as authorization for destructive Mac actions.
- depends on: A serial adapter for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; Relay transport abstraction that can ingest the existing pendant_store manifests; A typed receipt field distinguishing usb_serial from LTE/WebSocket


## What it asked for

### `t21-1g36` (tool) — mac_serial_exchange
- why: The pendant and ESP32 bridge are physically connected over USB serial now, but the granted Mac tools can launch apps and inspect directories yet cannot open a serial device, stream bounded diagnostic frames, or send the accepted fixture trigger. This is the missing action between the live hardware and the relay.

```json
{
  "type": "object",
  "properties": {
    "operation": {
      "type": "string",
      "enum": [
        "list_ports",
        "open",
        "write_frame",
        "read_frames",
        "close"
      ]
    },
    "port": {
      "type": "string",
      "enum": [
        "/dev/cu.usbmodem00096003658",
        "/dev/cu.usbserial-0287A9CA"
      ]
    },
    "baud": {
      "type": "integer",
      "minimum": 1200,
      "maximum": 921600
    },
    "payload_base64": {
      "type": "string"
    },
    "max_frames": {
      "type": "integer",
      "minimum": 1,
      "maximum": 200
    },
    "timeout_ms": {
      "type": "integer",
      "minimum": 50,
      "maximum": 30000
    },
    "session_id": {
      "type": "string"
    }
  },
  "required": [
    "operation"
  ]
}
```

## Its own summary

Round 168 produced three owner-facing directions: USB-serial opportunistic pendant↔Mac transport for the currently attached, LTE-unregistered hardware; authenticated-tab material-change alerts delivered to the pendant; and Mac-action receipts with bounded one-press undo for genuinely reversible work. I also queued a concrete `mac_serial_exchange` tool request with typed port/operation bounds. The most immediate blocker is not model capability: it is a bounded serial adapter that can arm the already-accepted diagnostic fixture and synchronize pendant_store manifests without shell access.

**Biggest unknown:** Whether the live Mac bridge already has an undocumented serial framing protocol and firmware command IDs for the nRF9160 and ESP32 ports. I need that contract (or permission to inspect the UART stream through the requested tool) before claiming the USB transport can be implemented safely.

