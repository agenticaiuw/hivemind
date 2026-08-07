# Harness derivation — faculty-action — round 33

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When you tell me to do something important, prepare it, show me the exact target and expected result on my pendant, and only carry it out if I confirm before the plan expires; if the page, file, or person changed meanwhile, stop and ask again."
- **useful because:** Prevents a stale judgement from changing the wrong account, document, recipient, or GUI state. It is genuinely hive-native: perception on the Mac/browser supplies a fresh target proof, judgement creates the plan, the relay holds the lease while the owner is away, and the pendant is the final confirmation and failure channel.
- **path:** faculty-judgement → faculty-perception → mac-planner → mac-vision → browser-extension → relay-realtime → pendant
- **model tier:** Use the cheaper background model for plan compilation and target-diff summaries; use realtime only for the spoken confirmation and terse result. No model should decide whether a proof hash matches; that is deterministic code.
- **latency:** Prepare in 1–3 seconds; confirmation feedback under 500 ms when relay/Mac are online; after confirmation, execute within 10 seconds or report lease expiry. A disconnected pendant leaves the lease queued durably rather than executing silently.
- **cost:** Usually <$0.01 per invocation when a compact deterministic diff is used; dominant cost is one small judgement/summary call, not realtime audio. Screenshots or large page extracts should be hashed locally and sent only when needed.
- **security:** The lease must contain target identity, surface/session/tab, normalized precondition hash, expected postcondition, expiry, privacy class, reversibility, and confirmation nonce. Never transmit page secrets in the pendant prompt; display redacted recipient/domain and change summary. Irreversible actions require explicit press-and-hold or two presses; cancellation and expiry must be idempotent. Send only hashes and minimum evidence to relay; retain full evidence locally with bounded TTL.
- **missing:** Typed ActionProof/ActionLease schema shared by judgement, perception, Mac/browser executors, relay, and pendant; Deterministic precondition/postcondition verifier that runs after execution and returns VERIFIED, FAILED, or UNKNOWN; Relay durable lease queue with expiry, nonce replay protection, and pendant delivery/ack receipts; Pendant UI/firmware affordance for redacted diff plus confirm/cancel/expired states; Executor gate that refuses execution when the proof is stale or target affinity is lost; Fresh post-action perception request tied to the same target and attempt ID

### "When I press and hold the pendant as I leave my desk, put my digital workspace into privacy mode: lock the Mac, pause screen sharing and recording, close or blur sensitive browser tabs, stop any pending computer-use loop, and tell me on the pendant exactly what was secured. When I return and press again, restore only the approved workspace—not passwords, submitted forms, or private tabs that were intentionally closed."
- **useful because:** The owner gets a physical, dependable privacy boundary without finding the Mac or speaking aloud in a public place. It uniquely combines the pendant's physical presence and offline button, the always-awake relay's intent and audit trail, the Mac's lock/screen controls, and the browser's authenticated tab/session reach. No single node can provide that boundary safely.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-judgement
- **model tier:** Use deterministic policy and OS/browser APIs for locking, pausing, and tab handling; use a cheap background model only to classify currently open surfaces into sensitive/non-sensitive when the owner has enabled that policy. Realtime is unnecessary except for an optional spoken confirmation.
- **latency:** Physical press acknowledgement under 300 ms locally; Mac privacy actions within 2 seconds; relay records completion within 5 seconds. If disconnected, the pendant still enters local 'privacy requested' state and retries; it must never claim the Mac is secured until receipt arrives.
- **cost:** Near-zero model cost for configured app/domain rules; under $0.01 only when semantic classification of an unfamiliar tab is needed. Main cost is implementation and OS/browser integration, not inference.
- **security:** The action must fail closed: uncertain sensitive classification means leave the tab open but lock the Mac and report it. Never transmit page contents or credentials to the relay. Require a deliberate long press, bind restore to the same device/session identity, maintain an append-only local audit receipt, and never auto-reopen authenticated pages or undo irreversible user actions. Screen recording must be explicitly stopped through approved APIs, with a visible report if permission is unavailable.
- **missing:** Pendant firmware state machine for offline privacy-mode trigger and retry/result indication; Authenticated relay endpoint for privacy-mode intents, receipts, and replay-resistant device identity; Mac privileged-but-minimal privacy controller for lock, screen-sharing/recording pause, and stopping active automation loops; Browser bridge commands to classify, blur, suspend, or close tabs with an owner-defined restore policy; A policy store mapping apps/domains to sensitive, suspendable, closeable, or never-touch categories; Cross-node completion receipt that distinguishes secured, partially secured, and unable-to-secure states


