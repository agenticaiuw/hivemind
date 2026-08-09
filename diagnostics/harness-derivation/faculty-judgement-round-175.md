# Harness derivation — faculty-judgement — round 175

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“What happened while I was away, and what did I miss?” Give me a time-bounded, source-linked replay of important events across my Mac, browser, relay, and pendant, explicitly showing gaps and whether I actually heard each spoken item."
- **useful because:** Today the system can report jobs, browser changes, and audio generation separately, but cannot tell the owner what reached them. A single replay would distinguish 'the agent knew', 'it acted', 'the pendant downloaded', and 'I heard it', preventing both missed deadlines and false reassurance.
- **path:** relay → mac → browser → pendant → dashboard
- **model tier:** background for event normalization and ranking; realtime only when the owner asks verbally for a replay
- **latency:** Under 3 seconds for a 24-hour replay from indexed events; up to 10 seconds for raw backfill
- **cost:** About $0.01–$0.05 per replay, dominated by summarization; indexing is local/relay storage work with no per-event model call
- **security:** Replay may expose private mail, calendar, browser, and spoken content. Default to metadata and redacted summaries, show source IDs, require an explicit dashboard reveal for sensitive snippets, and never infer playback from generation alone.
- **missing:** A durable common event index joining relay job IDs, Mac jobs, browser commands, pipeline artifacts, and pendant delivery ACK event IDs; A monotonic ordering/clock-skew model that labels uncertain ordering instead of pretending timestamps are exact; A read API that returns the joined timeline with provenance and explicit delivery state

### "“Before you do this complicated thing, walk me through the exact consequences in my own context, let me change one step by voice, then stage the final plan for one physical approval on the pendant.”"
- **useful because:** A generic preview shows operations, not consequences in the owner's life. This would turn ambiguous multi-app work into a short, spoken, editable rehearsal: which account, which browser tab, which files, what leaves the machine, and what can be undone before anything external happens.
- **path:** relay → mac → browser → pendant → dashboard
- **model tier:** realtime for the short conversational rehearsal; background for gathering state and calculating reversibility
- **latency:** First consequence summary in 5 seconds; each owner correction under 2 seconds; no mutation until physical approval
- **cost:** $0.03–$0.15 per rehearsal, mostly realtime turns and state extraction; no model cost for deterministic policy checks
- **security:** The rehearsal must not transmit page secrets or form values to the pendant or relay. Use least-privilege reads, redact sensitive snippets, bind the final plan to fresh source hashes, expire it quickly, and require the existing physical_transaction_approval_latch before external side effects.
- **missing:** A typed consequence graph that maps each planned step to affected records, audiences, reversibility, and evidence; A spoken edit protocol that changes a prepared plan without silently broadening its scope; A durable cross-surface approval handoff joining the Mac plan to the relay decision and pendant nonce; A final stale-state recheck that blocks if the browser tab, account, or source evidence changed

### "“Can you do that right now, and if not, what is the closest thing you can safely do?” Give me one honest answer that reflects the live Mac, browser, relay, and USB-connected pendant—not a generic capability list—and let me choose the fallback."
- **useful because:** The owner should never have to discover after the fact that LTE is unregistered, Safari is offline, Calendar is unreadable, or a permission blocks a step. This turns reachability into a useful conversational decision: execute, prepare, queue until a surface returns, or explain the missing owner action.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** deterministic policy and preflight first; realtime model only to phrase the result and resolve an ambiguous fallback
- **latency:** Under 500 ms for known intents; under 3 seconds when a read-only probe is needed; never wait on an unavailable surface indefinitely
- **cost:** Usually <$0.005 because the arbiter and preflight are deterministic; occasional realtime phrasing costs <$0.02
- **security:** Preflight must reveal only capability scopes and coarse failure reasons, not account names, page contents, or credentials. Mutations remain behind autonomy_policy_evaluate and physical approval; USB serial must be treated as local transport, not proof of relay/LTE reachability.
- **missing:** A live capability manifest published by each node with read/draft/mutate/destructive scopes, freshness, and transport state; A fallback planner that converts a blocked mutation into a reviewable draft or durable queue item without claiming success; A pendant-safe response envelope that says which surface is missing and preserves the user's exact intent across reconnect

