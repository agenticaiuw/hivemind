# Harness derivation — relay-realtime — round 258

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Check my signed-in pages and summarize what needs attention."
- **useful because:** The browser holds sessions nobody else can reach; using it turns the pendant into a real assistant for authenticated workflows.
- **path:** relay → mac-bridge → browser → pendant
- **model tier:** cheaper planner tier for browsing and extraction; realtime only for conversational clarification
- **latency:** Start within a second; browsing may take several seconds. Summaries should be concise and interruptible.
- **cost:** Moderate. Browser automation and page reads dominate; summaries are cheap.
- **security:** Never exfiltrate full page content by default. Extract only relevant fields, and confirm before sending messages or making purchases.
- **missing:** A robust, typed browser extraction schema with safe defaults; Better evidence capsules for what was read and why it was relevant

### "Give me a one-sentence daily brief based on what changed."
- **useful because:** A tiny, reliable brief reduces cognitive load and makes the system feel like a daily companion without requiring constant interaction.
- **path:** relay → mac-bridge → browser → dashboard → pendant
- **model tier:** scheduled/background tier for gathering; realtime only for playback or quick follow-ups
- **latency:** Runs unattended; when invoked, response should be under a few seconds.
- **cost:** Moderate. Gathering from multiple sources dominates. Caching and change-detection reduce repeat cost.
- **security:** Respect destructive-action confirmation. Keep summaries short; link out to details.
- **missing:** A unified change-detection layer across data sources; A stable store for prior snapshots to diff against

### "“Find the best appointment or reservation that fits my calendar and constraints, use my authenticated browser session to hold or book it, and tell me exactly what you chose and why.”"
- **useful because:** Today the owner must manually reconcile calendar availability, authenticated sites, and tradeoffs. This would turn a spoken goal into a completed real-world booking while keeping the wearable as the decision surface and the browser as the authenticated hand.
- **path:** pendant → relay → mac-planner → browser-harness → dashboard
- **model tier:** relay-realtime for constraint extraction and concise questions; background mac-planner/browser agents for search and form completion; faculty-judgement for ranking options.
- **latency:** First useful options within 30–60 seconds; booking completion may take several minutes with asynchronous pendant updates.
- **cost:** Roughly $0.03–$0.15 per request; browser interactions and repeated page reads dominate, not the initial voice turn.
- **security:** Calendar details and authenticated booking pages leave the Mac/browser boundary and are summarized to the relay. Never fabricate availability or booking success; return the exact provider, time, price, and receipt URL. Require an explicit final spoken choice before an irreversible purchase even though ordinary reversible navigation needs no gate.
- **missing:** A constraint query that can read calendar availability and normalize preferences across Mac and authenticated browser pages; A resumable multi-agent booking state with provider receipts and a final-choice checkpoint; A browser-side mechanism for temporary holds and robust recovery when a provider changes the form

### "“Tell me whether the thing you just did actually changed the world; if it did, give me a spoken receipt, and if it did not, show me the exact next step without making me repeat the request.”"
- **useful because:** The owner currently receives action completion as a best-effort conversation and cannot reliably distinguish a submitted form, a saved draft, a failed attempt, or a stale page. A truth-oriented spoken receipt would make remote control trustworthy while away from the Mac.
- **path:** pendant → relay → mac-planner → mac-vision → browser-harness → dashboard
- **model tier:** Cheap background verifier compares pre/post evidence; relay-realtime only renders the short status sentence; faculty-perception validates the external state before faculty-action reports success.
- **latency:** Initial acknowledgement under 2 seconds; verified receipt within 10–30 seconds for local actions and up to 2 minutes for authenticated web actions.
- **cost:** About $0.01–$0.08 per action, dominated by a post-action readback or screenshot and occasional retry.
- **security:** Evidence may contain private page contents, messages, or file paths. Send only a redacted digest to the pendant and retain the full evidence capsule locally with bounded expiry. Never say “done” from an HTTP 200 or a queued job alone; distinguish queued, applied, partially applied, and unverifiable.
- **missing:** A cross-surface pre/post evidence schema that can compare browser, Mac, and API state; A relay response policy that refuses success language until verification evidence exists; A compact owner-facing receipt view with replayable source evidence and expiry

### "“Keep working on this with me even when I stop talking: ask one precise clarification on the pendant when you truly need it, remember my answer, and resume the same browser/Mac task without losing progress or repeating completed steps.”"
- **useful because:** Long tasks fail today at the exact moment a planner encounters an ambiguity: the owner has to restart the conversation and hope the agent remembers which forms and choices were already completed. A durable clarification rendezvous would make the wearable a real remote control for work that outlasts a voice turn.
- **path:** pendant → relay → mac-planner → mac-vision → browser-harness → dashboard
- **model tier:** Background mac-planner/browser agents execute and checkpoint; relay-realtime asks and speaks only the single necessary question; a cheaper state machine validates the answer against the pending plan.
- **latency:** Question surfaced as soon as blocked, normally under 5 seconds; resume within 10 seconds of the owner's answer, with longer browser work continuing asynchronously.
- **cost:** $0.02–$0.10 per resumed task, mostly planner context reconstruction and browser state inspection; much cheaper than restarting the whole task.
- **security:** The pending task state may contain private URLs, drafts, and form values. Encrypt and expire checkpoints, bind answers to the exact task and question nonce, and reject late or ambiguous answers rather than applying them to a different job.
- **missing:** A durable task checkpoint containing completed actions, current browser/Mac state, and the one unresolved question; A pendant-delivery protocol for question/answer packets that survives a dropped session; Planner resume semantics that are idempotent and verify already-completed side effects before continuing


## What it asked for

_Nothing._
