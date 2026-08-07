# Harness derivation — mac-terminal — round 133

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Press the pendant button and read me what I’m looking at.”"
- **useful because:** This is the first genuinely wearable, end-to-end action: a button press on the device selects the owner’s current Safari page, the Mac reads the authenticated page it can actually access, and the ESP32/A2DP bridge speaks the answer without requiring the owner to touch the keyboard. It degrades to a queued request while USB is briefly unavailable and never claims a page was read unless the Mac receipt and audio delivery both confirm it.
- **path:** pendant → mac-planner → browser-extension → mac-terminal → relay-realtime
- **model tier:** Use a cheap local intent classifier for the fixed button command and page extraction; reserve realtime for summarization or a follow-up question. The Mac/browser agents do retrieval; the model only summarizes cited text.
- **latency:** Button acknowledgment under 150 ms locally; page extraction 1–3 s; spoken first sentence within 4 s. USB-tethered operation is testable today; LTE relay fallback is future work.
- **cost:** Usually one small summarization call, roughly $0.002–$0.02 depending on page length; extraction, routing, and audio transport dominate latency rather than tokens.
- **security:** Authenticated page text leaves the Mac only if summarization is remote; redact passwords, payment fields, and hidden form values before sending. Never read a different tab silently: announce title and origin first, and say unavailable on ambiguous or stale browser receipts.
- **missing:** A button-event bridge from the USB-connected nRF9160 to the Mac local agent; A current-tab browser read action that returns URL/title plus cited text and rejects stale tab identity; A Mac-to-ESP32 audio enqueue path with delivery receipt and a small offline queue; A truthful end-to-end receipt joining page identity, summary, and audio playback

### "“When I’m offline, let me tap the pendant to run my usual Mac shortcuts and tell me whether each one worked.”"
- **useful because:** Today a wearable request depends on the relay and model path, even though the pendant is physically USB-connected to the Mac. A tiny local command deck would make volume, brightness, focus, pause/play, and a predefined ‘save my current work’ scene available during internet outages or relay downtime, with haptic acknowledgment and spoken/result feedback only after the Mac confirms execution.
- **path:** pendant → mac-terminal → mac-planner → mac-vision → relay-realtime
- **model tier:** No model for the fixed shortcuts; use a local finite-state button interpreter. Use a cheap model only when the owner asks to change the shortcut deck. Realtime is unnecessary.
- **latency:** Local tap acknowledgment under 100 ms; Mac action and result under 500 ms for settings, under 5 s for a multi-action scene.
- **cost:** Near-zero API cost for fixed intents; occasional configuration call under $0.01. USB serial and Mac action latency dominate.
- **security:** The deck must contain only owner-approved intents and no arbitrary text entry. Do not treat a tap as proof that an action succeeded: return the Mac receipt, and haptically distinguish success, failure, and unavailable link.
- **missing:** A firmware button-sequence interpreter and persistent shortcut table; A USB serial command protocol with sequence numbers and acknowledgments; A Mac local endpoint that executes named scenes and returns typed results; A pendant/bridge result feedback path that works without relay connectivity

### "“When I walk away from my Mac, protect my private browser tabs automatically, and restore them when I come back with the pendant.”"
- **useful because:** The current system can operate authenticated Safari but has no physical-presence privacy boundary. A pendant-backed proximity state would lock or blur sensitive tabs, pause private audio, and invalidate queued browser actions when the owner leaves; return would restore the session only after the same pendant is present. This protects logged-in work even when the owner forgets to lock the Mac.
- **path:** pendant → mac-terminal → browser-extension → mac-planner → relay-realtime
- **model tier:** Deterministic device-presence and browser policy logic; no model call for lock/restore. Use a cheap model only to classify which open tabs are private when the owner first opts in.
- **latency:** Leave detection and privacy action within 2 s; return restoration within 3 s after stable presence. Must work with relay offline.
- **cost:** No per-event API cost; modest local storage and BLE/proximity hardware cost.
- **security:** Presence is not identity for high-impact actions: never use it alone to submit forms or send messages. Store only tab/session identifiers and encrypted policy state, not page contents. Recovery must default to locked if the signal is ambiguous or the pendant battery dies.
- **missing:** A production proximity channel (BLE companion or equivalent; nRF9160 alone is not a BLE wearable); A Mac daemon with lock/blur and audio-pause hooks; Browser extension APIs for tab redaction, action cancellation, and exact session restoration; A signed device identity and replay-resistant presence protocol

