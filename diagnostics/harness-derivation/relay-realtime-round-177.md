# Harness derivation — relay-realtime — round 177

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Tell me what happened with the thing I asked my Mac to do, and if it finishes later, let me know without me asking again."
- **useful because:** This removes the awkward polling loop. The owner can ask for status now, and also get a completion notification later if a long-running task finishes after the conversation ends.
- **path:** relay → mac-bridge → pendant
- **model tier:** relay for live status; mac-bridge for executing tasks; a cheaper background tier for completion monitoring
- **latency:** Status check should respond in under a second when possible; completion alerts can arrive minutes later.
- **cost:** Low for status reads (no Mac round trip); completion monitoring costs a small background check per job.
- **security:** Only job metadata and a short spoken summary leave the Mac; do not include sensitive content in the spoken notification.
- **missing:** A working event delivery path from relay to pendant/phone after session end; Background job watcher to trigger events without a live conversation

### "When I’m away from my Mac, keep working on the multi-step task I asked for and summarize the result when it’s done."
- **useful because:** It turns the system into a true assistant: the owner can hand off a complex job and walk away, then get a digest later.
- **path:** relay → mac-bridge → browser → pendant
- **model tier:** mac-planner for multi-step work; relay for short spoken updates; background tier for monitoring
- **latency:** Immediate acknowledgment in under a second; the task itself can run as long as needed.
- **cost:** Medium: planning and browser work dominate; monitoring adds small periodic checks.
- **security:** Browser work may touch authenticated sessions; summaries should redact or generalize sensitive content.
- **missing:** Durable background monitoring/scheduler; Reliable completion notification channel to pendant/phone; Typed result receipts for summaries if not already available

### "Remember this preference for how you should behave in similar situations, and don’t make me repeat it every session."
- **useful because:** Reduces friction. The owner can set preferences once (e.g., verbosity, default apps, notification style) and the system adapts across turns and devices.
- **path:** relay → mac-bridge → dashboard
- **model tier:** cheaper background tier for storage and retrieval; relay only for the immediate confirmation
- **latency:** Under a second to confirm; storage can be asynchronous.
- **cost:** Low per update; dominated by storage writes and retrieval when sessions start.
- **security:** Preferences may reveal habits; store minimally and encrypt at rest.
- **missing:** Shared, durable preference store accessible to relay and Mac; Context projection mechanism to avoid re-sending full preference data each turn

### "“Compare the same thing across my open browser tabs, Mac documents, and calendar, and tell me where they disagree—with the exact evidence and what I should verify.”"
- **useful because:** The current agents can inspect individual surfaces, but the owner cannot ask for a cross-surface consistency check. This catches mismatched dates, prices, names, versions, and commitments before the owner acts, especially when the relevant evidence is split between an authenticated browser session and local files.
- **path:** pendant → relay → browser-extension → mac-planner → mac-vision → faculty-perception → faculty-judgement
- **model tier:** Cheaper background perception workers extract normalized claims and provenance; judgement compares claims; realtime relay only presents the concise disagreement and answers follow-up questions.
- **latency:** Return an initial spoken result in 10–20 seconds for up to five sources; provide additional evidence on request.
- **cost:** Roughly $0.03–$0.20 per check, dominated by screenshots/page extraction and provenance-bearing model context; reuse hashes and extracted claims within a session to avoid resending unchanged content.
- **security:** Data leaves the Mac/browser only for this explicit request. Keep source-specific ACL/session identifiers, redact unrelated page regions, and speak claims rather than dumping private documents. No mutation is performed.
- **missing:** A provenance-preserving claim extraction schema shared by browser and Mac agents; A cross-surface comparison worker and contradiction ranking; A compact spoken-plus-drill-down evidence format for the pendant; Stable tab/document identity and snapshot timestamps

### "“Before you act on a consequential request, have two independent agents inspect the relevant Mac/browser state, tell me if they disagree, and proceed only with the interpretation I choose.”"
- **useful because:** A single planner can confidently misread a page, stale tab, or ambiguous voice instruction. The owner gets a compact disagreement report instead of discovering an interpretation error after an action. This uses the hive's genuinely different viewpoints rather than pretending one model has perfect context.
- **path:** pendant → relay → faculty-perception → faculty-judgement → mac-planner → mac-vision → browser-extension → faculty-action
- **model tier:** Two cheap independent perception passes (one DOM/text-oriented and one visual/local-file-oriented), followed by faculty-judgement to identify material disagreement; realtime relay speaks only the disputed alternatives and collects the owner's choice.
- **latency:** 2–6 seconds for a read-only disagreement check; up to 15 seconds when screenshots and local files are needed. No action starts until the selected interpretation is recorded.
- **cost:** Approximately $0.04–$0.25 per check, mostly duplicate perception context and screenshots; use it selectively for requests marked consequential or ambiguous rather than every utterance.
- **security:** Independent agents must receive the minimum relevant slices, with source and timestamp attached. The relay must not manufacture consensus from correlated outputs. The owner choice and both evidence sets should be retained in the job receipt; no new blanket confirmation policy is implied.
- **missing:** A fan-out coordinator that requests independent observations with isolated prompts; A typed disagreement object with evidence pointers and materiality score; A pendant-friendly choice response (numbered alternatives) correlated to the active job; An action barrier that accepts only the selected interpretation


