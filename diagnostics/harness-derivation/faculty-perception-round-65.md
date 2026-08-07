# Harness derivation — faculty-perception — round 65

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac accessibility and screen capture state** — As of 2026-08-07T12:27Z, AI Pendant Agent is running with Accessibility trusted=false, Screen Recording granted=false, inputReachability.status=failed, and uiActionsWillReachTheScreen=false. AppleScript automation grants are present and permissions.requiredMissing/optionalMissing are both empty, but overall ready=false.
  - evidence: GET /ops/status and GET /observe live responses
- **browser and authenticated-session observability** — Home Chrome extension is online but has no active tab (tabId null, tabCount null, blank URL/title) and 5 pending browser commands. The Mac agent reports 3 durable browser sessions, including a default session on https://time.is/UTC and two Selenium/httpbin probe tabs; no owner-authenticated page is currently observable.
  - evidence: GET /ops/status and GET /observe live responses; devices discovery
- **audio response path** — The live pipeline has produced a completed 24,000 Hz mono s16le TTS response (74.0 KiB, 1,578 ms audio, 0 clipped samples) and uploaded it to the relay for pendant playback. This establishes render/upload success, not end-to-end speaker audibility or packet-loss-free playback.
  - evidence: GET /pipeline live response, run job_309f5663-e01a-4f8a-b798-319c7c18313f events
- **current browser bridge reachability** — At probe time 2026-08-07T12:27Z, GET /browser/status reports online=false for home-chrome, blank tab identity, and 5 pending commands. GET /browser/sessions contains only the default time.is/UTC tab and two test forms; there is no evidence of an owner-authenticated tab.
  - evidence: GET /browser/status and GET /browser/sessions live responses

## Capabilities it proposed

### "When my pendant reconnects after being offline, tell me only what is still actionable, using my Mac and logged-in browser, and keep a cited catch-up brief I can review later."
- **useful because:** The current system can surface held alerts, but it cannot yet reconcile them against what changed while offline. This would prevent stale reminders and duplicate spoken alerts while preserving an auditable explanation of what was held, what was checked, and what remains.
- **path:** pendant → relay-realtime → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use the relay/background model for reconciliation and cited brief generation; use realtime only for the short spoken delta when the pendant reconnects. Use the Mac planner/browser bridge only for authenticated reads, not GUI vision.
- **latency:** On reconnect, speak a 1–2 sentence delta within 3 seconds; finish deeper Mac/browser reconciliation in the background within 60 seconds and update the dashboard.
- **cost:** Roughly $0.01–$0.05 per reconnect depending on authenticated-page extraction and brief length; realtime audio is the dominant latency/cost only for the spoken delta.
- **security:** Authenticated page contents leave the Mac only as extracted, cited fields; do not transmit secrets or full page HTML. Never send mail, submit forms, or mutate accounts. Require confirmation for any proposed action. Retain alert IDs, timestamps, source URLs, and hashes rather than raw pages, with short TTL.
- **missing:** A durable reconnect event contract joining pendant offline alert IDs to relay jobs and Mac/browser observations; A deduplication/reconciliation worker that can compare held alerts with current Calendar/Mail/browser facts; A cited catch-up brief and acknowledgement state exposed to pendant and dashboard; A reliable browser command queue drain/expiry policy; currently 5 commands are pending while no active Chrome tab is observable

### "After every pendant conversation, tell me whether you heard all of my request, which words or time ranges were missing, and let me repair only the missing part instead of repeating everything."
- **useful because:** Today a dropped LTE uplink can silently turn a long spoken request into a partial request while the system still produces a confident answer. The owner needs an honest, repairable conversation record rather than discovering later that the agent acted on an incomplete sentence.
- **path:** pendant → relay-realtime → relay → mac-planner → dashboard
- **model tier:** Use a cheap background model to align packet-loss intervals with the realtime transcript and classify confidence; use realtime only to ask the owner for a short repair when a gap affects intent. Do not spend the expensive model on intact turns.
- **latency:** Show a provisional integrity result within 2 seconds after the turn; if repair is needed, ask one concise question immediately, then complete the durable alignment within 30 seconds.
- **cost:** About $0.002–$0.01 per turn for alignment and compact repair text; storage and telemetry dominate, not inference.
- **security:** Keep raw audio on the pendant or short-lived relay storage; expose only transcript spans, sequence ranges, loss metrics, and confidence by default. Never infer or persist sensitive missing speech. Require confirmation before retrying an action whose intent was reconstructed.
- **missing:** Per-audio-frame sequence numbers and monotonic capture timestamps from the pendant; Relay-side loss and retransmission accounting that survives WebSocket reconnects and half-duplex contention; Transcript span alignment to packet ranges, with an explicit 'unknown' state instead of guessed words; A repair protocol that requests only a numbered missing span and prevents the original action from executing until intent is complete; Dashboard and spoken receipt surfaces for integrity status


