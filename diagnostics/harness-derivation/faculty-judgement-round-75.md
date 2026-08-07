# Harness derivation — faculty-judgement — round 75

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Keep my schedules and spoken briefs on the right local time. If my Mac, pendant, or saved preference disagree, warn me before moving anything, and show me which timezone each upcoming item will use.”"
- **useful because:** The live system has already observed America/New_York from the Mac while the owner's saved preference is America/Chicago. Silently choosing one can make a morning brief, reminder, or page-watch alert arrive at the wrong hour. This gives the owner a single, understandable decision point and prevents cross-surface schedule drift.
- **path:** relay-realtime → pendant → mac-planner → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use the cheap background tier to reconcile routine metadata and detect conflicts; use realtime only to ask the owner the one short confirmation question and to read back the final schedule. No model call is needed for ordinary offset conversion.
- **latency:** Routine checks under 1 second and normally silent. On a conflict, deliver one concise pendant prompt within 5 seconds; wait indefinitely for confirmation rather than guessing. Recompute after travel or a machine-context refresh.
- **cost:** Low: mostly deterministic timezone database and stored facts; typically one small background model call only when labels or intent are ambiguous, under $0.01 per conflict. Audio delivery is the dominant variable cost.
- **security:** Timezone and travel inference can reveal location. Keep raw location off the relay; send only timezone/offset and confidence. Never mutate routines or execute a time-sensitive action on a conflict without explicit confirmation; log the chosen zone and provenance for later undo.
- **missing:** A canonical timezone authority record with precedence and expiry (saved preference vs device vs explicit owner statement).; Conflict events shared by scheduler, page-watch, and briefing services, with a single deduplicated pendant notification and owner acknowledgment.; Routine preview/readback that includes the resolved IANA timezone and source before applying a change.; A travel/temporary-zone mode that expires automatically instead of overwriting the owner's home timezone.

### "“When you have a sensitive action ready—send this email, submit this form, buy this, or delete this—read me a short, exact summary and let me approve it with a physical double-press on the pendant. Bind that approval to exactly what I heard, and refuse if anything changed.”"
- **useful because:** Today approval is conversational and fragile: the owner may be away from the Mac, misunderstand what a private browser page will submit, or have a prepared action change between review and execution. A hardware-bound approval gives them a fast, deliberate control that works while walking, preserves the browser's private session, and makes accidental or stale approvals impossible.
- **path:** pendant → relay-realtime → unified → faculty-perception → faculty-judgement → faculty-action → mac-planner → browser-extension
- **model tier:** Use a cheap background model to prepare and compress the action summary; use realtime only to answer questions and read the final digest. The approval itself is deterministic cryptographic verification, not an LLM decision.
- **latency:** Summary preparation may take seconds for a browser or Mac workflow. Once the owner double-presses, verification and dispatch should complete in under 500 ms; if the action changed, interrupt immediately and require a new review.
- **cost:** Low: one short summarization call for complex actions, generally under $0.01; physical input, digest hashing, and signature verification are negligible. Sensitive purchases or sends still incur their normal service costs only after approval.
- **security:** The pendant must never contain email contents, payment credentials, or page secrets. The relay signs a canonical action digest (target, fields or message hash, irreversible effects, expiry, and originating session), sends only a spoken minimal summary to the pendant, and accepts one short-lived physical signature. Require an explicit spoken confirmation for unusually high-risk actions and provide a hardware stop gesture. Keep an immutable receipt without storing sensitive payloads.
- **missing:** A pendant firmware secure approval primitive with a debounced double-press, short-lived device key, and local haptic success/failure signal.; A canonical cross-surface action digest and signature verifier shared by relay, Mac executor, browser bridge, and job receipts.; A review protocol that freezes or revalidates every field, URL, recipient, amount, and side effect immediately before dispatch.; A pendant UX for hearing the digest in one sentence and requesting a repeat/detail without exposing private page data.


## Changes it proposed to its own stack

