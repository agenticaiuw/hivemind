# Harness derivation — faculty-judgement — round 187

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“After I react to a briefing, learn whether I wanted more, less, or no interruption next time—without silently changing my rules.”"
- **useful because:** The system currently ranks and speaks items, but has no closed loop from the owner's real reaction to future decisions. A one-tap/one-sentence reaction on the pendant could turn annoying interruptions into a visibly improving assistant while keeping policy changes reviewable.
- **path:** pendant → relay → mac-planner → dashboard
- **model tier:** Realtime only for interpreting the owner's short reaction; background model summarizes weekly patterns. Deterministic policy engine makes the actual decision.
- **latency:** Reaction acknowledgement under 300 ms locally; persisted event under 2 s when tethered; weekly summary can take minutes.
- **cost:** About $0.001–$0.01 per reaction depending on whether transcription is needed; most reactions are typed enums and cost nothing.
- **security:** A reaction is a preference, not permission to act. Store only enum, item ID, and policy field changed; never store spoken briefing content by default. Any proposed policy change is PREPARE/ASK, never silently applied.
- **missing:** A durable owner-feedback event writer linked to briefing item and policy version; A dashboard review showing proposed policy adjustments and their evidence; A firmware gesture or spoken command that produces compact reactions such as more_less_stop_later

### "“I got interrupted halfway through that briefing—tell me exactly what I heard, skip what I heard, and give me the shortest useful remainder.”"
- **useful because:** A generated brief is not the same as a delivered brief. With playback/download ACKs and an audio cursor, the system can avoid repeating content, recover after a dropped link, and distinguish ‘generated’ from ‘actually heard’—a daily trust problem no Mac-only assistant can solve.
- **path:** pendant → relay → mac-planner → dashboard
- **model tier:** Deterministic cursor and ACK reconciliation first; a cheap background model compresses only the unheard items. Realtime model is used only if the owner asks a follow-up.
- **latency:** On reconnect, reconcile delivery state in under 2 s; spoken recovery prompt under 1 s after button press; compression under 10 s for a long brief.
- **cost:** Near-zero for cursor reconciliation; roughly $0.002–$0.02 when an LLM must compress the remainder.
- **security:** Use opaque artifact/item IDs and source references, not raw audio in the pendant control channel. Never claim playback_finished without an authenticated device ACK. Expired or checksum-failed audio is treated as unheard, and any sensitive remainder follows the eventual spoken-content policy.
- **missing:** A server-side reducer that joins generated items, audio artifacts, cursor tokens, and record_pendant_delivery_event events; A durable item manifest with stable ordering and idempotent replay across reconnects; A short physical command mapped to s19-75il spoken_status_interrupt without adding a new gesture

### "“When I plug the pendant into my Mac, give me a safe arrival mode: reconcile anything I missed while mobile, offer one compact spoken queue, and stop cleanly when I unplug.”"
- **useful because:** The hardware is physically tethered and testable now even though LTE registration is absent. A USB-presence mode would make the pendant useful today, bridge offline work honestly, and prevent stale queued audio or actions from arriving after the owner has left the desk.
- **path:** pendant → mac-planner → mac-terminal → relay → dashboard
- **model tier:** Deterministic USB/session state machine and queue reconciliation; cheap background summarizer for backlog; realtime model only for the owner's spoken request.
- **latency:** Detect attach/detach in under 1 s; announce a compact status within 3 s; never block unplug handling on model inference.
- **cost:** Negligible API cost for state and receipts; $0.001–$0.02 only when backlog compression is requested.
- **security:** USB presence is not consent to execute external actions. Arrival mode may read and stage, but mutations remain behind autonomy_policy_evaluate and physical_transaction_approval_latch. On detach, cancel only owner-owned in-flight playback/staging and keep no raw audio beyond existing failure-path rules.
- **missing:** A signed USB attach/detach session adapter for /dev/cu.usbmodem00096003658* and the ESP32 bridge; A relay-visible session lease and idempotent detach cancellation; A compact catch-up projection that includes pendant items and delivery state, not merely Mac jobs; A dashboard control for enabling arrival mode and choosing its spoken backlog limit

### "“For any request, show me one short timeline: what I asked, what the relay planned, what the Mac/browser did, and what the pendant actually delivered.”"
- **useful because:** Today the owner can receive separate job, action, browser, pipeline, and playback records with unrelated IDs. A single causal timeline would make failures and partial success legible instead of forcing the owner to trust a fluent sentence that may only describe server acceptance.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic receipt join and state machine; no expensive model for the timeline. Use realtime only to answer a spoken follow-up such as ‘what failed?’
- **latency:** Dashboard timeline under 1 s for existing records; spoken summary under 2 s; late delivery ACKs update asynchronously.
- **cost:** No model cost for normal views; at most $0.001 for a natural-language spoken explanation.
- **security:** Expose least-privilege summaries and redact secrets; do not infer success from a missing event. Preserve immutable receipts and mark contradictory or late events explicitly. External side effects still require existing policy and physical approval.
- **missing:** A durable relay-job ↔ Mac-job ↔ browser-command ↔ pipeline-artifact correlation record; A typed state reducer distinguishing planned, accepted, executed, undone, downloaded, played, and unknown; A read route that returns the joined timeline with provenance and sensitivity-aware summaries

