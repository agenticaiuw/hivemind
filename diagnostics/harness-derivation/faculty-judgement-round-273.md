# Harness derivation — faculty-judgement — round 273

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Before I send or submit something consequential, give me a private adversarial review: what could be wrong, who could see it, what assumption is weakest, and a safer revision I can approve."
- **useful because:** The system should protect the owner from fluent, expensive mistakes—not merely execute drafts. The Mac or browser gathers the draft and recipient context; the relay model challenges it; the pendant gives the owner a short, interruption-safe verdict and lets them request a revision without exposing the draft aloud. Nothing is sent automatically.
- **path:** browser → mac → relay → pendant
- **model tier:** background for evidence extraction and first-pass critique; realtime only for the owner's spoken follow-up and concise verdict
- **latency:** 3–8 seconds for a review of one draft; under 1 second for the spoken follow-up after the critique is cached
- **cost:** Roughly one background model call plus optional realtime turn; dominated by draft/context tokens, typically <$0.03 for a short review
- **security:** Draft content and recipient identity remain on the Mac/browser unless the owner has allowed relay review; secrets must be withheld from spoken output; this is advisory only and must require explicit physical approval before any external mutation.
- **missing:** A typed draft-review envelope that carries draft hash, recipients, audience, evidence references, critique, and expiry across Mac/browser/relay; A redaction-aware review prompt that can distinguish claims needing evidence from private values; A pendant interaction binding one spoken request to the review hash without reading the draft aloud

### "At the end of my day, ask me what actually happened—not just summarize my notes—and turn the corrections into tomorrow's plan."
- **useful because:** A summary repeats the system's assumptions; a debrief lets the owner correct them. It would compare calendar/routine intent, reminders, mail and completed Mac/browser receipts with the owner's brief spoken account, identify what was missed or unexpectedly important, and produce a small, reviewable tomorrow plan. Over time this is how the system learns the owner's real priorities instead of optimizing for stale metadata.
- **path:** pendant → relay → mac → browser
- **model tier:** background model for assembling the day and extracting discrepancies; realtime model only for the 2–3 short spoken questions and final confirmation
- **latency:** Prepare in under 10 seconds at the scheduled evening window; each question should be answered in one short turn
- **cost:** One compact background call per day, usually <$0.02; realtime cost is limited to the owner's answers
- **security:** The debrief combines calendar, mail, browser and action history, so source-by-source consent and redaction are required. Never infer that an unmentioned plan was completed. Corrections that create reminders or change durable memory require explicit confirmation; retain the owner's answer as a short provenance-linked fact, not raw audio.
- **missing:** A durable debrief record with planned items, observed receipts, owner corrections, unresolved items and explicit confidence; A join from relay routine/job IDs to Mac/browser receipts (the current IDs are unrelated); A safe writer that turns confirmed corrections into memory facts, reminders and the next-day briefing without duplicating existing scheduled briefings; A pendant dialog state that can ask one question at a time and survive a dropped link

### "Did you actually reach me with that brief, or did you only generate it? Show me what was downloaded, played, interrupted, or never delivered—and quietly retry only what I missed."
- **useful because:** A completed server job is not the same as the owner hearing it. This gives the owner an honest answer after a dropped link, a busy pendant, or an interrupted playback, and prevents duplicate replays by using the artifact and playback cursor rather than guessing from job status.
- **path:** relay → pendant → mac → browser
- **model tier:** deterministic receipt reconciliation first; background model only to summarize multiple failures in owner language; realtime only if the owner asks during playback
- **latency:** Under 500 ms for a single artifact status; under 3 seconds for a day's delivery history
- **cost:** Negligible for reconciliation; <$0.01 only when a model summarizes several events
- **security:** Expose artifact IDs and timestamps, not audio contents, unless the owner explicitly asks. Retry must be idempotent, obey the universal stop latch and attention policy, and never replay a private item while the pendant is unavailable or the owner is speaking.
- **missing:** A durable cross-surface delivery ledger joining relay job, audio artifact, pendant session and item cursor; A user-facing query and retry policy that distinguishes not-downloaded, downloaded-not-played, interrupted and completed; A deduplicated replay action that preserves item position and records why the retry was allowed

