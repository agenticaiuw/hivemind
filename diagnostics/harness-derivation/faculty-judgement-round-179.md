# Harness derivation — faculty-judgement — round 179

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### ""Start my day" — give me exactly one trustworthy brief, not three overlapping ones, and tell me if any source was unreadable or the pendant did not actually play it."
- **useful because:** The owner currently has multiple daily routines at 07:00/07:30 that can independently generate overlapping briefs. This turns the morning into one deduplicated, provenance-backed decision: calendar/mail/browser changes are ranked once, stale or unauthorized sources are disclosed, and delivery is confirmed rather than assumed.
- **path:** relay → mac → browser → pendant
- **model tier:** Background model compiles and ranks the brief; realtime model only handles the owner's follow-up. Deterministic policy and dedupe run without an LLM.
- **latency:** Compile within 20 seconds of the scheduled boundary; spoken delivery starts as soon as the first safe batch is ready. A delivery receipt may arrive later without blocking the answer.
- **cost:** About $0.01–$0.05 per daily compile depending on source volume; dedupe, reconciliation, and ACK handling are local/relay compute.
- **security:** Never claim calendar/mail was clear when EventKit is unauthorized. Sensitive content follows the owner's later policy; default is redacted spoken headlines and a private queued detail. Require confirmation before any action suggested by the brief. Browser and Mac evidence remain source-linked.
- **missing:** canonical briefing compiler that claims one schedule slot; routine overlap/deduplication keyed by semantic brief window; delivery-aware brief state joining audio artifact ACKs to the brief item; owner-configurable briefing policy rather than the current placeholder

### ""Did that actually get done?" — verify the final result of something you asked the Mac or browser to do, not merely whether the job was accepted."
- **useful because:** Today a receipt can mean generation or acceptance while the intended world state remains unverified. This gives the owner a truthful closed loop: it checks the final observable state, distinguishes completed/partially completed/blocked/unknown, and speaks one short answer with evidence and a safe next step.
- **path:** pendant → relay → mac → browser
- **model tier:** Cheap deterministic checks first; background model interprets mismatches. Realtime model is used only for the spoken clarification or when the owner asks a follow-up.
- **latency:** Return an initial accepted/failed status immediately, then verify within 5–30 seconds depending on browser/Mac readback. Never wait indefinitely or convert timeout into success.
- **cost:** Usually under $0.01 per verification; browser/Mac readback dominates latency, not model tokens.
- **security:** Readback must be least-privilege and avoid returning secrets or page bodies unnecessarily. A stale plan must be revalidated before any repair. Never retry an external mutation automatically; repairs require autonomy_policy_evaluate and, where applicable, physical consent.
- **missing:** typed postcondition contracts for common actions (file exists, reminder exists, page field changed, draft saved); a durable join between relay job ID, Mac/browser IDs, and the postcondition; read-only verifiers for reminder/note creation and selected browser/Mac outcomes; owner-facing status that separates not-run, ran-but-unverified, and verified

### ""What should I believe and do about this?" — compare the relevant browser sources, show me the disagreement, and stage one evidence-backed next action without sending or buying anything."
- **useful because:** The system can currently research and act, but it does not turn conflicting sources into an explicit judgement. This is the distinctive hive capability: the browser supplies authenticated and public evidence, the Mac can stage a draft, the relay explains the reasoning, and the pendant gives a compact spoken recommendation while preserving a reviewable citation trail.
- **path:** browser → mac → relay → pendant
- **model tier:** Background model performs extraction, comparison, and recommendation; realtime model only answers the owner's conversational question. Deterministic provenance and policy checks gate any staged action.
- **latency:** Initial spoken verdict in 15–30 seconds; evidence table and draft continue asynchronously. No external side effect without explicit owner approval.
- **cost:** Roughly $0.03–$0.15 per investigation, dominated by page extraction and synthesis; substantially cheaper when unchanged page-watch evidence is reused.
- **security:** Authenticated pages may contain secrets and third-party personal data. Keep raw bodies local, pass redacted excerpts/digests to the model, cite source IDs, and require explicit confirmation for drafts that leave the machine or any purchase/send action. Conflicting evidence must produce uncertainty, not a forced answer.
- **missing:** wire the existing browserProvenance and crossCheck modules into production routes; typed claim-to-evidence links that survive from browser extraction to recommendation; a recommendation object with uncertainty, alternatives, and a no-side-effect staged draft; a user-visible review surface on the dashboard and a short pendant summary

