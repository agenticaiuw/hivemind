# Harness derivation — relay-realtime — round 259

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “park this until I’m back at my Mac,” turn my spoken thought into the right work artifact, then finish it when the pendant reconnects to the Mac and tell me exactly what happened."
- **useful because:** Today an offline voice memo can survive, but it remains a recording the owner must manually revisit. This would turn an away-from-desk utterance into an idempotent, actionable handoff: a draft, reminder, issue, or code task, with the original audio/transcript retained as evidence and a spoken completion receipt.
- **path:** pendant → relay → mac-planner → mac-terminal → dashboard
- **model tier:** Use the realtime model only to acknowledge and normalize the short utterance. Use a cheaper background planner to classify the artifact and produce a structured plan; let mac-planner/mac-terminal execute when the Mac reconnects.
- **latency:** Immediate acknowledgement under 1 second; artifact classification under 10 seconds; execution starts on the next Mac connection and may take minutes.
- **cost:** Roughly one short realtime turn plus one background planner call per parked thought; dominated by transcription/context and any long Mac plan, not the acknowledgement.
- **security:** The original voice and extracted text leave the pendant for relay storage; scope artifacts to the chosen project and preserve provenance. File edits, outgoing messages, and destructive actions need the owner's existing policy/confirmation semantics. Duplicate delivery must be prevented with an idempotency key.
- **missing:** A durable typed handoff record linking offline_voice_memo_store_and_forward output to a planner job and resulting artifact.; Relay-side semantic artifact extraction and idempotency state.; Mac reconnect trigger that drains pending handoffs, plus a structured receipt returned to the relay.; A way to associate a handoff with an explicit project or the next matching project context. 

### "Do this on my Mac when I get back, not while I’m away—and if the result changes files, let me undo the last delegated action by speaking to the pendant."
- **useful because:** The owner is usually away from the unattended Mac. This lets them delegate confidently without either waiting in a voice session or risking an action running at the wrong time, and gives a wearable recovery path instead of requiring them to find the Mac to reverse a mistaken edit.
- **path:** pendant → relay → mac-planner → mac-terminal → dashboard
- **model tier:** Realtime handles only intent capture and concise status. A background planner validates the deferred goal; the Mac planner executes on verified owner-presence; a deterministic receipt/rollback service handles undo without another expensive model call.
- **latency:** Capture and queue under 1 second; execution within 5 seconds of a verified return/presence event; undo acknowledgement under 2 seconds.
- **cost:** One short realtime call at capture and usually no model cost for presence/undo; planner cost only when the Mac executes. Storage and receipt bookkeeping are negligible.
- **security:** Presence must be cryptographically bound to this pendant and Mac session, not inferred from network reachability. Rollback must be limited to the exact job receipt and refuse if the file has since changed; send no file contents to the relay unless needed for planning. Owner policy currently allows reversible actions without asking, while irreversible work still follows existing policy.
- **missing:** A signed pendant↔Mac presence/return handshake over the existing USB serial path today and LTE/Mac bridge path later.; A durable deferred-intent queue keyed by presence rather than a wall-clock schedule.; Per-action inverse operations or filesystem snapshots recorded with GET /jobs/:jobId/receipts.; An undo command path from spoken relay intent to the specific prior job, with conflict detection.; A truthful completion/rollback event delivered through the existing pendant inbox mechanism.

### "What did you change in that file from my last request—and put it back exactly as it was before that request."
- **useful because:** The current job status and receipts can say whether work finished, but they do not give the owner a wearable, content-aware before/after explanation or a reliable inverse operation. A pendant-level “undo that last change” would make remote delegation trustworthy: the owner can recover from an unwanted edit without reopening the Mac or reconstructing the command.
- **path:** pendant → relay → mac-planner → mac-terminal → dashboard
- **model tier:** Use realtime only to resolve the spoken reference (“that last change”) and speak a one-sentence result. Use deterministic receipt and snapshot logic for the diff and rollback; use a background model only to summarize a large diff in owner language.
- **latency:** A short history/diff answer under 3 seconds; rollback acknowledgement under 5 seconds for ordinary files, with longer operations reported asynchronously.
- **cost:** Near-zero model cost for receipt lookup and small diffs; one background summarization call only for large or multi-file changes. Storage is proportional to opt-in rollback snapshots.
- **security:** Snapshots may contain secrets and must stay on the Mac, encrypted and retention-limited. Rollback must verify the job ID, target paths, and current file hashes; if anything changed afterward, refuse rather than overwrite newer work. Never claim success from a planner acknowledgement—speak only from the actual rollback receipt.
- **missing:** Mac-side pre/post manifests and bounded encrypted snapshots for actions that advertise rollback.; A deterministic diff endpoint keyed by jobId and a rollback endpoint with hash/conflict checks.; A relay resolver for relative voice references such as “the last change” across sessions.; A compact spoken result and durable audit record delivered to the pendant inbox when the voice session has ended.


## What it asked for

_Nothing._
## Its own summary

Recorded three owner-facing capabilities: (1) park a spoken thought while away and have it become the correct Mac work artifact on reconnect, (2) defer Mac execution until a cryptographically verified physical return and undo the delegated job from the pendant, and (3) obtain a wearable before/after diff and hash-checked rollback for the last Mac change. The prompt-projection wiring was rejected as already present in the backlog, so I did not count it. The real missing pieces are durable typed handoffs, pendant↔Mac presence binding, Mac-side snapshots/diff/rollback, relative job-reference resolution, and truthful asynchronous receipts.

**Biggest unknown:** Which Mac actions can safely produce bounded encrypted pre/post snapshots without disturbing the owner's work; that determines how broad the rollback capability can be.

