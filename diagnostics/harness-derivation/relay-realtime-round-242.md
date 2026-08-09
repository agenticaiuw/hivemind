# Harness derivation — relay-realtime — round 242

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“I’m in a meeting and missed that last point—tell me the key thing they just said, and draft a reply I can approve by voice.”"
- **useful because:** The owner can recover from a missed spoken moment without opening a laptop or making the meeting stop. It combines the worn microphone, the authenticated meeting/browser surface, and the Mac’s drafting ability in a way no one node can provide.
- **path:** pendant → relay → browser → mac-planner → mac-vision
- **model tier:** Realtime handles the short spoken request and confirmation; a cheaper background model extracts the latest caption/transcript window and drafts the reply. Use the expensive tier only for ambiguity and the final concise answer.
- **latency:** Initial acknowledgement under 500 ms; caption retrieval and summary in 3–8 seconds; draft in under 15 seconds. If captions are unavailable, say so rather than pretending to have heard the meeting.
- **cost:** About $0.01–$0.06 per use, dominated by transcript/caption extraction and draft generation; near-zero when the browser already exposes a small recent caption window.
- **security:** Meeting text and the proposed reply leave the browser/Mac only to the relay/model. Require an explicit spoken confirmation before sending anything; never infer permission to send from a request to draft. Mask unrelated participant text and retain the transcript slice only ephemerally.
- **missing:** A browser-extension action that exposes the most recent caption/transcript segment from the active meeting tab with timestamps; A relay session binding that keeps the request associated with the active meeting tab; A voice confirmation path that can return a drafted reply to the browser without sending it

### "“Find the thing I was looking at yesterday about the pendant, tell me which tab or file it was, and put me back exactly there.”"
- **useful because:** The owner gets continuity across a fragmented day: the pendant supplies the vague natural-language clue while the Mac and browser search their distinct histories and reopen the exact source. This is more useful than a generic web search because it recovers the owner’s own prior context.
- **path:** pendant → relay → mac-planner → browser-extension → mac-terminal
- **model tier:** Use a cheap background retrieval/ranking model over browser history, open tabs, recent files, and scoped memory; realtime only resolves the owner’s short clarification and speaks the winning provenance.
- **latency:** Acknowledge immediately, rank candidates within 5 seconds, and reopen the selected source within 10 seconds. If there are multiple plausible matches, speak at most three discriminating choices.
- **cost:** Roughly $0.01–$0.04 per invocation, dominated by embedding/ranking or summarizing candidate metadata; document contents should not be sent unless needed.
- **security:** Search only the owner’s local browser and Mac metadata by default; do not upload full file contents or private page bodies to the model. Report provenance (app, title, timestamp, URL/path) so the owner can detect a wrong match. Opening a source is reversible; do not edit it.
- **missing:** A unified, read-only recent-context index joining Safari/browser history, open tabs, and Mac recent documents; A local Mac action for opening a ranked provenance result by stable ID rather than by guessed title; A relay-side short-lived candidate cache so a follow-up like “the second one” is unambiguous

### "“I’m away from my Mac. Turn this spoken idea into a working experiment: create the project note, run the smallest safe test, and tell me what happened when it’s actually done.”"
- **useful because:** This is the system’s highest-value end-to-end promise: a thought captured while worn becomes a verifiable artifact and execution result without the owner sitting at the computer. The relay handles ambiguity, the Mac edits and runs, and the pendant delivers a truthful completion or failure later.
- **path:** pendant → relay → mac-planner → mac-terminal → mac-vision → dashboard
- **model tier:** Realtime converts speech into a compact goal and asks only essential clarifying questions. mac-planner performs the multi-step plan; a cheaper verifier checks receipts, test output, and changed files. Realtime returns only the final short spoken status.
- **latency:** Capture and acknowledgement under 1 second; planning under 10 seconds; execution may take minutes. Completion must be pushed asynchronously and remain available if the pendant is temporarily offline.
- **cost:** Approximately $0.05–$0.30 per experiment, dominated by planner/verifier turns and any long command output; token cost is reduced by passing structured receipts and diffs instead of full transcripts.
- **security:** The owner has granted broad access, but the system must still be truthful: distinguish queued, running, passed, failed, and not-run. Include command/file receipts and a compact diff in the dashboard. Never claim completion from a planner response alone; destructive or externally visible steps should be surfaced for the owner’s explicit approval.
- **missing:** A durable experiment job record containing goal, plan, commands, outputs, changed paths, and verification state; A planner-to-relay completion callback wired to the existing pendant inbox/event delivery, including offline retention; A verifier that can rerun or inspect tests independently and mark a job failed when the claimed artifact is absent; A Mac-local workspace lease so unattended jobs do not interfere with active work


## Changes it proposed to its own stack

### `browser-harness` — Add a meeting-context capture primitive to the browser extension: for the active tab only, expose a bounded rolling window of visible captions/transcript lines with speaker labels and monotonic timestamps, plus a tab/session identifier. The relay can request that window, but the extension must never silently capture microphone or hidden-tab content.
- **owner gets:** When the owner misses a sentence while wearing the pendant, the system can answer from the meeting’s actual visible words and draft a response instead of guessing or requiring them to rewind manually.
- effort: Medium: extension content-script adapters for supported meeting UIs, a normalized caption schema, relay endpoint, and tests against DOM changes and caption absence.  ·  risk: Meeting sites can change their DOM or captions can be incomplete; return an explicit unavailable result. Limit the window and active-tab scope, and recover by asking the owner to repeat or open the transcript. Do not send or post a reply automatically.
- cost: Low per request; only a small caption window is transferred. Engineering cost is the adapter maintenance across meeting sites.  ·  latency: Caption retrieval should add under 1 second; normalization is local to the extension.
- security: Improves privacy over full-tab capture by limiting data to visible captions and a bounded time window. Still treat meeting text as sensitive and avoid durable storage by default.
- depends on: A relay endpoint that can associate a request with the active browser session; The meeting-companion capability’s draft-only confirmation flow


## What it asked for

_Nothing._
