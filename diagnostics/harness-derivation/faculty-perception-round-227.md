# Harness derivation — faculty-perception — round 227

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **macOS input reachability** — As of 2026-08-09T00:54Z, AI Pendant Agent has Accessibility and Screen Recording granted; inputReachability is verified, synthesized events reach the screen, secure input is false, and automationMissing is empty. This supersedes the prior blocked-TCC state.
  - evidence: GET /observe HTTP 200: accessibility.trusted=true, screenRecording=true, inputReachability.status='verified', uiActionsWillReachTheScreen=true, host bundle com.aipendant.agent.
- **live Mac and browser state** — At 2026-08-09T00:54Z the Mac bridge and browser extension are online; Safari has 5 tabs and the active tab is USPS Tracking at tools.usps.com. The AI Pendant Agent's input reachability is verified and all required permissions are ready.
  - evidence: GET /ops/status and GET /observe both returned 200 with browserExtension.online=true, browser tabCount=5, active tab URL https://tools.usps.com, permissions.ready=true, inputReachability.status='verified'.

## Capabilities it proposed

### "“Do it, and only tell me it worked when you can prove the result is visible where it belongs.”"
- **useful because:** This would turn the system from an executor that reports Mac-side completion into one that verifies the owner's actual end state: the browser page, app UI, or relay handoff. It is the single most useful capability because it prevents silent false success on consequential everyday tasks.
- **path:** relay-realtime → mac-planner → mac-vision → browser-extension → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Realtime handles the short spoken confirmation; mac-planner and faculty-action use the cheaper action tier; mac-vision verifies only when an accessibility/browser semantic check is insufficient; faculty-perception compares before/after evidence.
- **latency:** 2–5 seconds for a normal browser or app task; up to 15 seconds when a screenshot/vision verification is needed. No expensive model call if a deterministic postcondition passes.
- **cost:** Usually <$0.01 in model/API cost; vision fallback dominates and should be under roughly $0.05 per verification. Storage is bounded to a compact receipt and redacted digest, not full screenshots by default.
- **security:** Before/after evidence may contain private page or app content, so redact secrets and retain only hashes, selectors, and a short claim. Destructive actions still require the owner's existing confirmation rule. Never call a socket write or relay delivery 'verified' without a device-originated acknowledgement.
- **missing:** A common postcondition schema shared by browser, Mac action, and relay jobs; A verifier that can consume browser semantic state or a screenshot and attach evidence to the existing action ledger/job receipt; Relay-side delivery verification remains unavailable until the pendant emits the accepted played event

### "“Before you use a remembered preference to act, tell me whether I actually said it or the machine invented it.”"
- **useful because:** A machine-derived value is currently able to masquerade as an owner preference: the pinned, high-confidence America/Chicago timezone is injected into every context projection despite the Mac being America/New_York. This capability would stop provenance errors before they cause wrong schedules, reminders, or file operations.
- **path:** faculty-perception → faculty-judgement → mac-planner → relay-realtime → unified
- **model tier:** Deterministic provenance and conflict checks first; use the cheaper text model only to explain a flagged conflict. Realtime is needed only if the conflict blocks a spoken request.
- **latency:** Under 150 ms for normal context assembly; under 1 second for a conflict explanation.
- **cost:** Near-zero for the deterministic check; <$0.005 only when generating a natural-language explanation.
- **security:** Do not expose hidden fact values unnecessarily. Preserve source.origin, confidence, and timestamps in an internal audit record, but speak only the minimum needed. Never silently rewrite owner memory; require the owner to correct a pinned fact.
- **missing:** A context-projection trust policy that distinguishes source.origin='owner' from source.origin='machine' for pinned preference kinds; A conflict record linking the rejected fact, authoritative machine observation, and action that was prevented; A safe owner-facing correction flow rather than DELETE /memory/facts/:idOrKey being used implicitly

### "“Know when I can actually listen, and hold non-urgent things until the moment I can act on them.”"
- **useful because:** The system can now observe the real foreground app and browser state, but relay announcements and scheduled briefs still have no shared interruption policy. This would prevent a spoken alert during a meeting or secure-input session, then deliver a compact, deduplicated batch when the owner returns to an actionable context.
- **path:** faculty-perception → faculty-judgement → relay-realtime → mac-planner → browser-extension → unified
- **model tier:** Deterministic policy over foreground app, secure-input state, active browser tab, pending jobs, and urgency; a cheap text model clusters and summarizes only the queued items. Realtime speaks only the final short batch.
- **latency:** A perception decision under 200 ms on every candidate announcement; queued digest generated in under 2 seconds when the owner becomes available.
- **cost:** Near-zero for state checks and queueing; <$0.01 per digest, dominated by summarization. No screenshot upload unless the owner explicitly asks for visual context.
- **security:** Foreground app names and browser URLs are sensitive; retain only coarse activity classes and hashes by default. Never infer availability from a single app name when secure input or a call state says otherwise. Urgent safety alerts bypass the queue under an explicit policy.
- **missing:** A shared interruption-state contract consumed by routines, relay announcements, and Mac jobs; A durable queue state that distinguishes deferred, surfaced, acknowledged, and expired without claiming the owner heard it; A Mac-side availability classifier that combines GET /observe, browser status, and active session/job state

