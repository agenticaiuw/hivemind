# Harness derivation — faculty-judgement — round 54

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Did that actually get done?” — after I ask the system to do something, give me a short answer about the real-world result, not merely whether a command was dispatched."
- **useful because:** Today an action receipt can say a Mac or browser accepted a command while the calendar, form, file, or message remains unchanged. The owner needs dependable closure, especially when they leave the room or lose connectivity. This turns the pendant into a trustworthy second check: it can say confirmed, not confirmed, or unknown with a reason and a link/evidence trail.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use the cheaper background model for post-action verification and evidence summarization; reserve realtime only for the owner's spoken follow-up and the final one-sentence answer.
- **latency:** Dispatch remains immediate; verify after a 2–10 second settle (configurable), then answer within 15 seconds. If a surface is offline, keep a durable pending check and notify when it reconnects.
- **cost:** Roughly $0.002–$0.02 per completed verification, dominated by screenshots/DOM extraction and any model interpretation; typed checks should avoid model calls in the common case.
- **security:** Verification must use least-privilege reads and preserve private-tab boundaries. Never infer success from a toast alone. Sensitive evidence should be hashed or redacted in receipts, and sending/deleting/purchasing still requires confirmation. Unknown must be an honest outcome, not a retry loop.
- **missing:** A shared postcondition schema (expected entity/value plus observation recipe) across Mac, browser, relay, and pendant; Independent settle-and-reread verifier with idempotency correlation and PASS/FAIL/UNKNOWN states; A user-facing timeline linking the dispatch, observation, evidence, and any recovery/undo path; Reconnect handling for checks that were deferred while the Mac, bridge, or pendant was offline

### "“If this isn’t done by Friday at 3, remind me and prepare the next step.”"
- **useful because:** A normal reminder fires at a time whether or not the task is already complete. A conditional promise watches the actual postcondition, suppresses needless nagging when it is done, and escalates with a prepared reversible next step only when the condition remains unmet. This is a life-level safety net for applications, appointments, forms, and follow-ups.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Cheap background/scheduled model evaluates the condition and drafts the next step; realtime is used only if the owner answers an escalation on the pendant.
- **latency:** Condition checks at a user-selected cadence or event, with a deadline-time check under 30 seconds; pendant alert should arrive within 5 seconds of a confirmed unmet condition.
- **cost:** About $0.001–$0.01 per check when typed reads are available; model cost is dominated by drafting a next-step brief, not monitoring. Default to sparse checks and event-driven updates.
- **security:** The promise definition must not expose private account data in notifications. Drafts remain unsent and destructive/financial actions require confirmation. The system must distinguish “not observed” from “not done” and avoid escalating on stale/offline evidence.
- **missing:** A durable conditional-obligation record with deadline, owner-visible wording, condition, cadence, quiet hours, and escalation policy; Postcondition verification adapters and freshness-aware UNKNOWN state; A deadline scheduler that survives relay restarts and reconnects the pendant/Mac/browser; A safe next-step planner that can prepare but not execute irreversible actions

### "“Notice when I keep getting stuck on the same kind of thing, and suggest one small change that would make it easier next time.”"
- **useful because:** The system should improve the owner's life, not merely execute isolated commands. Across repeated pendant conversations, failed browser attempts, abandoned Mac jobs, and postponed reminders, it can identify recurring friction—without diagnosing or judging the owner—and offer a concrete, optional intervention at a calm moment. For example: “This is the third time the reimbursement form stalled at the same field; want me to save a private checklist?”
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use a cheap background model over deliberately minimized, local summaries rather than raw audio or full browsing history; realtime only handles the owner's response when an intervention is offered.
- **latency:** No work on the critical interaction path. Analyze weekly or after three clearly related friction events; offer at most one suggestion in a short spoken sentence and otherwise remain silent.
- **cost:** Approximately $0.01–$0.05 per weekly analysis, dominated by summarizing candidate events; local clustering and typed receipts should make routine detection inexpensive.
- **security:** This is behavioral inference and therefore sensitive. Keep raw audio and page contents out of the analysis; use opt-in categories, local-first aggregation, retention limits, visible evidence for every suggestion, and a one-tap “never infer this again.” Never infer medical, psychological, or character traits, and never change routines automatically.
- **missing:** A privacy-preserving friction-event vocabulary and local aggregation layer spanning pendant, Mac, browser, and relay; Cross-surface links that can establish repeated task friction without retaining raw content; An owner-controlled review and suppression UI for inferred patterns; A conservative intervention policy that requires repeated evidence and caps suggestion frequency


