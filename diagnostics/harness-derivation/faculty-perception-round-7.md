# Harness derivation — faculty-perception — round 7

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-agent** — The live Mac local agent is reachable and healthy at version 0.5.0; it advertises /capabilities. GET /health returned HTTP 200 with ok:true.
  - evidence: GET /health -> {"ok":true,"service":"AI Pendant Mac Local Agent","version":"0.5.0","capabilities":"/capabilities"}
- **pendant-audio** — The pendant's current audio path is asymmetric: I2S capture is 15,625 Hz, Opus uplink is 16 kHz/16 kbps; playback decodes Opus at 24 kHz, resamples to 31,250 Hz I2S wire clock, and outputs via ESP32 bridge.
  - evidence: Live hardware/audio specification for pendant audio.
- **pendant-compute** — The nRF9160 application has 211,608 B RAM, Cortex-M33 64 MHz with DSP extension; simultaneous Opus encode/decode uses roughly 87% of one core (encode ~15 ms, decode ~25.4 ms per 60 ms packet).
  - evidence: Live pendant hardware and audio specifications.

## Capabilities it proposed

### "“What actually happened with that?”"
- **useful because:** After a long or asynchronous request, the owner gets a trustworthy spoken completion receipt rather than a model claiming success. It reconciles what the Mac attempted, what the browser actually changed, what the relay persisted, and whether the pendant delivered the result; failures and unknowns are explicit, with links/evidence on the Mac.
- **path:** pendant: owner asks the follow-up and receives one short spoken summary → relay-realtime: correlates the conversation/request ID and delivers the concise receipt → mac-planner: owns the canonical receipt and reconciles job state, action receipts, and timestamps → browser-extension: contributes URL/tab, extracted evidence, and before/after mutation records for private pages → mac-vision: contributes GUI action outcomes and screenshots/accessibility evidence when used → dashboard: exposes the evidence timeline and lets the owner inspect or retry failed legs
- **model tier:** background for receipt assembly and reconciliation (gpt-5.6-luna); realtime only for the follow-up wording and low-latency clarification
- **latency:** For a completed job, speak within 1 second from cached state; if reconciliation is still running, say that immediately and update within 10 seconds. Most time is waiting for late browser/pendant acknowledgements, not model inference.
- **cost:** Roughly $0.005–$0.03 per receipt, dominated by the background reconciliation context; follow-up speech uses a few realtime tokens.
- **security:** Receipts may contain private URLs, mail subjects, screenshots, or account data; keep evidence on the Mac and send only a minimized summary to the relay/pendant. Never infer that an irreversible action occurred from an intent or queued command. Require confirmation before retrying a send, purchase, deletion, or other irreversible step.
- **missing:** A shared request/job correlation ID across relay, Mac planner, browser bridge, and pendant playback acknowledgement; A typed receipt schema with attempted/observed/confirmed/unknown states, timestamps, provenance, and irreversible-action markers; Pendant-side delivery acknowledgement (played, skipped, or not received) exposed to the relay; A durable cross-surface receipt store and dashboard timeline

### "“Move this to my Mac and keep going from exactly here.”"
- **useful because:** Today a voice conversation, a private browser session, and a Mac job can each know different pieces of the same task. The owner should be able to hand off mid-task without repeating the goal, losing the logged-in tab, or accidentally restarting an irreversible step. The Mac should open the exact continuation point, while the pendant remains the interruption and completion channel.
- **path:** pendant: captures the explicit handoff request and confirms the destination → relay-realtime: freezes the live turn into a signed continuation capsule and resumes spoken updates → mac-planner: reconstructs the task state, asks the browser/vision facets to continue, and owns the handoff ledger → browser-extension: preserves the private tab/session and returns the current URL, selected text, and pending form state → mac-vision: restores the visible UI at the checkpoint without stealing focus unexpectedly → dashboard: shows the continuation capsule, evidence, and any confirmation gate
- **model tier:** gpt-5.6-luna background for capsule construction and task continuation; realtime only for the short spoken confirmation and updates
- **latency:** Acknowledge the handoff in under 1 second; restore the Mac continuation workspace in under 5 seconds. The owner should not wait on model work before the handoff is accepted.
- **cost:** About $0.01–$0.05 per handoff, mostly context serialization and one planner turn; browser and Mac execution dominate elapsed time rather than API tokens.
- **security:** The capsule can contain private page content, draft text, and session identifiers. Store it locally on the Mac, encrypt it at rest, send only a capability-scoped reference through the relay, expire it after completion, and require confirmation at the same irreversible boundary that existed before handoff. Never copy cookies or secrets into the capsule.
- **missing:** A signed, versioned continuation-capsule protocol shared by relay and Mac; Atomic checkpointing of planner state, browser tab identity, evidence, and confirmation gates; A browser-extension restore-at-checkpoint operation that does not expose cookies; A Mac workspace view for pending handoffs and explicit ownership transfer


