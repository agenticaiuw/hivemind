# Harness derivation — mac-planner — round 18

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "While I’m busy, watch my authenticated dashboards and tell me only when something important changes—like a bill, travel disruption, account alert, or delivery update."
- **useful because:** Turns the pendant into a quiet background assistant instead of requiring repeated manual checks. A hash/diff-based watcher avoids noisy notifications and can deliver a short audio briefing when the owner chooses to listen.
- **path:** dashboard → relay → browser → mac-bridge
- **model tier:** Scheduled/background extraction uses a cheap model (or no model for hashes); a small background model classifies changes. Realtime is used only when the owner asks for a spoken explanation. Browser Run handles server-side public pages; authenticated pages use the Mac browser bridge with origin/session affinity.
- **latency:** Polling every 30–60 minutes is acceptable; each check should finish within 45 seconds. Notification/audio generation can be deferred and batched into the next briefing.
- **cost:** Low: most checks are DOM/text hashes and short bounded extracts. Roughly cents per daily watcher set; cost is dominated by authenticated page extraction and optional TTS, not realtime tokens.
- **security:** Credentials remain in the browser session; extracted text may contain financial or health data and must be redacted before relay storage. Require explicit per-site enrollment, allowed origins, field selectors, retention limits, and confirmation before any action. Never auto-submit forms, pay, cancel, or send messages.
- **missing:** Scheduled watcher/job scheduler with retries and deduplication; Typed browser extraction contract with origin binding and bounded output; Encrypted/redacted snapshot storage and hash/diff engine; Notification/audio queue with offline retry; Per-site consent and pause controls in dashboard

### "Take care of this on my Mac, but show me exactly what you’re about to change before anything irreversible happens."
- **useful because:** Preserves the owner's maximum automation for harmless actions while making deletion, sending, purchasing, account changes, and arbitrary code execution inspectable and stoppable. The current FULL_CONTROL_MODE bypasses actionRisk entirely, so today an accidental plan can cause permanent damage.
- **path:** mac-bridge → dashboard → relay
- **model tier:** A deterministic local policy engine classifies actions; a cheap model summarizes the proposed diff in plain language. Realtime only reads the concise confirmation request and receives the result. No model should decide whether a shell command is safe.
- **latency:** Reversible UI/file actions remain immediate. Irreversible actions pause at a checkpoint, with a 10–30 second approval window and resumable job ID.
- **cost:** Negligible model cost if classification is local; one short summary costs only a few hundred tokens when needed. Engineering cost is primarily executor instrumentation and an approval endpoint.
- **security:** The existing full-control path accepts run_shell/run_applescript and has no approval token. Add deny-by-default for destructive shell, credential access, external sends, purchases, and broad filesystem operations; display exact target, payload, and touched paths. Log receipts with actor, origin, command hash, result, and undo availability. Emergency stop must cancel queued work, though already-running apps may not be reversible.
- **missing:** Make actionRisk mandatory in FULL_CONTROL_MODE; Typed policy/approval endpoint with expiring, single-use tokens; Preflight diff/receipt generation for each action; Job cancellation and timeout propagation; Dashboard and pendant confirmation UX

### "Before each meeting, prepare a two-minute brief from the invite, recent mail, and relevant files; afterward, draft the follow-up and put it in my drafts for review."
- **useful because:** Eliminates repetitive meeting preparation and follow-up while keeping the owner in control of outbound communication. It can arrive as audio on the pendant before the meeting and leave a reviewable draft afterward.
- **path:** mac-bridge → dashboard → relay → pendant
- **model tier:** A cheap background model gathers calendar/mail snippets and local file metadata, then writes the brief and draft. Realtime is only for a last-minute spoken query or clarification. TTS/audio generation runs asynchronously and is cached until played.
- **latency:** Trigger 15–30 minutes before meetings; brief ready within 1–2 minutes. Follow-up draft within 5 minutes after the meeting or on an explicit button press.
- **cost:** Low to moderate: bounded calendar/mail snippets and selected files, with one short generation per meeting. Audio costs are minimized by generating only for meetings marked important and retaining a text version.
- **security:** Mail and files are sensitive. Restrict sources to the meeting's account and explicitly approved folders; redact unrelated content and cap excerpts. Never send or modify calendar/mail automatically. Creating a draft is reversible, but require confirmation before sending and show recipients, attachments, and body exactly.
- **missing:** Meeting-to-source relevance selection and folder allowlists; Reliable meeting-end trigger or explicit pendant button; Asynchronous TTS/audio queue and playback receipt; Draft creation API with recipient/attachment preview; Retention and redaction policy for generated briefs


