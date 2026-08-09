# Harness derivation — faculty-judgement — round 204

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “that was wrong,” “skip this next time,” or “keep this,” while a briefing is playing, bind my correction to the exact item and source, stop repeating the mistake, and tell me what rule changed."
- **useful because:** The system currently records what it said and whether audio played, but it cannot learn from a spoken correction tied to one item. This turns the pendant from a one-way announcer into a system that gets less irritating every day, without silently changing broad preferences.
- **path:** pendant → relay → mac-planner → dashboard
- **model tier:** Realtime only for the short correction intent and item binding; a cheaper background model classifies the correction and proposes a policy/memory edit, with deterministic policy evaluation before use.
- **latency:** Barge-in acknowledgement under 500 ms; correction draft under 3 s; no policy takes effect until the owner says yes or approves in the dashboard.
- **cost:** About $0.002–$0.01 per correction; speech turn and optional background classification dominate.
- **security:** A correction may quote private briefing content. Store only the item ID, normalized rule, sensitivity, and provenance reference by default; never place raw spoken text in a third-party prompt. A correction must not revoke or mutate a source without explicit confirmation.
- **missing:** A production writer from the Mac bridge to fleet memory or a typed preference store with provenance links; A semantic correction-intent classifier and item-level policy schema; A durable link from a briefing item/audio cursor to its evidence and resulting preference; A spoken confirmation path for policy changes

### "Before you speak a response, tell me whether it can actually reach my ear; if the pendant link or audio path is unhealthy, give me the honest fallback and retry automatically when delivery becomes possible."
- **useful because:** A generated answer is not useful if it was never downloaded or heard. The owner gets a truthful “heard,” “queued,” or “not delivered” state instead of assuming silence means success, especially when the pendant is offline or a decode fails.
- **path:** relay → pendant → mac-planner → dashboard
- **model tier:** Deterministic preflight, queue, checksum, and ACK reconciliation; use the realtime model only to phrase the one-sentence spoken status and choose no content. Background reconciliation handles offline ACK replay.
- **latency:** Preflight and queue decision under 150 ms; owner-facing status at the utterance boundary; ACK reconciliation within one retry window after reconnect.
- **cost:** Negligible model cost for ordinary deliveries; roughly $0.001 only when a natural-language explanation is requested. Storage and link retries dominate.
- **security:** Artifacts remain opaque to the relay status layer; expose IDs, byte counts, and failure reasons, not transcript or audio content. Do not claim playback from download alone. Duplicate and out-of-order ACKs must be harmless.
- **missing:** A live implementation of the granted pendant delivery-event ingestion route, including durable replay and dedupe; A relay-side delivery state machine joining artifact IDs to job/briefing items; A pre-speech router that chooses pendant, Mac, or queued delivery without duplicating speech; A user-visible delivery history and expiry policy

### "Give me a short “what changed since yesterday?” briefing that only includes changes with evidence, separates new facts from unresolved conflicts, and lets me ask “why?” on any sentence to hear its source and confidence."
- **useful because:** The owner repeatedly asks for news and status, but ordinary summaries collapse fresh evidence, stale memory, and guesses into the same confident voice. A change-only briefing spends attention on what moved and makes uncertainty audible instead of burying it.
- **path:** relay → mac-planner → browser-extension → pendant → dashboard
- **model tier:** Cheap background model computes diffs and clusters; realtime is used only for the final short spoken rendering or a follow-up why-question. Deterministic provenance and conflict rules decide inclusion.
- **latency:** Precompute on schedule in under 60 s; spoken response under 2 s from cached results; source explanation under 1 s from stored provenance.
- **cost:** About $0.01–$0.05 per daily briefing, dominated by live web/news reads and summarization; follow-up why questions are pennies.
- **security:** Separate public web material from private mail/calendar/browser evidence. Never speak private source text merely because it is relevant; default to source class, timestamp, confidence, and a redacted title. Every sentence needs an evidence reference or is labeled inference.
- **missing:** A durable cross-surface change-set store with source IDs and freshness; Writers for fleet memory and browser provenance (the existing modules are largely unwired); A source-aware diff/contradiction evaluator that handles permission-denied as unknown, not empty; A briefing-item API that carries sentence-level evidence into the audio cursor

### "When you cannot answer because a permission, source, or device is unavailable, say exactly what is unknown, what you did check, and the smallest safe next step—never turn an empty result into “nothing happened.”"
- **useful because:** The owner has already received confident all-clear answers from unreadable calendars and repeated generic browser failures. A structured refusal preserves trust and makes failures actionable without pretending a permission grant or device delivery exists.
- **path:** relay → mac-planner → browser-extension → pendant → dashboard
- **model tier:** Deterministic evidence and permission classification first; realtime model only compresses the structured refusal into the owner's one-sentence spoken style. No expensive model call when a fixed refusal template is sufficient.
- **latency:** Under 300 ms for local permission/device failures; under 2 s when a live source check is needed; never block an unrelated answer while waiting for a disconnected surface.
- **cost:** Near-zero for deterministic refusals; under $0.001 for natural-language compression. Live retries and browser reads dominate.
- **security:** Describe missing scopes and source classes, not secret snippets or account contents. A refusal must not imply that a permission can be granted automatically. Safe next steps should be reversible and confirmation-gated.
- **missing:** A typed uncertainty/refusal result shared by relay, Mac, browser, and pendant; A permission-aware adapter distinguishing denied, empty, stale, offline, and not-yet-checked; A policy that prevents fallback summaries from silently substituting another timezone/source; Dashboard history showing the evidence behind a refusal

