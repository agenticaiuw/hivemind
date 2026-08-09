# Harness derivation — relay-realtime — round 253

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If I say ‘open the thing I was working on’, figure it out."
- **useful because:** This is the hive-mind advantage: context from memory, Mac state, and browser sessions can resolve ambiguous references better than any single node.
- **path:** relay → mac-bridge → browser → memory
- **model tier:** Realtime for clarification; mac-planner for heavy lifting and disambiguation.
- **latency:** Under 2 seconds to ask a clarifying question when ambiguous; otherwise route immediately.
- **cost:** Moderate; dominated by context retrieval and planning.
- **security:** Ambiguity can cause the wrong action; prefer clarification when confidence is low and avoid destructive actions without confirmation.
- **missing:** Context projection wired into the live prompt so ambiguity resolution doesn’t resend large context every turn.; A reliable intent routing implementation (relay_route_intent is schema-only today).

### "“Check whether the schedule in my authenticated work portal agrees with my Mac calendar for tomorrow. Tell me exactly what conflicts, and if I say ‘fix it’, update the calendar and leave the portal untouched.”"
- **useful because:** Today the owner must manually compare two surfaces that each agent can reach separately. This would turn the pendant into a trustworthy discrepancy detector: evidence from the browser session and local calendar is joined before any mutation, and the owner gets a concise spoken answer while away from the desk. It is more useful than another generic briefing because it exposes contradictions rather than silently choosing one source.
- **path:** pendant → relay → browser-extension → mac-planner → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Realtime relay for the short request and spoken result; faculty-perception for extracting dated events and provenance; faculty-judgement for matching identities/timezones and classifying conflicts; mac-planner/browser-extension for reads and a separately confirmed calendar mutation. Use a cheaper background model for normalization and comparison.
- **latency:** Acknowledge in under 1 second, return a first conflict summary within 15 seconds, and continue evidence collection asynchronously if either surface is slow. Never claim agreement until both reads have receipts.
- **cost:** Roughly $0.03–$0.12 per comparison, dominated by two authenticated page reads and one structured comparison; the spoken relay turn is the small fixed part.
- **security:** Portal contents and calendar entries leave their current surfaces only as the minimum structured event fields and source URLs. Preserve per-field provenance, redact unrelated event bodies, and require an explicit second utterance for the calendar write. If either source cannot be read, say 'could not verify' rather than infer.
- **missing:** A cross-surface event-normalization and identity-matching worker with timezone-aware conflict rules; A provenance bundle that joins browser and Mac receipts into one spoken/reportable result; A narrow follow-up state so “fix it” refers only to the conflicts just shown; A browser-session read route for the authenticated portal, if the existing browser extension cannot expose it

### "“I lost my place. Tell me what I was doing across my Mac and browser, what the last unfinished decision was, and reopen only the files and tabs that belong to that thread.”"
- **useful because:** After an interruption, the owner currently has to reconstruct intent from scattered tabs, editor state, terminal history, and voice turns. The pendant is the one surface that can ask for this while they are walking back to the desk. It restores a coherent work thread rather than merely listing open windows, and it makes the Mac ready for the owner instead of forcing a second planning session.
- **path:** pendant → relay → mac-planner → browser-extension → mac-terminal → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use a cheap background summarizer to cluster recent Mac/browser/voice events; faculty-perception extracts concrete artifacts and unfinished actions; faculty-judgement selects one thread and marks uncertainty; realtime relay only speaks the short reconstruction. mac-planner performs reversible reopen actions after the owner says “do it.”
- **latency:** Speak a provisional one-sentence orientation within 3 seconds, then a grounded reconstruction within 12 seconds. Reopening should be a separate, observable job and must not disturb unrelated windows.
- **cost:** About $0.02–$0.08 per recovery, dominated by event summarization and context retrieval; no browser page content should be re-sent when stable event metadata is sufficient.
- **security:** Recent URLs, filenames, terminal commands, and voice transcripts are sensitive. Keep the reconstruction scoped to a user-selected recency window, exclude secrets and command output by default, and provide source labels (“Safari tab”, “VS Code file”, “last voice turn”) so the owner can reject a mistaken thread. Reopen only exact artifacts already observed; do not invent paths.
- **missing:** A durable cross-surface activity ledger with timestamps, artifact IDs, and redaction rules; A thread-clustering and unfinished-decision extractor that can join voice, browser, editor, and terminal events; A reversible reopen manifest with before/after receipts and a way to leave unrelated Mac state untouched

### "“Find every copy of the document I’m talking about across my open browser sessions and Mac, tell me which one is newest and which one I actually used, then offer to archive the stale copies without deleting anything.”"
- **useful because:** The owner loses time to duplicate downloads, stale exports, and similarly named files split between authenticated browser sessions and local storage. No single node sees both sides or can infer usage history. A spoken, evidence-backed deduplication pass would be useful while away from the desk and safer than a blind file search because it distinguishes newest from most recently used and makes archiving reversible.
- **path:** pendant → relay → browser-extension → mac-planner → mac-terminal → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Cheap models enumerate metadata and hashes; faculty-perception extracts document identity from filenames, page titles, and content fingerprints; faculty-judgement ranks canonicality using timestamps and observed usage; realtime relay speaks the shortlist. mac-planner performs a reversible archive only after the owner chooses the items.
- **latency:** Acknowledge immediately; return a ranked list of up to five candidates within 10 seconds and run deeper hashing in the background. Archive execution should return receipts within 20 seconds.
- **cost:** About $0.01–$0.06 per search, mostly local hashing and a few browser metadata reads; avoid uploading document bodies by comparing hashes and short local metadata first.
- **security:** Document names, URLs, and hashes are sensitive. Keep full content local to the Mac/browser, send only candidate metadata and provenance to the relay, and never expose authenticated page text unrelated to the named document. Archive to a dated recovery folder with an undo receipt; never silently delete.
- **missing:** A cross-surface document identity service that can match browser resources to local files using hashes, titles, and canonical URLs; Usage evidence from browser history/tab events and Mac open-file events, with explicit retention limits; A reversible archive transaction spanning browser downloads and local files


## What it asked for

_Nothing._
## Its own summary

Recorded three new owner-facing capabilities: (1) cross-surface schedule discrepancy checking with evidence and a separately requested calendar fix, (2) spoken reconstruction and selective reopening of a lost Mac/browser work thread, and (3) cross-surface document identity/deduplication with reversible archiving. The first is the highest-value: it catches contradictions between authenticated browser state and local calendar rather than merely summarizing one source.

**Biggest unknown:** Whether the existing browser session can expose structured authenticated portal records and whether the Mac agent already emits enough timestamped artifact/usage events to build the work-thread and document-identity layers. The required changes are the cross-surface evidence join, provenance, and reversible transaction state—not another relay utterance or generic planner.

