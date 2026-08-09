# Harness derivation — unified — round 175

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac/browser readiness** — At round 175, /ops/snapshot reports AI Pendant Agent ready, Accessibility and Screen Recording granted, browser extension online with 9 Safari tabs, relay reachable, and no required permissions missing. Existing watches are present but disabled.
  - evidence: GET /ops/snapshot returned permissions.requiredMissing=[], accessibility.trusted=true, screenRecording.granted=true, browser.online=true, relay.reachable=true; GET /watches returned two disabled watches.

## Capabilities it proposed

### "“Submit this form for me, but show me exactly what will be sent and make me approve it on the pendant first.”"
- **useful because:** This would turn the existing physical approval latch into a complete, trustworthy browser workflow instead of a spoken promise that currently disappears. The owner gets an exact field/value diff, a nonce-bound deliberate button approval, submission, and a receipt proving which browser session submitted what; the Mac never receives a vague 'go ahead' that could drift into a different page.
- **path:** relay-realtime → pendant → browser-extension → mac-planner → relay-realtime
- **model tier:** Use the background/planner tier to inspect and summarize the form; use realtime only for the owner's live spoken interaction. Deterministic code computes the diff, digest, expiry, and receipt.
- **latency:** Preview in 3–5 s; pendant approval prompt within 1 s of preview; submit and receipt within 5 s after approval. Never submit on timeout, page mutation, or dropped approval.
- **cost:** Roughly $0.01–$0.05 per invocation, dominated by one planner call and optional browser-page summarization; digest, diff, and receipt generation are local.
- **security:** Only bound browser tab/session targets may be touched. Do not send passwords, page secrets, or full form contents to the relay. Hash sensitive values and speak only labels plus redacted previews. Require the physical transaction nonce, plan digest, world fingerprint, expiry, and one-time replay guard; abort if the page changes. Submission must remain a separate step from preview.
- **missing:** A production relay implementation of the existing approvalHandoff store contract; A delivery path that presents the approval prompt in an active pendant conversation and records deliveredAt; A browser command that returns a canonical form-field diff and post-submit receipt, rather than a screenshot-only result; A true authorization boundary so approval is not merely another AGENT_TOKEN holder

### "“Run a complete pendant check now and tell me whether the microphone, speaker, bridge, and 24 kHz link are actually healthy.”"
- **useful because:** The owner currently has to interpret serial logs and separate pipeline counters. This gives a single spoken HEALTHY/DEGRADED/FAILED result for the hardware that is physically attached today, with a clear next action. It catches the exact class of regressions that previously produced clicks, dropped mic blocks, bad framing, or a dead ESP32 bridge before a real conversation is lost.
- **path:** pendant → mac-planner → relay-realtime → mac-planner → pendant
- **model tier:** Deterministic fixture and threshold evaluation first; use the background tier only to explain a failed result in plain language. No realtime model is needed unless the owner asks follow-up questions.
- **latency:** 30–60 s for a bounded 10–20 s fixture run and collection of serial/bridge counters; return a partial result within 10 s if one surface is offline. Never inject synthetic audio into an active conversation.
- **cost:** Under $0.01 per run if deterministic; dominated by USB serial capture and fixture duration, not inference.
- **security:** Synthetic audio must be clearly tagged and must not be transmitted as a user recording or persisted to SD. Run only when explicitly requested, stop on an active conversation, bound captured logs, and redact serial identifiers from relay receipts.
- **missing:** A safe Mac-side serial/bridge runner that can invoke the existing J-Link/serial self-test hooks and collect correlated timestamps; An owner-facing orchestration route joining pendant counters, bridge acknowledgements, and pipeline validation into one verdict; A fixture-to-receipt schema with explicit thresholds for mic drops, tx starvation, decode cost, clipping, and frame continuity

