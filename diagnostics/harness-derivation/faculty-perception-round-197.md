# Harness derivation — faculty-perception — round 197

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac trust and browser state** — At 2026-08-08T22:54Z the Mac agent reports Accessibility and Screen Recording granted, requiredMissing=[], permissions.ready=true; Safari browser bridge is online with one device, 4 tabs, focused tab X search URL, pendingCommands=0 and spool=0. Relay is reachable and Mac bridge online. GET /v1/devices/status is not a Mac-agent route, so it remains unobserved here.
  - evidence: GET /ops/status HTTP 200 and GET /browser/status HTTP 200 at round 197; GET /v1/devices/status HTTP 404 on localhost:8000.

## Capabilities it proposed

### "Before you do anything consequential, say: “What do you actually know right now, what is stale, and what are you assuming?” Then refuse to act when the live evidence cannot support the requested action."
- **useful because:** This would be the system’s single most useful behavior: it stops a completed Mac job, a relay socket write, a stale browser tab, or a machine-written memory fact from being presented as owner reality. It gives the owner a short, inspectable evidence table instead of confident fiction.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Realtime only for the short owner-facing verdict; deterministic collectors and freshness/contradiction rules do the expensive work, with a cheap background model summarizing evidence.
- **latency:** Under 800 ms for ordinary checks; under 2 s if a browser snapshot and relay snapshot are both required. No action starts until the fence returns.
- **cost:** Usually <$0.01: mostly local route reads and rules; one small text-model call only when evidence conflicts or must be explained.
- **security:** Evidence must be scoped and redacted before leaving the Mac. Browser page bodies and memory values must not be sent to the relay by default. Consequential actions require explicit confirmation whenever a required witness is absent or stale.
- **missing:** A typed evidence-envelope contract with source, capturedAt, freshness deadline, confidence, and contradiction links; A gate in faculty-action that consumes the envelope and cannot downgrade unknown to success; Relay-side provenance for browser reads (stable ID plus content hash); A pendant-origin playback witness when a pendant exists

### "Audit my AI memory for facts that look authoritative but were written by a machine, are pinned forever, or contradict live Mac state—and show me the exact facts I should correct."
- **useful because:** The current timezone case proves this is user-facing harm: a machine-origin America/Chicago preference is pinned, confidence 0.99, injected into every prompt, and contradicts the live America/New_York machine zone. This capability finds that class of silent corruption before it changes reminders, routines, or actions.
- **path:** faculty-perception → mac-planner → relay-realtime → faculty-judgement
- **model tier:** Background/cheap model for clustering and explanation; deterministic source.origin, confidence, pinning, expiry, and live-state comparisons decide the findings. Realtime is unnecessary.
- **latency:** A few seconds on demand; a nightly sweep may run unattended and produce a bounded report.
- **cost:** <$0.02 per audit, dominated by a small explanation pass; comparison and ranking are local.
- **security:** Never rewrite owner facts automatically. Show provenance and the conflicting live observation; require owner confirmation before delete/patch. Keep private memory on the Mac and send only hashes/counts to relay.
- **missing:** A read-only memory-fact audit endpoint that returns source.origin, confidence, expiry, pinning, and last-used metadata; Typed comparators for live facts (timezone, permission state, browser identity, device presence); An owner-facing correction flow with explicit per-fact approval

### "When I ask “did that really happen?”, reconstruct the chain from the browser or Mac action through relay acceptance to physical output, and identify the first missing witness instead of saying completed."
- **useful because:** Today the system can prove that a Mac action ran or that relay bytes reached a socket, but not that the browser saw the mutation or that a pendant played audio. A first-missing-witness answer (“Mac receipt exists; browser result absent; playback unconfirmed”) is far more useful than a false success.
- **path:** relay-realtime → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-judgement
- **model tier:** Cheap background model formats a deterministic event-chain reconstruction; realtime only speaks the concise result when the owner asks.
- **latency:** Under 1 s from retained records; under 3 s if it must await a browser result or relay job status.
- **cost:** <$0.01 per query, mostly local joins over existing receipts and pipeline records.
- **security:** Do not expose page contents or credentials in the chain. Treat socket bytes, Mac completion, browser result, and device playback as distinct claims; never infer the latter from the former. Missing witnesses must remain unknown.
- **missing:** A shared correlation ID propagated through plan, Mac ledger, browser command/result, relay job, and audio artifact; A browser-side postcondition witness (before/after digest or capsule ID) for mutations; The already-designed device playback event emitted by firmware and consumed by relay; A durable cross-surface event index rather than count-capped per-source stores

