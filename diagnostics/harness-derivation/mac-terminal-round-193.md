# Harness derivation — mac-terminal — round 193

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“If something urgent arrives, interrupt me only when I can act, tell me why, and let me say ‘handle it’ or ‘snooze it’ from the pendant.”"
- **useful because:** The Mac can see the focused app, the browser can see authenticated work sessions, and the relay can keep triage alive while the Mac sleeps. Combining those lets the system suppress low-value notifications, detect urgency in the actual session, and make the pendant a two-way decision point instead of another notification light.
- **path:** relay-realtime → mac-planner → mac-vision → browser-extension → unified
- **model tier:** background for continuous event classification; realtime only for the short spoken interruption and the owner's reply
- **latency:** Urgent event to pendant decision in 2–5 seconds; snooze/handle acknowledgement under 1 second once the link is live.
- **cost:** Roughly $0.001–$0.01 per event batch depending on classification model; most events should be filtered locally from browser/Mac metadata and never reach a model.
- **security:** Browser titles, focused-app metadata, and possibly notification text leave the Mac. Redact secrets and page bodies by default; require explicit per-site enrollment for authenticated content. ‘Handle it’ must be scoped to the specific event and produce a receipt.
- **missing:** A Mac/browser event stream that emits notification and focus changes with source, timestamp, and sensitivity labels; An urgency/actionability policy with per-site rules and a durable snooze state; A relay command path that maps a pendant acknowledgement to the exact event, rejects stale acknowledgements, and reports the result

### "“Do this across my Mac and logged-in browser, and do not tell me it is done until you can prove the final state; if a step fails, repair it or tell me exactly where it stopped.”"
- **useful because:** Today mac_delegate and browser_run_actions can perform steps, but completion is mostly a model assertion. A postcondition contract would make the system trustworthy for real work such as submitting a form, exporting a file, or changing a setting: the owner gets proof, not optimism, and a precise recovery point after partial failure.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** cheap model for step selection and deterministic checks; realtime only for exceptions and the final spoken result; expensive reasoning only when recovery is ambiguous
- **latency:** Normal tasks add less than 2 seconds for verification per step; failed tasks may continue for up to 60 seconds while attempting one bounded repair before asking the owner.
- **cost:** About $0.002–$0.03 per task; deterministic URL/file/process checks dominate neither tokens nor latency, while ambiguous repair is the expensive case.
- **security:** Verification may inspect authenticated pages and local files. Keep evidence as hashes, URLs, titles, and redacted excerpts rather than raw screenshots by default. Destructive repair remains under the owner's existing maximum-access policy, but every attempted repair needs a durable action receipt.
- **missing:** A typed postcondition language covering browser URL/DOM predicates, file hashes, app state, and command exit status; A cross-surface transaction record linking pendant request, Mac job, browser command, evidence, and repair attempts; A recovery planner that resumes from the last verified checkpoint without repeating already-confirmed side effects

### "“Take the document I mean, remove the sensitive fields I name, upload the redacted copy to the authenticated site, and leave the original untouched.”"
- **useful because:** This joins a reach only the Mac and browser together have: selecting a local artifact, transforming it, and using an already-authenticated session. The pendant makes the request while away from the keyboard; the system can show a preview/hash and keep the original intact, avoiding the common failure where browser automation cannot reach local files safely or the wrong document is uploaded.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-action
- **model tier:** background model for file identification and redaction suggestions; realtime for the owner's spoken specification and final confirmation; deterministic tools for copying, transforming, hashing, and upload
- **latency:** Identify and preview in 3–8 seconds; upload after confirmation in under 15 seconds for ordinary PDFs/images.
- **cost:** Approximately $0.005–$0.05 per document, dominated by OCR/redaction reasoning; local copy/hash/upload orchestration is negligible.
- **security:** The original and redacted derivative are sensitive. Keep transformation local, never send the original to a cloud model, display exact removed fields and a content hash on the pendant/Mac, and require explicit confirmation immediately before browser upload. Site origin and selected file must be spoken back.
- **missing:** A local artifact picker/export capability that returns stable file identity and hash without exposing contents; A local redaction/OCR pipeline with a reversible derivative and a machine-readable redaction manifest; A browser-extension upload primitive that accepts a specific local path or approved file token and returns the destination origin plus upload receipt

### "“If I say ‘stop everything’ or press the pendant’s emergency control, immediately halt every Mac and browser task, close any sensitive browser session, and tell me exactly what was stopped and what may already have changed.”"
- **useful because:** The owner currently has no trustworthy global abort: cancelling a job is cooperative, a running shell may continue, browser commands may already be queued, and there is no single pendant-visible inventory of active work. A real emergency stop is the difference between delegating confidently and having to watch every action.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → faculty-action
- **model tier:** Firmware and relay perform the stop deterministically; a cheap background model summarizes affected jobs afterward; realtime speaks only the short confirmation and uncertainty report.
- **latency:** Local pendant acknowledgement immediately; relay-to-Mac/browser kill and session quarantine within 1 second when connected; truthful impact summary within 5 seconds.
- **cost:** Near-zero model cost for the stop itself; roughly $0.001–$0.01 for a post-stop summary when many jobs were active.
- **security:** The stop command must be authenticated to the paired pendant and protected against stale/replayed events. Closing browser sessions can discard unsaved work, so report that possibility. Never claim a process was stopped until the host returns a termination receipt; offline, show queued-stop state rather than inventing completion.
- **missing:** A privileged host-side kill-switch endpoint that terminates active child process groups and marks queued actions cancelled; A browser-extension emergency handler that rejects queued commands, aborts in-flight actions where possible, and optionally quarantines or closes enrolled sensitive sessions; A relay-wide active-work registry keyed by pendant request, Mac job, and browser command, plus an offline pendant event type for exactly-once emergency stop delivery; A compact impact report distinguishing stopped-before-start, terminated, completed-before-stop, and unknown

