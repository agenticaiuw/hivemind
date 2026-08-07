# Harness derivation — faculty-perception — round 44

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-ui-observability** — At 2026-08-07T11:18:20Z the Mac agent can enumerate apps, but UI control is not reachable: /observe reports Accessibility trusted=false, eventsPost=false, inputReachability=failed, screenRecording=false; /ops/status independently reports ready=false and missing Accessibility/Screen Recording. The host is AI Pendant Agent at /Users/evanliu/Applications/AI Pendant Agent.app, while the OS grant appears attached to a different binary. Browser extension is offline with 3 pending commands.
  - evidence: GET /observe and GET /ops/status live responses
- **machine-timezone** — The Mac machine-context currently reports timezone America/New_York. This is machine configuration evidence, not proof of the owner's authoritative timezone for scheduling.
  - evidence: GET /machine-context live response at 2026-08-07T11:18Z

## Capabilities it proposed

### "When I ask the pendant, “Did that actually happen?”, give me a trustworthy yes/no answer based on independent evidence—not just an action receipt—and if it did not happen, tell me exactly what blocked it and keep watching until the action becomes safe to retry."
- **useful because:** Today the system can report apparent success even when macOS rejects synthesized input. The owner needs to know whether the real-world change occurred, especially when away from the Mac, without manually checking every application. This combines wearable voice, always-on relay state, Mac observation, and authenticated browser/application postcondition checks.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use the realtime model only for the immediate spoken status question; use a cheaper background model for evidence reconciliation, postcondition checks, and retry readiness monitoring.
- **latency:** Speak an initial evidence state within 1–2 seconds from cached attestations; take up to 10 seconds for a fresh Mac/browser verification. Continue asynchronously when the owner leaves.
- **cost:** Low per query: mostly local probes and cached evidence; occasional background model call (roughly $0.01–$0.05 depending on the number of evidence sources). Realtime audio and TTS dominate immediate interaction cost.
- **security:** Evidence may include private screen/application state and authenticated page data, so keep raw screenshots and page content on the Mac/browser whenever possible and send only typed claims, hashes, timestamps, and capability status to the relay. Require confirmation before any retry that could duplicate an external side effect. Expire evidence quickly and clearly label unknown rather than infer success.
- **missing:** Cross-surface capability attestations with active-probe results, identity, freshness, and contradiction flags; A postcondition-verification protocol for Mac and authenticated browser actions, including typed evidence and idempotency keys; Relay-held pending verification records and owner-facing retry/readiness notifications; Pendant speech/status vocabulary for succeeded, not reached, uncertain, and verified-after-delay states


## Changes it proposed to its own stack

### `context` — Add a cross-surface capability-attestation record, produced by active probes rather than configuration: for each surface/action class store observedAt, probe method, host identity, permission result, reachability result, freshness TTL, and contradiction flags (for example grant cache says Accessibility=true while the running AI Pendant Agent fails a no-op input probe). The planner and action layer must consume this envelope and downgrade to observe/draft-only whenever attestation is missing, stale, or contradictory; receipts must carry the attestation ID so later perception can distinguish 'reported success' from 'reached the screen'.
- **owner gets:** The pendant will stop confidently claiming that it clicked or typed when macOS silently ignored the event. You get an honest spoken explanation ('I can see the app, but I cannot safely control it yet') and automatic recovery when the correct binary is granted permission, instead of lost work and untrustworthy action history.
- effort: Medium: shared schema plus probe scheduler, /observe and /ops integration, planner/action gating, receipt metadata, and dashboard display. No model training required.  ·  risk: A false-negative probe could unnecessarily block reversible work; recover with retry/backoff and an explicit owner-approved diagnostic. Never allow a stale positive cache to override a failed active probe.
- cost: Negligible API cost; a few local probe calls and small persisted JSON/D1 records.  ·  latency: ~100–500 ms for a fresh local attestation when needed; cached attestation avoids added latency within TTL.
- security: Improves safety by preventing UI actions under mismatched identity/permissions. Probe results reveal local process identity and should remain local/authenticated, not enter general model context unless task-relevant.
- depends on: A local no-op input probe that runs under the exact shipped AI Pendant Agent binary; Typed action receipts that can carry an attestation ID; Planner/action enforcement of observe-only degradation


## What it asked for

### `p3-elqi` (permission) — Grant macOS Accessibility and Screen Recording to the exact currently running binary identity com.aipendant.agent at /Users/evanliu/Applications/AI Pendant Agent.app (not a similarly named app), then restart/reprobe the agent; verify /observe inputReachability.status=ready and /ops/status permissions.ready=true.
- why: Live observation still proves UI actions cannot reach the screen, and receipts would be false. This blocks any safe computer-use capability.
- risk it sees: Granting these permissions gives the local agent broad screen/input access; keep it restricted to this signed app identity and retain the existing action approval/undo gates. Do not proceed if the binary hash or path changes unexpectedly.

