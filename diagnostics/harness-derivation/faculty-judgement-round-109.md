# Harness derivation — faculty-judgement — round 109

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“That’s not what I meant—fix the last thing you did.”"
- **useful because:** Today an action receipt can tell the owner what happened, and some individual jobs can be undone, but a human correction often means “change the parameter” rather than simply reverse it. This gives the owner a spoken, cross-surface repair path: identify the referenced recent action, explain the proposed patch, and apply the smallest safe correction instead of forcing them to reconstruct the original workflow.
- **path:** pendant → relay → mac-planner → browser-extension → mac-vision → dashboard
- **model tier:** Realtime for resolving the short spoken correction and selecting the recent receipt; a cheaper background model can compile and verify the patch. Execution remains deterministic on Mac/browser, with relay retaining the journal.
- **latency:** Acknowledge in under 1 second; show/speak the proposed repair within 5 seconds; execute reversible repairs within 15 seconds. Irreversible or ambiguous repairs stop for explicit confirmation.
- **cost:** Roughly $0.005–$0.03 per repair depending on whether semantic interpretation needs the realtime tier; most cost is receipt/context retrieval and any screenshot or page extraction, not deterministic execution.
- **security:** Only recent owner-scoped receipts and the minimum related page/file context leave the device. Never infer authorization from the correction alone: sending, deleting, purchasing, or changing external records requires confirmation. Keep before/after values, tab URL, file path, and an undo token; redact secrets from the spoken response and dashboard.
- **missing:** A durable cross-surface transaction journal that links Mac actions, browser mutations, and spoken intent under one repairable operation id; A semantic patch compiler that can turn “make it Tuesday instead” into a typed before/after change and reject unsupported repairs; A single confirmation/undo protocol shared by browser and Mac executors; Pendant delivery of a concise repair preview plus a local stop gesture

### "“I lost my pendant. Lock it now, keep my information safe, and let me continue from my Mac without losing my place.”"
- **useful because:** A wearable is uniquely exposed to loss, theft, or being left in a room. Today continuity and revocation are separate infrastructure concerns: the owner cannot quickly invalidate the missing device while preserving legitimate work context. This makes loss a recoverable interruption rather than a privacy emergency and prevents an attacker holding the pendant from replaying queued audio, invoking actions, or learning private context.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Realtime only for the owner's short loss report and immediate acknowledgement; deterministic relay security code performs revocation. A cheaper background model can assemble a redacted continuity packet on the Mac after the lock is complete.
- **latency:** Remote lock acknowledgement under 2 seconds when the relay is reachable; queued local lock takes effect on the pendant's next wake or button event. Mac continuity packet available within 30 seconds.
- **cost:** Under $0.01 per incident; dominated by one authenticated relay request and optional local context summarization. No recurring model cost.
- **security:** Revocation must require a second factor or an already-authenticated Mac session, otherwise anyone who hears the wake phrase could cause denial of service. Immediately invalidate device tokens, cancel pending audio/action deliveries, erase volatile audio and sensitive cache, quarantine queued jobs, and rotate session keys. Do not copy secrets into the continuity packet; show exactly what was retained and for how long. Require explicit confirmation before re-pairing a replacement pendant.
- **missing:** A device identity and key lifecycle service with remote revoke, rotation, replacement pairing, and replay protection; A pendant firmware panic/revocation state that survives reboot and refuses cached commands offline; A relay-wide kill switch for pending audio, browser, and Mac jobs scoped to one device identity; A redacted continuity export that transfers only active task state to the authenticated Mac, with audit receipts and expiry


## Changes it proposed to its own stack

