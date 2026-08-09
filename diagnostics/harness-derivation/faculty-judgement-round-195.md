# Harness derivation — faculty-judgement — round 195

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“I got interrupted—continue the briefing exactly where I stopped, and tell me what I actually heard.”"
- **useful because:** A spoken briefing should behave like a durable handoff, not a fire-and-forget audio file. After a dropped LTE session, reboot, or owner interruption, the system can distinguish downloaded, started, finished, and merely queued items, resume at the next unheard item, and avoid repeating content the owner already heard.
- **path:** relay → pendant → mac-planner → dashboard
- **model tier:** Background/cheap model for reconciliation and a short catch-up sentence; realtime only for the live continuation request.
- **latency:** Under 2 seconds to report the resume point; no model call if signed delivery receipts and item metadata are sufficient.
- **cost:** Usually under $0.01, dominated by optional short TTS regeneration; zero model cost for a receipt-only answer.
- **security:** Use opaque artifact and item IDs, not transcript text, in pendant ACKs. Resume only items authorized for this owner/session, and show provenance when an item was skipped or expired. Never claim heard based on downloaded alone.
- **missing:** A durable briefing manifest that maps item IDs to source and playback ranges; A server-side reducer that joins record_pendant_delivery_event events to that manifest and handles out-of-order offline replay; An idempotent resume endpoint that can create a new audio artifact for only the unheard suffix

### "“When the pendant audio glitches, tell me in plain English whether the fault was the radio, codec, bridge, or speaker path, and leave me a reviewable bug report.”"
- **useful because:** The owner currently experiences a symptom (“it clicked” or “nothing played”) but cannot know whether retrying will help. A causal diagnosis tied to UART evidence turns an intermittent wearable failure into an actionable answer and a reproducible issue draft without silently contacting anyone.
- **path:** pendant → relay → mac-planner → dashboard
- **model tier:** Cheap background classifier for structured diagnostic records; realtime model only to phrase the short spoken verdict.
- **latency:** A local diagnostic summary in under 1 second after a session; a richer draft under 10 seconds.
- **cost:** Typically <$0.01 per incident; model cost is only for wording, while parsing and thresholds are deterministic.
- **security:** Keep raw UART and audio metrics local by default; send only selected counters and hashes in a draft. Never include microphone PCM, transcripts, credentials, or network tokens. Filing/submitting an issue always requires owner confirmation.
- **missing:** A typed UART-log ingestion route with cursor and authenticated device-session validation; Correlation of UART records with pipeline IDs, artifact IDs, and pendant delivery ACKs; A review UI that shows the evidence chain and supports explicit export/submit after the local draft exists

### "“Only interrupt me when a browser task truly needs my login; say which site and what I need to do, then let me approve the handoff without ever reading my password.”"
- **useful because:** Long-running delegated work currently either stalls invisibly at an authentication wall or risks asking for far too much page detail. A privacy-preserving login gate lets the browser retain the credential and gives the owner a precise, bounded moment to take over, then resumes the task after the authenticated session is available.
- **path:** browser-extension → mac-planner → relay → pendant → dashboard
- **model tier:** Cheap deterministic classifier for login-need signals and site-origin history; realtime model only for the owner's spoken explanation or ambiguous takeover request.
- **latency:** Detect on the next browser poll (up to roughly 30 seconds); spoken prompt under 1 second once classified. No model call for known origin verdicts.
- **cost:** Near-zero for known origins; <$0.01 for an ambiguous page classification, dominated by one browser inspection.
- **security:** The pendant receives only origin, task label, and an expiring opaque continuation token—never DOM fields, cookies, password text, or screenshots. The extension performs login locally. Require physical approval before handing control back to the task, and expire the token on origin/session change.
- **missing:** Wire the existing browser-job/session-need island into production (its routes and scheduler are currently unreachable); A typed login-wall signal that distinguishes an actual credential challenge from generic page failure without exposing form values; A continuation protocol linking the browser command lease to the relay job and invalidating it after one successful resume

