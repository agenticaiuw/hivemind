# Harness derivation — mac-planner — round 273

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac accessibility and browser state** — AI Pendant Agent currently has Accessibility and Screen Recording, synthesized input is verified reaching the host, Safari is foreground, and four durable browser sessions exist; the active tab is USPS Tracking for tracking number 9200190323035201509394.
  - evidence: mac_readonly_inspect(operation=running_apps) resolved GET /observe at 2026-08-09T01:46:55.939Z and returned accessibility.trusted=true, eventsPost=true, screenRecording=true, foregroundApp=Safari, browser.sessions=4.

## Capabilities it proposed

### "“I’m stuck—look at what’s open on my Mac and tell me the next concrete step, or do it if it’s safe.”"
- **useful because:** The owner gets an actual rescue loop instead of a generic answer: the pendant supplies the urgent request, the relay coordinates, and the Mac/browser inspect the real foreground state and carry out a bounded fix. This is the single most useful cross-node behavior because it turns confusion at any app or web page into progress without requiring the owner to describe the screen.
- **path:** pendant → relay → mac-vision → browser → mac-planner
- **model tier:** Realtime only for the short spoken diagnosis; use a cheaper background planner for multi-step research or file work.
- **latency:** Under 3 seconds to inspect foreground app/browser and speak the first step; under 30 seconds for a safe bounded action.
- **cost:** About $0.01–$0.05 per rescue, dominated by one vision/context inference; action execution and inspection are local.
- **security:** Screen/UI state and the active URL leave the Mac to the relay/model. Never submit, send, purchase, delete, or navigate away without the owner's separately configured policy; redact passwords and secure-input fields. Existing FULL_CONTROL_MODE means the policy seam must be explicit before unattended mutations.
- **missing:** A stable semantic Mac/UI context payload with window title, focused control, selected text, and redacted screenshot metadata; A rescue planner that classifies the suggested fix as read-only, reversible, or high-impact and records a receipt; A pendant command/result event linking the spoken request to the Mac job

### "“Watch this page until the condition I name is true, then tell me on the pendant and stop watching.”"
- **useful because:** The owner can turn any currently logged-in Safari page—delivery tracking, a ticket queue, a price, a reservation slot—into a temporary personal sensor without leaving a permanent automation running. The browser holds the session, the relay polls and evaluates changes, and the pendant gives the result even when the Mac is not foreground.
- **path:** pendant → relay → browser → mac-planner
- **model tier:** Use a cheap background model or deterministic selectors for repeated page checks; reserve realtime for the final spoken alert or ambiguous condition interpretation.
- **latency:** Initial setup under 5 seconds; polling every 1–15 minutes depending on site; alert delivery under 5 seconds after detection.
- **cost:** Roughly $0.001–$0.02 per check if DOM/selector based; occasional model interpretation dominates when the condition is natural language.
- **security:** Authenticated page contents and URLs are read from the browser session and sent to the relay; store only a redacted diff and expire the watcher by default. Never perform purchases, submissions, or account changes. Require explicit confirmation for watchers involving sensitive health, finance, or private communications.
- **missing:** A durable watcher record with expiry, cadence, condition, last observation hash, and deduplication key; A browser page-watch/read-diff route that preserves the authenticated session without scraping credentials; A relay-to-pendant alert path that includes watcher identity and a stop acknowledgement

### "“Stop whatever computer task is running, save exactly where it got to, and tell me what can be resumed.”"
- **useful because:** A physical or spoken interruption becomes safe control rather than a half-finished mystery. The relay stops issuing actions, the Mac records completed and in-flight steps, browser sessions remain intact, and the pendant speaks a concise checkpoint. The owner can resume later without repeating a form, file move, or research step.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Use deterministic job cancellation/checkpointing; use a cheap model only to summarize the checkpoint. No realtime reasoning is needed unless the owner asks what to do next.
- **latency:** Acknowledge the stop in under 1 second; checkpoint in under 5 seconds; resume can take normal task time.
- **cost:** Near-zero model cost for cancellation and receipts; $0.005–$0.03 for optional checkpoint summarization.
- **security:** Stopping must be idempotent and must not undo already-committed external effects. The checkpoint may contain URLs, filenames, and snippets, so redact secrets and expire it. Resume must show the exact remaining actions and honor the owner's destructive-action policy.
- **missing:** A cooperative cancellation signal from relay to POST /execute and browser jobs; An atomic checkpoint format recording completed, in-flight, and not-started steps plus external side effects; A pendant stop event and resumable receipt surfaced through the existing job handoff

