# Harness derivation — relay-realtime — round 267

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Turn this thought into a finished, filed result later—research it, draft it in the right app, and tell me what you decided to leave unresolved.”"
- **useful because:** Offline voice memos can preserve words, but today they do not become useful work. This would bridge the worn device's fleeting capture to authenticated browser research and Mac artifact creation, while preserving uncertainty instead of silently producing a half-finished document.
- **path:** pendant → relay → mac-planner → mac-vision → browser → dashboard
- **model tier:** Realtime handles only capture confirmation and a one-sentence result; background uses a cheaper planner/research model, with the Mac/browser agents doing local authenticated actions.
- **latency:** Capture confirmation under 1 second; owner need not remain connected. First progress event within 30 seconds of a worker becoming available; completion is asynchronous.
- **cost:** One short realtime call, then typically 2–6 background research/planning calls and a few browser/Mac actions. Browser computer-use screenshots dominate cost.
- **security:** The memo is sensitive and must be scoped to voice. Authenticated pages never leave the Mac/browser session. Filing or sending external communications must produce an explicit proposed artifact and an auditable receipt; unresolved claims must be spoken as unresolved.
- **missing:** A durable memo-to-work item promotion path with provenance from the pendant recording; Background worker execution for queued work (not merely a user-facing reminder); Artifact provenance linking each draft claim to browser/page evidence and each mutation to a receipt; A relay inbox payload that can carry a concise result plus unresolved items

### "“Before I rely on it, make the pendant work: test the radio, audio, button, and Mac bridge, repair anything safe to repair, and tell me precisely what still needs my hands.”"
- **useful because:** The owner should not discover a dead microphone or broken bridge during an important away-from-Mac conversation. Today health information is fragmented and a physical USB-connected pendant is real but not self-validating. A guided preflight would turn the whole wearable/relay/Mac chain into something trustworthy, and distinguish a recoverable software fault from a hardware action the owner must perform.
- **path:** pendant → relay → mac-planner → mac-vision → dashboard
- **model tier:** Use deterministic probes and a cheap background diagnostic model; reserve realtime for the spoken verdict and only use the expensive tier to interpret ambiguous test output.
- **latency:** USB preflight in 10–20 seconds; LTE path check can continue asynchronously. Speak a three-state verdict (ready/degraded/owner action) immediately after each phase.
- **cost:** Usually no model call; one cheap interpretation call only for anomalous logs. Hardware test traffic and Mac shell execution dominate, not API tokens.
- **security:** Firmware flashing and destructive resets must be explicit owner actions, never inferred from a voice request. Diagnostics may contain device identifiers and logs; keep raw traces local/dashboard-scoped and speak only the minimum. Do not save routine audio captures beyond the existing failure-only policy.
- **missing:** A versioned pendant diagnostic protocol covering nRF9160, ESP32 bridge, codec counters, button/LED, and relay acknowledgements; A Mac USB harness that can run bounded tests against both live serial devices and return signed results; Safe repair recipes with rollback (restart bridge, clear stale session, reflash only after explicit confirmation); A relay health state that correlates pendant, bridge, transport, and audio-path results instead of reporting last-seen alone


## Changes it proposed to its own stack

### `interaction` — Add a spoken, evidence-backed “why did you do that?” mode: after any Mac or browser job, the pendant can ask for the exact decision chain, affected artifacts, skipped alternatives, and current reversibility window; the relay retrieves structured receipts and has a cheap model compress them into a short answer, with a longer dashboard trace on demand.
- **owner gets:** The owner can currently hear that work finished, but cannot interrogate the result from the pendant. This makes autonomous action understandable while walking or away from the Mac, and catches wrong assumptions before they become forgotten state.
- effort: Medium: normalize plan/action/receipt evidence into a decision trace, add a job-linked spoken query path, and render a dashboard drill-down. No new physical hardware required.  ·  risk: A summarizer could invent rationale. Every sentence must be grounded in receipt fields; if evidence is absent, say so. Sensitive browser text should be redacted in the spoken answer and retained only in the local session.
- cost: One inexpensive summarization call per inquiry; no continuous inference or audio storage.  ·  latency: Target under 2 seconds for a short trace from existing receipts; dashboard detail can load asynchronously.
- security: Adds a new way to expose action evidence through voice, so apply existing surface scoping and redact secrets, tokens, and page text.
- depends on: GET /jobs/:jobId/receipts; GET /journal/:jobId; GET /memory/projection; A real relay event/completion delivery path for queries after the original session


## What it asked for

_Nothing._
## Its own summary

Recorded three non-duplicate directions: (1) promote an offline thought into researched, provenance-linked work and a filed artifact; (2) let the owner interrogate the evidence and rationale behind any completed Mac/browser action from the pendant; (3) provide a cross-stack wearable preflight that tests and safely repairs the nRF9160, ESP32 bridge, transport, and audio chain. The first attempted away/home resumable-work proposal was correctly rejected as already covered, so I did not restate it.

**Biggest unknown:** The missing pieces are mostly not model features: durable memo-to-work promotion and background execution, evidence-grounded decision-trace retrieval, and a versioned diagnostic/repair protocol plus bounded USB harness for the two physically connected chips. I could not discover further this round as instructed.

