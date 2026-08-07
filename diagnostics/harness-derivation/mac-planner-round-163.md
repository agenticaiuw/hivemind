# Harness derivation — mac-planner — round 163

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Tell me whether tomorrow is actually doable: reconcile my calendar, travel/appointment details in my logged-in tabs, and commitments in recent mail, then point out only impossible overlaps, missing travel time, and decisions I must make."
- **useful because:** A normal morning brief lists facts; this catches a day that cannot physically happen and gives the owner an actionable repair plan before the first meeting.
- **path:** relay-realtime → faculty-perception → browser-extension → mac-planner → faculty-judgement → faculty-action
- **model tier:** background for the overnight reconciliation; realtime only to answer follow-up questions
- **latency:** Under 2 minutes overnight; under 10 seconds for a spoken follow-up
- **cost:** Roughly $0.03–$0.12 per overnight run; browser extraction and model reconciliation dominate, not Mac actions
- **security:** Calendar/mail snippets and authenticated travel pages leave the Mac to the relay; redact unrelated message bodies, retain only cited conflict fields, and never change bookings or send mail without confirmation.
- **missing:** A cross-source temporal/entity normalizer for calendar, mail, and authenticated page extracts; A durable conflict record with citations and dismissed-conflict state; Browser watch/session access to travel and appointment pages

### "When I press the pendant button twice, save exactly where I am on the Mac as a resume card—active app, file, browser tab, selected text if available, and my spoken note—then later let me say 'resume that' and reopen the same work without hunting."
- **useful because:** The owner loses more time reconstructing interrupted work than issuing commands. This makes the worn button a physical bookmark spanning the Mac, browser sessions, and relay, including when the original app is no longer foreground.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → faculty-perception → faculty-action
- **model tier:** realtime for the short spoken note and confirmation; background for card indexing and later retrieval
- **latency:** Capture in under 1 second locally; reopen in under 5 seconds after a later request
- **cost:** About $0.005–$0.02 per capture/retrieval; speech transcription and optional selected-text summarization dominate
- **security:** Cards may contain sensitive URLs, document names, or selection text. Store encrypted locally by default, redact secrets and form fields, require an explicit spoken confirmation before sharing a card to relay, and never capture passwords.
- **missing:** A pendant double-press event and USB-serial event bridge (the device currently has one button and is physically attached but unregistered); Read-only Mac context capture for foreground app/file and browser tab identity; current inspection grant is schema-only; A resume-card store and retrieval endpoint with TTL and per-card deletion

### "If I hold the pendant button for three seconds, stop every in-flight Mac and browser action, prevent queued jobs from starting, and tell me in one sentence what was stopped; preserve receipts so I can resume safely later."
- **useful because:** A physical stop works when the screen is hidden, a browser tab is stuck, or speech recognition is wrong. It is the safest high-value cross-surface primitive: one gesture can halt the Mac executor, browser bridge, and relay job runner without asking the owner to find the right window.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-action
- **model tier:** No model for the stop path; realtime model only summarizes the already-recorded cancellation receipt afterward
- **latency:** Hardware event to cancellation under 500 ms locally; spoken receipt under 3 seconds
- **cost:** Negligible API cost; one short receipt-generation call only when the owner requests detail
- **security:** The stop signal must be authenticated to the paired device and idempotent, with no ability to delete receipts or erase evidence. Canceling a partially completed external transaction cannot undo it, so the receipt must distinguish canceled, completed, and unknown states.
- **missing:** Firmware long-press event and a reliable USB/LTE control channel; Relay-wide cancellation token checked by durable jobs and browser requests; Mac executor cancellation hook that terminates the current action without replaying it; A visible/spoken cancellation receipt

### "Show me exactly what the AI has seen and shared for this task: every source opened, excerpt retained, model handoff, and Mac/browser mutation, with a one-tap purge of the task's temporary data."
- **useful because:** The owner can authorize powerful cross-surface work today but cannot answer the basic privacy question afterward: what crossed from a private tab or document into the relay, and what still remains. A task-scoped evidence ledger makes delegation trustworthy rather than opaque.
- **path:** relay-realtime → browser-extension → mac-planner → dashboard-ux → faculty-perception
- **model tier:** No expensive realtime model for recording; use a cheap background model only to summarize the ledger into plain language.
- **latency:** Ledger entries must be synchronous (<100 ms); summary under 5 seconds.
- **cost:** Negligible storage and API cost; occasional summary generation is under $0.01 per task.
- **security:** The ledger itself is sensitive. Encrypt it locally, hash or redact content by default, separate source metadata from excerpts, enforce per-task TTL, and make purge cryptographically verifiable. Purge must not erase required external-action receipts.
- **missing:** A task-scoped provenance/egress ledger spanning relay, browser bridge, and Mac executor; A dashboard route that renders source-to-model data flow and supports verified purge; Instrumentation at every browser extraction and Mac read/write boundary

