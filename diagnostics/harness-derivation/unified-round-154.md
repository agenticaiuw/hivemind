# Harness derivation — unified — round 154

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **approval-loop defect** — The live pipeline still emits “Waiting for your approval on the dashboard,” then renders and uploads that sentence as 24 kHz PCM, while no executable approval completion is exposed. This is a user-visible false affordance, not merely an architectural concern.
  - evidence: GET /pipeline returned job_309f5663... events at 2026-08-07T12:00:38Z (waiting approval), followed by TTS done 24,000 Hz and relay_result done.

## Capabilities it proposed

### "After every spoken answer, let me ask “did that come through?” and get a one-sentence, evidence-backed answer saying whether the relay accepted it, the pendant decoded it, and the bridge actually started playback."
- **useful because:** Relay success is not hearing. This gives the wearer a trustworthy answer when a congested link, stale browser bridge, or decoder failure makes the system appear to have answered while remaining silent.
- **path:** pendant → relay-realtime → mac-planner → mac-vision
- **model tier:** deterministic for correlation and verdict; background model only to compress unusual evidence into speech
- **latency:** Normal query under 300 ms from stored receipts; if a live device probe is required, under 2 s with an explicit stale/unknown result.
- **cost:** Near-zero for deterministic correlation; at most $0.005 for an unusual natural-language explanation.
- **security:** Expose only opaque turn IDs, counters, timings, and failure classes—never raw audio. Reject mismatched session/turn IDs and mark evidence stale after a bounded TTL. Do not claim playback when bridge acknowledgement is absent.
- **missing:** Extend audio_delivery_ack_queue with a bridge-started/bridge-finished acknowledgement and a compact evidence projection readable by the relay; Bind pipeline, Opus, pendant, and ESP32 bridge events to one turn ID end to end; Add a spoken query route that reads the projection without triggering another audio response

### "When the pendant is plugged into my Mac, let me say “run an audio check,” then automatically exercise capture, relay, TTS, Opus, pendant decode, and Bose playback, and tell me exactly which segment failed without saving my speech."
- **useful because:** The hardware is physically testable now even though LTE registration is not. A repeatable owner-triggered check turns silent audio regressions into a clear pass/fail before a real conversation, while keeping the test synthetic and privacy-safe.
- **path:** pendant → mac-planner → relay-realtime → mac-vision
- **model tier:** deterministic fixture and validator; background model only for the final human summary
- **latency:** 30–60 s for a full duplex check; immediate local acknowledgement and progress LED/audio cues.
- **cost:** Under $0.02 per check; most cost is a single optional summary call, while fixture generation and validation are local.
- **security:** Use fixed synthetic tones and nonce-tagged frames, never microphone content. Store only bounded counters and receipts. Require a deliberate button press to start; redact device identifiers in spoken output.
- **missing:** A single orchestrator route that invokes the existing fixture in both directions and correlates its artifacts; USB serial control for the currently attached nRF9160 and ESP32 bridge, including a bridge playback-start receipt; A bounded retention policy for diagnostic artifacts and a clear degraded result when LTE is unavailable

### "If I unplug the Mac or LTE drops during a conversation, keep exactly one turn alive: finish or cancel the current turn, switch transport at a turn boundary, and continue on the other link without replaying my speech or the answer twice."
- **useful because:** The owner should be able to walk away from the Mac without losing a live conversation. This is a genuinely cross-surface behavior: the pendant owns capture and physical turn boundaries, USB and LTE compete for transport, the relay deduplicates turn IDs, and the Mac/bridge reports the handoff.
- **path:** pendant → mac-planner → relay-realtime → mac-vision
- **model tier:** deterministic state machine and relay deduplication; realtime model is unchanged and is invoked at most once per turn
- **latency:** Detect link loss within 500 ms; hand off at the next 60 ms audio frame/turn boundary and resume within 2 s. Never wait indefinitely for a dead transport.
- **cost:** Negligible incremental API cost because no extra model turn is generated; modest relay storage for a bounded handoff record.
- **security:** Bind every frame to device/session/turn/transport generation and reject duplicates from the old path. Do not persist raw audio merely to hand off. On ambiguity, stop playback and tell the owner the turn was not completed rather than guessing.
- **missing:** A relay-side transport-generation and turn-fencing record with atomic ownership transfer between USB and LTE; An explicit end/cancel handshake from the pendant and bridge for the in-flight turn; A reconnect coordinator that can report handoff state to the wearer and expire abandoned turns

