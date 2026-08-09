# Harness derivation — relay-realtime — round 175

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Tell me when that finishes, even if I walk away.”"
- **useful because:** Long-running tasks are awkward on a wearable: the owner shouldn’t have to keep checking. A completion ping would make the system feel like an assistant, not a pager.
- **path:** relay → mac-bridge → pendant
- **model tier:** Realtime only to acknowledge the request; cheaper background tier to monitor job status and prepare a spoken update.
- **latency:** Under 1 second to confirm the watch is set; minutes to hours for completion depending on the job.
- **cost:** Low per use. The expensive part is status polling and speech rendering; keep polling off the realtime tier.
- **security:** The spoken message could leak sensitive task names. Use minimal phrasing, avoid full content, and respect any owner preference to suppress notifications for certain apps or tasks.
- **missing:** A real asynchronous event delivery mechanism (relay_event_push is schema-only today).; A background monitor to watch job completion without a scheduler (or add a scheduler).; A delivery target (pendant inbox/alert pipeline) to receive and play the notification.

### "“Be my wearable safety net—if I’m about to make a risky change on my Mac, warn me and suggest a safer alternative.”"
- **useful because:** This could prevent costly mistakes when moving fast, especially from voice. The owner would feel protected without losing speed.
- **path:** relay → mac-bridge → browser
- **model tier:** Realtime to hear intent and provide immediate guidance; cheaper tier to analyze risk and propose safer steps.
- **latency:** Under 2 seconds for a warning; longer analysis happens on the Mac tier.
- **cost:** Moderate. Risk analysis costs tokens; keep it off the realtime tier where possible.
- **security:** It must not block the owner by default. For sensitive actions, it should ask for confirmation but not impose new hard gates that were already rejected.
- **missing:** Typed action observability with confidence scoring that doesn’t block execution.; A risk model that can inspect planned actions without needing to run them.; A consistent way to label actions as high-risk without requiring a policy gate.

### "“Take over from where I left off.” The pendant should reconstruct my unfinished task across my Mac apps and authenticated browser tabs, explain the current state in two spoken sentences, and let me continue by voice without reopening or losing anything."
- **useful because:** The owner is often away from the Mac and currently has to remember which app, tab, document, and partial edits were active. This creates a real hive-only handoff: pendant supplies intent and conversation, relay coordinates, Mac sees local state, and the browser facet sees authenticated sessions.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension
- **model tier:** Realtime relay for the short spoken summary; mac-planner and browser inspection should use cheaper background/local models, with mac-vision only when an app has no structured state.
- **latency:** Initial spoken state in 5 seconds; deeper reconstruction may take 15 seconds and should stream a concise provisional answer first.
- **cost:** About $0.03–$0.12 per invocation; dominated by one planner call and optional screenshot/DOM interpretation, not the realtime turn.
- **security:** Local app titles, document names, clipboard-derived context, and authenticated tab metadata leave the Mac only as structured summaries. Never transmit page contents unless needed for the requested continuation; redact secrets and require explicit confirmation before mutating a document.
- **missing:** A cross-surface task-state snapshot contract covering active app, windows, unsaved documents, browser tabs, selection, and pending jobs; A relay session handoff endpoint that binds the snapshot to the current pendant conversation; A safe resume operation that can target the captured app/tab without discarding unsaved work

### "“Do this, but protect what I’m working on.” Before carrying out a voice command, the system should snapshot the affected Mac app/browser state, execute the change, verify the intended result, and automatically restore the snapshot if the action damaged unrelated work."
- **useful because:** Voice commands are issued hands-free and the owner may not see the Mac. Today a planner can act, but there is no owner-visible, cross-surface recovery when an action lands in the wrong tab, replaces text, or changes the wrong document. This makes remote control dependable rather than merely powerful.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension
- **model tier:** Use deterministic Mac/browser snapshot and restore primitives first; use mac-planner for selecting scope and realtime relay only to narrate success or recovery. Reserve vision for ambiguous UI verification.
- **latency:** For small actions, 3–8 seconds including verification. For multi-step tasks, provide a spoken acknowledgement immediately and finish asynchronously with a durable alert.
- **cost:** $0.01–$0.08 for small actions; larger workflows are dominated by screenshots and planner turns. Snapshot storage is local and cheap.
- **security:** Snapshots may contain private text, files, and page state; keep them encrypted and local with bounded retention. Restoring must be scoped to the touched resources and never overwrite newer owner edits; if comparison is uncertain, preserve both versions and report the conflict.
- **missing:** Transactional snapshot/restore primitives in the Mac and browser harnesses; Action-to-resource dependency tracking so unrelated work is provably untouched; Verification receipts that include before/after hashes or semantic diffs, not only success text

### "“When I’m in a conversation, be my private memory.” With one button press, the pendant should mark the last spoken exchange; the relay should link it to the relevant calendar event, Mac notes/files, and the browser page I was using, then later answer “what was that thing?” with the source and exact follow-up action."
- **useful because:** A wearable can capture the moment and the Mac/browser can identify its surrounding context, but neither alone can reliably bind speech to the meeting, document, and authenticated page that gave it meaning. This turns fleeting voice into retrievable, grounded personal memory instead of another generic memo.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** Realtime relay records the marker and gives immediate acknowledgement; a cheaper asynchronous model performs entity linking and source extraction, with realtime only for later retrieval.
- **latency:** Acknowledge the marker under 500 ms. Correlation may take up to 30 seconds; retrieval should answer in under 4 seconds with a confidence/source qualifier.
- **cost:** $0.02–$0.10 per marked moment, dominated by transcription and cross-source linking. Keep raw audio only under the existing failure-buffer rule; retain compact transcript and references by default.
- **security:** This is sensitive personal and potentially bystander speech. Default to owner-controlled retention, encrypt records, exclude unrelated browser contents, and visibly indicate recording. Never infer or expose a source when confidence is low; say which source supports each answer.
- **missing:** A deliberate marker event that references the active voice-run and nearby timestamp; Mac/browser context capture with calendar/document/tab identifiers and permission-aware source adapters; A durable cross-source memory index with provenance, deletion, and confidence handling