### "Before clicking, typing, sending, or deleting, prove that the visible app, browser tab, and target control are the ones I meant; if screenshot, accessibility tree, and URL disagree, stop and ask me."
- **useful because:** With Accessibility and Screen Recording now genuinely granted, the agent can finally detect the classic catastrophic error: acting in the wrong window or stale tab. The owner gets a physical pause before a mistaken send/delete, not an apology afterward.
- **path:** mac-vision → browser-extension → mac-planner → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Realtime/vision model only for ambiguous target matching; deterministic app identity, URL, tab ID, accessibility role, and screenshot freshness perform routine checks.
- **latency:** 150–500 ms for routine preflight; up to 2 s when vision disambiguation is needed.
- **cost:** <$0.02 per guarded action; local accessibility/browser reads dominate latency, with vision invoked only on ambiguity.
- **security:** Screenshots and accessibility text remain on the Mac unless owner explicitly permits relay analysis. Redact passwords, OTPs, payment fields, and private page bodies before any model call. Never treat a matching label alone as authorization.
- **missing:** A mandatory pre-action target-witness hook in faculty-action; A stable browser tab identity and DOM/control digest joined to the Mac accessibility snapshot; A screenshot-to-accessibility alignment result with freshness timestamps; Owner policy describing which destructive actions always require spoken confirmation

### "Tell me immediately if the system is about to leak something: a secret in a browser tab, an unexpected microphone/camera capture, a sensitive window on screen, or content about to leave the Mac for the relay."
- **useful because:** Perception currently reports whether permissions are available, not whether a dangerous state is active. A live egress-and-capture alarm would make the hive trustworthy while still allowing automation: it can catch an accidental password-page read, recording left on, or screenshot sent to a cloud model.
- **path:** mac-vision → browser-extension → mac-planner → relay-realtime → faculty-perception → faculty-judgement
- **model tier:** Deterministic local classifiers and OS/browser metadata first; a small local model classifies ambiguous visual sensitivity. Never use the expensive realtime model for continuous monitoring.
- **latency:** Continuous local checks every 1–2 seconds; speak/interrupt within 500 ms of a policy violation.
- **cost:** Near-zero API cost when local; modest CPU/battery cost for periodic screen and browser metadata sampling.
- **security:** This feature itself observes sensitive state, so raw screen content must stay local and be ring-buffered briefly. Require explicit opt-in per data class (credentials, health, finance, private messages). Relay receives only an alert category and redacted reason.
- **missing:** OS-level capture-session and microphone/camera-active telemetry exposed to the agent; Local secret/sensitivity classifier integrated with browser URL, form role, and focused-app metadata; A hard egress gate before screenshot upload, read_web_page, browser result, or relay prompt submission; Owner-configurable sensitivity policy and emergency mute button

### "Let me ask, “What did the whole system know at 9:15, before it acted?” and get a replayable, tamper-evident timeline of the Mac, browser, relay, and pendant state at that moment—not today’s reconstructed guess."
- **useful because:** Today each surface keeps different bounded records and most are overwritten by activity; a later explanation cannot distinguish what the agent knew then from what it learned afterward. A causal time-slice would let the owner audit an automation, prove whether a stale tab or stale memory caused it, and understand a failure without trusting a retrospective summary.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-judgement
- **model tier:** Cheap background summarization over immutable structured snapshots; cryptographic verification and temporal joins are deterministic. Realtime is used only when the owner asks for a spoken explanation.
- **latency:** Snapshot capture must be sub-100 ms at each local event; an on-demand replay should return a first answer in under 2 seconds and a detailed export in under 10 seconds.
- **cost:** <$0.01 per replay after storage; dominant cost is bounded local storage and periodic hashing, not model inference.
- **security:** Snapshots may contain screen, browser, memory, and audio metadata. Keep bodies local by default, encrypt the ledger, hash/redact sensitive fields before relay replication, and require confirmation before exporting a replay. A missing snapshot must be shown as a gap, never interpolated.
- **missing:** An append-only, encrypted, monotonic event journal with per-surface sequence numbers and hash-chain checkpoints; A relay protocol for exchanging signed state checkpoints between Mac, browser, and a future pendant, including clock-offset estimates; Browser and Mac hooks that snapshot precondition, decision, and postcondition state around every action; A replay query API that returns evidence intervals and explicit gaps rather than a prose-only retrospective; Pendant firmware emission of its beacon/capture/playback sequence numbers when connected

