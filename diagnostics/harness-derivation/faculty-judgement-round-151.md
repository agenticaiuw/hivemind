# Harness derivation — faculty-judgement — round 151

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Audit what you remember about me. Show me contradictions, stale assumptions, and where each came from; if I say forget this, remove it everywhere it was copied.”"
- **useful because:** The system currently can remember the same fact in facts.json, the context graph, evidence capsules, browser provenance, and eventually fleet memory, but cannot tell the owner that those copies disagree or honor one forget request across stores. This is the single most useful judgement capability: it makes memory inspectable and revocable instead of quietly shaping future decisions.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** background for the initial audit and contradiction clustering; realtime only for the owner's spoken selection of a claim to forget
- **latency:** Initial audit under 10 seconds with cached indexes; a forget confirmation should return within 2 seconds and report partial completion honestly.
- **cost:** One background model call per audit, roughly $0.01–$0.05 depending on claim count; most work is deterministic indexing, hashing, and joins.
- **security:** Never speak raw secret values by default. The dashboard may reveal source snippets only after an explicit local action. A forget request must be scoped to a claim/source and produce a receipt; failure in one store must be visible rather than implying global deletion.
- **missing:** A normalized claim index joining memory facts, context-graph entities, evidence capsules, browser provenance, and fleet events; capsuleId/source links on derived facts so evidence revocation can reach them; A durable cross-store tombstone/retraction protocol and a global forget executor; A dashboard/API read model that shows contradictions without leaking sensitive text

### "“Did I actually hear that briefing? Tell me which item was downloaded, started, finished, interrupted, or never delivered—and let me replay only the missing item.”"
- **useful because:** A generated response is not the same as one the owner received. With a dropped link, stale queue, checksum error, or an interruption, today's receipts stop at server acceptance and the owner cannot distinguish 'you said it' from 'I heard it'. This makes the pendant a trustworthy memory aid rather than a best-effort speaker.
- **path:** relay → pendant → mac → dashboard
- **model tier:** No model for delivery facts; use deterministic event reconciliation. Realtime is used only if the owner asks for a compact spoken explanation of a failure.
- **latency:** Status under 1 second from the local/relay event index; replay should begin at the next available audio boundary within 2 seconds.
- **cost:** Negligible model cost; storage is a bounded event log and opaque artifact metadata. Replay reuses the existing generated artifact where retained.
- **security:** Expose artifact IDs and delivery states, not audio bytes or transcript by default. Authenticate device session and reject duplicate/out-of-order events safely. Never claim playback_finished without an authenticated pendant event.
- **missing:** A durable query/read model joining briefing item IDs to artifact IDs and pendant delivery events; An idempotent replay command that targets one item without regenerating the whole briefing; Retention and privacy rules for delivery metadata after the audio artifact expires; A dashboard timeline and a terse spoken failure vocabulary

### "“For anything you tell me that could change what I do, say whether it was observed, inferred, stale, or unknown—and do not act on an inference until I confirm it.”"
- **useful because:** The system has separate evidence, browser, memory, and action receipts, but the owner still receives a single flattened answer. A judgement layer should distinguish a fresh observation from a model inference and a remembered assumption, then make that distinction change behavior. This prevents a plausible guess about a page, calendar state, or preference from becoming an external action.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Deterministic classification and policy evaluation first; a cheap background model may summarize conflicts. Realtime is reserved for the owner's immediate question or confirmation.
- **latency:** Under 500 ms when evidence is already present; under 5 seconds when the Mac/browser must refresh. No mutation until the policy verdict is explicit.
- **cost:** Usually no model call; approximately $0.005–$0.02 only for conflict summarization. Evidence hashes and freshness metadata dominate storage, not inference.
- **security:** Do not expose sensitive snippets merely to explain confidence. Every claim needs source IDs, capture time, freshness, and a redacted explanation. Inferred claims must be fail-closed for external side effects, spending, or messages; owner confirmation must be bound to the exact claim and current evidence.
- **missing:** A shared claim envelope with status observed|inferred|stale|unknown, freshness, source IDs, and confidence; A deterministic rule that maps claim status to ACT/PREPARE/ASK using autonomy_policy_evaluate; A single read path for browserProvenance and evidence capsules (browser provenance routes are currently unmounted); A claim-to-action binding so confirmation cannot be replayed after the evidence changes

