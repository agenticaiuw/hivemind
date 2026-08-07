# Harness derivation — faculty-judgement — round 36

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Let me give the pendant temporary permission to handle this one kind of task, and have it expire automatically when the task is done or after I say how long."
- **useful because:** Today authority is either too broad and implicit or stops at a fragile confirmation prompt. A time- and scope-limited consent lease lets the owner say “you may reschedule this meeting and update the travel booking for the next 20 minutes,” while the pendant shows/hears the active lease, the relay carries it across reconnects, the Mac gathers local context, and the browser performs only the permitted private-site steps. The owner gets safe autonomy without repeatedly narrating approval or accidentally authorizing unrelated actions.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified → faculty-judgement → faculty-action → dashboard
- **model tier:** Realtime only for issuing/renewing/revoking the lease and speaking the short status; use a cheaper background model to classify requested scope, enumerate candidate actions, and summarize the final receipt.
- **latency:** Lease acknowledgement within 1 second in the live conversation; enforcement checks add under 100 ms per action. Background impact analysis may take seconds and must not block the spoken acknowledgement.
- **cost:** Usually one realtime turn plus a small background classification/receipt pass, roughly $0.01–$0.05 per lease depending on context size; browser/Mac execution dominates wall-clock time, not tokens.
- **security:** A lease must be unforgeable, bound to owner/session/device, explicit about verbs, domains, data classes, and expiry, and default-deny on ambiguity. Never include send/delete/purchase or external publication unless separately named and confirmed. Persist only a hash and audit receipt, not secrets; revoke locally from a pendant button/phrase even if the relay is unreachable. Reconnects must not silently extend it.
- **missing:** Typed consent-lease schema and validator shared by judgement/action; Mac and browser middleware that reject actions outside the lease before execution; Pendant firmware lease indicator and offline revoke button/phrase; Relay persistence and replay-safe revocation/expiry across reconnects; Dashboard showing active leases, remaining time, covered actions, and receipts; A policy test matrix for compound tasks and irreversible-action escalation

### "When I double-press the pendant, put the whole hive in privacy mode until I release it: stop sending or reading sensitive context, pause Mac/browser observation, and tell me when it is safe to resume."
- **useful because:** A wearable is present in meetings, homes, and public places where the owner cannot afford an accidental transcript, screen read, or logged-in-page extraction. One physical gesture should protect every surface, not just mute the microphone: the pendant, relay, Mac vision/terminal, and browser bridge must all honor the same privacy boundary and recover without losing the task.
- **path:** pendant → relay-realtime → mac-vision → mac-planner → browser-extension → unified → faculty-perception → faculty-judgement → faculty-action → dashboard
- **model tier:** No model is needed for entering or enforcing privacy mode. Realtime is used only to announce state and reconcile a paused conversation; a cheap background model may summarize the explicitly resumed gap if the owner asks.
- **latency:** Physical entry and local mic suppression under 100 ms; relay and bridge stop-observing acknowledgements within 500 ms. Resume announcement under 1 second.
- **cost:** Near-zero model cost during privacy mode; small event/audit metadata only. Hardware work is firmware/UI and possibly a dedicated privacy indicator.
- **security:** Fail closed if any surface misses the privacy heartbeat: show “privacy not confirmed” locally and do not resume cloud audio. Do not persist raw audio or screenshots from the protected interval. Distinguish privacy mode from ordinary mute, make it visually/haptically obvious, and require a physical gesture or explicit phrase to leave it.
- **missing:** A signed privacy-state heartbeat consumed by relay, Mac bridge, and browser bridge; Pendant-local physical privacy toggle and unmistakable indicator; Mac vision/screen-capture and browser observation hooks that can hard-stop; Relay ingress suppression and retention tagging; A resume protocol that reports which surfaces acknowledged privacy and whether any data was buffered

