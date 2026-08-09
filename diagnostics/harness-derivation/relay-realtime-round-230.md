# Harness derivation — relay-realtime — round 230

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I ask you to do something on my Mac, give me a quick, low-latency “handoff receipt” that includes what you think you’re doing and a job reference I can ask about later."
- **useful because:** It builds trust and reduces confusion. The owner gets immediate confirmation that the request was understood, what system will handle it, and how to refer to it later via voice.
- **path:** relay-realtime → mac-planner → relay
- **model tier:** Realtime for the spoken receipt; lower-cost tiers for execution.
- **latency:** Receipt within a second; execution continues asynchronously.
- **cost:** Minimal. Mostly a small spoken message plus passing along a jobId.
- **security:** Avoid exposing sensitive details. The receipt should be generic and not include private content from documents or emails.
- **missing:** A structured, stable job reference returned to the relay at plan time and stored for voice lookup; A consistent receipt format that downstream agents populate

### "“For the next two hours, use my usual judgment: if a purchase is under $50 and matches my saved preferences, complete it; otherwise ask me on the pendant. Keep doing that even if I walk away from my Mac.”"
- **useful because:** The owner can grant a narrowly scoped, time-limited delegation once by voice instead of repeatedly approving routine work. The relay remains reachable while the Mac and authenticated browser do the actual work, and exceptions come back as one short spoken question.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Realtime model parses the spoken policy and asks at most one clarification; background mac-planner evaluates each candidate, while browser-extension performs authenticated checkout. Use a cheaper background model for matching and exception ranking.
- **latency:** Immediate acknowledgement in under 2 seconds; routine evaluation under 30 seconds; exception question delivered asynchronously when the owner is away.
- **cost:** Roughly $0.01–$0.05 per routine candidate plus browser/Mac execution; realtime cost is limited to policy creation and exceptions. Dominant cost is background reasoning over candidate items.
- **security:** A voice-granted policy must be scoped by action, amount, merchant/category, duration, and target account, with an immutable audit trail and an easy spoken revoke. Payment, identity, and final checkout data remain on the authenticated browser; relay receives only the minimum candidate and result metadata. A policy must never silently broaden itself.
- **missing:** A first-class expiring delegation/policy object accepted from voice; Policy evaluation hooks in mac-planner and browser-extension before an action; A pendant delivery path for exception questions that survives an ended session; Dashboard UI showing active policies, scope, expiry, and revocation

### "“Before you act on this, check my Mac files, calendar, and the logged-in web page; if they disagree, tell me exactly what conflicts and which source you trust. Otherwise just do it and give me the evidence.”"
- **useful because:** Today each substrate can report its own view, but the owner cannot ask the hive to establish one defensible truth before changing the world. This prevents stale browser state, an old local file, or a calendar conflict from quietly producing the wrong action, while keeping the normal case fast.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Faculty-perception/background model gathers and normalizes evidence; faculty-judgement compares freshness, authority, and contradictions; relay-realtime only speaks the result or one focused conflict question. Use the cheaper model for extraction and reserve realtime for the owner-facing turn.
- **latency:** A simple agreement in 5–10 seconds; a conflict report in under 20 seconds; long investigations become a tracked job with an asynchronous pendant alert.
- **cost:** About $0.03–$0.12 per investigation, dominated by multi-source extraction and screenshots/page reads; no extra realtime call when sources agree.
- **security:** Evidence capsules must preserve source URL/path, capture time, and redaction boundaries without copying secrets into the relay transcript. The system must distinguish “not checked” from “checked and absent,” and must never resolve a conflict by guessing. Any mutation still records the exact evidence set used.
- **missing:** A cross-surface evidence joiner with freshness/authority rules; A contradiction report schema that links claims to Mac and browser receipts; A planner mode that pauses mutation until perception returns agreement or an explicit owner choice; A compact spoken conflict renderer and dashboard evidence diff

### "“Finish that web task even if it hits a login challenge or a form only I can answer. Tell me on the pendant exactly what you need, let me answer or press the button, then continue without making me start over.”"
- **useful because:** Authenticated browser tasks currently fail at the precise moment they need the owner, especially when the owner is away from the Mac. This turns the pendant into a secure interruption channel: the browser pauses, the relay asks a narrowly scoped question, and the same job resumes at its exact step instead of abandoning the workflow.
- **path:** pendant → relay → browser-extension → mac-planner → dashboard
- **model tier:** Browser-extension detects challenge states and emits a structured pause; mac-planner preserves the action plan; relay-realtime renders the one question and parses the short answer. Use a background model to validate the answer against the form and resume, with no screenshot sent to the realtime model unless needed.
- **latency:** Challenge notification within 3 seconds of detection; answer acknowledged immediately; resume within 10 seconds after the owner responds. Keep the job paused for a configurable expiry rather than polling aggressively.
- **cost:** About $0.01–$0.08 per interruption, mostly browser inspection and answer validation; ordinary tasks incur no model cost until a challenge is detected.
- **security:** Never read or repeat passwords, full payment numbers, or one-time codes into durable memory. Classify challenge fields, redact them from logs, bind the response to the paused job and browser tab, and expire it after one use. The owner must be able to cancel from the pendant; dashboard shows every pause and continuation.
- **missing:** Browser challenge detection for login, CAPTCHA, confirmation, and owner-only questions; A resumable browser job checkpoint containing tab identity, action cursor, and redacted form state; A secure one-shot answer channel from pendant to the paused browser job; Relay event delivery wired to the existing pendant inbox with challenge-specific expiry; Mac/browser recovery when a tab navigates or the session expires while paused


## What it asked for

_Nothing._
## Its own summary

Recorded three new owner-facing capabilities: expiring voice-granted delegation across Mac/browser, cross-surface contradiction checking before actions, and resumable authenticated browser tasks that interrupt the owner on the pendant only for a one-shot answer. Each requires new coordination between existing planner, browser, job, receipt, and pendant-event surfaces; none is available end-to-end today.

**Biggest unknown:** Whether the existing browser command/job state can be safely checkpointed at a form-level action cursor without leaking credentials or allowing a stale tab to resume against the wrong page.

