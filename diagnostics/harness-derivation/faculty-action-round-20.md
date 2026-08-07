# Harness derivation — faculty-action — round 20

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Do this everywhere it needs doing, and only tell me it’s done when you can prove each part succeeded.”"
- **useful because:** Today judgement can decide a multi-surface plan and Mac/browser can return action receipts, but there is no shared commit protocol. A browser mutation can succeed while the Mac-side follow-up fails, or a stale page can make a receipt look successful. This capability turns a goal into a durable execution manifest: relay assigns one operation ID; Mac and authenticated browser steps acquire leases and report typed results; faculty-perception independently checks each postcondition from fresh UI/state; the relay records a dependency graph and compensating actions; the pendant gives one concise outcome, with the exact failed step and a safe retry/resume option. The owner gets truth rather than optimistic “done,” and a dropped Mac connection does not lose the operation.
- **path:** faculty-judgement emits a versioned manifest containing steps, dependencies, preconditions, postconditions, sensitivity, approval checkpoints, and compensation hints → relay persists the manifest, leases, event log, and resumable state; routes Mac and authenticated browser work and de-duplicates retries by operation/step IDs → mac-planner/mac-vision executes typed Mac actions and returns before/after evidence; browser-extension performs private-tab actions with URL/tab affinity and evidence → faculty-perception independently re-reads the relevant Mac state or browser page after each mutation and marks postconditions proven/unproven/unknown → relay-realtime speaks a short success or failure receipt through the pendant; on unknown or high-risk divergence it requests an owner decision, with the single button serving as approve-retry/cancel while the full evidence remains in dashboard
- **model tier:** Use the cheaper background model for manifest compilation, event reconciliation, and postcondition extraction; reserve realtime only for the owner's spoken request, ambiguity, and the final exception/approval exchange. Use deterministic validators for hashes, URLs, file existence, and typed browser fields rather than spending model tokens.
- **latency:** Immediate acknowledgement under 1 second from relay; reversible local steps usually complete in 2–10 seconds; verification adds one fresh read per mutation (roughly 1–3 seconds). Long jobs continue in the relay and surface a completion or exception later, without requiring the owner to stay connected.
- **cost:** Approximately $0.01–$0.08 per ordinary multi-step operation using background extraction/validation; dominant costs are browser/Mac round trips and occasional vision or realtime turns, not the durable event log. Deterministic checks are near-zero model cost.
- **security:** The manifest must be capability-scoped and signed/bound to the requesting session, with step-level sensitivity and explicit approval for irreversible sends, purchases, deletes, or external messages. Evidence may contain private page text or file contents, so retain only hashes/snippets by default and encrypt sensitive evidence; expire it separately from the operation record. Never infer success from an executor HTTP 200 alone. On lease expiry, stale precondition, conflicting external change, or unverifiable postcondition, stop rather than retry blindly. Provide an append-only audit trail and compensating undo where valid.
- **missing:** A shared operation/step event schema and durable state machine spanning relay, Mac harness, browser bridge, perception, and judgement; A relay lease/heartbeat and idempotency protocol with resume-after-disconnect semantics; A first-class postcondition verifier API that can request fresh browser snapshots, Mac state reads, or typed filesystem/app checks; Manifest-level approval checkpoints and a pendant button/server-push result path, including explicit unknown/needs-owner states; Evidence normalization (before/after references, provenance, timestamps, hashes) and a dashboard timeline that presents dependency failures and safe recovery options

