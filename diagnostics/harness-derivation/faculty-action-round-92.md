# Harness derivation — faculty-action — round 92

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **reachable devices** — The Mac bridge is online, but home-chrome is offline with zero tabs and no pendant is connected. Therefore action verification can currently be implemented/tested on Mac files, AppleScript apps, and the browser bridge only when Chrome returns; pendant-side offline confirmation cannot be validated.
  - evidence: discover:devices returned home-macbook-bridge online last seen 2026-08-07T13:38:35.909Z, home-chrome offline 0 tabs, and no pendant entry.

## Capabilities it proposed

### "Make sure that happened, and tell me if it didn't."
- **useful because:** Today an action receipt reports what the executor attempted, not independent proof that the external state changed. This gives the owner a trustworthy spoken result: the Mac performs the reversible action, perception re-reads the target, and the relay keeps retrying or reports the exact failure instead of claiming success. It is specifically useful when the owner is away from the screen and wearing the pendant.
- **path:** pendant → relay-realtime → faculty-judgement → faculty-action → mac-planner → mac-vision → faculty-perception → dashboard
- **model tier:** Use the realtime tier only for the pendant's short confirmation; use the cheaper local planner/vision and deterministic observation routes for execution and verification, with relay background retries.
- **latency:** Initial action acknowledgment under 1 second; verification within 3 seconds for app/file/browser state, with background retry up to 2 minutes for delayed effects.
- **cost:** Usually one local Mac action plus one local observation, near-zero external API cost; model cost only when semantic GUI interpretation is needed. Background retries should use the cheaper tier.
- **security:** Verification may read private app/browser state and must remain bearer-authenticated. Never infer success from HTTP 200 alone. For send/delete/purchase actions, verification is evidence only and the existing confirmation gate remains mandatory. Surface before/after fields and a confidence level in the receipt.
- **missing:** A verify_operation_step tool or equivalent authenticated observation endpoint that accepts the action's expected postcondition and returns observed evidence; A durable job state for pending verification/retry and an explicit distinction between attempted, verified, contradicted, and unknown; Pendant-safe spoken/error signaling when verification fails offline

### "When I tell you to do something later, do it when I am actually at the right place and device—not merely at a clock time—and tell me if the opportunity passed."
- **useful because:** The owner can make decisions while wearing the pendant away from the Mac, but today the system cannot safely defer an action until the physical and digital context makes it appropriate. This would turn an intent into a context-sensitive handoff: the relay holds it, the pendant supplies presence/button confirmation, and the Mac/browser executes only when the owner is at the intended workstation or site.
- **path:** pendant → relay-realtime → faculty-judgement → faculty-action → faculty-perception → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use the realtime model only to capture and clarify the intent. Use deterministic relay rules and a cheaper background model to evaluate context and select the execution surface; use the local Mac planner only at execution time.
- **latency:** Capture immediately; evaluate context on device events or a low-frequency heartbeat; execute within 5 seconds after the required context appears. Expire or ask again at the owner's stated deadline.
- **cost:** Low: mostly event matching and local observations; occasional cheap model call to resolve ambiguous context. No continuous realtime inference is needed.
- **security:** A deferred intent may contain private account or location context. Encrypt it at rest, retain only until completion/expiry, and expose a visible pending-intent list. Require explicit confirmation for sends, purchases, deletion, or physical-risk actions even when context matches. Never use inferred location as sole authorization.
- **missing:** A pendant-to-relay presence/context event stream (BLE proximity, button event, and connection state with timestamps); A durable conditional-intent state machine with predicates, expiry, cancellation, and exactly-once handoff; Mac and browser observations normalized into context facts such as active user session, focused workspace, network, and authenticated tab; A cross-surface pending-intent UI and pendant indication that an intent is waiting or has expired


## Changes it proposed to its own stack

### `mac-harness` — Add a postcondition verifier between action receipts and perception: every reversible action may carry a typed expectedState (file hash/exists, app frontmost, reminder presence, browser URL/text fingerprint, volume level). After dispatch, the local agent runs a fresh independent observation, stores before/after evidence and observedAt in the receipt, and classifies verified, contradicted, or unknown. A durable retry worker re-observes delayed effects without replaying the action; relay_job_status and the pendant receive the classification rather than treating executor success as completion.
- **owner gets:** When the owner says “do it,” they get an honest answer about the world, not merely that a command returned successfully. It prevents silent failures and duplicate side effects when an app is slow or a browser tab changes.
- effort: Medium: typed postcondition schema, observers for file/app/browser/reminder, receipt fields, retry state machine, and dashboard/spoken rendering; no Accessibility required for file, AppleScript, and browser-bridge observations.  ·  risk: A stale or overly broad postcondition could produce unknown/false contradiction; default to unknown and never retry the side effect. Recover by showing evidence and allowing a deliberate re-check. Browser/account reads remain private and authenticated.
- cost: Negligible storage for bounded evidence and no meaningful API cost; semantic GUI verification may use one cheaper local-model call.  ·  latency: Adds roughly 100–800 ms for deterministic checks; delayed effects move to background verification.
- security: Receipts may contain private URLs, snippets, and file hashes; redact content by default, retain only typed evidence unless the owner asks for detail.
- depends on: Existing actionReceipts.js and GET /jobs/:jobId/receipts; An implementation of the pending verify_operation_step tool or equivalent local-agent verifier; Perception contract defining evidence freshness and confidence

### `hardware` — Add a low-power BLE central/peripheral presence channel to the pendant product, with a locally authenticated rolling token and a small nonvolatile pending-intent journal. Firmware emits signed connect/disconnect/proximity events to the relay and uses the existing single LED plus button to expose waiting, ready, expired, and confirmation-required states. Keep the audio/I2S path unchanged; this is a separate control-plane feature, not an audio-path assumption.
- **owner gets:** The pendant can tell the system that the owner is really back at the intended Mac or has deliberately returned to an action, so deferred work happens at the right moment instead of firing while they are away or silently expiring.
- effort: Hardware revision or validated BLE-capable radio firmware, secure pairing/token rotation, a small event protocol, and relay persistence; prototype first with the existing radio if its firmware supports authenticated advertising, otherwise add a sub-$5 BLE beacon/SoC.  ·  risk: False proximity could release an intent too early, and a lost pendant could leave work waiting. Use proximity only as a readiness signal, never sole authorization for irreversible actions; require the button for those. Expire journals and provide cancellation from the dashboard. Recover with explicit pending/expired state.
- cost: Prototype firmware cost is low; a new beacon/radio component is roughly $3–8 in volume and tens of milliwatts only during brief scans/advertisements, with a small battery-life impact.  ·  latency: Presence transitions can be detected in roughly 1–5 seconds depending on scan interval; no impact on conversational audio when scheduled outside I2S handling.
- security: Pairing identifiers and intent metadata must be encrypted/authenticated; avoid broadcasting owner identity or task text. Rotate tokens and reject replayed events.
- depends on: Conditional-intent relay state machine; Authenticated pendant event ingestion; A cross-surface pending-intent display and explicit confirmation path


## What it asked for

_Nothing._
