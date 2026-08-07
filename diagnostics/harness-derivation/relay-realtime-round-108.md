# Harness derivation — relay-realtime — round 108

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I double-press the pendant, enter a temporary privacy bubble: stop sending live audio to the relay, tell my Mac to lock or hide sensitive work, pause browser-session observation, and restore everything when I press once again; tell me locally that privacy mode is active."
- **useful because:** The owner can physically and immediately prevent an overheard conversation or shared room from reaching cloud services, while also reducing exposure on the Mac and authenticated browser. Today the nodes have no coordinated, wearer-controlled privacy state, so stopping one channel still leaves other surfaces active.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Realtime handles only the button event, state transition, and a short spoken/local acknowledgement. The Mac planner and browser extension execute deterministic privacy actions; no expensive model is needed for the state machine.
- **latency:** Pendant acknowledgement under 300 ms; relay-to-Mac/browser propagation under 2 seconds. Restoration should be idempotent and report any surface that did not confirm.
- **cost:** Negligible model cost; a few relay requests per transition. Engineering cost is primarily a durable privacy-state record, authenticated fan-out, and recovery handling.
- **security:** The privacy command must be accepted from the paired pendant without requiring speech or cloud transcription. Audio buffers not yet uploaded must be discarded, and the relay must stop accepting new audio immediately. Mac/browser actions should record receipts but never transmit document contents. On resume, require explicit physical input and surface partial restoration rather than silently claiming privacy is off.
- **missing:** Pendant firmware double-press/single-press event semantics with an offline-safe privacy latch; Relay-wide privacy-state endpoint and enforcement at audio ingress, logs, and outbound fan-out; Mac planner action group to lock/hide configured sensitive apps and acknowledge state; Browser-extension command to suspend observation/command polling and acknowledge state; Durable cross-surface state reconciliation and a visible dashboard history of privacy transitions

### "Keep one conversation alive as I move between places: start speaking through the pendant while away, then when I sit at my Mac say “continue here” and have the Mac take over the same live thread with its screen and browser context; when I leave, hand it back to the pendant without starting over."
- **useful because:** The owner currently has separate wearable and computer interactions. They cannot begin a thought hands-free outdoors and finish it at the desk with the relevant Mac/browser context, nor leave the desk without losing the thread. This makes the hive feel like one assistant instead of disconnected agents.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime performs turn-taking and a compact handoff summary. A cheaper background model can compress the prior transcript and selected receipts; Mac-vision/browser provide observed context rather than re-describing whole screens.
- **latency:** Detect an explicit “continue here” and acknowledge within 500 ms; transfer usable context within 3 seconds. Handoff must degrade to a short summary if the Mac or pendant link is unavailable.
- **cost:** One small summary call per handoff plus normal voice traffic; context compression reduces repeated transcript-token cost compared with replaying the entire conversation.
- **security:** Only the paired Mac may claim a session, with short-lived authenticated handoff tokens. Do not transfer browser page contents or microphone audio unless the owner explicitly invokes the handoff. Show the active endpoint and invalidate the old endpoint's input token after transfer; retain a receipt for recovery.
- **missing:** A first-class session-transfer protocol with endpoint ownership, leases, and replay-safe sequence numbers; Mac-side presence/claim signal and a local “continue here” command surface; Compact encrypted handoff summaries containing pending intent, constraints, and action receipts; Pendant and Mac audio UX that can switch endpoint without creating duplicate assistant replies; Conflict recovery when both endpoints speak or either link drops mid-transfer


## Changes it proposed to its own stack

### `model-routing` — Add a cross-node audio quality negotiation and fallback path for the owner's 24kHz voice. The relay should detect when the pendant uplink is degraded (packet loss, jitter, low SNR) and switch to a more robust recognition mode or a lower-bitrate codec, while instructing the Mac (when online) to take over recognition from a local mic if the pendant audio becomes unusable. Record the chosen path in job/session metadata so later status queries explain what happened.
- **owner gets:** They get fewer 'sorry, I missed that' moments. If the pendant audio link is flaky, the system gracefully falls back to a better path without the owner needing to repeat themselves or troubleshoot.
- effort: High: requires telemetry from pendant/bridge, codec/ASR mode support, and coordination between relay and Mac for takeover.  ·  risk: Switching paths mid-session could confuse transcripts or duplicate actions if both paths act. Mitigate with a single authoritative action path and explicit session state transitions.
- cost: Moderate: telemetry collection is cheap; running multiple ASR paths or fallback recognition can increase compute. Keep fallback conservative and limited.  ·  latency: Small overhead to monitor; improved overall responsiveness by avoiding repeated misunderstandings.
- security: Audio is sensitive; ensure telemetry is minimal and encrypted. Avoid storing raw audio unless necessary, and clearly separate recognition results from control actions.
- depends on: Pendant/bridge audio telemetry exposure; ASR mode/codec options in relay; Mac agent capability to accept 'take over recognition' instruction; Session metadata store visible to relay_job_status


## What it asked for

### `c15-etjf` (context) — audio_path_state_24khz
- why: mac-planner asked what audio/SWB work is already implemented or proposed for the 24kHz path. I need a consolidated view of what exists (routes, skills, telemetry) to avoid re-proposing it and to design a genuinely new cross-node fallback.
- would change: If there is already an audio telemetry feed or SWB mode, I will design around it and focus on missing coordination and session state. If not, I will propose the minimal new hooks needed on pendant/bridge and relay to support negotiation and takeover.