### "“Before you do anything risky on my Mac or in my browser, give me a spoken dry-run of the exact changes, let me approve on the pendant, and continue only if the world is unchanged.”"
- **useful because:** This closes the most dangerous current UX gap: blocked plans are spoken about and then discarded, while the owner has no reliable approval control. A digest-bound dry run makes the agent's proposed side effects understandable, and a physical approval plus world recheck makes 'yes' apply to the exact plan rather than whatever the page or files became later.
- **path:** relay-realtime → mac-planner → browser-extension → pendant → mac-planner
- **model tier:** Planner/background tier creates the action summary and risk classification; deterministic code computes replay safety, plan/world digests, expiry, and approval state. Realtime is reserved for speaking the short summary and receiving the owner's next-turn response.
- **latency:** Dry-run in under 5 s for ordinary Mac/browser tasks; approval can remain pending until the next conversation, with a 30-minute expiry. Re-check files/page immediately before dispatch; if changed, explain and require a new preview.
- **cost:** About $0.01–$0.04 per risky invocation, mostly the planner summary; deterministic previews and receipts are negligible.
- **security:** Classify by riskTier and gate continuation by replaySafety, not reversibility alone. Idempotent/additive steps may be resumable only with an unexpired lease; unrepeatable/unknown steps require fresh approval. Never treat a spoken 'sure' detached from the digest as sufficient. Keep secrets out of the spoken preview and bind browser actions to explicit tabs.
- **missing:** Wire orchestrator closeLedger calls so completed plans are not falsely marked interrupted; Implement the existing relay approvalHandoff persistence and pending-approval selection; Deliver approval prompts during the next active conversation (unprompted push is unavailable today); Add a real post-approval execution endpoint with lease/replay checks and a browser-bridge supervisor sweep; Separate approval authority from the execution AGENT_TOKEN

### "“Watch this browser page until the condition I named is true, then stage the action for me—but never commit it without my pendant approval.”"
- **useful because:** This turns a passive watch into a safe, delayed agent: it can notice a price, appointment slot, or availability change while the Mac and relay are unattended, prepare the exact action, and wait for a deliberate physical approval. The owner gets leverage without granting an always-on agent permission to purchase, send, or book.
- **path:** relay-realtime → browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Background tier evaluates the condition and summarizes changes; deterministic code schedules polls, binds the target tab, freezes the action digest, and enforces expiry. Realtime is used only when the owner returns or asks for status.
- **latency:** Poll interval configurable from 1 minute to 1 hour; stage within 5 s of detecting a change; approval remains valid for at most 30 minutes and expires on page mutation or target loss.
- **cost:** About $0.001–$0.02 per poll depending on whether page extraction is deterministic or needs a model; one planner call only when the condition becomes true.
- **security:** Allowlist the exact URL/tab and selector or semantic condition. Do not click or submit during polling. Redact account data from relay logs. On trigger, create a one-time digest-bound staged action and require the physical transaction nonce; cancel when the page, amount, recipient, or world fingerprint changes.
- **missing:** A durable conditional-watch record that survives Mac/browser restarts and has an explicit owner binding; A browser extraction/condition evaluator with evidence snapshots rather than screenshots alone; The relay approval persistence and next-conversation delivery path already identified as missing; A lease and deduplicated trigger record so a reconnect cannot stage the same action twice

### "“When I have a meeting, put the pendant and Mac into a private meeting mode, and prove afterward that the microphone, speaker, browser exposure, and notifications were actually controlled.”"
- **useful because:** The owner should not have to remember a privacy ritual before every meeting. Calendar context can stage the mode, but the pendant’s local privacy latch remains the final authority. Afterward, a convergence receipt would prove what was muted, what was stopped, and whether any queued browser or audio data remained exposed.
- **path:** mac-planner → relay-realtime → pendant → browser-extension → mac-planner
- **model tier:** Deterministic calendar matching, latch state, queue state, and convergence checks; background tier only summarizes conflicts or exceptions. No realtime inference is needed.
- **latency:** Stage within 30 seconds of a matching calendar event; local mute must still occur immediately on physical confirmation. Produce a convergence receipt within 5 seconds of the latch state change and again when the meeting ends.
- **cost:** Near-zero model cost; dominated by local state checks and one short optional explanation.
- **security:** Calendar titles and attendees must stay local or be minimized. Automatic staging must never override the owner’s local latch semantics. If the device cannot confirm capture/playback/relay/browser shutdown, report UNKNOWN rather than claiming privacy. Meeting mode must expire explicitly and never silently unmute a latched microphone.
- **missing:** A calendar-to-privacy-mode policy with owner-configurable matching rules; A cross-surface convergence receipt that includes browser exposure and queued work, not only pendant state; A safe conflict rule for an already-active conversation or an existing local privacy latch; An owner decision about whether meeting titles/attendees may leave the Mac

