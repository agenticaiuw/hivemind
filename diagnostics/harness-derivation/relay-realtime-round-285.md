# Harness derivation — relay-realtime — round 285

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Start this on my Mac, then keep it going even if I stop talking, and give me a short summary later."
- **useful because:** This is the whole promise: the pendant can initiate work, the Mac executes, and the relay closes the loop asynchronously.
- **path:** relay → mac-bridge → browser → pendant
- **model tier:** realtime to interpret intent; mac planner for execution; cheaper background watcher for status
- **latency:** Fast start (a few seconds). Completion can happen anytime; summary delivery should be prompt.
- **cost:** Moderate. Planning/execution dominates; status watching is cheap.
- **security:** High-impact actions (email, purchases, deletion) must require confirmation. Summaries should avoid exposing sensitive content to bystanders.
- **missing:** Implemented event delivery from relay to pendant/phone; A durable watch that survives voice-session end; A concise summary generator that runs server-side

### "“I’m on a phone call—stay with me, tell me who is speaking and what they just asked, and when I say ‘reply’, draft or send the response I dictate.”"
- **useful because:** The owner can conduct a difficult call without staring at the Mac: the pendant is the conversational front door, while the Mac/iPhone are the only surfaces that can actually carry and control the call. This would make the system useful in one of the highest-value moments for a wearable.
- **path:** pendant → relay → mac-planner → ios → mac-vision
- **model tier:** Realtime relay for low-latency turn-taking and short spoken summaries; mac-planner for call control and deterministic actions; a cheaper background model for rolling transcript compression and speaker/topic tracking.
- **latency:** Under 700 ms for a spoken ‘what did they ask?’ summary; under 2 s for a dictated draft; sending or changing call state must wait for the owner’s explicit verbal command, not an inferred intent.
- **cost:** Roughly $0.02–$0.10 per five-minute call, dominated by realtime audio transcription/summarization; call-control actions are negligible.
- **security:** Phone-call audio and transcripts leave the phone/Mac and pass through the relay; retention must be off by default and visibly indicated. The system must distinguish ‘draft’ from ‘send’, never claim a reply was sent without an iOS receipt, and require an explicit utterance for muting, hanging up, or sending.
- **missing:** A Mac audio bridge that can capture the remote call leg and return a mixed, consent-marked stream to the relay; A phone-mirroring call-control contract with call audio routing, speaker attribution, and receipts; A relay realtime session mode for a bounded rolling transcript plus pendant interruption; A pendant UX for entering and leaving call-copilot mode without ambiguity

### "“When I’m away from my Mac, let me ask what changed in my authenticated browser sessions since I last looked, and read me only the changes that require my attention.”"
- **useful because:** The owner currently cannot use the wearable to query a logged-in work site while the Mac is offline or unattended. A durable browser-session mirror would let the pendant answer high-value change questions without pretending that a stale page or a failed check is current.
- **path:** pendant → relay → browser → mac-planner
- **model tier:** Cheaper background extraction/diffing for watched pages; realtime relay only for the owner’s question and concise prioritization.
- **latency:** A spoken answer in 3–5 s when a fresh snapshot exists; otherwise state plainly that the session is unavailable rather than hallucinating. Initial session capture may take 10–30 s.
- **cost:** About $0.005–$0.03 per page check plus encrypted storage; cost is dominated by browser execution and change extraction, not speech.
- **security:** Authenticated cookies and page contents are highly sensitive. Use an end-to-end encrypted, device-bound session handoff or a Mac-local encrypted snapshot service; never expose cookies to the model, redact secrets before diffing, keep short retention, and report ‘could not check’ separately from ‘no changes’.
- **missing:** A browser-extension session mirror that can produce encrypted, redacted snapshots while the Mac is online; A relay-held encrypted snapshot/diff store and an offline query path; A durable browser watch that can resume from a Mac reconnect and bind results to the correct account/session; A pendant-readable alert/query protocol for prioritized diffs