### `integration` — Add a shared notification event ledger between authenticated page-watch, relay, Mac jobs, and the pendant. Normalize each observation into (source, watch/job id, semantic subject, evidence hash, observed interval), derive a stable event key, and maintain unseen/announced/acknowledged/snoozed states with a suppression window. Repeated observations such as the same Order 42 change must update evidence and freshness without creating another spoken alert. A pendant tap or spoken “ack/stop watching this” writes the acknowledgement; only materially changed evidence or an owner-requested re-open can announce again. Include a compact provenance receipt and a reconciliation job for events emitted while the browser bridge was offline.
- **owner gets:** The owner currently receives repeated copies of the same page-watch change, which trains them to ignore the pendant. They should hear one useful alert, be able to acknowledge it from their body, and trust that offline/reconnected surfaces will not replay noise or lose a genuinely new change.
- effort: Medium-high: a small durable event schema and idempotent reducer, adapters in page-watch and relay notification paths, plus pendant acknowledgement UI/voice intent and tests for reconnect/replay.  ·  risk: A bad semantic key could merge two distinct order or appointment changes, or suppression could hide a real update. Keep raw evidence hashes and source timestamps, use conservative keys initially, expose “show suppressed updates,” and allow a spoken re-open. If the ledger is unavailable, fall back to current alert behavior rather than dropping events.
- cost: Negligible storage and CPU; one cheap background reduction pass per event. No extra realtime model call for exact duplicates; occasional semantic classification may cost under $0.01 per ambiguous event.  ·  latency: Adds under 100 ms for deterministic dedup; acknowledgment should reach relay/pendant state within a few seconds after reconnect.
- security: Event records may contain private page snippets. Store only minimal normalized subject plus encrypted evidence pointer, enforce source/session access, and never send page contents to the pendant unless the owner asks.
- depends on: A durable shared event/receipt store and an authenticated pendant-to-relay acknowledgement path.; The existing page-watch extraction and browser command/result correlation.; A notification policy that can distinguish alert, digest, and suppressed states.

### `hardware` — Add a secure-attention path to the pendant: a dedicated double-press gesture sampled locally with debounce and long-press cancellation, a per-device signing key held in a secure element or protected flash, and a distinct haptic success/failure pattern. The firmware signs only a server-provided action-digest nonce plus expiry; it cannot sign arbitrary text or replay an old digest. Relay verification must reject reused, expired, or mismatched digests before Mac/browser execution.
- **owner gets:** The owner gets a trustworthy physical “yes” and “no” that works away from the keyboard, without speaking private email or payment details aloud. A changed form or stale approval fails safely instead of silently applying the old decision.
- effort: High: secure-element selection and board integration, firmware gesture/state machine, relay challenge-signature protocol, and end-to-end tests for replay, disconnect, accidental presses, and battery loss.  ·  risk: Lost or cloned hardware could be abused if key enrollment and revocation are weak; require pairing-time enrollment, server-side revocation, and a spoken fallback that is at least as explicit. False double-presses must never approve by themselves, so require a fresh challenge and a short haptic pre-confirmation window.
- cost: Roughly $1–$4 BOM increase for a secure element and minor board area/power cost (sub-milliwatt average, brief wake current). No recurring model cost; cryptographic operations are negligible.  ·  latency: Local gesture recognition under 100 ms; relay verification and dispatch under 500 ms on a healthy link. Offline or stale challenges fail closed.
- security: Improves authorization substantially by binding approval to a physical enrolled device, but creates a high-value signing key. Use key rotation/revocation, rate limits, tamper-aware enrollment, and never expose the private key to application RAM.
- depends on: A canonical action-digest schema spanning Mac, browser, relay, and job receipts.; A pre-dispatch revalidation gate so the signed digest is compared with the exact action about to run.; Secure pairing and revocation UX.


## What it asked for

_Nothing._
## Its own summary

Round 75 produced a new cross-surface notification-ledger change: stable event identity, evidence-aware deduplication, pendant acknowledgement/snooze, and replay-safe reconciliation for browser-watch alerts. This directly addresses the verified repeated Order 42 notifications. I also recorded a timezone-conflict capability, though the recorder flagged it as close to existing work. I still need the shared durable event/receipt store and pendant acknowledgement path to make the dedup proposal real. Current owner-facing blockers remain: the browser bridge is offline, Mac Accessibility/Screen Recording are not granted, and Mac timezone (America/New_York) conflicts with the saved owner preference (America/Chicago); I will not guess or re-request those grants.

**Biggest unknown:** Whether the orchestrator's newly acted-on requests actually created the pending reconciliation/attention/audio tools: the live granted category reports zero, so I cannot verify their schemas or use them this round.

