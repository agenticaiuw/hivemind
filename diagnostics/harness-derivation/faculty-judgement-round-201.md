# Harness derivation — faculty-judgement — round 201

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “that’s wrong” during a briefing, stop, investigate the claim, and tell me what changed."
- **useful because:** The system currently can explain provenance or act on an item, but it cannot treat the owner's correction as a first-class event. This would turn a polished wrong answer into a repair loop: bind the objection to the exact spoken item, gather independent evidence, surface the disagreement, and only then update memory or future briefings.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Realtime for the interruption and a short acknowledgement; background model for evidence gathering and comparison; realtime only for the corrected spoken result.
- **latency:** Pause and acknowledge within 300 ms; investigate in 10–30 s, with a spoken 'I’m checking that' and a durable pending result if sources are slow.
- **cost:** About $0.01–$0.08 per repair, dominated by background synthesis and any web/browser reads; the immediate acknowledgement is cheap.
- **security:** The objection and source excerpts may contain private material. Keep raw excerpts on the Mac, pass redacted evidence capsules to the relay, cite every source, and require explicit confirmation before changing durable memory or causing an external action. Never silently overwrite the original claim.
- **missing:** A semantic correction/objection record linked to item_id and cursor_token; Production wiring for the existing crossCheck and browserProvenance modules; A source-comparison job that returns disagreement, confidence, and citations; A memory update transaction that records the old claim, correction, and provenance together

### "Don’t tell me a task is done until the machine that acted, the browser that changed, and my pendant all prove the same completion; if any proof is missing, tell me exactly what is still pending."
- **useful because:** Today a relay receipt can mean a job was accepted, a Mac receipt can mean an action ran, and the pendant can play audio without the owner hearing it. This capability gives the owner one honest answer: completed, partially completed, or unverified, with the missing leg named. It is especially valuable for reminders, purchases, form submissions, and spoken briefings.
- **path:** relay → mac → browser → pendant → dashboard
- **model tier:** Cheaper background model or deterministic reducer for joining receipts and delivery events; realtime only when the owner asks for the status aloud.
- **latency:** Update the state within 2 s of each receipt or pendant ACK; answer a spoken status query in under 1 s from the durable projection.
- **cost:** Under $0.005 per update when deterministic; occasional model use for human-readable explanations is roughly $0.01.
- **security:** Join only opaque IDs and hashes across surfaces, not page contents or audio. A browser result must distinguish executed from merely queued. Never infer success from a missing ACK; fail closed to unverified. External actions still require the existing physical approval latch.
- **missing:** A durable cross-surface receipt join keyed by relay job, Mac action, browser command, artifact, and delivery event; A completion state machine with executed, observed, delivered, played, and acknowledged states; A live consumer for record_pendant_delivery_event and browser result events; A user-facing status route that explains the missing proof and supports retry/undo without replaying completed legs

### "Move this conversation from my pendant to my Mac (or back) without losing the exact item, cursor, or pending action—and let me say “continue privately” when I’m somewhere public."
- **useful because:** A wearable is excellent for walking and terrible for long detail or private content; a Mac/browser is the inverse. Today each surface has its own session and audio item controls, so switching means repeating myself and risks saying sensitive material aloud. This makes the hive feel like one assistant: pause the pendant at a signed cursor, resume on the chosen surface, and preserve the pending action state without executing it twice.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Deterministic handoff protocol for cursor/session state; realtime model only to summarize if the destination cannot render the original format.
- **latency:** Pause and create the handoff in under 500 ms; destination ready in 2 s on an online Mac/browser; retain a durable pending handoff when offline.
- **cost:** Near-zero for protocol and rendering; $0.01–$0.03 only when a format conversion or concise summary is needed.
- **security:** Never transmit raw secrets to a less-private destination by default. Treat destination as an explicit audience and run autonomy_policy_evaluate before any pending action resumes. Use opaque item IDs and cursor tokens, redact previews, expire handoffs, and require physical approval for mutations.
- **missing:** A cross-surface session/handoff record that includes item ID, cursor token, transcript position, destination, and pending action nonce; Mac and browser renderers that can resume an audio item or show its private text without replaying it; A destination privacy policy and explicit owner command for private/public routing; Atomic acknowledgement so only one surface owns playback at a time

