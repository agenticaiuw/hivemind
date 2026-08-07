# Harness derivation — faculty-perception — round 50

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-agent trust and vision gates** — At 2026-08-07T11:44:48Z, exact running AI Pendant Agent (com.aipendant.agent, /Users/evanliu/Applications/AI Pendant Agent.app) is NOT Accessibility-trusted and has NO Screen Recording permission; inputReachability is failed, uiActionsWillReachTheScreen=false. /ops/status also reports computerUse.loopEnabled=false and visionUploadConsented=false. Automation grants are cached, but permissions.ready=false.
  - evidence: GET /observe and GET /ops/status live responses
- **timezone authority discrepancy** — Owner memory says authoritative timezone America/Chicago, while live GET /machine-context reports machine.timezone America/New_York. Any scheduled or spoken local-time interpretation must use the owner's stored timezone, not the machine field, until reconciled.
  - evidence: discover:owner remembered.text and live GET /machine-context response
- **browser reachability** — The home Chrome/browser extension is offline as of 2026-08-07T11:44:48Z; there are 4 pending browser commands and no live tab metadata. Mac bridge is online. Authenticated browser actions cannot currently be verified.
  - evidence: GET /browser/status and GET /ops/status live responses

## Capabilities it proposed

### "Before you try anything, tell me what you can actually reach right now—my pendant, Mac, browser tabs, and logged-in pages—and warn me if an action would only appear to succeed."
- **useful because:** The system currently reports cached automation grants while live input reachability, Accessibility, Screen Recording, and the browser extension disagree. The owner gets an honest preflight instead of a false success receipt, especially for GUI or private-web work.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → unified → faculty-perception
- **model tier:** No model for the basic verdict: a typed rules engine compares fresh observations. Use a cheap text model only to turn the evidence into one short spoken explanation; never use realtime for polling.
- **latency:** Under 500 ms from a live query; observations can be refreshed in parallel and cached for at most 10 seconds. A stale result must be labeled stale, never presented as ready.
- **cost:** Near-zero for the rules check; roughly $0.001 or less for an optional short explanation. Dominant cost is network/device probes, not tokens.
- **security:** Do not expose tokens, private page contents, or secret captured facts. Report capability class and freshness only (for example, 'Mail automation granted' or 'browser offline'). Require confirmation before probing or displaying sensitive page content.
- **missing:** A shared typed preflight schema consumed by relay, Mac planner, and action receipts; A pendant-visible compact status protocol for offline or stale verdicts; A permission reconciliation probe that verifies the exact running binary rather than trusting cached TCC grants; Browser extension heartbeat recovery or explicit offline queue semantics

### "After a conversation, tell me what I personally committed to, what others committed to, and what evidence supports each item; then prepare reminders or calendar drafts without sending anything."
- **useful because:** The owner can currently get transcripts, reminders, and private-page reads separately, but cannot reliably turn an ambient pendant conversation into an accountable, evidence-linked commitment list. This prevents forgotten promises without pretending inferred intent is fact.
- **path:** pendant → relay-realtime → unified → mac-planner → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use the realtime model only for the live conversation and a cheaper background model for post-conversation extraction and reconciliation. Use deterministic rules for speaker/time/source attribution where possible.
- **latency:** Conversation capture must add no noticeable latency. Produce a first commitment digest within 60 seconds after the session ends; private calendar/mail reconciliation may run in the background and update the digest later.
- **cost:** About $0.01–$0.05 per conversation depending on transcript length and private-source reconciliation; audio transcription and background extraction dominate.
- **security:** This is sensitive interpersonal data. Default to local/relay retention of transcript hashes and extracted commitments rather than raw audio; require an explicit capture indicator and a delete control. Never send a message, create a calendar event, or notify another person without confirmation. Clearly label inferred commitments and show source timestamps/snippets.
- **missing:** Speaker-aware or owner-confirmed attribution for multi-person conversations; A durable commitment object with status, confidence, provenance, due date, and expiry; A post-session extraction worker joining pendant transcript evidence with authenticated calendar/mail/browser evidence; A review UI and spoken summary that distinguishes explicit promises from model inference


## Changes it proposed to its own stack