### "“Make the computer reach this exact state, and don’t tell me it’s done until you can prove the screen and browser actually match.”"
- **useful because:** Today an action receipt can mean that clicks were issued, not that the intended result appeared. The owner should get closed-loop execution: the pendant states the goal, Mac/browser act, an independent verifier checks the resulting UI/DOM and relevant file state, and the pendant reports either proof or the precise mismatch. This is especially valuable for forms, settings, navigation, and multi-step browser workflows where a click can silently fail or land on the wrong account.
- **path:** pendant → relay → mac-planner → mac-vision → browser → dashboard
- **model tier:** Use deterministic assertions and DOM/accessibility queries first; use a cheaper vision model only for visual assertions that lack structured state. Realtime is needed only for the brief final spoken result.
- **latency:** Initial action under 10 seconds for a short workflow; verification under 3 seconds after each checkpoint; speak immediately on proof or mismatch.
- **cost:** Usually <$0.01 because most verification is local structured state; $0.01–$0.05 when screenshot interpretation is required.
- **security:** Verification may see sensitive page contents and must redact credentials, tokens, and private message bodies. Never treat visual similarity as permission to send, purchase, delete, or submit. For high-impact outcomes, report proof and still require the owner's configured confirmation. Store assertion results rather than full screenshots by default.
- **missing:** A typed goal/assertion format covering URL, app/window identity, visible text, control state, DOM selectors, and file hashes; A postcondition verifier that runs after each action and distinguishes action-issued from outcome-proven; A receipt schema carrying the evidence source, timestamp, redaction status, and exact mismatch when verification fails

### "“Save a private, verifiable record of what happened in this web task so I can prove it later without saving the whole page.”"
- **useful because:** For deliveries, support cases, applications, and account changes, the owner needs more than 'done'. The browser and Mac would produce a compact evidence capsule—timestamp, site identity, relevant redacted fields, before/after assertions, and action receipt—while the pendant confirms that it was sealed. It preserves useful proof without retaining an entire sensitive page or recording audio.
- **path:** pendant → relay → browser → mac-planner → dashboard
- **model tier:** Deterministic extraction and hashing by default; use a cheap model only to select relevant fields from an ambiguous page. Realtime is unnecessary except for the short spoken acknowledgement.
- **latency:** Seal within 5 seconds of task completion; retrieve or summarize later in under 3 seconds.
- **cost:** Usually <$0.005 per capsule; model extraction, when needed, adds roughly $0.01.
- **security:** Evidence can contain addresses, order numbers, account names, and URLs. Redact secrets by field-class, encrypt at rest, keep a short owner-selected retention period, and make export explicit. Do not claim legal evidentiary status; report exactly what was captured and what was omitted.
- **missing:** A redacted evidence-capsule format with field-level provenance and cryptographic hashes; Browser and Mac hooks that capture before/after structured state without retaining full screenshots by default; A retention/export/delete surface and pendant acknowledgement event

### "“Teach the system this workflow once, then let me invoke the intention later even if the website or app layout changes.”"
- **useful because:** The owner should be able to demonstrate a task once—using the pendant to name the intention while Mac/browser observe the actual controls—and later say the intention instead of repeating brittle click instructions. The system would store semantic targets and postconditions, not coordinates, re-plan when the UI drifts, and report exactly where the learned routine no longer matches.
- **path:** pendant → relay → mac-planner → mac-vision → browser → dashboard
- **model tier:** Use a cheaper background model to distill demonstrations into a semantic routine; use realtime only when the owner invokes it and needs immediate confirmation.
- **latency:** Teaching takes under 2 minutes; invocation should begin within 3 seconds and pause at the first ambiguous or high-impact step.
- **cost:** About $0.02–$0.10 to distill a demonstration; later runs are mostly local planning with occasional model calls.
- **security:** Demonstrations may expose private pages and credentials. Store only abstract targets, redacted examples, and necessary selectors; never persist passwords or raw keystrokes. The owner must be able to inspect, disable, and delete each routine. Mutation policy remains explicit rather than inherited from the current FULL_CONTROL_MODE bypass.
- **missing:** A semantic routine schema containing intent, preconditions, action slots, postconditions, UI fallbacks, and version history; A demonstration recorder that excludes secrets and distinguishes owner input from agent input; A drift resolver that pauses rather than guessing when multiple controls could satisfy the intent


## What it asked for

_Nothing._
