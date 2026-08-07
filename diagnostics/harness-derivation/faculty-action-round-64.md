# Harness derivation — faculty-action — round 64

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **execution surface readiness** — Mac agent is configured and relay reachable, but browser bridge is offline with 5 pending commands; Accessibility and Screen Recording are ungranted while AppleScript automation grants are present. Relay reports durable audio and persistent state enabled.
  - evidence: GET /ops/status returned agent ready:false, browser.online:false pendingCommands:5, accessibility.trusted:false, screenRecording.granted:false, automation grants true, relay.reachable:true, durableAudio:true.

## Capabilities it proposed

### "“Do this across my Mac and logged-in browser, and keep going if I walk away; tell me exactly what happened, and never repeat a step after a dropped connection.”"
- **useful because:** Today judgement can choose a multi-surface action, but execution cannot reliably carry a typed plan across Mac, browser, relay, and pendant interruption boundaries. This would turn a decision into a resumable real-world transaction: the pendant can announce staged/running/blocked/completed, the relay can keep the lease alive, the Mac or browser performs only the next verified step, and the owner gets a concise receipt rather than a vague success/failure.
- **path:** faculty-judgement → faculty-action → relay-realtime → mac-planner → browser-extension → unified
- **model tier:** Use the cheap background model to compile a decision into a typed step graph and reconcile receipts; use realtime only for the owner's live request and a short status utterance. No model call is needed to replay an already verified step.
- **latency:** Acknowledge on the pendant in under 500 ms; begin the first reversible step within 2 s. Resume after reconnect within 10 s. Human approval remains required immediately before sending, deleting, purchasing, or other irreversible steps.
- **cost:** About $0.003–$0.02 per ordinary multi-step job depending on graph compilation and receipt summarization; durable state and step hashes dominate engineering/storage cost, not inference.
- **security:** Persist only opaque job IDs, step hashes, target surface, and redacted evidence by default; never copy page secrets into relay logs. Bind each step to account/session/tab identity and an expiry lease. Require owner confirmation for irreversible effects, and expose undo where available. A stale lease or changed precondition must stop rather than guess.
- **missing:** A durable cross-surface step runner with atomic checkpoint commit and idempotency keys (the current browser runner backlog is still open).; A typed action envelope shared by judgement and faculty-action: preconditions, effect class, proof required, lease expiry, retry policy, and owner-confirmation state.; Pendant/relay status events for staged, waiting-for-approval, resumed, blocked, and completed; current durable audio exists but action-state delivery is not established.; Semantic receipt verification that records before/after evidence and prevents replay after a disconnect.

### "“Show me exactly what will change, and let me approve it from the pendant—even when I’m away from my Mac—but cancel that approval if anything on the page or target changes.”"
- **useful because:** The owner can currently prepare browser work and may approve reversible actions, but cannot safely carry approval from a cited preview to a later execution on another surface. This gives them a wearable-native, exact-intent consent token: the pendant speaks a compact before/after summary and receives one deliberate approval; faculty-action executes only if the same tab/session, target identity, evidence hash, and effect class still match. A changed price, recipient, amount, page, or account automatically invalidates the approval and asks again.
- **path:** relay-realtime → faculty-judgement → faculty-action → browser-extension → mac-planner → unified
- **model tier:** Use a small background model to compress cited before/after evidence into a short spoken approval card; realtime is only for the live confirmation exchange. Verification and invalidation are deterministic hashes and policy checks, not model work.
- **latency:** Approval prompt under 1 s after preparation; execution starts within 2 s of a valid pendant approval. Any stale or changed target blocks immediately and reports the reason in one spoken sentence.
- **cost:** Under $0.005 per approval for evidence summarization; cryptographic binding, expiry records, and receipts dominate implementation rather than inference.
- **security:** Never treat voice recognition alone as authorization. Require a physical pendant button press after the spoken challenge, bind the token to job ID, exact effect summary, target/session/tab, evidence hash, expiry, and owner policy. Do not store raw page data or audio in relay logs; keep only redacted hashes and a receipt. Sending mail, deleting, purchasing, or account/security changes always require this explicit approval and must offer a clear cancel path.
- **missing:** A signed, single-use approval-token format shared by relay, judgement, action, and browser bridge.; A pendant status/confirmation event with replay protection and a way to display or speak the exact effect summary.; A deterministic pre-execution verifier that re-reads target identity and cited before/after values and invalidates tokens on any mismatch.; A receipt field that proves which approval token authorized which browser/Mac effect.


