# Harness derivation — mac-terminal — round 248

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **bench USB visibility** — The granted mac_usb_serial_diagnostics schema still cannot execute against the live inventory; no serial/USB capability is published. The nRF9160 and ESP32 remain physically connected but I cannot truthfully report their UART health from this agent.
  - evidence: Called mac_usb_serial_diagnostics for all four documented ports with 1s bounded read; resolver returned unresolved, nearest action:get_mac_status (0.226), and inventory has no serial capability.

## Capabilities it proposed

### "Make my pendant's voice sound clear and natural, then tell me whether the audio link passed before I rely on it."
- **useful because:** This is the most valuable thing the system can do: a real conversation must remain intelligible end to end, not merely claim that Opus packets moved. It would run a spoken test tone/phrase, measure capture, encode, relay transcode, decode, I2S playback, latency, underruns and packet loss, and report one actionable result. It directly addresses the owner's current request to ship the 24 kHz superwideband path.
- **path:** pendant → relay-realtime → mac-planner → dashboard
- **model tier:** Use deterministic firmware/relay DSP and a cheap background model to summarize measurements; reserve realtime only for the owner's spoken request and final sentence.
- **latency:** A 10-second bounded test should finish in under 15 seconds; normal conversation stays realtime and must not wait for diagnostics.
- **cost:** Negligible model cost for a structured report; roughly 10 seconds of audio storage/transfer per test, dominated by R2 traffic if raw traces are retained. Keep only metrics by default.
- **security:** The test can include a synthetic phrase, not microphone recordings. Do not upload ambient audio outside the active test. Require an explicit spoken request before emitting a loud test signal; dashboard shows the raw metrics and firmware/version hashes.
- **missing:** A real authenticated audio-test command spanning USB-bench and LTE routes; A 24 kHz end-to-end framing contract: current capture is 15,625 Hz while playback decode is 24 kHz, and both share one full-duplex I2S peripheral; Relay-side metric collection for sequence gaps, jitter, transcode time and acknowledgements; A Mac/ESP32 bench adapter that can inject and capture known frames without pretending USB is a product transport

### "If something you ran on my Mac fails, explain what actually failed, show me the exact command and evidence, and offer the safest one-step recovery without making me repeat the whole task."
- **useful because:** Today a failed shell action loses the exit code, can run for 120 seconds after cancellation, has no durable job-to-ledger join, and may leave the job stuck after a restart. The owner should hear a truthful, compact diagnosis on the pendant and be able to resume from the failed step instead of guessing or rerunning side effects.
- **path:** mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Use deterministic receipt enrichment and recovery classification first; use a cheap background model to summarize stderr and suggest a bounded recovery. Realtime only speaks the one-sentence status when requested.
- **latency:** Failure status should reach the pendant within 2 seconds of process exit. Recovery planning can take up to 10 seconds and must never silently execute a mutation.
- **cost:** Low: receipts are small JSON and the model sees capped stderr plus metadata, not the whole environment. Cost is dominated by occasional recovery summaries.
- **security:** Never store inherited secrets from env; hash or allowlist environment names. Redact tokens from stdout/stderr. A recovery proposal must be visibly separate from execution, and destructive actions remain subject to the owner's existing policy. The pendant should say 'failed' rather than infer success when the Mac disappears.
- **missing:** Capture exit code, signal, argv/command hash, resource timing and child PID in the shell receipt; Pass cancellation to the child process group and reconcile processing jobs on boot; Close the action ledger and persist planMeta.jobId so job, receipt and ledger are joinable; A resume endpoint that replays only failed, idempotent steps and marks non-replayable steps as requiring a new plan

### "Keep working on this while I leave my Mac, and interrupt me only if you need a decision; otherwise tell me the result when I am back in range."
- **useful because:** Today a task handed to the Mac is effectively tied to that host and its polling link. The owner cannot transfer an in-progress multi-step job to the always-awake relay/pendant, continue through a Mac sleep or network loss, and return to a trustworthy result. This would make the hive feel like one persistent assistant rather than a voice front end attached to one computer.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use a durable deterministic task state machine and checkpoint protocol; use a cheap background model for step selection and result summarization. Realtime is used only for a decision request or the final spoken result.
- **latency:** A handoff acknowledgement should reach the pendant within 2 seconds. Ordinary checkpoints can take 1–5 seconds; the owner should not wait synchronously for a long task.
- **cost:** Low-to-moderate: one model call per ambiguous checkpoint, with compact state rather than full conversation context. Storage is bounded task state and receipts; browser page contents remain ephemeral unless the owner asks to save them.
- **security:** The relay must never gain blanket Mac authority: each checkpoint carries the originally authorized action scope and expiration. Browser sessions and Mac credentials stay on their surfaces. A task that reaches a send/delete/purchase step pauses for the owner's explicit decision on the pendant. The spoken result must distinguish completed, paused, expired, and host-lost.
- **missing:** A portable, versioned task-state/checkpoint format with idempotency keys and a lease owner (Mac, relay, or browser); A relay worker that can hold a task while the Mac is asleep and request a reconnect instead of declaring success; Mac execution that reports a durable checkpoint after every step, including output references and whether the next step is replay-safe; Browser-session capabilities that can resume a named authenticated session after a host handoff without exporting cookies; Pendant protocol support for compact decision prompts and signed approve/deny replies, beyond the existing action-status beacon

