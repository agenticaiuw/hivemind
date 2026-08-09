# Harness derivation — unified — round 220

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### ""Submit this form, but make me physically approve the exact final action on the pendant first.""
- **useful because:** This is the first end-to-end path that turns the pendant into a real safety boundary: the browser can inspect the signed-in page, the Mac can prepare but not submit, the pendant requires a deliberate offline-safe approval, and the relay can release only the exact unchanged transaction. The owner gets useful browser automation without treating a spoken 'okay' as sufficient consent.
- **path:** browser → mac-planner → relay-realtime → pendant
- **model tier:** background for page inspection and transaction preparation; realtime only to explain the pending action and collect the owner's next-turn confirmation; deterministic code for digest, expiry, nonce, and release
- **latency:** Prepare in 2-5 s; pendant pending state immediately; after physical approval, submit within 2 s and speak a receipt within 3 s
- **cost:** Usually one background planning call plus one short realtime turn; roughly $0.02-$0.10 depending on page complexity. Browser and relay calls dominate latency, not tokens.
- **security:** Never send page secrets or form values to the pendant. Bind approval to plan digest, world fingerprint, target tab, expiry, and one-time nonce; refuse if the page changes. Require explicit confirmation for irreversible/off-machine actions. This depends on implementing the relay half of approvalHandoff and making the next-conversation delivery path real; the current single bearer token is not privilege separation.
- **missing:** relay implementation of APPROVAL_STORE_CONTRACT; bridge from prepare/approve to browser submit; delivery/readback so deliveredAt can be set; transaction release endpoint that verifies the pendant nonce

### ""Before an important call, tell me whether the whole system is actually ready — pendant, link, relay, Mac, browser, and headphones — and what I should do if it isn't.""
- **useful because:** A single owner-facing readiness verdict prevents the worst failure mode: beginning a conversation while the microphone, relay, browser bridge, or Bluetooth playback is silently broken. It combines live evidence rather than reporting one green health endpoint, and can recommend a safe fallback instead of pretending readiness.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** deterministic checks and cheap background summarization; realtime only for the concise spoken verdict
- **latency:** Under 5 s for checks, under 8 s to speak. Never run synthetic audio on every turn; use the explicitly triggered fixture and cached last-known-safe profile.
- **cost:** Near-zero model cost for deterministic checks; at most a short summarization call, under $0.01. Network and hardware probes dominate.
- **security:** Report only health counters and redacted identifiers, not page contents or audio. A failed check must not auto-change network, privacy, or audio settings. If repair is offered, require a separate owner confirmation and retain the diagnostic receipt.
- **missing:** a typed readiness aggregator correlating pendant counters, bridge acknowledgement, relay job state, Mac/browser bridge state, and the latest audio fixture; a small owner-facing policy for stale versus fatal measurements; optional safe repair hooks for restarting browser polling or revalidating the audio path

### ""Calibrate the pendant-to-headphones path so speech is clear and never clips, then show me the measured before/after.""
- **useful because:** The shipped 24 kHz path ends at a prototype ESP32 A2DP bridge that resamples to fixed 44.1 kHz stereo, and its Bluetooth buffer has already starved into silence. A user-facing calibration would measure the real bridge and headphones, choose safe gain/latency parameters, and prove the result instead of guessing from the relay's PCM.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** deterministic synthetic audio and on-device counters for calibration; cheap background model only to explain the measurements; realtime only for the spoken result
- **latency:** One deliberate calibration run in 15-30 s, with playback muted until the fixture is ready; no calibration work on the conversation hot path
- **cost:** Negligible model cost; a few deterministic fixture runs. Main cost is 15-30 s of owner time and Bluetooth test audio.
- **security:** Use synthetic tones/no speech and discard captured audio. Require explicit physical start because the fixture emits sound. Never raise gain above a measured clipping ceiling or alter privacy-latch state. Persist only numeric profile values and a receipt.
- **missing:** bridge-side loopback/ack and clipping telemetry at the A2DP sink; a controllable safe gain/latency profile separate from the 24 kHz codec profile; fixture orchestration that correlates pendant decode, ESP32 resampler, SBC/A2DP buffer, and headphone playback; owner-visible before/after report

