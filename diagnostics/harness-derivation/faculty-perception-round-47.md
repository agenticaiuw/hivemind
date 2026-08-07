# Harness derivation — faculty-perception — round 47

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac UI perception readiness after requested grant** — As of 2026-08-07T11:32:10Z, the running AI Pendant Agent binary is still not trusted for Accessibility and lacks Screen Recording; inputReachability is failed and uiActionsWillReachTheScreen=false. Any ui_click/type/keypress receipts are explicitly untrustworthy. Browser extension is offline with 4 pending commands. Relay and Mac bridge are reachable, but ops permissions.ready=false.
  - evidence: GET /observe and GET /ops/status both returned HTTP 200 with accessibility.trusted=false, screenRecording.granted=false, inputReachability.status=failed, browser.online=false; /ops/status relay.macBridgeOnline=true.

## Capabilities it proposed

### "“Did that actually happen?” — after you work on my Mac, browser, or pendant, verify the real-world result and tell me what is proven, what is only reported, and what could not be checked."
- **useful because:** Today the Mac agent can report success while Accessibility/input is ineffective, and the browser can be offline with queued commands. This gives the owner an honest answer instead of a false completion, especially for reminders, edits, navigation, and private-page work.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use deterministic probes and receipts first; use a cheap background text model only to reconcile conflicting evidence and produce the short explanation. Reserve realtime for the spoken follow-up.
- **latency:** 2–5 seconds for local observation and receipt reconciliation; up to 30 seconds for browser reattachment or a background evidence sweep. Speak immediately with a provisional status if verification is delayed.
- **cost:** Usually near-zero model cost for typed probes; roughly $0.001–$0.01 when a small model must reconcile multiple evidence records. Dominant cost is screenshots/page extraction, not reasoning.
- **security:** Evidence may include private browser text, file paths, and screenshots; keep raw evidence on the Mac, send only hashes, redacted snippets, and status to relay. Never claim verified when permissions are degraded. Require confirmation before any retry that could duplicate an irreversible action.
- **missing:** A cross-surface verification record linking intended action, action receipt, and independent postcondition probes; Read-only Mac probes for app state/files/reminders that expose trustworthy provenance and permission health; Browser extension reconnect/queue reconciliation with idempotency keys and postcondition extraction; Pendant/relay status vocabulary for verified, reported-only, contradicted, stale, and unverifiable results; Dashboard view that shows the evidence chain without exposing raw private content

### "“Only interrupt me when I’m actually available.”"
- **useful because:** A scheduled brief or urgent alert should not speak over a meeting, music, navigation, or a noisy environment. The wearable can sense whether speech is audible while the Mac can reveal active calls, presentations, focus state, and foreground work; the relay can defer and then deliver when availability returns.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** Deterministic event classifier for audio level/playback and Mac app/call state; a cheap background model may label ambiguous foreground-app situations. Realtime is used only for the eventual spoken alert.
- **latency:** Under 1 second to classify current interruptibility; defer checks every 15–60 seconds while an alert is pending. No perceptible work during normal conversation.
- **cost:** Near-zero model cost for local typed signals; occasional cheap classification under $0.001 per deferred alert. Main cost is relay event storage and a small always-on audio feature extractor.
- **security:** Keep raw microphone audio on the pendant and never upload it for availability detection; export only coarse features (speech/noise/quiet) and confidence. Mac app names and meeting state are private. Provide a physical override button and a dashboard audit trail; emergency alerts must have an explicit bypass policy.
- **missing:** Pendant-local coarse audio availability events (no raw audio) with confidence and drop-link buffering; Mac read-only focus/call/presentation and playback-state probe with freshness timestamps; Relay policy engine for defer, coalesce, expire, and wake-on-availability events; Owner-configurable quiet hours, emergency categories, and maximum deferral duration

### "“What changed while I was away, and what did we miss?”"
- **useful because:** Today the owner can receive separate job receipts and scheduled briefs, but cannot get a trustworthy reconstruction of the interval when the pendant, relay, Mac, or browser was disconnected. This would distinguish confirmed changes from unobserved time, reconcile late-arriving device events, and surface only decisions that need the owner.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use deterministic event-log reconciliation, timestamps, hashes, and connectivity intervals first; use a cheap background model only to compress the reconciled delta into a short spoken summary. Realtime is needed only when the owner asks follow-up questions.
- **latency:** Generate a compact delta within 5 seconds when connectivity returns; permit up to 60 seconds for browser/Mac reconciliation. The pendant should announce a one-line availability result immediately and let the owner ask for detail.
- **cost:** Near-zero model cost for event reconciliation; about $0.001–$0.01 for optional summarization. Storage and periodic connectivity probes dominate rather than inference.
- **security:** Keep raw private page text, audio, and file contents on their originating device; relay receives event IDs, timestamps, provenance, sensitivity labels, and redacted summaries. Explicitly mark gaps instead of inferring them. Retain a user-visible deletion and retention policy, and require confirmation before any proposed catch-up action.
- **missing:** A shared append-only event envelope with monotonic device sequence, wall-clock estimate, source, sensitivity, and connectivity interval; Pendant-local durable event markers for button, audio-session, playback, and link transitions that survive outages; Mac and browser change snapshots with before/after hashes and freshness, not merely action receipts; Relay reconciliation that handles late, duplicated, and conflicting events without silently rewriting history; A dashboard and pendant vocabulary for confirmed change, late evidence, contradiction, and unknown interval

