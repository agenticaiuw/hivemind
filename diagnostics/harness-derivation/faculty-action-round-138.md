# Harness derivation — faculty-action — round 138

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live wearable reachability** — The live device registry exposes Safari with 3 tabs online and the Mac bridge online, but no registered pendant or ESP32 bridge; the physically USB-attached hardware therefore still needs a local serial session layer before relay jobs can use it.
  - evidence: discover(devices) returned Safari on MacIntel online, home-macbook-bridge online, and only cloudflare-contract-test mobile offline; no pendant entry.

## Capabilities it proposed

### "“Run an audio self-test.” Have the Mac drive the USB-connected nRF9160 pendant and ESP32 bridge through a 24 kHz loopback, measure clock drift, underruns, latency, and intelligibility, then tell me the result and save a short diagnostic receipt."
- **useful because:** The owner explicitly wants the 24 kHz path shipped. This turns the physically attached hardware into a repeatable end-to-end test instead of requiring firmware expertise or guessing from logs.
- **path:** mac-terminal → mac-planner → relay-realtime → faculty-perception → faculty-action
- **model tier:** background for orchestration and analysis; realtime only if the owner is asking interactively
- **latency:** under 60 seconds for a normal test; up to 3 minutes for repeated drift measurement
- **cost:** roughly $0.01–$0.10 per run; device I/O and local signal analysis dominate, not model tokens
- **security:** USB serial logs and generated audio remain local by default; transmitting excerpts to relay requires explicit opt-in. No microphone capture; use generated test tones and loopback. Flashing firmware must require separate confirmation.
- **missing:** A local typed tool that can open both known USB serial ports, issue the firmware's test commands, capture timestamped PCM/telemetry, and return measurements; A documented 24 kHz acceptance profile for pass/fail thresholds; A firmware test mode on both chips that exposes deterministic loopback and counters

### "“I’m leaving.” Lock down my computer and preserve my place: lock the Mac, pause or checkpoint reversible jobs, stop browser polling, and make the pendant show a local red/amber status until I return."
- **useful because:** A worn button or spoken command can provide a single, reliable departure action across the Mac, browser, relay, and pendant, reducing the chance of leaving private tabs or half-completed actions exposed.
- **path:** relay-realtime → mac-planner → browser-extension → mac-terminal → faculty-action
- **model tier:** realtime for interpreting the short command; deterministic local handlers for execution
- **latency:** lock within 2 seconds; status reconciliation within 10 seconds
- **cost:** under $0.01 per invocation; almost entirely local control-plane work
- **security:** Locking is low-risk but pausing jobs can lose progress; only pause jobs with checkpoints and record receipts. Never close tabs or delete data. Return status without exposing page contents. A physical pendant trigger should be debounced and require a deliberate long press.
- **missing:** A pendant-to-Mac USB event command and LED status protocol; An idempotent 'departure mode' coordinator spanning browser polling, relay jobs, and Mac lock; A resume/reconcile operation that verifies which jobs actually paused before restoring anything

### "“Bring this task with me.” When I leave the Mac, turn the current task into a compact handoff: what was observed, what remains, links and receipts, and a one-button way on the pendant to resume it when the Mac reconnects."
- **useful because:** The pendant is worn while the Mac is not. A task should not become stranded when the owner walks away; this makes the wearable a continuation of the Mac/browser work rather than a separate chat endpoint.
- **path:** faculty-perception → faculty-judgement → faculty-action → mac-planner → browser-extension → relay-realtime
- **model tier:** background model to summarize and checkpoint; realtime only for the spoken handoff command
- **latency:** produce handoff in under 15 seconds; resume acknowledgement in under 3 seconds after USB reconnect
- **cost:** about $0.02–$0.15 per handoff depending on transcript/page context; local persistence dominates reliability
- **security:** Handoff must redact secrets and private page bodies by default, retaining source URLs and hashes. Resuming an external side effect must require the normal confirmation gate and show the last receipt; reconnect alone must never execute.
- **missing:** A compact signed task-handoff schema with source timestamps, pending steps, and redaction policy; Pendant storage/transport for a small handoff packet over USB (and later LTE) with reconnect reconciliation; A resume endpoint that revalidates browser tab/session affinity and Mac job state before acting

### "“Keep my voice usable when the connection gets bad.” Have the pendant and bridge detect packet loss, clock drift, or radio/USB degradation, switch to the most intelligible safe audio mode locally, and tell the Mac/relay what changed so the conversation can continue without me debugging it."
- **useful because:** A wearable conversation that fails silently is unusable. Local adaptation preserves intelligibility during transient failures, while the Mac and relay retain a truthful explanation and can restore the preferred 24 kHz mode when conditions recover.
- **path:** relay-realtime → faculty-perception → faculty-action → mac-terminal → mac-planner
- **model tier:** deterministic firmware policy for fast adaptation; background model only for explaining the incident afterward
- **latency:** adapt within 100 ms of a sustained fault; human-readable explanation within 10 seconds
- **cost:** near-zero API cost during calls; only occasional low-cost incident summarization
- **security:** Audio stays on the active path and is not retained merely because adaptation occurred. Telemetry should contain counters and mode changes, not speech content. Any remote change to modem parameters must require an explicit policy.
- **missing:** A dual-mode codec/transport policy implemented in both chips; A shared telemetry event schema for mode changes and recovery; Relay and Mac logic that surfaces degradation without interrupting the owner

