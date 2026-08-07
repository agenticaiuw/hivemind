# Harness derivation — unified — round 138

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“What did I decide, and why?” — reconstruct the decision from my recent spoken exchanges, calendar, Mail, local files, and logged-in browser pages, then give me the evidence, alternatives I considered, and the next commitment."
- **useful because:** People routinely remember the outcome but lose the reasoning. This would turn the pendant into a reliable decision memory rather than another search box, with citations and uncertainty instead of invented recollection. It requires the wearable conversation, always-awake relay, Mac-local sources, and authenticated browser sessions together.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-terminal → dashboard
- **model tier:** background for evidence gathering and synthesis; realtime only for the short spoken answer and follow-up questions
- **latency:** Initial spoken answer under 8 seconds when sources are cached; cold cross-source reconstruction up to 60 seconds, with pendant progress and a reviewable brief on Mac.
- **cost:** Roughly $0.03–$0.15 per reconstruction; dominated by source extraction and synthesis tokens, not device work.
- **security:** Evidence may include private mail, files, browser pages, and audio transcripts. Keep raw content on Mac where possible, send only selected excerpts to relay/model, encrypt the evidence bundle, cite every claim, and require confirmation before turning a reconstructed commitment into an action.
- **missing:** A unified, consent-scoped decision/commitment index spanning conversation, Mac files, calendar/mail, and browser sessions; A source-citation schema with timestamps and confidence that can survive browser tab changes; A retrieval route that can search those heterogeneous sources without projecting all secrets into the prompt

### "“Act on this private page, but don’t let its secrets leave my devices.” Before any model call, classify the data, keep sensitive fields on the Mac/browser, send only the minimum redacted task context, and let me approve the exact fields that would cross the boundary."
- **useful because:** The system can reach logged-in accounts, but today the owner must choose between useful automation and trusting an opaque prompt projection. A visible, per-field privacy boundary makes browser and Mac agency safe enough for daily use.
- **path:** browser-extension → mac-planner → mac-terminal → relay-realtime → pendant → dashboard
- **model tier:** cheap background classifier/redactor for fields and DOM regions; realtime model only for the owner's spoken policy questions or approval conversation
- **latency:** Redaction preview under 1 second for a page already inspected; up to 3 seconds for a large document. Never block local-only actions on a network round trip.
- **cost:** Usually <$0.01 per action using local classification; model cost only when ambiguous fields need review.
- **security:** The classifier itself must not upload the content it protects. Use local DOM/file inspection, deterministic secret detectors, an explicit allowlist of fields, and a fail-closed default. The pendant approval must identify the destination, purpose, and fields, not merely say “approve.”
- **missing:** A local Mac/browser data-classification and redaction service with typed field-level labels; A cross-surface policy evaluator that can enforce no-upload, relay-only, or approved-destination rules; A compact pendant approval protocol that can represent field classes and denial offline

### "“During this meeting, listen quietly and keep me useful.” With one button press on the pendant, capture only the meeting-relevant audio, identify names/decisions/action items, cross-check dates and links against my Mac and logged-in browser, and whisper a short prompt only when I am about to miss a commitment."
- **useful because:** This is a true wearable-to-computer loop: the pendant supplies an always-available, low-friction microphone and private cue channel; the Mac and browser supply the surrounding facts; the relay coordinates without forcing the owner to stare at a screen. It reduces cognitive load in meetings while remaining opt-in and quiet.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-vision → dashboard
- **model tier:** realtime for bounded audio segmentation and urgent cue generation; cheaper background model for transcript cleanup, entity resolution, and action-item extraction
- **latency:** Private cue within 2 seconds of a detected question or commitment; rolling summaries every 2–5 minutes; full meeting brief within 2 minutes after stop.
- **cost:** $0.10–$0.50 per hour depending on audio bitrate and realtime minutes; background extraction dominates only after the meeting.
- **security:** Recording must be a deliberate button gesture with a visible LED and spoken start/stop confirmation; default to on-device ring buffer and delete raw audio after extraction. Do not surveil bystanders or send audio to browser/cloud without explicit policy. Cues must be suggestions, never autonomous speech in the meeting.
- **missing:** A consent-aware meeting capture mode with hardware-visible recording state and bounded retention; Low-latency audio segmentation and diarization that can run on the current pendant/bridge split; A cross-source entity/date/link resolver joining transcript facts to Calendar, Mail, files, and authenticated browser tabs; A private cue channel that can interrupt playback without leaking meeting content

