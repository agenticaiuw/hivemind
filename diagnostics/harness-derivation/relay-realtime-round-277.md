# Harness derivation — relay-realtime — round 277

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Use the pendant as a direct controller when it’s plugged into my Mac."
- **useful because:** Right now the owner is often away from the Mac, but when they are physically connected over USB, we should take advantage of that reliable link for fast control, status, and debugging without LTE registration.
- **path:** pendant → mac-bridge → relay
- **model tier:** realtime for the conversational front door; mac planner for any multi-step Mac workflows
- **latency:** Interactive; should feel immediate when wired. Anything multi-step should be delegated to the Mac planner.
- **cost:** Mostly local; API cost is minimal. Main cost is development and maintaining a stable USB protocol.
- **security:** USB control is powerful. Restrict to reversible actions by default and clearly separate read-only status from mutations. Avoid exposing secrets from the Mac to the pendant.
- **missing:** A concrete, callable bridge work tool on the relay side (the grant mentions /v1/bridge/work permission, but no tool is wired for it); A defined set of USB commands and responses for status, audio, and control

### "While I’m speaking, detect if I’m asking for something that needs complex Mac workflow planning and hand it off cleanly, then summarize what’s happening without flooding me."
- **useful because:** This is the “single most useful” shape of the system: the pendant stays responsive and conversational, while the Mac does the heavy lifting. The owner gets a smooth handoff and clear status without babysitting.
- **path:** relay → mac-bridge → mac
- **model tier:** realtime for intent capture and conversational control; mac planner for multi-step execution; cheaper tier for status summaries if available
- **latency:** Immediate acknowledgment on the pendant; planning can take longer. Summaries should be brief and interruptible.
- **cost:** Low per turn at the relay; cost sits mostly in Mac planning and execution. Avoid re-sending large context blocks.
- **security:** Complex workflows can touch sensitive data (mail, files, credentials). Default to read-only previews when possible; require confirmation before sending or deleting.
- **missing:** A stable, enum-based routing tool or contract at the relay (current relay_route_intent is schema-only/unresolved); A consistent status receipt format the relay can read aloud without rewriting

### "While I am in a meeting, listen to the meeting audio on my Mac and tap me only when my name, a direct question, or an assigned action is detected; after the meeting, tell me the three commitments I made."
- **useful because:** The pendant can be worn away from the screen, and this turns it into a discreet attention filter rather than another meeting window. It combines Mac-local audio access with relay low-latency speech and the pendant's existing alert inbox; no single node can do the whole job.
- **path:** pendant → relay → mac-planner → dashboard
- **model tier:** Realtime relay model for name/question detection with a tiny streaming classifier on the Mac; cheaper background model for post-meeting commitment extraction and deduplication.
- **latency:** Under 2 seconds from a detected question to a pendant alert; post-meeting summary within 60 seconds of the meeting ending.
- **cost:** About $0.01-$0.05 per meeting hour for streaming detection plus $0.02-$0.10 for the final transcript pass, dominated by audio transcription. Mac-local VAD and keyword filtering should keep raw audio off the relay when irrelevant.
- **security:** Meeting audio is sensitive. Default to Mac-local capture, send only short candidate windows or transcript spans, visibly show an active-capture indicator, expire audio/transcript buffers after the summary, and never alert other meeting participants. The owner has maximum-access policy, but recording still needs an explicit start/stop gesture.
- **missing:** Mac meeting-audio capture and bounded streaming transcript route; Relay stream session with retention/expiry controls; Pendant alert-inbox payload type for urgent question versus post-meeting commitment; Meeting lifecycle detection or an explicit start/stop action

### "When I ask “what did I actually agree to with Alex?”, search my Mac mail/messages/calendar, authenticated browser pages, and prior pendant conversations, then answer with the exact evidence, dates, and any contradictions—not a guessed memory."
- **useful because:** People routinely need to recover commitments across surfaces that no individual agent can see. This would make the pendant a trustworthy memory probe: it distinguishes an explicit agreement from an inference and exposes the source instead of inventing continuity.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Cheap retrieval and date/entity normalization on the Mac and browser; relay-realtime only for the spoken clarification turn; a slower synthesis model ranks evidence and writes the concise answer.
- **latency:** Initial answer in 5 seconds for indexed sources, with a follow-up correction if a slower source is still being searched. Never block speech on a full historical crawl.
- **cost:** Roughly $0.01-$0.08 per query, mostly retrieval and synthesis tokens; incremental indexing can run locally without model cost.
- **security:** Search results may include sensitive messages. Keep raw evidence on the Mac/browser, send only minimal quoted spans and metadata to the relay, redact unrelated participants, and expire the assembled case after the answer unless the owner explicitly saves it.
- **missing:** A cross-surface evidence query that can search local mail/messages/calendar and authenticated browser state in one job; Stable source citations and contradiction records in job receipts; Conversation transcript indexing with explicit consent and retention controls; A relay response format that can speak a provisional answer while evidence continues

### "When I say “pack up,” capture a resumable work capsule from my Mac and browser—open documents, unsaved text, selected tab, active task, and my spoken next step—then when I later press the pendant and say “resume,” restore the right apps and tabs and read me the next step."
- **useful because:** This solves the real gap between wearing the pendant away from the desk and returning hours later: the owner does not have to reconstruct context from memory. It requires the Mac to observe unsaved UI state, the browser to expose authenticated tabs, the relay to retain a compact capsule, and the pendant to retrieve it.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** Local deterministic state capture and restore on Mac/browser; a cheaper background model compresses the capsule and extracts the next step. Relay-realtime only handles the spoken pack-up/resume exchange.
- **latency:** Pack-up acknowledgement under 3 seconds; resume restoration under 15 seconds, with a spoken summary available immediately while apps finish opening.
- **cost:** Under $0.02 per capsule for compression and summary; most cost is local state capture and storage, not inference.
- **security:** Capsules may contain private document text, authenticated URLs, and unsaved secrets. Encrypt at rest, keep full contents on the Mac when possible, store only hashes/labels in the relay, expire capsules after a configurable period, and never replay passwords or destructive form contents.
- **missing:** A versioned cross-surface capsule schema with local encrypted payload and relay metadata; Mac capture/restore actions for unsaved editor state and window layout; Browser export/restore of authenticated tab identity without copying cookies; A pendant command that selects and speaks a capsule while the Mac is offline or reconnecting


## What it asked for

_Nothing._
## Its own summary

Recorded three new owner-facing capabilities: private meeting commitment/question filtering, evidence-backed cross-surface agreement retrieval with citations and contradictions, and encrypted pack-up/resume work capsules spanning Mac, browser, relay, and pendant. Each names the missing cross-node pieces rather than pretending current routes are sufficient. A live interpreter idea was rejected as a duplicate and was not repeated.

**Biggest unknown:** Whether the existing backlog already contains a more specific implementation of cross-surface work capsules or agreement evidence retrieval; the recorder marked both recorded but flagged the capsule as close to an existing “pick this back up” idea.

