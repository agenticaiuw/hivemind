# Harness derivation — faculty-action — round 263

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live device reachability** — The live device inventory currently reports nrf9160-pendant offline (last seen 2026-08-09T02:56:31.366Z) while home-macbook-bridge is online (last seen 2026-08-09T03:49:55.073Z). Any proposal requiring live LTE pendant delivery remains untestable until registration; Mac-side orchestration is reachable.
  - evidence: discover(devices) live result in round 263

## Capabilities it proposed

### ""Send this to Alex, and make sure it actually went through.""
- **useful because:** This is the system's most valuable missing end-to-end behavior: one operation identity follows the owner's spoken request from pendant capture through relay planning, physical approval, Mac/browser execution, and independent postcondition verification. The owner gets a truthful verified/safe-to-retry/unknown result, not a claim based on an executor receipt. The operation record also joins the produced artifact (draft/message/file) to the originating request and records degraded source health, so a later status question can name exactly what was sent and why confidence is limited.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Use realtime only to parse the short request and announce status; use a cheaper background model for plan normalization and artifact-summary generation. Deterministic relay state machines, not a model, own approval, retries, correlation, and commit.
- **latency:** Acknowledge in under 1 second; stage for physical approval within 3 seconds; execute within 15 seconds; verification within 5 seconds. If the browser or Mac is stale, say so immediately rather than waiting.
- **cost:** Roughly $0.01–$0.05 per invocation depending on whether a background model summarizes the artifact; most cost is optional planning/summarization, not state transitions or verification.
- **security:** The pendant receives only an opaque operation nonce and a short risk summary, never message contents or credentials. Require the existing physical approval latch for external sends. The verifier is read-only and returns hash/minimal provenance by default. Expire approvals, refuse digest mismatch/replay, and make degraded source health visible. Never label an executor receipt as success without independent verification.
- **missing:** A durable operation↔artifact↔request correlation record shared by relay, Mac, and browser; A source-health/degraded receipt vocabulary carried into the final status; An orchestrator that calls the granted verify_operation_step for every commit step and persists its provenance; A dashboard/status query that can retrieve the joined record after interruption

### ""Move this task from my Mac to my iPhone and finish it there.""
- **useful because:** The owner can begin a task at a desk and hand it to the real phone without reconstructing the task. The system packages a redacted checkpoint (target, current step, and safe-to-share fields), asks for physical approval before any external submission, drives iPhone Mirroring through the Mac, then independently verifies the resulting app state. This makes the pendant, browser session, Mac, and phone one usable handoff rather than four isolated surfaces.
- **path:** pendant → relay → mac-planner → browser → ios → dashboard
- **model tier:** Realtime parses the handoff request; a cheaper background model summarizes and redacts the checkpoint. Deterministic adapters perform the iOS and browser actions; verification and approval remain state-machine operations.
- **latency:** Checkpoint preview in 3 seconds; approval prompt immediately; handoff execution under 20 seconds when both surfaces are online. If the phone is unavailable, retain a resumable checkpoint rather than pretending completion.
- **cost:** $0.01–$0.04 per handoff, dominated by optional checkpoint summarization; action execution and verification are local.
- **security:** Never copy passwords, payment data, or hidden form values into the checkpoint. Show the exact destination and fields to the pendant, require the existing physical approval latch for submission, expire checkpoints, and independently verify the phone's postcondition. A phone-unavailable or stale-mirroring state must be reported as blocked, not success.
- **missing:** A typed cross-surface checkpoint schema with redaction and expiry; An iOS Mirroring executor/receipt adapter exposed through the Mac agent; A handoff resume route that binds checkpoint ID to browser/app session identity; A verification adapter for iOS app state

### ""I pressed the bookmark button—later tell me what was happening at that moment.""
- **useful because:** A moment bookmark is currently just a timestamp/payload. This turns it into a useful memory: when the Mac reconnects, correlate the monotonic bookmark with the nearest captured conversation turn, foreground app, browser tab/session, calendar event, or active operation, and return a compact private context card. The owner can recover why they marked something without recording continuously or saving audio by default.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** No realtime model is needed at capture. A cheap background model may label the correlated context; deterministic time-window and operation joins do the primary work.
- **latency:** Bookmark acknowledgement under 300 ms locally. Context card within 30 seconds of Mac/relay reconnection; if sources are stale, return the bookmark with explicit missing-source reasons.
- **cost:** Usually under $0.01; background labeling is optional and dominates cost. Storage is a few hundred bytes per bookmark plus existing references, not an audio copy.
- **security:** Default to metadata and hashes, not transcript/audio. Keep the card private to the owner, apply source sensitivity labels, and require an explicit request to reveal message or page snippets. Never infer a precise location or timezone from the pendant's zoneless clock.
- **missing:** A durable bookmark↔context correlation key and bounded time-window semantics across pendant and Mac clocks; A source-health snapshot attached to each correlation attempt; A private retrieval/card route that can explain which sources contributed and which were unavailable; A policy for transcript/page snippet disclosure

### ""Handle this checkout, but do not show or say my payment details—just tell me the merchant, amount, and whether it succeeded.""
- **useful because:** The owner should be able to delegate sensitive transactions without turning the pendant, relay, or model into a holder of card numbers, passwords, or page secrets. The Mac/browser executes inside the already-authenticated session; the owner receives only a constrained transaction summary and a verified outcome. This is a practical privacy boundary, not merely an approval prompt: the system must prove that secret fields never crossed the model/device boundary and that the final amount and merchant came from fresh page state.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Realtime handles the short request and reads back only the merchant, amount, and risk class. Deterministic browser actions and redaction policy do the work; a small background model may normalize merchant names but must not receive secret fields.
- **latency:** Show a redacted transaction preview within 3 seconds, request the existing physical approval, and return a verified result within 15 seconds. If the page changes, authentication expires, or the amount cannot be independently read, stop and report unknown.
- **cost:** Usually below $0.02 per transaction; the dominant cost is optional merchant normalization, while redaction, field policy, and verification are local/deterministic.
- **security:** Secret form values must be write-only from the browser bridge and excluded from screenshots, logs, model context, receipts, and pendant payloads. Approval binds to merchant, amount, currency, and destination digest—not a vague 'continue'. Refuse changed totals, replayed approvals, unexpected redirects, or unverifiable success. Store only a salted transaction fingerprint and minimal provenance.
- **missing:** A browser-side secret-field classification and write-only fill primitive; A redaction contract enforced before browser snapshots, receipts, and model prompts; A transaction preview digest that binds merchant/amount/currency/destination to physical approval; An independent payment-result verifier that checks fresh browser state without exposing secrets; Audit proofs showing which fields were withheld rather than merely claiming they were


## What it asked for

_Nothing._