### "“Before you carry out anything consequential, argue against your own recommendation: show the strongest reason not to do it, what evidence would change your mind, and the safer reversible alternative.”"
- **useful because:** Today the system can plan and evaluate an action, but the owner cannot ask the judgement layer to actively search for disconfirming evidence before it commits. A deliberately adversarial second pass would catch stale browser state, mistaken identity, hidden side effects, and overconfident inferences—especially where the Mac, authenticated browser, relay, and pendant each see different parts of reality.
- **path:** relay → mac → browser → pendant → dashboard
- **model tier:** Background model for the adversarial critique and alternative generation; deterministic policy and evidence checks decide whether the critique is mandatory. Realtime only presents the short verdict and obtains owner confirmation.
- **latency:** 5–15 seconds for a consequential action; no external mutation until the critique has either passed or the owner explicitly overrides it.
- **cost:** One additional background call, roughly $0.01–$0.08 depending on evidence size; deterministic state refreshes and browser reads dominate latency, not token cost.
- **security:** The critic must receive redacted evidence and never invent disconfirming facts. It must cite source IDs and freshness, distinguish missing evidence from negative evidence, and bind any override to the exact plan hash. The dashboard may show sensitive detail; the pendant should speak only the short risk and alternative.
- **missing:** A durable adversarial-review record linked to the exact plan, evidence snapshot, policy version, and owner override; A cross-surface evidence refresh that can compare Mac state, authenticated browser state, and relay records without mutating; A mandatory gate in the executor between PREPARE and MUTATE, with fail-closed behavior on stale or conflicting evidence; A compact owner-facing presentation of strongest objection, uncertainty, and reversible alternative

### "“Give me a 30-day trial where you may handle this narrow class of routine tasks on your own, then show me what you did, what went wrong, and whether I should keep or revoke that permission.”"
- **useful because:** The owner must currently choose between approving each action and granting a broad, opaque autonomy setting. A bounded trial would let the system earn trust on a narrow category while preserving a complete review trail and automatic expiry. It turns autonomy into a measurable relationship rather than a permanent switch.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Cheap background model summarizes outcomes and clusters failures; deterministic policy evaluates each action. Realtime is used only for the owner's spoken approval, pause, or revocation.
- **latency:** Per-action overhead under 300 ms when policy and capabilities are cached; weekly trial report under 10 seconds. Revocation must take effect locally and at the relay within one heartbeat.
- **cost:** Near-zero for routine actions; one background summary call per weekly report, roughly $0.01–$0.05. Storage is bounded receipts and policy versions.
- **security:** Trials must be least-privilege, category- and target-scoped, time-limited, spend-capped, and never include destructive or sensitive-content actions by default. A pendant stop latch and dashboard revoke must override queued work. Every action needs an immutable policy decision and undo/receipt where possible.
- **missing:** Durable cross-surface autonomy grants with scope, expiry, budget, success criteria, and revocation epoch; A trial outcome ledger that joins relay jobs, Mac/browser receipts, failures, undos, and owner corrections; Automatic fail-closed suspension on repeated errors, stale evidence, or policy violations; An owner dashboard and spoken weekly report that explain actions without leaking content

### "“When two parts of my life pull in opposite directions, show me the tradeoff as a small set of choices, tell me what each choice sacrifices, and let me choose without silently resolving it for me.”"
- **useful because:** Current planning can rank tasks and triage signals, but it tends to collapse competing obligations into one recommendation. The owner needs judgement that preserves real conflicts—time, privacy, money, relationships, and commitments—and makes the sacrifice visible before any Mac or browser action occurs.
- **path:** relay → mac → browser → pendant → dashboard
- **model tier:** Background model constructs and explains a small Pareto set from deterministic evidence; realtime presents no more than three choices and records the owner's selection.
- **latency:** Under 10 seconds for a cross-surface conflict; no action is taken until the owner selects a choice or explicitly delegates the decision.
- **cost:** One background reasoning call, roughly $0.02–$0.10 for complex conflicts; evidence gathering and durable choice records dominate operational cost.
- **security:** Conflicts may involve private mail, calendar, browser pages, or other people. Use redacted summaries by default, cite each competing fact, preserve minority options, and require explicit confirmation for external effects or spending. A choice must expire if its evidence changes.
- **missing:** A typed conflict object linking competing obligations, evidence, deadlines, affected people, and sacrifices; A deterministic stale-evidence check that invalidates choices when calendar, mail, browser, or job state changes; A durable owner-choice record with expiry and provenance, separate from the action plan; A renderer that can speak a concise choice set while keeping sensitive rationale on the local dashboard


## What it asked for

_Nothing._
## Its own summary

Round 151 produced three non-duplicate owner capabilities: (1) a cross-store memory audit with scoped global forgetting, (2) truthful per-item audio delivery/replay status, and (3) an epistemic mode that distinguishes observed, inferred, stale, and unknown and blocks action on inference. The new grants are useful primitives, but they do not yet provide the durable joins or enforcement these experiences require.

**Biggest unknown:** Whether the live backend already has an unobserved read route for browser provenance or a durable claim index; the proposal recorder confirmed the named granted tools/routes but explicitly warned that its builtFrom check is not proof those missing pieces are absent.