## Changes it proposed to its own stack

### `firmware` — Add a local audio health governor around the current Opus pipeline: measure encode/decode wall time, I2S FIFO watermarks, packet loss, and modem transmit pressure; select among 24-kHz playback, reduced-complexity 24-kHz, and a clearly reported fallback mode before an underrun occurs. Emit a compact health epoch with each conversation so the relay and Mac receipt can distinguish clean 24-kHz audio from degraded playback.
- **owner gets:** The pendant should remain intelligible instead of stuttering or silently dropping audio when LTE bursts and simultaneous encode/decode consume the available CPU. The owner and support tools can tell whether a conversation really used the requested wideband path.
- effort: Medium: firmware instrumentation and state machine, relay schema plumbing, and bench tests across sustained LTE transmit and SD-card activity.  ·  risk: A bad governor could switch modes too aggressively or add latency. Use hysteresis, conservative thresholds, and a manual diagnostic mode; if telemetry is malformed, retain the existing fixed mode rather than blocking conversation.
- cost: Negligible API cost; a few bytes per health epoch. No hardware cost; modest flash/RAM for counters and thresholds (target under 4 kB RAM).  ·  latency: Reduces worst-case perceived latency by preventing underruns; mode changes should occur only at frame boundaries, adding under 60 ms.
- security: Telemetry contains performance data only, not audio content. Keep detailed traces local and send aggregate counters unless the owner explicitly requests diagnostics.
- depends on: A verified 24-kHz implementation and runtime observability path; Relay support for audio health epochs; A hardware test fixture capable of sustained LTE-M plus audio playback

### `integration` — Create a cross-surface continuation capsule protocol. At an explicit handoff, the relay signs a short-lived capsule containing task ID, last confirmed semantic turn, pending/blocked action, browser session alias (never cookies), evidence hashes, confirmation requirements, and expiry. The Mac atomically consumes it into a local workspace; the browser extension and vision loop acknowledge restoration; subsequent events append by capsule version so stale handoffs cannot resume or overwrite newer work.
- **owner gets:** They can move from pendant to Mac without repeating themselves or wondering which draft, tab, or step is current. If the handoff is interrupted or duplicated, the system resumes at the last known safe checkpoint instead of silently doing the same thing twice.
- effort: Medium-high: protocol/schema design, local encrypted persistence, relay signing, browser restore acknowledgement, and failure-injection tests for duplicate and stale capsules.  ·  risk: A race could produce two active continuations or restore the wrong tab. Enforce one owner lease per task, monotonic versions, short expiry, and a visible conflict state that stops before any irreversible action.
- cost: Negligible storage and API cost; one small signed record per handoff. No new hardware.  ·  latency: Sub-second acknowledgement; roughly 2–5 seconds to restore the Mac workspace, with no need to replay the full conversation context.
- security: Improves containment by passing opaque session aliases instead of credentials, but the capsule still carries private task data; encrypt locally, minimize relay payloads, audit reads, and expire aggressively.
- depends on: A shared task/request identity across relay, Mac, browser, and vision; Local encrypted continuation storage; Browser and Mac acknowledgement events


## What it asked for

_Nothing._
## Its own summary

Established three current truths: the Mac agent is healthy at v0.5.0; the pendant audio path remains asymmetric (15,625-Hz capture/16-kHz uplink versus 24-kHz decode playback); and simultaneous Opus work is about 87% of one Cortex-M33 core. I recorded those facts, proposed a cross-surface 'what actually happened?' completion receipt with evidence-backed confirmed/unknown states, and proposed a local audio health governor to prevent wideband underruns and report degradation honestly.

**Biggest unknown:** I still lack live pendant/firmware diagnostics and the current 24-kHz implementation status, so I cannot establish whether the requested 24-kHz superwideband path is actually working end to end. The pending bearer-authenticated Mac diagnostic access (ops/status, machine-context, pipeline, capabilities) and the requested pendant diagnostics tool would also materially improve confidence.