### "“Before you send, buy, delete, or publish anything important, have one part of you make the change and a different part independently check that the target and result are what I intended.”"
- **useful because:** Today the same planning path can select a target, execute it, and report completion without an independent challenge. This capability would catch wrong-recipient mail, wrong browser account, wrong file, stale page state, and accidental destructive scope before the owner pays the cost. It uses the hive's genuinely different reach: the relay decides the check, the Mac acts, the browser sees authenticated state, and the wearable gives the final concise challenge or approval.
- **path:** relay-realtime → faculty-judgement → faculty-action → mac-planner → mac-vision → browser-extension → unified
- **model tier:** Use deterministic target and policy checks first. Use a cheap text model to generate an independent counter-check from the proposed action and observed state. Reserve realtime for the owner's final spoken confirmation or a one-sentence conflict report; do not spend the expensive tier on routine verification.
- **latency:** 2–4 seconds for reversible actions; up to 10 seconds for mail, purchases, deletion, or publication because the independent observer may need a fresh browser/app observation.
- **cost:** Typically <$0.02 per guarded action; vision fallback and authenticated browser inspection dominate. Store only a bounded action receipt, target digest, and verifier verdict rather than private screenshots or message bodies.
- **security:** The verifier must not execute or mutate anything. It must read a fresh state through a different surface than the actor and report target, scope, and confidence. Destructive actions remain confirmation-gated even if the verifier agrees. Conflict, stale state, missing authentication, or an unavailable browser must fail closed and be spoken plainly. Evidence containing recipients, account names, or private page text must be redacted and short-lived.
- **missing:** A first-class independent-verifier phase in the plan/execute lifecycle, with separate actor and observer identities; A normalized target/scope digest shared by Mac actions, browser commands, and relay jobs; A fail-closed policy engine that requires owner confirmation when the verifier disagrees or cannot obtain fresh state; A receipt schema recording the proposed target, observed target, verifier verdict, and final owner decision

### "“Give me a short window after an important action where I can say ‘undo that’ and have you reverse the actual change, not just remove your local record.”"
- **useful because:** The Mac already has action ledgers and job undo paths, but browser mutations and external side effects do not share a wearable-triggered reversal contract. A bounded recovery window would make the system safer in daily use: undo a sent draft, browser setting change, file move, or calendar edit while the original authenticated session is still available.
- **path:** relay-realtime → faculty-perception → faculty-judgement → faculty-action → mac-planner → browser-extension → unified
- **model tier:** Deterministic inverse actions and ledger lookups do the work. Use a cheap model only when an inverse is ambiguous and must be explained; realtime receives the owner's ‘undo’ and returns the result.
- **latency:** A spoken undo command should stop or reverse a reversible action within 2 seconds. If reversal is impossible, report that within 1 second rather than pretending success.
- **cost:** Usually <$0.01 per action; the dominant cost is no model call but keeping bounded before/after metadata and, for browser mutations, an authenticated session long enough to reverse them.
- **security:** Never claim external reversal when the service offers no reliable inverse. Sending or purchasing may be irreversible and must remain confirmation-gated. Store redacted before/after values, target digests, and expiry times; never retain passwords, payment data, or full page bodies. The owner must explicitly confirm a late reversal outside the grace period.
- **missing:** A cross-surface inverse-action registry with explicit reversible/irreversible classification; Browser mutation receipts linked to the existing Mac action ledger and command IDs; A pendant/relay command path that can identify the most recent owner-approved action without confusing speech with authorization; Service-specific compensating actions for calendar, mail, files, and browser state

### "“Before anything leaves my Mac or a logged-in site, show me exactly what private information is crossing the boundary and let me approve the smallest safe version.”"
- **useful because:** The system can act across private browser sessions, local files, mail, and a cloud relay, but it does not provide one cross-surface disclosure preview. This would prevent accidental leakage of credentials, personal messages, tracking numbers, or unrelated page content when researching, drafting, uploading, or asking the relay to speak something aloud.
- **path:** faculty-perception → faculty-judgement → faculty-action → mac-planner → mac-vision → browser-extension → relay-realtime → unified
- **model tier:** Local deterministic classifiers and field-level redaction run first. A cheaper text model may explain categories and produce a minimized draft. Realtime only asks for approval when the boundary policy requires it; no private payload needs to be sent to the expensive model.
- **latency:** Under 300 ms for routine local classification; under 3 seconds for a redaction preview and spoken approval. Hard-block unknown or high-risk destinations until the owner decides.
- **cost:** Near-zero for local pattern and metadata checks; <$0.01 for an optional explanation. The main cost is implementation of destination-aware redaction, not inference.
- **security:** The classifier must inspect locally before relay upload and must not log raw sensitive values. Redaction must be reversible only in memory until approval, with a bounded audit record containing categories and hashes. Explicitly distinguish browser-originated secrets, owner-approved content, and untrusted page text. Destructive or external transmission remains confirmation-gated.
- **missing:** A common data-boundary policy covering relay, browser, mail, file, and speech destinations; Local field-level classification/redaction shared by browser and Mac action paths; A preview protocol that returns categories, byte/character counts, and the exact minimized payload without persisting the original; A wearable-friendly approval token bound to one preview hash so approval cannot be replayed for a different payload


## What it asked for

_Nothing._
