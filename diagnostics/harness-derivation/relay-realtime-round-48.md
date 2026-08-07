# Harness derivation — relay-realtime — round 48

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Keep our conversation intelligible while I’m walking, and tell me when the audio link—not my words—is the problem.”"
- **useful because:** Today the physical path has materially different rates (15,625 Hz microphone capture, 16 kHz/16 kbps Opus uplink, 24 kHz TTS playback resampled to 31,250 Hz I2S), but the owner gets no end-to-end quality diagnosis or recovery. A rate-aware path would prevent avoidable speech distortion and distinguish packet/audio failures from recognition failures instead of making the owner repeat themselves.
- **path:** pendant → relay → dashboard
- **model tier:** Realtime only for conversational acknowledgement and a short spoken diagnosis; deterministic DSP/telemetry and a cheaper background analyzer should handle quality scoring and trend detection.
- **latency:** Local framing and rate conversion under 50 ms; relay quality decision under 150 ms; any spoken warning within the next turn. No cloud model call for ordinary healthy audio.
- **cost:** Negligible model cost in the healthy path; roughly $0.001–$0.01 per degraded-session analysis depending on whether a background model summarizes the telemetry. Main cost is firmware/relay implementation and test coverage.
- **security:** Transmit compact acoustic/network metrics (loss, jitter, clipping, underruns, effective sample rates), not raw audio beyond the existing conversation. Avoid retaining voice-derived quality snippets; require explicit owner-visible opt-in if diagnostic audio samples are ever uploaded.
- **missing:** Pendant firmware rate-contract and quality telemetry (including effective input/output rates, clipping and buffer health); Relay audio pipeline that preserves declared versus effective rates, performs validated resampling, and uses jitter/loss recovery; A small local quality classifier and spoken-status vocabulary so the realtime model does not guess from transcript confidence; Dashboard/history view showing per-turn audio health and whether recovery succeeded; End-to-end test fixture covering 15.625 kHz capture through 16 kHz Opus and 24 kHz playback

### "“Stop that.” (At any point while you hear a response or a Mac/browser task is running.)"
- **useful because:** The pendant is the always-present front door, yet an action handed to the Mac or browser can outlive the spoken turn and there is no guaranteed, cross-surface emergency cancellation path. The owner should be able to interrupt speech immediately and propagate cancellation to queued or in-flight downstream work, especially when the original request was misunderstood.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** No expensive model is needed: device button/voice keyword detection, relay state machine, and downstream cancellation tokens should do the work. Realtime is only used to acknowledge cancellation in speech.
- **latency:** Mute/stop local playback in under 100 ms; relay acknowledgement under 250 ms; cancellation signal to Mac/browser under 500 ms where the underlying operation supports interruption. If an operation cannot be interrupted, report that explicitly rather than claiming success.
- **cost:** Near-zero per invocation; implementation and integration-test cost dominates. Persistent cancellation state needs a small durable record per active job.
- **security:** A false trigger could stop useful work, so the device should require the explicit wake context or a deliberate button gesture, while preserving the owner's no-confirmation policy. Cancellation requests and the operation they affected should be retained as an auditable receipt; no new content needs to leave the device.
- **missing:** A pendant-local stop gesture/keyword path that works while TTS is playing; Relay-owned active-turn registry mapping one spoken interaction to every downstream job and transport; Cancellation-token protocol implemented by mac-planner, mac-vision, and browser-extension, including honest non-cancellable states; Audio mixer/stream control that can cut playback without waiting for a model turn; Dashboard receipt showing requested, propagated, and effective cancellation timestamps

### "“Do it, and only tell me it’s done when you can verify the result.”"
- **useful because:** Current delegated work can produce an execution receipt without proving the requested world state changed. A relay-coordinated postcondition check would have the Mac agent perform the mutation, the browser/session surface or Mac read back the resulting state, and the relay speak a truthful success, partial-success, or unverifiable outcome. This is especially valuable when the owner is away from the screen and cannot inspect it.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use the planner for structured pre/postcondition extraction and a cheap deterministic comparator for readback; reserve realtime for the owner-facing response. Do not spend realtime tokens narrating intermediate actions.
- **latency:** For simple local actions, verification should add under 1 second; for browser tasks, up to 5 seconds is acceptable. The owner should hear an immediate “working” acknowledgement and a final result only after the check or a clear timeout.
- **cost:** About $0.002–$0.03 per delegated operation when planner reasoning is needed; deterministic local/browser reads dominate latency, not model cost. Storage is a compact operation/postcondition receipt.
- **security:** Readback may expose authenticated page or local-app content to the relay. Minimize it to typed fields and redact secrets; retain hashes/diffs rather than screenshots by default. Never claim verification from an unchanged or ambiguous state; expose ambiguity in the spoken result.
- **missing:** A typed goal format carrying expected postconditions, not just an action list; Mac and browser adapters that return minimal typed readbacks with session/tab affinity; Relay verifier and timeout state machine that distinguishes success, failure, partial, and unverifiable; Cross-surface correlation IDs and dashboard display of before/after evidence; Planner prompts/tests for extracting safe, observable postconditions from natural speech


## What it asked for

_Nothing._
## Its own summary

Discovery shows the production tools are present (get_mac_status, mac_run_actions, browser_run_actions, web_search, mac_delegate, read_web_page, relay_job_status) and the granted list includes new routing/status concepts, but the relay_route_intent tool is not actually available under the discover/describe contract. I can describe and use mac_delegate and relay_job_status for routing and status, and relay_job_status is explicitly for Mac work already handed off.

**Biggest unknown:** Whether the intended new relay routing tool (relay_route_intent) is implemented under a different name or simply not wired into the tool registry yet; until it exists, routing is still implicit via which tool I call, which limits explicit observability and status handoff across surfaces.

