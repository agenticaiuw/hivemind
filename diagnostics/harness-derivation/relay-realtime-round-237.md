# Harness derivation — relay-realtime — round 237

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“When I’m at my Mac, carry out this change; if I walk away before it is committed, stop and leave me a clear draft instead.”"
- **useful because:** The pendant can become a physical-presence key for unattended-computer actions: the owner gets powerful automation without a task continuing after they leave the desk. This is materially different from a confirmation prompt because presence is continuously re-checked during a multi-step job, not guessed from the original voice turn.
- **path:** pendant → relay → mac-planner → mac-vision → dashboard
- **model tier:** Realtime relay handles the short spoken command and state changes; mac-planner performs the workflow; a cheap background verifier watches presence and job receipts. No expensive model is needed for the repeated heartbeat checks.
- **latency:** Under 300 ms to acknowledge presence and under 2 s to pause a running job after loss; initial planning may take 3–10 s.
- **cost:** Roughly one realtime turn plus one planner invocation per job; verifier polling should be Worker-side and near-zero model cost.
- **security:** A USB-connected pendant is evidence of proximity, not identity by itself; bind the session to an authenticated device key and fail closed on disconnect, stale heartbeat, or serial ambiguity. Do not delete or send anything merely because presence changed; pause, preserve the draft, and report exactly what was and was not committed.
- **missing:** A signed pendant-presence lease with monotonic heartbeat and disconnect semantics; Planner/execute checkpoints that can pause between actions and emit a durable partial receipt; A relay policy that maps presence loss to pause rather than cancellation

### "“While I’m working, notice when two apps or tabs contain conflicting versions of the same thing, tell me the conflict in one sentence, and let me choose which source wins.”"
- **useful because:** Today the owner can ask the Mac or browser to read and edit, but has to know where inconsistency is hiding. A cross-surface reconciliation agent would compare local files, authenticated browser pages, and recent action receipts, then present a small decision on the pendant instead of silently overwriting one source.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use a cheaper background model for extraction and pairwise comparison; use realtime only to summarize the detected conflict and collect the owner’s winner choice. Mac-planner/browser actions then apply the selected patch.
- **latency:** Detection can take 30–120 s after a relevant job or on demand; the spoken conflict summary should arrive within 2 s once detected.
- **cost:** One low-cost comparison per changed-source pair; realtime cost only when a conflict is surfaced or the owner asks for detail.
- **security:** Read only by default. Preserve source snapshots and a field-level diff, never claim consistency if one source could not be read, and require an explicit spoken choice before overwriting either source. Authenticated page contents and private files leave their surfaces only as encrypted, scoped comparison inputs.
- **missing:** A cross-surface content identity and canonicalization layer; A durable conflict record with source snapshots, field-level diff, and chosen winner; Browser and Mac adapters that return provenance rather than plain text; An inbox delivery path that carries a decision request, not merely a completion alert

### "“Before I leave, ask me only about unfinished things that are blocked by my decision, and let me resolve each one by voice without reopening the Mac.”"
- **useful because:** The owner currently receives task completion/status information, but no compact, decision-focused end-of-session sweep. This would turn abandoned Mac/browser work into a bounded voice queue: the relay identifies jobs that cannot proceed, the pendant asks one high-value question at a time, and the selected answer is handed back to the exact waiting workflow.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** A background classifier ranks blocked jobs and extracts the smallest missing decision; realtime handles the short interactive sweep; the planner resumes the original job after the answer.
- **latency:** Generate the queue in under 5 s; each question should be spoken within 1 s of the owner asking for the sweep. Resumption can be asynchronous.
- **cost:** One cheap ranking pass per sweep and one realtime turn for the dialogue; reuse stored job receipts to avoid re-reading the Mac.
- **security:** Only jobs owned by the current session/device may enter the queue. Show the originating app/site and proposed consequence before applying a choice. Never infer a choice from silence, and preserve the unanswered queue when the pendant disconnects.
- **missing:** A first-class blocked/awaiting-owner state in job receipts; A durable decision-token linking one spoken answer to one exact pending action; A compact owner-facing queue distinct from generic completion notifications; Resume support in the Mac planner after a decision arrives


## What it asked for

_Nothing._
## Its own summary

Recorded three new owner-facing capabilities: (1) presence-bound execution that pauses when the worn pendant leaves the Mac, (2) cross-app/browser conflict detection with provenance and a spoken winner choice, and (3) a voice-resolvable queue of unfinished jobs blocked on the owner’s decision. The system still needs signed presence leases and checkpoint pause semantics; provenance-rich cross-surface comparison and durable conflict records; and first-class blocked-job decision tokens with resume support. Existing routes can carry much of the plumbing, but they do not provide those missing semantics.

**Biggest unknown:** Whether the live Mac planner and browser adapters already expose enough per-action checkpoints and source provenance to implement these safely, or whether both need new contracts.