### "“Remember the commitments I make in conversation, resolve them against my calendar, mail, browser and notes, and tell me before I miss one—without me having to say ‘remind me’.”"
- **useful because:** People routinely promise things without creating a reminder. The pendant is present at the moment of commitment, while the Mac and browser hold the evidence needed to resolve a person, deadline, thread, and completion state. This turns fleeting speech into reliable follow-through rather than another capture inbox.
- **path:** pendant → relay → mac-planner → browser → ios → dashboard
- **model tier:** Realtime relay extracts a candidate commitment in one pass; a cheaper background model resolves entities, checks evidence, and ranks urgency; realtime is used only when the owner asks for the current commitment list.
- **latency:** Acknowledge a detected commitment in under 1 s without interrupting the owner; reconciliation can take minutes. Notifications should arrive before a deadline, with quiet suppression when evidence shows it is already done.
- **cost:** Approximately $0.01–$0.05 per commitment over its lifetime, dominated by background reconciliation across mail/calendar/browser evidence.
- **security:** This processes private speech and personal/work records. Store only the commitment and minimal evidence pointers, allow correction/deletion, never infer a commitment from background audio after button release, and clearly label uncertain matches instead of asserting completion.
- **missing:** A commitment-specific entity and lifecycle model distinct from generic tasks; Cross-surface evidence joins for calendar, mail, browser and iOS with provenance and confidence; A scheduler/standing-watch policy that can recheck commitments and suppress duplicates; A reliable pendant notification path that carries a short spoken escalation and supports correction


## Changes it proposed to its own stack

### `integration` — Build a bounded phone-call copilot integration: iPhone Mirroring exposes the active call’s remote audio and call identity to a Mac-local mixer; the relay receives a consent-marked realtime stream, maintains a rolling transcript, and returns short Opus summaries to the pendant. Add explicit draft/send/hang-up commands with receipts and a hard session timeout.
- **owner gets:** The pendant could actually help during a live call instead of merely taking notes afterward, while the Mac and iPhone do the parts the pendant cannot physically do.
- effort: High: Mac audio capture/routing, iOS call-control and receipt plumbing, relay session state, and pendant mode UX.  ·  risk: Call audio could leak or be mixed incorrectly; recover by defaulting to no capture until the owner starts copilot, showing an active-mode indicator, dropping the stream on disconnect, and never sending without an explicit command plus receipt.
- cost: Moderate realtime transcription and synthesis cost per call; no new cloud browser cost. Likely 1–3 engineer-weeks for a safe prototype.  ·  latency: Adds one audio hop; target under 700 ms for short summaries and under 2 s for dictated drafts.
- security: High sensitivity: encrypt in transit, avoid transcript retention by default, isolate call audio from general memory, and bind commands to the active call session.
- depends on: A Mac-local call audio capture/mixer; A real iOS Mirroring call-control and receipt surface; Relay support for bounded rolling realtime sessions

### `memory` — Add a commitment lifecycle to the existing fact/graph store: extract only from an active pendant turn, record promise text, owner/other party, due-window, evidence pointers, confidence, and states (open, fulfilled, declined, expired). A background reconciler joins calendar, mail, browser and iOS evidence, while the existing routine/watch machinery produces one prioritized escalation and accepts spoken corrections.
- **owner gets:** Promises made casually become dependable follow-through without forcing the owner to remember the magic words ‘remind me’.
- effort: Medium-high: schema/lifecycle, extraction, cross-surface entity resolution, reconciliation rules, and notification suppression.  ·  risk: False commitments or premature ‘done’ claims would erode trust; recover by requiring confidence thresholds for alerts, retaining provenance, allowing ‘that wasn’t a commitment’ correction, and never treating absence of evidence as completion.
- cost: Low-to-moderate background model and storage cost; most checks can use cheap diffing and existing scheduled/watch execution.  ·  latency: No interruption to the live turn beyond a short extraction pass; reconciliation is asynchronous.
- security: Speech and personal records are joined. Keep minimal evidence pointers, scope facts to voice/mac/browser/ios, encrypt sensitive content, and honor deletion/expiry.
- depends on: Wire GET /memory/projection into the live conversation path; A commitment-specific graph schema and correction endpoint; Use the existing routines and watches for rechecks rather than inventing another scheduler


## What it asked for

_Nothing._