### "“After you act for me, tell me whether the result matched what you predicted, and learn from my correction without silently changing what you’re allowed to do.”"
- **useful because:** Today receipts say that an action completed, but not whether it achieved the owner's intent. A lightweight outcome review would catch “successfully did the wrong thing,” let the owner correct the interpretation, and improve future judgement while keeping authority changes explicit and reviewable.
- **path:** relay → mac-planner → browser-extension → pendant → dashboard
- **model tier:** Cheap background model compares the prepared intent, observed receipt, and owner correction; realtime is used only if the owner answers during a live conversation.
- **latency:** Generate a compact review within 5 seconds of a completed job; defer non-urgent analysis until idle. Never block the original reversible action on this review.
- **cost:** Usually <$0.02 per reviewed job; most comparisons are structured and avoid model inference.
- **security:** Store a redacted intent/effect summary and provenance IDs, not page contents or credentials. Corrections may update a preference or policy only after explicit confirmation; never infer broader authority from one correction. The owner can inspect and revoke the learned rule.
- **missing:** A typed outcome-review record linking one owner intent to the prepared plan, execution receipt, and observed external state; A bounded correction workflow that distinguishes factual correction, preference change, and one-time exception; A policy-versioned learner that can propose—but never silently activate—a changed autonomy rule

### "“Before you tell me something is done, prove that the dangerous side effect did not happen anywhere else—no message sent, no duplicate booking, no second charge—and show me exactly what you checked.”"
- **useful because:** Completion receipts can prove that one local step ran while missing a duplicate or an unintended external effect on another surface. An explicit negative-assurance check would make high-consequence automation trustworthy: it either finds corroborating absence evidence or says that absence cannot be proven.
- **path:** relay → mac-planner → browser-extension → dashboard → pendant
- **model tier:** Deterministic checks and receipt joins first; a cheap background model summarizes conflicting evidence. Realtime only speaks the final bounded verdict.
- **latency:** Under 3 seconds for known receipt/state checks; escalate to a reviewable pending result rather than blocking indefinitely.
- **cost:** <$0.01 for structured checks; browser verification may dominate latency, not model cost.
- **security:** Read-only by default and fail-closed. Never claim global absence from one surface. Show scope, timestamp, and sources; sensitive evidence stays on the Mac and the pendant receives only a redacted verdict.
- **missing:** Typed postcondition/negative-assurance contracts for action classes such as send, book, buy, and delete; Read-only corroboration adapters for each relevant external surface, with freshness and scope metadata; A verdict type that distinguishes confirmed absent, contradicted, unknown, and stale rather than collapsing to success/failure

### "“If my request is ambiguous, ask me the one question whose answer most changes what you would do, and show me the two possible outcomes instead of making me repeat the whole task.”"
- **useful because:** The owner should spend attention only where it changes the decision. A clarification engine can identify the smallest unresolved variable, present concrete alternatives, and preserve the original context across the answer rather than restarting a cold conversation or guessing silently.
- **path:** relay-realtime → faculty-judgement → mac-planner → browser-extension → pendant
- **model tier:** Realtime model selects and phrases the single high-value question; deterministic policy and typed plan branches ensure it cannot widen scope or execute while clarification is pending.
- **latency:** One spoken turn, ideally under 1.5 seconds to formulate; no external action until the owner answers or the pending branch expires.
- **cost:** <$0.03 per ambiguous request, dominated by one realtime turn; branch previews should use the cheaper planner tier.
- **security:** Question choices must not reveal secrets from candidate branches. Persist only the original intent, unresolved slot, branch summaries, and expiry. Treat silence as cancellation, never consent.
- **missing:** A durable ambiguity object with candidate branches, expiry, and an answer binding to the original request; A planner interface that returns materially different previews without executing either branch; A context-resume path that survives relay/Mac handoff and makes the answer idempotent


## What it asked for

_Nothing._
## Its own summary

Round 195 produced three distinct owner-facing capabilities: receipt-proven briefing recovery (recorded, though the recorder flagged similarity with prior resume work), evidence-backed UART/audio fault diagnosis with a reviewable bug draft (recorded, with similarity warning), and a privacy-preserving browser login-wall handoff that wakes the owner only for a real authentication need and resumes without exposing credentials. The third is the clearest new direction: productionize the currently unreachable browser session-need island, bind it to expiring cross-surface continuation, and keep all secrets in the browser.

**Biggest unknown:** I still need implementation confirmation for the missing joins: whether a durable briefing manifest, UART cursor/authentication surface, and browser login-wall signal already exist under routes not yet inventoried. I do not need to re-request denied owner preferences or TCC grants; the remaining owner inputs are the eventual policy values (which sites may request takeover, what may be spoken, and interruption timing), which should remain explicit configurable fields rather than guessed defaults.

