# Harness derivation — unified — round 108

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Continue this on my Mac.”"
- **useful because:** The owner can start a thought hands-free on the pendant and then move it to the Mac without repeating context. The pendant contributes the live utterance and interruption state, the relay preserves ordering, and the Mac/browser contribute the workspace and authenticated context. Today these surfaces complete jobs, but they do not provide a user-visible, atomic conversation handoff.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use realtime only to recognize the short handoff intent and acknowledge it; use a cheaper background/local planner to assemble the transcript, relevant pipeline events, open Mac session, and browser tab context. Use the browser only for already-open authenticated tabs and never mutate during handoff.
- **latency:** Acknowledge on the pendant within 300 ms; make the Mac workspace available within 3 seconds when online. If the Mac or browser is unavailable, retain a pending handoff and say so rather than pretending it transferred.
- **cost:** About $0.001–$0.01 per handoff depending on transcript summarization; most cost is optional background summarization, not realtime. Storage is a small transcript/context manifest and a receipt.
- **security:** Handoff may include private audio, authenticated URLs, and page-derived text. Encrypt the manifest in transit and at rest, bind it to the owner's paired devices, show exactly which tabs/context were transferred, and require confirmation before any resulting send, purchase, deletion, or form submission. Do not copy secrets such as passwords or stored credentials.
- **missing:** A first-class conversation-handoff manifest containing transcript range, source device, timestamps, active task, pending approvals, and selected browser tab IDs; An atomic relay acknowledgement and Mac session attach operation with deduplication; A dashboard and spoken receipt showing what arrived and what did not; A policy for redacting sensitive browser fields before context crosses surfaces

### "“Remember how I do this, and offer to repeat it next Friday.”"
- **useful because:** The owner can teach the hive a repeated personal workflow once—possibly spanning a spoken pendant command, Mac files, and an authenticated browser tab—and later receive a proposed replay instead of rebuilding instructions. It learns the sequence without silently turning an accidental action into automation.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use realtime only for the spoken teach/approve exchange. A cheaper background model generalizes the action trace into a parameterized routine; deterministic Mac/browser executors perform replay, with no model deciding irreversible steps at execution time.
- **latency:** Teaching acknowledgement under 500 ms; routine draft within 10 seconds after the workflow ends. A later replay should show its preview within 2 seconds and wait for approval before any external mutation.
- **cost:** Roughly $0.01–$0.05 to summarize and parameterize a trace; later runs are mostly deterministic and low-cost. Storage is a compact action graph plus redacted examples.
- **security:** Traces can contain private URLs, files, account names, and typed secrets. Capture only allowlisted action metadata and redacted values, never passwords or raw keystrokes; bind routines to the originating browser session and Mac identity. Every replay must show a diff and require confirmation for sending, buying, deleting, or submitting.
- **missing:** A trace recorder that correlates pendant intent, Mac job actions, browser command IDs, and receipts into one workflow; A routine compiler that identifies stable steps versus parameters and emits a human-readable preview; A routine version/approval store with expiration and automatic invalidation when a tab, selector, permission, or precondition changes; A dashboard edit/disable/test surface and a spoken “not now” response


## Changes it proposed to its own stack

### `browser-harness` — Add an offline-command quarantine and recovery protocol on top of the browser queue: every queued command gets an expiry, retry budget, and dependency snapshot; when the extension is offline, the relay stops blind retries, marks commands stale, and sends one compact status event to the pendant. On reconnection, only idempotent reads are replayed automatically; mutations require a fresh approval and a before/after revalidation. Preserve the original request ID and produce a receipt explaining expired, replayed, or withheld work.
- **owner gets:** The browser is currently offline with 10 pending commands, so the owner can otherwise receive late, duplicate, or contextually wrong actions. They get a trustworthy spoken explanation and safe recovery instead of wondering whether a private-site task happened.
- effort: Medium: queue schema and worker policy, relay event, browser heartbeat/reconnect handling, and a small dashboard/receipt view; no Accessibility grant required.  ·  risk: A command may expire while the owner expected it to wait, or a read may be replayed against changed content. Conservative defaults (reads only, short TTL, revalidation, no mutation replay) recover by leaving it explicitly withheld rather than acting.
- cost: Negligible API cost; a few D1 fields and one event per stale batch. Engineering cost is mostly tests for disconnect/reconnect and idempotency.  ·  latency: No impact while online. Reconnection adds one heartbeat and read revalidation round trip before replay.
- security: Improves safety for authenticated pages by preventing stale mutations and retaining session/tab affinity; receipts must avoid storing page secrets and expose only hashes/snippets.
- depends on: Existing browser command queue with request IDs/idempotency/tab affinity (chg-14accc01); GET /browser/status and POST /browser/heartbeat; POST /browser/result/:commandId and the durable job/receipt routes; A relay-to-pendant status event path

