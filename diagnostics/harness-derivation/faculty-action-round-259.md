# Harness derivation — faculty-action — round 259

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Do this whole multi-step task, but if any step cannot be verified, stop safely and undo only what you can.”"
- **useful because:** The system can finally act across Mac, browser, and iPhone without claiming success from executor receipts alone. A dependency-aware saga would verify each postcondition, pause for the pendant’s existing physical approval latch when required, and compensate reversible steps when a later step fails.
- **path:** relay → mac-planner → mac-vision → browser → iOS → pendant → dashboard
- **model tier:** Background planner for the dependency graph; realtime only for the owner’s spoken clarification; cheap verifier/perception model for each postcondition.
- **latency:** Plan in under 3 seconds; each step may take normal UI time; surface a verified/unknown result within 2 seconds of the final check.
- **cost:** Moderate: one planning call plus cheap per-step verification; dominant cost is Mac/browser execution time, not tokens.
- **security:** Never pass page secrets to the pendant or relay. Require the existing physical transaction approval latch for destructive or external-send steps. On uncertainty, stop rather than infer; compensation must be explicitly bounded and logged.
- **missing:** Saga/dependency execution coordinator with durable compensation records; A narrow live verifier route behind the currently unresolved verify_operation_step schema; Per-step compensation declarations in POST /plan and POST /execute

### "“When I press the bookmark button, remember exactly what I was doing across the pendant conversation and my Mac/browser so I can ask about that moment later.”"
- **useful because:** The existing bookmark can become genuinely useful rather than an isolated timestamp: one deliberate sw1 press creates a compact, ordered marker joining the conversation event, foreground Mac app, browser tab/session identity, and relay receipt. It works offline and later answers “what was I doing then?” without continuously recording audio.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** No expensive model for capture; background model only when the owner later asks to summarize or search markers.
- **latency:** Haptic acknowledgement under 150 ms locally; host snapshot within 1 second; durable relay merge when connectivity returns.
- **cost:** Negligible capture cost; occasional small background summarization call. Storage is a few hundred bytes per marker plus existing references.
- **security:** Default to IDs, timestamps, app name, URL origin/title only; redact URL query strings and private fields. Never copy microphone contents. Markers created offline must remain ordered and deduplicated when merged.
- **missing:** A signed clock/sequence correlation between pendant sw1 events and Mac/browser observation; A privacy-redacting context snapshot endpoint that joins GET /observe and GET /browser/status; A query surface over merged markers

### "“I missed the last answer—turn the wheel back one notch and play it again.”"
- **useful because:** This gives the owner a reliable, physical, private rewind control without asking them to repeat a long request. The future rotary encoder selects a recent response ID; the relay re-delivers the existing audio artifact, and the pendant reports whether playback actually started or was interrupted.
- **path:** pendant → relay-realtime → Mac bridge → dashboard
- **model tier:** No model for selection or replay; realtime audio transport only. Use a cheap background model only if the owner asks for a transcript or summary.
- **latency:** Wheel selection/haptic feedback under 100 ms; replay begins within 500 ms when the artifact is cached; otherwise report queued/retry state.
- **cost:** Near-zero inference cost; bandwidth dominates only when the artifact must be fetched again.
- **security:** Wheel events select opaque response IDs, never raw transcript text. Expire private artifacts promptly, enforce owner/session binding, and do not replay while an active response is speaking unless the owner explicitly clicks to interrupt.
- **missing:** Rotary encoder and second-button hardware integration requested by the owner; Pendant firmware wheel event protocol and compact recent-response index; Relay endpoint that maps response ID to the existing audio delivery ACK/retry queue

### "“Before you change anything, check my calendar, the relevant email or message, and the live browser state; if they disagree, ask me one precise question instead of guessing.”"
- **useful because:** Today the system can act on one surface while silently missing contradictory facts on another. This capability makes contradiction itself a first-class result: it gathers fresh evidence across authenticated Mac apps, browser sessions, and iPhone state, explains the smallest conflict, and asks only the decision the owner must make.
- **path:** relay → mac-planner → mac-vision → browser → iOS → pendant
- **model tier:** Cheap background extraction and entity matching; realtime model only for the final clarification spoken to the owner.
- **latency:** Under 5 seconds for a normal three-source check; clarification must be delivered before any mutation.
- **cost:** Low-to-moderate inference cost; browser and iPhone observation latency dominates.
- **security:** Read only until contradiction resolution. Keep message bodies and calendar details on the Mac where possible; send only hashes, entities, and minimal conflicting snippets to the relay. Never choose a side automatically for dates, recipients, amounts, or permissions.
- **missing:** A cross-surface evidence correlator with source timestamps and freshness bounds; Structured iOS observation results that can be compared with Mac/browser entities; A pendant-friendly contradiction summary and answer protocol

### "“Tell me exactly what changed after you finished—files, settings, messages, and browser state—and let me inspect the sensitive parts only if I ask.”"
- **useful because:** A success receipt is not the same as understanding the impact of an action. The owner should receive a compact, source-linked change report that distinguishes created, modified, deleted, sent, and merely viewed artifacts, with before/after hashes by default and local snippets only on demand.
- **path:** relay → mac-planner → mac-vision → browser → iOS → pendant → dashboard
- **model tier:** Cheap deterministic diffing and hashing first; background model summarizes only the selected changes.
- **latency:** Initial report within 3 seconds after completion; deeper inspection on demand within 2 seconds for local evidence.
- **cost:** Low model cost; storage and local diff computation dominate.
- **security:** Default evidence is hash-only. Secrets, private message bodies, and page contents stay local unless the owner explicitly requests a snippet. Reports must distinguish observed from inferred changes and retain provenance.
- **missing:** A normalized cross-surface change ledger covering Mac files/apps, browser fields, and iPhone state; Before-state capture that is bounded and privacy-aware; Dashboard and pendant rendering for a compact change summary


## Changes it proposed to its own stack

### `interaction` — Add a cross-surface “decision checkpoint” protocol: when an operation depends on a value with multiple plausible interpretations (date, recipient, account, amount, or scope), freeze the operation, present the competing normalized choices on the Mac/browser and a short numbered summary through the pendant, then accept one explicit choice and bind that choice into the operation hash before execution.
- **owner gets:** The owner stops having to notice hidden ambiguity after an action has already happened. One short answer resolves the exact choice while preserving a durable record of what they selected.
- effort: High: requires shared normalization across Mac, browser, iOS, relay, and pendant input, plus operation-hash binding.  ·  risk: A stale or incomplete source could omit a choice; default must be no execution. Recovery is to expire the checkpoint and recompute from fresh state, never silently reuse it.
- cost: Small inference cost for normalization; browser/iOS observation and evidence storage dominate.  ·  latency: Adds 1–5 seconds only when ambiguity exists; no cost on unambiguous operations.
- security: Only opaque option IDs and minimal labels need reach the pendant. Sensitive values remain on the Mac; selected option hash prevents substitution between approval and execution.
- depends on: A typed cross-surface evidence correlator; Fresh state timestamps for Mac/browser/iOS observations; Operation hash support in the existing approval and receipt ledger


## What it asked for

_Nothing._