### ""Keep me from saying something private out loud." The pendant should recognize when another person is nearby, automatically switch to a terse non-content mode, and let me explicitly unlock detail for this conversation."
- **useful because:** Today speech confidentiality depends on the caller remembering a policy that the audio path does not enforce. A wearable that is always at the owner's mouth is the only surface that can stop disclosure at the last centimeter, before relay TTS or a bystander's ears. This is a felt safety feature, not a logging improvement.
- **path:** pendant → relay → mac → browser
- **model tier:** A tiny on-device acoustic/proximity classifier handles presence locally; the relay model only classifies the requested content and selects a safe rendering. Never send raw ambient audio for this purpose.
- **latency:** The public/private mode must change in under 300 ms and must fail closed during uncertainty. Content transformation can take 1–2 seconds, but the device must be able to suppress playback immediately.
- **cost:** One-time hardware addition roughly $5–$20 for a second microphone or proximity sensor and modest firmware work; negligible per-use model cost if the classifier is local.
- **security:** Ambient room audio must never leave the device. Presence inference is itself sensitive and should be ephemeral. Default behavior is no names, subjects, codes, or message bodies aloud; explicit owner unlock expires at utterance or short timeout. The Mac/browser provide context, but cannot override a pendant-local veto.
- **missing:** a local bystander/proximity signal (the current board has no reliable audience sensor); a firmware playback veto integrated before every decoded frame; a signed, expiring public/private unlock event shared by pendant and relay; a confidentiality gate in pendantSpeech/audioBrief, which currently have none

### ""If I say yes to this, what will it displace?" Give me a counterfactual schedule: show the time, commitments, and downstream tasks that would be crowded out before I accept a new meeting, deadline, or purchase."
- **useful because:** The current day-plan ranks items but does not simulate the consequence of adding one. The owner needs judgement before commitment: whether accepting a browser invitation or creating a reminder creates an impossible day, which existing obligation would move, and what tradeoff is being made.
- **path:** browser → mac → relay → pendant
- **model tier:** Deterministic interval arithmetic and policy rules produce the first feasibility result; a background model explains tradeoffs in one short spoken summary. Realtime is reserved for negotiating alternatives with the owner.
- **latency:** Under 5 seconds for local calendar/reminder data; up to 20 seconds if authenticated browser details must be read. No action is committed while the simulation is running.
- **cost:** Usually under $0.03 per simulation; cost is dominated by reading authenticated browser state when an invitation or deadline lives there.
- **security:** Read only until explicit approval. Do not infer a personal timezone from the pendant’s zoneless clock. Treat missing calendar permission as unknown rather than free time. Any proposed reschedule or acceptance must go through autonomy policy and physical confirmation when externally visible.
- **missing:** a typed interval/constraint simulation object rather than prose day-plan output; read access for the relevant reminder/task store and authenticated invitation details; a way to mark uncertainty and distinguish unavailable data from empty time; a reviewable alternative plan with reversible apply and evidence links

### ""When I am away from my Mac, preserve the exact decision I was in the middle of and resume it safely when I return." The pendant should tell me what was waiting, let me dismiss or defer it offline, and restore the Mac/browser context without replaying a side effect."
- **useful because:** A dropped link currently turns a partially understood task into a cold restart, while resuming an in-flight action risks duplicate mutations. The wearable, relay, Mac, and authenticated browser together can preserve the owner's *decision boundary*: what was observed, what was proposed, what still requires consent, and what must never be replayed.
- **path:** pendant → relay → mac → browser
- **model tier:** No expensive model for storage or safety transitions. A background model summarizes the preserved decision only when the owner asks; realtime handles the short offline/return conversation.
- **latency:** The pendant must receive a compact state envelope within 1 second of link loss; reconnection reconciliation within 5 seconds. Any mutation remains stopped until stale-plan revalidation and explicit owner consent.
- **cost:** Low ongoing model cost; roughly $0.01–$0.05 only when generating a return summary. Main engineering cost is durable state and browser/Mac context restoration.
- **security:** Persist opaque IDs and redacted summaries, never credentials or page secrets on the pendant. The envelope must expire, be signed, and carry a monotonic action epoch. On return, compare current browser/Mac state before showing approval; never replay a mutation merely because it was pending before disconnect.
- **missing:** a true cross-surface decision-boundary record joining relay/Mac/browser IDs; pendant inbox fields for deferred decision state and expiry (not a second queue); browser/Mac context snapshot and read-only restoration primitives; an end-to-end stale-plan reconciliation that blocks replay on changed evidence


## What it asked for

_Nothing._
## Its own summary

Round 179 produced three owner-facing capabilities. The highest-value one is a canonical, delivery-aware “Start my day” brief: deduplicate the owner’s overlapping routines, reconcile unreadable sources honestly, arbitrate attention once, and confirm that the pendant actually downloaded/played the selected items. I also proposed evidence-backed research-to-recommendation with explicit disagreement and staged no-side-effect action. The postcondition verifier was recorded but flagged as close to an existing backlog idea, so it should not be expanded or re-proposed without a genuinely different boundary.

**Biggest unknown:** I still need an owner decision on personal timezone versus the Mac’s authoritative America/New_York routine zone (the owner memory says America/Chicago), and on which notification/content classes may be spoken aloud. Until those are stated, the briefing must conservatively redact content and disclose timezone ambiguity rather than silently choose. Implementation-wise, the canonical brief still needs a semantic routine deduper and a durable brief-item-to-pendant-delivery join; existing policy, triage, provenance, and ACK primitives are not yet one end-to-end user-visible flow.

