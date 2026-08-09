# Harness derivation — relay-realtime — round 229

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If my Mac is offline, read this public page for me and summarize it."
- **useful because:** The owner can get quick answers without needing their Mac online, which is perfect for a wearable voice interaction.
- **path:** relay
- **model tier:** realtime for interaction; the fetch/summarize can be a cheaper model if available
- **latency:** A few seconds, mostly network.
- **cost:** Moderate; dominated by web fetch and summarization tokens.
- **security:** Only public content should be fetched on the server. Avoid authenticated pages.
- **missing:** 

### "“Check whether this document, email, or web page is actually true. Compare it against my local files, authenticated browser sources, and current web evidence, then tell me the conclusion, the strongest conflicting evidence, and exactly where each claim came from.”"
- **useful because:** The owner currently gets either a fast answer or a computer action, not an auditable cross-surface investigation. This would make the pendant a fact-checking instrument for decisions made while away from the Mac, while preserving uncertainty instead of confidently repeating one source.
- **path:** pendant → relay → mac-planner → mac-terminal → browser-extension → dashboard
- **model tier:** Use relay-realtime only to clarify the claim and speak the result; use faculty-perception/judgement for source comparison and a cheaper background model for extraction. mac-planner/mac-terminal inspect local material, browser-extension reads authenticated pages, and the dashboard exposes a citation ledger.
- **latency:** Speak an acknowledgement in under 1 second; return a preliminary verdict in 10–20 seconds and a full evidence bundle asynchronously.
- **cost:** Roughly $0.03–$0.15 per investigation, dominated by page/document extraction and the background comparison model; relay speech remains a small fraction.
- **security:** Local files and authenticated pages leave their surfaces and are joined into one evidence record. Never read unrelated sources: require explicit source scope or a narrow claim target, redact secrets from spoken output, and retain citations rather than raw documents by default.
- **missing:** A cross-surface evidence graph with claim-level provenance and contradiction scoring; A Mac action that exports selected document/email/page text with stable source identifiers; A relay spoken-result format that can cite a short source name and expose the full ledger on the dashboard

### "“Set up a meeting with [person] about [topic]. Find a time that works for both of us, use the right account and time zone, send the invitation, and tell me what you sent.”"
- **useful because:** A worn assistant should finish a coordination task rather than merely create a reminder or open an app. Today the owner must manually bridge calendar, contacts, email, and authenticated web sessions, especially when the Mac is unattended. This is a genuinely cross-surface transaction with a clear final receipt.
- **path:** pendant → relay → mac-planner → mac-terminal → browser-extension → dashboard
- **model tier:** Relay-realtime extracts names, topic, and constraints. A cheaper planner resolves calendars and identities; browser-extension handles the authenticated scheduling surface; mac-planner uses native Calendar/Mail when that is the authoritative account. The relay speaks only the final receipt or a single blocking ambiguity.
- **latency:** Acknowledge immediately; resolve availability in 15–30 seconds; if a participant must be contacted through a web portal, complete asynchronously and push one concise result.
- **cost:** About $0.05–$0.25, dominated by browser/calendar reads and invitation composition; much cheaper than keeping the realtime model in the loop.
- **security:** Identity confusion and accidental external communication are the main risks. Match the person against contacts and prior correspondence, show recipient/time/account in the spoken pre-send summary, and write an immutable sent-message receipt. The owner’s standing maximum-access policy means this need not become a generic confirmation gate.
- **missing:** A unified availability and identity resolver across native Calendar/Mail and authenticated browser sessions; An atomic send-and-receipt operation so partial invitations cannot be reported as complete; A durable, owner-visible transcript of recipient, timezone, account, and exact invitation body

