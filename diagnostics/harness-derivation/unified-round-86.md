# Harness derivation — unified — round 86

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Keep working on this while I’m away, and when it is ready, tell me what will happen; one deliberate press on my pendant should approve exactly that staged action.”"
- **useful because:** This closes the gap between background Mac/browser work and trustworthy real-world completion. The relay can continue while the Mac is unattended, the browser can retain the owner’s private session, and the pendant can provide a physical, low-ambiguity approval without requiring the owner to reopen a screen. It must refuse if the staged page, values, scope, or risk changed.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use the cheaper background model for planning, extraction, and change detection; use realtime only to explain the final receipt over audio. Deterministic policy code, not a model, validates the approval token and exact before/after hash.
- **latency:** Background work may take minutes. The review notification should reach the pendant within 2 seconds of staging; approval acknowledgement within 1 second when LTE-M is available, with a spoken fallback if the link is interrupted.
- **cost:** About $0.01–$0.08 per background task depending on browser/model calls; approval and receipt are negligible. Dominant cost is authenticated page extraction and long-running planner context.
- **security:** Never transmit page secrets into the spoken prompt or store them in the approval payload. Bind a short-lived, single-use token to session/tab, URL, action type, normalized before/after values, risk class, and expiry. A second press cancels; changed DOM, stale session, timeout, reconnect, or any destructive/send/purchase action requires fresh review. The pendant LED should indicate staged versus approved without exposing content.
- **missing:** A durable staged-action record shared by relay, Mac, and browser with immutable before/after evidence hashes; A pendant-side single-use approval/cancel gesture and signed acknowledgment (the one-button hardware needs a deliberate long-press or press-confirm sequence); A server policy gate that revalidates the exact staged record immediately before execution; Push delivery and retry semantics to the pendant, including a safe expired-token state; Dashboard review UI showing provenance, scope, and the exact irreversible boundary

### "“Don’t interrupt me at random: watch my calendar and active Mac/browser work, queue only genuinely urgent events, and tell me the shortest useful version at the next safe moment.”"
- **useful because:** Today a wearable can be always available but has no shared notion of whether the owner is speaking, presenting, driving a staged browser task, or free. A relay-level interruption arbiter would combine calendar state, active task checkpoints, browser urgency, and pendant audio state so alerts arrive when useful rather than breaking concentration or exposing private content aloud.
- **path:** relay-realtime → pendant → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic priority, quiet-hours, and speech-state rules first; a cheap background model clusters and summarizes queued events. Realtime is used only for the one-sentence spoken delivery when the arbiter opens a safe window.
- **latency:** Ingest events within 5 seconds; decide within 1 second after an event or speech-state transition; deliver at the next safe boundary, otherwise visibly/haptically queue it. No polling more often than necessary.
- **cost:** Usually under $0.01 per event batch; model cost is dominated by summarizing multiple queued items, not by arbitration. Calendar/browser polling and audio event transport dominate infrastructure overhead.
- **security:** Classify event sensitivity before speech: never speak message bodies, account names, or browser secrets in public mode. Store only redacted queue cards with provenance and expiry. Calendar and browser events need scoped permissions, and the owner must be able to mute, inspect, reorder, or delete the queue. Critical actions remain review-only and cannot be triggered by an interruption.
- **missing:** A shared event envelope carrying source, urgency, sensitivity, expiry, and suggested delivery mode; Reliable pendant speech/recording boundary events and a local queue indicator; Mac/browser adapters for active-window, presentation, meeting, and staged-transaction state without Accessibility assumptions; A policy editor in the dashboard plus a durable queue and delivery receipts

