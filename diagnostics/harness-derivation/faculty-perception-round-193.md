# Harness derivation — faculty-perception — round 193

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac agent permissions and browser continuity** — Live /ops/status reports AI Pendant Agent host fingerprint com.aipendant.agent with Accessibility trusted=true, Screen Recording granted=true, requiredMissing=[] and ready=true. Browser extension is online with 3 tabs, 0 pending commands, current active tab Namecheap, and relay is reachable with D1 store and macBridgeOnline=true.
  - evidence: GET /ops/status HTTP 200 at 2026-08-08T22:41Z
- **live pipeline failure and delivery truth** — The newest routine pipeline job job_e60ca5d3... is marked failed after Mac TTS produced 430,836 bytes of 24 kHz PCM, because reporting bridge work result returned HTTP 413 Payload Too Large. Its derived delivery state is composed_on_mac, awaitsDevice=true, heard=unknown; no device_playback event exists. /ops/snapshot simultaneously reports browser pendingCommands=1.
  - evidence: GET /pipeline and GET /ops/snapshot HTTP 200 at 2026-08-08T22:41Z

## Capabilities it proposed

### "When I ask “what failed while I was away?”, give me only verified failures and unfinished actions, explain the exact boundary where each stopped, and offer the safest resume for each."
- **useful because:** Today the system can mark a run failed after a 413 while audio exists, and can simultaneously leave a browser command pending; a human cannot tell whether to retry, shorten audio, or execute the browser action. This capability turns raw telemetry into an honest, actionable interruption report without claiming the owner heard anything.
- **path:** relay → mac-planner → browser-extension → dashboard
- **model tier:** background for correlation and classification; realtime only to answer a follow-up or request confirmation
- **latency:** under 3 seconds for the report; no action is taken until confirmation
- **cost:** about $0.01–$0.04 per report, dominated by a small background model call; most evidence is structured and needs no model
- **security:** May expose browser URLs and job text; redact secrets and show provenance. Never retry side effects automatically; require confirmation for browser mutations or re-speaking audio.
- **missing:** A durable cross-surface failure record joining pipelineId, relay job ID, bridge result status, browser command ID, and receipt ID; A payload-size-aware audio handoff that records whether the PCM was chunked, rejected, or only locally rendered; A classifier that distinguishes 'Mac rendered', 'relay accepted', 'device received', and 'owner heard'

### "Finish this briefing even if the network rejects the audio: deliver a compact playable version, preserve the full answer locally, and tell me exactly which version was sent and which was not."
- **useful because:** A verified live run rendered 430,836 bytes of 24 kHz PCM but failed reporting with HTTP 413 Payload Too Large, leaving the answer composed on the Mac and unheard. Adaptive delivery would make long responses usable instead of silently ending at the transport limit.
- **path:** mac-planner → relay → relay-realtime → pendant → dashboard
- **model tier:** No expensive model for transport adaptation; use deterministic chunking/codec policy, with a cheaper background summarizer only when a compact fallback is needed
- **latency:** first playable fallback within 2 seconds after a 413; full upload may continue in the background
- **cost:** negligible API cost for chunking; optional fallback summarization about $0.005–$0.02
- **security:** Audio and transcript cross the relay; bind chunks to a per-response ID, hash each chunk, expire incomplete uploads, and require explicit owner policy before replacing a long answer with a summary.
- **missing:** Chunked/resumable PCM or Opus upload with negotiated byte limits; Relay-side reassembly and per-chunk checksum/expiry; A device playback acknowledgement tied to the response ID; A spoken or dashboard label distinguishing fallback summary from full answer

### "Resume everything that was interrupted while I was away, but first show me a ranked list of what is safe to resume, what needs my approval, and what is no longer valid."
- **useful because:** The live system can know that a browser command is pending and that a pipeline failed, but it does not unify them into resumability. This would prevent duplicate browser actions, avoid replaying stale news, and let the owner recover useful work with one deliberate confirmation.
- **path:** relay → mac-planner → browser-extension → dashboard → pendant
- **model tier:** Cheap background model for ranking and expiry reasoning; realtime only for the owner's spoken confirmation
- **latency:** under 5 seconds to produce the ranked queue; execution begins only after confirmation
- **cost:** about $0.01–$0.05 per ranking; action execution uses existing Mac/relay costs
- **security:** Never infer approval from inactivity. Browser mutations, messages, purchases, and reminders require explicit per-item confirmation. Treat stale routine/news content as expired using source timestamps, not job completion.
- **missing:** A resumability journal with idempotency keys and semantic expiry per work item; A browser command lifecycle that exposes pending/claimed/applied/rolled-back rather than only pending count; A policy evaluator for reversible versus irreversible actions; A true device-heard signal before treating spoken recovery as complete

