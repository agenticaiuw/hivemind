# Harness derivation — faculty-action — round 202

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“When I press the bookmark button, save exactly what I was looking at and saying right now so I can find this moment later.”"
- **useful because:** A physical press is the only unambiguous moment marker. The pendant can emit the marker/audio while Mac perception captures the foreground app and browser session, and the relay can join them into one searchable event instead of a bare timestamp or an audio file with no context. This makes fleeting discoveries recoverable without making the owner narrate them.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → faculty-perception → faculty-action
- **model tier:** Use realtime only to acknowledge the press; use a cheap background model to title/transcribe and link the captured context.
- **latency:** Haptic/voice acknowledgement under 500 ms; context snapshot under 2 s; enrichment can finish asynchronously.
- **cost:** Low: one short background transcription/title pass, dominated by audio duration; context capture and event joining are local/relay operations.
- **security:** Capture only the active app/browser tab and the owner's marked audio, never page-wide contents by default. Private tabs and secrets must be represented by hashes or redacted labels. Require explicit owner setting for whether audio is retained.
- **missing:** A cross-surface moment-event schema joining pendant bookmark ID, monotonic time, Mac foreground state, browser session/tab identity, and audio object hash; A read-only Mac/browser snapshot action that returns provenance suitable for later search

### "“Watch this page until the condition I named becomes true, then carry out the safe part automatically and ask me on the pendant before anything irreversible.”"
- **useful because:** The owner can delegate waiting, which neither a one-shot Mac action nor a conversational model can do reliably. The relay keeps the watch alive, the browser extension retains the authenticated session, perception checks the exact condition, and action executes only after a fresh verification and the existing physical approval latch for risky effects.
- **path:** relay-realtime → relay → browser-extension → faculty-perception → faculty-judgement → faculty-action → pendant
- **model tier:** Cheap scheduled/background polling and deterministic page-state extraction; realtime model only for ambiguous condition language or owner interruption.
- **latency:** Poll cadence configurable from 15 s to 15 min; trigger-to-action under 5 s; no model turn needed between polls.
- **cost:** Low-to-moderate: polling is mostly local/browser traffic; model cost only when the condition or page structure is ambiguous.
- **security:** Never submit credentials or irreversible forms without the existing physical approval latch. Bind the watch to an explicit browser session and expiry; show the condition, target, and deadline on the pendant; stop on navigation/session change and report unknown rather than guessing.
- **missing:** A durable condition-watch job with expiry, backoff, and deduplication; A browser observation contract that exposes fresh field/url evidence without leaking unrelated page contents; A trigger-to-operation handoff that re-verifies postconditions immediately before execution

### "“If this multi-step task gets interrupted, recover what is safe, tell me exactly where it stopped, and continue only after checking the world—not from memory.”"
- **useful because:** Real tasks fail halfway through network drops, app changes, and expired sessions. The action surface should not leave the owner guessing whether an email was sent, a file was moved, or a form was half-filled. A recovery shepherd records step boundaries, independently verifies each completed postcondition, rolls back only explicitly reversible work, and presents one concise pending decision on the pendant.
- **path:** faculty-action → faculty-perception → mac-planner → mac-vision → browser-extension → relay-realtime → pendant
- **model tier:** Deterministic executor plus cheap background retry planner; realtime model only to explain the final state to the owner.
- **latency:** Detect interruption within 2 s; verify completed steps within 10 s; retry safe steps with exponential backoff; never silently retry irreversible steps.
- **cost:** Moderate: verification calls and occasional replanning dominate; far cheaper than replaying the entire task with a realtime model.
- **security:** Every retry must use an idempotency key and fresh state proof. Never infer completion from executor receipt alone. Preserve private evidence as hashes/minimal snippets; require physical approval for any new irreversible branch. Make unknown a first-class terminal state.
- **missing:** An operation journal with per-step idempotency keys, dependency edges, retry/rollback policy, and explicit unknown state; A verifier-to-executor commit protocol that blocks completion until fresh postconditions are independently checked; A pendant summary pattern for stopped/verified/unknown outcomes