### "“What did you share about me, with which device or service, and why?”"
- **useful because:** The owner cannot currently inspect a single, trustworthy privacy ledger across pendant audio, relay transcription, Mac files, and authenticated browser pages. A plain-language, per-request disclosure receipt would make the hive understandable: what stayed local, what crossed the relay, which model saw it, retention, and whether a secret or private page was included.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Generate the ledger deterministically from typed data-flow events and redaction decisions; use a cheap background model only to translate the receipt into one short spoken explanation. Realtime is unnecessary except for an immediate owner query.
- **latency:** Attach a receipt synchronously to every request and expose a spoken summary in under 1 second; detailed export can be produced in the background.
- **cost:** Negligible model cost; dominated by small encrypted event storage and occasional dashboard export. No screenshot or page-content upload is needed to explain most flows.
- **security:** The ledger itself is sensitive and must be encrypted locally with relay metadata minimized. Never store raw secrets or raw audio merely to prove handling; use keyed hashes, field-level sensitivity labels, destination, purpose, retention, and deletion status. The owner must be able to erase ledger entries without erasing unrelated task records.
- **missing:** A typed end-to-end data-flow event emitted by every surface and tool, including fields selected, redactions, destination, model, purpose, and retention; Field-level sensitivity classification shared by pendant, relay, Mac, and browser instead of prompt-level secrecy only; A cryptographically tamper-evident but content-minimized local ledger with relay acknowledgment and deletion semantics; Dashboard and pendant commands for 'show me this request' and 'forget this disclosure'; Automated tests proving that secrets and raw audio never enter the ledger payload


## Changes it proposed to its own stack

### `hardware` — Replace the prototype’s single raw I2S microphone path with a production audio front end that includes a low-power always-on voice/activity detector (or a tiny companion DSP) and exposes coarse speech/noise/quiet interrupts to the nRF9160; retain the full-band mic path for conversations. Keep the existing full-duplex I2S for Opus, but do not run a second software VAD on the already ~87%-busy audio core.
- **owner gets:** The pendant could know locally whether the owner is speaking, in a noisy street, or in a quiet place and defer alerts without uploading raw sound or draining the battery. Availability sensing would continue through a dropped Mac/relay link.
- effort: Medium-high: select a low-power audio/VAD IC, revise the microphone/ESP32 bridge board and firmware drivers, define privacy-preserving feature events, and validate coexistence with the 24 kHz playback path.  ·  risk: False quiet/noisy classifications could delay an important alert; retain a physical override and configurable emergency bypass. Hardware respin risk is recovered by keeping the current I2S mic as a fallback and feature-gating the detector.
- cost: Roughly $2–$8 BOM increase plus PCB respin; detector power target under 5 mW in always-on mode, versus materially higher CPU/battery cost for software analysis while encode/decode already consume ~87% of one core.  ·  latency: Activity interrupt target 10–100 ms; no added latency to 24 kHz playback or Opus conversation path.
- security: Raw audio remains on-device; only coarse classifications and confidence leave the pendant. Detector firmware and event transport need signed/update-safe handling to prevent covert audio-state leakage.
- depends on: Define the interruptibility event schema and relay defer policy; Confirm production microphone, codec, and enclosure requirements beyond the nRF9160 DK prototype; Add pendant-local buffering and privacy controls for coarse audio events


## What it asked for

_Nothing._
## Its own summary

Round 47 established that the requested Mac grants have not taken effect: at 11:32Z the exact running AI Pendant Agent remains Accessibility-untrusted, Screen Recording is absent, input reachability failed, and UI receipts cannot be trusted. The browser extension is offline with four pending commands, while relay and Mac bridge are reachable. I recorded this finding, informed mac-vision, faculty-judgement, and unified, and proposed (1) evidence-backed postcondition verification instead of trusting action success, (2) interruptibility-aware alert delivery across pendant/Mac/relay, and (3) a low-power local audio-activity detector so the pendant can sense availability privately despite link loss.

**Biggest unknown:** Whether macOS permissions can be granted to the exact running binary and re-probed successfully; pendant-side diagnostics and the real 24 kHz end-to-end implementation state also remain unavailable, so I cannot yet establish device-local audio or continuity truth.