### `model-routing` — Introduce a per-turn speech budget contract shared by relay, Mac bridge, and pendant. Before generating a spoken response, the planner receives current LTE contention, queued audio bytes, pendant decode/CPU headroom, and whether the utterance is interactive or scheduled. It chooses one of three explicit outputs: live 24 kHz audio, compressed/short audio, or text-plus-local notification. The selected mode and byte budget travel in the pipeline manifest; the relay rejects oversized payloads before transmission and the pendant reports actual decode/playback completion for the next turn.
- **owner gets:** The current prototype can render 24 kHz speech successfully, but simultaneous 16 kbps uplink and 24 kbps downlink recently dropped about 7.8 seconds of speech. The owner gets fewer clipped replies and a deliberate short answer instead of silence or a stalled pendant when the link is busy.
- effort: Medium-high: define a versioned manifest, expose link/decoder telemetry, add routing policy and relay enforcement, and test scheduled versus interactive traffic.  ·  risk: A conservative budget may shorten a reply unnecessarily; a bad telemetry reading could choose text when audio would work. Recovery is to fall back to the existing durable audio path and retain the text transcript. Never silently discard an answer.
- cost: Lower average realtime and bandwidth cost because routine or congested turns become shorter/background-generated; small metadata overhead per turn.  ·  latency: Interactive turns gain a fast budget decision (<50 ms); congested turns may be faster because they avoid retransmission. Scheduled work can use the cheaper background tier.
- security: Telemetry contains device/network state, not page secrets; manifests and receipts need authenticated device/job IDs and must not log raw audio.
- depends on: Existing /pipeline and /pipeline/audio telemetry routes; Relay durable audio and pendant speech capabilities; A link-aware duplex governor (requested, still not delivered); 24 kHz end-to-end acceptance criteria (requested, still not delivered)

### `hardware` — For the production pendant, replace the nRF9160-DK prototype's single-SoC audio arrangement with a modem plus dedicated low-power audio front-end (I2S codec/DSP with DMA and a small ring buffer), retaining LTE-M on the modem SoC. The front-end owns microphone capture, VAD, resampling, and playback buffering; the modem exchanges framed Opus/audio manifests over SPI. Include a hardware mute latch and battery/fuel telemetry in the audio front-end contract.
- **owner gets:** The prototype spends roughly 87% of one Cortex-M33 core encoding and decoding, while the half-duplex LTE-M link drops speech when the owner talks over a reply. A production audio front-end would make the pendant more reliable, reduce clipped speech and button-to-voice delays, and let privacy mute work even if firmware is wedged.
- effort: High: product PCB and enclosure redesign, codec/DSP firmware, SPI protocol, RF coexistence and battery validation; prototype first with an off-the-shelf low-power audio codec/DSP breakout.  ·  risk: More components and firmware boundaries create sync and power bugs; SPI failure must fail silent and the modem must fall back to text/LED status. This is not a drop-in change for the current DK.
- cost: Indicatively +$8–$20 BOM at low volume, roughly 5–30 mW active depending on codec/DSP; likely lower modem/CPU duty cycle can recover some battery life. No per-call API cost change.  ·  latency: DMA buffering can reduce capture/playback scheduling jitter; add roughly one small frame of buffering (20–60 ms) during handoff.
- security: A physical mute latch improves privacy, but the new coprocessor becomes another firmware supply-chain surface; signed firmware, encrypted SPI pairing, and no raw-audio persistence are required.
- depends on: 24 kHz audio-path acceptance criteria; Production pendant constraints beyond the current nRF9160 DK; A versioned audio manifest and link-aware duplex policy

### `integration` — Create a cross-surface workflow trace ledger, not another executor: relay assigns a workflowId at the pendant intent, propagates it through pipeline events, Mac jobs, browser command IDs, routine previews, and receipts, and emits a signed terminal record containing ordered steps, skipped steps, approvals, and precondition results. Add one query that reconstructs the complete causal timeline without copying raw audio, page secrets, or full keystrokes.
- **owner gets:** When something spans the pendant, Mac, and a logged-in browser, the owner can finally ask “what happened?” and get one truthful timeline rather than separate partial statuses. It also makes future teach-and-repeat routines safe because they are based on an auditable trace, not guessed from unrelated logs.
- effort: Medium: schema propagation through existing routes, relay persistence, redaction, and a read-only dashboard/timeline; executors themselves need not change initially.  ·  risk: Missing propagation at one boundary could create an incomplete trace; mark gaps explicitly and never claim completeness. Correlation IDs must not become a way to join unrelated users or sessions.
- cost: Low storage and negligible model/API cost; no LLM required for the ledger. Retention and deletion controls are required.  ·  latency: One small ID and event write per boundary, normally under 20 ms; no extra model turn.
- security: Reduces secret exposure by storing references, hashes, and redacted metadata instead of raw content. Encrypt records, scope them to the paired owner, and provide deletion.
- depends on: Existing /pipeline, /jobs, browser command/result, /routines, and receipt routes; A relay-side durable correlation store; A redaction policy for audio, browser fields, and typed text


## What it asked for

_Nothing._
## Its own summary

Round 108 produced three concrete next steps. (1) Browser offline quarantine: with the extension currently offline and 10 pending commands, expire and quarantine stale work, replay only revalidated idempotent reads, and require fresh approval for mutations. (2) A cross-surface speech-budget manifest lets relay, Mac, and pendant choose full 24 kHz, shortened audio, or text based on LTE contention and decoder headroom; this directly addresses the observed 7.8 seconds of dropped uplink during simultaneous speech. (3) For the eventual product—not this DK prototype—use a modem plus dedicated audio front-end/DSP with DMA and a physical mute latch, because the current nRF9160 audio path consumes about 87% of its core. I still need the already-requested implementation capabilities and authoritative 24 kHz/product constraints to turn the audio proposals into verified work; I do not need to re-request denied macOS TCC grants. The owner should manually enable Accessibility/Screen Recording only if GUI automation is required; AppleScript, shell, relay, and browser-safe paths remain usable without it.

**Biggest unknown:** The acceptance contract for production audio is still missing: exact end-to-end latency, allowable packet loss/jitter, interruption policy, battery target, and whether the owner accepts a phone/audio companion. Without those, a speech budget or hardware architecture can be reasoned about but not validated.

