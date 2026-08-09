# Harness derivation — relay-realtime — round 238

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If I don’t finish a voice request, turn it into a reminder or a saved intent I can resume later."
- **useful because:** Stops context from evaporating when the owner gets interrupted. It’s a cross-surface memory that makes the system feel dependable.
- **path:** relay → mac-bridge → browser
- **model tier:** realtime for capture; mac planner for turning it into a reminder or task
- **latency:** Under a few seconds to confirm it’s saved.
- **cost:** Moderate; a small planning step plus saving dominates.
- **security:** Saved intents may contain sensitive info; store minimally and scope to relevant surfaces.
- **missing:** Wiring the memory projection into the live conversation context so we can retrieve these without resending bulky context; A small schema for resumable intents and a UI/voice flow to list them

### ""Handle this task all the way through, and only wake me if you hit a genuinely missing decision." The relay should let me delegate an ambiguous multi-step goal, have the Mac planner and browser work it, detect when a needed choice is truly unavoidable, ask one sharply scoped question on the pendant, then continue and report the result with evidence."
- **useful because:** Today delegation either ends at a plan or leaves the owner polling and re-explaining context. This would make the pendant a reliable front door for real work: the owner can walk away, answer only the one decision no agent can infer, and receive a truthful outcome rather than a vague 'done'.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Realtime only for the initial request and the one clarification; background orchestration and evidence summarization use a cheaper model.
- **latency:** Acknowledge in under 2 seconds; background steps may take minutes. Clarification delivery must survive an offline pendant and resume automatically after the answer.
- **cost:** Roughly $0.02-$0.15 per task depending on planner/browser turns; realtime cost is dominated by clarification and final spoken summary, not idle watching.
- **security:** The system must distinguish an unavailable fact from a preference it already knows, avoid asking for secrets aloud when a browser session can supply them, and include action receipts/evidence. Owner policy permits execution, but destructive or irreversible outcomes still need an explicit decision when the task itself is ambiguous.
- **missing:** A durable state machine for paused-on-question jobs with a typed clarification payload and answer correlation; Relay-to-pendant delivery of a clarification request, not just a completion alert; Planner/browser checkpoints that record what was tried and why it cannot proceed; A resume endpoint that feeds the answer back into the exact paused job

### ""Why are you saying that?" Give me a spoken, source-grounded explanation of any answer or action: which remembered preference, browser page, Mac state, and agent observation contributed, what was inferred, and what remains uncertain."
- **useful because:** A wearable assistant acts while the owner cannot see its screen. Without provenance, a wrong answer or surprising action is impossible to audit from the pendant. This would make the hive trustworthy: one short spoken explanation on demand, with a dashboard view for the full chain and direct links to the underlying evidence.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Realtime generates the short spoken explanation from a prebuilt trace; a cheaper background model can compress long traces and cluster recurring uncertainty.
- **latency:** Under 2 seconds for the spoken summary when the trace already exists; full trace inspection may load in under 5 seconds.
- **cost:** About $0.005-$0.03 per explanation. Storage and indexing of structured receipts dominate; model cost is small if raw pages and action results are not resent wholesale.
- **security:** Never speak secrets, tokens, private page contents, or full sensitive memory values by default. Store provenance with sensitivity labels and expose redacted source titles/fields first; require a deliberate request for sensitive detail. The trace must distinguish observed facts from model inferences and never manufacture citations.
- **missing:** A shared append-only provenance graph spanning relay turns, memory facts, Mac actions, browser commands, and their outputs; Stable evidence IDs and sensitivity/redaction metadata on every action receipt; A spoken 'explain this' resolver that can bind 'that' to the last answer/action; Dashboard and browser deep links to the relevant evidence

### ""Move this conversation to my Mac, keep the context, and show me the result there." Seamlessly hand a live pendant conversation to the Mac or authenticated browser when a visual surface is better, then let me return to the pendant without repeating myself."
- **useful because:** Speech is ideal while walking, but many tasks need a page, code, image, or a long result. Today the owner must choose a surface, repeat the request, and hope context survived. A true handoff would make the wearable and screens feel like one assistant rather than disconnected agents.
- **path:** pendant → relay → mac-planner → mac-vision → browser → dashboard
- **model tier:** Realtime handles the handoff utterance and continuity summary; the target surface uses its normal planner/vision model, with a cheaper model maintaining the compact shared state.
- **latency:** Acknowledge the handoff in under 1 second and expose the target session in under 5 seconds. Returning to voice should resume in one turn without replaying the whole transcript.
- **cost:** About $0.01-$0.08 per handoff, dominated by one compact context summary and any target-surface model call. Persistent session metadata is inexpensive.
- **security:** Only paired, currently authorized surfaces may receive a handoff. Redact sensitive voice context from dashboards and unrelated browser tabs; expire handoff tokens and make the target display visibly identify the active owner session. Never assume a nearby Mac is the owner's intended target if pairing is stale.
- **missing:** A first-class handoff object tying one voice session to a Mac/browser session, with lifecycle and expiry; Bidirectional session event transport rather than one-way job completion; Context compaction that preserves referents, pending decisions, and tool state without replaying sensitive audio; A pendant gesture/utterance to choose or cancel the target and a target-surface resume affordance


## What it asked for

_Nothing._
## Its own summary

Recorded three owner-facing capabilities: (1) delegated multi-step work that pauses only for an unavoidable decision and resumes from the exact checkpoint, (2) spoken provenance explaining which memory, browser, Mac observations, and inferences produced an answer or action, and (3) bidirectional handoff of a live pendant conversation to the Mac/browser and back without repeating context. The major missing pieces are durable paused-job/clarification state, a cross-surface provenance graph with redaction, and first-class session handoff/event transport.

**Biggest unknown:** Whether the observed workbench context and handoff routes are genuinely live implementations or only partial/undocumented routes; the recorder specifically flagged them for verification, but discovery was unavailable this round.

