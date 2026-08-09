# Harness derivation — unified — round 248

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live capability resolution** — The granted audio_link_fault_inject capability is not callable against the live inventory: its 5% SWB fault test resolved to nothing, with nearest real routes GET /audio-retention and POST /pipeline/audio. The audio validator also requires an explicit pipeline ID and did not run when omitted.
  - evidence: audio_link_fault_inject returned resolution=unresolved; audio_pipeline_validate returned invoked=false, why pipelineId required.

## Capabilities it proposed

### "“Finish the checkout I started in Safari, but do not submit until I approve it on the pendant.” Then, after I hold the approval button, submit exactly the staged order and tell me what happened."
- **useful because:** This is the single most useful cross-surface action: the pendant supplies deliberate consent, the browser supplies the authenticated checkout session, the Mac executes only the bound plan, and the relay preserves the handoff if one surface drops. It prevents both silent no-ops and accidental purchases.
- **path:** pendant → relay → browser → mac-bridge → dashboard
- **model tier:** Realtime for the short spoken summary and confirmation readback; deterministic planner/executor for checkout inspection and submission; background model only for extracting a concise receipt from page evidence.
- **latency:** Stage in under 5 s; physical approval should be reflected in under 2 s; submit and receipt in under 10 s. If any surface is offline, retain the staged plan rather than retrying a purchase.
- **cost:** ~$0.01–$0.05 per invocation, dominated by one planner/readback pass; browser inspection and deterministic execution dominate latency, not model tokens.
- **security:** Never send card numbers or page secrets to the relay/model. Bind a plan digest, target tab/session, merchant, amount, cart hash, expiry, and world fingerprint; require the pendant nonce and reject any page or price change. Store redacted receipts, not checkout contents. Submission, messages, and other irreversible actions require the physical approval; cancellation must be possible before expiry.
- **missing:** Relay persistence and delivery for the existing physical_transaction_approval_latch staged nonce; the approval readback path is currently not completable.; A browser transaction adapter that exposes merchant/cart/total as typed fields and refuses unbound navigation.; A real submit-and-receipt coordinator joining browser result, Mac job receipt, and pendant approval; existing approval currently has no production caller.; Orchestrator closeLedger and relay job leases before safe outage recovery can be enabled.

### "“Is this browser page safe to act on? Read the relevant details to me, identify what would change or be sent, and do not click anything.”"
- **useful because:** A wearable owner can get a compact, non-mutating safety review of an authenticated page without handing control to an opaque model. It makes the browser useful for high-consequence decisions while preserving the physical approval boundary for any later action.
- **path:** pendant → relay → browser → mac-bridge
- **model tier:** Background model extracts and summarizes page claims; deterministic browser inspection and redaction enforce the target-tab binding; realtime model speaks only the final short assessment.
- **latency:** Snapshot and spoken answer in 3–6 s. Never wait indefinitely for a browser bridge; return a stale/unknown verdict with timestamp and tab identity.
- **cost:** ~$0.005–$0.03 per review, dominated by page extraction and one summarization pass.
- **security:** Read-only by construction: no click, type, navigation, or submit actions. Bind to an exact tab/session and capture timestamp; redact passwords, tokens, payment fields, and unrelated tabs. Clearly label model inference versus page evidence and require a separate staged transaction flow for any action.
- **missing:** A typed browser-inspection route returning page title, origin, forms, outbound destinations, monetary totals, and destructive controls without raw secrets.; A provenance-preserving risk schema with evidence spans and freshness timestamps.; Pendant speech/UI for uncertainty and a one-tap path to stage (not execute) a reviewed action.; Browser identity attestation remains unavailable, so tab binding must use the existing session/URL constraints until that grant exists.

### "“Before you submit anything from my browser, read me the exact fields and destinations that will be sent, compare them with what I approved, and stop if even one changed.”"
- **useful because:** A merchant total can remain unchanged while the address, subscription flag, recipient, or outbound destination changes. This gives the owner a concrete, spoken diff at the last responsible moment, rather than trusting a stale screenshot or a generic approval nonce.
- **path:** pendant → browser → relay → mac-bridge → dashboard
- **model tier:** Deterministic extraction and canonicalization for form fields, origin, destination, and amount; background model only converts the diff to plain speech; realtime tier reads the final diff and refusal.
- **latency:** Final diff within 2 s of the submit attempt. If the browser cannot be inspected in that window, fail closed and preserve the staged action for a later conversation.
- **cost:** ~$0.003–$0.02 per check; browser snapshot and hashing dominate, with little model work.
- **security:** Never transmit raw secrets or full form values when a redacted hash suffices. Canonicalize and hash approved fields at staging, bind to tab/session/origin, and invalidate on navigation, DOM replacement, origin change, price/address/recipient change, or expiry. A mismatch must be a hard stop, not a warning the model can override. Keep an append-only redacted diff receipt.
- **missing:** A browser-side typed form extractor and canonical field allowlist; current inspect/result surfaces are too unstructured for a security comparison.; A stable tab/session identity attestation (the already-requested browser_identity_attestation remains unresolved).; A submit interception point that performs the comparison immediately before mutation, not merely when the plan is created.; Relay storage for the approved canonical digest and a pendant speech/LED refusal state.

