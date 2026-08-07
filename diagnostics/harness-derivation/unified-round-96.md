# Harness derivation — unified — round 96

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If the pendant loses signal while I’m speaking, keep the request, tell me what was received, and resume the conversation when it reconnects—without running anything twice."
- **useful because:** LTE-M is currently half-duplex and measured to drop roughly 7.8 seconds of uplink when the agent speaks. Today the owner can neither know whether a request was complete nor safely retry it. A cross-device turn ledger would turn a frustrating silent failure into an explicit, recoverable conversation.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Realtime for the live acknowledgment and short repair prompt; background/cheaper model for reassembly, transcription comparison, and receipt generation.
- **latency:** Pendant must emit a local 'captured N seconds / upload incomplete' cue within 300 ms; relay acknowledgment within one LTE round trip (target 1–3 s). Reassembly and duplicate-check may complete in the background. No action executes until the turn is complete and classified once.
- **cost:** Usually one extra short realtime turn (about $0.01–$0.05 depending on audio); background reconciliation uses a cheaper model and is dominated by storage/transcription, not generation.
- **security:** Raw fallback audio may contain private speech and must stay encrypted on SD/R2 with a short TTL. The relay must use a turn UUID plus chunk hashes and an idempotency key; browser/Mac actions remain staged until the owner confirms any irreversible step. Dashboard should show exactly what audio/transcript was retained and offer delete.
- **missing:** A pendant-side turn journal with encrypted chunk files, monotonic sequence numbers, and a local spoken/LED acknowledgment mode; Relay protocol for resumable chunk upload, hash-based deduplication, completion receipts, and explicit incomplete/complete turn states; A cheap reconciliation worker that compares partial and final transcripts and prevents a recovered turn from being planned twice; Mac/browser adapters that consume one canonical recovered turn and preserve action idempotency across reconnects; Dashboard and pendant UI for 'received', 'awaiting reconnect', 'recovered', and 'discarded' states

### "When I ask “what happened?”, give me one synchronized, spoken timeline of what the pendant heard, what the relay decided, what the Mac or browser actually changed, and any audio or evidence used—without making me hunt through logs."
- **useful because:** Today those facts are split across pipeline events, Mac jobs, browser commands, and audio objects with different identifiers and timestamps. The owner cannot independently reconstruct whether a spoken request was misunderstood, merely planned, or actually changed something. A human-readable causal replay would make the hive trustworthy and debuggable in daily use.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use a cheap background model to compress already-recorded structured events; use Realtime only to answer the owner's short spoken question and read the resulting timeline. Do not resend raw history to the expensive turn unless the owner asks for detail.
- **latency:** Return a concise spoken timeline in under 2 seconds from indexed records; dashboard can progressively load raw evidence afterward.
- **cost:** Near-zero incremental inference for normal cases: structured event joining plus a short cheap summarization, with realtime cost only for the spoken response (roughly $0.005–$0.03). Storage/indexing dominates.
- **security:** Evidence may include private page text, email, screenshots, or audio. Apply per-event sensitivity labels, redact secrets by default, keep raw artifacts local or short-lived, and require explicit confirmation before revealing sensitive snippets aloud in public settings. Never allow the replay query to trigger a re-run.
- **missing:** A durable causal correlation ID spanning pendant turn, relay job, pipeline, Mac job, browser command, and generated audio; An append-only event index with monotonic timestamps and explicit planned/attempted/completed/blocked states; A provenance joiner that links each claimed change to before/after evidence and receipt hashes; A sensitivity-aware spoken summarizer and dashboard timeline with raw-evidence expansion; A pendant query response that can identify the last turn without relying on the owner's exact wording

### "If I take the pendant off or it runs out of battery, move the live conversation to my phone or Mac automatically, then move it back when the pendant returns—without restarting or losing the current turn."
- **useful because:** The pendant is the owner's always-there interface, but it is not always powered or in radio range. Today a disconnect ends the interaction and forces the owner to repeat context. A stateful live migration would make the assistant continuous rather than tied to one piece of hardware.
- **path:** pendant → relay → iOS → mac-bridge → browser → dashboard
- **model tier:** Realtime handles only the active handoff cue and conversation; a cheaper background service maintains replicated session state and selects the healthiest audio surface.
- **latency:** Detect loss and announce a fallback within 1 second; resume audio on phone/Mac within 3 seconds. Returning to the pendant may take one LTE/BLE setup round trip.
- **cost:** Usually no additional model call beyond a short handoff utterance; infrastructure cost is session replication and audio relay. A background summarizer is used only if state must be compacted.
- **security:** Pairing and handoff must be authenticated to the owner's devices; never fall back to an unpaired nearby phone. Mute the old surface before enabling the new one, expire replicated audio quickly, and show the active microphone/output device prominently. Destructive actions keep their existing confirmation state and must not be re-approved ambiguously.
- **missing:** A replicated session state machine with one active audio-owner lease and fencing tokens; A phone companion that can receive/send the same live audio and spoken handoff state; Pendant presence/battery/link-loss signals and a resumable audio cursor; Relay-side duplicate suppression so a handoff cannot produce two replies or two actions; Dashboard controls to choose automatic versus manual handoff and to revoke a device