### "At the end of my day, show me where my plan diverged from reality—what I intended, what actually happened, and the smallest change that would make tomorrow easier—without turning it into a productivity score."
- **useful because:** The owner gets a humane explanation of recurring friction rather than another task list: overloaded transitions, interruptions, failed automations, and unfinished intentions become concrete patterns they can choose to change. It treats the system as a witness to a life, not a manager grading one.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Cheap background model clusters timestamped events and drafts two or three causal hypotheses; realtime is only for an on-demand spoken recap. Deterministic evidence links and explicit uncertainty prevent the model from inventing causes.
- **latency:** Generated after the day's final quiet window in under 2 minutes; spoken recap under 2 seconds from cache; no interruption unless explicitly requested.
- **cost:** About $0.01–$0.05 per daily reflection, dominated by clustering and evidence summarization; no cost when there are too few trustworthy events.
- **security:** This is an intimate behavioral profile. Keep raw activity local, retain only short-lived aggregates by default, let the owner delete a day atomically, and label hypotheses as hypotheses. Never infer health, mood, or character from timing alone.
- **missing:** A cross-surface event journal that joins planned items, actual action receipts, browser changes, audio delivery, and owner cancellations; A causal-diff schema distinguishing observation from model hypothesis; A local retention/deletion boundary spanning facts, graph, provenance, and receipts; A dashboard review where the owner accepts, edits, or rejects each suggested pattern

### "Let me ask, “What would have to be true for this plan to work?” and get a compact, testable pre-mortem: dependencies, likely failure points, owner decisions, and a safe fallback—before anything is sent, bought, deleted, or scheduled."
- **useful because:** People usually discover hidden dependencies only after an action fails. A pre-mortem turns the hive's reach across the Mac, browser, relay, and pendant into foresight: the owner sees what must be true and can approve a bounded plan instead of approving an opaque intention.
- **path:** relay → mac-planner → browser-extension → dashboard → pendant
- **model tier:** Background model expands the goal into dependency hypotheses; deterministic preflight, autonomy policy, stale-plan revalidation, and provenance checks verify each dependency. Realtime only reads the short result aloud.
- **latency:** Under 5 seconds for an ordinary plan; up to 30 seconds for browser/session checks; no mutation during analysis. Revalidation immediately before any later execution.
- **cost:** About $0.01–$0.08 per pre-mortem, mostly model reasoning over multi-surface context; live checks and browser reads dominate wall time.
- **security:** Analysis must be read-only and must not visit sensitive pages or expose credentials. Each claimed dependency needs an evidence reference and freshness timestamp. External side effects remain impossible until a separate explicit approval.
- **missing:** A typed dependency/precondition graph with pass/fail/unknown states; A planner that can represent safe fallback branches rather than only one linear action list; Cross-surface read adapters for current browser/Mac state with least privilege; A durable, owner-visible pre-mortem tied to the exact plan and invalidated when evidence changes

### "After you change something in the world, check the resulting state and tell me whether the intended outcome—not merely the click or API call—actually happened; if it did not, show the mismatch and stop rather than retrying blindly."
- **useful because:** A successful command is not a successful outcome: a page can reject a form after a click, a reminder can be created with the wrong time, or a browser session can lose state. The owner gets outcome truth and a safe stop instead of a misleading completion receipt.
- **path:** relay → mac-planner → browser-extension → dashboard → pendant
- **model tier:** Deterministic postcondition checks and idempotency first; a cheap background model maps the owner's goal to observable postconditions. Realtime only gives the concise result or asks for clarification when the postcondition is ambiguous.
- **latency:** Reversible local changes verified within 2 seconds; browser outcomes within 10 seconds; irreversible actions require a predeclared verification plan and never auto-retry on mismatch.
- **cost:** About $0.005–$0.03 per complex action, dominated by a follow-up browser read or Mac query; trivial actions use no model.
- **security:** Verification must read only the minimum fields needed and redact secrets. Never infer success from a visual click or HTTP 200. A mismatch is a stop condition; retries require a new autonomy-policy evaluation and owner confirmation for external effects.
- **missing:** A typed postcondition language with observable fields, tolerances, and unknown handling; Execution receipts that retain the intended postcondition and verification evidence; Browser and Mac adapters that can perform read-after-write without duplicating destructive actions; A durable mismatch record the owner can inspect and resolve


## What it asked for

_Nothing._
## Its own summary

Round 204 produced four owner-facing capabilities: correction learning bound to the exact briefing item, truthful heard-vs-generated delivery status, evidence-backed change-only briefings, and structured refusals that distinguish unknown from empty. The recorder noted the first two are close to existing backlog items, so they should be treated as amendments rather than separate primitives. The strongest distinct proposal is the refusal contract: it directly fixes the observed dangerous behavior where unreadable calendars and failed browser work become confident all-clear answers.

**Biggest unknown:** The live implementation status of the newly granted provenance, attention, policy, and delivery-event tools is still partial: several resolve only as side-effect descriptions or have no production writer. Before promising any of these to the owner, the system needs one authoritative cross-surface contract that returns evidence state (readable/empty/denied/stale/offline), and a real durable writer for delivery ACKs and cross-surface memory.