### "“Read the one-time code currently visible in my authenticated browser and speak it to me through the pendant, without sending the code to the relay, model, logs, or clipboard.”"
- **useful because:** The owner can complete 2FA and other sensitive workflows hands-free without copying a secret into a general-purpose model or leaving it in browser history, clipboard state, relay storage, or job receipts.
- **path:** browser → mac-bridge → pendant
- **model tier:** Local deterministic OCR/extraction on the Mac; no cloud model and no relay persistence. Realtime audio only transports the already-redacted, ephemeral speech result over the authenticated local path.
- **latency:** Under 3 s from request to spoken code; secret buffer erased immediately after playback or a 30-second timeout.
- **cost:** Near-zero API cost; local OCR and short-lived encrypted IPC dominate.
- **security:** Bind extraction to the explicitly selected authenticated tab, never expose raw pixels or code to the relay, disable clipboard and logging, redact screenshots and receipts, erase buffers on completion, and require a physical pendant hold before speaking a detected secret. If tab identity or local transport cannot be authenticated, refuse.
- **missing:** A local-only browser secret extraction route with strict field types and no raw-page forwarding.; An authenticated Mac-to-pendant ephemeral secret channel; current browser and relay paths are not designed for secret delivery.; Browser identity attestation, which remains unresolved.; A firmware playback mode that marks secret audio as non-recordable and emits no durable transcript.

### "“Hand this conversation to my Mac exactly where we left off, but show me the sentence, task state, and pending decision you are carrying before you continue.”"
- **useful because:** The owner should be able to move between the worn pendant and the Mac without losing the active thread or silently inheriting stale assumptions. A previewed, bounded handoff makes continuity visible and lets the owner reject incorrect context before any action resumes.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** Deterministic handoff packaging and state diff; background model summarizes only the conversation excerpt and pending decision; realtime model handles the spoken preview.
- **latency:** Preview in 2 s and handoff in 5 s. No action resumes until the owner accepts the presented handoff.
- **cost:** ~$0.005–$0.02 per handoff; storage and state comparison dominate.
- **security:** Include only the selected conversation, never ambient history. Bind the handoff to session, device, and expiry; show pending irreversible actions separately; require explicit acceptance before rehydrating context or dispatching work. Preserve an audit receipt without retaining rejected context longer than its TTL.
- **missing:** A user-visible handoff envelope containing transcript excerpt, active goal, pending actions, source timestamps, and expiry.; A pendant-to-Mac presentation/acceptance protocol independent of the unavailable unprompted push path.; A context diff verifier that distinguishes new owner input from stale recovered state.; Integration with existing workbench handoff records without turning them into automatic action resume.

### "“Only let this Mac and browser act while my pendant is physically present; if the link disappears, freeze sensitive commands and show me exactly what was blocked when it returns.”"
- **useful because:** A stolen, unattended, or merely unlocked Mac should not retain the ability to perform sensitive browser actions. Presence would become a bounded authorization condition, while ordinary observation can continue in degraded mode and queued work is frozen rather than silently replayed.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic lease and command gate; realtime model only explains blocked and released work.
- **latency:** Suspend sensitive command dispatch within one lease interval (under 5 s); restore only after authenticated reappearance and explicit owner policy. No model round trip belongs in the security decision.
- **cost:** Near-zero model cost; small authenticated heartbeat/lease traffic and bounded relay state.
- **security:** Presence is not identity by itself: bind the pendant key, session, and lease; use monotonic counters and replay rejection; distinguish link loss from deliberate privacy latch; never auto-submit commands accumulated during absence. Non-sensitive reads may remain available only if the owner configures that mode.
- **missing:** A cryptographic pendant presence lease and key provisioning path.; Mac and browser executor gates that classify commands as presence-required and freeze them before dispatch.; Relay lease expiry/reconciliation and a durable blocked-command receipt.; An owner policy for which action risk tiers require physical presence versus per-action approval.


## Changes it proposed to its own stack

### `relay` — Implement the missing durable approval handoff and guarded browser-transaction coordinator: persist staged plan digest/world fingerprint/expiry and pendant nonce in relay storage, deliver the readback on the next conversation, reject stale or changed browser state, and join the final browser result to the Mac job receipt. Add relay job leases and close ordinary ledgers so outage recovery cannot mistake every historical plan for an interrupted one.
- **owner gets:** A deliberate hold on the pendant would become real consent instead of an audit-only signal, and a dropped Mac or browser would fail closed without duplicating a purchase or leaving the owner with a promise that nothing can finish.
- effort: Medium-high: relay schema/store changes, coordinator state machine, browser typed extraction, integration tests, and hardware-in-the-loop approval tests.  ·  risk: A bug could block legitimate actions or, worse, submit against stale state. Recover by defaulting to refusal, preserving the staged plan for explicit restaging, and requiring digest/world/nonce matches at the final mutation boundary.
- cost: Negligible storage and API cost per staged action; one small D1 row and a few receipts. Model cost remains limited to spoken summaries.  ·  latency: Adds ~0.5–2 s for final state verification; no impact on ordinary read-only browser work.
- security: Improves security by making approval action-bound, expiring, replay-resistant, and fail-closed. Secrets stay in the browser/Mac; relay stores hashes and redacted metadata only.
- depends on: Implement the APPROVAL_STORE_CONTRACT rather than its current schema-only documentation.; Wire physical_transaction_approval_latch delivery and next-conversation readback; unprompted pendant push is unavailable.; Add typed browser form extraction and the unresolved browser identity attestation.; Fix orchestrator closeLedger calls and add relay job lease_until/requeue before enabling resume.


## What it asked for

_Nothing._