### "“Cancel the thing I just asked for.” The pendant should identify the active Mac/browser job from natural speech, stop it safely, and report exactly what was already changed and what was reverted."
- **useful because:** Hands-free delegation is unsafe without a reliable abort handle when the owner notices a mistake after walking away. This is not a status notification: it is a cross-node control path from a physical button/voice session through the relay into an executing planner or browser workflow, with truthful partial-completion reporting.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension
- **model tier:** Realtime relay resolves the short cancellation intent; deterministic job cancellation and compensating actions run locally on the Mac/browser. Use a cheap planner only to generate a compensation plan when no native undo exists.
- **latency:** Acknowledge cancellation immediately; issue the stop within 1 second and speak a verified outcome within 5 seconds.
- **cost:** Usually under $0.02; compensation planning may add $0.03–$0.10. Most value comes from local cancellation and receipts, not model tokens.
- **security:** Cancellation must be scoped to the owner’s active session and job, not guessed globally. A stop may leave partial mutations, so the system must list them and never claim rollback without evidence. Keep an immutable local audit receipt.
- **missing:** A real POST /jobs/:jobId/cancel route and execution-side cancellation token; Compensating-action/undo metadata for plan and browser actions; Pendant-side disambiguation when multiple jobs are active, without requiring the owner to remember an ID

### "“Hand me my work when I get to the Mac.” The pendant should carry an unfinished voice task while I am away, detect the Mac becoming available over USB, open the exact apps/documents/tabs involved, and continue the same conversation on the desktop without making me repeat the request."
- **useful because:** The wearable is the only surface present during travel and the Mac is the only surface able to perform rich work. Today a dropped link or physical move forces a restart. This creates a tangible handoff that uses the currently real USB-connected hardware, while still working over LTE later.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension
- **model tier:** Realtime relay handles the initial request and concise handoff; a slower local planner restores the workspace and resumes the queued job. No expensive model should be called merely to detect USB presence.
- **latency:** Store the handoff immediately; on Mac attachment, restore within 10 seconds and give the owner a desktop notification plus a short pendant acknowledgement.
- **cost:** $0.01–$0.06, mostly one planner turn for restoration. USB serial presence detection is negligible; state storage is small.
- **security:** Bind handoffs to the paired pendant and Mac identity, encrypt pending transcripts, and expire them after a bounded period. Do not open private tabs or speak sensitive content until the physical pendant is present and the owner presses the button.
- **missing:** A pendant↔relay handoff record with resumable conversation and job state; USB serial registration/heartbeat from the live nRF9160 pendant to the relay/Mac agent; A Mac-side resume endpoint that atomically restores apps/tabs and attaches to the existing job

### "“Tell me what changed while I was gone, and only act on the important changes.” The relay should compare a bounded before/after snapshot of my Mac and authenticated browser sessions, cluster changes into decisions or risks, and let me approve one specific follow-up by speaking a number."
- **useful because:** A wearable owner cannot inspect dozens of tabs, documents, and queued jobs after being away. Existing status endpoints report isolated facts; they do not establish what changed during an absence or turn it into an actionable, source-grounded shortlist across nodes.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Cheap asynchronous diffing and clustering should do the scan; realtime relay only narrates the top three and routes the chosen action. Vision is fallback for apps with no structured change feed.
- **latency:** When the owner asks, provide a first three-item spoken digest in 5 seconds; complete low-confidence enrichment in the background and push only if it changes the ranking.
- **cost:** $0.03–$0.15 per scan depending on screenshots and page volume; cache hashes and structured metadata to avoid resending unchanged context.
- **security:** Snapshots must be local/encrypted and content minimized. Never read arbitrary authenticated pages merely because they are open; use an explicit allowlist of apps/sites and show provenance for every item. Approval must identify the exact item and target.
- **missing:** A durable snapshot/diff store with owner-configurable scope and retention; Change feeds or hashes for Mac documents, apps, jobs, and browser tabs/pages; A spoken numbered-selection protocol that binds approval to a specific diff item


## What it asked for

_Nothing._
## Its own summary

Recorded six owner-facing capabilities: cross-surface continuation, protected execution with recovery, context-linked memory markers, a pendant abort handle for active jobs, USB/LTE handoff from pendant to Mac, and an absence diff that turns Mac/browser changes into numbered spoken actions. The most useful is the resumable handoff/continuation: it lets the owner start work while away and resume on the exact Mac/browser state without repeating themselves. All require new connective state and control contracts rather than another isolated route; specifically cancellation/compensation, resumable session state, USB presence registration, bounded snapshots/diffs, and provenance-aware context joins.

**Biggest unknown:** Whether the recorder considers any of these close to existing backlog entries despite their explicit missing contracts. The proposals were accepted by the recorder, with several warnings that the named routes already exist and the missing value is the connective behavior between them.