### "“When I arrive at [place], have everything ready for me—but don’t change or send anything until I confirm on the pendant.”"
- **useful because:** The owner cannot currently have a trustworthy physical-context handoff. The pendant is always with them, the phone can know location, the relay can wait while the Mac sleeps, and the Mac/browser can prepare private work—but there is no shared trigger, staged preparation, or local confirmation boundary. This would let a real-world event start useful work without prematurely sending messages, submitting forms, or exposing private content. For example, arrival at an airport could cause the relay to ask the Mac to collect the owner’s itinerary and open the relevant private tabs, while the pendant announces only that a ready packet exists; a deliberate button press releases the final action.
- **path:** iOS/phone location service detects a user-defined geofence or Bluetooth/Wi-Fi place identity and sends a signed arrival event to the relay → relay applies quiet hours, freshness, privacy, and rate-limit policy; starts a staged job and retains it durably if the Mac or browser is offline → Mac planner and browser bridge gather the allowed private context, prepare reversible drafts/open tabs/files, and return evidence without submitting or sending → faculty-judgement evaluates the staged packet against the trigger and asks for approval only for the final side effect → pendant receives a minimal local prompt such as 'Airport packet ready'; button press approves the named operation, while timeout, departure, or a second press cancels/locks it; relay then dispatches the approved Mac/browser action and reports outcome
- **model tier:** Use deterministic geofence/event policy and a cheap background model for packet preparation and summarization. Use the realtime tier only if the owner asks a follow-up question or the trigger requires spoken disambiguation; do not spend realtime tokens on routine arrival events.
- **latency:** Arrival event to a ready packet in 10–60 seconds depending on Mac/browser availability. Pendant confirmation must be local and immediate; final dispatch acknowledgement under 2 seconds, with long work continuing asynchronously.
- **cost:** Roughly $0.01–$0.05 per triggered packet, dominated by private-page extraction and any vision step; geofence events, relay persistence, and deterministic policy are negligible. A daily rate limit and deduplication prevent location chatter from becoming API spend.
- **security:** Location history is highly sensitive: keep only coarse place IDs and event timestamps, encrypt them, and expire raw coordinates immediately. Each geofence must be explicitly configured with permitted data sources and actions; never trigger external sends, purchases, deletes, or unlocks automatically. Bind the approval token to the exact staged manifest, expire it quickly, prevent replay, and require a visible spoken/LED indication of what will happen. If location is uncertain, the phone is spoofed, the owner departs, or private sessions are unavailable, do nothing and say why.
- **missing:** A privacy-preserving iOS location/geofence client and signed arrival-event protocol; Relay-side staged-job and expiring approval-token state, with deduplication and quiet hours; A pendant local confirmation/result protocol that survives a transient network drop and clearly distinguishes ready, approved, cancelled, and failed; Cross-surface policy tying each place trigger to an allowlisted data scope and action manifest; Mac/browser preparation mode that can collect evidence and draft/open reversible artifacts without accidentally committing side effects


## Changes it proposed to its own stack

### `relay` — Implement an operation journal and commit state machine shared by judgement, action, and perception. Persist Operation {operationId, manifestHash, requester/session, status}; Step {stepId, dependency IDs, lease token/expiry, precondition result, executor receipt, postcondition result, evidence refs, compensation}; and append-only events. Expose claim/heartbeat/complete/verify/resume endpoints with idempotency on operationId+stepId, optimistic version checks, and a reconciler that marks disconnected leases as paused rather than replaying them. Completion must require an independent verifier result for every postcondition; otherwise status is needs-review. Add a deterministic verifier adapter for common Mac/browser facts and a signed final receipt consumed by relay-realtime and the dashboard.
- **owner gets:** When the owner asks for a chain of changes across private browser tabs and the Mac, the system can resume safely after sleep or a dropped connection and can distinguish 'executor returned' from 'the intended result is visibly true.' Failures become one actionable exception with a safe resume/undo path instead of silent partial completion.
- effort: Medium-high: shared schema and D1 migrations, relay endpoints and worker reconciler, local-agent claim/heartbeat adapter, browser bridge evidence adapter, and perception verifier integration; then fault-injection tests for duplicate delivery, stale pages, lease expiry, and partial completion.  ·  risk: A bug in dependency or version handling could pause valid work or, worse, duplicate a side effect. Default all unknown/stale/conflicting states to pause; require idempotency keys and manual approval for irreversible steps. Keep the current executor path as a compatibility fallback and migrate one reversible workflow first.
- cost: Small D1/event-storage increase; evidence should be content-addressed and short-lived in R2. Background model calls for semantic verification are the main API cost; hashes, URL checks, and typed field comparisons are effectively free.  ·  latency: Adds one verification read after each mutation and heartbeat traffic for long steps; no added latency to simple read-only replies. Relay acknowledgement remains immediate while execution is asynchronous.
- security: Improves auditability and limits replay, but manifests and evidence become sensitive durable records. Bind leases to authenticated device/session, sign final receipts, encrypt sensitive evidence, redact page text by default, and enforce per-step approval policy before dispatch.
- depends on: A typed action receipt format that includes provenance and before/after references; A perception endpoint/tool able to request fresh Mac and browser observations; Durable browser job runner and authenticated browser session affinity; A server-push/result path to relay-realtime and a pendant approval interaction

