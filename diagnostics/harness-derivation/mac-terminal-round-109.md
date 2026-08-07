# Harness derivation — mac-terminal — round 109

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-observability-2026-08-07** — GET /observe is truthful read-only telemetry: Accessibility trusted=false, eventsPost=false, inputReachability failed, ui_actions_will_reach_screen=false; however it explicitly warns UI actions may report success while doing nothing. Browser extension offline with 9 pending commands. GET /ops/status says fullControlMode=true and computerUse loop disabled; relay and Mac bridge reachable.
  - evidence: GET /observe and GET /ops/status at 2026-08-07T14:14:55Z

## Capabilities it proposed

### "When I ask you to do something on my Mac, tell me truthfully whether it actually happened—and if the Mac or browser cannot reach the screen, recover through another path or leave a clearly tracked pending job instead of claiming success."
- **useful because:** Today /observe proves the agent can report a successful click or typed text even when macOS rejects synthesized input; the browser can be offline while nine commands remain queued. This capability turns silent no-ops and stale browser work into an understandable outcome on the pendant, while preserving the owner's maximum-access policy.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension
- **model tier:** Use deterministic local checks and a cheap background model for classification/retry explanation; reserve realtime only for the short spoken status. No expensive model is needed to decide that accessibility=false or browser online=false makes a UI receipt untrusted.
- **latency:** Return an immediate pendant acknowledgement in under 300 ms from cached reachability, then a durable final receipt within the existing action timeout (typically 120 s). A fallback retry should add at most one bounded attempt; never wait indefinitely on an offline extension.
- **cost:** Near-zero model cost for health checks and receipts; roughly one cheap text-model call only when explaining a multi-step fallback or ambiguity. Dominant cost is existing Mac/browser execution time, not inference.
- **security:** Keep command contents and page text on the Mac/browser unless already authorized for relay speech. Send the relay only action id, surface, reachability verdict, status, and a redacted explanation. Do not add approval gates: the owner explicitly wants unrestricted execution. Mark UI actions as untrusted when /observe says events will not reach the screen, and distinguish 'not attempted', 'attempted but unverifiable', 'confirmed', and 'failed'. Browser queued commands need device identity, creation time, and a TTL so stale authenticated actions are not replayed after reconnect; expired commands should be recorded as dropped, not silently executed.
- **missing:** A receipt verifier in mac-planner that consults /observe before and after ui_click/type_text/press_keys and downgrades false-positive receipts; A fallback matrix that routes UI work to shell/AppleScript or browser actions when the target surface is unreachable, without pretending the original UI action succeeded; Browser command queue reconciliation keyed by extension/device identity with TTL, cancellation, and explicit expired-command receipts; A relay event schema to stream provisional, confirmed, unverifiable, failed, and expired states to the pendant; A permission-remediation hint that identifies the exact host binary needing Accessibility/Screen Recording without blocking unrelated shell work

### "If I start a task on my pendant and then walk away or lose the connection, have the system resume it on the right Mac/browser session later, remember exactly what I meant, and tell me what changed since I last heard from it—without making me repeat the request."
- **useful because:** Today a spoken request can outlive the voice turn only as a low-level job, while browser identity, Mac focus, intermediate intent, and the owner's last acknowledged state are not one resumable handoff. The owner should be able to start work hands-free and trust that a disconnect is a pause, not a reset or an unexplained duplicate action.
- **path:** pendant → relay → mac-planner → browser-extension → mac-vision → dashboard
- **model tier:** Use deterministic durable state and a cheap background model to summarize deltas and select a resume checkpoint; use the realtime model only to acknowledge the pendant request and answer a live status question.
- **latency:** A local/relay acknowledgement in under 500 ms; checkpoint persistence before acknowledging; resume within 10 seconds of a healthy Mac/browser heartbeat. Reconnection must not replay a step until its prior execution state is reconciled.
- **cost:** Negligible inference for state transitions; one small background summarization call per completed checkpoint batch. Storage and heartbeat traffic dominate, with no recurring realtime-model cost while idle.
- **security:** The handoff must bind to a paired pendant, Mac host fingerprint, browser extension identity, and session—not merely a tab URL—so authenticated work is never resumed in the wrong profile. Persist intent and checkpoint metadata encrypted at rest; relay receives redacted summaries and opaque job ids by default. The owner’s unrestricted execution policy remains intact, but irreversible steps need idempotency keys and explicit duplicate-prevention semantics. Expired or superseded handoffs must be visible and never silently replayed.
- **missing:** A durable cross-surface handoff object containing original intent, acknowledged interpretation, target surface/session identity, checkpoint, last owner-visible update, and resume policy; An exactly-once/reconcile protocol shared by relay jobs, Mac jobs, and browser commands, including step idempotency and recovery after a crash between action and receipt; Heartbeat-triggered resume orchestration that waits for the bound Mac and browser identities rather than any merely online device; A pendant-accessible delta/status stream and dashboard timeline showing paused, resumed, superseded, and completed checkpoints; Retention, encryption, and garbage-collection policy for handoff context distinct from the existing short job history


## What it asked for

_Nothing._
## Its own summary

Round 109 established a live, consequential defect: /observe reports Accessibility untrusted, synthesized events rejected, and input reachability failed, while the executor can still emit apparently successful UI receipts. The browser is offline with 9 queued commands. I recorded this and proposed a cross-node truthful execution/recovery capability spanning pendant→relay→Mac planner/vision→browser, using existing observation, job, receipt, journal, cancel, and browser polling/result routes. It preserves FULL_CONTROL_MODE and adds no approval gates.

**Biggest unknown:** I still need the implementation contract for browser queue identity/TTL/reconciliation and the exact receipt lifecycle/event schema. I also need confirmation of whether any existing backlog item already implements truthful UI-evidence grading; the current live endpoints show the defect remains.

