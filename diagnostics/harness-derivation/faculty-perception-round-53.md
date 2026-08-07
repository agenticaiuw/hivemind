# Harness derivation — faculty-perception — round 53

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-observe-2026-08-07-r53** — Live Mac observation: AI Pendant Agent PID 25245 is running, but Accessibility is not trusted for com.aipendant.agent and Screen Recording is not granted. inputReachability.status=failed; synthesized input is explicitly not accepted, so UI action receipts cannot be trusted. Browser extension home-chrome is offline with 5 pending commands. Relay is reachable and Mac bridge online.
  - evidence: GET /observe at 2026-08-07T11:51:42.313Z and GET /ops/status: accessibility.trusted=false, screenRecording.granted=false, inputReachability.failed, browserExtension.online=false/pendingCommands=5, relay.reachable=true/macBridgeOnline=true.
- **mac-authority-timezone-contradiction-r53** — The live Mac machine-context reports timezone America/New_York, while owner memory says America/Chicago. Do not infer local time or schedule semantics from machine-context until authoritative timezone is resolved.
  - evidence: GET /machine-context returned machine.timezone=America/New_York; owner projection says timezone America/Chicago.

## Capabilities it proposed

### "Before you act, tell me whether the pendant, Mac, and browser are genuinely ready—and if one is unavailable, continue only with the parts that are safe and report exactly what could not be verified."
- **useful because:** Today the Mac can return successful-looking UI receipts even when synthesized input does nothing, and browser commands can queue while the extension is offline. This gives the owner a truthful readiness boundary instead of silent false completion, using live perception and freshness/contradiction checks across all surfaces.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use a cheap background/status model to normalize observations; reserve realtime only for speaking the concise result. No expensive reasoning is needed unless observations conflict or the owner asks why.
- **latency:** 1–2 seconds for parallel health/perception reads; under 5 seconds when a contradiction requires a second probe. Never block safe read-only work behind an unavailable UI surface.
- **cost:** Usually <$0.01 per check; dominated by model normalization, which can be skipped when typed status fields are unambiguous. No audio generation unless spoken to the owner.
- **security:** Perception must be read-only and redact secrets. Do not capture screenshots or upload vision data without consent. A readiness result is advisory and must not itself authorize irreversible actions; action gates must require fresh preconditions and owner confirmation where policy requires it.
- **missing:** A typed cross-surface readiness contract with observedAt, TTL, capability, and evidence reference for pendant/relay/Mac/browser; Contradiction resolver for owner timezone versus machine-reported timezone and stale browser heartbeat; A pre-action hook that consumes readiness evidence and refuses to trust UI receipts when inputReachability is not ready

### "If the pendant connection drops while you and I are in the middle of something, let me resume later from the exact point we stopped—tell me what changed on my Mac or in my browser while I was away, and never pretend an unfinished step completed."
- **useful because:** A wearable conversation is interruptible by design: radio loss, walking out of range, sleep, or a reboot should not erase the owner’s working state or force them to reconstruct it. The owner gets a concise, trustworthy handoff rather than duplicated work or a false completion claim.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use deterministic event/state reconciliation first. A cheaper background model summarizes the delta; use realtime only for the spoken resume exchange.
- **latency:** Resume state should be available within 1 second after reconnect; delta summarization within 3 seconds. No work should be repeated merely because the link dropped.
- **cost:** Usually under $0.01, dominated by optional delta summarization; event capture and reconciliation are local/database operations.
- **security:** Persist only an encrypted, scoped conversation checkpoint plus action IDs and metadata—not raw microphone audio by default. Browser evidence must retain tab/session boundaries and expire. Never replay or retry an irreversible action without fresh owner confirmation. If state cannot be reconciled, say so and stop rather than guessing.
- **missing:** A cross-surface interruption checkpoint protocol with monotonic sequence numbers for pendant audio, relay turns, Mac jobs, and browser commands; A reconnect reconciler that distinguishes committed, failed, pending, and unknown actions and produces a human-readable delta; A pendant-visible resume marker and acknowledgement handshake so the owner can explicitly accept continuation; Retention and deletion controls for checkpoints separate from ordinary session transcripts


## Changes it proposed to its own stack

### `integration` — Add a read-only Perception Fence service that snapshots /observe, /ops/status, /browser/status, /machine-context, /pipeline, and relay health in parallel; assigns each fact an observedAt, TTL, source, and confidence; detects contradictions (for example machine timezone America/New_York versus owner-authoritative America/Chicago); and emits a signed readiness token that action planning must consume. The token must explicitly mark UI receipts untrusted when inputReachability.status is failed, and expire before any irreversible step.
- **owner gets:** The pendant will stop telling the owner that something happened when the Mac or browser was not actually reachable. It will explain precisely which surface is blocked and still let safe read-only work proceed.
- effort: Medium: shared schema, parallel collector, contradiction rules, token propagation into planner/executor, and dashboard display; add integration tests for offline extension and false UI receipts.  ·  risk: A stale or overly strict fence could refuse useful work. Recover by allowing read-only degraded mode, short TTLs with automatic refresh, and an explicit override only for reversible actions. Never let override turn an untrusted receipt into verified success.
- cost: Negligible runtime cost; typed collection avoids an LLM call. Small storage cost for short-lived evidence records.  ·  latency: Parallel probes add roughly 1–2 seconds before computer actions; cached evidence can serve within TTL for status-only responses.
- security: Read-only metadata only; no screenshots or page contents. Tokens should be scoped to job/session, signed, short-lived, and exclude secrets. Contradiction logs may reveal environment details, so retain briefly.
- depends on: A typed readiness/evidence schema shared by relay, Mac planner, and faculty-action; A planner/executor precondition hook that requires a fresh fence token before UI actions; A browser heartbeat/extension recovery path so offline pending commands are not silently treated as complete


## What it asked for

_Nothing._
