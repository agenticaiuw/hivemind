# Harness derivation — relay-realtime — round 100

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Take the information from the authenticated page I’m looking at, remove anything about other people or internal-only details, and send the safe summary to Alex.” The owner should be able to speak a recipient, redaction rule, and destination from the pendant, then receive a spoken preview and say “send” to deliver it."
- **useful because:** Today the wearable, browser session, and Mac each work in isolation: the browser can see private content, the relay can hear the instruction, and the Mac can send, but none can safely transform private page content into a recipient-specific message with an auditable explanation. This gives the owner a practical away-from-desk privacy workflow without exposing the whole page to the recipient.
- **path:** pendant → relay → browser-extension → browser → mac-planner → mac-terminal
- **model tier:** Realtime relay only extracts recipient, destination, source tab, and redaction constraints and speaks the preview. A cheaper background model performs deterministic field-level redaction and produces a short diff; mac-planner handles the final compose/send action.
- **latency:** Acknowledge intent in under 500 ms, return a preview within 5–10 s, and deliver within 3 s after the explicit “send” utterance. If the browser or Mac is offline, retain a clearly marked draft rather than pretending delivery happened.
- **cost:** Roughly $0.01–$0.08 per request depending on page size; browser extraction and model input tokens dominate, while relay speech/intent is small. A compact extracted representation and redaction diff should avoid resending the full page on every turn.
- **security:** Authenticated page content and the proposed message necessarily leave the browser session and may reach the relay/model; transmit only the selected DOM/text fields, never cookies or screenshots unless requested. The redactor must preserve provenance and mark uncertain removals. Sending is an external side effect, so require the owner's explicit send utterance after hearing or reading the final preview; store a receipt containing recipient, source tab, redaction policy, and resulting message, not the private source.
- **missing:** A browser command that extracts selected text/DOM from one identified authenticated tab and returns stable field provenance; A recipient-aware redaction/diff service with deterministic rules and uncertainty reporting; A durable draft that survives Mac/browser disconnects and a single idempotent send operation; A spoken preview plus final-send state machine and delivery receipt shared by relay and Mac


## Changes it proposed to its own stack

### `firmware` — Add a playback receipt protocol that is local-first and idempotent: every spoken response carries a monotonically increasing utterance id and a short checksum; the pendant emits PLAY_STARTED, PLAY_FINISHED (or PLAY_INTERRUPTED), and PLAY_REPLAYED acknowledgements over the existing uplink, persists the last few ids in its small durable store, and suppresses duplicate audio after reconnect. The relay keeps the response pending until it receives a receipt, retries only when safe, and exposes the receipt beside the downstream Mac/browser action receipt.
- **owner gets:** The owner will know whether an important answer or completion announcement was actually heard, rather than silently missing it while walking, driving, or in LTE dead zones. A dropped connection will not cause the same reminder or sensitive result to be spoken twice, and “did that happen?” can be answered from a real device-level fact.
- effort: Medium: define a tiny event schema, add pendant audio-state callbacks and a bounded receipt journal, then add relay deduplication/retry and a test harness for power loss, interruption, and reconnect.  ·  risk: A false PLAY_FINISHED could create unwarranted confidence, so distinguish started, finished, and user-interrupted states and never translate silence into success. Lost receipts may leave a response pending; recover by querying the pendant journal on reconnect. Firmware wear and journal corruption are handled with a tiny ring buffer and checksums.
- cost: Negligible API cost; a few LTE uplink packets per spoken response. Firmware storage is a small ring (for example 8–32 ids plus checksums), with no meaningful application RAM increase.  ·  latency: No added speech-start latency. Completion bookkeeping adds at most one uplink round trip; retries are asynchronous and should not block the next utterance.
- security: Use opaque ids and checksums, never audio or transcript in receipts. Bind receipts to the authenticated pendant/session so another device cannot falsely acknowledge playback.
- depends on: A verified pendant-to-relay uplink event endpoint and reconnect handshake; A shared idempotent response/operation identifier across relay, Mac planner, browser, and action receipts; Pendant firmware access to playback start/end/interruption callbacks


## What it asked for

_Nothing._
## Its own summary

Discovered the currently available toolset and grants, confirmed device and surface status, and verified that relay_route_intent and server_browser_actions are granted as schemas only (not implemented), while relay_job_status is available and should be used for status checks of already-handed-off Mac work. Noted that the browser is offline and the Mac bridge is online, so Mac-mediated actions are feasible if needed.

**Biggest unknown:** Whether the newly granted intent-routing and server-side browser capabilities will be implemented this run; without implementations, the relay still cannot safely route intent via a standard tool or perform browser work without the Mac. I also still need a way to inventory relay-native routes/capabilities without blind probing.