### "Before you let me believe a browser action worked, show me the page state that proves it, say what changed, and tell me if the proof came from the browser session, the Mac screen, or neither."
- **useful because:** The system now has verified Accessibility and Screen Recording, a live Safari extension, and browser commands, but success is still inferred from command completion rather than observed state. A provenance-labelled visual witness would catch failed submits, login walls, stale tabs, and actions that never reached the screen.
- **path:** browser-extension → mac-vision → mac-planner → relay → pendant → dashboard
- **model tier:** Use deterministic browser result/DOM checks first; use the vision model only when structured state is unavailable; realtime is only for the owner's immediate question
- **latency:** 2–6 seconds after a browser mutation, with a screenshot/DOM witness before reporting success
- **cost:** Usually no extra model cost; vision fallback roughly $0.01–$0.05 per witness depending on image size
- **security:** Screenshots may contain passwords, payment data, and private pages. Redact before relay storage, keep evidence local by default, hash the witness, and require confirmation before sharing or acting on sensitive state.
- **missing:** A single postcondition contract joining browser command ID, tab/session, expected state, and observed witness; Redaction and retention policy for screenshot evidence; A relay-visible provenance reference so spoken claims can cite the witness without uploading the whole image

### "Show me a safe counterfactual of an unfinished action: what the Mac, browser, relay, and pendant would do next, what could go wrong, and the exact point where I would still be able to cancel—without touching the real world."
- **useful because:** The owner cannot currently inspect the next step of a partially completed workflow without either trusting a planner or risking a retry. A cross-surface dry-run would turn opaque recovery into something reviewable, especially when a browser command is pending or audio transport stopped mid-flight.
- **path:** mac-planner → mac-vision → browser-extension → relay → pendant → dashboard
- **model tier:** Cheaper background model for plan simulation; deterministic action schemas and capability checks must constrain it; realtime only to narrate the result
- **latency:** under 5 seconds for a simulation; zero side effects during simulation
- **cost:** roughly $0.01–$0.05 per simulation, dominated by vision only when screen state is required
- **security:** Simulation must never invoke mutating endpoints, send text, purchase, or upload private content. Mark inferred branches separately from observed facts; keep screenshots local and redact secrets.
- **missing:** A first-class dry-run mode accepted by Mac and browser action executors; A shared workflow graph with per-step cancel points and side-effect classifications; A way to model pendant delivery without falsely treating socket writes as hearing

### "Let me ask “what did you almost do?” and get a privacy-preserving answer listing discarded, blocked, and abandoned actions—including the reason, the data they would have touched, and whether anything escaped the device."
- **useful because:** Today the owner can see successful jobs and some failures, but not the dangerous near-misses: an action rejected by a permission boundary, an abandoned browser mutation, or a response that rendered locally but never left. This is the missing negative-space view of agency.
- **path:** relay → mac-planner → browser-extension → dashboard → pendant
- **model tier:** Deterministic event aggregation first; cheap background summarization for human wording; realtime only when asked aloud
- **latency:** under 3 seconds from bounded ledgers
- **cost:** near-zero model cost for structured results; under $0.01 when summarization is needed
- **security:** Negative-space logs can reveal private URLs, message targets, and secrets indirectly. Store redacted reason codes and destination classes by default, with detailed evidence kept local and short-lived.
- **missing:** A durable non-action ledger for refused, cancelled, expired, and never-dispatched intents; A distinction between planned data access and actual data egress; Retention and redaction rules for abandoned work, not just completed jobs

### "When a sensitive action needs approval, let me authorize exactly that action with one physical pendant gesture, show me the precise scope and expiry first, and make the authorization useless for every other site or action."
- **useful because:** The owner currently has to trust a conversational confirmation across relay, Mac, and browser; a spoken yes can be ambiguous or arrive after state changes. A physical, narrowly scoped approval would bind intent to the person wearing the device and prevent accidental reuse.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic policy and token checks; realtime only to explain the pending approval; no background model needed
- **latency:** approval acknowledgment under 500 ms once the owner presses; token expiry and replay checks synchronous
- **cost:** Negligible model/API cost; small firmware and protocol work
- **security:** A lost or stolen pendant becomes an approval bearer. Require session binding, nonce, short expiry, visible spoken summary, cancellation gesture, and server-side audit; never permit unrestricted shell, payment, or message scopes.
- **missing:** A pendant-originated signed approval frame with monotonic counter and nonce; Relay-issued capability tokens scoped to action, origin, parameters hash, and expiry; Browser/Mac executors that refuse mutations without a matching token; A clear physical UX for approve, cancel, and emergency revoke