### "Never turn a plausible guess about my life into a fact. Before you remember something, act on it, or tell me it is true, show whether it came from my words, a live source, or your inference—and ask me only when the distinction could change what happens."
- **useful because:** The most dangerous failure is not a bad click; it is a confident fiction becoming durable context and then steering every later decision. The owner should have one epistemic boundary across the pendant, relay, Mac and browser: observations remain observations, inferences remain labeled hypotheses, and only confirmed claims can influence external actions or long-lived memory.
- **path:** pendant → relay → mac → browser
- **model tier:** A cheap deterministic classifier and provenance check on every result; use the expensive model only to resolve conflicts or explain why a claim is consequential; realtime is reserved for the owner's brief confirmation.
- **latency:** Under 150 ms for ordinary source labeling; under 2 seconds when a conflict or consequential inference needs a spoken clarification.
- **cost:** Near-zero for typed provenance checks; occasional <$0.02 model call for conflict explanation, dominated by the competing evidence snippets.
- **security:** Do not speak private evidence merely to justify a claim. Preserve source IDs and hashes rather than raw quotations where possible. A claim marked inferred must never authorize a send, purchase, deletion, or durable memory write without explicit owner confirmation; revocation must invalidate downstream uses.
- **missing:** A pre-commit epistemic gate that every memory writer, planner and executor must call before persisting or acting; A common claim envelope with status observed|owner_stated|inferred|conflicted|revoked, source references, freshness, and consequence level; Propagation from a revoked or corrected source to derived facts, plans, reminders and pending actions; A compact pendant explanation such as 'you told me', 'I read this', or 'I inferred this' without exposing sensitive content

### "Notice the recurring things I keep compensating for, and propose one change that would remove the cause—not another reminder. Show me the evidence and let me accept, reject, or defer the change."
- **useful because:** The owner should not have to repeatedly invent workarounds for missed briefings, stale browser sessions, duplicated routines, or misunderstood preferences. A longitudinal friction detector would look across receipts, corrections, cancellations and repeated manual steps, then recommend a concrete change to a routine, policy, hardware interaction or model route. It turns the hive mind into something that improves the owner's life rather than merely completing more tasks.
- **path:** pendant → relay → mac → browser
- **model tier:** Background model over compact event aggregates, not raw transcripts; realtime only to present the single highest-value recommendation and capture accept/reject/defer.
- **latency:** Weekly or after a meaningful pattern; preparation under 20 seconds, spoken recommendation under 30 seconds.
- **cost:** One low-frequency background analysis, roughly <$0.05 depending on the event window; most work is deterministic counting and clustering.
- **security:** Do not infer personal shortcomings or health traits from behavior. Keep evidence source-linked and locally summarized; recommendations must be reversible or explicitly labeled as a proposed configuration/hardware change. Never silently alter routines, permissions, memory retention, or model routing.
- **missing:** A cross-surface event stream that normalizes failures, retries, owner corrections, manual repeats and abandoned actions; A pattern engine that distinguishes systemic friction from a one-off incident and estimates owner-time saved; A proposal lifecycle with evidence, expected benefit, affected surfaces, rollback plan and owner decision; A durable link from accepted proposals to the change and later measurement of whether friction actually fell


## What it asked for

_Nothing._
## Its own summary

This round produced three owner-facing capabilities: (1) an adversarial private review before consequential sends/submits, with evidence, audience-risk and safer revision; (2) an evening reality debrief that compares plans with receipts and asks the owner what actually happened before updating tomorrow; and (3) truthful proof of audio delivery, distinguishing generated, downloaded, played, interrupted and missed items. The third is close to an existing delivery-history idea, so it should be merged rather than restated. I still need durable cross-surface joins (relay↔Mac↔browser↔pendant), a debrief record/writer, and a draft-review envelope. Owner policy questions remain intentionally open: which content may reach the relay/TTS, what requires physical approval, and what counts as consequential.

**Biggest unknown:** Whether the owner wants the system to retain short spoken debrief corrections as durable memory, or treat each evening's correction as ephemeral unless explicitly saved.