### "“Keep the pendant useful all day: when battery, link quality, or codec load gets tight, quietly switch to the best speech mode that preserves intelligibility, and tell me only if my experience will materially change.”"
- **useful because:** The owner should not have to choose between the verified 24 kHz experience and an unexpectedly dead pendant. The system can trade fidelity, frame cadence, briefing length, and retry behavior against actual battery/link/CPU conditions while preserving the owner's ability to override. This is a felt benefit—longer reliable conversations—not another status dashboard.
- **path:** pendant → relay → mac-planner → dashboard
- **model tier:** Deterministic controller using measured battery, packet loss, queue depth, and codec counters; no realtime model except to explain a mode change in one sentence. A background model may learn per-owner tolerance from explicit overrides, never silently.
- **latency:** Controller reacts within one audio frame or one telemetry interval; no model on the audio critical path. Explanation under 1 second when requested.
- **cost:** Negligible API cost; modest firmware/relay engineering. Optional background learning costs less than $0.01 per day.
- **security:** The controller must not silently reduce intelligibility or alter microphone retention. Every transition carries old/new profile, measurements, and reason; owner overrides are durable preferences. No raw audio or location leaves the device.
- **missing:** Authenticated low-rate telemetry for battery, radio quality, decoder utilization, underruns, and queue depth; A signed profile table with hard quality floors and hysteresis so it cannot oscillate; An atomic audio-boundary profile switch and rollback path across nRF9160, ESP32 sink, relay, and Mac; A user-visible override and explanation surface tied to the existing autonomy policy

### "“Before I rely on the pendant for the day, tell me whether it can actually hear me, speak to me, and deliver a reply—not merely whether the Mac process is running.”"
- **useful because:** A green server health check does not prove microphone capture, codec headroom, bridge playback, or end-to-end delivery. A compact active self-test would catch the failure before the owner is walking or in a moment where help matters.
- **path:** pendant → relay → mac-planner → dashboard
- **model tier:** Deterministic hardware test and signed measurements; no model required. Realtime speech is used only for the owner's optional spoken confirmation.
- **latency:** Cold self-test under 10 seconds; passive health badge updates continuously without interrupting conversation.
- **cost:** No model cost. A few seconds of USB/audio activity per requested test.
- **security:** The test must use synthetic tones and a nonce phrase, never retain microphone recordings, and never send a diagnostic phrase to third-party services. It must clearly label stale or simulated results and avoid claiming LTE capability while the pendant is USB-only.
- **missing:** A signed end-to-end health challenge spanning nRF9160 mic, Opus encode/decode, ESP32 I2S sink, relay, and ACK; A passive health state reducer with expiry and explicit unknown state; A pendant-safe test trigger and a dashboard card that explains the failing segment

### "“Run my scheduled routines only after a harmless rehearsal proves the surfaces they depend on are alive; if not, leave me a useful draft and explain exactly what was unavailable.”"
- **useful because:** A routine can report completed while calendar access is unreadable, browser connectivity is stale, or audio never reached the pendant. Preflight currently answers capability questions when asked, but the owner needs scheduled work to fail honestly and degrade into a reviewable artifact instead of silently disappearing.
- **path:** relay → mac-planner → browser-extension → pendant → dashboard
- **model tier:** Deterministic preflight, policy, and fallback; cheap background model only to compress the draft. No realtime model on the scheduled path.
- **latency:** Preflight adds at most 2 seconds to a routine; fallback draft is available within the routine's normal completion window.
- **cost:** Near-zero model cost for checks; $0.001–$0.01 only for a generated fallback summary.
- **security:** Rehearsal is read-only and must not send, buy, delete, or mutate. Calendar/reminder empty results must be treated as unreadable unless permission evidence corroborates them. Drafts retain provenance and require owner confirmation before external effects.
- **missing:** A routine wrapper that invokes preflight and blocks false completion; Typed fallback targets for draft/note/queued audio with idempotency; Receipt fields for preflight evidence, degraded outcome, and owner-visible reason; A scheduler policy value the owner can override per routine


## What it asked for

_Nothing._
## Its own summary

Recorded four owner-facing capabilities: reaction-driven briefing calibration; truthful unheard-remainder recovery; USB-tethered arrival/departure mode; and a unified causal timeline across relay/Mac/browser/pendant. The second and fourth are mostly connective work over newly granted delivery/provenance primitives, not claims that those primitives are absent.

**Biggest unknown:** The USB attach/detach session contract and the durable cross-surface correlation/reducer are still unobserved. I also still lack owner-stated interruption/disclosure preferences; I will not invent them or re-request the declined preference grants.

