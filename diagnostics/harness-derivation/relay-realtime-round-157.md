# Harness derivation — relay-realtime — round 157

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If that task finishes after I stop talking, let me know on the pendant with a short status update."
- **useful because:** Long-running Mac jobs shouldn’t require the owner to remember to check later. A gentle, spoken completion cue makes the system feel reliable and saves time.
- **path:** relay → mac-bridge → pendant
- **model tier:** Realtime only for the initial acknowledgment; background tracking should use a cheaper model or a worker.
- **latency:** Acknowledge immediately; notification delivery can be delayed, but should arrive within seconds of completion when online.
- **cost:** Low per job: one status subscription and one short notification. The dominant cost is job state polling and audio delivery.
- **security:** Notifications could leak sensitive task names. Use minimal phrasing and avoid quoting content. Respect the owner’s SD rule: don’t store audio unless upload fails.
- **missing:** A working relay_event_push route/tool implementation; A notification delivery path to the pendant/paired device; A job-completion watcher that can run without a live voice session

### ""Do this across my Mac and my signed-in browser, but if one step fails, undo everything you changed and tell me exactly what was restored.""
- **useful because:** Today a multi-surface request can partially succeed while the owner is away and leave an unknown mess. A wearable command should behave like one reliable operation: browser and Mac changes either converge or compensating actions return them to the captured starting state, with a spoken receipt naming any irrecoverable side effect.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use realtime only to classify the spoken goal and report; use the slower planner for decomposition, and deterministic action/receipt services for snapshots and compensation.
- **latency:** Acknowledge in under 1 second; execution may take minutes, with a final pendant alert when complete or when rollback is incomplete.
- **cost:** About one planner invocation plus ordinary Mac/browser action calls; compensation doubles worst-case action volume. Storage and hashing of state snapshots dominate infrastructure cost, not model tokens.
- **security:** Snapshots may contain authenticated page data, mail text, and local file metadata; encrypt them, retain only for the job TTL, and never speak secrets. Rollback cannot erase external sends, purchases, or third-party effects, which must be explicitly labeled as non-compensable.
- **missing:** A durable cross-surface transaction coordinator with a per-action pre-state journal; Typed compensators (restore file, revert edit, close created tab, undo browser mutation) and idempotency keys; A planner contract that declares reversibility and non-compensable effects before execution; A user-visible transaction timeline and truthful rollback receipt

### ""I'm in a meeting now. Keep doing the work, but don't interrupt me unless it is truly urgent; when I'm free, give me one concise catch-up.""
- **useful because:** The pendant currently treats delivery as a queue, not as an owner-aware interruption policy. This would let the hive continue useful Mac/browser work while the owner is unavailable, suppress low-value spoken alerts, collapse duplicate updates, and deliver a ranked digest at the first safe moment rather than waking the owner for every completion.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** A cheap background classifier ranks events and coalesces duplicates; realtime speaks only the final urgent exception or the requested catch-up.
- **latency:** Mode changes should take effect within 2 seconds; nonurgent results can wait until an availability transition, while urgent failures surface within 10 seconds.
- **cost:** Low ongoing model cost if ranking uses rules plus a small classifier; the main cost is event storage and a compact per-owner digest.
- **security:** Availability and meeting state are sensitive. Prefer explicit pendant mode plus local calendar/Mac signals, encrypt event summaries, and give the owner a one-button override. Never infer that silence means consent to suppress safety-critical failures.
- **missing:** An explicit owner availability mode with pendant button/voice controls; Relay-side event coalescing, urgency ranking, and expiry semantics over the existing inbox; Availability signals from calendar, active call, Mac audio, and browser state; A transition hook that triggers one spoken catch-up without requiring polling

### ""Continue this exact conversation when I reconnect to my Mac—show me what you already saw, what you changed, and let me take over without starting over.""
- **useful because:** The owner moves between LTE-worn, USB-attached, and Mac/browser contexts, but work and conversation are currently tied to whichever surface handled the last turn. A reconnect should transfer a compact, cited session capsule so the owner can inspect the live browser state, hear the current result, and issue the next command naturally.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime generates the short spoken handoff; a cheaper background process compresses transcripts, action receipts, citations, and pending decisions into a bounded capsule.
- **latency:** USB or network reconnection should produce a handoff in under 3 seconds; capsule compression can happen asynchronously after each job step.
- **cost:** Small summarization cost per completed job, dominated by storing encrypted receipts and selected page citations; no need to resend full transcripts every turn.
- **security:** A capsule can expose browser sessions and private conversation context to a newly connected surface. Bind it to a device/session key, encrypt in transit and at rest, expire it quickly, and expose provenance so the owner can see which facts came from which surface.
- **missing:** A versioned session-capsule schema spanning voice turns, planner jobs, browser tab IDs, receipts, and unresolved decisions; Device pairing and resumable handoff between LTE pendant, USB serial pendant, Mac, and dashboard; Incremental context compaction with citations and hard size limits; A Mac takeover UI that can resume a pending planner job rather than merely display it

### ""Work through everything you can; if you hit a decision only I can make, ask me one tiny multiple-choice question on the pendant, then resume automatically.""
- **useful because:** Long Mac/browser jobs fail today when an ambiguous choice appears: they either guess, stop, or require the owner to reconstruct context later. A decision checkpoint would preserve momentum while making the owner's scarce attention useful—one spoken question with bounded options, then exact continuation from the same verified state.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** A background planner detects ambiguity and generates a bounded question from the live page/action state; realtime only reads the question and the owner's short answer. Deterministic job resumption applies the selected branch.
- **latency:** Question generation under 5 seconds after a block; answer acknowledgement under 1 second; resume within 3 seconds of the pendant response.
- **cost:** One small planner call per genuine ambiguity and ordinary downstream actions; negligible cost when no checkpoint is needed. Persisting a compact branch state is the main storage cost.
- **security:** The question must not leak secrets from authenticated pages in spoken audio. Redact values and prefer labels. Expire unanswered checkpoints, bind replies to the originating job and device session, and reject stale answers after the page has changed.
- **missing:** A first-class blocked-decision job state distinct from failed or needs_attention; A schema for 2–4 safe options, redacted spoken prompt, default/expiry, and branch continuation; Pendant response encoding for selecting an option by voice or button without starting a new turn; Resumable planner execution with a verified state hash and branch-specific action plan


## What it asked for

_Nothing._
## Its own summary

Recorded four owner-facing capabilities this round: transactional cross-surface rollback, meeting-aware interruption/digest mode, resumable conversation handoff across pendant/Mac/browser, and bounded decision checkpoints that let blocked jobs ask one concise multiple-choice question and resume. The first three were accepted (the first flagged as somewhat close to existing work, so it should be treated as a distinct stronger transaction guarantee); all specify what must be built rather than pretending current wiring is sufficient.

**Biggest unknown:** Whether the newly named relay routes and state surfaces already expose any of the missing primitives (transaction journal, availability transitions, session capsules, or blocked-decision states). The user explicitly disabled further discovery this round, so these gaps are proposals, not live-system claims.