## Changes it proposed to its own stack

### `integration` — Implement an adaptive bridge-result envelope: send transcript/result metadata first, stream PCM in bounded chunks under the relay request limit, and make the final receipt reference chunk IDs and SHA-256 hashes. On HTTP 413, automatically retry only the missing chunks or a deterministic low-bitrate fallback, never the whole side effect.
- **owner gets:** A real briefing currently renders audio successfully but becomes failed at the final 413, so the owner gets neither a reliable response nor a clear recovery. This makes long spoken answers finish instead of disappearing at the upload boundary.
- effort: Medium: protocol and relay storage changes across Mac bridge and cloud relay, plus integration tests with oversized audio.  ·  risk: Chunk loss or duplicate playback; mitigate with idempotent response/chunk IDs, expiry, and device playback acknowledgement. Recover by retaining the Mac-local full audio and reporting exact missing chunks.
- cost: Small storage and bandwidth increase; no model cost. Chunk metadata adds a few KB per response.  ·  latency: First audio can start sooner; full completion may add one round trip for missing chunks.
- security: Audio crosses relay in more requests; authenticate every chunk, bind it to the response, hash it, and expire abandoned uploads.
- depends on: A relay contract for resumable audio chunks; A device playback acknowledgement tied to response ID

### `dashboard-ux` — Add a “reality boundary” row to every run showing independently: rendered_on_mac, accepted_by_relay, received_by_device, playback_started, playback_finished, and owner_heard; render unknown as unknown, never as success. Include the exact first failure (for example HTTP 413) and any pending browser command IDs.
- **owner gets:** The current live pipeline already knows that audio was rendered but not heard, yet that truth is buried in telemetry. The owner should immediately see whether a failure needs retry, confirmation, or no action.
- effort: Low to medium: reuse existing delivery object and pipeline events, add UI and structured error joins.  ·  risk: False confidence if a fallback derivation is reused; require each state to name its witness and prohibit Mac completion from closing device states.
- cost: Negligible API cost; modest dashboard engineering.  ·  latency: No runtime effect; dashboard reads existing records.
- security: Expose only bounded error/provenance metadata; redact command text and URLs according to existing sanitization.
- depends on: A stable response/run identifier shared by pipeline and relay receipts; A defined device_playback emitter, currently absent

### `context` — Add a cross-surface uncertainty budget to every answer: each factual claim carries an evidence class (observed, reported by another surface, inferred, or unknown), an age, and an explicit contradiction set. The relay must preserve these annotations when turning Mac/browser evidence into speech instead of flattening them into a completed narrative.
- **owner gets:** The owner would stop receiving a single confident story when the Mac says audio exists, the relay says a job failed, and the pendant has no playback witness. They would hear exactly which parts are facts and which are only inference.
- effort: High: propagate compact evidence annotations through planner output, relay job records, browser provenance, and speech composition; add tests that reject unsupported completion claims.  ·  risk: More qualified answers may feel slower or less decisive; mitigate by speaking only the top contradiction and offering detail on request. Never let an inferred fact satisfy an action precondition.
- cost: Small storage/context overhead; lower model cost if structured annotations replace repeated prose evidence.  ·  latency: Adds tens to hundreds of milliseconds for validation, not a model round trip on the hot path.
- security: Evidence references may expose URLs or local paths; use opaque IDs and access-controlled local expansion, with redacted summaries sent to relay.
- depends on: A shared evidence vocabulary across Mac, browser, relay, and pendant; Stable IDs for cross-surface joins; A speech renderer that can preserve uncertainty instead of converting it to success/failure


## What it asked for

_Nothing._
## Its own summary

Fresh reality established: Accessibility and Screen Recording are now truly granted to com.aipendant.agent; /observe says inputReachability=verified and UI actions will reach the screen. Safari’s extension is online with 3 tabs, but /ops/snapshot currently reports 1 pending browser command. The newest pipeline rendered 430,836 bytes of valid 24 kHz PCM, then failed at bridge-result reporting with HTTP 413 Payload Too Large; its honest state is composed_on_mac, awaitsDevice=true, heard=unknown. I recorded these facts and proposed adaptive resumable audio, a reality-boundary dashboard, failure/resume triage, and postcondition visual witnesses. What I still need is not another diagnostic grant: the exact relay payload limit and a bounded chunk/fallback contract, a stable response ID joining pipeline/relay/browser receipts, and a real device playback event. The pendant remains absent from the live registry, so hearing cannot yet be verified.

**Biggest unknown:** Which browser command is pending and whether it is safe or stale; /ops/snapshot exposes only the count, not the command identity in the aggregate view.