### "Before you message, book, or submit anything involving a person or account, ask me to disambiguate the identity when names, addresses, or accounts could refer to more than one target—and remember that choice only for the stated context."
- **useful because:** A wrong Alex, duplicate customer account, or personal-vs-work address is a life-changing failure that ordinary confirmation dialogs do not catch. The pendant can ask a short disambiguation question while the Mac/browser inspect the available identities, then bind the owner's answer to the exact action without granting a global identity assumption.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Deterministic candidate extraction and exact-match checks; realtime model only to phrase the short question and interpret the owner's answer.
- **latency:** Detect ambiguity before any draft or mutation in under 1 s; ask one concise question and resume within 3 s after the answer.
- **cost:** Usually under $0.005 per action; model cost is limited to ambiguous cases.
- **security:** Identity candidates can expose private contacts. Show only names/domains and masked account suffixes on the pendant; keep full addresses on the Mac. Scope the binding to one action or explicit context, expire it, and never treat a prior choice as consent to send.
- **missing:** A typed identity-candidate and disambiguation record linked to the exact action hash; Candidate extraction from Mail, Calendar, Contacts, and authenticated browser forms; A pre-mutation hook that blocks submission until ambiguity is resolved; A scoped memory representation that cannot silently become a global person alias

### "When I am making a consequential choice, show me two or three honest alternatives with the tradeoff that matters to me, let me choose by voice or button, and carry the selected option through the Mac and browser without reopening the whole task."
- **useful because:** The current system is good at executing a chosen action but leaves the owner to do the hardest part: compare options across fragmented tabs, messages, calendars, and constraints. This would make the pendant a decision aid rather than an automation trigger, while keeping the final choice explicit and auditable.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Background model gathers and normalizes alternatives; realtime model speaks only a compact comparison and records the owner's selection; deterministic executor applies the selected prepared plan.
- **latency:** First two alternatives in 5–15 s; selection acknowledgement under 300 ms; application begins only after a fresh confirmation when externally visible.
- **cost:** Roughly $0.03–$0.20 per decision, dominated by reading several sources and comparison synthesis.
- **security:** Do not invent missing prices, deadlines, or policy constraints; label assumptions and unknowns. Private source text stays on the Mac where possible. No option may mutate state during comparison, and the selected plan must be revalidated before execution.
- **missing:** A durable option-set schema with evidence, assumptions, tradeoffs, and selection state; Read adapters for the relevant source families and a normalizer that preserves provenance; A plan compiler that maps one selected option to browser and Mac steps without replaying reads; Owner-facing explanation of rejected alternatives and a stale-state recheck

### "Let me set a personal energy budget for the day—deep work, errands, social commitments, and recovery—and have the pendant warn me when a proposed plan exceeds it, offering a lower-load alternative before anything is booked or sent."
- **useful because:** Calendars optimize empty slots, not a human body. The owner needs protection from a day that is technically schedulable but physically or emotionally impossible. A cross-surface planner could combine calendar commitments, browser tasks, travel estimates, and the owner's own stated limits, then negotiate a gentler plan instead of silently filling every gap.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Background model estimates effort and conflicts; deterministic budget accounting produces the warning; realtime model asks for a concise adjustment when the owner is moving.
- **latency:** A budget check within 2 s of a proposed plan; warning in the next spoken turn; no background interruption unless the owner has explicitly enabled it.
- **cost:** About $0.01–$0.05 per plan check, mostly for effort estimation; repeated checks should use cached estimates.
- **security:** Energy and health-adjacent observations are highly personal. Store only owner-entered categories and coarse scores by default, never infer a diagnosis, and keep the policy owner-editable. Do not cancel or reschedule commitments automatically; present alternatives and require approval.
- **missing:** An owner-editable budget model with categories, costs, recovery rules, and uncertainty; Effort/travel estimates grounded in calendar and browser evidence rather than fabricated numbers; A planner constraint that can return lower-load alternatives, not merely conflicts; A private dashboard and pendant interaction for changing the budget without exposing its details aloud


## What it asked for

_Nothing._
## Its own summary

Round 201 produced three distinct owner-facing capabilities: (1) a spoken-briefing truth-repair loop that binds “that’s wrong” to the exact item and investigates before changing memory, (2) cross-surface completion proof that refuses to call work done until Mac/browser execution and pendant delivery/playback evidence agree, and (3) lossless private handoff between pendant, Mac, and browser with cursor and pending-action ownership preserved. I still need production wiring for correction records, receipt joins, and handoff ownership; I do not need another generic policy or queue.

**Biggest unknown:** Whether the owner wants the default destination for “continue privately” to be the Mac screen, the authenticated browser, or simply silent queueing. No owner preference should be invented; ship an explicit choice prompt and conservative default.

