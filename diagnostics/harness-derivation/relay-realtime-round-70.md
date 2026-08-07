# Harness derivation — relay-realtime — round 70

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Keep working after I stop talking: check my open tabs and inbox for anything urgent, draft responses, and leave a review queue I can approve later."
- **useful because:** This matches how the owner lives with the pendant: speak a goal, walk away, and later review a prepared, evidence-backed set of drafts without having to re-run the whole thought process.
- **path:** relay → mac-bridge → browser → unified → faculty-judgement → faculty-action
- **model tier:** Realtime for the initial voice handoff; a cheaper planner model for the long-running work; a small action model for extraction/filling.
- **latency:** Under a second to acknowledge; seconds to hand off a plan; minutes for the full review queue to be assembled.
- **cost:** Cheap for routing and receipts; moderate for browser extraction and summarization; dominated by authenticated page reads and reconciliation.
- **security:** Needs strict provenance and a hard stop before sending. Drafts and extracted content are sensitive; keep them local unless the owner explicitly exports them.
- **missing:** Durable job runner for browser and Mac tasks; Persistent review queue UI or artifact; Typed context service to avoid resending large state every turn; Reliable browser session affinity and tab results

### "“What was I doing on my computer when I left, and what’s the next useful step?”"
- **useful because:** The pendant is worn away from the Mac; today it cannot reconstruct a trustworthy interrupted-work context across the Mac, authenticated browser tabs, and the last voice exchange. This would let the owner resume work hands-free instead of remembering which app, page, and unfinished action they left behind.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use relay-realtime only to capture the question and speak the short answer. A cheaper background synthesis model should combine timestamped Mac activity, browser-extension tab metadata/content that is already open, and the recent pendant transcript; mac-planner should identify the unfinished goal and mac-vision/browser should verify the current visible state before any suggested next step.
- **latency:** A spoken acknowledgement in under 500 ms; a first factual context card within 5 seconds when the Mac/browser are online. If either is offline, say exactly which evidence is stale rather than guessing, and complete when connectivity returns.
- **cost:** Roughly $0.01–$0.08 per reconstruction depending on how much page text and screen evidence is summarized; the dominant cost is background synthesis and transferring selected page/screen context, not the short relay turn.
- **security:** This could expose sensitive open tabs, documents, and screen content through the relay. Keep raw screenshots/page bodies on the Mac or browser bridge, send only time-bounded extracted evidence and citations, encrypt the retained context, and visibly label every fact with source and age. Never infer that an action was completed from intent alone; executing the proposed next step must remain a separate explicit request.
- **missing:** A local append-only activity journal on the Mac with app/window/document identifiers and timestamps, excluding keystroke contents by default; A browser-extension endpoint that reports the authenticated open-tab trail and selected page headings/snippets with per-item freshness and source IDs; A relay-side context-reconstruction job that correlates Mac, browser, and pendant events and returns a cited, confidence-ranked interruption summary; A compact spoken-result and dashboard view that lets the owner inspect the evidence and discard the reconstructed context; A reliable reconnect-and-complete path for when the pendant is online but the Mac is asleep or temporarily unreachable

### "“I’m stuck—look at what’s on my Mac and tell me the safest next step. Don’t change anything yet.”"
- **useful because:** Today the owner can either speak to the pendant without visual computer state or use the Mac agents without a live spoken diagnostic loop. This would turn the worn device into a remote, read-only troubleshooting companion: the owner describes the problem, the Mac/browser surfaces inspect the actual state, and the pendant explains one concrete next step without silently acting.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Relay-realtime handles turn-taking, clarification, and concise speech. mac-vision (or a new read-only observation worker) captures the relevant Mac screen/app state; browser-extension supplies DOM/accessibility evidence for browser issues; mac-planner synthesizes the diagnosis and returns typed, cited observations. Do not invoke an action worker until the owner separately asks to perform the step.
- **latency:** Acknowledge in under 400 ms, obtain a fresh observation in 2–4 seconds, and speak the diagnosis in under 6 seconds. If visual capture is unavailable, state that limitation and ask the owner for a screenshot or exact text rather than hallucinating.
- **cost:** About $0.02–$0.12 per diagnostic turn; screen/DOM capture and multimodal synthesis dominate, while relay speech costs little relative to the vision call.
- **security:** Screens may contain passwords, messages, health, or work data. Capture only the foreground app/window and redact password fields before leaving the Mac; browser evidence should be limited to the active tab and selected DOM nodes. Store no screenshots by default, retain source IDs and hashes for audit, and make the default mode strictly observational. The owner’s separate action request should be clearly echoed before execution, but no confirmation gate is needed for read-only diagnosis.
- **missing:** Re-enable or replace the currently disabled mac-vision observation loop with a read-only snapshot endpoint and freshness metadata; A Mac-side redaction/cropping layer for foreground-window and browser accessibility evidence; A relay conversation protocol that correlates the spoken turn with one observation request, supports one clarification, and expires stale evidence; Typed diagnostic responses with source citations and an explicit distinction between observation, inference, and proposed action; A pendant UX state (LED/audio cue) indicating observing versus acting, so the owner knows no mutation occurred

