# Harness derivation — mac-terminal — round 233

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live USB bench access** — The newly granted mac_usb_serial_diagnostics call still does not resolve against the live inventory, even with exact enumerated device paths; no serial capability is currently callable. The physical devices remain listed only as Mac-attached hardware, so bench reads still require an implementation on top of run_shell or a new host capability.
  - evidence: Called mac_usb_serial_diagnostics for /dev/cu.usbmodem00096003658, A, B and /dev/cu.usbserial-0287A9CA with 1s/8192-byte bounds; resolver returned unresolved, best match action:get_mac_status score 0.226.

## Capabilities it proposed

### "“Is the pendant actually ready right now?” Run a 30-second bench smoke test: verify both USB chips, capture bounded UART health from nRF9160 and ESP32, exercise one audio round-trip, and tell me exactly which link or counter failed — with the result spoken back through the pendant."
- **useful because:** This is the first honest readiness answer available today: the hardware is physically present but LTE is unregistered, and generic Mac health cannot distinguish a dead audio bridge from a healthy one. It combines the worn device's real button/audio path, the Mac's USB reach, and the relay's conversational report instead of claiming wearable continuity from /health.
- **path:** pendant → mac-planner → relay-realtime → unified
- **model tier:** Cheap deterministic shell/parser and counter comparison first; use realtime only to turn the structured result into a concise spoken explanation.
- **latency:** 30–45 seconds for capture and one bounded audio probe; under 2 seconds to speak the result after the test.
- **cost:** Near-zero model cost on pass/fail; roughly $0.01–$0.05 only when a realtime explanation is needed. Dominant cost is the 30-second USB capture, not inference.
- **security:** UART output can contain firmware diagnostics and identifiers; keep raw logs on the Mac, send only counters/failure classes to relay, and require no network or LTE assumption. The test must never flash firmware or transmit arbitrary captured audio.
- **missing:** A real host serial reader/parser (the granted mac_usb_serial_diagnostics schema still has no implementation); A bounded, read-only audio loopback test with explicit frame/counter assertions; A relay-to-pendant result event that distinguishes USB bench success from LTE wearable success

### "“What was interrupted while my Mac agent was down?” On reconnect, reconcile every in-flight Mac action, identify the last completed step, and offer to resume only the unfinished work; if it cannot be safely resumed, say exactly why through the pendant."
- **useful because:** Today a crash leaves jobs marked processing forever, cancellation cannot stop a running shell, and the ledger is never closed or joined to the job ID. The owner can otherwise believe an email was sent, a file was moved, or a browser task finished when it did not. This turns a silent crash into a truthful, actionable handoff across the always-awake relay, the Mac ledger, and the wearable.
- **path:** relay-realtime → mac-planner → browser-extension → pendant → unified
- **model tier:** Deterministic boot reconciliation and step-state matching first; a cheap background model summarizes ambiguous receipts. Realtime is used only if the owner asks by voice or needs an immediate spoken status.
- **latency:** Reconcile within 5 seconds of Mac-agent startup/reconnect; spoken summary within 2 seconds of a pendant request. Resume work asynchronously rather than blocking the conversation.
- **cost:** Usually no model call; under $0.01 for an ambiguous summary, with realtime cost only for live speech. Disk I/O and ledger scan dominate.
- **security:** Never replay a side effect solely because a step was interrupted. Require per-action replaySafety/idempotency evidence, preserve the existing owner maximum-access policy, and report sensitive command/file names locally rather than uploading raw params to relay.
- **missing:** Call closeLedger for every orchestrator execution and persist the real jobId in planMeta; Boot-time reconciliation that marks processing jobs interrupted instead of leaving them forever; A resume planner that uses the existing ledger resume payload and executionContext idempotency state, with explicit non-replayable actions; A relay event carrying the reconciliation summary to the pendant

### "“Give me a private, evidence-backed replay of the last five minutes.” The pendant should retain a rolling, encrypted local audio/event buffer; the Mac should contribute foreground-window and browser-session transitions; the relay should assemble a short chronological explanation with links to the exact local action receipts, then erase the raw buffer unless I explicitly save it."
- **useful because:** When an interruption, accidental action, or missed spoken instruction happens, the owner can ask what actually occurred instead of relying on memory or an unjoined job log. This is not a generic activity feed: it is an on-demand reconstruction that combines the device's physical timeline, the Mac's actions, and authenticated browser provenance while keeping raw material local by default.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → unified
- **model tier:** Local deterministic event indexing and redaction first; use a background model to draft the chronology, with realtime only to answer the live spoken request. Never send the raw rolling audio or full screen contents to the model unless explicitly saved.
- **latency:** A 30-second replay summary in under 5 seconds; a five-minute reconstruction in under 15 seconds. Buffering and indexing are continuous but must not affect the active audio path.
- **cost:** Typically $0.01–$0.05 for a generated summary; storage and local indexing dominate. Raw audio retention should be bounded to 5–10 minutes and automatically discarded after a successful summary.
- **security:** This buffer could contain highly sensitive speech and screens. Encrypt locally, keep raw audio/screens on the Mac or pendant, redact tokens and secrets before relay transfer, require an explicit save command for retention, and expose a visible recording state. Browser provenance must remain origin-scoped and never become a general page archive.
- **missing:** A synchronized monotonic clock and signed event envelope shared by pendant, Mac, browser extension, and relay; A bounded encrypted ring buffer on the pendant/Mac for audio and UI metadata, with deletion proofs or at least durable expiry; A cross-surface event-join service that links button edges, turn IDs, Mac job IDs, browser command IDs, and action receipts; A local redaction/summarization worker that can produce a useful chronology without exporting raw content; A spoken replay control and unmistakable privacy indicator on the pendant

