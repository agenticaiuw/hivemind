# Harness derivation — faculty-judgement — round 91

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Don’t tell me something is done until you’ve verified it. If it failed, say what actually happened and what I should do next.”"
- **useful because:** Today a Mac or browser action can return a success-shaped receipt while accessibility, screen capture, or the browser bridge is offline and nothing changed. This gives the owner a trustworthy answer: independently observe the target state, classify the claim as observed/acknowledged/stale/unverified, and—when safe—offer a repair or a reviewable retry. It joins the pendant’s request and spoken status, the relay’s durable job record, the Mac’s actual state, and authenticated browser inspection; no one surface can establish the truth alone.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use the cheap background model for polling, normalization, and evidence comparison; use realtime only to speak the one-sentence verdict or ask for confirmation when a repair is consequential.
- **latency:** Initial verdict within 3 seconds for Mac state and 5–10 seconds for browser reinspection; longer investigations continue as a durable job and the pendant announces only when confidence changes.
- **cost:** Roughly $0.001–$0.01 per verification, dominated by model calls only when evidence conflicts; most checks are typed route responses and hashes. One extra browser/Mac observation is the main latency cost.
- **security:** Private page text and local state must remain scoped to the originating job and be redacted from spoken output. Never retry sending mail, purchases, deletion, or other irreversible actions automatically; require confirmation after showing the conflicting evidence. Keep evidence hashes and short snippets, not full page contents, under retention controls.
- **missing:** A durable evidence-claim record linking intent, action receipt, target state predicate, and independent observations; Typed observation adapters for common Mac outcomes and authenticated browser outcomes, including explicit bridge/permission health; A reconciliation policy that distinguishes observed, acknowledged, stale, and unverified and emits a repair proposal without silently retrying; Pendant delivery/acknowledgement of a changed verdict

### "“When I ask ‘why did I decide this?’ or ‘where did I see that?’, reconstruct the decision or fact from my own recent conversations, Mac documents, calendar, mail, and logged-in browser pages, with the original evidence and what is still uncertain.”"
- **useful because:** Today the system can search or summarize one surface, but it cannot reconstruct a trustworthy personal memory across the pendant, Mac, relay, and authenticated browser. This would preserve the owner’s reasoning and source—not merely a final answer—so they can recover a lost decision, link, commitment, or piece of research weeks later without manually remembering where it lived.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → browser-extension → dashboard
- **model tier:** Use a cheap background model to index and cluster opted-in events and a compact retrieval model to assemble a timeline; reserve realtime for the owner’s spoken query and final concise answer.
- **latency:** A normal query should return a sourced first answer in 3–8 seconds; deeper reconstruction can continue asynchronously and notify the pendant when additional evidence is found.
- **cost:** Approximately $0.005–$0.03 per query, dominated by embedding/re-ranking and only a small synthesis call. Incremental indexing is batch work and should use the cheaper tier.
- **security:** This must be explicitly opt-in by source and category, with private/off-record intervals, per-source retention, and secret redaction. Never ingest arbitrary browser pages or microphone audio by default. Show the source title, timestamp, and a short quoted fragment; require confirmation before exposing sensitive content aloud or sharing it.
- **missing:** An owner-controlled personal evidence index spanning pendant events, Mac files/notes/mail/calendar, and browser inspection results; A provenance graph that links claims to timestamped source fragments and records contradictions instead of flattening them; Capture and retention controls for explicit off-record windows and per-source inclusion; A query route that can return a ranked timeline with uncertainty and citations, plus a compact spoken rendering


## Changes it proposed to its own stack

