# Harness derivation — faculty-judgement — round 244

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Make my morning brief happen exactly once, and tell me if it was actually delivered and played."
- **useful because:** The owner currently has multiple daily brief routines at overlapping times, while calendar emptiness can falsely mean 'all clear' when EventKit is unauthorized. This makes one authoritative run, one artifact, one spoken delivery, and an honest delivered/played receipt—the most useful daily behavior this system could provide.
- **path:** relay → mac → browser → pendant
- **model tier:** Background model composes and deduplicates the brief; realtime is used only for a spoken status or owner follow-up. Deterministic policy handles schedule collision, permission confidence, and delivery state without an expensive model call.
- **latency:** At scheduled time, under 60 seconds to produce the brief; spoken status under 1 second after an owner query. If a source is unreadable, say so and do not substitute 'nothing happening.'
- **cost:** Roughly $0.01–$0.05 per brief depending on mail/browser context; most cost is one background composition, not receipt reconciliation.
- **security:** Do not speak calendar/mail content when source permission is uncertain; store only artifact IDs and delivery states in the relay receipt. Browser reads remain read-only. Routine deletion or changing the surviving schedule requires owner confirmation.
- **missing:** A durable routine-group/deduplication key so the four existing brief routines can be reconciled into one owner-approved schedule; A server-side join from relay job, Mac job, audio artifact, and pendant delivery ACK (current IDs are unrelated); A truthful EventKit permission/readability probe used by briefing composition rather than the false-empty day-plan path; An owner decision about which of the overlapping morning briefs survives and whether content may be spoken

### "Forget this fact everywhere, and prove which copies were removed or could not be removed."
- **useful because:** The system currently deletes a fact without touching the context graph, revokes evidence without removing derived facts, and has no global forget operation. An owner-facing erasure request should be a real cross-store operation with a bounded report, not a reassuring sentence that leaves copies behind.
- **path:** mac → relay → browser → pendant
- **model tier:** Deterministic source graph traversal and deletion first; a cheap model may summarize the receipt, but it must not decide what to delete. Any ambiguous match becomes a review item rather than an automatic deletion.
- **latency:** Under 10 seconds for local stores and relay tombstones; browser-origin fan-out may take up to 60 seconds and must remain pending until acknowledged.
- **cost:** Usually under $0.01; storage and traversal dominate, not model inference. No raw value needs to leave the Mac.
- **security:** Require explicit confirmation for the destructive operation. Match by stable source/capsule/fact IDs where possible, never broad substring deletion by default. Emit tombstones and preserve only minimal audit metadata. If a browser or relay is offline, say 'not yet erased' rather than claiming success.
- **missing:** A provenance edge from derived memory facts to evidence capsules/source records (memory facts currently lack capsuleId); A deletion cascade across facts, context graph, browser provenance, relay fleet memory, and pendant caches; A durable erasure job with per-surface acknowledgements, retry, expiry, and a final incomplete report; A read-only preview that lists exact records before confirmation

### "Give me the four newest items on my Safari Reading List, one sentence each, and let me save or dismiss each by button while you read them."
- **useful because:** The owner has asked this repeatedly, but today the system can only drive generic browser actions; it cannot identify Reading List entries as durable items, cite each source, or bind a pendant button press to the item currently being spoken. This turns a browser chore into a hands-free, resumable interaction.
- **path:** browser → relay → pendant → mac
- **model tier:** Browser extraction and item ordering are deterministic; a background model produces one-sentence summaries from the page text. Realtime only handles barge-in/button-bound item selection and short speech.
- **latency:** First item within 8 seconds if the browser is online; each subsequent item under 1 second from the queued artifact. If Safari is offline, report that and offer the last verified snapshot rather than inventing entries.
- **cost:** About $0.02–$0.08 for four summaries depending on article length; browser extraction and item actions are otherwise local. Cache summaries by URL/content hash to avoid repeat cost.
- **security:** Read-only by default; never publish, purchase, or send. Saving/dismissing changes Reading List state and needs the owner's deliberate item-bound button action. Strip page secrets and avoid speaking page text beyond the requested summary.
- **missing:** A typed Safari Reading List extractor in the browser extension (generic list_tabs/read_page does not expose Reading List as items); A durable item cursor that binds the current spoken item to a physical pendant press and survives a link drop; A read-only citation and content-hash record so a summary can be audited when the page changes; An executor action for save/archive/dismiss with idempotency and owner confirmation semantics

