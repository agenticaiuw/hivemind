# Harness derivation — faculty-action — round 25

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac action execution truth** — The Mac local agent is online and full-control configured, but Accessibility is not trusted for the running AI Pendant Agent binary; synthesized events are rejected and UI actions cannot be trusted. Screen Recording is also absent. Browser bridge home-chrome is offline with 3 pending commands.
  - evidence: GET /observe at 2026-08-07T10:09:21.699Z and GET /ops/status: trusted=false, eventsPost=false, uiActionsWillReachTheScreen=false, screenRecording=false, browser online=false, pendingCommands=3.

## Capabilities it proposed

### "After you change something on my Mac or in a logged-in website, prove that it actually took effect and tell me if it didn't."
- **useful because:** A successful API response is not proof that a click reached the screen or that a private web transaction persisted. This gives the owner a trustworthy outcome instead of a misleading completion message, especially when Accessibility or the browser bridge is unavailable.
- **path:** faculty-judgement plans the intended reversible change and its expected postcondition → faculty-action dispatches to mac-planner/mac-vision or browser-extension with an idempotency key → faculty-perception independently re-reads the relevant Mac state or authenticated page and compares it with the expected postcondition → relay-realtime delivers a concise spoken result on the pendant; the Mac keeps the cited evidence and retryable job record
- **model tier:** background for planning and evidence comparison; deterministic checks first (receipt status, file hashes, UI accessibility state, page extraction), escalating to planner only when the postcondition is semantic or ambiguous. Realtime is used only to converse with the owner.
- **latency:** For local reversible actions, 1–3 seconds. For authenticated browser verification, up to 10 seconds; if the bridge is offline, say queued/unverified rather than spending repeated calls.
- **cost:** Usually no model call for deterministic checks; about $0.001–$0.01 for an ambiguous background comparison, dominated by page/UI evidence tokens. No screenshot upload unless the owner explicitly allows it.
- **security:** Verification must use the same scoped tab/session and avoid exposing private page content in relay speech. Never claim verified from an API acknowledgement alone. Irreversible actions still require the existing owner approval policy; this capability verifies effects, it does not authorize them.
- **missing:** A typed postcondition/verification contract attached to each action plan; A faculty-perception verification endpoint that can read Mac state and authenticated browser evidence; Cross-node correlation of action idempotency key, before/after evidence, and final receipt; The browser bridge must return stable extraction evidence when it comes back online

### "Prepare the change, and when I press the button on my pendant, carry it out—even if the voice connection has dropped."
- **useful because:** The owner can currently prepare work conversationally but cannot provide a reliable, local final authorization when the network or voice session disappears. A physical pendant press gives a clear last-mile signal without opening a microphone, while preventing a stale or replayed request from executing later.
- **path:** faculty-judgement creates a bounded, reversible transaction with an exact action hash, expiry, and expected target → relay stores the encrypted pending transaction and delivers a one-time challenge to the pendant → pendant firmware displays a short confirmation cue and turns the button press into a locally signed nonce response → relay validates the nonce and forwards the transaction to mac-planner or browser-extension → faculty-action executes with idempotency, then faculty-perception verifies the resulting state and sends a compact success/failure receipt back to the pendant
- **model tier:** Deterministic protocol and action execution; use the background tier only to summarize the prepared transaction or resolve an ambiguous postcondition. Realtime is not required once the transaction is prepared.
- **latency:** Button acknowledgement under 250 ms locally; relay-to-Mac execution normally under 5 seconds. An expired or disconnected transaction should fail closed and remain visibly pending rather than execute later.
- **cost:** Near-zero model cost for the protocol; approximately $0.001–$0.01 only when semantic postcondition verification needs a background model. Storage and relay traffic are negligible per transaction.
- **security:** The signed response must bind to transaction hash, target session/tab, expiry, and a single-use nonce. Do not put private page contents on the pendant. Require a deliberate long-press or two-step button gesture for high-impact actions, and show a distinct failure cue when the relay cannot confirm execution.
- **missing:** Pendant firmware support for a local confirmation challenge and signed one-time response; A relay transaction escrow with expiry, nonce replay protection, and delivery receipts; A shared transaction hash/idempotency protocol accepted by Mac and browser executors; A pendant-to-relay authenticated pairing key and a user-visible pending/expired state


## Changes it proposed to its own stack

### `mac-harness` — Make every Mac action receipt reachability-aware and evidence-graded. At dispatch, attach the current /observe snapshot (Accessibility trusted, eventsPost, uiActionsWillReachTheScreen, Screen Recording, browser-online/session state). For UI actions, if uiActionsWillReachTheScreen is false, mark the step attempted_unverified rather than success, preserve the exact reason and affected step range, and require a later verified re-run to close the job. For browser actions, distinguish queued, bridge_offline, executed, and result_verified. Never let a syntactically successful API response overwrite an unverified physical outcome; expose a compact receipt suitable for pendant speech and a detailed audit record.
- **owner gets:** Today the agent can say it completed a click or typed text even though macOS reports synthesized events do not reach the screen. The owner gets an honest answer immediately, knows exactly what needs fixing, and can safely retry later instead of trusting a false completion.
- effort: Medium: central receipt schema plus pre/post observation capture, status transitions, tests for inaccessible UI and offline browser, and relay speech formatting.  ·  risk: Some existing jobs will appear less successful because false positives become attempted_unverified; recover by retaining raw responses and offering explicit retry after permissions/bridge return. Observation itself is read-only.
- cost: Negligible API cost; a small local JSON receipt and one read-only observation call per UI job/step batch.  ·  latency: Adds roughly 50–150 ms for local observation; no model call required.
- security: Improves safety and auditability. Snapshots should exclude window contents/URLs unless already part of the action receipt; do not upload screenshots or page text.
- depends on: A stable typed receipt schema shared by /execute, jobs, and relay completion messages; The existing /observe endpoint and inputReachability probe; A retry/continuation endpoint that preserves idempotency keys


## What it asked for

_Nothing._
