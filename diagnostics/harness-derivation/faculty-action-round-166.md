# Harness derivation — faculty-action — round 166

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Handle this whole thing across my Mac and browser, but if any step fails or becomes uncertain, stop safely, tell me exactly where, and let me resume without starting over.”"
- **useful because:** Turns the system from a sequence of brittle clicks into a recoverable transaction: it can perform a multi-step job across browser sessions and Mac apps, verify each postcondition, pause on ambiguity, and resume after a link drop or owner decision. The owner gets honest progress instead of a confident but false 'done'.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Use the low-latency model only for interpreting the spoken request and safety boundary; use a cheaper background planner for the step graph, and deterministic executors/verifiers for each step.
- **latency:** Acknowledge in under 1 s; execute ordinary steps within 2–10 s each; pause immediately on an unverified step and speak the blocking reason.
- **cost:** Usually one realtime turn plus low-cost planner/verifier calls; API spend is dominated by screenshots or page snippets, so default to structured browser/app state and hashes.
- **security:** Persist only opaque step IDs, action parameters, and verification hashes; never put credentials or page secrets in the pendant. Irreversible steps require the existing physical transaction approval latch. Recovery must never replay a completed side effect; unknown outcomes remain unknown until independently checked.
- **missing:** A durable saga/step-state store with idempotency keys and explicit unknown state; Executor receipts correlated to verify_operation_step evidence; Compensation or operator-choice metadata for steps that cannot be undone; A resume command exposed to the pendant and dashboard

### "“Read my newest messages, tell me which ones actually need me, draft replies for the rest, and only send after I approve each one on the pendant.”"
- **useful because:** This is a daily high-value use of every surface: browser sessions and Mac apps can reach messages the relay cannot, the model summarizes and drafts, and the pendant supplies a deliberate, secret-free send approval. It reduces inbox burden without silently speaking for the owner.
- **path:** pendant → relay → mac-planner → browser → mac-vision → dashboard
- **model tier:** Cheap background model batches and ranks messages; realtime model is used only for the owner's spoken clarification and final approval prompt; deterministic browser/Mac actions send only approved drafts.
- **latency:** First digest in 5–15 s; each draft in under 3 s after selection; send confirmation should be under 1 s after the physical gesture.
- **cost:** Low to moderate: one batch summarization call and small per-draft generation; browser inspection text, not screenshots, keeps token cost down.
- **security:** Drafts may contain private correspondence, so keep content on the Mac/browser path and send only a redacted summary plus draft digest to the relay. Never transmit passwords or full inbox dumps to the pendant. Each send needs a nonce-bound physical approval and fresh browser-field verification of recipient, body, and thread immediately before submission.
- **missing:** A message-provider adapter for Mail and authenticated webmail with a common message/draft schema; Per-message approval queue with expiry and recipient/body digest; A private local summarization route that avoids relaying message contents; Post-send verification and an undo window where the provider supports it

### "“Let every device see only the smallest proof it needs: let the Mac and browser do private work locally, and tell me what happened without sending my private data through the relay.”"
- **useful because:** The owner gets a genuinely private hive: authenticated facts, digests, and redacted summaries can cross surfaces while message bodies, credentials, files, and page contents stay on the Mac or browser. This enables useful coordination without making the relay a copy of the owner's life.
- **path:** pendant → relay → mac-planner → browser → mac-vision → dashboard
- **model tier:** Use deterministic local policy and redaction first; use a cheaper model on the Mac for classification/summarization; reserve realtime reasoning for the owner's live question. The relay should route signed claims, not raw private context.
- **latency:** Local disclosure decision under 100 ms; spoken answer within 1–2 s; never wait on a cloud model when a local deny policy can decide.
- **cost:** Lower than current screenshot/transcript-heavy workflows because only compact claims and selected snippets leave the Mac; occasional local model inference dominates.
- **security:** A claim must carry issuer, audience, scope, expiry, sensitivity, and a content digest. Default deny, no wildcard scopes, no raw secrets in logs, and visibly tell the owner when a request was refused or redacted. Browser content must not be exfiltrated merely because a planner asks for it.
- **missing:** A capability-scoped claim/envelope format shared by relay, Mac, browser, and pendant; A local disclosure policy engine with redaction and deny-by-default behavior; Route-level sensitivity labels and log scrubbing; A spoken/dashboard explanation of what data crossed the boundary

