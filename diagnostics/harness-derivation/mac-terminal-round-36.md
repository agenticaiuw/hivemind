# Harness derivation — mac-terminal — round 36

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-ui-execution-trust** — The Mac agent is online and FULL_CONTROL_MODE is enabled, but Accessibility is untrusted for the actual AI Pendant Agent binary and Screen Recording is missing. /observe explicitly says ui_click, ui_menu, type_text, and press_keys report success while doing nothing; existing receipts currently attach ok/status but have no execution-confidence field.
  - evidence: GET /observe at 2026-08-07T09:59:21Z: accessibility.trusted=false, eventsPost=false, uiActionsWillReachTheScreen=false, consequence says receipts cannot be trusted. GET /ops/status reports ready=false and screenRecording.granted=false.

## Capabilities it proposed

### "“Make sure that happened.” After any computer task, independently verify the visible result, tell me whether it really took effect, and if the Mac could not receive input, fix or retry only the uncertain part."
- **useful because:** Today the Mac can return a successful-looking UI receipt even when macOS rejects synthesized input from the running agent. The owner needs a dependable distinction between attempted and accomplished work, especially when they are away from the screen and relying on the pendant.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → dashboard
- **model tier:** Use realtime only to interpret the spoken request and report the result; use a cheaper background planner for verification/retry planning, with mac-vision only when visual confirmation is necessary.
- **latency:** Initial reachability/result check within 1 second after the action; visual verification within 5–10 seconds. Do not delay ordinary non-UI shell/API jobs unnecessarily.
- **cost:** Usually near-zero incremental model cost for structured postcondition checks; roughly $0.01–$0.05 when a vision verification frame and background reasoning are required. The dominant cost is image analysis, not telemetry.
- **security:** Screen images may contain private data and should remain on the Mac unless the owner has already enabled vision upload. Spoken results must say 'unverified' rather than claim success. Retrying should be limited to explicitly uncertain steps and preserve the original receipt; mutations still follow the owner's existing maximum-access policy.
- **missing:** A typed postcondition contract for each UI action (expected app/window/text/state), rather than checking only that dispatch returned.; Mac executor fields for input reachability and permission state at action start/end.; A verification adapter that can use accessibility state, app/API queries, or local screenshots without falsely treating dispatch success as completion.; A retry operation addressing only unverified action IDs, with stable idempotency keys.; Relay/pendant wording and dashboard rendering for verified, unverified, and failed outcomes.


## Changes it proposed to its own stack

### `mac-harness` — Add a non-blocking execution-confidence envelope to every Mac action and relay receipt. At dispatch, snapshot /observe permission and reachability state; tag UI-mediated actions (click/menu/type/keys and vision loop steps) as verified, unverified, or not-applicable. If Accessibility/input reachability is false, preserve FULL_CONTROL_MODE and still execute, but mark the result unverified with the exact cause, affected steps, and a recovery hint; never emit a plain successful receipt for an action that could not reach the screen. Propagate the envelope through GET /jobs, /jobs/:id/receipts, /ops/snapshot, and the pendant completion message. When reachability later recovers, offer an explicit retry of only unverified action IDs, while stable IDs and existing receipts prevent replaying verified steps.
- **owner gets:** The owner will stop hearing 'done' when nothing happened on screen. They get an honest spoken/dashboard result such as 'I attempted it, but macOS rejected input from AI Pendant Agent; nothing is verified,' plus a one-tap or spoken retry after permissions are fixed. This adds truth without taking away the owner's deliberate maximum-access policy.
- effort: Medium: centralize pre/post reachability sampling in executor.js, extend actionReceipts schema and relay serialization, add unverified-step retry endpoint, and cover permission-failure tests. No approval gate or command restriction is introduced.  ·  risk: A transient permission probe failure could over-label a genuinely completed UI action as unverified; retain raw result, timestamps, and before/after observations, and allow retry only for explicitly unverified IDs. Non-UI shell/API actions remain unaffected. Existing jobs need a backward-compatible 'confidence: unknown' default.
- cost: Negligible API cost; a small local probe per action and a few receipt fields. Storage increases minimally per receipt.  ·  latency: Tens of milliseconds for pre/post observation; no extra model round trip. Retry remains user-initiated or planner-selected after state recovery.
- security: Improves auditability and prevents false claims; it does not narrow FULL_CONTROL_MODE, add confirmations, or expose new secrets. Permission details should be summarized rather than leaking paths/fingerprints to the relay.
- depends on: chg-5fc73ce3 receipt/undo implementation; /observe permission and inputReachability telemetry; relay job and pendant completion serializers


## What it asked for

_Nothing._
