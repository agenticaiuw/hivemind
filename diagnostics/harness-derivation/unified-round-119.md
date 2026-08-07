# Harness derivation — unified — round 119

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **audio-pipeline-approval-ordering** — A completed pipeline generated and uploaded a 24 kHz PCM response while its Mac agent was still blocked on a shell approval; event order is agent waiting approval → TTS done → relay_result done. Spoken output can therefore arrive before the owner approves the underlying action.
  - evidence: GET /pipeline returned job_309f5663... events at 12:00:38–12:00:39: waiting approval for run_shell, then TTS 24 kHz PCM 75,734 bytes, then response waiting for pendant.

## Capabilities it proposed

### "“When you finish something across my Mac and logged-in browser, tell me exactly what happened—and if the connection dropped, continue from the last safe checkpoint and give me one spoken receipt with links and an undo option.”"
- **useful because:** Today pipeline history can contain contradictory states (for example, a Mac approval still waiting while audio is already marked ready). This gives the owner one trustworthy answer assembled from Mac receipts, browser evidence, relay state, and the pendant's actual delivery status—not a plausible but premature summary.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use the cheap/background model to reconcile completed event logs and receipts; reserve realtime only for the owner's live approval or clarification. Use the local Mac planner for resumed computer work and the browser bridge for private-session evidence.
- **latency:** Immediate one-sentence pending/approval prompt; completion receipt within 2–5 seconds after the final receipt arrives. If disconnected, continue asynchronously and notify on reconnect rather than blocking the conversation.
- **cost:** Usually <$0.01 per completed task for reconciliation, dominated by a small background model call; no model call when typed receipts are already sufficient. Audio rendering/upload is the larger cost only for the final spoken receipt.
- **security:** Never include private page text in a notification preview unless the owner requested it. Bind the receipt to job id, action hash, tab/session id, and evidence timestamps; require explicit approval for irreversible actions. Undo must be offered only when a verified inverse exists.
- **missing:** Approval-aware pipeline state machine and durable checkpoint/resume; Cross-surface receipt reconciler joining Mac action receipts, browser provenance, relay jobs, and pendant delivery ACKs; Pendant spoken receipt/approval protocol with expiry and replay protection; A single owner-facing receipt route and dashboard timeline

### "“While you’re speaking a briefing, let me say ‘source’ or ‘go back’ and take me to the exact page and sentence behind the current claim—on my Mac or browser—then resume the briefing where I left off.”"
- **useful because:** A spoken summary is not trustworthy enough when the owner cannot inspect its evidence without stopping to reconstruct the task. This would make the pendant a genuinely useful front end for private browser research: claims remain auditable while walking, driving, or away from the desk.
- **path:** pendant → relay → browser-extension → mac-planner → dashboard
- **model tier:** Use a cheap background model only to segment the briefing into claims and associate each with existing evidence. Use realtime for the short interruption command; use the Mac/browser harness for exact-tab navigation and the relay for session state.
- **latency:** Acknowledge the interruption on the pendant within 300 ms; resolve the cited source and open/focus it within 2–4 seconds; resume audio from the saved claim boundary without replaying the whole briefing.
- **cost:** Usually under $0.01 per briefing for claim/evidence indexing, dominated by one small summarization call. Navigation and resume use existing session state and incur no model cost.
- **security:** Only expose evidence from the owner's authenticated tab/session and never read a different account to satisfy a citation. Show the URL, timestamp, and quoted snippet before opening a mutation-capable page; navigation is reversible and requires no approval, but any action on the page still uses the existing confirmation policy.
- **missing:** Claim-level citation markers embedded in generated text and audio timing metadata; A relay citation registry mapping claim IDs to browser tabId, URL, DOM locator, timestamp, and snippet hash; A pendant command grammar for source/back/resume plus a small local playback bookmark; A Mac/browser route that focuses the exact tab and scrolls to a verified locator, with graceful fallback when the page changed


## Changes it proposed to its own stack