### `integration` — Add an evidence-reconciliation coordinator between action execution and spoken completion: every reversible or consequential job declares a target-state predicate; after the receipt, it gathers an independent observation from the Mac or browser, records source/timestamp/health, compares it with the predicate, and updates the job to observed, acknowledged-only, stale, or unverified. If unverified, it schedules one bounded re-observation and presents a repair proposal rather than claiming success. Expose the evidence chain in the dashboard and a compact verdict to the pendant.
- **owner gets:** The owner stops having to discover later that “done” meant only that a command was accepted. They get a truthful one-line answer and a clear next step, even when the bridge or Mac permissions are broken.
- effort: Medium: typed state predicates and adapters for existing action types, a small durable evidence table, reconciliation worker, and pendant/dashboard rendering. Start with reminders, file creation, browser navigation, and drafts; expand action types incrementally.  ·  risk: A stale observation could be mistaken for current truth, or an overly strict predicate could report false failure. Include timestamps, health checks, confidence, and a visible “last observed” time; never auto-retry irreversible actions. Recover by rerunning observation or marking the claim unverified.
- cost: Low API cost: mostly route calls and hashes; approximately $0.001–$0.01 only for conflict explanation. Small durable storage increase per action (metadata plus hashes, not page contents).  ·  latency: Adds about 0.5–3 seconds for local Mac checks and up to 5–10 seconds for browser checks; asynchronous jobs can speak an interim “accepted, verifying” status.
- security: Evidence must inherit the originating job’s privacy scope, redact secrets from logs and speech, and retain snippets only when needed for owner review. Confirmation remains mandatory for sending, deleting, purchasing, or other irreversible repair.
- depends on: A durable evidence-claim schema and target-state predicates; Explicit Mac/browser health and permission signals in observation adapters; A pendant delivery/ack queue for revised verdicts

### `memory` — Create a provenance-first personal evidence graph rather than another generic context projection. At ingestion, each opted-in event becomes a source fragment with timestamp, surface, sensitivity, retention deadline, and cryptographic content hash; extraction creates claims linked to fragments, while contradictions remain separate. A temporal snapshot query then reconstructs what was knowable at a chosen time and labels later edits or stale pages instead of rewriting history.
- **owner gets:** They can recover not only an answer but the state of their life and the evidence behind a decision at the moment it was made. This prevents the assistant from confidently blending today’s changed page with an old conversation.
- effort: High: event adapters, encrypted index, temporal claim graph, source-level controls, redaction, retrieval API, and dashboard/talkback UI. Build a narrow first slice for pendant notes, Mac Notes/Calendar, and browser inspections.  ·  risk: Over-collection or a misleading synthesized memory could expose sensitive material or create false certainty. Default to explicit source opt-in, short retention, source citations, contradiction display, and a hard delete path; never treat inferred claims as facts without evidence.
- cost: Moderate storage and indexing cost; batch embeddings are inexpensive, with query cost roughly cents. Encryption and retention sweeps add operational complexity but no meaningful pendant API cost.  ·  latency: Event indexing is asynchronous. Query latency is 3–8 seconds for a first sourced timeline, with deeper retrieval continuing in the background.
- security: This is the most privacy-sensitive memory layer: per-source ACLs, encrypted-at-rest fragments, local redaction before relay upload where possible, no secret indexing by default, and spoken answers that avoid quoting sensitive text unless explicitly requested.
- depends on: Owner-facing source and retention controls; A durable event/claim schema with timestamps and provenance; A retrieval route that supports temporal snapshots and uncertainty; A reliable off-record latch across pendant, relay, Mac, and browser


## What it asked for

_Nothing._
## Its own summary

New proposal: a truthful completion contract that never equates an accepted receipt with a completed outcome. Each job declares a target-state predicate; relay, Mac, and authenticated-browser observations independently verify it and classify the result as observed, acknowledged-only, stale, or unverified. I recorded both the owner-facing capability and the integration change, built from the existing execute/job/receipt/browser/pipeline/Mac routes. What remains is connective implementation: durable evidence claims, target predicates, health-aware observation adapters, and pendant delivery of revised verdicts. No new orchestrator permission is needed for the design; GUI-level verification remains limited until the owner grants the already-known per-binary macOS TCC permissions.

**Biggest unknown:** Which concrete action types and target-state predicates should be first in the implementation (reminders/files/drafts/browser navigation), and the owner's preferred wording when an action is acknowledged but not independently observed.

