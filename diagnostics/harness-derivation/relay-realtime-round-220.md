# Harness derivation — relay-realtime — round 220

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Find the best option for this purchase, fill everything in, and leave it staged for me to finish later.” Later: “Finish the staged purchase.”"
- **useful because:** The owner can delegate the tedious authenticated checkout while away from the Mac, without losing the exact cart, shipping choices, or page state. The first request produces a durable, inspectable checkout capsule; the second resumes that same browser session instead of starting over.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use relay-realtime only to classify the short utterance and acknowledge; use mac-planner for the multi-step plan and browser-extension for authenticated Safari execution. Use a slower background model only to summarize the staged capsule.
- **latency:** Acknowledge in under 1 second; staging may take 30–90 seconds asynchronously. Resume should report the final page state within 10 seconds of the Mac/browser becoming available.
- **cost:** About $0.03–$0.15 per staging run, dominated by mac-planner/browser observations; resume is similar. Relay speech classification should be one short low-token turn.
- **security:** The browser session contains payment and address data. The capsule must store references and redacted field hashes, never card numbers or page screenshots by default. Completion must be bound to the exact capsule and current cart total; if merchant, amount, recipient, or shipping changes, report needs_attention rather than silently submitting. The owner's explicit “finish” is the authorization, not a generic policy gate.
- **missing:** A durable checkout-capsule record with expiry, redacted state, expected merchant/amount, and browser session/tab identifiers; A resume operation that revalidates the capsule against the live authenticated page before submitting; A pendant-readable completion or needs-attention event for this capsule, with stale-session recovery

### "“Remember the return deadline on the page I’m looking at, and tell me if it changes.” Later: “Has that deadline changed?”"
- **useful because:** The owner gets a trustworthy personal watch over a fact in an authenticated page, rather than a copied note that silently goes stale. The system records the exact page location and observed value, rechecks the live tab, and speaks only a confirmed change or a clear inability to verify.
- **path:** pendant → relay → browser-extension → mac-planner → dashboard
- **model tier:** Use relay-realtime for the immediate capture/answer; use a cheaper scheduled or on-demand checker for revalidation; use the browser page model only when DOM structure requires interpretation.
- **latency:** Capture acknowledgement under 2 seconds. A recheck should complete within 15 seconds when Safari is online; if offline, retain the last verified value and say so rather than guessing.
- **cost:** Capture is roughly $0.01; each recheck $0.01–$0.05 depending on whether page interpretation is needed. Storage is a small structured fact plus selector/URL provenance.
- **security:** Authenticated page contents must remain scoped to the browser surface and be redacted before projection to voice. Persist only the requested field, page origin, selector/heading anchor, observed timestamp, and a content hash. Never expose neighboring private content in a spoken update. If the page redirects or the anchor is ambiguous, emit needs_attention.
- **missing:** A first-class browser-fact watch that binds a memory fact to a page anchor and content hash, instead of treating browser findings as ordinary text; A checker that can distinguish unchanged, changed, redirected, and unavailable states and update the existing fact with provenance; A compact voice result that includes old/new values only when the owner asks

### "“Turn the latest Discord thread with Alex into an unsent Outlook reply, keeping the links and action items, and show me what you drafted on my Mac.”"
- **useful because:** The owner can bridge conversations across apps without copy/paste: the relay identifies the requested authenticated thread, the browser facet extracts only that thread, the Mac planner creates an unsent Outlook draft, and the pendant reports whether it was created. It saves time while preserving the important boundary that nothing is sent.
- **path:** pendant → relay → browser-extension → mac-planner → dashboard
- **model tier:** Relay-realtime handles entity resolution and a one-sentence acknowledgement; a cheaper planner performs extraction and drafting asynchronously. Browser and Mac agents do the app-specific work; a small verifier compares source links/action items with the draft before completion.
- **latency:** Acknowledge immediately; produce the draft in 20–60 seconds. If either authenticated surface is unavailable, queue the job and notify the pendant when it can resume.
- **cost:** Approximately $0.05–$0.20 per workflow, dominated by reading the thread and composing the draft; verification adds a small second model call.
- **security:** Read only the named conversation and avoid unrelated Discord channels. Keep the draft unsent and mark it explicitly as a draft. Do not copy secrets or attachments unless requested. Store source message IDs and a redacted hash so a retry cannot duplicate drafts; surface any recipient ambiguity instead of guessing.
- **missing:** A cross-surface handoff that passes a scoped browser transcript and provenance to the Mac planner without dumping the whole browser session into the prompt; An idempotent Outlook draft action keyed by source-thread ID, with a verifier and update-in-place behavior; A result receipt that includes the Mac draft location and source links for the dashboard and pendant


## Changes it proposed to its own stack

### `integration` — Build a provenance-carrying cross-surface handoff envelope and coordinator. Each relay job may issue a short-lived, scoped envelope containing the owner utterance, selected browser tab/message IDs, redacted extracted fields, source hashes, intended downstream operation, and an idempotency key. The browser facet and Mac planner consume that envelope rather than receiving an unbounded transcript; they return signed step receipts and a final receipt that the relay can speak and the dashboard can inspect. Add explicit states for staged, resumed, changed-source, unavailable, and needs-attention, plus expiry and replay protection.
- **owner gets:** The owner can ask for work that crosses their authenticated browser and Mac without the system losing which page, message, or draft the request referred to. Results become dependable: “done” means the specific requested artifact changed, and a reconnect or retry will not create duplicate drafts, purchases, or stale answers.
- effort: Medium-to-large: coordinator data model, browser and Mac adapters, receipt verification, redaction tests, and pendant-facing summaries. Build a narrow vertical slice for browser-thread-to-Outlook-draft and staged checkout first.  ·  risk: A bad scope could leak private page content to the wrong downstream agent, or an overly strict hash could reject legitimate page updates. Recover by defaulting to redacted fields, short TTLs, explicit source-change states, and retaining the original job for inspection rather than retrying blindly.
- cost: No meaningful per-turn infrastructure cost; envelope storage is a few KB per job. Verification adds about $0.01–$0.05 when semantic comparison is needed.  ·  latency: Adds under 300 ms for envelope creation and receipt validation; end-to-end work remains dominated by browser/Mac execution.
- security: Improves least-context exposure without imposing an owner-facing confirmation gate. Use per-job bearer capability, audience binding (browser vs Mac), encrypted-at-rest payloads, and one-time idempotency keys; never include card numbers or raw private-page dumps.
- depends on: A real relay-side job coordinator that can persist the envelope and receipt chain; Browser and Mac adapters agreeing on scoped handoff and receipt schemas; A working asynchronous event delivery path to pendant/phone/dashboard; Conversation-context wiring to the existing memory projection so only relevant scoped facts enter the relay prompt


## What it asked for

_Nothing._
## Its own summary

Recorded three owner-facing capabilities and one integration change. The most valuable gap is a provenance-carrying cross-surface coordinator: it would let the pendant safely drive authenticated browser work and Mac artifacts without losing the exact source, duplicating actions, or claiming success on stale state. I also recorded durable staged checkout/resume, browser-fact change verification, and Discord-thread-to-unsent-Outlook-draft workflows. What must change is not another generic action route: the relay needs scoped, expiring handoff envelopes, idempotency keys, source-change states, signed step receipts, and a real asynchronous delivery path.

**Biggest unknown:** The exact live schemas and ownership boundaries of the existing /watches and /pipeline/events implementations remain unclear; the proposals deliberately treat them as integration points to verify rather than assuming their current payloads can support provenance, expiry, and receipt chaining.

