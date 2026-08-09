# Harness derivation — relay-realtime — round 273

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If I say something like 'the Outlook thing', check its status."
- **useful because:** Voice references are fuzzy; this lets the owner talk naturally and still get accurate status without re-identifying job IDs.
- **path:** relay
- **model tier:** Realtime, because the owner is waiting on a spoken answer.
- **latency:** Under 2 seconds for a spoken status.
- **cost:** Very low; a single read of relay job records.
- **security:** Must not invent success. Speak the tool’s spoken field verbatim, and avoid adding details.
- **missing:** None for basic status; but richer receipts would benefit from structured job metadata.

### "File a bug report from the pendant logs."
- **useful because:** Turns real-world failures into actionable reports automatically, which is huge for a wearable under development.
- **path:** pendant → relay → mac-bridge
- **model tier:** Realtime to confirm capture; Mac/relay to assemble and file the report.
- **latency:** Capture should be immediate; filing can take longer and be asynchronous.
- **cost:** Moderate; log upload plus report generation. Dominated by transport and any attachments.
- **security:** Logs may contain sensitive info. Redact secrets and require confirmation before sending externally.
- **missing:** A standardized UART log ingestion route from relay to Mac.; A report generator that can attach firmware version, timestamps, and minimal reproduction.; A safe destination (issue tracker integration) with credentials managed on the Mac.

### "Call my dentist and reschedule me for the earliest slot next week; handle the conversation and interrupt me only when you need a decision."
- **useful because:** The owner can delegate a real-world phone task while walking, without sitting at the Mac or manually relaying what the other person says. This is a genuinely cross-surface capability: the pendant supplies intent and decisions, the Mac/iPhone places the call, and the relay remains the low-latency conversational coach.
- **path:** pendant → relay → iOS → mac-planner → mac-vision
- **model tier:** Realtime relay for the owner's short decisions and turn-taking; gpt-5.6-luna for call planning and extraction; gpt-4.1-mini vision only for phone UI state.
- **latency:** Initial call setup under 10 seconds; spoken decision requests under 2 seconds; otherwise the phone conversation proceeds in real time.
- **cost:** Roughly $0.05-$0.30 per call depending on duration and transcription; telephony audio streaming and model inference dominate.
- **security:** The counterpart's voice and potentially health or financial details leave the phone and pass through the relay. The owner must explicitly start the call, hear who is being called, and be able to stop it immediately; do not silently record or send commitments beyond the requested constraint.
- **missing:** A bidirectional iPhone telephony-audio bridge exposed to the Mac agent (iPhone Mirroring UI alone cannot safely provide counterpart audio to the relay); Call-state and hangup controls with a hard physical stop from the pendant; Streaming speech-to-text/text-to-speech turn exchange and explicit recording disclosure; A durable call transcript/result receipt tied to the job, with sensitive-data retention controls

### "I'm away from my desk. Look at the thing open on my Mac, explain what it is in one sentence, and if it is broken, repair it and tell me exactly what changed."
- **useful because:** This makes the worn pendant a remote pair of eyes and hands rather than merely a command microphone. It combines current-screen perception, terminal/browser action, and a concise spoken explanation, allowing the owner to recover from a stuck app or broken development task without returning to the Mac.
- **path:** pendant → relay → mac-vision → mac-terminal → mac-planner → browser-extension
- **model tier:** gpt-4.1-mini for rapid screenshots and UI grounding; gpt-5.6-luna for diagnosis, repair planning, and change summary; realtime relay only for the conversation.
- **latency:** First spoken diagnosis within 5 seconds; repair may run asynchronously with a completion alert.
- **cost:** $0.02-$0.15 per investigation depending on screenshot count and shell output; vision calls dominate.
- **security:** Screenshots may contain passwords, private messages, or source code. The Mac agent must redact known secrets before sending frames, keep raw screenshots ephemeral, and report every mutation. The owner has approved broad access, but a physical stop and truthful failed-state report remain essential.
- **missing:** Re-enable and expose the currently disabled computer-use/vision loop; A relay-visible screenshot and incremental observation stream rather than only a final Mac job result; Structured before/after file, app, and process diffs for an honest change report; A pendant interrupt that cancels an in-flight repair, not merely shortens speech

### "Find the answer in my private Mac, browser, or phone data, and say the answer plus where you found it; if the sources disagree, ask me instead of guessing."
- **useful because:** The owner gets a trustworthy spoken answer while away, grounded in the private surfaces that public search cannot reach. The source disagreement behavior is more valuable than a generic assistant answer for questions like dates, commitments, account status, or the latest version of a document.
- **path:** pendant → relay → mac-planner → browser-extension → ios-control
- **model tier:** Cheap retrieval and ranking first; gpt-5.6-luna only to reconcile evidence and formulate the short spoken answer; realtime relay handles follow-up clarification.
- **latency:** First answer in 3-8 seconds for indexed data; live browser/iPhone checks may take up to 20 seconds and should stream a brief progress cue.
- **cost:** $0.01-$0.08 per query; embedding/search is cheap, while live browser or iPhone inspection and reconciliation dominate.
- **security:** Private mail, notes, browser pages, and phone content must not be mixed into unrelated prompts or persisted as broad memories. Return source labels and timestamps, retain only the answer provenance, and require the owner to explicitly name a sensitive surface when appropriate.
- **missing:** A unified cross-surface retrieval API over Mac files/mail/calendar, authenticated browser sessions, and mirrored iPhone state; Freshness metadata and conflict detection across results rather than selecting the highest-scoring snippet; A spoken provenance format that remains understandable in one sentence; Live-turn wiring of the existing scoped memory projection so stable preferences and task context are not resent as legacy blocks


## Changes it proposed to its own stack

### `integration` — Standardize a UART log capture path: relay collects pendant/bridge logs during a session, forwards to the Mac, and the Mac can attach them to bug reports. Include firmware version, build ID, and timestamps.
- **owner gets:** When something breaks in the field, they get a ready-to-file report instead of a vague complaint.
- effort: Medium. Needs a streaming/rotation format and a small ingestion route.  ·  risk: Logs can be large or contain secrets. Mitigate with size limits, redaction, and owner confirmation before upload.
- cost: Low to moderate; dominated by upload size.  ·  latency: Capture is streaming; upload may delay report creation.
- security: Potential data leakage; default to local-only until confirmed.


## What it asked for

_Nothing._
## Its own summary

Recorded three new owner-facing capabilities: a pendant-initiated phone-call concierge, remote visual diagnosis/repair of the Mac, and provenance-backed private cross-surface answers. The essential missing work is connective: bidirectional iPhone call audio and hard stop; a live screenshot/observation stream plus before/after diffs for the disabled vision loop; and a unified retrieval/conflict layer across Mac, browser, and iPhone. Existing plan/execute/job routes are building blocks, not those capabilities by themselves.

**Biggest unknown:** Whether the Mac/iOS harness can expose call audio and live screen observations without adding native bridges; neither is established by the routes available to this agent.