## Changes it proposed to its own stack

### `relay` — Add an ActionLease service implementing a two-phase commit for owner-approved actions. A lease stores actionId, target/surface affinity, precondition digest, expected postcondition, privacy class, reversibility, confirmation nonce, deadline, and attempt number. The relay durably queues only the redacted lease, sends it to the pendant, rejects replay/late confirmations, and forwards a commit token to the Mac/browser executor. The executor must acquire the token, re-perceive the same target, execute, then submit before/after evidence; a verifier returns VERIFIED, FAILED, or UNKNOWN. On timeout, disconnect, target drift, or UNKNOWN, the lease expires without action and the pendant receives a durable alert.
- **owner gets:** An instruction like “send this to Alex” cannot accidentally go to the wrong Alex or a changed web form while the owner is away. The owner gets a clear pending confirmation and a trustworthy answer about what actually happened, rather than a success message based only on a click.
- effort: Medium-high: shared schema and verifier, relay D1 tables/expiry worker, Mac/browser gate integration, pendant notification protocol, and end-to-end fault-injection tests.  ·  risk: A false precondition match could still permit a wrong action; mitigate with target identity plus content/DOM digests and mandatory postcondition verification. Lost acknowledgements must be idempotent. If verifier cannot establish truth, report UNKNOWN and never claim success. Roll out first for reversible Mac actions and drafts, then gated browser writes.
- cost: Negligible relay/D1 overhead; one compact background verification call when semantic comparison is needed, typically <$0.01. No new hardware required.  ·  latency: Adds roughly 0.5–2 seconds for fresh perception and verification; confirmation delivery should be sub-second on LTE/Mac-online paths. Offline actions wait for reconnect and lease expiry rather than running blind.
- security: Improves security by binding confirmation to nonce, target, and expiry and minimizing relay data. Requires careful redaction and secure storage of nonce/evidence; never put private page contents in push payloads.
- depends on: Typed ActionProof contract agreed with faculty-judgement and faculty-perception; Durable relay job/notification delivery and pendant push acknowledgement; Browser command queue with tab/session affinity and Mac executor receipt APIs; A fresh observation endpoint that can verify target and postcondition


## What it asked for

### `s3-33pb` (skill) — action_lease_indicator
- does: Stores one redacted pending ActionLease and presents it offline as LED patterns plus short beep/vibration-equivalent audio cue through the existing playback path: pending, confirm-held, cancelled, expired, and result-verified/unknown. A deliberate long press confirms the nonce-bound lease; a short press cancels. It emits an authenticated ack or expiry when LTE returns, and never executes the action locally.
- must be on-device because: The owner needs to approve or cancel while away from the Mac or during a transient link drop, and the confirmation must survive a dropped voice session. The pendant is the only surface physically attached to the owner. Server-side execution remains gated until the ack arrives.
- trigger: Server push of a lease; local button event; timer expiry; reconnect event.
- storage: Persist at most one active lease and a small ring of  eight ack/result records on microSD (under 16 KB total), with nonce and expiry; clear sensitive text on completion/expiry.
- RAM budget: About 8–12 KB for state machine, CBOR/JSON parsing, nonce, LED/audio cue buffers, and retry queue; comfortably below the 211,608 B application RAM budget, though playback buffers must be reused rather than duplicated.

### `t22-oceb` (tool) — verify_action_proof
- why: Action execution needs deterministic postcondition verification tied to the same target and attempt; without it the action agent can only report that a click/API call completed, not that the intended world state resulted.

```json
{
  "type": "object",
  "required": [
    "actionId",
    "attemptId",
    "target",
    "expectedPostcondition",
    "beforeEvidence",
    "afterEvidence"
  ],
  "properties": {
    "actionId": {
      "type": "string"
    },
    "attemptId": {
      "type": "string"
    },
    "target": {
      "type": "object",
      "properties": {
        "surface": {
          "type": "string"
        },
        "entityId": {
          "type": "string"
        },
        "sessionId": {
          "type": "string"
        },
        "tabId": {
          "type": "string"
        }
      }
    },
    "expectedPostcondition": {
      "type": "object",
      "description": "Typed predicate, not free-form prose"
    },
    "beforeEvidence": {
      "type": "object"
    },
    "afterEvidence": {
      "type": "object"
    }
  }
}
```