### "Watch me do this once, learn the parts that are safe to repeat, and run it for me every Friday—stopping and asking only when the website or my files have materially changed."
- **useful because:** Current routines store a command and schedule it, but the owner cannot demonstrate a multi-surface workflow once and have the system preserve its intent, detect UI/file drift, and safely re-plan the changed step. This would turn repeated personal computer work into a reliable skill instead of a brittle macro.
- **path:** mac-planner → browser-extension → relay-realtime → pendant → dashboard
- **model tier:** Use the computer-use/browser traces and deterministic action fingerprints for replay and drift detection; use a cheaper background model to abstract the demonstration into intent and to explain a changed step. Realtime only asks the owner about a drift decision.
- **latency:** Recording adds no noticeable latency. A scheduled replay should start within 30 seconds of its trigger; drift analysis under 15 seconds before asking.
- **cost:** Moderate once per demonstration and low on repeats. Store compact action fingerprints, selectors, file identities and outcomes, not screenshots or full page text unless needed for diagnosis.
- **security:** Demonstration must label secrets and never record passwords, tokens, or private page text. Safe steps can run unattended under the owner's existing policy; sending, deletion, purchases, and irreversible file changes pause for confirmation. Each replay needs a visible diff of what changed and an undo/reference receipt where possible.
- **missing:** A demonstration recorder that captures semantic intent alongside browser and Mac actions; Stable action fingerprints for URLs, DOM targets, file paths and app state, with drift scoring; A routine version store with per-step replay safety and a human-readable change report; A scheduler that can invoke the learned workflow across browser and Mac surfaces rather than only a free-text command; A pendant decision packet small enough to approve one changed step without opening the dashboard

### "When several things are waiting on me, give me one short decision queue on the pendant, in priority order, and let me answer each with a clear yes, no, or later without reopening my Mac."
- **useful because:** Today a blocked browser task, Mac job, or scheduled routine can each wait in its own surface. The owner has no single place to resolve consequential choices while walking around, and stale prompts can be mistaken for current requests. A durable decision queue would make the hive coordinate interruptions instead of competing for attention.
- **path:** relay-realtime → pendant → mac-planner → browser-extension → dashboard
- **model tier:** Use deterministic queueing, expiry, authorization-scope checks and deduplication; use a cheap model only to compress each item's context into one spoken sentence. Realtime handles the short question and signed reply.
- **latency:** New urgent decisions appear within 2 seconds; answering one should acknowledge locally in under 300 ms and reconcile the owning job within 5 seconds.
- **cost:** Low: compact decision records and one short summary per item. No page/audio payload should be copied to the relay unless needed to answer the owner's question.
- **security:** Every item names its source, target action, risk and expiry. A reply is bound to a job and a nonce, cannot approve a different action, and expires when the underlying page/state changes. Sensitive decisions are spoken only after the pendant's active conversation is established; the dashboard provides the full evidence.
- **missing:** A cross-surface decision inbox with stable item IDs, priority, expiry and deduplication; Signed pendant replies bound to a job/action hash, with replay protection; Mac and browser adapters that publish blocked decisions and consume an answer without losing session context; A relay arbiter that prevents two agents from asking the same question and marks stale choices invalid; A compact audio/LED fallback for queued, expired and answered decisions


## Changes it proposed to its own stack

### `firmware` — Replace the prototype's split-rate audio contract with an explicit 24 kHz superwideband session: capture at a declared rate, resample once at a known boundary, packetize with turn ID/sequence/timestamp, and expose measured encode/decode budget. The nRF9160 and ESP32 bench firmware must reject mismatched sample-rate headers rather than silently feeding 15,625 Hz capture into a 24 kHz playback assumption.
- **owner gets:** The owner gets speech that is consistently intelligible instead of a path that can sound slow, pitch-shifted, or intermittently underrun while every component reports success. It makes the phrase '24 kHz audio' truthful and gives a reproducible answer when it is not.
- effort: Medium-high: define a versioned frame header, implement fixed-point resampling and ring-buffer accounting on the nRF9160, update ESP32 bridge framing, and run dual-UART bench captures against known audio. One I2S full-duplex peripheral and roughly 87% one-core Opus load leave little headroom, so profiling is required.  ·  risk: CPU starvation or buffer growth could make current conversations worse. Roll back by accepting the existing v1 frame header and selecting the old codec profile when the peer does not advertise v2; keep a compile-time feature flag until 30-minute soak tests pass.
- cost: No per-call model cost. Engineering only; a USB bench run uses negligible power, while a production 24 kHz path may increase CPU and radio airtime modestly.  ·  latency: Target unchanged 60 ms packets and under 150 ms mouth-to-ear; resampling must add less than 5 ms. Current decode is already about 25.4 ms per 60 ms packet, so add no heavyweight DSP.
- security: Frame headers and test telemetry contain turn IDs and timing, not speech content. Authenticate the session and avoid persisting PCM; retain aggregate counters only.
- depends on: The audio-test capability must have a versioned metric schema; A known-good 24 kHz frame fixture and ESP32 capture harness; A transport decision for the currently USB-connected bench versus future LTE-M; USB remains bench-only


## What it asked for

_Nothing._
## Its own summary

This round produced three non-duplicate pieces: (1) an owner-facing end-to-end audio qualification that measures the real 24 kHz path across pendant, relay, Mac and ESP32; (2) a firmware change making the sample-rate/frame contract truthful instead of silently mixing 15,625 Hz capture with 24 kHz playback; and (3) failure recovery that preserves shell exit evidence, joins jobs to ledgers, and lets the owner resume only safe failed steps. I also tested the newly granted USB diagnostic schema: it remains unresolved, so I recorded that the connected chips cannot yet be inspected from this agent.

**Biggest unknown:** Whether the current firmware and relay actually negotiate a valid 24 kHz frame end to end. I still need a real bounded serial reader/bench harness implementation (or captured UART logs), a versioned audio frame contract, and authoritative route implementations for the pipeline audio/event endpoints. I do not need another proposal for a serial schema; the missing part is the implementation.

