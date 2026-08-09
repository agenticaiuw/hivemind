# Harness derivation — relay-realtime — round 164

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Remember this moment and follow up when you see something relevant on my Mac or in my browser."
- **useful because:** This turns the pendant into a hands-free, context-aware assistant: you can bookmark a moment while away from the Mac, and later the Mac/browser side notices a relevant change and nudges you with a short spoken update. It’s the kind of multi-surface loop a single device cannot do alone.
- **path:** pendant → relay → mac-bridge → browser
- **model tier:** Realtime only to capture the moment quickly; a cheaper Mac/browser model watches and matches later.
- **latency:** Under a second to capture the bookmark; follow-ups can arrive minutes or hours later.
- **cost:** Low per bookmark; matching cost depends on watch scope, dominated by browser/Mac inspection and summarization.
- **security:** Bookmarks are sensitive context. They should be stored encrypted, scoped to the owner, and include minimal content. Follow-ups must quote only what’s necessary. Provide a clear way to delete bookmarks.
- **missing:** A relay-visible event schema for signed pendant events with nonce and monotonic timestamp; A durable watch/match service on the Mac/browser side; A delivery path for async spoken notifications (currently unresolved relay_event_push)

### "If my request is running, keep an ear on it and tell me when it’s done, even after I stop talking."
- **useful because:** This is a single most useful behavior: you can ask for a task, go about your day, and get a spoken completion cue without polling. It’s the missing glue between voice, Mac actions, and delivery to the wearable.
- **path:** relay → mac-bridge → pendant
- **model tier:** Realtime to confirm the job is queued; a cheaper worker/Mac tier monitors and summarizes completion.
- **latency:** Seconds to acknowledge; completion can be delivered whenever it happens.
- **cost:** Low per job to monitor; costs come from periodic job status checks and generating a short spoken summary.
- **security:** Notifications can leak sensitive task names. Use redaction and allow the owner to opt out per task. Ensure only the owner’s devices receive the message.
- **missing:** A working async notification channel to the pendant (relay_event_push is unresolved); A durable monitor that can run without an open voice session (no scheduler/worker wired today); A compact, signed notification format suitable for the existing inbox/alert mechanism if audio cannot be stored routinely

### "Read the screen for me and answer questions, but only when the Mac says it has a relevant view and the browser session is available."
- **useful because:** A wearable can ask for visual context that it cannot see. The Mac can, but only when it’s online and the session is ready. This capability coordinates those constraints so the owner gets a correct answer instead of a guess.
- **path:** pendant → relay → mac-vision → browser
- **model tier:** Realtime for the conversation; mac-vision for the actual reading and answering.
- **latency:** Realtime response under a second when available; otherwise a quick fallback message and optional deferred answer.
- **cost:** Cheap when unavailable; moderate when mac-vision and browser inspection are active.
- **security:** Screen content is sensitive. Keep answers minimal, don’t retain screenshots longer than necessary, and never exfiltrate secrets to third-party services.
- **missing:** A relay inventory endpoint so this surface can verify its own routes/tools without blind probing; A reliable way to know mac-vision availability before delegating; A deferred delivery mechanism if the answer is ready later (async notifications are unresolved)

### "“Is the thing I asked for actually done?” — reconcile the live truth across my pendant, Mac job receipts, open browser tabs, and project files, and tell me what is confirmed, what is stale, and what disagrees."
- **useful because:** Today each surface can report its own partial state, so the owner can hear a confident but wrong completion answer. A single answer that distinguishes relay acknowledgement, Mac execution, browser state, and resulting artifact would be the system’s most useful trust feature: it prevents acting on a completion claim when only a plan was queued or a tab changed but the file did not.
- **path:** pendant → relay → mac-planner → mac-terminal → mac-vision → browser-extension → dashboard
- **model tier:** Realtime relay for the short spoken synthesis; faculty-perception for source reconciliation; mac-planner/mac-terminal for filesystem and job receipts; mac-vision/browser-extension for UI state; cheaper background model for longer discrepancy explanations.
- **latency:** Speak an initial confirmed/pending/disagreement summary within 2 seconds; gather deeper evidence asynchronously and push a correction if the answer changes.
- **cost:** Roughly $0.02–$0.10 per query depending on whether vision and a second model are needed; latency and cost are dominated by Mac/browser round trips, not the spoken synthesis.
- **security:** Authenticated browser content and local files leave their respective devices only as narrowly scoped evidence, with source labels and timestamps. Never claim success from a plan record alone; redact secrets and require explicit owner-visible provenance for sensitive sources.
- **missing:** A cross-node evidence envelope with source, observation time, freshness, and confidence; A reconciliation coordinator that can query Mac, browser, relay jobs, and pendant acknowledgements in one request; A typed final-state schema distinguishing planned, dispatched, executed, observed, and verified; A push path for a later correction when an initially pending source becomes verified

