# Harness derivation — faculty-judgement — round 34

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Why are you suggesting this, and what exactly will happen if I say yes?” (Also: “Stop using that source for this.”)"
- **useful because:** The owner can trust a multi-surface assistant without having to remember which machine saw what. For any reminder, brief item, draft, or proposed action, the system gives a short spoken explanation tied to the original evidence, freshness, confidence, policy, and intended side effects; it can immediately revoke that source or permission for the current task. This is a user-facing accountability loop, not just an internal log.
- **path:** relay-realtime → pendant → faculty-perception → faculty-judgement → faculty-action → mac-planner → browser-extension → unified
- **model tier:** Use gpt-5.6-luna for provenance reconciliation and policy interpretation; use gpt-realtime-2.1 only to answer the live spoken question and collect a yes/no/revoke response. No model call for static receipt rendering.
- **latency:** Spoken explanation starts within 500 ms from cached receipt metadata; deeper cross-surface evidence reconciliation under 3 s. Revoke takes effect before any subsequent action, with a durable confirmation receipt.
- **cost:** Roughly $0.01–$0.05 per explanation depending on whether fresh browser/Mac evidence must be gathered; most requests should use cached typed receipts and cost under $0.01. Realtime cost is limited to the short dialogue.
- **security:** Private URLs, snippets, and account names must remain on-device or in redacted provenance tokens; never read secrets aloud by default. Revoke must be fail-closed and scoped (source, task, or globally), with explicit confirmation for global changes. The assistant must distinguish observed evidence from inference and show age/uncertainty.
- **missing:** A signed, cross-surface provenance receipt schema linking observations, transformations, policy decisions, and intended side effects; A user-facing revoke/denylist store enforced by browser, Mac, relay, and scheduled-job runners before reads and writes; A pendant/relay route for ‘explain’, ‘source’, and ‘revoke’ with concise spoken rendering; A cross-surface audit query that can prove which evidence was actually used, not merely which evidence was available


## Changes it proposed to its own stack

### `integration` — Introduce a signed Evidence-to-Effect (E2E) envelope shared by relay, faculty, Mac, browser, and scheduled jobs. Each envelope records observation IDs and redacted source pointers, timestamp/freshness, transformations and confidence, policy decisions, proposed side effects, approval token, and final outcome. The action runner must verify the envelope signature, scope, expiry, and revocations before every write; the relay can render a one-sentence explanation from it and the Mac dashboard can show the full chain. Store only hashes/redacted pointers in relay; retain sensitive snippets locally on Mac/browser.
- **owner gets:** When the assistant makes a surprising suggestion or a task goes wrong, the owner can immediately understand what it relied on and stop that source from influencing future actions. This turns opaque automation into something they can safely delegate to every day.
- effort: Medium-high: define schema and signing keys, add middleware to action/job/browser runners, implement local sensitive evidence store, and add spoken/dashboard renderers plus scoped revocation propagation.  ·  risk: Schema or signature bugs could block legitimate actions; recover by fail-open only for read-only explanations and fail-closed for writes, with versioned envelopes and a local emergency disable. Stale revocation caches are a safety risk, so each write needs a short-lived lease and relay connectivity check.
- cost: Negligible per-request compute/storage; roughly 0.5–2 KB metadata per action and one inexpensive reconciliation call only when the owner asks for explanation. Engineering cost is the main cost.  ·  latency: Under 10 ms local verification; up to 100–300 ms for revocation lookup. Cached explanation is immediate; fresh evidence collection remains task-dependent.
- security: Improves least-privilege and auditability, but introduces signing-key and provenance-linkage sensitivity. Keep keys in OS keychain, rotate them, redact account content, and never expose raw secret values to relay or model prompts.
- depends on: A typed cross-surface context/provenance service rather than hand-written fleet prompts; Durable job/action receipts and browser request IDs; A revocation/denylist primitive enforced by every action backend; Pendant/relay spoken explanation and revoke routes

### `hardware` — Add a true hardware privacy control to the pendant: a latching side switch (or mechanically distinct long-press button) that cuts microphone power/data before firmware, drives a bright local red indicator, and emits a signed privacy-state event when connectivity returns. Relay, Mac agent, browser bridge, scheduled jobs, and any active audio pipeline must treat that state as an absolute no-capture/no-transcription lease; on unmute, the pendant announces the transition locally and the system records a gap rather than pretending continuity.
- **owner gets:** The owner can be certain that a private conversation is private, even if software is stuck, a job is running, or the network reconnects unexpectedly. They get one physical action that overrides every surface, plus an honest record of what the assistant could not hear.
- effort: High: revise pendant PCB/enclosure and power path, add debounce and indicator, firmware state/signing, and a fail-closed privacy lease enforced by relay, Mac, browser, and queued-job consumers. Existing devices need a compatibility mode that stops capture as soon as the event arrives.  ·  risk: A damaged or ambiguous switch could leave the owner muted or falsely indicate privacy; use normally-closed sensing, boot-time self-test, unmistakable indicator, and a local audible/tactile confirmation. Fail closed on state uncertainty. Emergency recovery is a deliberate physical toggle plus visible state check.
- cost: Roughly $2–$8 incremental components/enclosure work per pendant and negligible steady-state power; engineering and PCB revision dominate. No model/API cost.  ·  latency: Local mic cut is immediate (hardware propagation); remote consumers stop within one event round-trip, typically under 300 ms. Reconnect must not replay buffered audio recorded during privacy mode.
- security: Strongly improves protection against accidental capture and compromised software, but signed state keys and event handling become security-critical. Never let a remote command clear hardware mute; privacy state must be monotonic until local release.
- depends on: A cross-surface privacy-state protocol and durable gap receipts; Audio pipeline changes so buffering and retry queues honor hardware mute; Relay/Mac/browser enforcement middleware that rejects capture while the privacy lease is active


## What it asked for

### `t13-5tzh` (tool) — explain_action_provenance
- why: The owner needs an immediate, trustworthy answer to ‘why did you suggest/do this?’ and the ability to revoke a source. Existing receipts are completion records, not a verified chain from evidence through judgement to effect.

```json
{
  "type": "object",
  "required": [
    "action_or_item_id",
    "mode"
  ],
  "properties": {
    "action_or_item_id": {
      "type": "string",
      "description": "Receipt, job, briefing item, reminder, or proposal identifier."
    },
    "mode": {
      "type": "string",
      "enum": [
        "explain",
        "list_sources",
        "revoke_source",
        "revoke_task"
      ],
      "description": "Explain the evidence chain or apply a scoped revocation."
    },
    "source_id": {
      "type": "string",
      "description": "Required for revoke_source."
    },
    "confirmation_token": {
      "type": "string",
      "description": "Required for revocation writes; generated by a prior explanation response."
    },
    "include_sensitive": {
      "type": "boolean",
      "default": false,
      "description": "Only local dashboard may request true; spoken relay must reject it."
    }
  }
}
```

## Its own summary

Discovered the owner’s current reality (Mac online, browser offline; repeated failed private-account requests; short spoken replies; destructive actions require confirmation) and the existing backlog. Added a new accountability layer: an owner-facing ‘why did you suggest/do this?’ and scoped ‘stop using that source’ capability, backed by signed Evidence-to-Effect envelopes across pendant, relay, faculty, Mac, browser, and scheduler. Proposed the integration change and queued explain_action_provenance.

**Biggest unknown:** Whether the current job/action and browser receipt implementations already preserve enough observation-level provenance to populate the envelope, or only final outcomes. I still need the orchestrator’s pending cross-surface persistence/context details and implementation of the queued provenance query/revocation tool.

