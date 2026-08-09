# Harness derivation — unified — round 186

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live readiness** — Mac local agent is healthy at version 0.5.0; home-macbook-bridge is online, Safari has two tabs online, and the cloudflare contract-test device is offline. The granted incident_diagnostics schema did not resolve in the live inventory this round, so it cannot currently provide the promised correlated snapshot.
  - evidence: GET /health returned 200; discover(devices) returned the three statuses; incident_diagnostics returned resolution:'unresolved' with nearest GET /ops/snapshot.

## Capabilities it proposed

### "Set up and certify my pendant over USB, then tell me exactly what works and what does not."
- **useful because:** The hardware is physically here and testable now, but today commissioning still requires knowing firmware logs and separate checks. This gives the owner a one-command, human-readable readiness report covering the real nRF9160, ESP32 bridge, microphone, speaker, buttons, privacy latch, approval latch, USB audio session, and 24 kHz path—before trusting it away from the Mac.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** background for the deterministic test plan and report; realtime only to narrate the result over the pendant
- **latency:** 30-90 seconds for a full wired certification; individual hardware checks should return within 5 seconds
- **cost:** Near-zero model cost for scripted checks; one short background summary, dominated by no API cost rather than inference
- **security:** The fixture must use synthetic audio only, never record room audio, and must not transmit secrets. Physical approval/privacy states must be tested without clearing the owner's privacy latch or approving a real transaction. Require explicit confirmation before any firmware flash or persistent calibration write.
- **missing:** A Mac serial harness that can address both /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA with typed commands and capture timestamped receipts; A firmware/bridge commissioning command protocol exposing synthetic loopback, button/LED state, latch state, monotonic counters, and bridge acknowledgements; A persisted signed device capability manifest and a dashboard/readout that distinguishes tested, skipped, and failed rather than treating absent LTE registration as failure

### "Keep this conversation going when I unplug the Mac or leave USB range—don't make me repeat myself or hear the same answer twice."
- **useful because:** The pendant is usable over USB today but LTE is not registered. A transport change is currently a hidden failure boundary: a turn can be captured twice, dropped, or played twice. This capability makes walking away from the Mac feel like one conversation, with an explicit owner-visible handoff point and no duplicate speech.
- **path:** pendant → mac-bridge → relay-realtime → mac-planner
- **model tier:** deterministic state machine for sequence/turn reconciliation; background tier only for a concise recovery explanation
- **latency:** Handoff decision under 250 ms at a turn boundary; recovery status under 2 seconds; never interrupt an active utterance
- **cost:** Negligible inference cost; small relay storage for a bounded turn checkpoint and receipts
- **security:** Bind checkpoints to an authenticated device/session and monotonic turn counter. Never replay captured audio merely to reconcile. Drop stale transport claims, expose whether a turn was heard versus merely accepted, and require confirmation before abandoning an in-progress staged action.
- **missing:** A relay-side session/transport lease and atomic compare-and-set handoff record; the existing job lease gap means two transports could claim one turn; A USB serial transport adapter that emits the accepted usb_fallback_audio_session sequence fields and a relay adapter for LTE when it becomes available; A single owner-facing handoff receipt joining capture, model response, and physical playback acknowledgement

### "Show me every fact you inferred about me from this conversation, let me point to one, and erase it everywhere."
- **useful because:** The system can extract facts into context storage that the owner did not explicitly create, but there is no owner-facing inventory or precise erase receipt. This makes remembering auditable: the owner sees the exact extracted claim and evidence, can delete only that claim and its derived copies, and is told when off-machine deletion is still pending rather than being falsely told it is gone.
- **path:** pendant → relay-realtime → mac-planner → dashboard
- **model tier:** background model to cluster and explain candidate facts; deterministic deletion and receipt logic; realtime only when the owner asks verbally
- **latency:** List within 3 seconds for local facts; deletion acknowledgement within 2 seconds locally and an explicit pending state for relay replicas
- **cost:** One inexpensive extraction/list pass; deletion itself is deterministic and near-zero inference cost
- **security:** Default to showing evidence before storing or deleting. Never include raw audio in the list. Require an exact fact identifier or a spoken confirmation for deletion, preserve action audit history, redact secrets in evidence capsules, and distinguish local erased from relay deletion requested/pending.
- **missing:** A typed fact inventory route returning stable fact IDs, provenance capsules, derived-copy IDs, and retention reason; An atomic tombstone protocol spanning facts.json/context graph and relay replicas, with retry and a verifiable pending receipt; A pendant/dashboard presentation that can read a short fact label and exact deletion target without exposing unrelated private context