### "“Before you change anything important, make me a reversible checkpoint; if I regret it, restore the exact prior state instead of just telling me how to undo it.”"
- **useful because:** The owner gets a safety net for real-world actions, not merely an approval prompt. The system snapshots the minimum restorable state before an approved mutation, tests the rollback while possible, and offers a time-limited spoken 'restore that' command from the pendant.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Use deterministic snapshot/restore adapters and cheap background validation; realtime is only for interpreting the owner's restore request and confirming scope.
- **latency:** Checkpoint preparation under 2 s for supported objects; restoration begins within 1 s of physical confirmation and reports verified/unknown honestly.
- **cost:** Low API cost; storage and provider-specific rollback adapters dominate. Keep snapshots encrypted, deduplicated, and automatically expired.
- **security:** Never claim reversibility where the provider cannot guarantee it. Checkpoints may contain private data, so encrypt locally and bind restore tokens to the exact object, owner, and expiry. Restoring messages, payments, or shared documents needs the existing physical approval latch.
- **missing:** Provider-specific snapshot and restore adapters with capability declarations; Encrypted local checkpoint store and retention/expiry policy; A preflight that proves a rollback path exists before mutation; A restore verifier and explicit irreversible-action warning


## Changes it proposed to its own stack

### `integration` — Make the physically connected nRF9160 pendant usable today as a first-class USB-tethered wearable session: the Mac bridge should discover the pendant's serial endpoint, negotiate capabilities, forward button/audio/event frames to the relay, and return downlink audio and compact status cues. Maintain an explicit tethered-vs-LTE transport state, sequence numbers, bounded buffering, and reconnect/resume receipts; do not claim LTE availability.
- **owner gets:** The owner can wear and use the actual pendant while it is attached to the Mac now, rather than waiting for LTE registration. A button press and spoken request can reach the same mind, and replies can play through the verified 24 kHz bridge path with truthful connection status.
- effort: Medium: serial framing and device discovery, relay session binding, reconnect tests, and a small status surface. No firmware flash is required for an initial bridge implementation.  ·  risk: USB disconnects, partial frames, stale session ownership, or duplicate audio/events could cause missed or repeated actions. Recover with CRC/sequence numbers, idempotent event IDs, bounded queues, and an explicit 'not delivered' cue; never silently fall back to an unregistered LTE assumption.
- cost: Negligible API cost beyond normal voice turns; approximately $0 hardware because both chips and USB links already exist.  ·  latency: Adds roughly 5–30 ms serial/bridge overhead; reconnect may take seconds but should be visible.
- security: Bind the serial device by stable identity, encrypt/authenticate the relay session, and do not expose raw serial commands to browser content. Tether mode must not grant action approval by itself.
- depends on: A stable serial framing contract for nRF9160↔Mac and ESP32↔Mac; A relay session transport enum that distinguishes USB tether from LTE; The existing /pipeline/audio and /pipeline/events correlation fields

### `hardware` — Add a pendant-resident secure element with a hardware-unique signing key and monotonic anti-rollback counter, and make the Mac bridge verify signed device attestations before accepting button events, audio session binding, or action receipts. Keep the existing physical approval latch as the human-consent mechanism; this adds device identity and tamper/replay resistance rather than another approval gesture.
- **owner gets:** The owner can trust that a nearby USB device or replayed serial packet cannot impersonate their pendant, inject a fake button approval, or attach a conversation to the wrong Mac session. It makes the wearable a real security boundary instead of just another serial peripheral.
- effort: High: select and fit a secure element, update the pendant and bridge protocols, provision keys safely, add rotation/recovery, and validate behavior across reset, battery loss, and reconnect. Requires a hardware revision or an external secure-element daughterboard.  ·  risk: Lost or failed hardware could lock the owner out; provision a recovery ceremony requiring the owner and never export private keys. Counter wear and clockless expiry need careful design. Existing un-attested boards must enter a clearly limited read-only/development mode.
- cost: Approximately $1–5 per device for a secure element plus board/layout and provisioning work; negligible runtime power compared with the radio/audio path; no meaningful per-request API cost.  ·  latency: Usually sub-millisecond signature verification locally; a few milliseconds during session establishment and receipt validation.
- security: Strongly improves anti-spoofing and replay resistance, but introduces key lifecycle and recovery obligations. The relay should receive attestations and signatures, never private keys.
- depends on: A canonical signed event/receipt envelope shared by firmware, Mac bridge, and relay; A stable device identity registry and key-rotation/recovery procedure; The existing physical transaction approval latch and explicit USB-vs-LTE transport state


## What it asked for

_Nothing._
## Its own summary

Discovered the live surfaces: Safari is online, the Mac bridge is online, and the mobile/LTE device is offline. The physical pendant is therefore useful today only through a USB-tethered path, not LTE. I recorded three concrete proposals: (1) recoverable cross-surface action sagas that stop on unknown and resume idempotently, (2) private message triage with per-draft pendant approval and fresh send verification, and (3) first-class USB-tethered pendant sessions with explicit transport state and reconnect receipts. Still needed: a durable saga/step-state and idempotency layer, provider adapters and private local message processing, and a tested serial framing/session contract between the connected nRF9160, ESP32 bridge, Mac, and relay. I also warned faculty-judgement that the saga is close to existing verified-action work and should be treated as an amendment rather than a duplicate primitive.

**Biggest unknown:** The exact serial protocol and stable device identity exposed by the physically connected nRF9160 pendant are still unknown; without that, USB tethering can be specified but not honestly implemented or tested end to end.

