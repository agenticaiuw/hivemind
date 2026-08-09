# Harness derivation — relay-realtime — round 264

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When that task finishes, tell me on the pendant if it succeeded, failed, or needs attention."
- **useful because:** This becomes the system’s signature move: you can start work, walk away, and still get a concise outcome without polling or staring at a screen.
- **path:** relay → mac-bridge → pendant → phone → dashboard
- **model tier:** Realtime only for the spoken handoff; cheaper background checks for job state.
- **latency:** Completion delivery is async; the spoken summary must be under a couple of seconds once delivered.
- **cost:** Low per task. The expensive part is any downstream work; status checks and a short spoken message are cheap.
- **security:** Spoken summaries can leak sensitive content. Keep them generic by default and require confirmation before speaking detailed results in shared spaces.
- **missing:** Implement relay_event_push (currently a schema only).; Implement a real completion watcher rather than relying on best-effort polling.; Integrate with the existing watch/report shape so the protocol isn’t reinvented.

### "What’s still running from earlier, and do I need to do anything?"
- **useful because:** A quick, low-friction status sweep while the owner is moving around. It reduces anxiety and prevents forgotten work from silently failing.
- **path:** relay → mac-bridge → dashboard
- **model tier:** Realtime for summarizing; background reads for job status.
- **latency:** Sub-second to start speaking; summary under ~10 seconds, with spoken_status_interrupt available to cut it short.
- **cost:** Low. Mostly status reads and summarization.
- **security:** Avoid naming sensitive documents or recipients unless the owner asks for detail; keep default summaries high-level.
- **missing:** Standardize job labels and categories so summaries are meaningful.; Ensure relay_job_status can resolve ambiguous references reliably.

### "Send this to my Mac to handle, and route it to the right place."
- **useful because:** Reduces friction. The owner shouldn’t have to remember whether something is a Mac action, a browser action, or a delegated plan.
- **path:** relay → mac-bridge → browser
- **model tier:** Realtime for intent capture; downstream planning uses cheaper tiers.
- **latency:** Fast classification (<300ms) before handing off.
- **cost:** Low. Routing decisions are cheap; downstream execution dominates.
- **security:** Misrouting could trigger unintended actions. Require reversible defaults and confirmations for destructive steps.
- **missing:** Implement a real relay routing tool with an enum of supported intents (current relay_route_intent schema is unresolved).; Publish a capability manifest for the relay so routing can be validated.

### "“What changed in my work since the last time I wore you?” Give me only the meaningful changes across my Mac and my signed-in browser, and let me ask about any one of them by voice."
- **useful because:** Today the owner must remember which app or website to inspect. A worn device should provide a trustworthy return-to-work delta even after time away, combining local Mac activity, browser-session changes, and prior pendant tasks into one ranked spoken answer.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Use a cheap background summarizer for snapshot comparison and ranking; use relay-realtime only to conduct the short follow-up conversation. Never send raw page contents to the realtime tier unless the owner asks about a specific change.
- **latency:** Initial request can take 10–20 seconds; follow-up should begin in under 1 second from a stored change card. Snapshot capture may run opportunistically when Mac/browser surfaces are online.
- **cost:** Roughly $0.01–$0.05 per comparison depending on changed document/page text; most runs should be embedding/hash and metadata work, with a small-model summary only for changed items.
- **security:** Browser pages may contain private work data. Store encrypted hashes, timestamps, titles, and narrowly scoped excerpts rather than full snapshots; require explicit owner request before reading a changed page aloud. Do not report a change merely because a surface was offline.
- **missing:** A per-surface snapshot ledger with provenance, content hashes, and last-successful-capture state; Mac hooks that capture selected app/document metadata and browser hooks that capture authenticated-tab metadata without treating offline as no-change; A cross-surface diff/ranking worker and a compact change-card API; A spoken drill-down route from a change-card id to its source surface

### "“That didn’t work—why, and can you recover it?” Have the pendant explain a failed Mac/browser task in one sentence, identify what actually happened, and offer the safest concrete recovery (retry, undo, or continue from the last confirmed step)."
- **useful because:** A queued job saying failed is not enough: the owner may be away from the Mac and cannot inspect which step happened. This turns failure from a dead end into a truthful, actionable recovery conversation spanning relay records, Mac receipts, browser state, and the pendant’s spoken interface.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Use a small background model to classify receipts and construct a recovery graph; relay-realtime only answers the owner and dispatches an already-selected recovery. Use the stronger planner only when the graph has an unknown or ambiguous step.
- **latency:** Read the existing receipt and speak an initial diagnosis in under 2 seconds. A recovery may take normal Mac/browser execution time, with progress delivered through the existing inbox/event path.
- **cost:** Usually under $0.01 because it is receipt summarization; $0.03–$0.10 only when replanning a failed multi-step workflow.
- **security:** The explanation must distinguish confirmed actions from attempted actions and must never claim an undo succeeded until a fresh receipt verifies it. Recovery can touch documents, mail, or websites, so preserve the owner’s existing maximum-access policy but expose the exact target and resulting receipt in the dashboard.
- **missing:** A normalized per-action receipt schema shared by Mac and browser executors, including precondition, outcome, and reversible inverse; A failure-cause and recovery planner that can replay only the unconfirmed suffix of a job; A user-facing spoken recovery endpoint that accepts a job reference or resolves “that” from the active session; Verification hooks for browser and Mac state after retry/undo

