# Harness derivation — relay-realtime — round 192

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Read what’s on my screen and act on it, but only if it’s safe and I asked for it."
- **useful because:** It turns the pendant into a hands-free assistant for real workflows: summarize what’s visible, extract key info, then take a requested action, with strong privacy boundaries.
- **path:** browser → mac-bridge → relay
- **model tier:** Mac planner and browser computer-use loop do the heavy lifting; relay stays conversational and low-latency.
- **latency:** One quick spoken acknowledgement; then a few seconds to read/extract; longer if login or multi-step navigation is needed.
- **cost:** Moderate and dominated by browser extraction and follow-on actions. Results should be cached/normalized to avoid re-reading unchanged pages.
- **security:** Never exfiltrate hidden fields, credentials, or private messages by default. Use typed extraction and redaction; require confirmation for destructive actions like sending mail or purchases.
- **missing:** Typed browser evidence capsules and a privacy boundary in the extension before data leaves Safari.; A durable browser command ledger with idempotency and session affinity.; A lease/heartbeat-based health gate to avoid acting on stale sessions.

### "If the pendant is misbehaving, file a bug report for me with logs and a short repro."
- **useful because:** When something is broken, the fastest path to a fix is a crisp report. The owner shouldn’t have to copy logs or remember steps while the device is glitching.
- **path:** pendant → relay → mac-bridge
- **model tier:** Relay compiles the report; Mac can attach simulator artifacts; cheaper backend handles storage and dedup.
- **latency:** Under a few seconds to confirm it’s captured; attachments upload in the background.
- **cost:** Low to moderate. Mostly storage and occasional log retrieval; dedup reduces repeated noise.
- **security:** Logs may contain sensitive info. Strip secrets and tokens; never include audio unless the owner explicitly asks. Keep reports scoped to this device and session.
- **missing:** A stable log retrieval path from pendant/bridge over USB and from the relay’s own logs.; A report store with deduplication and threading (link to existing jobs/incidents).; A redaction pass before upload.

### "“Research this question using my open browser sessions, my Mac files, and the public web; tell me the answer aloud, distinguish facts from guesses, and cite where each important claim came from.”"
- **useful because:** This would turn the pendant into a trustworthy personal research front door rather than three disconnected search tools. The relay could reconcile public facts with the owner's private, authenticated context and expose contradictions instead of silently choosing one source.
- **path:** pendant → relay → mac-planner → browser-extension → mac-vision
- **model tier:** Realtime relay for clarification and a short spoken synthesis; background gpt-5.6-luna planner for parallel retrieval and evidence reconciliation; no realtime model spent on long documents.
- **latency:** Acknowledge in under 500 ms, first useful spoken result in 5–8 s, then optionally continue collecting evidence asynchronously.
- **cost:** Roughly $0.03–$0.15 per request depending on document length; latency and tokens are dominated by private-file/browser extraction and synthesis, not the initial voice turn.
- **security:** Private files and authenticated browser contents leave the Mac only to the relay/model path and must be explicitly labelled in the spoken answer. Never quote secrets or upload an entire file when a local extractor can return a bounded excerpt. Claims need source IDs and timestamps so stale browser data is not presented as current.
- **missing:** A cross-surface retrieval/merge planner that can call Mac files, browser sessions, and web search in one job; A provenance object carried from each extractor into the final spoken response; A bounded local extraction route for private files and browser DOM/screenshot evidence

### "“Take this coding problem from my voice: inspect the project, reproduce the failure, read the relevant documentation in my browser, make the smallest fix, run the tests, and tell me exactly what changed.”"
- **useful because:** A worn button and voice should be enough to start a complete engineering loop while the owner is away from the keyboard. The value is not merely running a shell command: the Mac planner, terminal, browser session, and relay would iteratively gather evidence, fix, verify, and explain rather than stopping after the first failed command.
- **path:** pendant → relay → mac-planner → mac-terminal → browser-extension
- **model tier:** Use realtime only to capture constraints and provide concise checkpoints; use gpt-5.6-luna for the multi-step plan and a cheaper execution/diagnostic loop for shell and browser observations.
- **latency:** Confirm scope within 1 s; reproduce within 15 s; provide a first diagnosis within 30 s; long test/fix loops may continue after the voice session, with a durable result notification.
- **cost:** About $0.10–$0.60 per incident, dominated by planner turns and test-output context; local shell execution itself has no model cost.
- **security:** The owner has requested maximum access, but destructive operations still need an explicit dry-run/rollback record. Send command output and only necessary source excerpts to the model; redact environment secrets. Preserve a patch, test receipt, and base revision so an incorrect fix can be reverted.
- **missing:** A Mac-terminal execution loop that feeds structured test failures back into the planner; A browser-context adapter that can search/read the owner's existing authenticated documentation sessions; A durable patch/test artifact and completion delivery path to the pendant

