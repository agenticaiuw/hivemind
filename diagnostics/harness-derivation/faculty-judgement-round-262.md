# Harness derivation — faculty-judgement — round 262

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“What is the one thing I should do next, and if I say ‘do it’, carry it through and tell me whether it actually worked?”"
- **useful because:** Today the system can rank plans, execute actions, and report receipts, but those are disconnected. This gives the owner one outcome-oriented loop: select one evidence-backed item, act on the correct surface, verify the changed state, and close or requeue it. It prevents the wearable from celebrating a queued job as a finished life outcome.
- **path:** relay → pendant → mac → browser
- **model tier:** Use the cheap background model to assemble candidates and summarize evidence; use realtime only for the owner's spoken selection and clarification. Deterministic policy/preflight decides whether the selected step may ACT, PREPARE, or ASK.
- **latency:** Initial spoken answer under 2 seconds from cached state; execution may take up to 60 seconds, with a concise pendant update only after verified outcome or a concrete failure.
- **cost:** About $0.01–$0.05 per interaction, dominated by evidence synthesis and verification; most turns should be deterministic and cached.
- **security:** Never treat audio playback or a queued receipt as success. Revalidate the plan immediately before mutation, require physical consent for irreversible actions, and expose provenance for every recommendation. Browser page text and mail content stay local unless the existing redaction/origin policy allows projection.
- **missing:** An outcome record that links one owner-selected item to its prepared plan, action receipts, and verifier result; Relay-side job leases/requeue so a Mac crash cannot strand the selected action; A small verifier vocabulary for calendar/mail/browser/file state changes; A durable relay↔Mac job identity mapping

### "“Give me a private briefing when I am actually wearing the pendant; if it is on a desk or other people may hear, put it in the inbox instead.”"
- **useful because:** The current system can decide urgency and redact some briefings, but it cannot distinguish a worn, private listening context from an unattended speaker. A physical wear/presence signal would make private audio a deliberate delivery channel instead of an assumption.
- **path:** pendant → relay → mac → browser
- **model tier:** No expensive model is needed for the gate. Firmware reports a signed wear/privacy state; relay attention arbitration and the existing redaction policy choose speak, queue, or suppress. Use the background model only to summarize queued items later.
- **latency:** Local state transition under 100 ms; relay decision under 500 ms. If the signal is unknown, fail closed to the existing inbox rather than speaking.
- **cost:** Roughly $5–$15 for a capacitive/skin-contact or proximity sensor and board integration, plus negligible per-use API cost; the current single LED remains the only acknowledgement channel.
- **security:** Do not infer identity or record raw proximity data. Transmit only signed states (worn/unworn/unknown, timestamp, firmware epoch). Private or secret content is never spoken when state is unknown; policy decisions must cite the state and rule that caused them.
- **missing:** A real wear/contact sensor or equivalent firmware signal; none is present on the current board; A relay contract carrying signed privacy-state epochs; A single delivery policy joining wear state, focus/idle state, sensitivity, and attention_arbitrate; A way to surface a queued private item without leaking its title on the LED or public Mac

### "“If my Mac or browser dies halfway through something, pick it up safely when it comes back—without repeating a step or pretending it finished.”"
- **useful because:** An in-flight job currently can remain stuck in processing for up to a day, and the owner has no honest distinction between prepared, partially applied, and verified. This would make the hive resilient in the way a wearable should be: the conversation can disappear, but the intention and safe next step survive.
- **path:** relay → mac → browser → pendant
- **model tier:** Use deterministic lease/recovery and idempotency logic first. Invoke a cheaper background model only to reconstruct a human-readable resume summary from the context handoff; realtime is needed only when the owner asks what happened.
- **latency:** Recovery scan every 30–60 seconds; reconnect status in under 2 seconds; no automatic replay of an uncertain mutation. Ask the owner only when state cannot be proven safe.
- **cost:** Negligible API cost for the lease and receipt path; approximately $0.005–$0.02 only when a resume summary must be generated.
- **security:** Fail closed on stale or ambiguous plans. Revalidate source state and policy before resuming, use action-level idempotency keys, and never retry destructive/external actions automatically. Show the owner the last verified step and the exact reason for asking.
- **missing:** relay_jobs lease_until, expiry sweep, and bounded reclaim policy; A durable relay-job↔Mac-job mapping rather than telemetry-only localJobId; Step-level outcome/checkpoint records covering browser commands as well as Mac actions; A resume endpoint that consumes contextHandoff plus revalidate_pending_plan and returns a safe next step

### "“When your sources disagree, show me the two plausible interpretations and what each would cause before you choose or do anything.”"
- **useful because:** A trustworthy assistant should not collapse contradictory timezone, permission, calendar, browser, or goal evidence into one confident answer. The owner would see the disagreement, the consequence of each branch, and the smallest decision needed to resolve it—without any side effect occurring first.
- **path:** relay → mac → browser → pendant
- **model tier:** Use deterministic conflict detection and consequence extraction first; use the background model to phrase the two branches. Realtime is used only to ask the final concise question and record the owner's choice.
- **latency:** Under 3 seconds for a cached conflict; up to 10 seconds when fresh Mac/browser reads are required. No mutation until the branch is explicitly selected.
- **cost:** Approximately $0.01–$0.04 per conflict, mostly for branch explanation; source comparison and policy checks are deterministic.
- **security:** Branch previews must be read-only and redact sensitive snippets. Every claim needs source IDs and freshness. A branch must never be executable merely because it was displayed; the selected branch must pass preflight and autonomy policy again.
- **missing:** A typed counterfactual/branch result joining conflict evidence to predicted consequences; Read-only consequence previews for the actual action types available on Mac and browser; A durable owner choice that records which assumption was accepted and when

### "“Before I change how you behave, let me try the rule on recent real situations and see exactly what you would have spoken, queued, or blocked.”"
- **useful because:** Interruption and disclosure policies are currently either placeholders or scattered enforcement decisions. The owner needs to calibrate them safely against representative history before trusting the pendant in public or during focused work. A simulation mode turns hidden policy consequences into an inspectable, reversible choice.
- **path:** relay → mac → pendant → browser
- **model tier:** Replay stored event metadata with deterministic policy evaluation; use a cheaper background model only to summarize patterns. Realtime is unnecessary except for the owner's final confirmation of a chosen policy.
- **latency:** 5–15 seconds for a 24-hour replay; longer historical windows may run asynchronously and leave a reviewable report. Simulation must never emit audio or mutate external state.
- **cost:** Approximately $0.005–$0.03 per simulation; dominated by summarization, not evaluation.
- **security:** Replay event metadata and sensitivity labels by default, not raw mail/page text. Make clear that simulated outcomes are not actual deliveries. Policy edits require explicit confirmation and retain a versioned before/after explanation.
- **missing:** A policy simulation endpoint that replays attention, disclosure, and autonomy decisions against historical event metadata; Stable event fixtures linking triage findings, browser watches, audio items, and delivery outcomes; A versioned policy store with rollback and owner-readable rule explanations


## What it asked for

_Nothing._