### "“When something fails, give me the complete case file.” Gather the correlated pendant UART log, Mac job receipt, browser command IDs, timestamps, and the exact failed step into one redacted incident bundle, then leave a concise explanation and a reproducible next action."
- **useful because:** Today a failure can be spread across wearable logs, relay records, and browser state. A single evidence bundle would let the owner fix or report a problem instead of repeatedly asking what happened.
- **path:** faculty-perception → faculty-action → mac-terminal → mac-planner → browser-extension → relay-realtime
- **model tier:** background model for correlation, redaction, and explanation; deterministic collectors for raw evidence
- **latency:** bundle available within 30 seconds of failure; explanation under 15 seconds after collection
- **cost:** about $0.02–$0.20 per incident depending on log size; local collection dominates
- **security:** UART may contain credentials or personal data, and browser evidence may be private. Redact secrets locally, retain hashes and minimal snippets by default, and require confirmation before uploading or filing externally.
- **missing:** A cross-surface correlation ID propagated into firmware diagnostics, Mac jobs, and browser commands; A local UART collector with bounded, encrypted retention; A redaction/export service that can produce a reproducible bundle without exposing page contents

### "“Tell me whether this automation is still trustworthy.” Periodically exercise a safe, non-destructive canary across the pendant, Mac, relay, and browser bridge, compare each result with its expected invariant, and alert me only when a real capability has regressed."
- **useful because:** A green process or heartbeat does not prove that the whole hive can act. A small end-to-end canary would catch broken serial paths, stale browser sessions, expired Mac permissions, and relay mismatches before the owner needs the system.
- **path:** relay-realtime → mac-planner → mac-terminal → browser-extension → faculty-perception → faculty-action
- **model tier:** cheap background/scheduled model; deterministic assertions for pass/fail
- **latency:** daily scheduled run in under 2 minutes; urgent failure notification within 1 minute
- **cost:** under $0.05 per scheduled run; local test execution dominates
- **security:** Use synthetic data and a dedicated harmless test page/document. Never send mail, mutate private records, or navigate to arbitrary URLs. Store only status, timestamps, and failure evidence.
- **missing:** A synthetic browser canary target and Mac-safe test intents; A pendant serial/audio canary command that cannot alter production state; A scheduler and regression history joining all surfaces by one run ID


## Changes it proposed to its own stack

### `firmware` — Add a compile-time diagnostic mode to the nRF9160 and ESP32 bridge that emits framed 24 kHz test telemetry over their existing USB serial links: sequence number, sample counter, dropped-frame counter, DMA underruns, codec rate, and monotonic timestamp. The mode must be read-only with respect to radio credentials and disabled in production builds.
- **owner gets:** They can know whether the wearable audio is actually reliable, with a concrete pass/fail report, before trusting it in daily use.
- effort: 2–4 engineering days across both firmware targets plus a host parser; no hardware changes.  ·  risk: Diagnostic output could contend with the audio stream or expose verbose logs; rate-limit telemetry, use a separate command channel, and compile it out of release builds. Recovery is reboot into normal firmware.
- cost: No API cost; negligible flash/RAM overhead in diagnostic builds.  ·  latency: Less than 1 ms control overhead if counters are sampled from existing ISR state.
- security: No secrets emitted; explicitly redact modem and pairing data.
- depends on: A host-side USB serial probe/parser; The agreed 24 kHz acceptance thresholds

### `mac-harness` — Add a USB-wearable session manager that discovers the known nRF9160 and ESP32 serial identities, claims exclusive leases, timestamps reconnects, and exposes a typed device session to jobs. It must refuse destructive firmware operations and provide a clear receipt when either device disappears.
- **owner gets:** A plugged-in pendant should work immediately today instead of each agent guessing ports or silently talking to the wrong serial device.
- effort: 1–2 engineering days; udev/IOKit identity matching, lease handling, and a small local API.  ·  risk: A stale lease could block another tool or a reconnect could be misidentified; expire leases quickly, verify USB VID/PID plus serial identity, and offer a local release command.
- cost: Negligible API cost and CPU; no hardware cost.  ·  latency: Device discovery under 1 second; reconnect event under 2 seconds.
- security: Keep serial access local to the agent; never upload raw UART unless a job explicitly requests it.
- depends on: Stable USB identities for both connected chips; A typed host tool for serial read/write

### `interaction` — Create a physical-presence continuity protocol: when the pendant is USB-attached, a deliberate long press emits a signed nonce; the Mac agent binds that nonce to the currently active task and returns a receipt plus LED pattern. Reconnect requires a fresh nonce before resuming any pending side effect.
- **owner gets:** Walking away or returning becomes unambiguous: the wearable can carry the task context without accidentally resuming an email, purchase, or other external action.
- effort: 3–5 engineering days across pendant firmware, USB bridge, relay, and Mac job coordinator.  ·  risk: Button bounce, accidental presses, or replayed nonces could trigger work; use hardware debounce, monotonic counters, expiry, and require normal confirmation for irreversible actions.
- cost: No recurring API cost beyond tiny receipt metadata; under 1 KB per event.  ·  latency: Sub-second local acknowledgment; relay synchronization can take a few seconds.
- security: Nonce binding prevents replay and makes physical presence explicit; do not encode task contents in the nonce.
- depends on: A pendant button event transport; The durable task-handoff schema; Per-job resume precondition checks


## What it asked for

_Nothing._