### `integration` — Add a live trust-convergence verifier that compares macOS TCC state for the exact running AI Pendant Agent identity against inputReachability and screen-capture probes, records probe timestamps and binary hashes, and marks cached permission grants invalid when they disagree. Expose a single machine-readable readiness record consumed by vision activation, planner preconditions, and receipts; include an owner-facing remediation instruction but do not silently open System Settings or claim readiness.
- **owner gets:** After the orchestrator granted permissions, live evidence still says Accessibility=false, Screen Recording=false, inputReachability=failed, and visionUploadConsented=false. This prevents the pendant from saying a GUI action worked when it did nothing and tells the owner exactly what remains blocked.
- effort: Medium: implement a verifier around existing /observe and /ops/status probes, persist the last successful exact-binary verification, and wire its result into vision/planner/action receipt gates.  ·  risk: A transient probe failure could falsely mark the Mac unavailable; require two consecutive failures or a short grace period, retain the last evidence, and distinguish unknown from denied. Recovery is automatic on the next successful exact-binary probe.
- cost: Negligible API cost; a few local probe calls per activation or every 30–60 seconds while the agent is active.  ·  latency: Adds roughly 100–300 ms to first GUI-action preflight; no cost on non-GUI work if the cached verification is fresh.
- security: Improves security by preventing stale/cross-binary TCC grants from authorizing actions. Store binary identity, permission booleans, and timestamps only; never capture screen pixels in this verifier.
- depends on: Exact-binary Accessibility and Screen Recording grants must actually be present before readiness can become true; visionUpload consent must be represented separately from OS Screen Recording; mac-vision must consume the verifier rather than its current static loop flag

### `context` — Make timezone resolution explicit and provenance-aware: represent owner timezone (America/Chicago) and host timezone (America/New_York) as separate facts, require every schedule/time answer to declare which one it uses, and reject silent conversion when the two disagree. Add a one-time spoken clarification flow and persist the owner's chosen authority with source and timestamp.
- **owner gets:** The current live machine context conflicts with the owner's remembered timezone. Without this, daily routines and answers to 'what time is it?' can be off by an hour or more, particularly around DST.
- effort: Small to medium: typed context fields, resolver tests across DST boundaries, and updates to routines/briefing/time responses.  ·  risk: Existing routines could shift if migrated incorrectly. Preserve their original timezone and preview all next-run changes before applying; fall back to the owner fact until explicitly changed.
- cost: Negligible API cost; no hardware cost.  ·  latency: No meaningful runtime impact; one additional context lookup for time-sensitive responses.
- security: Low. Avoid exposing location inference; store only timezone identifiers and provenance.
- depends on: A typed context projection with source and expiry; Routine scheduler must store timezone per routine rather than inheriting host timezone; Owner confirmation of the authoritative timezone if America/Chicago is not still correct

### `memory` — Introduce an append-only commitment ledger distinct from ordinary notes and reminders. Each entry stores exact source session/pipeline ID, timestamp, speaker attribution state, verbatim evidence span hash, extracted commitment, owner/other-party role, due-date confidence, review status, and retention deadline. A background reconciler may link entries to later calendar/mail/browser evidence but may never rewrite the original evidence; corrections create superseding records.
- **owner gets:** The owner gets a trustworthy answer to 'what did I promise?' instead of an untraceable summary or a reminder detached from the conversation that produced it. They can review, correct, or delete a commitment while preserving why it was suggested.
- effort: Medium to high: schema and durable storage, transcript-span indexing, extraction/reconciliation worker, review surface, and retention/deletion controls.  ·  risk: False attribution or accidental recording of bystanders could damage trust. Require an explicit capture mode, mark uncertain speaker attribution, default to no external follow-up, and support immediate deletion by session or commitment.
- cost: Small storage cost; background model and transcription costs scale with captured conversation minutes. No per-turn realtime increase after capture.  ·  latency: No live interaction impact; extraction target under 60 seconds after a session, with later evidence joins asynchronous.
- security: High sensitivity. Encrypt ledger contents, minimize raw transcript retention, keep source hashes and redacted spans by default, and prevent the browser/Mac agents from seeing unrelated conversation entries.
- depends on: A pendant/relay capture indicator and explicit session-level consent; Durable pipeline/session IDs and transcript-span retrieval; A typed context projection that can expose only the selected commitment to reminders or review; Owner confirmation before any reminder, calendar change, email draft, or browser action is created


## What it asked for

_Nothing._