### "“Turn what just happened into a bug report.” Capture my spoken symptom on the pendant, reproduce it in the authenticated browser, inspect the Mac’s relevant logs and project state, and return a concise report with exact repro steps, evidence, and the smallest likely fix."
- **useful because:** The owner currently has to be the integration layer: remember the symptom, find the right tab, reproduce it, collect logs, and explain the mismatch. This would turn a vague wearable utterance into an actionable, evidence-backed report without requiring the owner to sit at the Mac.
- **path:** pendant → relay → mac-planner → mac-terminal → mac-vision → browser-extension → dashboard
- **model tier:** Realtime relay captures and confirms the short symptom; a cheaper background planner coordinates reproduction and evidence collection; mac-terminal gathers scoped logs, mac-vision handles non-DOM UI failures, and browser-extension reproduces authenticated flows.
- **latency:** Acknowledge in under 1 second and speak a preliminary diagnosis in 5 seconds; allow up to 60 seconds for a full reproduction and report, with a push notification when complete.
- **cost:** About $0.05–$0.30 per incident, dominated by computer-use/vision retries and log summarization; most successful cases should use the cheaper planner rather than realtime.
- **security:** Only the named project, tab, and time window should be collected. Authenticated page content and logs remain scoped to the incident, secrets and tokens are redacted, and no issue is submitted externally without an explicit owner request.
- **missing:** An incident-session object tying pendant audio, browser actions, Mac commands, screenshots, and timestamps together; A safe scoped log collector and browser reproduction mode; Evidence redaction plus stable citations into the report; A background coordinator and asynchronous completion delivery

### "“What changed on my screen since I last looked?” Compare the current Mac/browser view with the last owner-marked view, ignore cosmetic movement, and speak only the meaningful changes and any action they imply."
- **useful because:** A wearable owner cannot continuously inspect a Mac. A change-focused answer is much more useful than reading the whole screen: it can tell them that a build failed, a download finished, a form gained an error, or a page changed while preserving attention and avoiding a long spoken dump.
- **path:** pendant → relay → mac-vision → mac-planner → browser-extension → dashboard
- **model tier:** Realtime relay handles the short question and speech; a low-cost vision/diff worker computes perceptual and semantic deltas; mac-vision interprets pixels while browser-extension supplies DOM/accessibility changes and mac-planner maps changes to project context.
- **latency:** Return a first spoken delta within 3 seconds and a richer explanation within 10 seconds; no periodic capture is required—the owner explicitly marks a baseline and asks for comparison.
- **cost:** Approximately $0.01–$0.08 per comparison, with the cost dominated by one or two screenshot/DOM analyses; baseline metadata is cheap and can remain on the Mac.
- **security:** Screenshots and DOM text may contain private or authenticated data, so retain baseline and diff locally where possible, transmit only cropped changed regions and extracted text, and expire baselines automatically. Never infer that an unchanged screenshot means an unchanged underlying task.
- **missing:** A pendant gesture/voice operation to mark a named visual baseline; Mac-local encrypted baseline storage and perceptual/semantic diffing; A browser DOM/accessibility snapshot paired with each screenshot; A change classifier that separates cosmetic motion from actionable state; A relay response format with cited regions and timestamps

### "“Use my work account for this, not personal.” Route a request to the correct authenticated browser identity, Mac workspace, and project context, and tell me which identity was actually used after the action."
- **useful because:** A wearable voice command often omits account and workspace details, while the browser may hold multiple authenticated identities. The dangerous failure is not inability to act but silently acting in the wrong account. This capability makes account choice an explicit, inspectable part of cross-node execution without forcing the owner through a confirmation dialog for every reversible action.
- **path:** pendant → relay → browser-extension → mac-planner → mac-terminal → dashboard
- **model tier:** Realtime relay extracts the requested identity and keeps the spoken exchange short; a cheaper planner resolves account/workspace evidence from browser sessions and Mac context; browser-extension performs the identity-bound action and returns a signed receipt.
- **latency:** State the selected identity and workspace in under 2 seconds, then complete ordinary actions within the existing browser/Mac action latency.
- **cost:** About $0.01–$0.06 per request; most cost is a browser session inspection and occasional planner call.
- **security:** Never transmit passwords or cookies to the relay. The browser harness should expose only non-secret account labels, origin, profile, and session freshness. If the requested identity cannot be proven, report that plainly rather than guessing; preserve an immutable receipt of origin/profile/action/result.
- **missing:** A browser session identity inventory exposing safe labels without credentials; A Mac workspace/project identity inventory; Cross-node identity binding and freshness rules; Action receipts that include origin, browser profile, Mac workspace, and actor identity; A voice disambiguation path only when two identities are genuinely indistinguishable


## What it asked for

_Nothing._
## Its own summary

Recorded four owner-facing capabilities: cross-node truth reconciliation, spoken-to-evidence bug reports, visual change narration, and identity-bound browser/Mac execution. The common missing piece is not another action route; it is a cross-node evidence/context layer that correlates pendant utterances, browser identity and state, Mac workspace/logs, execution receipts, timestamps, and later corrections. It needs scoped redaction, freshness/confidence semantics, and an asynchronous coordinator. Existing routes can supply most raw observations, but none currently produces that unified, trustworthy evidence envelope.

**Biggest unknown:** Whether the current browser and Mac surfaces expose enough safe account/workspace labels and stable timestamps to bind evidence without sending credentials or private full-page content to the relay.