### "“Use my logged-in browser and Mac to answer this, but prove that passwords, tokens, and unrelated private page content never leave the device or enter the model context.”"
- **useful because:** The owner can get useful answers from private accounts without choosing between convenience and uncontrolled data disclosure. The browser and Mac can inspect sessions they alone can reach, while the relay receives only an allowlisted, purpose-bound result and a verifiable redaction receipt—not a page dump or credential-bearing screenshot.
- **path:** browser-extension → mac-planner → relay-realtime → dashboard → pendant
- **model tier:** Run extraction, secret detection, and field allowlisting locally with deterministic code; use a cheaper background model only on the resulting structured fields. Use realtime only to speak the answer. A policy engine, not an LLM, decides whether data may cross the boundary.
- **latency:** For an already-open tab, local filtering and a short answer should complete in 2–5 seconds. New navigation or multi-page research may take minutes in the background; the owner should hear only a progress receipt, never raw sensitive content.
- **cost:** Usually <$0.02 per request; model tokens fall because only selected fields cross the boundary. Engineering and test cost dominates, especially secret-pattern coverage and browser/OS boundary verification.
- **security:** Treat DOM, screenshots, clipboard, accessibility trees, shell output, and model prompts as separate egress surfaces. Default-deny all fields, classify secrets and quasi-identifiers locally, bind an extraction to the user’s stated purpose, log hashes and policy decisions rather than values, expire intermediate buffers, and require explicit confirmation before any value crosses from a private session into an external service. Fail closed on classifier uncertainty.
- **missing:** A local, deterministic redaction/allowlist service shared by the browser bridge and Mac planner; A relay admission gate that accepts typed fields plus a signed privacy receipt, rejecting raw page text, screenshots, clipboard data, and credentials; End-to-end secret-canary tests proving values do not appear in prompts, logs, D1, R2, receipts, or spoken output; Dashboard controls for per-domain data classes and a visible proof of what was allowed, blocked, and discarded


## Changes it proposed to its own stack

### `integration` — Introduce a single signed Cross-Surface Event Envelope and append-only delivery ledger. Every calendar, browser, Mac-job, and pendant event carries eventId, source surface, createdAt, expiry, urgency, sensitivity, required delivery mode, related job/session, and redacted payload hash. Relay deduplicates and orders envelopes, the Mac contributes active-task context, and the pendant acknowledges spoken/haptic delivery. Consumers can replay from a cursor without duplicating alerts.
- **owner gets:** The owner gets one coherent alert stream instead of duplicate or contradictory notifications when the same browser change, Mac job completion, and pendant audio event race each other. Alerts can be safely delayed, resumed after a dropped link, and explained with a receipt.
- effort: Moderate relay schema and adapters, then small changes to pendant event emission, Mac bridge polling, browser watch jobs, dashboard queue, and receipt queries. Add fault-injection tests for reconnect, clock skew, duplicate delivery, and expired events.  ·  risk: A bad ordering rule could hide urgent events or speak stale private data. Use monotonic per-source sequence plus server receipt time, never discard high-urgency events silently, redact payloads at ingress, and show an explicit unknown/out-of-order state. Ledger growth needs bounded retention and compaction.
- cost: Small D1/R2 storage and bandwidth increase; no model cost for routing. Summaries invoke a cheap model only when multiple envelopes must be compressed into speech.  ·  latency: One extra relay write/read, typically tens of milliseconds; reconnect replay may deliver a short burst that must be rate-limited.
- security: Event envelopes should be authenticated per device/session and sensitivity labels enforced before audio. Hashes and redacted payloads make receipts useful without persisting secrets; delete expired payloads while retaining minimal audit metadata.
- depends on: Pendant speech-state and local queue event definitions; Durable relay job/receipt cursor support; Owner interruption and urgency policy; A typed context projection so active-task facts do not leak into unrelated alerts


## What it asked for

_Nothing._
## Its own summary

Round 86: discovered the live owner/device/tool state and backlog, then recorded three forward steps: exact single-press approval for immutable staged Mac/browser actions, a cross-surface interruption arbiter, and a signed append-only event envelope/delivery ledger. The most valuable new connective gap is reliable ordering, deduplication, expiry, and privacy-aware delivery across pendant, relay, Mac, and browser.

**Biggest unknown:** I still lack the authoritative 24 kHz end-to-end acceptance thresholds, production pendant constraints, and the owner's interruption/urgency and queued-action resume policy. Those requests are already pending and should not be duplicated; they determine whether audio and approval policies are safe. Also, the current browser-session device is offline, so live private-page validation remains unavailable.