### "“Watch me do this once, then let me repeat the routine from the pendant without asking me to explain every step.”"
- **useful because:** The owner can teach a routine by completing it once across Safari and Mac apps—such as opening a work dashboard, exporting a report, and filing it locally—then invoke it with a button sequence or short phrase. The system would replay only the recorded concrete steps, re-checking the target tab and visible preconditions at each boundary, and stop with a concise haptic/spoken explanation when the page has changed.
- **path:** pendant → browser-extension → mac-vision → mac-planner → mac-terminal → relay-realtime
- **model tier:** Use a cheap background model to turn a completed receipt trace into a named routine and identify stable versus variable fields. At invocation, deterministic typed actions do the work; realtime is reserved for ambiguity or a repair question.
- **latency:** Teach-time compilation under 10 s; invocation starts within 300 ms and completes at the underlying workflow speed. A changed-page repair question within 5 s.
- **cost:** One small compilation call per new routine, roughly $0.01–$0.05; repeat invocations usually have no model cost unless repair is needed.
- **security:** Never record passwords, tokens, arbitrary keystrokes, or page text by default. Show the owner the captured action outline and variable fields; keep routines local and require an explicit opt-in for any irreversible step. A failed precondition must stop, not guess.
- **missing:** A cross-surface trace format that captures typed actions and stable preconditions rather than screenshots alone; A routine compiler and versioned local library; Browser and Mac replay adapters with semantic precondition checks; A pendant command registry and spoken/haptic success/failure result


## Changes it proposed to its own stack

### `integration` — Add an end-to-end truth ledger for every cross-surface action. At creation, bind the request to the exact browser tabId/windowId and Mac jobId; at completion, require matching URL/origin/title, action receipt, and (for spoken output) an audio enqueue/playback acknowledgment. If any identity or delivery edge disagrees—as the current logs do, where a Portal watch reports an Order 42 URL—publish a distinct PARTIAL/UNKNOWN result with the conflicting evidence rather than success. Expose a compact owner-readable timeline and machine-readable reconciliation reason.
- **owner gets:** The owner will stop hearing confident answers about the wrong tab or believing that audio was delivered when only text generation succeeded. Failures become understandable and recoverable instead of silently corrupting trust.
- effort: Medium: a shared correlation schema, validators in browser and Mac result adapters, and a small status projection; no model training required.  ·  risk: Some currently successful jobs will be labeled partial when their old adapters omit evidence. Recover by showing the raw receipt and offering a retry against a freshly enumerated tab.
- cost: Negligible storage; reduces wasted model calls by preventing summaries of stale or mismatched pages.  ·  latency: Adds tens of milliseconds for validation; avoids long wrong answers and retries.
- security: Improves containment by preventing data from one authenticated tab being attributed to another; retain only hashes/snippets needed for audit.
- depends on: Implement the pending truthful action status / USB link beacon concepts or equivalent receipt fields; Browser adapter must return stable tab identity and canonical origin; Audio bridge must emit a delivery acknowledgment

