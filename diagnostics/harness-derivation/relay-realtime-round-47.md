# Harness derivation — relay-realtime — round 47

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "While I’m away from my Mac, let me say “keep an eye on this and tell me if anything changes,” then have the pendant later interrupt me only when a meaningful change is verified across my authenticated browser and Mac data."
- **useful because:** Today the owner must repeatedly ask, remember which surface was used, and be present when the Mac is available. This would turn a spoken request into a resilient personal watch: the relay understands it immediately, the browser observes sessions the Mac cannot reach, the Mac supplies local context when online, and the pendant delivers a short, actionable alert rather than a noisy stream.
- **path:** pendant → relay → browser → mac-bridge → dashboard
- **model tier:** Realtime model extracts the watch target and urgency from speech; a cheaper background model compares successive observations, verifies significance, and drafts the alert. Use the Mac planner only for local facts or actions that browser data cannot provide.
- **latency:** Acknowledge the request on the pendant within 1 second. Observation can be eventual (minutes), with alert delivery under 10 seconds after a verified change. The owner should be able to cancel or revise the watch by voice.
- **cost:** About $0.01–$0.05 per watch per day depending on polling frequency and page size; browser/session access and scheduled wakeups dominate, not the realtime turn. Use hashes, extracted fields, and conditional polling to avoid resending full pages.
- **security:** Authenticated page contents and Mac-local observations leave their source devices for comparison, so retention must be bounded and encrypted. The system must show what source changed and why it was considered meaningful; spoken alerts should avoid leaking sensitive content in public. Any resulting mutation remains an explicit downstream action, not an automatic consequence of observation.
- **missing:** A durable watch registry with ownership, expiry, pause/resume, deduplication, and cancellation by voice; Cron/Durable Object alarm execution for browser and Mac observations; A browser page-observation adapter that can safely re-use authenticated sessions and emit stable structured fields/diffs; A cross-surface evidence joiner that correlates browser and Mac observations without storing whole pages; Pendant push notifications with urgency-aware interruption and a compact spoken evidence payload; Dashboard controls for active watches, source permissions, last observation, diff, and expiry

### "When you tell me something, let me ask “why?” or “that’s wrong—fix it,” and have you replay the exact browser/Mac evidence, identify which claim failed, correct the answer, and avoid repeating that source mistake."
- **useful because:** A voice-only owner cannot inspect a dashboard or scroll through logs when away from the Mac. Today an incorrect spoken answer is effectively un-auditable. Evidence-backed conversational correction makes the hive trustworthy: the owner can challenge a result in one sentence and receive a corrected, source-specific answer rather than restarting the task.
- **path:** pendant → relay → browser → mac-bridge → dashboard
- **model tier:** Realtime handles the short follow-up and intent classification. A cheaper background model reconstructs the cited evidence and compares the challenged claim against fresh browser/Mac reads; use the realtime model only to explain the resulting correction naturally.
- **latency:** Answer “why?” from retained evidence in under 2 seconds. For “fix it,” start speaking within 1 second, refresh relevant sources within 10 seconds, and state clearly when correction is pending or impossible.
- **cost:** Roughly $0.005–$0.04 per audit/correction; the dominant cost is refreshing authenticated pages or invoking the Mac planner, while evidence lookup and claim comparison can use a small model.
- **security:** Evidence may contain private mail, work pages, or local files. Store redacted, encrypted claim-level citations with short retention and source-specific access controls; never read a sensitive excerpt aloud without the owner requesting it. Corrections must update answer provenance, not silently rewrite history.
- **missing:** A claim/evidence ledger linking every spoken assertion to source snapshots, timestamps, transformations, and confidence; A voice-addressable correction protocol that identifies the challenged claim from conversational context; Fresh-read adapters for authenticated browser pages and Mac-local state, with stable selectors and redaction; A correction history that tracks source reliability without treating one owner correction as universal truth; A pendant-friendly spoken citation format and dashboard view for full evidence