### "“My Mac is stuck / this app is broken. Diagnose it, save anything recoverable, fix it or roll back the last change, and keep trying until you can tell me exactly what state it is in.”"
- **useful because:** This would be the system’s most valuable everyday capability: the owner can recover an unattended Mac from a pendant instead of waiting until they return to it. It combines perception, judgement, reversible action, and truthful completion rather than stopping at a suggestion or a queued plan.
- **path:** pendant → relay → mac-planner → mac-vision → mac-terminal → dashboard
- **model tier:** Relay-realtime handles the initial symptom and short spoken updates. faculty-perception plus mac-vision inspect the actual UI/process state; mac-terminal performs diagnostics and checkpointed recovery; faculty-judgement selects a rollback or repair; a cheaper background worker verifies stability. Escalate to the owner only when the machine cannot establish a safe state.
- **latency:** Acknowledge in under 1 second, establish a first diagnosis in 5–10 seconds, and continue recovery for up to several minutes while the owner is away. Deliver a final spoken state plus a durable dashboard receipt.
- **cost:** Approximately $0.10–$0.60 per incident, dominated by repeated screenshots/vision and terminal verification; most healthy-path incidents should use only a few planner calls.
- **security:** Recovery can destroy unsaved work or widen damage. Capture process/window state and make a local checkpoint before mutations, prefer app-native recovery and reversible moves, record every command and screenshot hash, and never claim success without a post-fix health check. Secrets and document contents must stay on the Mac unless the owner explicitly asks for them.
- **missing:** Enable a real Mac computer-use/vision loop with screenshot and interaction feedback; the current loop is disabled; Checkpoint/rollback primitives for common apps and filesystem mutations, including unsaved-work detection; A watchdog worker that can continue and verify recovery after the voice session ends; A truthful incident receipt and pendant push path that distinguishes fixed, partially recovered, and unreachable


## Changes it proposed to its own stack

### `relay` — Publish a relay capability manifest route (e.g., GET /capabilities) that lists the relay’s own routes, tools, and which are implemented vs schemas-only. Include enum values where applicable and a live/disabled flag.
- **owner gets:** Reliability improves immediately: the voice agent stops guessing what exists, routes requests correctly, and avoids dead ends that sound like promises but do nothing.
- effort: Medium. It’s a new route plus a small registry that mirrors what the Mac agent already exposes.  ·  risk: Low risk. Worst case is an incomplete manifest; mitigate by marking entries as disabled until proven live.
- cost: Small ongoing overhead to generate the manifest; negligible per request.  ·  latency: Tiny. One extra introspection call when needed.
- security: Moderate. The manifest could expose internal surface names; restrict it to authenticated callers and redact sensitive details.

### `mac-harness` — Replace the disabled computer-use loop with a bounded observe–act–verify runner: capture a redacted screenshot and accessibility tree, execute one reversible action, recapture, and persist a step receipt; support checkpoint creation and automatic rollback for the app/filesystem operations it touched. Let the relay keep the job alive after the voice session and push only state transitions to the pendant.
- **owner gets:** When the owner is away, saying “fix my Mac” would result in a verified recovery instead of a guess, a stale plan, or an unexplained failed job.
- effort: High: enable and harden the vision model integration, add screenshot/accessibility adapters, checkpoint providers for common apps, a watchdog, and failure-injection tests against unattended Mac states.  ·  risk: A bad action could close an app or alter data. Recover with per-step checkpoints, process/window inventory, an emergency stop command from the pendant, and a hard cap on retries; if verification fails, report needs-attention rather than continuing blindly.
- cost: Roughly $0.05–$0.40 per incident for vision calls plus local storage for receipts/checkpoints; no hardware cost.  ·  latency: Adds 1–3 seconds per observe–act–verify step, but allows progress and completion after the owner stops speaking.
- security: Screenshots may contain private documents and credentials. Redact before relay storage, keep raw captures on the Mac with short retention, and transmit hashes/state summaries unless the owner explicitly requests imagery.
- depends on: An enabled mac-vision computer-use loop; A durable post-session job watcher and pendant event delivery; Mac-local checkpoint/rollback primitives


## What it asked for

_Nothing._
## Its own summary

Recorded three new owner-facing capabilities: provenance-backed cross-surface fact checking, end-to-end meeting coordination, and unattended Mac diagnosis/recovery—the last is the highest-value daily capability. Also recorded the concrete Mac-harness change needed to make recovery real: bounded observe–act–verify with checkpoints, rollback, receipts, and post-session pendant updates. The missing pieces are explicit in each record: evidence/identity transaction layers, atomic send receipts, and an enabled verified vision/recovery loop.

**Biggest unknown:** Whether any of these narrowly scoped workflows already exists under a differently named backlog entry; I was instructed not to discover further this round, so the proposals are intentionally specific about their missing cross-surface guarantees rather than assuming generic planner support is enough.