### "“Before you send, book, publish, or change anything that affects another person, show me who is affected, what they could infer, and the least-harmful reversible alternative.”"
- **useful because:** Current approval can ask whether an action is allowed, but it does not make third-party consequences legible. The owner gets a human-readable impact boundary instead of discovering later that a client, colleague, or family member was exposed or inconvenienced.
- **path:** relay → mac → browser → pendant → dashboard
- **model tier:** background for deterministic impact extraction and entity resolution; realtime only to explain the short impact card
- **latency:** Under 4 seconds for a prepared action; block execution until the owner has seen the impact summary and made the existing deliberate approval
- **cost:** $0.02–$0.10 per complex action, dominated by extracting affected entities and audiences; simple local actions are deterministic
- **security:** The impact analyzer must not copy third-party content into the relay or pendant. Use local redacted entity classes, show only the minimum needed, and fail closed when audience or consequence cannot be established.
- **missing:** A typed third-party-impact model linking each plan step to affected people, audiences, and reversibility; A local redacted impact extractor for mail, calendar, browser forms, and files; A policy field distinguishing owner consent from consent on behalf of another person; A receipt proving the impact summary was generated from the same plan that was approved

### "“After something you did for me, tell me whether it actually achieved the outcome I wanted—not merely whether the command ran—and let me correct your interpretation once so the correction changes future decisions.”"
- **useful because:** A successful receipt can still mean a failed life outcome: the wrong booking, an unreadable reminder, a message that reached the wrong audience, or audio the owner never heard. This closes the loop from intent to real-world result and lets the owner teach judgement through one concrete correction.
- **path:** relay → mac → browser → pendant → dashboard
- **model tier:** background for outcome checking and longitudinal pattern detection; realtime only for the concise post-action question
- **latency:** Ask within 30 seconds of a verifiable completion or on the owner's next interaction; outcome checks may take up to 60 seconds for browser/calendar propagation
- **cost:** $0.01–$0.08 per completed action, mostly outcome extraction; deterministic receipts and delivery ACKs are free of model cost
- **security:** Do not silently infer satisfaction from silence. Store only the owner's explicit correction and a compact outcome label, with provenance and expiry; never let a learned correction authorize a new external side effect without normal policy and approval.
- **missing:** An intent-to-outcome schema with explicit success, partial, failed, and unknown states; Outcome probes for propagation and audience reach across Calendar, Mail, browser, and pendant playback; A durable feedback record consumed by autonomy_policy_evaluate without becoming an opaque permanent profile; A spoken, non-annoying feedback policy with opt-out and deduplication

### "“Show me which interruptions were worth breaking my attention for this week, which were noise, and let me set a budget for how often the pendant may interrupt me.”"
- **useful because:** The system currently decides per event but cannot learn whether interruption was worth the disruption. A weekly attention ledger would make the cost visible, let the owner tune a measurable budget, and prevent a flood of individually defensible alerts from consuming the day.
- **path:** relay → mac → browser → pendant → dashboard
- **model tier:** background aggregation and ranking; realtime only when the owner asks for the report or changes the budget
- **latency:** A report in under 5 seconds from stored decisions; budget changes apply to the next arbitration cycle
- **cost:** <$0.01 per report; event aggregation is deterministic and model use is limited to summarizing clusters
- **security:** Attention history can reveal meetings, habits, and sensitive topics. Store event metadata and redacted labels by default, allow local-only retention, and never use silence as evidence that an interruption was welcome.
- **missing:** A durable attention-decision and owner-feedback ledger joining arbitration, delivery, playback, and acknowledgement; A measurable interruption budget model with owner-set windows and categories; A feedback action that marks an interruption useful, premature, or harmful without exposing its private content; A dashboard/pendant summary that does not itself become another interruption


## What it asked for

_Nothing._
## Its own summary

This round produced three recorded owner-facing capabilities: (1) a source-linked replay of what happened while the owner was away, including whether the pendant actually downloaded and played each item; (2) a spoken consequence rehearsal that lets the owner edit a multi-surface plan before one physical pendant approval; and (3) truthful live capability/fallback negotiation across USB pendant, Mac, browser, and relay. The third is mostly unwired connective behavior, not a new primitive: the missing piece is a fresh capability manifest plus a fallback planner that turns blocked actions into drafts/queues without claiming success. I also told mac-planner the USB/LTE constraint and the cross-surface join need.

**Biggest unknown:** Whether the live route inventory already exposes a usable cross-surface event join or capability manifest. The proposal recorder specifically warned that several named pieces are known but not proven wired together; I need a targeted source/live inspection of those joins before claiming the owner can use them today.

