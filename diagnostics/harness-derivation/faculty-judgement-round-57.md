# Harness derivation — faculty-judgement — round 57

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **routine_truthfulness** — The live routine ledger marks all five scheduled routines as completed, while owner memory records repeated failed Gmail/GitHub/Calendar reads. There is no visible per-source coverage or freshness in GET /routines.
  - evidence: GET /routines returned five entries with lastStatus=completed and lastError=null; owner discover:owner lists failed reads for gmail, github, and calendar.

## Capabilities it proposed

### "“When my scheduled brief runs, tell me exactly which sources were checked, which were unavailable or stale, and keep retrying the missing parts—never say it completed when it only produced a partial answer.”"
- **useful because:** The current routine ledger reports multiple jobs as completed even though the owner’s requested Gmail, GitHub, and Calendar reads have repeatedly failed. This gives the owner a trustworthy brief rather than confident silence, and lets them decide whether to fix permissions or accept a partial result.
- **path:** relay-realtime → relay → mac-planner → browser-extension → mac-terminal → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use a cheap background model to normalize source receipts and classify stale/blocked/complete; reserve realtime only to explain the result or ask for one permission decision. No model should infer success from a lack of error.
- **latency:** At schedule time, publish a partial coverage receipt within 2–5 seconds, then retry eligible missing sources in the background for up to 15 minutes. Spoken summary should be under 30 seconds and interruptible.
- **cost:** Low: one background normalization call per routine run (roughly $0.001–$0.01 depending on source count); retries are mostly I/O. Realtime cost occurs only if the owner asks follow-up.
- **security:** Receipts must contain source names, timestamps, permission state, and error class, not page contents or secrets. Browser data remains in the authenticated bridge; require confirmation before any mutation. Never expose secret-bearing URLs or snippets in the pendant audio.
- **missing:** A routine execution contract with per-source required/optional inputs and freshness windows; A durable per-step receipt schema shared by Mac, browser bridge, relay, and pendant; A retry/lease policy that distinguishes transient offline failures from permanent permission failures; A scheduler rule preventing lastStatus=completed when required evidence is absent; A compact spoken and dashboard rendering for coverage receipts

### "“If I double-press and hold the pendant, make the whole AI hive go private immediately: stop talking, cancel queued actions, freeze browser and Mac control, revoke active sessions, and do not send or retain anything else until I explicitly unlock it.”"
- **useful because:** A person wearing an always-listening, multi-surface agent needs a dependable physical privacy brake that works even when speech recognition, the Mac, or the network is confused. Today there is no owner-verifiable way to stop every surface at once or know that private mode actually took effect.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → mac-terminal → unified → faculty-action → faculty-judgement
- **model tier:** No model is needed to enter or enforce private mode. The pendant firmware and relay enforce it deterministically; a cheap background process may reconcile acknowledgements afterward. Realtime may only speak the short confirmation after local enforcement succeeds.
- **latency:** Pendant must mute capture/playback and emit the local privacy indication immediately, under 100 ms. Relay and connected surfaces should acknowledge within 1 second; disconnected surfaces receive the revocation on reconnect before accepting work.
- **cost:** Very low per invocation: state propagation and cancellation only, with no inference. Small persistent event records cost negligible storage. Hardware cost is near zero if an existing button supports a distinct gesture; otherwise a dedicated privacy switch is roughly $1–$3 in components.
- **security:** The gesture must be local, debounced, and impossible to trigger accidentally during ordinary presses. Private mode should fail closed: no queued command may execute without a fresh capability token issued after unlock. Existing in-flight irreversible actions need a defined boundary—cancel before commit where possible, otherwise report their receipt without taking new action. Store only mode transitions, not audio. Unlock must require a deliberate local gesture plus spoken/visual confirmation; never unlock from a remote request.
- **missing:** A pendant-firmware privacy latch with local mute and nonvolatile mode state; A signed, short-lived cross-surface capability token required by Mac and browser action endpoints; Relay fan-out for immediate revoke, cancellation, and reconnect-time enforcement; Browser extension and Mac agent middleware that rejects commands while the token is revoked; A visible pendant indicator and a concise acknowledgement protocol; An audit/receipt record showing which surfaces acknowledged the freeze without recording private content


## Changes it proposed to its own stack

### `integration` — Add a routine coverage ledger and completion gate between the scheduler, Mac jobs, browser commands, and briefing/audio delivery. At run creation, compile required sources and freshness windows; every child operation emits a typed receipt {source, attemptId, startedAt, finishedAt, status=verified|stale|blocked|transient-failure|not-run, evidenceRef, errorClass}. The parent routine is completed only when all required sources are verified or the owner explicitly accepts partial; otherwise it is partial/needs-attention. Retry transient failures with leases, stop retrying permission failures, and send one reconnect/permission event to the pendant. Render the same receipt in /briefing/latest and the spoken audio queue.
- **owner gets:** A morning brief will distinguish “nothing changed” from “I could not read your accounts,” and it will not silently turn inaccessible mail/calendar/GitHub into a false completed run. The owner gets one actionable explanation instead of discovering failures later.
- effort: Medium-high: shared receipt schema, scheduler parent/child state machine, adapters in Mac and browser bridge, retry worker, and briefing/audio renderer; add failure-injection tests for offline, stale, permission-denied, duplicate, and reconnect cases.  ·  risk: A strict gate may produce more partial alerts and expose flaky permissions. Recover by allowing per-routine required/optional source policy and an explicit “accept partial” action; idempotent attempt IDs prevent duplicate retries or duplicate audio.
- cost: Negligible storage and I/O; one cheap background aggregation call per run if normalization is model-assisted. No additional hardware.  ·  latency: Initial receipt in seconds; retries can continue asynchronously for up to a policy limit. Spoken brief may be delayed only when required sources are pending; otherwise partial is immediate.
- security: Keep evidence references opaque and redact page contents from receipts/audio. Permission errors are safe to report; authenticated source payloads stay on their owning surface. Preserve confirmation gates for sends/deletes/purchases.
- depends on: Durable cross-surface job/event persistence and leases; A typed context projection that supplies routine source policy and freshness; Browser bridge reconnection and Mac permission truthfulness; The already-requested cross-surface preflight/recovery primitives


## What it asked for

_Nothing._