### "“Review the change I was working on and tell me the one thing most likely to break.” From the pendant, inspect the currently focused project/diff on my Mac, consult relevant authenticated documentation in my browser if needed, and speak a concise risk plus the exact file or test to inspect."
- **useful because:** The owner often notices a concern away from the desk but cannot reconstruct the current editor state. This makes the pendant a useful engineering partner rather than only a remote-control button: it joins the Mac’s real working tree, browser context, and voice follow-up without requiring the owner to paste code.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Use mac-planner to gather a bounded diff, test status, and focused-file metadata; use a cheaper background code-review model for analysis. Relay-realtime only conducts clarification and speaks the ranked finding.
- **latency:** Speak an acknowledgement immediately, then return the first finding in 10–30 seconds. If tests are needed, stream a short “checking” status and deliver the result asynchronously rather than holding the voice turn.
- **cost:** About $0.03–$0.20 per review, dominated by diff/test context; avoid sending the entire repository by using a bounded changed-file and relevant-symbol slice.
- **security:** Source code and private documentation leave the Mac only to the configured model/relay. Default to the focused project and uncommitted diff, redact secrets and environment files, cite exact evidence, and say “could not inspect” when the Mac or browser is offline instead of guessing.
- **missing:** A Mac action that exports a bounded, secret-redacted working-tree diff plus focused editor file and test status; A code-review worker with repository-aware context selection and evidence citations; A browser handoff that can fetch only documentation pages relevant to imported symbols; A durable review-result card that the pendant can summarize after the original voice session


## Changes it proposed to its own stack

### `relay` — Add a relay-side capability manifest endpoint (e.g., GET /capabilities) and wire it into discovery tooling, so agents can inventory what the relay can actually do.
- **owner gets:** Fewer failures and less guesswork means faster, more reliable voice interactions. You stop asking for things that don’t exist.
- effort: Moderate: implement route, ensure it reflects live router, and update discovery paths.  ·  risk: Low. Main risk is exposing internal names; mitigate by redacting sensitive routes.
- cost: Minimal runtime cost; small maintenance overhead.  ·  latency: None for normal operation; slight cost when clients call discovery.
- security: Requires careful filtering of internal-only endpoints.
- depends on: Access to the relay router metadata in the worker

### `integration` — Implement job completion delivery by composing existing building blocks: a completion watcher that feeds a single queue of typed alerts, with delivery to pendant/phone/dashboard and clear TTL semantics.
- **owner gets:** You can trust the system to close the loop without babysitting it.
- effort: High: needs orchestration, storage of pending notifications, and reliable delivery semantics.  ·  risk: Medium: duplicate or missing notifications are confusing. Use idempotent receipts and retries.
- cost: Low per notification; storage bounded by TTL.  ·  latency: Async; delivery should be near-instant when online.
- security: Spoken content must be sanitized; detailed info only on request.
- depends on: Implement relay_event_push or an equivalent real route; Durable storage for pending notifications


## What it asked for

### `t24-i49m` (tool) — relay_capability_manifest
- why: As the relay agent, I need a reliable way to discover my own live routes and tools so I don’t guess or probe blindly.

```json
{
  "type": "object",
  "properties": {
    "includeRoutes": {
      "type": "boolean"
    },
    "includeTools": {
      "type": "boolean"
    },
    "includeVersions": {
      "type": "boolean"
    }
  },
  "required": [
    "includeRoutes",
    "includeTools"
  ]
}
```

## Its own summary

Recorded three owner-facing capabilities: a trustworthy spoken “what changed since I last wore you?” cross-surface delta; truthful failure diagnosis with verified retry/undo recovery; and voice-triggered review of the current Mac project/diff with browser documentation context. The largest gap is not another relay verb: it is a provenance-bearing, secret-redacted evidence layer connecting Mac state, authenticated browser state, and job receipts to spoken drill-downs. Each proposal names the missing pieces rather than pretending existing routes already provide them.

**Biggest unknown:** The exact live schemas and capture boundaries for Mac working-tree/editor state and authenticated browser snapshots remain unobserved; implementation must define those while preserving provenance and avoiding claims based on an offline surface.

