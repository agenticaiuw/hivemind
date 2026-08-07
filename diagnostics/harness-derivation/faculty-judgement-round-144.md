# Harness derivation — faculty-judgement — round 144

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“I just left a meeting—capture what I promised, check the source documents, and put only the real follow-ups on my calendar.”"
- **useful because:** The pendant gives the owner a one-button or spoken meeting exit. The relay records a short local-first note; Mac uses Calendar/Mail/Notes and the open browser tabs to identify attendees, documents, and existing deadlines; the system distinguishes an actual commitment from a vague thought, drafts tasks and reminders, and reads back a three-item confirmation. This closes the gap between remembering a promise and doing it, without pretending a transcript is a plan.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Realtime only for the brief capture and one clarification; a cheaper background model extracts commitments and deduplicates them against Calendar/Notes; deterministic Mac actions create reminders after confirmation.
- **latency:** Acknowledge the button within 300 ms, give a first spoken summary within 8 s, and finish source checking in under 60 s. If the Mac or browser is unavailable, preserve the note and reconcile on reconnect.
- **cost:** About $0.01–$0.05 per meeting exit, dominated by transcription and background extraction; deterministic Calendar/Notes reads and reminder creation add negligible API cost.
- **security:** Meeting audio and private documents leave the pendant only to the relay/Mac pipeline; default to a 90-second clip with automatic deletion after extraction. Never infer a commitment from a third party as fact; show source snippets and require confirmation before creating or sending anything. No email is sent.
- **missing:** A bounded pendant capture trigger and local clip handoff over the currently USB-connected serial path; A commitment extractor that stores source, confidence, owner/other-person attribution, and due-date uncertainty; A cross-source deduplicator and confirmation UI/audio card for proposed follow-ups

### "“Before my week gets away from me, find the three decisions I’m silently postponing, show me the smallest next step for each, and ask me one at a time.”"
- **useful because:** Most assistants report tasks; they do not notice unresolved choices hiding across calendar conflicts, reminders, notes, drafts, and logged-in pages. A background weekly scan would cluster evidence into decision candidates, rank by consequence and approaching deadline, and use the pendant for a deliberately tiny, interruptible decision conversation. The result is not a longer to-do list: each item becomes decide, delegate, schedule, or consciously drop, with a dated record of why.
- **path:** relay → mac-planner → browser-extension → pendant → dashboard
- **model tier:** Cheap background model performs clustering and consequence ranking; realtime is used only when the owner engages with one decision; deterministic routes write the chosen next step.
- **latency:** Scan completes while the owner sleeps; the spoken interaction is under 20 seconds per item and can pause/resume across the pendant and Mac.
- **cost:** Roughly $0.03–$0.15 per weekly scan depending on document/page volume; realtime cost is limited to decisions the owner actually opens.
- **security:** The scan touches sensitive notes, mail metadata, calendar, and authenticated pages. Keep raw evidence local on the Mac where possible, send only short candidate claims to the relay, attach source links/snippets, and never infer that a person is committed without owner confirmation. Quiet hours and an explicit weekly opt-in are mandatory.
- **missing:** A decision-candidate schema separating facts, options, owner commitments, and uncertainty; A consequence/urgency ranker that can explain its top-three selection; A durable decision record with a revisit date and a spoken pause/resume protocol

### "“Pressure-test this before I commit: look for evidence in my calendar, notes, mail, and the logged-in page, tell me the strongest reason not to do it, and give me a reversible first step.”"
- **useful because:** The system should be a judge, not merely an executor. This invokes a deliberate dissent pass over the owner’s actual private context: conflicts, hidden deadlines, prior notes, cancellation terms, and missing information. It returns a short argument against the plan, confidence and citations, then stages a low-cost experiment instead of pushing straight to an irreversible action. The pendant makes this available while walking; the Mac and browser reach sources no single surface can see.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** A cheaper background model gathers and normalizes evidence; a stronger model performs the bounded adversarial synthesis only after evidence is assembled; realtime handles the spoken result and one clarification.
- **latency:** Return a spoken go/no-go-risk summary within 15 seconds for open tabs and local sources; allow up to two minutes for a logged-in multi-page investigation. Never block the owner’s other work while investigating.
- **cost:** Approximately $0.02–$0.20 per pressure test, mostly page extraction and synthesis; use cached evidence and only re-read sources whose freshness matters.
- **security:** This is intentionally high-context and can expose sensitive plans. Keep evidence scoped to named tabs/apps, do not search unrelated accounts, cite every claim with timestamp/source, and treat missing evidence as unknown rather than reassurance. It must not autonomously cancel, purchase, send, or publish; staged actions require the existing confirmation policy.
- **missing:** A scoped evidence-bundle compiler spanning local sources and authenticated tabs; A dissent rubric that separates factual blockers, value tradeoffs, and unknowns; A reversible-experiment planner with explicit cost, expiry, and postcondition