### `integration` — Create a cross-surface repair journal and semantic patch protocol. Every Mac/browser mutation and spoken request receives one operationId, stores typed before/after state plus provenance and an inverse or compensating action, and exposes PATCH /operations/:id/repair that accepts a constrained patch (field, old value, new value). The relay resolves “that last thing” to a candidate operation, the model may only fill the patch schema, and executors reject stale before-values or non-invertible actions. Return a preview and one-tap/pendant confirmation, then append the result as a new receipt.
- **owner gets:** When the assistant gets something slightly wrong, the owner can correct it naturally instead of manually undoing, reopening the right app, and repeating the whole task. Stale or dangerous changes fail visibly rather than silently overwriting newer work.
- effort: Medium-high: shared operation schema and journal, adapters for existing Mac/browser receipts, patch validation, relay endpoint, and dashboard/pendant preview.  ·  risk: Some actions have no safe inverse or external state may change; stale-value checks and confirmation are required. Recovery is to leave the original receipt untouched and provide a manual next step if repair is unsupported.
- cost: Negligible storage/compute; occasional low-cost model call for spoken correction. Screenshot/page extraction can dominate browser repairs.  ·  latency: Adds 1–3 seconds for candidate resolution and before-state validation; deterministic repairs remain within one job round trip.
- security: Improves auditability but centralizes sensitive before/after values. Encrypt journal fields, apply short retention, redact secrets, and enforce owner/job scoping.
- depends on: The existing receipt/undo implementation must expose stable operation IDs and typed before/after fields.; Browser command queue must return typed mutation receipts rather than only success/failure.; Owner confirmation and universal stop behavior must be wired into the shared executor.

### `firmware` — Add a persistent device-identity lifecycle to the pendant: hardware-backed device key, short-lived relay credentials, signed revocation epochs, and a local REVOKED mode stored in a tiny protected flash record. Every queued command and audio delivery must carry the device epoch; firmware rejects old epochs after reboot and zeroes volatile audio/context buffers on revocation. Replacement pairing requires a challenge approved from an authenticated Mac session plus a physical button gesture.
- **owner gets:** If the pendant is lost, the owner can make it harmless remotely without losing their active work, and a replacement can be paired without handing over their whole account. Stale queued commands cannot come alive later when the missing device reconnects.
- effort: High firmware/relay/security work: key provisioning, epoch propagation through jobs and audio, protected flash handling, recovery UX, and adversarial testing for offline and replay cases.  ·  risk: A false revocation or lost second factor could strand the owner. Provide a clearly documented recovery code stored outside the pendant and a Mac-only recovery flow; keep revocation idempotent and auditable.
- cost: Negligible per-request API cost; modest flash writes and roughly tens of bytes of protected state. Hardware-backed key support may add $1–$4 BOM if the chosen production MCU lacks a secure element.  ·  latency: One signature/epoch check per command, typically under milliseconds; remote lock remains relay-latency bound.
- security: Substantially reduces blast radius of pendant loss, but makes key provisioning and recovery high consequence. Never log private keys or recovery codes; rate-limit pairing and revoke all prior epochs on replacement.
- depends on: A relay device-identity registry and remote revocation endpoint.; Consistent device epoch fields in queued jobs, audio packets, and browser/Mac delivery receipts.; An authenticated Mac second-factor flow and owner-facing recovery-code storage.


## What it asked for

_Nothing._
## Its own summary

I found and recorded one genuinely new connective capability: a cross-surface repair journal and semantic patch protocol. It lets the owner say “that’s not what I meant—fix the last thing,” validates typed before/after state across Mac and browser actions, previews the smallest safe correction, and preserves an audit/undo chain. The production 24 kHz hardware redesign was already in the backlog, so I did not duplicate it. Still-needed inputs are the authoritative audio acceptance criteria and the actual cross-surface persistence/journal primitives; both are already pending upstream, so I did not re-request them. Browser work also remains honestly blocked until the owner enables the denied Accessibility/Screen Recording and reconnects the bridge; no agent-side grant can fix that.

**Biggest unknown:** Whether the newly granted implementation work has actually landed in the live relay (the granted category is empty this round), especially durable operation IDs and typed before/after receipts needed to implement repair safely.