### "“Privacy now.” A dedicated pendant button press should immediately stop microphone capture, prevent any queued audio or screen context from leaving, tell the Mac to pause browser/UI observation, and confirm locally even if the relay is offline; when I release privacy mode, the system should report what was suppressed rather than silently resuming."
- **useful because:** The owner needs a physical, reliable privacy boundary that does not depend on a voice command, an active LTE session, or a functioning Mac. It spans the only hardware that knows the owner's immediate intent, the Mac that can see browser/screens, and the relay that must stop forwarding queued context. Offline confirmation matters because privacy is most urgent exactly when connectivity is uncertain.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → unified
- **model tier:** Firmware state machine and deterministic local-agent controls; no model call for entering or leaving privacy mode. A cheap background model may summarize suppressed events only if the owner asks.
- **latency:** Local microphone shutdown and LED confirmation under 100 ms; Mac/browser pause within 1 second when connected; queued outbound items marked suppressed immediately.
- **cost:** Negligible API cost. Small local state and one durable event per transition.
- **security:** Privacy mode must be fail-closed on transport loss: do not claim remote pause was acknowledged unless it was. Existing queued audio/context needs a suppression tombstone so it cannot replay after reconnect. The indicator must be unambiguous with one LED and survive reboot.
- **missing:** A dedicated privacy button/action in pendant firmware using the existing second physical switch, not a gesture on the recording button; A transport-level privacy epoch checked by relay, Mac agent, and browser extension before sending or resuming queued data; Mac/browser pause and resume endpoints for screen observation, browser polling, and context capture; A durable suppression manifest and owner-visible report of what was discarded


## Changes it proposed to its own stack

### `mac-harness` — Add a first-class bench-session recorder around the existing dual-chip capture scripts: allocate a session UUID, record exact device-path/baud/read windows, stream each line with monotonic timestamps, parse framed health counters when recognizable, and persist a compact manifest plus raw-log paths. Do not pretend this is a product transport; make it an explicitly bench-only artifact that can be handed to the relay.
- **owner gets:** When the pendant misbehaves, the owner gets an answer tied to the actual cable session — which board disappeared, when counters stopped, and the raw evidence to send to a developer — instead of a vague failed shell job or a claim based on LTE status.
- effort: 2–4 engineering days: a small native serial reader or bounded helper, framing parsers for both firmware logs, and a manifest reader. Existing scripts can remain the fallback.  ·  risk: A parser could mislabel free-form logs. Preserve raw bytes, mark unknown frames as unknown, and never turn an absent parser match into a pass. USB unplug must close descriptors and finalize the manifest.
- cost: No API spend; a few MB per captured session, with retention/cleanup after upload or 7 days.  ·  latency: No impact on normal Mac actions; session startup under 500 ms and line parsing streaming.
- security: Raw UART logs remain local by default. Any relay handoff sends a redacted summary and explicit session ID, not arbitrary logs or environment variables.
- depends on: A real serial implementation (the currently granted mac_usb_serial_diagnostics schema is unresolved); Stable health-counter/frame formats in both firmware logs; A documented bench-only invocation path separate from wearable LTE routing

### `hardware` — Add a hardware-enforced microphone privacy cutoff to the next pendant revision: a normally-open analog switch or load switch controlled by the dedicated privacy input, with a local latch that removes microphone power before firmware or LTE code runs. Feed the latch state back to the nRF9160 so the LED and event envelope can distinguish 'mic physically disconnected' from 'software muted.'
- **owner gets:** The owner gets a privacy guarantee that survives a wedged firmware task, a dropped relay link, or a compromised/buggy Mac agent. Pressing privacy would physically prevent new audio from being captured rather than merely asking every software layer to remember to mute.
- effort: Moderate hardware respin: schematic/layout change, switch-pop and codec validation, firmware state reporting, and a small enclosure/button-label revision.  ·  risk: Power transients or switch leakage could create audio pops, and a latched cutoff could make recovery confusing. Use a normally-off default at boot, debounce in hardware, test brownout recovery, and require an explicit physical re-enable. Existing recording and staged-reply LED states must yield to the privacy indication.
- cost: Roughly $0.10–$0.60 in components and PCB changes per unit; negligible steady-state power, with a few microamps for the latch if implemented discretely.  ·  latency: Hardware mute under a few milliseconds, faster than a radio or firmware round trip; no impact on normal conversations when privacy is inactive.
- security: Strongly improves confidentiality by making the microphone cutoff independent of the cloud, Mac, and application token. It does not protect already-buffered audio, so software must still purge or tombstone queued frames on entry.
- depends on: A dedicated privacy control that does not steal the active-edge recording button; Firmware and relay privacy-epoch propagation; A visible single-LED privacy state and explicit recovery behavior


## What it asked for

_Nothing._