## Changes it proposed to its own stack

### `integration` — Make every GUI-oriented action receipt carry a machine-observed reachability envelope from /observe: accessibilityTrusted, screenRecording, inputReachability, foreground app, and probe timestamp. If inputReachability is failed, classify ui_click/type_text/press_keys/ui_menu as 'not-established' rather than success, while leaving AppleScript and browser-bridge receipts independently typed. Add a reconciliation job that rechecks reachability before claiming completion.
- **owner gets:** The owner will stop hearing that a click or keystroke succeeded when it actually did nothing. They get an honest explanation and can still use the reliable AppleScript/browser paths instead of debugging invisible failures.
- effort: Moderate: typed receipt schema, pre/post observation calls, dashboard wording, and regression tests for permission failure and recovery.  ·  risk: Extra observation latency; a transient probe failure could downgrade a real action. Recover by retaining raw action result plus probe evidence and allowing a later recheck to upgrade only with positive evidence.
- cost: Negligible API cost; one local observation per GUI action batch and a small receipt payload.  ·  latency: Approximately 50–200 ms per GUI batch for local observation; no impact on AppleScript-only actions.
- security: Improves safety by preventing fabricated success claims; observation metadata is local and should omit page contents.
- depends on: GET /observe is live and read-only; GET /ops/status is live; Action receipt schema from chg-5fc73ce3 exists but currently lacks permission/reachability gates

### `hardware` — Replace the prototype's single shared I2S path plus opaque ESP32 bridge buffering with a production audio front end containing timestamped DMA on both directions, a small nonvolatile event buffer (FRAM or equivalent), and a fuel-gauge/RTC companion. Expose capture sequence, playback sequence, underrun/overrun counters, reconnect timestamps, and battery state to the nRF9160 over the currently free I2C bus; keep the SD card reserved for large failure audio.
- **owner gets:** The owner gets a pendant that can prove whether it heard and played a sentence, preserve a tiny diagnostic trail through a power or LTE failure, and report battery/time truthfully—rather than receiving an answer with no way to know whether the wearable actually delivered it.
- effort: High hardware and firmware revision: select an audio codec/bridge with hardware timestamps and DMA, add FRAM, fuel gauge, and RTC, define a compact diagnostic record, then validate coexistence with LTE-M and Bluetooth SBC.  ·  risk: Board redesign, new power budget, codec-driver defects, and possible Bluetooth latency changes. Recover with a compatibility mode using the existing I2S path and bounded diagnostics; never make the new counters a prerequisite for ordinary calls.
- cost: Rough prototype delta roughly $8–$20 in components and PCB area, plus tens of milliwatts for codec/gauge/RTC; negligible per-call API cost.  ·  latency: Hardware buffering can reduce jitter and packet starvation, but adds a bounded 10–30 ms buffering floor; diagnostic records are asynchronous.
- security: FRAM must contain only sequence/timing/error metadata by default, with encrypted audio excluded. Battery and clock data are low sensitivity; protect diagnostic export with the existing pairing/authentication.
- depends on: A new pendant/bridge board revision (the current Nordic DK and HUZZAH32 are prototypes); Firmware protocol for timestamped audio and diagnostic records; Relay schema that can consume and display device evidence without treating missing telemetry as success


## What it asked for

_Nothing._
## Its own summary

Established fresh truth: the Mac agent is online and AppleScript-capable but GUI input is not trustworthy—Accessibility and Screen Recording are false, inputReachability failed, and UI receipts can claim success while doing nothing. The browser bridge is currently offline with no active Chrome tab and 5 pending commands; its durable sessions are only time.is and test forms. The 24 kHz mono TTS path rendered and uploaded successfully (74 KiB, 1.578 s, zero clipping), but this does not establish speaker audibility or loss-free pendant playback. I recorded these facts, informed judgement, and proposed a reconnect reconciliation capability plus reachability-aware action receipts.

**Biggest unknown:** Actual pendant-side playback and reconnect state remain unobservable from this node: we still need a trustworthy end-to-end pendant diagnostic/ack signal (received, decoded, played, packet loss) and a durable browser-command acknowledgement/expiry signal. The owner still needs to grant Accessibility and Screen Recording manually to the exact AI Pendant Agent binary before GUI perception can become true.