### "“Prepare the whole change in a safe draft first, show me exactly what would change across my files and browser, and commit it only when I say ‘ship it’.”"
- **useful because:** The owner can currently ask for actions, but multi-step work often mixes irreversible local edits with authenticated browser mutations. A cross-surface draft/commit mode would let them delegate confidently: the Mac works on copies or staged patches, the browser stays in preview/draft state, and one pendant decision commits the coherent bundle.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → faculty-judgement → faculty-action
- **model tier:** background model for constructing the draft and summarizing diffs; realtime only to explain the preview and receive the commit phrase; deterministic executors for staging and commit.
- **latency:** Preview in 5–20 seconds depending on files and site; commit acknowledgement under 2 seconds after the explicit phrase.
- **cost:** About $0.01–$0.10 per draft for diff summarization and browser state interpretation; local staging is cheap.
- **security:** Draft copies may contain private data and browser sessions may support side effects even in preview. Keep drafts local, bind commit to a nonce and exact preview hash, expire stale previews, and clearly report anything the target site cannot stage transactionally.
- **missing:** A cross-surface draft manifest containing file patches, browser mutations, preview hash, expiry, and commit scope; Mac filesystem/app adapters that can stage and atomically apply or roll back supported edits; Browser adapters for dry-run/draft semantics and a commit-token protocol for sites that do not natively support drafts; Pendant confirmation that speaks the scope and rejects a changed or expired preview

### "“When I come back, give me a short, trustworthy account of what changed while I was away across my Mac and logged-in browser, with links to the exact items and no repeated noise.”"
- **useful because:** Existing status and job tools answer what the system did, not what changed in the owner’s working world during an absence. A return brief would reconcile browser session changes, local project activity, completed/failed delegated work, and the pendant’s offline interval into one deduplicated account, so the owner can resume without manually reconstructing time.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-judgement
- **model tier:** Cheap background change detector and deduplicator; realtime only when the owner asks for the spoken brief or a follow-up.
- **latency:** First answer in 3 seconds from an incremental index; deeper item verification under 10 seconds.
- **cost:** Around $0.002–$0.02 per return brief; incremental hashes and metadata avoid resending page bodies or full transcripts.
- **security:** The index can reveal sensitive sites and files. Encrypt it locally, use per-source retention and sensitivity labels, redact content by default, and require explicit enrollment for authenticated browser origins. Never summarize a change without a source timestamp and stable link/path.
- **missing:** A local append-only change index for focused apps, project files, delegated jobs, and enrolled browser sessions; Browser page/session diffs that retain stable item identity and timestamps without storing full private pages; A cross-source deduplication model that groups the same event seen in browser, Mac, relay, and pendant records; An offline interval marker and resume cursor shared with the pendant so the brief has a precise boundary


## Changes it proposed to its own stack

### `model-routing` — Create a persistent two-lane task contract: the realtime model handles only the spoken turn, intent extraction, and immediate acknowledgement; once accepted, a cheaper background planner owns execution and emits structured progress milestones and a final evidence bundle. Escalate to the expensive model only on ambiguity, failed verification, or a safety-sensitive interpretation. Carry a compact task state handle instead of replaying the full transcript on every poll.
- **owner gets:** Long Mac/browser work stops monopolizing the voice model or going silent. The owner gets an immediate, honest “started” response, can ask for status later from the pendant, and pays less while still getting deep reasoning exactly when the task gets difficult.
- effort: Medium: task-state schema, routing thresholds, milestone events, and relay-to-Mac status correlation.  ·  risk: A cheap planner may miss intent or overconfidently continue. Start with deterministic escalation triggers (conflicting targets, failed postcondition, authenticated-site change, destructive action) and make the spoken acknowledgement distinguish accepted from completed. Fall back to realtime when the background worker misses its heartbeat.
- cost: Typically 60–90% lower model cost on multi-step tasks; event storage and polling are minor.  ·  latency: Immediate acknowledgement remains sub-second; completion latency is unchanged or slightly lower because the realtime model is not held open.
- security: Compact handles reduce transcript exposure. Sensitive browser/file context is fetched only by the worker that needs it and should be redacted from milestones.
- depends on: A durable task handle shared by relay, Mac job, and browser command records; Structured milestone events on POST /pipeline/events; A final evidence/verification payload rather than free-form completion text


## What it asked for

_Nothing._
## Its own summary

Produced three distinct owner-facing capabilities: (1) urgency-aware interruption triage where the relay, focused Mac app, authenticated browser, and pendant acknowledgement decide whether to interrupt; (2) verified cross-surface task completion that will not claim success without a postcondition and bounded repair; and (3) local-document redaction plus authenticated browser upload while preserving the original. Also recorded a two-lane model-routing change that gives immediate spoken acceptance, cheaper background execution, compact task handles, and escalation only on ambiguity/failure. The shell-lineage receipt proposal was correctly rejected as already covered by existing observability work, so I did not rephrase it.

**Biggest unknown:** The missing pieces are not basic Mac control: they are the event/notification stream, postcondition/evidence schema, local artifact redaction and upload-token primitives, and durable task handles joining relay/Mac/browser records. I still need those capabilities built; no additional permission or duplicate diagnostic tool is needed from me this round.

