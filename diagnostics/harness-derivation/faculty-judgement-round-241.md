# Harness derivation — faculty-judgement — round 241

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Remember this moment.” (Later: “What was I doing when I marked that?”)"
- **useful because:** A physical sw1 mark should capture the owner’s actual working context, not just an unexplained timestamp: the current spoken item, foreground Mac app, browser tab/title, and any active job. It makes fleeting ideas and interruptions recoverable across a dropped link and lets the owner return to the exact place in their work.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Realtime only to acknowledge the mark; deterministic capture and later lookup should use the relay/background tier. No expensive model is needed for the snapshot.
- **latency:** Acknowledge locally immediately; relay event within 2 seconds when connected; Mac/browser context capture within 5 seconds. If unavailable, retain the mark and explicitly show missing surfaces.
- **cost:** Under $0.01 per mark; dominated by optional background summarization, which should be skipped unless requested.
- **security:** Browser URLs/titles and foreground-app state can be sensitive. Store a redacted digest by default, link exact evidence only on an owner retrieval request, and make the policy table decide whether browser content is included. Never claim a surface was captured if it was offline.
- **missing:** A typed cross-surface bookmark record joining the pendant marker to relay job, Mac job, browser command, and audio cursor IDs; A Mac endpoint that snapshots foreground app and browser tab without pretending Accessibility is available; A durable fleet-memory writer or local note writer for the bookmark projection; A retrieval route that searches bookmarks by time or spoken description

### "“That’s wrong—don’t use that source again,” while the pendant is speaking a briefing item."
- **useful because:** The owner can correct the mind at the moment an error is heard instead of waiting to find a dashboard control. The physical interruption binds the correction to the exact audio item; the system records what was wrong, shows the evidence chain, and can revoke or down-rank the offending source without losing the rest of the brief.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Realtime handles the short utterance and item binding; a cheaper background model classifies the correction and proposes a scoped memory/source change. Deterministic provenance and policy checks decide whether anything is revoked.
- **latency:** Stop/acknowledge in under 500 ms; draft the correction in under 3 seconds; never apply source revocation or persistent preference changes without explicit confirmation unless the owner has separately enabled that policy.
- **cost:** About $0.01–$0.04 per correction, dominated by transcription/classification; provenance lookup is local/relay storage.
- **security:** A correction may contain private or third-party content. Keep the raw utterance local where possible, pass only a redacted digest to the model, show the source IDs and proposed scope, and fail closed when the current audio cursor is unknown. Revocation must be scoped and reversible; do not silently erase unrelated facts.
- **missing:** A semantic correction record linking audio cursor, evidence capsule/source, claim, and proposed policy change; A correction-aware memory writer; current fleet memory has schema but no production writer; A safe UI/voice confirmation flow for source revocation versus merely marking a claim disputed; A pendant speech path that guarantees the correction is not itself spoken back in public

### "“I’m in public—tell me only what needs my attention, and put the details somewhere private.”"
- **useful because:** The pendant should distinguish urgency from disclosure. It can speak a neutral, short alert while routing the sensitive subject/body to the owner’s authenticated Mac/browser, instead of either blurting private content or suppressing an important deadline. This is a usable privacy boundary even when no OS Focus signal exists.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Deterministic sensitivity/redaction and attention policy first; use the realtime model only to compress a safe, non-identifying alert. Background work prepares the private detail page and evidence links.
- **latency:** Neutral spoken alert within 2 seconds; private detail page/draft within 10 seconds. If the Mac/browser is offline, queue the detail and say only that it is waiting.
- **cost:** Usually under $0.01; model cost is only for safe compression, while routing and redaction are local.
- **security:** The owner must set the policy table rather than inherit a guessed public/private trust list. Never expose subject lines, names, or snippets in the neutral alert; include a visible provenance trail on the private destination. Require confirmation before external sharing or destructive follow-up.
- **missing:** An owner-configurable disclosure policy mapping sensitivity and destination to speak/queue/block; A single enforcement point in pendantSpeech/audioBrief; today briefingTriage redacts but direct audio paths do not; A durable private-detail handoff with expiry and one-time retrieval, not a raw URL spoken aloud; A real presence/public-context signal; until then this must be explicit owner mode, not inferred from nonexistent Focus state