### `integration` — Add a privacy-preserving place-trigger service spanning the iOS client, relay, Mac agent, browser bridge, and pendant: iOS converts approved geofences into coarse signed place-arrival events (never uploads continuous coordinates); relay deduplicates and starts a staged, allowlisted preparation job; Mac/browser run read-and-draft-only actions; relay creates a short-lived approval token bound to the exact manifest; the pendant displays a minimal ready state and requires a deliberate button event before the final action is released. Expire or cancel the token on departure, timeout, stale private-page evidence, or changed manifest.
- **owner gets:** The owner can walk into a place and have the relevant work ready without needing to remember to ask, while retaining a clear physical boundary before anything consequential is sent or changed. It makes the wearable, phone, always-on relay, private browser, and Mac cooperate in a way no single device can provide.
- effort: High: iOS native geofence/background delivery, relay event and token persistence, staged Mac/browser execution mode, pendant result/approval protocol, dashboard configuration UI, and end-to-end spoofing/offline/timeout tests.  ·  risk: False or spoofed location could start private preparation or cause notification fatigue; it must never authorize the final side effect. Use coarse place IDs, signed events, deduplication, quiet hours, per-trigger budgets, and default cancellation. If the pendant is disconnected, leave the packet staged and do not auto-commit.
- cost: Low ongoing storage and event cost; approximately $0.01–$0.05 per preparation run for background extraction, with no realtime call unless the owner engages. iOS implementation and QA are the dominant engineering cost.  ·  latency: Background geofence delivery is platform-dependent; target 10–60 seconds from arrival to ready packet. Button approval is immediate, and final dispatch acknowledgement should be under 2 seconds.
- security: Introduces location and trigger metadata, so store coarse place identifiers only, expire event details, encrypt staged private evidence, bind approval tokens to a manifest hash and device/session, and audit every trigger and approval. Require explicit setup and per-trigger scope; no silent external communication.
- depends on: iOS background location/geofence integration; Relay staged-job and expiring approval-token state; Pendant firmware/server-push status and local confirmation handling; Mac/browser read-and-draft-only preparation mode; Per-place privacy/action policy and dashboard configuration


## What it asked for

### `t21-8d1c` (tool) — verify_operation_step
- why: The proposed commit protocol cannot honestly close an operation from executor receipts alone. faculty-action needs a read-only verifier call to faculty-perception that independently checks a specific step's postconditions against fresh Mac/browser state and returns provenance, without opening a microphone or performing mutations.

```json
{
  "type": "object",
  "properties": {
    "operation_id": {
      "type": "string"
    },
    "step_id": {
      "type": "string"
    },
    "postconditions": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "kind": {
            "type": "string",
            "enum": [
              "app_state",
              "file_state",
              "browser_field",
              "browser_url",
              "message_draft",
              "generic"
            ]
          },
          "expected": {
            "type": "string"
          },
          "locator": {
            "type": "string"
          },
          "sensitivity": {
            "type": "string",
            "enum": [
              "normal",
              "private",
              "secret"
            ]
          }
        },
        "required": [
          "kind",
          "expected"
        ]
      }
    },
    "evidence_mode": {
      "type": "string",
      "enum": [
        "hash_only",
        "minimal_snippet",
        "full"
      ],
      "default": "hash_only"
    }
  },
  "required": [
    "operation_id",
    "step_id",
    "postconditions"
  ]
}
```

## Its own summary

I discovered the current fleet still has only executor receipts/undo and browser/Mac action tools; no shared operation state machine or independent proof of postconditions. I proposed a new cross-surface capability and relay change: durable operation manifests, dependency-aware leases, idempotent resume, fresh faculty-perception verification, pause-on-unknown, and a signed final receipt delivered through relay/pendant. I also requested a read-only verify_operation_step tool so action cannot claim success from HTTP 200 alone. What I still need is that verifier tool, a shared operation/step event schema plus relay lease endpoints, and a pendant/server-push approval/result path; no additional owner context is needed to define the gap.

**Biggest unknown:** Whether faculty-perception can currently expose fresh, provenance-bearing Mac and authenticated-browser observations quickly enough for postcondition checks; without that, the protocol must conservatively return needs-review rather than claim completion.