### "Prepare this action now, but do not execute it until my pendant confirms the exact final details—even if I am away from the Mac; then execute it once, and tell me whether it succeeded."
- **useful because:** The owner could safely delegate a long or sensitive browser/Mac transaction without remaining at the keyboard. The pendant supplies a physical, device-bound approval of the final target and fields, while the Mac/browser supplies authenticated reach.
- **path:** relay-realtime → pendant → mac-planner → browser-extension → faculty-judgement → faculty-action
- **model tier:** Background model prepares and verifies the transaction; realtime model handles only the short approval exchange and result.
- **latency:** Preparation can take minutes; after pendant confirmation, execution starts within 1 second and returns a receipt within 10 seconds.
- **cost:** Approximately $0.02–$0.10 per prepared transaction, dominated by authenticated-page extraction and final verification.
- **security:** Never transmit raw credentials or approval secrets through the relay. Bind a canonical transaction hash to the device, target account, tab/session, expiry, and allowed fields; reject any DOM or destination change and make approval single-use. External side effects remain distinguishable from a local cancellation.
- **missing:** A canonical transaction serializer and hash/diff verifier across browser and Mac actions; Authenticated pendant challenge-response over the current USB path and later LTE path; A durable escrow queue that survives relay/Mac restarts and expires safely; Executor preconditions checked immediately before side effect

### "Run a one-button pendant health check and tell me which link is broken—microphone, pendant speaker/I2S, USB, ESP32 Bluetooth bridge, LTE, relay, or Mac—without starting a conversation or sending any recording."
- **useful because:** When audio fails, the owner currently has no way to distinguish a dead microphone from a saturated LTE path or silent Bluetooth bridge. A private loopback plus synthetic test tone and control-plane probes would give an immediate repair instruction instead of repeated guesses.
- **path:** pendant → ESP32 audio bridge → mac-planner → relay-realtime → faculty-perception
- **model tier:** No model for measurement; use a cheap background model only to convert structured test results into one spoken sentence.
- **latency:** Complete in under 15 seconds; each component result should appear within 3 seconds.
- **cost:** Near-zero API cost; local synthetic audio and bounded health requests dominate no token spend.
- **security:** Use generated tones and counters only—never upload microphone content. Authenticate control probes, avoid changing audio routing, and retain only pass/fail plus firmware versions.
- **missing:** A firmware diagnostic mode that injects a synthetic I2S signal and reports mic/I2S counters without opening the conversation path; ESP32 bridge loopback and Bluetooth sink acknowledgement; Relay health challenge and Mac USB-serial probe; A typed result schema and spoken diagnosis


## Changes it proposed to its own stack

### `integration` — Add a local USB pendant/ESP32 session supervisor on the Mac: discover /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA, attach monotonic session IDs, tail framed UART diagnostics, detect silence/boot loops/audio underruns, and expose a single health event stream to relay and dashboard. On reconnect, send only an idempotent status request (never replay queued browser or voice commands), then publish a spoken/LED-safe 'pendant attached but relay-unregistered' state.
- **owner gets:** Today the owner cannot tell whether a failure is LTE, relay registration, the USB cable, or the audio bridge. This would make the prototype self-diagnosing at the exact moment it fails and prevent stale commands from unexpectedly running after reconnect.
- effort: Medium: a Mac launch agent plus two protocol adapters, a small event schema, and relay/dashboard display; firmware needs a read-only diagnostic/status frame if the current UART has none.  ·  risk: Serial probing can contend with an active flasher or firmware console; use exclusive-open, bounded reads, and never write except an explicit status opcode. If the supervisor crashes, the devices continue unchanged; disable it with one launch-agent toggle.
- cost: No meaningful API cost; approximately 20–40 MB resident Mac process and a few KB/day of local logs. Hardware cost $0 using the already connected boards.  ·  latency: Health events within 1–2 seconds of cable or firmware failure; no voice-path latency change.
- security: UART logs may contain transcripts, identifiers, or tokens; redact payload bytes by default, hash device IDs, and keep raw logs local with a short retention window.
- depends on: A framed, read-only diagnostic/status opcode in pendant and ESP32 firmware; A local relay endpoint accepting device-health events; A real implementation of read-only Mac inspection or a dedicated serial supervisor route


## What it asked for

_Nothing._
## Its own summary

This round produced four owner-facing directions, led by a genuinely high-value one: an overnight 'is tomorrow doable?' reconciliation across Calendar, Mail, and authenticated browser pages, reporting only impossible overlaps, travel gaps, and decisions. I also proposed a physical pendant-to-Mac/browser resume card, a USB serial supervisor that diagnoses pendant-vs-bridge-vs-relay failures without replaying commands, and a three-second physical emergency stop spanning relay, Mac, and browser jobs. Live discovery confirms Safari is online with three tabs and the Mac bridge is online; the newly granted mac_readonly_inspect calls are still schema-only and return no implementation. Hardware is physically testable over the two known USB serial paths, but the pendant is not relay-registered.

**Biggest unknown:** Whether the existing UART firmware has a framed, read-only diagnostic/status opcode and whether the Mac executor/job runner exposes cancellation hooks. I still need real implementations for read-only Mac context/inspection, serial supervision, cross-source temporal reconciliation, durable resume cards, and relay-wide cancellation; Accessibility/Screen Recording remain owner-side TCC grants and are not available from this agent.