### "If I hit the pendant’s emergency stop, cancel every pending or running Mac, browser, relay, and audio action, freeze new autonomous work, and show me a receipt proving each surface reached the stopped state."
- **useful because:** The existing privacy latch protects microphone and playback, but it does not stop an already-running browser command, Mac job, relay job, or queued action. The owner needs one physical control that immediately makes the whole hive inert when something behaves unexpectedly.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-vision → dashboard
- **model tier:** deterministic control-plane operation; no model call
- **latency:** Pendant capture/playback stop immediately; relay broadcasts cancellation within 500 ms; convergence report within 3 s, with explicit unknown states for disconnected surfaces.
- **cost:** Negligible API cost; bounded event and cancellation records are the main storage cost.
- **security:** The stop event must be authenticated by the pendant’s device key and monotonic counter, not the bearer token. Cancellation must be fail-closed: if a surface cannot confirm, mark it isolated and prevent new work when it reconnects. Do not claim cancellation of an irreversible external side effect that already happened.
- **missing:** A firmware emergency-stop event distinct from the local privacy latch; Relay-wide cancellation and freeze state with short expiry and monotonic generation; Mac and browser executors that check the freeze generation before each step and acknowledge cancellation; A single authenticated convergence receipt covering queued, running, and already-completed work

### "Before you use a logged-in page for me, show me which fields and page regions may leave the browser, let me approve a minimum data boundary, and then prove that anything outside that boundary never reached the relay or model."
- **useful because:** The current browser bridge can reach private sessions, but the owner has no enforceable, inspectable boundary on what page contents are exposed to the rest of the hive. This would make browser automation useful without turning every logged-in tab into unrestricted model input.
- **path:** browser-extension → relay-realtime → mac-planner → pendant → dashboard
- **model tier:** deterministic DOM/data classifier with background review for ambiguous fields; realtime only for the owner’s short approval exchange
- **latency:** Preview in under 2 s for ordinary pages; block submission until the boundary is approved. Subsequent actions add under 100 ms of local filtering latency.
- **cost:** Usually under $0.01 per page preview; ambiguous pages may require one background classification call. Storage is bounded hashes and policy, not page copies.
- **security:** Filtering must occur inside the browser before relay upload, with fail-closed behavior when classification is uncertain. Preserve opaque hashes and field labels for audit, never raw secrets. A physical approval should bind the policy to the tab/session and expire when the DOM changes.
- **missing:** A browser-resident pre-upload redaction/filtering layer rather than filtering after relay receipt; Typed field sensitivity labels and DOM-region hashes that survive harmless layout changes but detect meaningful changes; A policy compiler shared by browser and Mac execution so the planner cannot request data outside the approved boundary; A compact pendant/dashboard receipt proving what categories were allowed and blocked

### "For this conversation, keep everything local: capture, transcription, reasoning, browser data, and playback must stay on my pendant/Mac, and refuse or clearly label any step that would send data to the relay or an external model."
- **useful because:** The owner currently has a privacy latch that stops capture, but no affirmative mode for having a conversation while deliberately excluding the cloud. This is the difference between “not recording” and “I can use the system with a local privacy boundary.”
- **path:** pendant → mac-planner → mac-vision → browser-extension → relay-realtime
- **model tier:** local deterministic router plus a local background model where available; never silently fall back to realtime/cloud
- **latency:** Mode acknowledgement under 300 ms; local responses may take up to 5 s. If local capacity is insufficient, refuse rather than leak data.
- **cost:** No relay/model API cost in local-only mode; local CPU and battery use increase, especially for transcription and reasoning.
- **security:** The mode must be enforced before microphone frames or browser content enter relay queues, not as a post-hoc annotation. Show a persistent pendant indicator, reject cloud-only actions, and provide a signed session receipt listing every surface that remained local. Cached cloud credentials and queued uploads must be excluded.
- **missing:** A first-class transport/data-residency policy carried in every turn and browser command; A local speech-to-text and reasoning fallback on the Mac or bridge with explicit capacity limits; Firmware and relay enforcement that rejects frames marked local-only rather than merely trusting the client; A local-only session indicator and post-session audit receipt


## Changes it proposed to its own stack

### `integration` — Replace the blocked-plan response path that currently says “Waiting for your approval on the dashboard” and synthesizes it into 24 kHz audio with an honest pending record: emit a short local status event only, enqueue the plan for the next owner conversation, and expose explicit states pending-delivery, delivered, approved, expired, or cancelled. Do not send TTS until an approval surface actually exists.
- **owner gets:** The owner will stop hearing a sentence that promises a dashboard control that does not exist. Pending actions become findable and resumable at the next conversation instead of silently disappearing.
- effort: Small-to-medium: bridge response handling, pending-store projection, and one regression test against the live pipeline event sequence.  ·  risk: Existing callers may expect a spoken result for blocked plans; migrate them to a distinct pending status and preserve the plan digest. Recovery is replaying the pending record after restart, never re-running the action automatically.
- cost: Negligible API cost reduction because false TTS is removed; small bounded relay/local metadata storage.  ·  latency: Immediate local acknowledgement; approval waits for the next conversation rather than pretending to be available.
- security: Improves safety by preventing accidental interpretation of a spoken promise as consent. Preserve plan/world digest and expiry; do not expose secrets in the pending sentence.
- depends on: Relay persistence for approval records; A real delivery/approval surface, either next-conversation spoken delivery or the already-accepted physical transaction latch; Orchestrator closeLedger fix so pending and completed plans are distinguishable


## What it asked for

_Nothing._