### "“If I accept this, what happens?” Before I approve a calendar invite, purchase, booking, or logged-in form, build a time-and-obligation simulation across my calendar, travel, tasks, and existing commitments; show the conflicts, downstream changes, and reversible alternatives, then let me choose."
- **useful because:** The owner currently gets either a draft or an action, not a dependable picture of consequences. This would prevent double-bookings, missed travel connections, accidental commitments, and cascading changes by using the browser and Mac as evidence sources while the pendant makes the decision available hands-free.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-terminal → dashboard
- **model tier:** background model for extracting constraints and generating counterfactuals; realtime only to answer the owner's follow-up and read the compact comparison aloud
- **latency:** A cached comparison in under 5 seconds; a cold browser/Mac investigation in under 45 seconds with progress updates and no mutation until approval.
- **cost:** Approximately $0.03–$0.20 per simulation; browser extraction and constraint resolution dominate, while the final synthesis is small.
- **security:** The simulator touches private calendars, bookings, tasks, and account pages. Keep raw records local, transmit only normalized constraints, label inferred assumptions, and treat every external mutation as a separate explicit approval. Never imply a cancellation or reservation is reversible unless verified.
- **missing:** A temporal/obligation constraint graph that can represent travel buffers, recurring commitments, deadlines, and cancellation rules; A pure counterfactual execution mode that computes browser/Mac changes without submitting them; A normalized diff renderer and spoken comparison format for the pendant; Verified connectors for calendar, task, travel, and authenticated transaction semantics

### "“Put that on my screen.” Resolve “that,” “this,” and “the one we were discussing” from the pendant conversation against the Mac’s focused app and Safari tabs, then open the exact source, highlight the relevant passage, and keep the spoken and visual views synchronized."
- **useful because:** A wearable has no reliable pointer or screen. This would make natural deictic speech useful instead of forcing the owner to repeat URLs, titles, or account names, joining the pendant’s immediate context to the Mac/browser’s visual reach.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** realtime model for resolving the short reference; cheap local ranking for candidate tabs/windows and deterministic highlighting
- **latency:** Resolve and open in under 2 seconds when the focused context is available; ask one concise clarification rather than guessing when confidence is low.
- **cost:** Under $0.01 per handoff in the common case; occasional model disambiguation is the main cost.
- **security:** Focused-page contents can be sensitive. Candidate ranking should stay local, reveal the chosen title/domain before opening, and refuse cross-account ambiguity. Never highlight or narrate a private page to an unapproved output channel.
- **missing:** A continuously reported focused-context identity from Mac and browser with tab/window provenance; A cross-surface reference resolver retaining only short-lived conversation pointers; A browser action for stable semantic highlighting and scroll anchoring, not just navigation


## Changes it proposed to its own stack

### `interaction` — Add a cross-surface counterfactual session primitive: the relay assigns a simulation ID, Mac and browser adapters execute reads and hypothetical mutations against isolated in-memory state, every resulting constraint is typed with source/time/confidence, and the pendant receives a compact spoken diff. The session must expire without committing and be promoted to a real job only after a fresh approval.
- **owner gets:** They can ask “what happens if I do this?” and get consequences before making a commitment, rather than discovering conflicts after a booking, invitation, or form submission.
- effort: High: temporal constraint graph, browser/Mac adapter snapshots, typed diff UI, and approval-to-job promotion across relay and local agent.  ·  risk: A simulation could omit an external side effect or model a site incorrectly. Mark unknown effects explicitly, prohibit real submissions, expire snapshots quickly, and require revalidation immediately before any promoted action.
- cost: Low incremental API cost for local simulations; roughly $0.02–$0.15 for model-based constraint extraction per session. Storage is short-lived state and diffs.  ·  latency: Adds 1–5 seconds for cached state and up to a minute for cold authenticated-page reads; provides progress rather than blocking silently.
- security: Private records remain on Mac/browser where possible. Simulation artifacts need sensitivity labels and short retention; promotion must re-check authorization and destination.
- depends on: A temporal/obligation constraint graph; Pure read/hypothetical adapters for Mac and authenticated browser actions; A typed cross-surface diff and approval protocol; Fresh pre-commit revalidation


## What it asked for

_Nothing._
## Its own summary

Recorded three new owner-facing capabilities: cited decision reconstruction across conversation/Mac/browser sources; a field-level privacy firewall that redacts before model calls; and an opt-in quiet meeting copilot using the pendant for capture and private cues while Mac/browser resolve commitments. The first is the highest-leverage long-term capability because it makes the whole hive a trustworthy memory of decisions, not merely an executor.

**Biggest unknown:** The connective primitives are still missing: a unified provenance/decision index, local field-level data classification and policy enforcement, and consent-aware low-latency meeting capture/cue delivery. No new orchestrator grants appeared this round. The current USB-attached pendant is testable, but LTE registration and the complete audio acceptance target remain unavailable; Accessibility should not be re-requested.