### `integration` — Make pipeline delivery approval-aware: classify each run as informational, reversible, or gated; when any action is blocked on approval, hold action-dependent TTS/audio and relay_result until approval resolves. Emit a separate short pendant prompt containing the exact pending action, evidence link, expiry, and approve/reject affordance; on approval, resume from the checkpoint and produce the final 24 kHz audio, with idempotency so reconnects cannot duplicate execution or speech.
- **owner gets:** The pendant will stop saying a result is ready while a hidden Mac approval is still pending. You get one clear spoken request, can approve from the wearable or dashboard, and then hear only the answer that reflects what actually happened.
- effort: Medium: typed pipeline state/gate, checkpoint persistence in D1, relay-to-pendant approval event, Mac job resume handling, and integration tests for disconnect/reconnect and duplicate presses.  ·  risk: A stale or ambiguous approval could resume the wrong job; bind approvals to job id plus action hash, expire them, require confirmation for destructive actions, and keep current dashboard approval as fallback. Recovery is replay from the last checkpoint without rerunning completed steps.
- cost: Negligible API cost; one small D1 checkpoint/approval record per gated job and a few hundred bytes of event metadata. Audio generation is reduced when blocked because it is not rendered prematurely.  ·  latency: Informational replies unchanged. Gated tasks add one approval round-trip; after approval, resume should be faster than replanning.
- security: Improves safety: approval is cryptographically/request-id bound to exact action and evidence, and no action-dependent content is spoken or delivered before authorization. Pending summaries must avoid leaking private page content on an unattended pendant.
- depends on: An approval-capable pendant event/button protocol (the requested physical transaction approval latch or equivalent); Durable job checkpoints/resume policy; Existing pipeline event stream and Mac action receipts

### `hardware` — For the production pendant, split audio processing from LTE/control: retain the cellular MCU for modem and orchestration, add a low-power audio companion with hardware I2S sample-rate conversion and Opus (or move to an SoC with a dedicated audio/DSP core), and expose a DMA-backed 24 kHz playback/capture path. Specify a clocked 16 kHz uplink and 24 kHz downlink contract instead of the prototype's 15,625 Hz mic and 31,250 Hz wire-clock resampling.
- **owner gets:** Voice will remain clear and responsive while LTE reconnects, buttons/alerts fire, or a long response plays. The pendant is less likely to underrun, clip, or drop a sentence during real-world use.
- effort: High: product-board redesign, codec/DSP firmware, power/RF coexistence validation, and end-to-end audio acceptance testing; keep the nRF9160 DK path as a compatibility fallback during development.  ·  risk: New silicon can introduce driver, clock, and RF-noise failures; mitigate with an audio-loopback fixture, brownout/reconnect tests, and a firmware feature flag that falls back to the existing path. More components increase BOM and board area.
- cost: Roughly $4–$15 BOM increase depending on codec/DSP choice, plus ~10–40 mW active audio power; potentially lower peak cellular-MCU power and fewer retransmitted frames.  ·  latency: Removes current software contention (both Opus directions consume roughly 87% of one Cortex-M33 core); target under 20 ms buffering added by the companion, with more stable 60 ms packet playback.
- security: Keep microphone PCM and keys inside the pendant; companion firmware must be signed, isolated by a narrow control protocol, and erase buffers after transmission. No new cloud data is required.
- depends on: 24 kHz superwideband end-to-end acceptance criteria; Final product pendant constraints and cellular/audio codec selection; audio_link_fault_inject and audio_path_preflight_receipt validation tooling

### `integration` — Add a claim-addressable media/evidence manifest to every generated briefing: each spoken claim gets a stable claimId, source references, byte/time offsets in the audio, and a signed provenance hash. Persist it with the relay job and expose a jump/resume protocol so a pendant interruption can request the current claim, while the Mac/browser opens the matching authenticated tab and locator.
- **owner gets:** The owner can challenge or inspect one sentence of a spoken briefing instead of accepting an opaque audio blob or losing their place while searching. It turns private browser research into something they can audit hands-free.
- effort: Medium-high: extend briefing generation and TTS segmentation, persist manifests, add browser locator fallback when DOM changes, and implement pendant playback bookmarks plus Mac focus/scroll behavior.  ·  risk: A stale locator or inaccurate claim alignment could send the owner to the wrong evidence. Require source timestamp/hash validation, visibly label unavailable or changed sources, and fall back to the cited page rather than pretending exactness.
- cost: Small metadata overhead (roughly 1–5 KB per briefing); modest background indexing cost. No additional realtime model call for simple source/back commands.  ·  latency: No impact on initial playback beyond manifest generation; source lookup should complete within a few seconds, with immediate local pause/bookmark feedback.
- security: Manifests must inherit source sensitivity and remain authenticated; do not copy private snippets into push notifications or public URLs. Use opaque claim IDs and server-side session authorization.
- depends on: A stable browser evidence locator/provenance format; Segmented 24 kHz audio or timing markers; Pendant playback bookmark and interruption protocol; Mac/browser exact-tab focus route


## What it asked for

### `t12-uicl` (tool) — query_unified_job_receipt
- why: The existing job, pipeline, browser-inspection, and action-receipt reads are separate; we need one authenticated read that can determine whether a cross-surface task actually completed and whether its audio was delivered.

```json
{
  "jobId": "string",
  "includeEvidence": "boolean, default false",
  "includeUndo": "boolean, default true",
  "maxEvents": "integer, default 50"
}
```