## Changes it proposed to its own stack

### `integration` — Add a cross-surface postcondition verifier beside the existing action-receipt layer. Every planned action declares an expected typed postcondition (entity, field, target value/range) and an observation recipe (Mac accessibility/UI or filesystem read, browser DOM/session query, relay pipeline state, or pendant ACK). After a settle window, an independent verifier re-reads the target, correlates by idempotency key, records before/after evidence and freshness, and emits PASS, FAIL, or UNKNOWN. Queue UNKNOWN checks for reconnect and expose a compact evidence timeline plus recovery/undo suggestion.
- **owner gets:** The owner gets closure about what changed in the world, rather than false confidence that a button press was accepted. It is especially valuable for browser forms, reminders, files, and jobs that continue after the owner walks away.
- effort: Medium-high: typed schema and receipt migration, four observation adapters, durable queue/reconnect logic, and dashboard/voice rendering; start with reminders/files/browser forms before arbitrary GUI tasks.  ·  risk: Some actions have delayed or ambiguous effects, and UI reads may be stale. Mitigate with settle windows, source timestamps, explicit UNKNOWN, and no automatic retries for irreversible actions. If an adapter fails, retain the dispatch receipt and mark verification unavailable rather than claiming success.
- cost: Small storage increase per receipt (roughly 1–4 KB plus optional evidence hashes); background model cost only for semantic/ambiguous checks, with deterministic checks near-zero.  ·  latency: Adds seconds after dispatch for confirmation; immediate dispatch UX is unchanged. Offline surfaces defer verification instead of blocking the owner.
- security: Read-only verification inherits each surface's session permissions; redact secret values and keep raw screenshots/DOM out of voice and long-lived logs. Irreversible operations remain approval-gated.
- depends on: Existing receipt/undo records and idempotency keys; Typed context/provenance service or equivalent source/timestamp fields; Mac accessibility/browser bridge reconnect support; Durable relay job/event persistence

### `memory` — Create a privacy-preserving friction-memory layer that stores only short-lived, typed event sketches: task family, failure/stall reason, surface, count, recency, and owner suppression state. A local/relay aggregator links sketches across pendant utterances, Mac receipts, browser outcomes, and deferred jobs; it expires raw evidence quickly, requires repeated corroboration, and emits a reviewable suggestion candidate rather than an automatic action.
- **owner gets:** The owner gets help with recurring obstacles instead of repeatedly paying the same cognitive tax. Suggestions can become a checklist, reminder, shortcut, or prepared draft only after the owner agrees.
- effort: High: event taxonomy and privacy model, local aggregation, cross-surface correlation, suggestion ranking, suppression controls, and a small dashboard review surface.  ·  risk: False patterns could feel intrusive or insulting, and cross-surface correlation could reveal sensitive activities. Mitigate with opt-in categories, minimum-count thresholds, strict TTLs, evidence links, neutral wording, and an immediate permanent suppression control. Recovery is deletion of all sketches and disabling the analyzer.
- cost: Low ongoing storage if sketches are capped and expire; roughly $0.01–$0.05 per scheduled analysis, with raw transcript/page retention avoided.  ·  latency: None for live actions; analysis is asynchronous and suggestion delivery is rate-limited.
- security: Reduces data exposure by retaining derived sketches instead of raw content, but the derived behavioral profile remains sensitive and must be encrypted, access-controlled, and excluded from ordinary prompt context unless the owner reviews it.
- depends on: A typed cross-surface event/receipt vocabulary; Owner-controlled privacy, retention, and suppression settings; Durable scheduled background execution


## What it asked for

_Nothing._
## Its own summary

Discovered the owner context and backlog, then added two new owner-facing capabilities: (1) “Did that actually get done?” backed by independent cross-surface postcondition verification with PASS/FAIL/UNKNOWN evidence, and (2) conditional promises such as “If this isn’t done by Friday, remind me and prepare the next step.” I also recorded the integration change needed to make receipts prove world state rather than dispatch.

**Biggest unknown:** Whether the existing durable job/event and receipt primitives already support typed expected postconditions and reconnect-safe deferred verification; I asked faculty-action to confirm. Still needed: the shared postcondition schema/adapters, deadline-obligation persistence and scheduler, freshness-aware UNKNOWN handling, and a private evidence timeline surfaced on pendant/dashboard.

