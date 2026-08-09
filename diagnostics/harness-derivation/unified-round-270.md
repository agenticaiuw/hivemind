# Harness derivation — unified — round 270

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When a conversation or action goes wrong, tell me exactly where it failed: my button press, the relay, the Mac/browser action, or whether I actually heard the reply."
- **useful because:** A successful relay receipt is not capture, execution, or hearing. This gives the owner one causal, cross-surface answer instead of repeated retries and false 'done' claims, using sequence IDs and delivery evidence to distinguish missing audio from missing action.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** deterministic correlation and thresholds first; background model only to phrase the ranked hypotheses; realtime for a spoken concise answer
- **latency:** Return a first diagnosis in under 2 s from cached receipts; fetch missing evidence within 10 s and clearly stream 'still checking'.
- **cost:** <$0.005 for deterministic cases; <$0.02 when a model summarizes ambiguous evidence. Storage is a bounded event index, not audio retention.
- **security:** Expose only artifacts bound to the owner's job/session; hash or redact page contents and audio. Do not let diagnosis trigger retries or repairs. Distinguish 'not observed' from 'failed' and preserve immutable receipts for accountability.
- **missing:** A correlated event key spanning pendant turn, relay job, Mac/browser command, and audio delivery ACK; A read-only owner-facing route that joins existing pipeline, job, browser, and pendant receipts; A dashboard timeline and concise spoken diagnosis renderer

### "Before you run a long or risky computer task, give me a short spoken preview, let me approve it on the pendant, and resume safely after a Mac or relay restart without doing any step twice."
- **useful because:** The action ledger and approval cryptography already exist, but the live approval loop is unreachable and interrupted ledgers are falsely reported because ordinary plans never close. Wiring this end to end is the single biggest trust improvement: the owner gets a physical consent boundary and crash recovery rather than spoken promises that disappear.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** deterministic ledger/replay and approval checks; background planner for preview wording; realtime only to read the preview aloud
- **latency:** Preview in under 3 s; physical approval receipt within 2 s of reconnect; restart recovery on next worker poll, under 30 s.
- **cost:** <$0.01 per plan outside model planning; negligible storage for bounded ledgers and approval records. Background planning dominates.
- **security:** Gate approval by plan digest, world fingerprint, expiry, and physical nonce; auto-resume only idempotent/additive replaySafety, require fresh approval for unrepeatable/unknown or riskTier irreversible-write/off-machine/uncontained. Never send secrets/page contents to the pendant. Keep job leases and approval records auditable.
- **missing:** Call closeLedger from orchestrator and reject stale inflight steps; Implement relay persistence for APPROVAL_STORE_CONTRACT and a next-conversation delivery path; Add relay job lease_until/requeue sweep and invoke the existing resume planner; Wire physical_transaction_approval_latch events into /approve and dashboard preview

### "Before you send anything off my Mac or pendant, show me exactly what data will leave, where it will go, how long it will be kept, and let me allow or deny that specific transfer."
- **useful because:** The system spans a relay, browser sessions, Mac apps, and a wearable, but the owner cannot inspect the data boundary of a particular request. A per-transfer manifest makes privacy a concrete decision instead of a global trust assumption, especially for page text, audio, screenshots, and inferred facts.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** deterministic data-flow classification and redaction; background model only to summarize a manifest in plain language
- **latency:** Manifest in under 500 ms before dispatch; physical approval or denial within 2 s; no transfer may begin while the decision is pending.
- **cost:** <$0.005 per manifest; classification is deterministic and model summarization is optional.
- **security:** The manifest itself must not leak the sensitive payload it describes. Hash and classify fields, show bounded previews only after explicit expansion, bind consent to destination, purpose, payload hash, and expiry, and fail closed on unknown flows. Preserve denial receipts without retaining rejected content.
- **missing:** A provenance/data-flow manifest emitted by every Mac, browser, relay, and audio operation; A pre-dispatch policy gate that can hold a job before network transmission; Dashboard and pendant rendering for manifests larger than a short spoken summary; A distinct owner policy for categories such as raw audio, page secrets, screenshots, and derived facts