## Changes it proposed to its own stack

### `model-routing` — Introduce a three-tier planner pipeline: deterministic intent/action compiler for simple desktop commands; cheap background model for multi-step planning, extraction, and scheduled work; realtime model only for live ambiguity resolution and spoken summaries. Add a compact per-job context packet drawn from the graph instead of injecting the whole fleetContext prompt on every turn.
- **owner gets:** Routine tasks become cheaper and faster, while live conversation stays responsive. The assistant can run several jobs at once without making the owner wait or paying realtime rates for background work.
- effort: Medium: define typed job intents, routing rules, compact context schema, and fallback to realtime when confidence is low.  ·  risk: A cheap model may misunderstand a high-impact request. Enforce confidence thresholds and route any destructive or ambiguous plan to deterministic policy plus explicit confirmation; retain the current realtime fallback.
- cost: Likely materially lower token/audio spend for routine tasks; small routing overhead. No hardware cost.  ·  latency: Simple actions become near-instant; background tasks can be asynchronous; only ambiguous requests incur realtime latency.
- security: Smaller context packets reduce unnecessary exposure of private memory. Routing must preserve tenant/account scope and never pass secrets into prompts.
- depends on: Typed mac/browser action schemas; Job IDs, progress, cancellation, and receipts; Per-surface compact context projection

### `dashboard-ux` — Add a unified job inbox showing queued/running/paused/completed work across relay, Mac, and browser. Each job displays source, progress, exact effects, touched resources, reversibility, cost estimate, and an audio/text result; paused irreversible steps expose approve, edit, or cancel. Include per-site watcher consent and a one-tap global pause.
- **owner gets:** The owner can delegate work without wondering whether it ran, what it changed, or where the result is. They can review asynchronous work from the pendant companion, menubar, web, or iOS without repeating requests.
- effort: Medium-high: shared job event schema, receipt UI, cross-surface synchronization, and cancellation/approval endpoints.  ·  risk: Too much status detail could expose private content or overwhelm the owner. Default to summaries with redacted previews, expand on demand, and enforce account-scoped access. A global pause must be reliable and clearly indicate jobs already in progress.
- cost: Small dashboard/storage cost; lower model cost by avoiding repeated status questions and regenerating context. No hardware cost.  ·  latency: Status updates should stream within seconds; results remain asynchronous. Approval actions need low-latency delivery to the waiting Mac/browser job.
- security: Receipts may contain sensitive paths, recipients, and snippets. Encrypt or redact them, use short-lived approval tokens, and log access. Never place secrets in notification text.
- depends on: Typed cross-agent job/event schema; Cancellation and approval endpoints; Mac/browser effect receipts; Compact per-surface context projection


## What it asked for

### `t9-e7fl` (tool) — mac_action_preflight
- why: FULL_CONTROL_MODE currently executes arbitrary desktop actions without actionRisk or confirmation. Before executing a server plan, the planner needs a read-only deterministic classification, touched-resource list, reversibility assessment, and exact preview so irreversible actions can be gated.

```json
{
  "type": "object",
  "properties": {
    "actions": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "type": {
            "type": "string"
          },
          "app": {
            "type": "string"
          },
          "path": {
            "type": "string"
          },
          "url": {
            "type": "string"
          },
          "content": {
            "type": "string"
          },
          "destination": {
            "type": "string"
          },
          "key": {
            "type": "string"
          },
          "modifiers": {
            "type": "array",
            "items": {
              "type": "string"
            }
          },
          "text": {
            "type": "string"
          },
          "shortcut": {
            "type": "string"
          }
        },
        "required": [
          "type"
        ]
      }
    },
    "dry_run": {
      "type": "boolean",
      "const": true
    }
  },
  "required": [
    "actions",
    "dry_run"
  ]
}
```