### "Let me say “rehearse this” and have the pendant, Mac, browser, and relay work out the whole task without changing anything, then tell me exactly what would happen, what information would leave my devices, and where you would stop for approval."
- **useful because:** The owner cannot safely evaluate a multi-surface automation from a single confirmation dialog. A true dry-run would let them inspect the complete proposed route—including private browser reads, local files, notifications, irreversible steps, and failure branches—before granting authority. It builds trust without requiring the owner to understand which agent can reach which system.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → mac-terminal → browser-extension → unified → faculty-perception → faculty-judgement → faculty-action → dashboard
- **model tier:** Use a cheaper background model for plan expansion, data-flow classification, and branch simulation. Use realtime only to collect the rehearsal request and speak the short result or ask one clarification.
- **latency:** Acknowledge immediately; produce a basic rehearsal in 3–10 seconds and a complex one asynchronously with a pendant notification. No real action may occur while rehearsal mode is active.
- **cost:** Approximately $0.02–$0.15 for a complex rehearsal, dominated by context extraction and branch analysis; no external action cost. Cache unchanged page/file observations during the rehearsal.
- **security:** The dry-run itself must not perform side effects, trigger page mutations, upload screenshots, or expose more private data than the eventual task. Each simulated step needs a source, proposed executor, data-egress classification, reversibility label, confidence, and explicit “not executed” marker. If a tool cannot guarantee read-only behavior, omit it and say so. Require a fresh approval after the rehearsal; never convert a rehearsal token into execution authority.
- **missing:** A side-effect-free execution contract enforced below the planner; Read-only adapters for Mac, browser, and relay with capability declarations; A typed simulation trace covering data access, egress, mutations, approvals, and failure branches; A dashboard and spoken summary format for reviewing/revising the rehearsal; A fresh approval token cryptographically separated from the rehearsal result


## Changes it proposed to its own stack

### `interaction` — Add a cross-surface consent-lease protocol: faculty-judgement emits a signed lease containing allowed action verbs, target domains/resources, data sensitivity ceiling, expiry, and confirmation requirements; relay stores the lease and revocations durably; faculty-action, Mac bridge, and browser bridge verify it immediately before every step. Add a pendant haptic/LED/audio state for lease active, expiring, revoked, and blocked, plus a long-press local revoke that works offline. Every lease decision emits a compact receipt with requested scope, actual scope used, and rejected attempts.
- **owner gets:** The owner can delegate a bounded piece of work confidently and walk away, knowing a reconnect, ambiguous instruction, or buggy agent cannot turn permission to edit one calendar event into permission to send mail or buy something.
- effort: Medium-high: protocol/types, relay persistence, three enforcement adapters, pendant UI/firmware, dashboard and adversarial tests.  ·  risk: A stale verifier or clock skew could accept an expired lease; use monotonic expiry where possible, short maximum lifetimes, fail-closed on missing relay acknowledgement, and revoke locally. Recovery is a visible blocked receipt and a new explicit lease.
- cost: Negligible runtime API cost; small D1/R2 metadata per lease and audit event. Pendant firmware change has low component cost and modest battery impact only while indicating an active lease.  ·  latency: One local signature/lookup check per action, typically under 100 ms; no extra model turn after issuance.
- security: Materially improves least-privilege and auditability, but creates a high-value authorization primitive; protect signing keys, bind leases to session/device, prevent replay, and redact target/resource identifiers in spoken output.
- depends on: A typed action/precondition envelope from faculty-judgement to faculty-action; Durable cross-surface job/event persistence; Mac and browser bridges exposing a pre-execution policy hook; Pendant firmware event and indicator support

### `firmware` — Make 24 kHz superwideband an explicit end-to-end audio profile rather than a codec option: pendant advertises capabilities, relay negotiates and records the selected profile, packets carry sequence/timestamp/profile metadata, and both ends expose underrun, concealment, and measured round-trip/jitter counters. Fall back to the proven narrowband profile only after a bounded failed negotiation, with a spoken/LED indication and a diagnostic receipt. Add a local ring-buffer of pre/post failure audio metadata (not raw speech) so the pendant can file a useful UART bug report.
- **owner gets:** Voice sounds natural and intelligible in daily use, and when it does fail the system can tell the owner whether the problem was the pendant, network, relay, or playback instead of silently degrading or losing a turn.
- effort: Medium: firmware codec/transport integration, relay negotiation and metrics, playback compatibility, acceptance tests over reconnect, packet loss, and battery conditions.  ·  risk: Higher bitrate can expose radio/battery limits and a partial rollout could produce one-way audio. Keep a tested narrowband fallback, never switch profiles mid-utterance, and surface the selected mode in diagnostics.
- cost: No per-call model increase; modest bandwidth/storage increase and likely a small additional audio power draw. Exact battery impact needs measurement on the actual pendant radio/codec.  ·  latency: Negotiation adds only at session setup; packetization/codec tuning should target unchanged conversational latency.
- security: Audio remains sensitive: metrics must exclude speech content, and diagnostic buffers must not retain raw audio by default.
- depends on: A defined audio acceptance test matrix and fixtures; Relay audio profile negotiation support; Pendant firmware codec and packet metadata support; Playback path verified at 24 kHz


## What it asked for

_Nothing._