### "Let me set actions that may run only when my pendant physically confirms my presence and intent—for example, a spoken command can draft a transfer, but only a button press on the pendant while the Mac and browser show the same target can authorize sending it."
- **useful because:** A Mac session, browser cookie, or relay token is not proof that the owner is present or intended the final irreversible step. Binding authorization to the worn device and the exact target gives the owner a practical last-mile safety boundary that no single cloud, Mac, or browser surface can provide.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Deterministic challenge/response and target hashing do the authorization; realtime only explains the pending challenge and result.
- **latency:** Challenge delivery and validation under 1 second when connected; offline pendant should retain a short-lived authorization until the Mac reconnects.
- **cost:** <$0.005 per authorization; small persistent nonce ledger and negligible relay compute. Hardware addition, if required, is a secure element under roughly $1–3 per unit.
- **security:** Use per-action nonce, target digest, expiry, replay protection, and device-bound keys; never authorize from a bare button press. The spoken target and browser/Mac target must hash to the same canonical intent. Lost pendant requires revocation and recovery policy.
- **missing:** A pendant-held device key with secure nonvolatile monotonic counter or secure element; A relay challenge/response protocol that binds nonce to canonical action digest and device identity; Browser/Mac target attestation covering tab, URL, control, and pre-action state; An action policy engine distinguishing draft, reversible, and irreversible operations; A recovery and revocation flow that does not silently fall back to Mac-only authorization


## Changes it proposed to its own stack

### `interaction` — Add an owner-visible “epistemic diff” view: every answer or action preview shows only the facts that changed since the last turn, which surface supplied each change, and which conclusions would disappear if that source were offline. Make it available as a spoken short form and a detailed Mac/browser view.
- **owner gets:** The owner can tell whether the system is reacting to a new browser result, a fresh Mac observation, or merely repeating memory. This makes stale context and accidental prompt carry-over visible without requiring the owner to inspect logs.
- effort: Medium: event normalization, source-aware diffing, and a compact UI/voice renderer; requires new cross-surface metadata rather than new model training.  ·  risk: A diff can overwhelm or falsely imply that unchanged facts are still true. Cap it, show freshness, and label unavailable sources as gaps. Recovery is falling back to the current ordinary answer.
- cost: <$0.01 per rendered explanation; storage grows only with bounded event metadata, not page/audio bodies.  ·  latency: Adds roughly 100–300 ms for local diff computation; no extra model call for the compact form.
- security: Keep sensitive values out of the diff; expose field names, provenance, and redacted change classes by default. Detailed values require confirmation.
- depends on: A shared event envelope with source, sequence, capturedAt, and freshness; Mounting browser provenance records and propagating relay correlation IDs; A bounded local diff index that survives relay restart


## What it asked for

_Nothing._
## Its own summary

Round 197 established a major live change: the exact AI Pendant Agent identity now has Accessibility and Screen Recording, all required permissions are ready, Safari bridge is online with four tabs and no pending/spooled commands, and the relay/Mac bridge are reachable. I recorded that evidence. I proposed five capabilities, led by a hard pre-action evidence fence (the single most useful behavior): before consequential action, expose freshness, provenance, contradictions, and refuse when the witness is missing. I also proposed machine-origin memory corruption audits, first-missing-witness action reconstruction, wrong-window/tab target proof, and local sensitive-data/capture egress alarms. The recorder noted that several are connective work because the component routes already exist; the genuinely missing work is the typed envelope/gates between them.

**Biggest unknown:** The pendant remains absent from the live registry and has never registered, so physical playback, offline beacon, capture-quality verdicts, and any device-origin witness are still unverified. I still need a real cross-surface correlation/provenance contract (especially relay browser IDs/content hashes), an action gate that consumes it, and owner policy for confirmation/sensitive-data classes. GET /v1/devices/status is relay-only and cannot be checked through the Mac agent route I probed.