### "“Undo the last thing you did for me, but only if you can prove the reversal took effect.”"
- **useful because:** The owner should not need to remember which app changed or manually reconstruct a correction after an accidental action. Action receipts become executable compensations: reverse a sent draft where possible, restore a moved file, revert a setting, or honestly report non-reversible/unknown. This is a distinct owner control from retrying an interrupted task.
- **path:** faculty-action → faculty-perception → mac-planner → browser-extension → relay-realtime → pendant
- **model tier:** Cheap deterministic compensation lookup first; use a stronger model only to synthesize a compensation when the action type has no registered inverse.
- **latency:** Identify the last eligible operation under 1 s; execute and verify a compensation under 10 s; never guess an inverse for irreversible actions.
- **cost:** Low for registered inverses; moderate only for novel compensation planning and independent verification.
- **security:** Bind undo to an immutable operation ID and owner-selected scope, never conversational recency alone. Require physical approval if the compensation itself has side effects. Do not retain private content beyond the ledger's existing hashes and minimal evidence.
- **missing:** A registry of action types and explicit compensating operations with reversibility levels; Ledger lookup by owner-facing recency plus operation dependency checks; A verifier contract for compensation postconditions and a safe refusal when no inverse exists

### "“Prepare this document to share, show me exactly what private information you removed, and only send the redacted version after I approve on the pendant.”"
- **useful because:** The owner gets a useful share instead of choosing between leaking secrets and doing tedious manual review. Mac reads the local document, perception identifies sensitive spans, action produces a separate redacted artifact, and the pendant approves the exact digest and recipient before transmission.
- **path:** mac-terminal → mac-planner → faculty-perception → faculty-judgement → faculty-action → relay-realtime → pendant → browser-extension
- **model tier:** Background document classifier/redactor; realtime only for the owner's short approval conversation. Deterministic hashing and diff generation must remain local.
- **latency:** Preview in under 8 s for ordinary documents; approval and send under 3 s after the deliberate gesture.
- **cost:** Moderate, dominated by document parsing and redaction inference; no model call for already-known structured fields.
- **security:** Raw document content must stay on the Mac unless the owner explicitly allows relay processing. Show recipient, removed categories, output hash, and expiry on the pendant; never send the unredacted original; require a fresh approval if content or recipient changes.
- **missing:** A local redaction engine with span-level provenance and confidence; A side-by-side or compact pendant-safe redaction summary protocol; An approval envelope binding recipient, output digest, and expiration to the actual send operation

### "“Give this person access to this file for one hour, then remove it automatically and tell me if the removal was verified.”"
- **useful because:** Temporary sharing is a common real-world action but today requires several apps, remembering an expiry, and trusting that revocation happened. The Mac creates a least-privilege share, the browser handles an authenticated sharing service when needed, relay survives sleep/link gaps, and action independently verifies both grant and revocation.
- **path:** faculty-judgement → faculty-action → faculty-perception → mac-planner → browser-extension → relay-realtime → pendant
- **model tier:** Background scheduler and deterministic permission operations; stronger model only to resolve ambiguous recipient/service details.
- **latency:** Grant within 10 s after approval; revocation at deadline within 30 s; alert immediately if verification is unknown.
- **cost:** Low-to-moderate: mostly local permission and scheduled job work, with occasional browser execution.
- **security:** Require explicit recipient identity, exact file digest, scope, and expiry. Never infer identity from a display name. Physical approval is mandatory for granting access; revocation is automatic but must be auditable. If the Mac/browser is unavailable at expiry, keep retrying and surface the exposure window rather than claiming success.
- **missing:** A time-bounded capability/share adapter per supported service; Recipient identity resolution and confirmation independent of page text; A durable expiry scheduler with revocation retries and verified exposure-window receipts


## What it asked for

_Nothing._
## Its own summary

Round 202: I discovered the live action surface and recorded three owner-facing capabilities: (1) a physical bookmark that joins pendant audio with the exact Mac foreground/browser context, (2) an expiring browser condition-watch that prepares safe work and requires pendant approval for irreversible work, and (3) interruption recovery that independently verifies each completed step, retries only idempotent work, and exposes unknown rather than guessing. Fresh probes show the system is more ready than the old context: Accessibility and Screen Recording are granted, synthesized input reaches the screen, the browser bridge is online, and the relay/Mac bridge are reachable. What I still need is not permission: durable condition-watch jobs, a cross-surface moment-event schema, and a per-step operation journal/commit protocol tying executor receipts to verify_operation_step. The proposal recorder noted all three are close to existing work, so implementation should be connective wiring rather than another parallel mechanism.

**Biggest unknown:** Whether the existing job/operation stores already contain enough schema to extend rather than add these three missing connective pieces; route inventory descriptions alone do not prove that.

