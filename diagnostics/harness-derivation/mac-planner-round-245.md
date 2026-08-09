# Harness derivation — mac-planner — round 245

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Before you change anything on my Mac, tell me the exact short preview through the pendant; when I say 'do it' or press the button, execute it and read back a receipt."
- **useful because:** Today the Mac agent can execute powerful plans, but the voice surface has no durable, human-readable commit step. This gives the owner a fast way to approve a real multi-action plan without staring at the screen, while preserving the owner's rule that destructive work needs confirmation.
- **path:** relay-realtime → pendant → mac-planner → faculty-judgement → faculty-action
- **model tier:** realtime for the short preview and confirmation parsing; background for assembling a detailed receipt or recovery explanation.
- **latency:** Preview within 2 seconds of a plan; confirmation-to-execution under 5 seconds; receipt spoken within 3 seconds after completion.
- **cost:** Roughly $0.003–$0.02 per confirmed plan, mostly realtime voice turns; Mac execution and preflight are local.
- **security:** Never infer confirmation from silence or an unrelated utterance. Bind confirmation to a one-time plan hash and expiry, state touched resources and reversibility, and redact secrets from the spoken preview. Destructive operations remain blocked until explicit confirmation; all outcomes need an immutable receipt and a way to undo where supported.
- **missing:** A relay-side pending-plan record keyed by plan hash with expiry; A voice/button confirmation route that consumes exactly one pending plan; A policy router that distinguishes owner-approved destructive classes from an empty default policy

### "If my Mac goes to sleep or a long job is interrupted, keep the work resumable; when I put on the pendant later, tell me what finished, what is safe to retry, and offer to resume it."
- **useful because:** Long research, file-generation, and browser-assisted jobs currently leave the owner to reconstruct state after a sleep, crash, or link loss. A durable handoff lets the always-awake relay explain the situation while the Mac is unavailable, then resumes only the unfinished idempotent steps when the Mac returns.
- **path:** relay-realtime → pendant → mac-planner → browser-extension → faculty-judgement
- **model tier:** Background model for checkpoint summarization and retry classification; realtime only for the owner's short status question and explicit resume command.
- **latency:** Checkpoint every completed step without delaying it; status available from relay in under 2 seconds; resume begins within 10 seconds of Mac reconnect.
- **cost:** About $0.005–$0.03 per interrupted job, mostly a compact checkpoint summary; storage and hashing are local.
- **security:** Persist only action metadata, hashes, and redacted results—not browser cookies, document bodies, or secrets. Retry only idempotent steps; mark deletes, sends, purchases, and external submissions as never automatic. Bind a resume command to the exact job and show the pending irreversible steps.
- **missing:** A Mac reconnect worker that reconciles workbench handoffs with the live job queue; A step-level idempotency manifest and explicit retry classification for browser and Mac actions; A relay status projection that can speak a compact pending-work summary while the Mac is offline

### "Put the thought I just dictated on the pendant into the right place in the file I'm editing, as a clearly marked draft, and tell me which file and line you changed."
- **useful because:** Voice memos are easy to collect but costly to turn into work. This closes the loop from worn-device speech to the owner's actual VS Code task: the Mac identifies the current file and insertion point, the planner creates a reversible draft patch, and the pendant reads back a precise receipt.
- **path:** pendant → relay-realtime → mac-planner → faculty-perception → faculty-action
- **model tier:** Realtime only to transcribe/confirm the short dictation; background model for locating the best insertion point and formatting it as a draft.
- **latency:** Capture acknowledgement immediate; propose target within 5 seconds; apply after explicit spoken confirmation in under 5 seconds.
- **cost:** About $0.01–$0.05 per insertion, dominated by transcription and contextual placement; file inspection and patching are local.
- **security:** Never overwrite silently. Show file, line range, and exact diff through the pendant before applying; default to a comment or TODO draft. Restrict to the active VS Code workspace, avoid secrets and generated files, and keep an undoable patch/receipt. A dictated secret should be redacted from logs and not sent to the relay beyond transcription.
- **missing:** A semantic Mac read for active editor, file path, selection and line range (the pending mac_semantic_context_read request); A planner operation that produces a unified diff and applies it atomically through the workbench; A voice confirmation binding the diff hash to one execution