### "“Research this question, keep every important claim tied to its source, and if I later ask you to act on it, refuse to use facts whose evidence has gone stale.”"
- **useful because:** This would make research useful for consequential decisions rather than producing an attractive but untraceable answer. The owner gets a compact spoken briefing plus durable claim-level provenance; a later browser or Mac action can be gated on source freshness and can show exactly which claims authorize the action.
- **path:** relay-realtime → browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Background/planner tier gathers and compresses sources; deterministic code stores claim IDs, hashes, timestamps, source bindings, and freshness rules. Realtime only speaks the short result or answers a follow-up.
- **latency:** Initial briefing in 15–60 seconds depending on source count. Provenance lookup under 2 seconds. Any action based on stale or conflicting claims pauses for a new research pass.
- **cost:** Approximately $0.03–$0.20 per research request, dominated by retrieval and synthesis; follow-up provenance checks are negligible.
- **security:** Bind sources to explicit URLs or browser sessions and preserve redacted excerpts rather than unrestricted page dumps. Do not treat a source hash as proof that the source is trustworthy. Conflicting claims must remain visible. Actions must require separate approval and must not inherit authorization from research.
- **missing:** A claim-level provenance store with source snapshots, freshness/expiry, and conflict states; A browser evidence adapter that returns stable excerpts and page timestamps; A policy connecting evidence freshness to downstream Mac/browser plans; A compact pendant-readable citation format

### "“Do this multi-step task, but only call it finished when the requested outcome passes its checks; if the Mac or browser dies halfway through, recover without repeating an unrepeatable step.”"
- **useful because:** Today the system can plan and execute actions, but the owner cannot ask for an outcome with a verifiable completion contract. This capability would distinguish 'the command ran' from 'the result is true', recover safely after an outage, and leave a spoken proof or an explicit blocked state instead of a confident half-success.
- **path:** relay-realtime → mac-planner → browser-extension → relay-realtime → pendant
- **model tier:** Planner tier decomposes the request and writes acceptance checks; deterministic execution, replay-safety classification, leases, verification, and rollback handle the workflow. Realtime only reports milestones or asks for approval.
- **latency:** Plan and checks within 5 seconds for ordinary tasks; verification immediately after each phase; recovery begins within one lease interval after reconnect. Never replay an unrepeatable step without fresh approval.
- **cost:** Approximately $0.02–$0.10 per task, dominated by planning and occasional verification; retries should reuse prior context rather than resynthesize.
- **security:** Gate recovery on replaySafety, not merely reversibility. Persist an inflight record before dispatch, bind browser tabs and file fingerprints, and stop all later phases after an uncertain result. Never claim completion from a missing receipt. Sensitive evidence should be redacted in spoken and relay-visible summaries.
- **missing:** A production trigger for the existing resume engine; Correct ledger closure for completed orchestrator runs; Leased relay jobs with expiry and requeue; Invocation of the existing workbench transaction commit/verification path; A completion-contract schema expressing checks, tolerances, and unacceptable partial success


## Changes it proposed to its own stack

### `integration` — Build a 'return-to-conversation handoff' spanning the relay, Mac/browser jobs, and pendant: when a long-running or approval-blocked job finishes while the pendant is offline, retain a compact spoken-ready card (what changed, what evidence exists, what decision is pending), bind it to the next conversation turn, and mark it consumed only after a delivery receipt. If the owner reconnects over USB today, use the USB session as the local delivery path; if LTE is later available, use the relay inbox. Never replay a completed card or silently execute a pending one.
- **owner gets:** The owner can leave the desk, lose the link, and come back without asking 'what happened?' repeatedly or missing a dangerous approval. The pendant becomes the place where unfinished work reliably meets him, while the Mac/browser remain free to finish work asynchronously.
- effort: Medium: a durable compact-card schema, relay selection/ack endpoints, Mac job-to-card adapter, and pendant/USB delivery integration. Can be prototyped against the currently USB-attached hardware before LTE registration.  ·  risk: Stale or duplicated spoken cards, especially across USB-to-LTE handoff; mitigate with jobId+cardId+turn sequence, expiry, idempotent acknowledgement, and explicit pending-vs-completed state. Do not include raw page secrets or full audio.
- cost: Negligible storage and model cost; one short background summarization per completed asynchronous job. USB serial and relay receipts dominate engineering effort, not API spend.  ·  latency: Card generation under 2 s after job completion; delivery on the next natural conversation turn, with no unsolicited audio interruption.
- security: Only bound job/session recipients receive cards. Pending approvals remain inert until physical approval; delivery receipts prove presentation, not consent. Redact sensitive browser fields.
- depends on: A relay-backed pending-card store and delivery receipt route; USB fallback audio session firmware work already accepted; A caller that emits closeLedger/settled status for completed action ledgers; An explicit policy for retention/deletion of cards (owner decision still outstanding)


## What it asked for

_Nothing._