### "“What am I looking at on my Mac right now? Explain the important controls or errors aloud, and if I say ‘do that’, carry out the exact highlighted action.”"
- **useful because:** This gives the owner a genuine remote pair of eyes while wearing the pendant: the vision tier grounds the answer in the current screen, the browser tier can use DOM semantics when available, and the relay turns it into a short spoken interaction. The explicit referent and second utterance prevent a vague screen description from becoming an unintended action.
- **path:** pendant → relay → mac-vision → mac-planner → browser-extension
- **model tier:** gpt-4.1-mini computer vision for screenshot/DOM grounding, gpt-5.6-luna only for ambiguous referents and action planning, realtime relay for the low-latency spoken exchange.
- **latency:** Screen description in 2–4 s; resolve ‘that’ and return an action preview in under 2 s after the follow-up; execute only after the owner’s follow-up utterance.
- **cost:** Approximately $0.01–$0.08 per inspection/action, dominated by screenshot tokens; DOM extraction should be preferred over pixels to reduce cost.
- **security:** Screens may contain passwords, private messages, or financial data. Redact known sensitive regions before model transmission, retain no screenshots by default, and state which app/window was inspected. The second utterance must bind to an identified control, not an inferred broad goal.
- **missing:** A live Mac-vision inspection route exposed to the relay; A shared screen-grounding reference that survives from description turn to action turn; A reliable browser DOM fallback and sensitive-region redaction


## Changes it proposed to its own stack

### `browser-harness` — Introduce a privacy-bounded evidence capsule protocol in the Safari extension: typed extracted fields, explicit allowed regions, redaction of sensitive inputs, and provenance metadata. Treat extracted content as untrusted data and never executable instructions.
- **owner gets:** Lets the assistant help on real pages while protecting private information and reducing accidental exfiltration.
- effort: High: extension work, schema definitions, normalization, and tests; relay and Mac must accept and verify capsules.  ·  risk: Over-redaction can make the assistant useless; under-redaction leaks secrets. Start strict, add allowlists, and require explicit user selection for sensitive contexts.
- cost: Moderate development cost; runtime cost mainly serialization and verification.  ·  latency: Small overhead for capsule creation and verification.
- security: Strongly positive: reduces privacy risk and injection risk.
- depends on: Extension update mechanism; Schema validation in Mac agent and relay; UI/voice affordance for user-selected capture

### `mac-harness` — Add a durable browser command ledger with idempotency keys, session/tab affinity, retries, and expiry. Include a lease/heartbeat health gate so the relay can safely queue work and avoid acting on stale sessions.
- **owner gets:** Browser actions become reliable: fewer hangs, fewer duplicated clicks, and better recovery when Safari or the extension drops.
- effort: High: persistent store, reconciliation logic, and integration with /browser/heartbeat and /browser/poll.  ·  risk: Ledger bugs could block actions or replay them. Mitigate with clear state machine, expiries, and manual cancel/undo paths.
- cost: Moderate development; small ongoing storage and CPU.  ·  latency: Slight overhead per command; large reduction in failure recovery time.
- security: Positive: auditable actions and safer retries.
- depends on: Persistent storage for the ledger; Extension heartbeat fidelity; Command schema versioning

### `hardware` — Add a matched two-microphone array to the ESP32 audio bridge, with a local beamforming/noise-suppression stage that preserves the existing press-to-talk boundary and 24 kHz Opus path. The bridge should emit a confidence/noise estimate alongside each uplink block so the relay can ask for a repeat instead of pretending it heard correctly.
- **owner gets:** The owner could use the pendant in a street, kitchen, or busy office without shouting or repeating themselves. It improves recognition at the moment of capture, before private speech is sent anywhere, while keeping the current physical consent gesture unchanged.
- effort: Moderate hardware revision and firmware work: matched digital/analog mic placement, acoustic calibration, beamformer/AEC implementation, enclosure retuning, and measured tests across wind, speech direction, and bridge playback. This is a new capability, not a resampling change.  ·  risk: Poor calibration can amplify noise or create speech coloration; AEC can accidentally suppress the owner's voice. Provide a firmware flag to disable processing, retain raw-path fallback, and compare word-error rate plus mic-drop rate against today's single-mic baseline before rollout.
- cost: Roughly $8–$25 for two microphones, PCB/layout and acoustic parts in a prototype; likely under 100 mW incremental bridge power depending on DSP implementation. No recurring API cost.  ·  latency: About 2–10 ms local processing, with no additional relay round trip.
- security: Better local rejection means less unintended ambient speech reaches the relay. Raw audio remains press-to-talk only; do not add always-on buffering.
- depends on: A bridge firmware audio-processing stage with the existing 24 kHz framing; A hardware enclosure/PCB revision; A repeatable noisy-environment speech-quality benchmark


## What it asked for

_Nothing._