### `mac-harness` — Build a command capsule and recovery loop around unrestricted run_shell without adding gates: capture resolved cwd, argv/command text, selected environment fingerprints, start/end monotonic time, exit code, stdout/stderr separately with bounded tails plus content hashes, and files/processes explicitly touched when observable. Classify failures into transient (retry with the same capsule), context (offer the exact cwd/path correction), semantic (do not retry), and interrupted/USB-lost (persist capsule for resume). Let the planner request a replay or a parameter edit from the capsule, and attach every attempt to the existing job receipt/undo record.
- **owner gets:** When a command fails—or succeeds in the wrong directory—the agent can explain exactly what happened and continue instead of guessing. Long tasks can resume after a USB disconnect or Mac sleep, while the owner still keeps the maximum-access policy.
- effort: Medium-high: executor instrumentation, bounded artifact storage, failure classifier, and resume API; preserve arbitrary command execution exactly as today.  ·  risk: Capturing environment or output can expose secrets and large files; default to allowlisted environment names, redact common tokens, cap output, and let the owner delete capsules. A replay can repeat irreversible side effects, so mark replay as repeat-risk in the receipt rather than blocking it.
- cost: Small storage and one cheap classifier call only on failures; fewer expensive planner retries.  ·  latency: Under 100 ms instrumentation overhead; retries happen only when useful.
- security: Better auditability without reducing capability, but capsules must be encrypted/local-only by default and never upload raw stdout automatically.
- depends on: Existing GET /jobs and receipt records; An implemented local-agent job lifecycle/status route; The pending USB disconnect job cache can provide durable interruption storage

### `hardware` — Replace the prototype nRF9160 DK’s tiny/contended application flash arrangement with a production pendant carrier that adds 8–16 MB external QSPI NOR flash, a real haptic motor, and a debounced multifunction button while retaining USB serial and the nRF9160 modem. Use the flash as an append-only encrypted event spool for button intents, delivery receipts, and short generated-audio indexes—not raw microphone audio. The firmware should compact acknowledged records and reserve a fixed emergency partition for link-loss recovery.
- **owner gets:** A button press remains reliable through Mac sleep, cable movement, or a relay outage: the pendant can acknowledge “queued,” then later prove what was acted on and what was spoken instead of losing the request or pretending it happened. Haptic feedback makes queued/success/failed states usable without looking at a screen.
- effort: High: new carrier/PCB, QSPI driver and wear leveling, haptic power driver, enclosure and battery validation; prototype with an SPI flash breakout on the live USB-connected board first.  ·  risk: Power and RF layout changes can reduce battery life or modem performance; mitigate with write batching, brownout-safe records, and a hardware-in-loop endurance test. Flash wear or corruption must fail closed to a visible haptic error, never fabricate delivery.
- cost: Roughly $3–8 in flash, motor, driver, and PCB BOM at volume; tens of milliwatts only during writes/haptic pulses, negligible idle draw. No per-call API cost.  ·  latency: Button acknowledgment becomes local and sub-100 ms; durable write adds roughly 5–20 ms per event.
- security: Encrypt the spool with a device key and erase it on owner reset; do not persist page text, credentials, or raw audio.
- depends on: Define the cross-surface truth-ledger event schema; USB link/queue firmware integration; Production pendant carrier rather than the current development kit


## What it asked for

_Nothing._
## Its own summary

Discovered live devices (Safari with 3 tabs and online Mac bridge), current jobs/logs, and the nRF9160/ESP32 hardware limits. Proposed three new owner-facing steps: (1) the most useful wearable workflow—press the pendant button to read the exact authenticated Safari page aloud through the ESP32/A2DP bridge, with truthful delivery state; (2) an end-to-end truth ledger that rejects mismatched tab/URL/audio receipts as PARTIAL or UNKNOWN (current logs already show Portal reporting Order 42); and (3) a maximum-access shell command capsule with cwd/output/exit evidence and failure recovery, without adding gates. Also proposed production pendant external QSPI event storage plus haptic feedback so requests survive cable/sleep/link loss. I told faculty-action about the receipt-integrity issue.

**Biggest unknown:** The missing implementation seams: USB button-event ingestion from the connected nRF9160, stable current-tab extraction with identity guarantees, Mac-to-ESP32 audio delivery acknowledgment, and a durable local-agent job lifecycle/capsule store. Existing routes/tools expose pieces, but they do not yet prove the entire request-to-audio chain. I do not need another permission this round; those are engineering work items.