### "“A month after an important decision, show me what I expected, what actually happened, and one thing I should do differently next time.”"
- **useful because:** The system currently helps decide and act, but cannot help the owner learn whether their judgment was calibrated. This creates a private, evidence-backed decision postmortem: recover the original rationale and prediction, inspect later Calendar, Mail, Notes, and authenticated-page outcomes, distinguish outcome from luck, and offer one behavioral adjustment. It turns the pendant from an answer machine into a long-term improvement loop without requiring the owner to maintain a journal.
- **path:** relay → mac-planner → browser-extension → pendant → dashboard
- **model tier:** A cheap scheduled model performs outcome matching and extracts factual deltas; a stronger model is used only for the short causal interpretation; realtime is reserved for the owner’s optional spoken reflection.
- **latency:** Run asynchronously on a monthly or decision-specific schedule; deliver a two-minute spoken review or a compact dashboard card when the owner chooses, never interrupting them unexpectedly.
- **cost:** About $0.03–$0.20 per review, dominated by source retrieval and synthesis; use hashes and cached snapshots to avoid rereading unchanged pages.
- **security:** Decision rationale may contain sensitive personal or financial information. Keep raw evidence on the Mac, retain only a compact private summary and source hashes, allow deletion, and never turn a single outcome into a durable personality judgment. The owner must be able to mark an outcome as unknowable or irrelevant.
- **missing:** A durable prediction-and-rationale record created at decision time; A later-outcome matcher spanning local and authenticated sources with temporal boundaries; A calibrated postmortem rubric that separates controllable choices, luck, and missing information


## Changes it proposed to its own stack

### `integration` — Add a first-class “dissent mode” execution branch: before any owner-approved consequential plan, compile a scoped evidence bundle from the named Safari tabs, Calendar/Mail/Notes metadata, and recent capture; classify each claim as blocker, tradeoff, or unknown; require the synthesis to produce one cited counterargument and one reversible experiment. Surface it as a 20-second pendant card/audio response, with an expiry and explicit “proceed anyway” decision recorded separately from the action receipt.
- **owner gets:** It gives the owner a trusted second opinion grounded in their real private context, catching conflicts and forgotten cancellation terms before money, time, or reputation are spent.
- effort: Medium-high: evidence scoping and provenance are partly present, but the classifier, counterargument rubric, experiment planner, and pendant response need implementation and tests across browser-unavailable and stale-source cases.  ·  risk: False alarms could create decision fatigue; unsupported counterarguments could erode trust. Mitigate with source citations, an uncertainty label, a configurable threshold, and a bypass that never silently changes the planned action. Recover by replaying the original plan without dissent mode.
- cost: Low incremental API cost when evidence is cached; synthesis adds roughly one background model call and occasional realtime response. Storage is a small decision record plus hashes, not raw private pages.  ·  latency: Adds 5–15 seconds before a consequential action when invoked; no latency for ordinary reversible actions.
- security: High-context private data is joined temporarily. Enforce named-source scope, local-first extraction, redaction before relay, short retention, and no transmission of raw page content unless the owner explicitly asks.
- depends on: A provenance-bearing evidence bundle across /research, /browser/inspections, /journal, and /capture; A typed reversible-experiment and postcondition representation; The existing action receipt/undo path, with a separate owner decision record

### `memory` — Create a user-visible prediction ledger for consequential decisions. At the moment the owner chooses a path, store the exact expectation, time horizon, confidence, alternatives rejected, and evidence snapshot; later, a scheduled evaluator asks the owner whether the outcome is observable, matches it against fresh Mac/browser evidence, and produces a non-moralizing calibration report with an explicit luck/unknown category. Allow the owner to correct or delete every inference.
- **owner gets:** They can learn from real decisions instead of relying on vague memory or hindsight. The pendant can deliver one useful lesson at a time, while the dashboard preserves the evidence needed to trust it.
- effort: High: this needs a new durable schema, capture at decision time, temporal evidence matching, outcome adjudication, and careful evaluation against fabricated causality.  ·  risk: The system could overfit noisy outcomes, expose sensitive history, or make the owner feel judged. Mitigate with explicit confidence, an unknowable outcome state, source citations, owner edits, deletion, and no personality labels.
- cost: Small storage cost; one scheduled background synthesis per reviewed decision, approximately $0.03–$0.20 depending on source volume.  ·  latency: No impact on ordinary actions; capturing a prediction adds under one second, while reviews run asynchronously.
- security: Decision histories are highly sensitive. Keep raw snapshots local-first, transmit only minimized claims, encrypt retained records, enforce per-item retention, and require explicit opt-in to cross-link private browser sources.
- depends on: A durable decision-time prediction record; Temporal matching of later Calendar/Mail/Notes/browser evidence; A background evaluator that can abstain when outcomes are unknowable; Pendant audio delivery for the concise lesson


## What it asked for

_Nothing._
