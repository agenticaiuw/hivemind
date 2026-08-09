# Harness derivation — faculty-judgement — round 243

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Make my morning brief happen once, with only sources that were actually readable, and tell me if it was delivered to the pendant."
- **useful because:** Today several daily routines overlap at 07:00/07:30 and calendar reads can silently look empty when permission is missing. The owner should receive one merged brief, not duplicate audio or a confident false all-clear, with a receipt that distinguishes generated, downloaded, and played.
- **path:** relay → mac-planner → pendant → dashboard
- **model tier:** background for source gathering and merge; realtime only for a one-sentence exception or owner follow-up
- **latency:** Prepare by the scheduled time; source checks under 10 seconds, audio generation under 30 seconds, and never block the owner on a missing pendant link.
- **cost:** About one background synthesis plus TTS/audio encoding per brief; roughly $0.01-$0.05 depending on source volume. Deduplication reduces repeated audio/model cost.
- **security:** Do not claim calendar/mail success from empty arrays; carry source permission/readability provenance into the brief. Spoken content must pass the existing redaction path. Mutating reminders or mail is out of scope and requires confirmation.
- **missing:** A durable morning-brief coordinator that claims overlapping routines exactly once; A routine/job lease and requeue path for interrupted generation; A source-readable verdict wired to briefing output rather than raw empty results; A single artifact identity shared from relay generation through pendant playback ACK

### "If an audio brief fails on the pendant, recover it automatically without making me hear the same thing twice."
- **useful because:** A generated brief is not useful merely because the relay says it succeeded. The pendant can now report download and playback outcomes; use those facts to detect checksum errors, interruptions, or no-audio delivery, then produce one shorter fallback or leave a clearly labeled unread item instead of silently losing the brief or replaying duplicates.
- **path:** relay → pendant → mac-planner → dashboard
- **model tier:** cheap deterministic controller for ACK classification and deduplication; background model only for a compact fallback summary; realtime is unnecessary
- **latency:** Classify an ACK immediately; enqueue fallback within 2 seconds of a confirmed failure, with no more than one retry per artifact.
- **cost:** Negligible controller cost; fallback synthesis/TTS only on failure, roughly $0.002-$0.02 per recovered item. Storage is a small opaque artifact/event record.
- **security:** Fallback must inherit the original item's sensitivity and provenance, never include raw diagnostics or credentials, and require no external mutation. Treat duplicate or out-of-order ACKs idempotently; do not replay until a failed terminal state is authenticated.
- **missing:** A relay-side recovery state machine keyed by artifactId and item identity; A compact fallback audio profile and an explicit terminal failure status; A pendant-visible distinction between retrying, recovered, and unreadable; A durable exactly-once link between generated item, delivery events, and the spoken item cursor

### "Before you tell me a consequential fact, check that it is still true and say when you are uncertain."
- **useful because:** The system can generate a polished answer from stale memory, an unreadable calendar, or a disconnected browser. A final evidence-and-freshness pass would turn silent uncertainty into an honest spoken qualifier, especially for deadlines, permissions, device state, and external-action previews.
- **path:** relay → mac-planner → browser → pendant → dashboard
- **model tier:** deterministic freshness/provenance checks first; a cheap background verifier compares claims to cited evidence; realtime is reserved for delivering the final short answer
- **latency:** Under 1 second for local state checks and under 5 seconds for a verifier; if verification cannot finish, speak a short 'I could not verify that' rather than waiting indefinitely.
- **cost:** Most checks are free; verifier calls roughly $0.001-$0.01 per consequential answer. No extra cost for ordinary conversational chatter that has no external or time-sensitive claim.
- **security:** Never send raw sensitive text solely for verification; use source IDs, digests, and minimal snippets. A failed check must block mutation and downgrade speech, not merely add a cosmetic confidence number. Preserve the evidence references for owner inspection.
- **missing:** A claim extraction and freshness gate immediately before speech or mutation; Typed freshness policies by claim kind (device state, calendar, mail, browser, memory); A response format that carries claim-level evidence and an explicit unverifiable state into pendantSpeech; A cheap verifier route that cannot itself trigger actions

### "Notice when I am overloaded and automatically make every spoken answer shorter, slower, and easier to resume—without making me configure a mode."
- **useful because:** The pendant is the only surface that can observe repeated barge-ins, abandoned audio, long pauses, and playback interruptions while the Mac can observe rapid app switching and unfinished actions. Today those signals are treated as isolated failures or attention events; the owner still receives the same dense response when they are clearly overloaded.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** deterministic signal aggregation and a cheap background classifier; realtime only renders the already-selected concise response
- **latency:** Update the estimated load state within 2 seconds of an interruption or abandoned item; apply it to the next utterance with no extra conversational turn.
- **cost:** Near-zero for local feature extraction; occasional background classification under $0.01 per state transition. No additional model call for ordinary replies once a state is available.
- **security:** Infer only interaction load, never medical or emotional diagnoses. Keep a short-lived local feature window rather than retaining raw audio or page contents. Show the owner which observable signals caused compression and provide an explicit dashboard reset.
- **missing:** A cross-surface cognitive-load state with decay and confidence rather than a binary focus flag; A response-rendering contract that supports concise, slow, resumable speech and preserves omitted detail for later expansion; Pendant playback/interrupt metrics joined to Mac/browser interaction telemetry; An owner-visible explanation and reset for automatically adapted verbosity


## What it asked for

_Nothing._
## Its own summary

This round added three distinct owner-facing capabilities: (1) a single exactly-once morning brief with honest source-readability and pendant delivery status, (2) authenticated audio-failure recovery that retries or creates one compact fallback without duplicate playback, and (3) a final evidence/freshness gate that downgrades unverifiable consequential claims before speech or mutation. I also attempted a global forget-everywhere capability, but the recorder correctly rejected it as an existing backlog item rather than letting me restate it.

**Biggest unknown:** The implementation still lacks durable cross-surface joins: relay job IDs, Mac jobs, audio artifacts, evidence, and pendant ACKs are not one queryable identity. That prevents the three accepted capabilities from being fully trustworthy until the missing coordinator/index and job-lease pieces are built.