## Changes it proposed to its own stack

### `hardware` — Replace the prototype HUZZAH32 ESP32-classic bridge with an ESP32-WROVER-class Bluetooth Classic module (external PSRAM, at least 4 MB) and add a small I2C fuel-gauge IC plus brownout-safe flash/PSRAM power decoupling. Keep the nRF9160↔bridge I2S contract, but move the resampler, a bounded 100–250 ms jitter buffer, and A2DP queues out of scarce internal DRAM; expose battery percentage and brownout events upstream.
- **owner gets:** Spoken replies would stop going silent when Bluetooth scheduling and the current 44 kB buffer collide, and the pendant could warn before a call dies instead of abruptly disappearing. The owner gets dependable headphones and an honest battery warning, especially during the 24 kHz full-duplex path.
- effort: Moderate hardware respin and enclosure/antenna validation; then bridge firmware changes for PSRAM-safe buffers, watchdog recovery, and fuel-gauge telemetry. Keep the existing prototype bridge as a fallback during bring-up.  ·  risk: PSRAM timing, RF layout, and A2DP stack behavior need validation; an over-large jitter buffer can add perceptible latency. Recover with a compile-time buffer profile and a hardware bypass/test fixture. Battery telemetry must fail safe to 'unknown', never fabricate charge.
- cost: Roughly +$8–$20 BOM versus the dev board (module, gauge, PCB and passives); bridge power rises modestly during buffering, likely tens of mA peak, while the gauge is sub-mA. No per-call API cost.  ·  latency: Adds 100–250 ms only when the link is jittery; steady-state target remains under 150 ms bridge delay. PSRAM buffering should reduce underruns rather than increase normal latency.
- security: No new cloud data path. Battery and brownout state are low sensitivity; PSRAM must be cleared on disconnect if it can contain decoded speech, and debug UART dumps must not include audio.
- depends on: A firmware PSRAM allocator and bounded jitter-buffer implementation; A 24 kHz audio-path acceptance test across nRF9160, I2S, bridge, and headphones; A production PCB/antenna design; current HUZZAH32 remains the prototype reference

### `model-routing` — Make capability routing permission-aware at plan time: normalize /ops/status into a typed surface matrix (AppleScript app automation, browser bridge, shell, Accessibility, Screen Recording), mark Accessibility/vision actions unavailable when TCC is false, and force a deterministic fallback or an honest blocked receipt before mac-vision is invoked. Also fix the contradictory ready/requiredMissing representation so planners cannot treat 'ready:false' as 'all required permissions satisfied'.
- **owner gets:** The Mac is online and most app/browser automation is granted, but GUI automation is not. Today a request can waste time entering a vision loop that cannot control or inspect the screen, then leave an opaque failure. The owner instead gets a fast result using AppleScript/browser routes—or a clear instruction that only a manual TCC grant can unblock it.
- effort: Small-to-moderate relay/local-agent routing change: schema, preflight, planner prompt projection, and regression tests for each permission combination. No Accessibility grant is needed to implement it.  ·  risk: Overly conservative mapping could reject an action that AppleScript can perform. Recover with per-action capability declarations and a dry-run preflight receipt; never infer permission from cached grant text alone.
- cost: Negligible API cost; avoids expensive realtime/vision attempts and unnecessary screenshots.  ·  latency: Adds one local status lookup (target <100 ms), usually reducing total latency by avoiding doomed loops.
- security: Improves least privilege: no screenshot or GUI event is attempted without the matching TCC grant. Permission state itself is local metadata and should not be sent beyond the relay unless needed for a receipt.
- depends on: Live /ops/status and /routing capability snapshots; Typed action-to-permission requirements in mac_run_actions, mac_delegate, and mac-vision; A blocked-action receipt exposed through /jobs/:jobId/receipts or /journal/:jobId


## What it asked for

_Nothing._
## Its own summary

Discovered the live system is now producing 24 kHz mono PCM successfully, but the end-to-end path still has two concrete gaps: LTE-M contention can lose ~7.8 seconds of uplink while the agent speaks, and the ESP32 bridge has a fragile 44 kB buffer that can starve Bluetooth into silence. I recorded three new items: resumable, idempotent turn recovery across pendant/relay/Mac/browser; a PSRAM-equipped Bluetooth bridge with fuel gauge and jitter buffering; and permission-aware routing that avoids impossible mac-vision loops when Accessibility/Screen Recording remain unavailable.

**Biggest unknown:** The remaining acceptance thresholds for the 24 kHz path—maximum tolerable round-trip latency, packet-loss concealment target, reconnect timeout, and exact owner-visible recovery behavior—are still unspecified. I also still need an end-to-end fault-injection test proving that a recovered turn cannot execute twice.