### "When I enter a meeting, give me a private, two-minute preparation in my ear from the actual invite and relevant open browser tabs, then let me ask for a person or topic without exposing the meeting to any service."
- **useful because:** The owner currently has separate calendar, browser, mail, and audio surfaces but no moment where they become one private preparation tool. This would turn the instant before a meeting—when context is most valuable and attention is scarce—into a reliable briefing, while keeping sensitive meeting material local unless the owner explicitly asks otherwise.
- **path:** mac → browser → relay → pendant
- **model tier:** Mac and browser gather invite metadata, related local notes, and explicitly allowlisted open tabs. A background model prepares the compact brief; realtime handles only follow-up questions and interruption-safe playback. A deterministic privacy policy blocks unapproved sources before model context is assembled.
- **latency:** Detect meeting start within 30 seconds; prepare in under 90 seconds; begin playback at a safe utterance boundary. Follow-up answers under 2 seconds when the relevant source is already cached.
- **cost:** About $0.03–$0.15 per meeting depending on the amount of page and mail context; local extraction and caching dominate latency, not audio synthesis.
- **security:** Meeting content, attendee names, and client information must not leave the Mac by default. Browser tabs require an explicit per-origin allowlist; no meeting recording or transcription. The pendant receives only the generated brief and opaque item IDs. The owner must confirm before any outward action such as sending a follow-up or creating a commitment.
- **missing:** A trustworthy meeting-state detector that combines calendar timing with foreground/browser evidence and distinguishes a scheduled event from an actual meeting; A local-only context assembler that links an invite to relevant notes and allowlisted browser tabs without sending raw content to the relay; A private-content speech policy enforced at every pendant audio entry point, not only the briefing-triage path; A resumable, item-addressable meeting brief with source citations and a physical stop/next control; An owner-configurable per-origin and per-calendar trust policy; conservative defaults must exclude all unlisted sources

### "Keep me understandable when the link or pendant is struggling, and tell me afterward if anything I said was lost."
- **useful because:** The pendant's 24 kHz path is now excellent under its tested conditions, but a real owner moves through radio fades, CPU pressure, and queue starvation. Today there is no end-to-end adaptive quality contract: the relay, codec, and speech recognizer can each appear healthy while words disappear. The owner should get graceful degradation rather than a silent failure.
- **path:** pendant → relay → mac
- **model tier:** Firmware and relay use deterministic measured thresholds for bitrate, frame size, retransmission, and uplink complexity. A slower model is used only to summarize a post-conversation loss report; realtime audio must never wait for it.
- **latency:** Adapt within one audio control interval (under 2 seconds) without audible clicks or a dropped utterance. Produce a concise loss report within 5 seconds after the conversation ends or reconnects.
- **cost:** Negligible model cost; modest radio bytes for authenticated metrics and occasional control envelopes. Engineering cost is substantial because adaptation must be validated against the measured 24 kHz acceptance criteria.
- **security:** Metrics must contain no PCM, transcript, or location. Control messages must be authenticated and monotonic so stale relay commands cannot downgrade or interrupt a newer session. Never claim speech was delivered unless the pendant ACK and recognizer receipt agree.
- **missing:** A signed end-to-end audio health contract carrying sequence gaps, queue depth, underruns, codec mode, and recognizer acceptance—not just server pipeline receipts; Firmware adaptation states with tested transitions among the shipped 24 kHz mode and a measured fallback, including click-free boundaries; A relay reconciliation layer that distinguishes microphone capture, radio upload, server receipt, transcription, and owner playback loss; An owner-facing post-call loss report tied to utterance ranges, with a clear 'unknown' state for unacknowledged data

### "Remember this only for this project and until Friday, then show me everywhere it was used and remove it."
- **useful because:** The owner can currently create facts and notes, but retention is mostly hard-coded by kind, scope is inconsistent, and deletion does not propagate from facts to the context graph, evidence, browser-derived claims, or relay memory. A spoken, time-bounded memory contract would let the owner use memory without turning a temporary detail into permanent personal history.
- **path:** pendant → relay → mac → browser
- **model tier:** Deterministic parsing enforces scope, expiry, and propagation; a background model may normalize the owner's wording and find dependent claims. Realtime confirms only the policy—never the sensitive value—over audio.
- **latency:** Acknowledge the contract within 2 seconds; apply expiry and revocation asynchronously but expose progress immediately. All dependent uses should be listed within 10 seconds on local stores and marked pending for offline surfaces.
- **cost:** Usually under $0.02 per memory contract; model cost is only for ambiguity resolution. Storage is small metadata plus source links, not another copy of the raw value.
- **security:** A missing or ambiguous expiry must fail closed to session-only rather than become permanent. Scope must be enforced at prompt projection and action planning, not merely displayed in a UI. Revocation must produce tombstones and explicitly report offline or unlinked copies that could not be removed.
- **missing:** A user-facing memory contract with real project/surface scope, expiry, and session-only default; Provenance links from every derived fact and context-graph entity to its originating capsule/capture/browser record; A propagation worker that enforces expiry and revocation across Mac, relay, browser, and pendant stores; A pre-use check that blocks an expired or out-of-scope fact from model context or external actions; An owner-readable use ledger showing which jobs, briefings, and actions consumed the memory


## What it asked for

_Nothing._
## Its own summary

This round produced three owner-facing capabilities: (1) exactly-once morning briefing with truthful source-readability and pendant delivery/playback receipts; (2) a cross-store 'forget this everywhere' operation with preview, confirmation, per-surface acknowledgements, and an incomplete-erasure report; and (3) hands-free Safari Reading List triage with four cited summaries and item-bound pendant save/dismiss controls. The delivery-status variant was rejected as already covered, so I did not restate it. I still need owner decisions—not infrastructure guesses—on which overlapping morning brief survives and whether notification content may be spoken; I also need the missing provenance links, durable cross-surface IDs, and Safari Reading List extractor identified in the proposals.

**Biggest unknown:** Whether the owner wants the morning brief to read calendar/mail/browser content aloud at all, especially when EventKit readability is uncertain; the system must ship conservative and say 'unreadable' rather than infer an empty day.