### "“Did it actually happen—not just get queued?”"
- **useful because:** Today a receipt can mean generation or acceptance while the real-world effect, browser state, and what the owner heard remain uncertain. The owner should receive a postcondition verdict: what changed, what independently confirms it, what did not happen, and what remains unverified. This prevents false confidence about sent, booked, changed, or heard outcomes.
- **path:** relay → mac → browser → pendant → dashboard
- **model tier:** Deterministic postcondition checks and receipt correlation first; use the slower model only to explain conflicting evidence in one short sentence.
- **latency:** For local actions, verify within 5 seconds; for browser or external effects, poll up to 30 seconds and then state unverified rather than guessing.
- **cost:** Under $0.01 per check; most cost is browser/Mac polling, not inference.
- **security:** Verification reads potentially private destinations and must be least-privilege. Never turn a read-back into a mutation. External side effects need the existing confirmation policy; conflicting evidence should be surfaced, not resolved by model confidence.
- **missing:** A typed postcondition schema per action kind; A durable join from relay job to Mac action/browser command and pendant delivery ACK; Read-only verifiers for common effects such as calendar/reminder/mail/browser state; A user-facing distinction among confirmed, accepted, partially verified, and unknown

### "“When I come back, tell me what changed while I was away, and why it matters.”"
- **useful because:** The system should form a bounded absence episode across the worn device, Mac, browser, and relay: completed jobs, failed or orphaned work, changed watched pages, new scheduled items, and unheard audio, ranked by consequences rather than by arrival time. The owner gets one coherent return briefing instead of separately checking every surface.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Background model composes the episode after deterministic event collection and deduplication; realtime is used only when the owner asks for the spoken recap.
- **latency:** Prepare in under 20 seconds after reconnection or return; spoken answer starts in under 2 seconds from a cached episode.
- **cost:** $0.02–$0.08 per absence episode, dominated by composition; collection and dedupe should be deterministic.
- **security:** Absence itself can be sensitive. Keep raw page/mail content on its source surface, pass only redacted facts to composition, expire low-value events, and let the owner choose whether the pendant may mention private categories aloud. Never infer physical location from connectivity.
- **missing:** A durable absence boundary with explicit start/end markers and clock provenance; One event ledger that joins relay, Mac, browser, and pendant records without duplicate IDs; Consequence ranking that distinguishes changed state from mere notifications; A cacheable episode artifact with source links and per-item dismissal

### "“Keep me from making the same mistake I made last time.”"
- **useful because:** The system should recognize a repeated risky pattern across sessions—such as approving an action after evidence went stale, missing a deadline after deferring it, or repeating a failed browser workflow—and intervene at the moment of choice with a concise, source-backed warning and a safer alternative. This is judgment that learns from outcomes, not a static reminder.
- **path:** relay → mac → browser → pendant → dashboard
- **model tier:** Background model mines completed, cancelled, corrected, and reversed action histories for candidate patterns; deterministic policy evaluates whether a warning is allowed. Realtime only delivers the short warning.
- **latency:** Pattern mining nightly or after a completed outcome; warning decision under 300 ms at an approval/action boundary.
- **cost:** $0.03–$0.15 per periodic mining run; action-time checks are local and cheap.
- **security:** A learned warning must never silently block the owner or become a hidden personality judgment. Show the exact prior evidence, confidence, expiry, and a dismiss/forget control. Keep sensitive prior content out of spoken warnings and require confirmation before any preventive mutation.
- **missing:** Outcome-linked learning records connecting an attempted action to its later success/failure/reversal; A typed, expiring “habit/risk pattern” with evidence references and owner dismissal; A policy hook that can warn without blocking, and an explanation route for why it fired; Cross-surface retention and revocation so deleting the source also removes derived patterns


## What it asked for

_Nothing._
## Its own summary

Round 241 produced three new owner-facing capabilities. Highest value is an in-utterance correction loop: “That’s wrong” pauses the exact brief item, binds the correction to its provenance, and proposes a scoped source dispute/revocation rather than forcing the owner into a dashboard. I also proposed context-rich physical bookmarks (sw1 mark joined to audio/Mac/browser state) and an explicit public-mode disclosure router (neutral spoken alert, private detail on authenticated Mac/browser). All three were recorded; the implementation gap is connective semantics between existing primitives, not another generic route.

**Biggest unknown:** The owner has not chosen the policy values that determine disclosure destinations, public-mode activation, or whether a correction may automatically down-rank a source. Until those are set, ship conservative defaults: no sensitive speech, no automatic revocation, and preserve an explicit reviewable draft.