### ""Before anything leaves my Mac or browser, show me exactly which fields and bytes would cross the boundary, minimize them to the task, and let me approve the sanitized payload on the pendant.""
- **useful because:** Today an action can be approved as a whole, but the owner cannot inspect or constrain the data it exports. This would make the hive useful for sensitive work: it could operate logged-in browser sessions and the relay while proving that only the minimum task-specific data crossed from Mac/browser, with a physical approval for the final payload.
- **path:** mac-planner → browser-extension → relay-realtime → pendant
- **model tier:** deterministic taint/provenance tracking and redaction first; background model for proposing minimization rules; realtime only to summarize the compact diff and collect the next-turn decision
- **latency:** Preview in 2-6 s for ordinary pages/files; physical approval and release in under 2 s after the owner decides. No payload should be transmitted before approval except explicitly classified public metadata.
- **cost:** Low model cost for routine schemas, roughly $0.01-$0.05 when semantic field classification is needed. Hashing, diffing, and relay persistence dominate implementation rather than inference.
- **security:** The pendant receives field names, hashes, sizes, and a human-readable summary—not secrets or raw page contents. Every outbound byte needs provenance, destination, purpose, expiry, and a redaction decision. Refuse unknown binary blobs, hidden form fields, and changed pages. Preserve an audit receipt without retaining the sensitive payload; make deletion and relay replication explicit.
- **missing:** byte/field-level taint tracking across Mac actions, browser results, and relay jobs; a deterministic minimizer/redactor with owner-editable allowlists and deny patterns; a compact pendant preview protocol that can represent fields, hashes, and an approval-bound payload digest; relay storage and release that verifies the approved sanitized digest, destination, expiry, and page world fingerprint; tests proving no pre-approval payload leakage in logs, receipts, model prompts, or browser command queues


## Changes it proposed to its own stack

### `relay` — Implement the approvalHandoff relay store and release path: persist the prepared plan digest/world fingerprint/expiry/deliveredAt, accept exactly one pendant approval nonce or cancellation, and atomically hand the unchanged browser command to the Mac. Add a lease and expiry sweep so a relay or Mac crash cannot leave an approval or browser job permanently processing.
- **owner gets:** The owner can safely say 'do it' for a sensitive browser action and physically approve the exact action, rather than hearing 'waiting for approval' and discovering nothing can ever continue. Crashes become recoverable instead of silently dropping or duplicating the submission.
- effort: Medium-high: D1 schema/migrations, relay handlers, pendant event verification, browser-job release, integration tests for page mutation and replay.  ·  risk: A bug could release an action twice or approve a changed page. Mitigate with unique nonce/plan digest constraints, compare-and-set state transitions, short TTLs, world revalidation immediately before submit, and a dry-run test harness. Recover stale records with expiry/cancellation, never automatic replay of unrepeatable actions.
- cost: Small D1 storage and a few relay requests per staged action; negligible model cost. No new hardware cost.  ·  latency: Adds roughly 0.5-2 s after the physical approval; preparation remains asynchronous.
- security: Improves security by making the pendant approval meaningful, but the shared bearer token still lacks privilege separation; split prepare/release credentials before treating this as a strong authority boundary.
- depends on: Use the existing POST /prepare and POST /approve Mac routes; Implement relay side of shared/approvalHandoff.js APPROVAL_STORE_CONTRACT; Connect physical_transaction_approval_latch events from the pendant; Add browser-job release and final /browser/inspect world check


## What it asked for

_Nothing._
## Its own summary

Discovered the live Mac agent is healthy (v0.5.0), with 223 routes and real /prepare and /approve groups; the earlier assumption that those routes were absent was wrong. Recorded three distinct capabilities: (1) physically approved exact browser submission, (2) cross-surface pre-call readiness verdict, and (3) measured pendant-to-headphones calibration. Also recorded the relay-side approvalHandoff implementation as the key stack change. The owner-facing fact-review/erase proposal was correctly rejected as already covered by existing policy/backlog, not rephrased.

**Biggest unknown:** The relay's actual approval persistence and pendant-event ingestion are still unobserved. I also still need a typed bridge telemetry/calibration interface: current audio routes expose pipeline artifacts, but not proof that bytes reached the ESP32 A2DP sink or headphones.

