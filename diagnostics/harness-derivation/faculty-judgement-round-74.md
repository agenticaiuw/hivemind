# Harness derivation — faculty-judgement — round 74

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Before you schedule anything or tell me a time-sensitive deadline, make sure your clocks and time zones agree. If they don’t, tell me the conflict in one sentence and ask which time zone to use; never silently guess.”"
- **useful because:** The live Mac is currently America/New_York while the owner profile says America/Chicago. A silent guess can create missed meetings, wrong reminders, and false urgency. This gives the owner a small, understandable decision instead of an invisible cross-surface failure, and then records the chosen authority for the task.
- **path:** pendant → relay → mac-planner → browser-extension → unified
- **model tier:** Background/cheap model for periodic normalization; realtime only for the short spoken conflict prompt. Deterministic timezone comparison should run before any model call.
- **latency:** Under 300 ms for local clock/context checks; under 2 s for a spoken conflict explanation. Scheduling waits for explicit owner choice only when authorities disagree.
- **cost:** Usually near-zero for deterministic checks; roughly $0.001–$0.01 only when the cheap model must explain a complex calendar/browser mismatch. No expensive realtime call unless the owner asks a follow-up.
- **security:** Timezone, calendar, and browser locale metadata leave the relevant devices only; event titles and account contents need not be sent. Do not infer a permanent home timezone from IP or travel. Choosing a timezone is non-destructive; applying a schedule remains subject to existing confirmation policy.
- **missing:** A single authoritative temporal-context record with source, timestamp, confidence, and task-scoped override; A preflight hook that can block /execute and reminder creation when temporal evidence conflicts; A one-turn pendant prompt and durable record of the owner's choice, including expiry when traveling

### "“Before you send or submit anything on my behalf, tell me which account and identity it will use, who will receive it, and whether any private information crosses accounts; warn me if the browser tab, Mac app, or saved login is not the identity I intended.”"
- **useful because:** A person can be logged into several Gmail, work, GitHub, banking, or government identities at once. Today an agent can have the right content in the wrong account and produce a plausible but damaging result. This gives the owner a compact identity-and-data-boundary check at the only moment it matters: immediately before the external side effect.
- **path:** pendant → relay → browser-extension → mac-planner → mac-vision → unified
- **model tier:** Deterministic account/session and recipient extraction first; a cheap background model classifies data-flow risk. Realtime is used only to speak the short preflight and receive the owner's choice.
- **latency:** 1 second for ordinary identity lookup and risk classification; no more than 3 seconds for a spoken preflight. The send/submit remains paused until confirmation when identity or data flow is ambiguous.
- **cost:** Near-zero for typed session metadata and destination matching; under $0.01 for unusual content classification. No cost for actions that are safely blocked before model reasoning.
- **security:** The system must never echo secrets or full message bodies in the prompt. Store only provider, account label, recipient domain, data classes, and hashes of evidence. Cross-account transfer is denied by default when the destination identity is unknown; the owner can approve a single action without changing global policy.
- **missing:** A provider-neutral identity manifest for each browser tab, Mac app account, and outbound channel; A data-flow classifier that labels selected fields before they cross accounts; A mandatory pre-send/submit gate shared by browser and Mac action executors, with a typed receipt naming identity evidence; A pendant-visible compact confirmation state that remains available if the network drops


## Changes it proposed to its own stack

### `context` — Add a Temporal Authority Resolver between /machine-context, calendar/browser reads, planning, and execution. It emits a typed task-scoped object {zone, source, observedAt, confidence, conflicts[], expiresAt}; a conflict preflight blocks time-sensitive /plan or /execute until the pendant receives a one-sentence choice. Persist the choice only for that task or an explicitly named trip, then attach the resolver receipt to the job and spoken completion receipt.
- **owner gets:** The owner will stop getting confidently wrong times when the Mac, remembered profile, browser, or calendar disagree. They are asked one clear question at the moment it matters, rather than discovering a missed appointment later.
- effort: Medium: deterministic resolver, preflight middleware, pendant prompt/response, and tests across reminder, calendar, and browser workflows.  ·  risk: A false conflict could interrupt harmless requests; recover by allowing an explicit 'use current device time once' choice and logging the evidence. If resolver is unavailable, refuse only time-sensitive actions and continue ordinary non-temporal actions.
- cost: Negligible compute and storage; one short cheap-model explanation only for unusual multi-zone cases. No additional API spend for deterministic comparisons.  ·  latency: ~100–300 ms for metadata reads; adds an owner turn only when evidence conflicts.
- security: Transmit timezone identifiers and timestamps, not event titles or account contents. Task-scoped choices expire and are not silently promoted to permanent profile facts.
- depends on: A pendant event/response channel for the owner's timezone choice; The existing job receipt and preflight plumbing must expose a block reason; An authoritative timezone policy, currently unresolved between owner memory and live machine context

### `integration` — Introduce an Account-and-Data Boundary Gate shared by browser and Mac executors. Before any send, submit, upload, or external mutation, it resolves the active provider/account from the tab or app, normalizes the destination identity, computes coarse data classes for the outgoing fields, and compares them with the requested identity. Unknown or cross-account flows produce a typed HOLD receipt and a pendant confirmation containing only account labels, recipient, and data classes; approved one-shot actions carry the same boundary proof into the final executor and job receipt.
- **owner gets:** The owner gets protection against the most dangerous silent automation error: sending a correct-looking message or form through the wrong logged-in identity, or leaking private material across accounts. They can approve a clearly described exception without reconfiguring every account.
- effort: Medium-high: provider adapters for identity discovery, field-level classification, shared executor middleware, compact pendant prompt state, and adversarial tests for account switching and stale tabs.  ·  risk: Some sites expose incomplete identity metadata, causing extra holds; recovery is a clearly labeled one-shot manual identity selection, never an inferred guess. A stale identity proof must expire and force revalidation.
- cost: Small metadata storage and deterministic checks; occasional cheap classification call, with no expensive model needed for known-safe fields.  ·  latency: Adds roughly 0.5–2 seconds before an external side effect; zero delay for read-only work.
- security: Improves isolation by default. Do not retain message contents; retain only provider/account identifiers, destination, data-class labels, evidence hashes, expiry, and approval receipt. The gate itself becomes a high-value policy component and needs tamper-evident logs.
- depends on: A provider-neutral account manifest and tab/app identity probes; A shared pre-send hook in both browser and Mac action runners; A pendant event channel and offline-safe display of HOLD/APPROVE state; Typed job receipts that include the boundary proof


## What it asked for

_Nothing._
## Its own summary

I found and recorded a new, narrow safety gap rather than repeating the broad browser/watch backlog: a Temporal Authority Resolver must sit between live machine context, authenticated calendar/browser evidence, planning, and execution. It should block only time-sensitive work when America/New_York (live Mac) conflicts with the owner's remembered America/Chicago, ask one short pendant question, attach the choice and evidence to the job receipt, and expire task-scoped overrides. I recorded both the owner-facing capability and the integration/context change.

**Biggest unknown:** The authoritative policy is still missing: should the owner profile, calendar event timezone, current device timezone, or a one-time travel override win? Implementation also still needs a pendant event/response channel and a preflight hook that can return a typed temporal conflict before /plan or /execute. Until those exist, time-sensitive scheduling should be treated as unsafe rather than silently guessed.

