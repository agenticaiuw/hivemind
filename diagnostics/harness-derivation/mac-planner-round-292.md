# Harness derivation — mac-planner — round 292

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “do this” through the pendant, use the current Mac/browser context to carry it out, but if the Mac is locked or the browser session is unavailable, queue it safely and resume automatically after the machine becomes usable; tell me exactly what happened."
- **useful because:** This is the central hive behavior: the pendant captures intent anywhere, the relay preserves it, perception establishes whether the Mac is actionable, and the Mac/browser executes only when its real session is available. Today a request can silently fail or be attempted against loginwindow. A durable, state-aware handoff turns that into a trustworthy assistant instead of a remote-control demo.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime for the short spoken acknowledgement; a cheaper background planner for queueing, context matching, retry, and receipt summarization.
- **latency:** Acknowledge in under 500 ms. Context check in 2 s. Execute immediately when unlocked/online; otherwise retry on state change and expire after an owner-configured TTL.
- **cost:** About $0.01–$0.05 per queued request depending on whether vision/browser context is needed; most retries should be zero-model-cost state polling.
- **security:** Current foreground state is demonstrably loginwindow, while Accessibility and Screen Recording are now granted and synthesized input is verified. Do not execute against a locked session. Persist only a redacted intent, target app/domain, and receipt; never store page passwords or raw screenshots by default. The owner still needs to define unattended URL/app classes because FULL_CONTROL_MODE currently has no effective approval gate.
- **missing:** A lock/loginwindow-aware queue state in the relay job model; A Mac state-change trigger or bounded retry worker that wakes queued jobs after unlock/browser reconnect; Owner-configurable unattended action policy, read at runtime rather than assumed; A compact cross-surface receipt linking /plan, /execute, and browser command results

### "When the pendant is plugged into my Mac, run a one-command audio health check, prove the uplink and 24 kHz downlink meet their measured limits, save a human-readable report, and tell me whether the hardware is safe to use before I leave."
- **useful because:** The pendant is physically present over USB today but LTE is unregistered. This makes the accepted diagnostic fixture useful now: the Mac can arm it, collect bounded serial output, evaluate alias rejection/CPU/mic-drop/tx-starved thresholds, and give the owner a go/no-go result without pretending the radio is online. It catches exactly the class of audio regressions that previously shipped.
- **path:** pendant → mac-planner → relay → dashboard
- **model tier:** No realtime model for the test itself; use deterministic scripts and a cheap background summarizer only for the final plain-language report.
- **latency:** Start within 2 s of the spoken request; complete in under 60 s. Return raw measurements immediately and a concise verdict within 2 s of completion.
- **cost:** Under $0.01 per run; dominated by local serial/test runtime, not model tokens.
- **security:** The fixture must use synthetic audio only and never open or persist the microphone stream. USB output should be bounded, scrubbed of secrets, and stored locally with a hash. Do not claim LTE readiness from a USB-only test; label radio registration as unknown/offline.
- **missing:** A bounded, read-only Mac serial diagnostic action that can arm the existing fixture and collect logs (not a persistent serial session); A deterministic threshold evaluator for scripts/audio-quality-probe.mjs output; A receipt schema that records firmware/build identity, fixture vector hash, measurements, and pass/fail reasons; An explicit dashboard/pendant indication for ‘USB audio verified, radio not verified’

### "If I engage the pendant’s privacy latch, immediately stop any queued or running Mac/browser work that could expose data, show me that the stop propagated, and never resume those actions automatically when privacy is released."
- **useful because:** A local privacy latch is only half a privacy guarantee if a previously issued browser or Mac job keeps running. This makes the wearable’s physical state authoritative across the hive: pendant stops capture/playback locally, relay broadcasts a revocation, Mac cancels or checkpoints jobs, and the owner gets a durable receipt. Releasing privacy remains local and safe; it must not silently restart automation.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic event handling and job cancellation; use the realtime model only to phrase the brief spoken status if the owner asks.
- **latency:** Pendant-local mute is immediate. Relay fanout under 250 ms when connected; Mac/browser cancellation under 2 s. If disconnected, the pendant retains the latch and the relay marks revocation pending until reconnect.
- **cost:** Negligible model cost; roughly $0.001 or less per state event, dominated by durable event/receipt writes.
- **security:** Revocation events must be authenticated, monotonic, replay-resistant, and fail closed. Cancellation should not delete evidence of what ran; store redacted job IDs, timestamps, and cancellation results. Never require network confirmation to leave or enter the local latch, and never transmit buffered microphone/audio while latched.
- **missing:** A relay-wide privacy-revocation event with monotonic epoch/version; Cancellation/checkpoint semantics for POST /execute jobs and browser commands; A receipt that distinguishes stopped-before-start, interrupted, and completed-before-revocation; A dashboard and pendant status path that confirms fanout without exposing sensitive job content

### "Let me ask, “Did you actually do that?” and receive a tamper-evident proof that follows the request from my pendant through the relay to the Mac or browser, including which app/session acted, what result came back, and whether anything was skipped or only simulated."
- **useful because:** Today a job receipt can say that a plan or action was recorded, but the owner cannot independently distinguish ‘planned’, ‘dispatched’, ‘executed’, and ‘verified by the target surface’. A signed cross-node provenance chain would make the system trustworthy for consequential work without requiring the owner to inspect logs or remember which body acted.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Deterministic event/proof construction; use the cheaper background model to summarize the chain, and realtime only to answer a spoken question about an existing proof.
- **latency:** Append provenance asynchronously with less than 100 ms overhead per hop. Answer a spoken verification question in under 2 seconds; proof export can take longer.
- **cost:** Low: cryptographic signatures and hashes dominate, with under $0.01 for an occasional natural-language summary.
- **security:** Each node needs an isolated signing key and monotonic counters; private page contents, credentials, screenshots, and microphone data must never enter the proof by default. The proof must state uncertainty explicitly when a target app only acknowledged dispatch rather than confirming the real-world effect. Key rotation and device revocation are required.
- **missing:** Per-node signing keys and a relay-maintained trust registry; A canonical event schema distinguishing planned, accepted, dispatched, executed, observed, and verified states; Mac and browser adapters that return target-surface evidence rather than generic success; A pendant-readable short proof code plus a dashboard endpoint for full-chain inspection; A durable revocation and key-rotation mechanism


## What it asked for

_Nothing._