### "“I think I left my devices exposed—lock everything down now, and tell me what you did.”"
- **useful because:** A worn pendant is an always-available emergency control surface, but today there is no single spoken containment operation spanning the Mac, authenticated browser sessions, and relay. In a stressful moment the owner should not have to remember separate commands or reach the Mac.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Relay-realtime recognizes only a tightly scoped containment intent and immediately speaks acknowledgement. A deterministic relay policy fans out in parallel: Mac agent locks the screen and disables local sharing where supported; browser extension closes or suspends selected authenticated tabs and invalidates extension-held task leases; relay revokes active remote action tokens. A slower background auditor reports which operations succeeded, failed, or were unreachable.
- **latency:** Acknowledge immediately and begin containment within 1 second. Lock/revoke operations should complete within 5 seconds; the spoken report must enumerate unknown/unreachable surfaces rather than claiming global lockdown.
- **cost:** Under $0.01 for deterministic fan-out; the optional audit/summarization is roughly $0.01–$0.03. Cost is dominated by any device-status retries, not model inference.
- **security:** False positives are disruptive, so require a distinctive phrase or a physical long-press plus voice phrase, but never require a slow conversational confirmation once triggered. Make the operation idempotent and reversible where possible; preserve a local, tamper-evident receipt. Do not transmit passwords or page contents. The owner must be able to configure whether browser tabs are merely suspended, logged out, or closed, because logout can destroy unsaved work.
- **missing:** A pendant firmware emergency trigger with debounce, distinct LED/audio acknowledgement, and offline queueing until the relay reconnects; A relay containment coordinator with idempotency keys, bounded retries, partial-failure reporting, and revocation of in-flight jobs; Mac bridge primitives for immediate screen lock and sharing/network containment; Browser-extension primitives for suspending/closing configured authenticated sessions and revoking extension leases; A dashboard policy editor and immutable containment receipt viewer; A tested recovery path that restores only explicitly configured non-sensitive state after the owner is safe


## Changes it proposed to its own stack

### `relay` — Add a lightweight intent-routing tool contract that returns a job id immediately and stores a normalized intent + utterance, then emits progress receipts to the relay so it can narrate status without re-planning.
- **owner gets:** The owner gets a snappy acknowledgment and consistent follow-up: they can ask “what happened to that?” and hear a precise status even if the Mac is asleep.
- effort: Medium: define schemas, wire to existing plan/execute endpoints, and unify job receipts with relay_job_status.  ·  risk: Misrouting if the intent classifier is wrong; mitigate by keeping actions reversible by default and using typed targets.
- cost: Low API cost per invocation; main cost is storage for job metadata and receipts.  ·  latency: Improves perceived latency by returning quickly; background work continues elsewhere.
- security: Stores sensitive utterances and task metadata; must encrypt at rest and limit retention.
- depends on: Job receipt/undo consistency across relay and Mac harness; Durable job runner or at least a reliable receipt store

### `routines` — Introduce a scheduler layer (cron triggers or durable object alarms) to run page watches and daily briefings, with quiet hours and backoff, then notify the relay with a compact summary when new findings exist.
- **owner gets:** The system can prepare useful information while the owner is away, so the pendant delivers value instantly when they ask or when something urgent appears.
- effort: High: requires backend wiring, persistence, and careful cadence controls.  ·  risk: Notification spam or repeated work; mitigate with semantic change fingerprints and cooldowns.
- cost: Moderate ongoing cost for scheduled runs; dominated by authenticated reads and extraction.  ·  latency: Improves interactive latency because work is precomputed.
- security: Scheduled jobs touch sensitive accounts; require provenance logging and never auto-send actions.
- depends on: Durable job runner; Browser session affinity and authenticated page access; Typed context service to minimize resending state


## What it asked for

_Nothing._