### "Mark this real-world handoff as witnessed: record only who/what I name, the exact time, and a signed press from my pendant—no room audio—and let me retrieve the receipt later."
- **useful because:** The owner has no trustworthy way to create a privacy-safe proof that an in-person event happened. A deliberate pendant action can attest to a named handoff without continuously recording or inferring location, while the Mac can attach a calendar/task reference and the relay can preserve the receipt across link loss.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** deterministic receipt construction; background model only to normalize the owner's spoken label
- **latency:** Local confirmation under 300 ms; signed relay receipt under 5 s when connected; durable offline queue when disconnected.
- **cost:** Under $0.005 per receipt; a few hundred bytes of metadata, no audio storage.
- **security:** Require explicit button confirmation, bind the receipt to a nonce and monotonic device counter, encrypt names/labels, and never claim a person's identity or physical location beyond what the owner explicitly entered. Make receipts individually revocable without rewriting the audit chain.
- **missing:** A pendant event-attestation payload and monotonic counter integration; Relay storage and verification for signed non-audio attestations; A Mac/dashboard form that binds an attestation to an optional task or calendar item

### "For the next 30 minutes, block every off-device transfer of audio, page content, screenshots, and inferred facts, while still letting me use local Mac actions; show me what was held and release it only when I say so."
- **useful because:** The existing privacy latch protects the pendant, but it does not provide a temporary system-wide egress embargo across the relay, browser, Mac, and queued work. This gives the owner a bounded privacy mode that is stronger than muting and less disruptive than shutting down local assistance.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** deterministic policy enforcement and queue classification; no model call on the enforcement path
- **latency:** Latch-to-egress block under one second; queued-transfer inventory under two seconds; release requires an explicit new confirmation.
- **cost:** Negligible runtime cost; bounded metadata queue. No model cost unless the owner asks for a natural-language inventory summary.
- **security:** Fail closed on unknown destinations and unknown payload classes. Do not retain blocked raw audio merely to report it. Bind expiry and release to a device nonce, prevent stale queued work from bypassing the embargo, and make the pendant's LED state distinguish embargo from ordinary mute.
- **missing:** A shared egress policy hook in Mac, browser, and relay dispatchers; A typed pending-transfer inventory with payload hashes and destinations; Firmware event handling that starts/ends the temporary embargo without replacing the persistent privacy latch

### "Move an active conversation from the pendant to my Mac speakers or back without making me repeat myself, duplicating a reply, or losing what was already spoken."
- **useful because:** The owner currently has no user-visible endpoint handoff: a worn device, relay, and Mac bridge can each be alive while turn state and playback ownership remain implicit. A negotiated handoff would make the hive feel like one conversation and prevent split-brain audio during charging, travel, or a link recovery.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** deterministic turn/sequence handoff; realtime model only continues the conversation after the transport switch
- **latency:** Announce and commit a handoff within 1 s; resume playback within 500 ms at a turn boundary; never cut a decoded frame mid-buffer.
- **cost:** No additional model call for transport changes; small relay state and one control event per handoff.
- **security:** Require the owner to initiate or confirm the destination, authenticate both endpoints, and fence old playback with an epoch token. Do not mirror microphone audio to a second endpoint during transition; expire abandoned handoff offers.
- **missing:** A transport-owner/epoch protocol spanning pendant, relay, bridge, and Mac audio; A turn checkpoint containing transcript position, playback sequence, and unplayed audio range; Mac speaker/microphone endpoint controls and a visible handoff affordance


## What it asked for

_Nothing._
## Its own summary

This round produced three new recorded capabilities: (1) a cross-surface causal failure diagnosis that distinguishes pendant capture, relay acceptance, Mac/browser execution, and physical hearing; (2) an end-to-end physically approved, crash-safe action workflow using replaySafety rather than reversibility; and (3) a fail-closed per-transfer data-flow manifest so the owner can approve exactly what leaves the device. The hidden-fact erase proposal and timezone audit were correctly rejected as existing backlog items. Live discovery also showed the pendant registered but offline and the Mac bridge online.

**Biggest unknown:** Several routes relied on by the approval/data-boundary designs are not currently verified as callable on the live server: describing POST /prepare and POST /approve produced GET-style 404 probes. I still need a real POST route check or orchestrator confirmation of their deployment, plus implementation of relay approval persistence, event correlation IDs, and per-operation data-flow manifests.

