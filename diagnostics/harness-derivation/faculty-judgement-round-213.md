# Harness derivation — faculty-judgement — round 213

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### ""I marked that I'm leaving—what am I likely to forget, and what should I do before I go?""
- **useful because:** A dedicated departure moment turns the existing second-button marker into a useful, bounded ritual: it catches imminent meetings, overdue commitments, unsent drafts, browser tabs that need a decision, and unfinished Mac jobs without requiring the owner to remember which surface held each one.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Cheap background classifier ranks existing evidence; realtime model only converts the ranked result into one short spoken checklist.
- **latency:** Marker acknowledgement immediately; checklist within 15 seconds, with late browser reads allowed to become a follow-up rather than blocking departure.
- **cost:** About $0.005–$0.03 per departure; most cost is optional authenticated-browser reads.
- **security:** The pendant sends only a marker kind and monotonic id, never location or microphone audio. Browser and mail content stays local unless a short item is explicitly selected for speech. Never send or delete anything; creating a reminder requires the owner's existing non-confirmation rule, while external mutations still require confirmation.
- **missing:** A departure-specific marker_kind payload on the already accepted offline_moment_bookmark record; A bounded 'before I go' query that joins day-plan, jobs, browser sessions and mail triage without treating missing sources as empty; A policy for how far ahead counts as imminent and how many checklist items to speak; A return path that lets the owner mark one item done/deferred from the pendant inbox

### ""If something fails while I'm away from the Mac, make the safest useful fallback and tell me what changed.""
- **useful because:** Today an offline browser, stale Mac job, or missing audio ACK can leave work apparently accepted but not actually completed. This capability turns failures into a reviewable local draft, reminder, or queued alert instead of silently losing the owner's intent, while preserving an honest boundary between prepared and executed work.
- **path:** relay → mac → browser → pendant → dashboard
- **model tier:** Deterministic policy and background repair planner; realtime model only explains the final fallback in one sentence.
- **latency:** Detect within 30 seconds of a lease/ACK timeout; fallback decision under 2 seconds after the owner asks.
- **cost:** Under $0.01 per failure scan; storage and status reads dominate.
- **security:** Fail closed for sends, purchases, deletion and credentialed browser actions. A fallback may create a local note/reminder or preserve a draft, but never retries a non-idempotent external mutation without physical consent. Every fallback carries a source receipt and an explicit 'prepared, not done' label.
- **missing:** Relay-job leases and requeue sweep for orphaned processing jobs; A typed fallback matrix mapping failure classes to reversible local actions; Cross-surface job-id mapping and durable approval decision storage; A delivery-aware rule using pendant downloaded/played ACKs rather than server acceptance alone

### ""These headlines disagree—what is actually known, what is disputed, and what would change your mind?""
- **useful because:** The owner's repeated news requests currently optimize for three short sentences, which hides disagreement and source quality. This capability turns a headline cluster into a compact epistemic map: independently corroborated facts, claims that are merely repeated, material omissions, and explicit unknowns. It helps the owner decide without pretending that a fluent summary is certainty.
- **path:** browser → mac → relay → pendant → dashboard
- **model tier:** Background model gathers and clusters sources; a higher-quality judgement pass is used only when sources materially conflict; realtime model speaks the final three-part answer.
- **latency:** 90 seconds for a fresh cluster; spoken answer under 12 seconds, with a dashboard expansion available.
- **cost:** Approximately $0.03–$0.15 per invocation, dominated by source retrieval and long-page extraction; cache source fingerprints for unchanged articles.
- **security:** Only public URLs and excerpts leave the machine. Do not infer private facts about named people beyond the sourced reporting. Every spoken claim needs clickable source IDs and a timestamp; label analysis versus reported fact. No posting, subscribing, or contacting sources without confirmation.
- **missing:** A durable source-cluster object linking article fingerprints to claims and counterclaims; A contradiction detector that distinguishes independent corroboration from copied wire text; A spoken-safe citation token that lets the owner ask 'which source?' and hear one at a time; A freshness and correction policy for replacing a cluster when a source updates

### ""I need to change this commitment—show me the least disruptive option, draft the affected messages, and wait for me to approve one.""
- **useful because:** Today the owner can read separate calendar, mail, browser, and reminder surfaces, but cannot ask the system to reason about the social and scheduling consequences of changing one commitment as a single situation. This gives them options rather than a brittle yes/no: preserve hard deadlines, identify who is affected, draft tailored notices or reschedule proposals, and leave every external action pending until the owner chooses.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Background model gathers the affected commitments and computes alternatives; realtime model is used only for the owner's spoken choice and concise explanation.
- **latency:** Initial impact map within 20 seconds; draft alternatives within 60 seconds; no external send until explicit physical or spoken confirmation under the existing approval policy.
- **cost:** About $0.02–$0.10 per invocation, dominated by authenticated mail/calendar/browser reads and draft generation; no cost for the deterministic constraint pass.
- **security:** Never send mail, edit calendar, cancel appointments, or expose private attendee details without explicit approval. Show each option's assumptions, affected people, source timestamps, and irreversible steps. Keep drafts local by default; the pendant hears only counts, times, and the selected option unless the owner asks for content.
- **missing:** A unified read model for commitments with real calendar/reminder permission truth rather than empty-read ambiguity; A constraint solver for hard deadlines, travel/transition buffers, attendee impact, and reversible alternatives; A durable draft bundle linking every proposed message and calendar mutation to one owner approval decision; A cross-surface impact preview that can revalidate all sources immediately before approval


## What it asked for

_Nothing._
## Its own summary

This round produced three distinct owner-facing capabilities: (1) a departure ritual on the existing offline moment bookmark that joins imminent commitments, unfinished jobs, browser state, and mail into a short checklist; (2) safe failure fallback that converts stale/offline work into a clearly labeled local draft, reminder, or alert without retrying dangerous mutations; and (3) a news-disagreement explainer that separates corroborated facts, copied claims, disputes, omissions, and unknowns with source-linked spoken citations. The morning-brief idea was correctly rejected as already present in the backlog, so I did not count or rephrase it.

**Biggest unknown:** I still need owner-set values, not guesses: what counts as 'leaving soon' (time horizon), how many departure items may be spoken, which reversible fallback types are allowed automatically, and whether public-news analysis may retain source excerpts. Implementation still needs marker_kind added to the existing bookmark payload, relay job leases/requeue, and a durable source-cluster/contradiction record.