## Changes it proposed to its own stack

### `model-routing` — Introduce a cheap background model tier for monitoring and summarizing job progress, leaving the relay model for low-latency speech only.
- **owner gets:** Keeps live conversations snappy while still providing rich follow-ups for longer tasks.
- effort: Medium. Requires routing logic and job ownership rules.  ·  risk: Inconsistent summaries if multiple tiers race; mitigate by centralizing job state reads and using receipts.
- cost: Reduces expensive relay usage by shifting monitoring to cheaper compute.  ·  latency: Improves perceived responsiveness for live voice; background work can be slower.
- security: Background tier must respect the same data minimization and access controls.
- depends on: Job-state watcher and event pipeline

### `context` — Add a small shared preference and session-memory projection: store owner preferences once, then project only relevant keys into each session to avoid resending bulk context.
- **owner gets:** The system feels consistent and personalized without repeating setup every turn, and it saves cost.
- effort: Medium. Needs a schema, storage, and projection rules.  ·  risk: Stale preferences causing surprising behavior; mitigate with versioning and explicit user confirmation when changing defaults.
- cost: Low per request; saves tokens over time by reducing repeated context.  ·  latency: Minimal; retrieval can be cached.
- security: Preferences reveal habits; encrypt at rest and restrict access.

### `interaction` — Add a pendant-native 'conversation lease' protocol: every spoken request receives a short lease token; the relay, Mac planner, and browser agent attach that token to intermediate observations, and the pendant can say “continue,” “cancel,” or “use the other option” while the task is still running. The relay must reject late observations from an expired or cancelled lease and announce which lease is active when multiple jobs overlap.
- **owner gets:** The owner can safely start several things by voice and steer the right one without repeating the whole request or accidentally answering a stale question. It makes the pendant feel like a persistent control surface rather than a push-to-talk microphone.
- effort: Medium-high: protocol fields across relay/Mac/browser, a small active-job selector in firmware, and race-condition tests for reconnects and late results.  ·  risk: A dropped packet or ambiguous short answer could attach to the wrong task. Recover by speaking the active task label, requiring an explicit lease token for destructive steering, and expiring leases conservatively. Existing one-button/one-LED hardware needs a spoken selector rather than new controls.
- cost: Negligible per-request API cost; modest Worker and agent state storage. No new hardware required.  ·  latency: Adds under 300 ms for token routing; avoids much larger latency from restarting a task.
- security: Improves isolation between concurrent jobs, but lease tokens must be unguessable and scoped to the owner/session; do not expose them in spoken output.
- depends on: A durable resumable job/checkpoint state machine; A relay-to-pendant asynchronous message path; Consistent job IDs and receipts across POST /plan and POST /execute


## What it asked for

### `t21-gxpu` (tool) — job_completion_watch
- why: We need a real way to monitor jobs and emit completion events after the voice session ends, without the relay inventing a protocol.

```json
{
  "type": "object",
  "properties": {
    "jobId": {
      "type": "string"
    },
    "onState": {
      "type": "string",
      "enum": [
        "complete",
        "failed",
        "needs_attention"
      ]
    },
    "summaryStyle": {
      "type": "string",
      "enum": [
        "short",
        "detailed"
      ]
    },
    "ttl_seconds": {
      "type": "integer"
    },
    "deliveryTargets": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": [
          "pendant",
          "phone",
          "dashboard"
        ]
      }
    }
  },
  "required": [
    "jobId",
    "onState",
    "deliveryTargets"
  ]
}
```

### `c19-1pig` (context) — shared preference store and session memory projection
- why: I proposed remembering preferences once and projecting only relevant keys into sessions, but this depends on whether a shared store already exists and how session context is injected.
- would change: If a store exists, I’ll specify the schema and projection rules to fit it; if not, I’ll propose a minimal storage layer and injection point.

## Its own summary

Recorded three new directions: (1) cross-surface contradiction checking with provenance across authenticated browser tabs, Mac documents, and calendar; (2) a conversation-lease protocol so spoken steering/cancel commands cannot attach to stale or concurrent jobs; and (3) independent perception agents that surface material disagreement before consequential action. A proposed clarification-loop capability collided with an existing backlog item and was not recorded, so I did not rephrase it.

**Biggest unknown:** Whether the relay's existing event-push route can actually deliver a correlated, bidirectional question/answer exchange to the pendant; the tool is granted but side-effect execution is unresolved. The recorded ideas need durable cross-agent state, provenance/disagreement schemas, and reliable asynchronous pendant delivery.