### "When I ask, “Why did you change that?”, show me the exact evidence, plan, and result behind any Mac or browser action, and let me undo that specific change if it is still reversible."
- **useful because:** An autonomous assistant is only trustworthy if the owner can reconstruct its decisions after the fact. This would turn opaque automation into an inspectable personal audit trail: the pendant gives a short explanation, the Mac opens a redacted evidence card, and the owner can target one action rather than guessing which job or receipt to undo.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Background model builds the evidence graph and explanation; realtime is used only to answer the owner's short question and disambiguate which action they mean.
- **latency:** Find the likely action in under 2 seconds; render the evidence card in under 5 seconds; undo starts only after the owner names or confirms the selected action.
- **cost:** About $0.005–$0.03 per investigation, mostly summarizing a small receipt/evidence bundle; ordinary action logging is local and cheap.
- **security:** Redact passwords, cookies, private mail bodies, and sensitive URL parameters from spoken and displayed explanations. Preserve cryptographic hashes and timestamps so the explanation cannot silently rewrite history. Undo must be scoped to one receipt and refuse if later actions depend on it; external sends, purchases, and deletes remain non-undoable and must be identified plainly.
- **missing:** A cross-surface causal ledger linking intent, plan hash, evidence snapshot, individual action, result, and reversibility; A query route that resolves vague spoken references such as “that change” to candidate receipts without exposing unrelated private history; Per-action compensating operations for browser and Mac mutations, with dependency checks before undo

### "If a browser or Mac task starts changing more than I asked for, stop at the next safe point, tell me through the pendant what unexpectedly changed, and preserve the work so I can decide whether to continue."
- **useful because:** Authenticated browser sessions and desktop automation can encounter redirects, changed page structure, or side effects that were not present when the plan was made. A live deviation monitor would prevent a routine task from silently becoming a broad mutation while preserving enough state for a deliberate recovery.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → faculty-perception → faculty-judgement
- **model tier:** Realtime only for a terse urgent alert; a cheaper background model classifies the before/after diff and proposes the safest continuation.
- **latency:** Detect a material deviation within one browser action or Mac step; alert within 2 seconds; checkpoint before pausing where possible.
- **cost:** About $0.005–$0.03 per multi-step task, dominated by diff classification; local hashes and DOM/resource summaries are inexpensive.
- **security:** Compare redacted structural summaries rather than uploading page contents, cookies, or document text. Define owner policy for what counts as material (domain change, new download, recipient change, permission prompt, destructive verb). Never auto-dismiss security warnings; preserve evidence locally and expire it on a short retention schedule.
- **missing:** Browser and Mac before/after state fingerprints tied to each action, not just whole-job receipts; A deviation classifier with resource-specific thresholds and safe checkpoint semantics; A pendant interrupt/acknowledgement path that can pause an in-flight browser or Mac plan without corrupting it

### "Let me mark a browser tab, project, or document as private so the Mac can still help locally, but nothing from it is sent to the relay or spoken through the pendant; tell me if a requested action would cross that boundary."
- **useful because:** The current privacy latch is all-or-nothing, while useful work often mixes sensitive and ordinary contexts. A per-resource boundary would let the owner keep using local automation without leaking document text, URLs, or screenshots into the always-awake voice path, and would make the boundary visible before an action crosses it.
- **path:** mac-planner → browser-extension → relay-realtime → pendant → faculty-judgement
- **model tier:** Background model for local classification and redaction; realtime only for a brief boundary warning or the owner's explicit override.
- **latency:** Apply a local privacy label immediately; evaluate a cross-boundary action before dispatch; warning under 1 second.
- **cost:** Negligible for labels and local filtering; occasional small model calls for classification, roughly $0.001–$0.01 per ambiguous resource.
- **security:** Private labels must be enforced locally before network serialization, not merely hidden in the spoken summary. Store only salted resource identifiers and policy metadata in relay-visible logs. Overrides require explicit owner confirmation and should be one-shot, time-limited, and auditable; never upload the private content to classify it.
- **missing:** A Mac/browser resource-label store covering tabs, workspace roots, files, and document identities; A serialization/redaction gate that runs before pipeline events, receipts, screenshots, and model prompts leave the Mac; A pendant-visible but content-free boundary state and a command to label/unlabel the current resource


## What it asked for

_Nothing._
## Its own summary

This round produced three non-duplicate owner-facing capabilities: voice-confirmed Mac plan commits with exact previews and receipts; resumable cross-node jobs that survive Mac sleep and report through the pendant; and dictation-to-VS-Code draft insertion with a diff hash and explicit confirmation. The attempted pendant bookmark context proposal collided with an existing capability, and the hardware-health proposal collided with the existing fixture-to-health-check idea, so I did not count or restate them.

**Biggest unknown:** The newly granted/observed workbench and approval routes still need live schema verification, and the pending mac_semantic_context_read remains the key missing primitive for editor-aware actions. I still need a real step-level idempotency/reconnect worker, a relay pending-plan confirmation record, and semantic active-editor context; no further permission request is warranted this round.