## Changes it proposed to its own stack

### `firmware` — Add an end-to-end audio handoff watchdog and loss-tolerant frame contract: every 24 kHz/60 ms Opus frame carries a monotonically increasing stream sequence and presentation deadline; the nRF9160 records decode time, ring-buffer depth, underruns, and CRC/sequence gaps in a compact  telemetry record, while the ESP32 bridge reports resampler starvation and SBC queue depth. On a missed deadline, the pendant emits a bounded comfort tone/status event and requests only the missing frame range instead of silently continuing. The relay stores a short encrypted replay window keyed by stream ID and sequence, and the Mac TTS producer publishes the same contract. Add an offline fixture that feeds synthetic speech and verifies 24 kHz decode -> 31,250 Hz I2S -> 44.1 kHz SBC without gaps.
- **owner gets:** Briefings and replies would stop going mysteriously silent. If the owner walks between relay coverage and headphones, the system can recover a small gap, say that audio is degraded, and leave a diagnosable receipt instead of pretending the message played. This is grounded in the current prototype's 25.4 ms decode per 60 ms frame, 87% combined encode/decode CPU load, and the bridge's known 44 kB-buffer starvation failure.
- effort: Medium/high: define a versioned frame header, implement compact counters and replay-window lookup in firmware/relay, add bridge telemetry, and build a host-side deterministic fixture. No flash should occur until the owner approves and the fixture passes.  ·  risk: Extra headers and telemetry consume airtime, flash, and RAM; replay can increase latency if the window is too large. Keep the window to a few seconds, cap counters, and fall back to live playback after one bounded retry. If the contract version is unknown, fail closed with a status event. Recovery is a firmware rollback plus relay feature flag.
- cost: Negligible inference cost; roughly 1–3% extra uplink/downlink bytes and small persistent relay storage per active stream. Hardware unchanged.  ·  latency: Normal path adds under 5 ms bookkeeping; recovery adds at most one frame interval plus network RTT (target under 300 ms).
- security: Stream IDs and replay objects must be opaque and encrypted/TTL-deleted; telemetry must contain no audio payload or transcript. Sequence metadata can reveal listening times, so retain briefly and restrict to the owner's job.
- depends on: 24 kHz acceptance criteria from the owner; audio_path_probe tool or an equivalent host/bridge loopback test; Permission to read/build the pendant simulator firmware (not yet granted); A relay route for bounded encrypted frame replay and typed telemetry


## What it asked for

_Nothing._
## Its own summary

I discovered the live boundary and recorded two new proposals. First: a typed, resumable cross-surface execution envelope so judgement can hand faculty-action an idempotent step graph with preconditions, leases, approval gates, and receipts across relay/Mac/browser/pendant; it pauses safely instead of replaying after disconnects. Second: a firmware/relay audio frame contract with sequence numbers, deadlines, underrun telemetry, bounded replay, and a deterministic 24 kHz→I2S→44.1 kHz fixture, aimed at preventing silent or unverifiable briefings. Fresh status confirms relay and durable audio are reachable, but browser is offline with five pending commands and TCC GUI permissions remain absent; AppleScript automation is available.

**Biggest unknown:** The owner’s authoritative 24 kHz acceptance criteria, the audio loopback probe, and firmware read/build permission are still outstanding. I did not re-request them this round. I also still need confirmation from faculty-judgement on whether interruption handoff/attention arbitration is already represented by an existing backlog item.

