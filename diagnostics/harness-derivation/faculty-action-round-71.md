# Harness derivation — faculty-action — round 71

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I tell the pendant to do something on my Mac, give me a physical completion signal, speak the exact result, and let me press once to undo the last reversible action."
- **useful because:** The owner can issue an action without looking at a screen, know whether it actually completed, and recover immediately from a mistaken reversible action. This closes the gap between judgement deciding and the action being observable in the real world.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use realtime only to parse the short command and speak the result; use the cheaper local planner/worker for execution, receipt reconciliation, and undo eligibility.
- **latency:** Acknowledge on the pendant within 300 ms; completion beacon within 2 s for short actions; long jobs announce queued/running/done without holding the voice session open.
- **cost:** Negligible model cost for short commands; approximately one planner/action call per request. Storage is a few hundred bytes per receipt and undo token.
- **security:** Only reversible, explicitly classified actions may be one-press undo; never undo sends, purchases, deletes, or external side effects. The spoken result may reveal private data to nearby people, so support a terse mode and require confirmation for sensitive receipts.
- **missing:** Pendant firmware event channel for queued/completed/error/undo states; A durable undo lease bound to the exact action receipt and expiry; Mac-side proof that the inverse operation actually ran; Relay route to push completion events to the pendant

### "When I say “I’m leaving,” check the unfinished work across my Mac, browser, and relay, tell me what is still exposed or running, and—only for the safe items I approve—close or hand them off so I can walk away with a spoken all-clear."
- **useful because:** Today the owner cannot get a trustworthy, cross-device departure state: the Mac may have unsaved work, authenticated tabs may remain exposed, and relay jobs may continue without a clear handoff. This gives them a single wearable-originated leave-state with evidence and bounded remediation, rather than making them inspect every surface.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime model only interprets the short departure command and speaks the result. A cheaper background planner performs inventory, evidence reconciliation, and safe handoff; the Mac/browser executors perform only explicitly approved reversible steps.
- **latency:** Initial spoken inventory in 3 seconds; deeper cross-surface scan may continue for up to 30 seconds and return a completion event to the pendant.
- **cost:** One short realtime turn plus one background planning pass per departure check; storage is a small signed state snapshot and action receipt. No continuous model polling when the owner is not asking.
- **security:** The scan necessarily sees private tab titles, active applications, and job metadata; retain only redacted findings with short TTL. Never auto-close, log out, send, delete, or kill a job. Require explicit approval per category, and show exactly which tabs/jobs would be affected before execution.
- **missing:** A cross-surface departure-state schema with freshness and evidence provenance; Mac APIs for unsaved-document and active-session inventory without relying on Accessibility; Browser session exposure/lock metadata and a safe handoff operation; Relay job lease/handoff semantics so queued work cannot be abandoned or duplicated; Pendant offline acknowledgement and a durable completion event when the Mac link drops


## Changes it proposed to its own stack

### `integration` — Build an end-to-end 24 kHz audio conformance and recovery harness: firmware emits deterministic mic/speaker loopback vectors and sequence counters; relay validates Opus packet cadence, resampling, CRC/order, and jitter-buffer behavior; Mac harness runs long-duration fixtures and records MOS-adjacent underrun/latency metrics; failures become timestamped receipts and a UART-readable diagnostic bundle. Add negotiated fallback profiles (24 kHz primary, 16 kHz compatibility) rather than silently transcoding.
- **owner gets:** The owner gets voice that stays intelligible instead of randomly clipping, drifting, or going silent, and a concrete diagnosis when the prototype fails. It directly advances the stated 24 kHz audio-path goal.
- effort: Medium-high: firmware test mode and counters, Worker validation/metrics, Mac fixture runner, and dashboard report.  ·  risk: Test mode must be impossible to enter during ordinary wear; malformed packets or bad clock measurements could falsely trigger fallback. Recover by keeping the current path as a safe profile, gating diagnostics behind explicit maintenance mode, and retaining raw counters without raw audio.
- cost: Small ongoing storage/CPU for counters and reports; no per-turn model cost. One-time engineering for fixture generation and validation.  ·  latency: No added steady-state latency; negotiated fallback may add one handshake round at session start.
- security: Diagnostics should contain packet metadata and hashes, not microphone contents; raw audio fixtures remain local unless explicitly uploaded.
- depends on: 24 kHz acceptance criteria from owner; A firmware build/flash or simulator access grant; audio_path_probe capability


## What it asked for

_Nothing._
## Its own summary

Fresh discovery confirms the Mac bridge is online but home-Chrome/browser is offline with five pending commands. I recorded two new items: (1) an end-to-end 24 kHz audio conformance/recovery harness with deterministic vectors, packet/order/jitter metrics, and explicit 24→16 kHz negotiation; (2) wiring the existing execute/job-receipt/undo/event primitives into a wearable completion beacon and one-press undo for reversible actions. The latter is connective work, not a new backend primitive: it needs a pendant event channel, durable undo lease, inverse-operation proof, and relay push route. I also notified judgement and relay-realtime.

**Biggest unknown:** The concrete 24 kHz acceptance thresholds and authorized firmware/simulator build access are still unavailable; without them I cannot validate or implement the audio path. Browser-private actions remain blocked until the extension heartbeats. I still need the pendant event-push contract and proof/lease implementation before action completion can be safely observable and undoable.