### "Let me say “send that to my notes,” “put this in the project,” or “show me that later,” even when “that” is on my authenticated browser and I’m away from the Mac; resolve the reference, carry the smallest useful excerpt plus a source link, and finish the handoff on whichever surface is available."
- **useful because:** The pendant has no screen and the owner is often away from the Mac, so ordinary copy/paste and tab switching are unavailable. This would make the whole hive feel like one workspace: browser context can become a Mac note or queued project item, while the pendant remains the voice interface and the relay preserves exactly what “that” referred to.
- **path:** pendant → relay → browser → mac-bridge → dashboard
- **model tier:** Realtime resolves the spoken deictic reference from the current conversation. A cheaper background model extracts a concise excerpt, title, and destination metadata; the Mac planner or browser adapter performs the final reversible handoff.
- **latency:** Resolve and acknowledge the referenced object in under 2 seconds. Complete a normal handoff in 5–15 seconds, with a spoken fallback if the destination surface is offline; never make the owner repeat the URL or title unless ambiguity is real.
- **cost:** About $0.005–$0.03 per handoff. Browser extraction and Mac execution dominate; a small model can summarize or normalize text, while the realtime turn only resolves the reference.
- **security:** Do not transmit entire pages by default. Use least-content transfer (title, selected passage, URL, and owner-specified note), preserve origin and timestamp, and reject ambiguous references rather than sending the wrong private material. Destination permissions and audit receipts must be visible in the dashboard.
- **missing:** A cross-surface object identity and reference resolver for tabs, pages, files, and prior spoken results; A minimal-content transfer envelope with source URL/path, selection, provenance, and sensitivity labels; Destination adapters for Notes/project stores and a durable queue when the destination device is offline; Conversation-scoped reference retention so “that” expires safely instead of pointing at an old sensitive page; A dashboard showing pending handoffs, payload previews, and undo links


## Changes it proposed to its own stack

### `model-routing` — Add an uncertainty-aware cross-surface fanout router. For a spoken request whose answer may differ by surface, relay-realtime emits a typed observation request to browser and Mac in parallel, each returns claims with timestamps, provenance, freshness, and confidence, and a lightweight reconciler decides whether they agree, are stale, or require one clarifying question. It must never execute a mutation from speculative observations; it only improves the answer or hands a resolved goal to the existing action tier.
- **owner gets:** The owner can ask naturally, even while away, without knowing whether the truth is in a logged-in website, a Mac file, or both. They get one answer that says when sources disagree instead of an overconfident answer from whichever node happened to respond first.
- effort: Medium-high: define an observation envelope, implement parallel dispatch and timeout handling in the relay, add freshness/confidence reporting to browser and Mac adapters, and build deterministic reconciliation tests for disagreement and offline nodes.  ·  risk: Conflicting or stale claims could still be merged incorrectly. Recovery is to preserve each claim, speak the disagreement, and ask the owner; circuit breakers must drop to single-source behavior if an adapter emits malformed provenance. No existing action path is changed until reconciliation is complete.
- cost: Small extra relay and storage cost; typically two cheap observation calls instead of one, with the expensive realtime model used only for the final spoken synthesis. Roughly $0.01–$0.08 per multi-surface query depending on page size and planner use.  ·  latency: Parallel calls keep common-case latency near the slower source (target 2–6 seconds); offline-source timeouts should be capped around 3 seconds and reported rather than blocking indefinitely.
- security: The envelope must carry source and sensitivity labels, not raw secrets into the other surface. Browser content and Mac-local data should be joined only in the relay's short-lived encrypted context, with redacted evidence retained in receipts.
- depends on: A typed observation/result envelope shared by relay, browser, and Mac; Browser and Mac adapters exposing freshness and provenance; Short-lived relay correlation state and timeout handling


## What it asked for

_Nothing._
## Its own summary

Recorded four new cross-surface proposals: verified change watches with meaningful-only wearable alerts; uncertainty-aware parallel browser/Mac observation and reconciliation; voice-addressable evidence replay and correction; and a minimal-content semantic handoff from authenticated browser context to Mac destinations. The owner cannot have these today because durable watches, cross-surface provenance, claim ledgers, reference identity, and offline destination queues are absent.

**Biggest unknown:** Which authenticated browser targets and project/note destinations the owner considers highest value; implementation should begin with a narrow allowlist and explicit source/destination adapters rather than assuming universal access.

