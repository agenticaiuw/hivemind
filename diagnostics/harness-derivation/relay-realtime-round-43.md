# Harness derivation — relay-realtime — round 43

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Keep working on that for me even if my Mac or browser drops offline, and tell me on the pendant when it is finished or genuinely stuck."
- **useful because:** Today a spoken delegation silently depends on one surface staying reachable; the owner has no dependable way to leave the Mac, let execution migrate to the authenticated browser or relay, and receive a truthful completion or blocked result. This gives the worn device an always-available, cross-surface continuation rather than merely a status page.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard-ux
- **model tier:** Realtime only interprets the initial spoken goal and announces concise state changes. A cheaper background model classifies retryability and summarizes receipts; mac-planner plans Mac work, mac-vision performs UI steps when available, and browser-extension/server browser executes browser-native steps when a valid session exists.
- **latency:** Acknowledge the request on the pendant within 1 second. Persist and begin the run within 3 seconds. Surface migration/retry state changes within 10 seconds of health changes; completion announcement can be delayed up to 30 seconds. No polling loop should consume realtime tokens.
- **cost:** Initial voice turn uses the existing realtime tier; each migration or retry uses a small background-model call, roughly $0.002–$0.02 per state transition depending on receipt size. Dominant cost is model context and any browser/computer-use calls, not relay storage.
- **security:** The relay must persist an explicit task scope, destination, and plan hash, never silently broaden a failed task while migrating surfaces. Browser sessions and Mac credentials remain on their respective devices; only typed intents, redacted receipts, and necessary outputs leave them. Owner policy permits reversible execution without prompts, but irreversible external sends/purchases/deletions must be surfaced as awaiting owner confirmation rather than claimed complete. Every retry needs an idempotency key and an audit trail to prevent duplicate actions.
- **missing:** A durable task supervisor with lease/heartbeat and retryable-vs-terminal error classification; Cross-surface execution adapters that can hand the same scoped task from Mac to authenticated browser/server browser and back; A relay-to-pendant push/event channel for completion, migration, and blocked announcements, including offline buffering; A portable receipt schema containing scope, plan hash, evidence, side effects, and idempotency key; A migration-aware dashboard showing which surface currently owns the lease and why a task stopped

### "Take the latest file from my Mac project, prepare exactly the fields this authenticated web form needs, fill it in, and show me a short preview on the pendant before submitting."
- **useful because:** This joins two trust domains that are currently separate: local Mac files and a browser session. The owner can complete a real work handoff while away without dictating sensitive content or manually copying it between devices, while retaining a compact spoken preview before an external submission.
- **path:** pendant → relay → mac-planner → mac-terminal → browser-extension → dashboard-ux
- **model tier:** Realtime extracts the target and preview preference only. mac-planner/mac-terminal locate and minimally transform the local file; a cheaper background model maps content to the form schema and flags missing or ambiguous fields; the browser harness fills fields. Realtime speaks only the preview and asks for the final submit decision.
- **latency:** Speak an acknowledgement in 1 second, return a field preview in 15 seconds for a small local file, and complete filling within 45 seconds. Submission must wait for the owner's explicit spoken confirmation after the preview.
- **cost:** One small background extraction/mapping call, approximately $0.005–$0.05 depending on document size, plus one browser/computer-use operation. Realtime cost is limited to acknowledgement and preview/confirmation turns; the dominant variable is document parsing and browser interaction.
- **security:** Raw local file contents must be transferred only over an authenticated, encrypted, short-lived relay envelope and should be deleted after receipt retention expires. Never send secrets or unrelated file sections; show field names and redacted values on the pendant/dashboard. The browser session identity and destination URL must be displayed in the preview. Filling is reversible; external submission always requires explicit confirmation, with an immutable receipt of the exact submitted field set.
- **missing:** A scoped Mac-to-relay artifact transfer with content redaction, size limits, and expiry; A browser form-schema extractor that returns typed fields and destination identity rather than coordinates alone; A field-mapping/validation service with provenance back to source spans and ambiguity reporting; A pendant-sized preview encoding and explicit one-button/voice confirmation protocol; A transactional submit adapter that can prove the submitted values and avoid duplicate submissions


## Changes it proposed to its own stack

### `relay` — Add evidence-gated Action Leases to the live voice path: every routed plan/execution request carries a plan hash and session binding, with preflight evidence requirements, postcondition evidence capture, and idempotency to reject stale duplicate button presses. States: blocked, awaiting-confirmation, in-progress, completed, failed. The relay speaks blocked/not-done when prerequisites (like macOS Accessibility/Screen Recording or browser session online) are missing, and can resume when evidence arrives.
- **owner gets:** They get trustworthy voice feedback. If the Mac/browser isn’t in a usable state, the pendant says so instead of pretending work happened. Duplicate presses won’t double-run actions, and long tasks can be tracked safely.
- effort: Medium: relay state model + job record changes + plan/execution plumbing; UI is voice-only.  ·  risk: If lease checks are wrong, tasks could be blocked unnecessarily. Recovery is to bypass lease for reversible reads, or to re-issue with a fresh lease after a timeout.
- cost: Small API overhead per request (lease payload, evidence receipts).  ·  latency: Adds a tiny preflight check; negligible compared to cross-device work.
- security: Improves safety by preventing replay/duplication and ensuring evidence-backed completion.
- depends on: A way to store lease state in the relay job records; Downstream agents returning pre/post evidence receipts


## What it asked for

### `t12-81eu` (tool) — relay_route_intent
- why: The relay needs a safe, explicit routing tool to send normalized intents to downstream agents without inventing ad-hoc protocols in the voice path. It should encapsulate target selection, session binding, and minimal context fields, and return a job reference for status checks.

```json
{
  "type": "object",
  "properties": {
    "intent": {
      "type": "string",
      "description": "Concise intent label, e.g. 'open_app', 'search_web', 'dictation', 'system_status'."
    },
    "utterance": {
      "type": "string",
      "description": "Raw or normalized user utterance to preserve meaning."
    },
    "context": {
      "type": "object",
      "description": "Optional session context such as locale, time, constraints.",
      "additionalProperties": true
    },
    "target": {
      "type": "string",
      "description": "Preferred downstream target agent id, e.g. 'mac-planner' or 'mac-vision'."
    }
  },
  "required": [
    "intent",
    "utterance",
    "target"
  ]
}
```

### `t13-6jyq` (tool) — server_browser_actions
- why: To do useful voice tasks when the owner’s Mac/browser is offline, the relay needs a server-side browser automation capability (Cloudflare Browser Run) for public pages. This reduces dependency on the Mac being online and avoids fragile routing through the browser extension.

```json
{
  "type": "object",
  "properties": {
    "url": {
      "type": "string",
      "description": "Starting URL to open."
    },
    "actions": {
      "type": "array",
      "description": "High-level browser actions to perform (navigate, click, extract, search).",
      "items": {
        "type": "object",
        "additionalProperties": true
      }
    },
    "timeout_ms": {
      "type": "number",
      "description": "Overall timeout in milliseconds."
    }
  },
  "required": [
    "url",
    "actions"
  ]
}
```