### "Calibrate the pendant and headphones to my hearing once, then make every reply as clear and safe as possible without me adjusting volume."
- **useful because:** The owner should not have to solve intelligibility by repeatedly changing volume or tolerating harsh speech. A short, synthetic hearing-and-device calibration could measure the actual pendant-to-bridge path, establish a personal speech-preserving EQ and safe loudness ceiling, and apply it consistently across model replies while keeping the owner's raw hearing-test responses local.
- **path:** pendant → mac-bridge → mac-planner → relay-realtime
- **model tier:** Deterministic signal generation, measurement, and DSP profile selection; background tier only to explain the result in plain language
- **latency:** Initial calibration under 5 minutes; profile application adds less than one audio frame; no model round trip during playback
- **cost:** Near-zero API cost after setup; a few kilobytes for the profile and negligible per-turn computation
- **security:** Use synthetic tones and speech-shaped test signals only; do not upload microphone recordings or infer medical conditions. Store the profile locally, show exactly what is measured, expose a reset, and warn that it is an accessibility aid rather than a clinical hearing test.
- **missing:** A calibration protocol spanning the nRF9160 output, ESP32 resampling/A2DP path, and the owner's actual headphones; Bridge DSP controls for a bounded EQ, loudness ceiling, and soft limiter that preserve the shipped 24 kHz source path; A local profile store and an owner-facing calibration/reset flow with versioned receipts so a changed headset cannot silently reuse the wrong profile

### "Read this private page to me through the pendant, but keep its text off the relay, out of browser history, and out of your memory."
- **useful because:** The browser can reach accounts and pages that the relay should never receive. Today the owner must choose between manually reading the page and sending its contents through the cloud conversation. A locality-bound read would let the Mac/browser retrieve and summarize or speak the page locally, while the pendant receives only audio and an opaque completion receipt.
- **path:** browser-extension → mac-planner → mac-bridge → pendant → relay-realtime
- **model tier:** Local Mac model or deterministic extraction for page text; realtime model only if the owner explicitly requests a cloud question about the page
- **latency:** Begin speaking within 2 seconds for visible-page text; local-only operation must remain usable if the relay is offline
- **cost:** No relay token cost for plain reading; local model cost depends on summarization length; bounded temporary storage is deleted after playback acknowledgement
- **security:** Bind the operation to one explicitly selected tab, reject cross-origin navigation during the job, never send page text or screenshots to the relay by default, disable browser-history/search mutation, wipe temporary text and audio after acknowledgement, and show a visible local-only indicator. Any cloud question must be a separate explicit confirmation.
- **missing:** A browser command that returns selected-page text directly to the Mac agent without relay publication or persistent inspection records; A local TTS/audio path from Mac to the USB-connected pendant/bridge, with a no-cloud receipt; A lifecycle scrubber that proves temporary page text, generated audio, and model context are removed after completion


## Changes it proposed to its own stack

### `firmware` — Add a bridge-side fail-closed playback watchdog: require monotonic frame/turn sequence advancement and a bounded inter-frame deadline, fade to silence on timeout or malformed input, reset the SBC/A2DP pipeline without replaying buffered audio, and emit a compact reason-coded recovery receipt when the stream resumes. Keep buffers below the measured 44 kB starvation threshold.
- **owner gets:** If the relay, USB link, or pendant stalls, the headphones should go quiet instead of hanging on a repeated fragment, emitting a click, or remaining apparently connected while no new speech can arrive. Recovery should be automatic and audible only as the next valid turn.
- effort: Medium: bridge firmware state machine, timeout tests, and a USB fault-injection harness; no new hardware required.  ·  risk: An overly short deadline could cut speech during normal Bluetooth jitter; use measured jitter margins and hysteresis. A reset can lose the tail of a sentence, so report it and let the session layer decide whether a concise replay is appropriate—never replay blindly.
- cost: No API cost; a few hundred bytes of state and a small CPU load. Keep RAM well below the known 44 kB failure point.  ·  latency: Silence after roughly one missed deadline; resume at the next valid frame, with no extra model round trip.
- security: Fail-closed prevents stale audio from continuing after a privacy latch or transport loss, but receipts must contain IDs/counters only, never PCM.
- depends on: usb_fallback_audio_session sequence numbers; audio_delivery_ack_queue for physical playback receipts; The ESP32 bridge's measured 44 kB buffer ceiling and SBC-only 44.1 kHz output

### `interaction` — Add a physically initiated guest-session boundary: a deliberate button action creates a short-lived, capability-limited conversation identity with a fresh context, no access to owner memories, browser sessions, Mac actions, extracted facts, or pending transactions; the pendant LED and spoken opening identify guest mode, and ending it cryptographically invalidates the session and scrubs its temporary context.
- **owner gets:** The owner could hand the pendant to a friend, child, technician, or visitor without handing over their private assistant. They get a useful generic voice interface while the owner's accounts, memories, and queued actions remain unreachable.
- effort: High: identity/session policy across pendant, relay, Mac, and browser, plus a clear physical enter/exit flow and adversarial tests.  ·  risk: A confused exit or stale guest token could either expose owner context or strand the owner in guest mode. Default to guest on uncertainty, expire automatically, require a deliberate local exit, and make every privileged request fail closed with an explanation.
- cost: Small bounded relay/session storage and negligible inference overhead; no new audio bandwidth.  ·  latency: One extra local session check per turn, targeted below 20 ms; no added speech latency.
- security: Strongly positive if context and capability checks are enforced server-side rather than by prompt. Requires separate guest and owner authorization domains, revocation, audit receipts, and no secrets in guest error messages.
- depends on: physical_transaction_approval_latch for deliberate local state change; A relay session-identity and capability firewall; Mac/browser routes that accept an explicit session capability rather than only the single bearer identity; A pendant LED/status protocol that clearly distinguishes guest from owner mode


## What it asked for

_Nothing._
