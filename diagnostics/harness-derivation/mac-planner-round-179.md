# Harness derivation — mac-planner — round 179

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-session state** — Safari browser bridge is online with 9 tabs; active tab is https://platform.openai.com titled 'Billing overview - OpenAI API', with zero pending commands and no affinity.
  - evidence: GET /browser/status returned online:true, tabCount:9, tabUrl platform.openai.com, pendingCommands:0.

## Capabilities it proposed

### "“When I press the bookmark button or say ‘record this decision’, save not just my words but the exact evidence I was looking at.” Later I should be able to ask for a decision receipt containing the timestamp, active browser tab, calendar context, document identifiers, and hashes of captured artifacts."
- **useful because:** A normal voice memo loses the surrounding context and makes later recall ambiguous. A provenance receipt lets the owner distinguish what was actually seen or decided, link it to the right project, and verify that a follow-up was based on the original evidence without retaining unnecessary page bodies.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Use deterministic capture, hashing, and redaction first; use a cheap background model only to label entities or summarize after capture. Reserve realtime for the spoken bookmark command.
- **latency:** A bookmark acknowledgement must remain immediate (<300 ms); context collection may complete asynchronously within 5 s and visibly mark the receipt partial if a surface is unavailable.
- **cost:** Usually near-zero model cost for the receipt; optional background summary is a small completion. Storage is bounded metadata plus opt-in artifact hashes, not full browsing history.
- **security:** Default to hashes, titles, URLs, app/document IDs, and redacted snippets; never silently persist passwords, billing values, or page bodies. Browser capture must honor origin/session boundaries. Receipts need an immutable event ID and explicit deletion that removes all linked artifacts.
- **missing:** A provenance receipt schema and durable append-only store distinct from ordinary voice-memo blobs; browser command to return active-tab identity and selected/redacted evidence with origin policy; Mac read-only document identity/selected-text inspection beyond current foreground/app and directory operations; relay query endpoint that can retrieve and explain a receipt

### "“When I start a pendant call, put a privacy curtain over the browser immediately, and restore exactly what I was viewing when the call ends.” The curtain should work for the current Safari tab, preserve its session, and show only a local ‘Pendant call active’ page while sensitive screens are hidden."
- **useful because:** The pendant can be used in public or beside other people, while the Mac currently shows authenticated pages (the live browser is on an OpenAI billing page). Muting the pendant does not protect visible secrets. A local extension curtain gives a concrete, reversible visual privacy boundary without logging out or destroying the tab.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** No model: call lifecycle, tab affinity, overlay, and restoration are deterministic. Realtime only carries the lifecycle event.
- **latency:** Curtain injected within 250 ms of call-start event; restoration within 500 ms after call end or disconnect. If the relay disappears, the extension should fail closed until its short local timeout expires.
- **cost:** No per-invocation API cost. Small browser-extension implementation and local state storage.
- **security:** Never copy page contents into the relay. Store only tab/window ID, URL, and a restoration token locally in the extension. Handle navigation and tab closure explicitly; do not restore a different authenticated page into view. The owner must be able to locally cancel the curtain, and a dropped link must not leave an inaccessible blank screen forever.
- **missing:** Browser extension command/event for call-start and call-end with tab/session affinity and a local opaque overlay; Relay lifecycle fan-out from pendant call state to browser heartbeat/poll channel; Crash-safe extension restoration state and a bounded fail-closed timeout; Optional Mac-level curtain for non-browser apps (blocked for UI-wide coverage without Accessibility/Screen Recording)

### "“What would happen if I click the button under my cursor?” While I am wearing the pendant, inspect the focused browser element and tell me its visible label, destination, side effects, and whether it looks like a login, purchase, deletion, or other consequential action—without clicking it. If I then say ‘do it’, hand the exact element back to the browser executor."
- **useful because:** This gives the owner a spoken safety lens over authenticated web sessions that the Mac planner cannot infer from a URL alone. It is especially useful on unfamiliar billing, admin, and forms pages, and it separates inspection from execution so a vague voice command cannot silently act on a different tab.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** A small/cheap model or deterministic DOM classifier should extract element metadata and risk classes; use realtime only to answer the short spoken question. Never send full page text unless explicitly requested.
- **latency:** Return element metadata in under 700 ms and a spoken answer in under 2 s; bind any later execution to the same tab, frame, element selector, and page revision, expiring after 30 s or navigation.
- **cost:** A few cents at most for an explanation-heavy request; deterministic extraction is effectively free. Browser-side implementation is the main cost.
- **security:** Redact values and secrets before relay upload; preserve origin and tab affinity; reject stale selectors and navigation changes. The ‘do it’ path must report the exact action and target, and must not infer a different target from natural language. Log only the risk classification and hashes, not passwords or payment data.
- **missing:** Browser extension API for hovered/focused element metadata, DOM ancestry, form/action destination, and page revision; Relay intent carrying a signed inspection token into a later execution request; A typed browser action that accepts only that token and revalidates origin/DOM state; Pendant call-state event and short-lived spoken follow-up correlation

### "“Give me a physical emergency stop for anything the assistant is doing on my Mac or in my browser.” If an external side effect is underway—sending a message, submitting a form, moving files, or launching a command—I should be able to press a dedicated pendant control and have every node revoke the action lease immediately, then report whether it stopped before or after the side effect."
- **useful because:** A spoken cancel can be missed while the owner is watching a dangerous action happen. A physical, low-latency stop works even when the browser or Mac is busy and provides a precise boundary between ‘cancelled’ and ‘already committed’. This is materially different from muting audio or pausing privacy capture.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** No model in the stop path. The relay maintains action leases and deterministic cancellation; a model may explain the resulting receipt afterward.
- **latency:** Pendant-to-relay-to-executor stop propagation under 150 ms on USB and under 500 ms on LTE. Every executor must checkpoint before irreversible OS or web commits.
- **cost:** No per-use model cost. Requires firmware input/state work, executor integration, and browser command cancellation.
- **security:** The stop signal must be authenticated, monotonic, and bound to the owner’s active session. Executors must fail closed on lease expiry or lost heartbeat, while explicitly distinguishing cancellation from successful completion. Do not claim rollback where a remote web side effect already committed.
- **missing:** A dedicated physical stop control or redesigned pendant input state machine; the current two-button semantics are already allocated; Relay-wide action lease and revocation protocol shared by Mac and browser executors; Checkpoint/cancel hooks around Mac and browser mutations; A durable post-action receipt with committed-before-stop versus stopped-before-commit status

### "“Before you act on a web page or in an app, give me a compact spoken contract of exactly what will change, and afterward prove that the observed result matches it.” The contract should include target, recipients, files or records touched, and expected before/after state; the browser or Mac executor should refuse to report success without a machine-readable result."
- **useful because:** Today a plan and an execution receipt can say that an action ran, but they do not give the owner a cross-surface, machine-checkable promise that the intended object changed and nothing else did. This would make automation trustworthy for consequential work without requiring the owner to inspect every screen.
- **path:** relay-realtime → pendant → mac-planner → browser-extension
- **model tier:** Use deterministic schemas, hashes, and postcondition checks. A cheap model can turn the contract into a short spoken explanation; realtime is only needed for the owner-facing utterance.
- **latency:** Contract under 1 s for known actions; postcondition receipt within 2 s after completion. Unknown or unverifiable postconditions must be reported as unknown, never inferred as success.
- **cost:** Minimal model cost for routine actions; implementation cost is typed pre/postcondition adapters for common Mac and browser operations.
- **security:** Contracts must redact secrets and avoid sending page bodies or private file contents to the relay. Hashes and stable identifiers should be preferred. A mismatch must stop chained actions and surface the exact discrepancy rather than retrying blindly.
- **missing:** A shared action-contract and postcondition schema spanning Mac and browser; Browser adapters that snapshot permitted DOM/state fields before and after mutation; Mac adapters that verify file/app state without relying on visual Accessibility access; Executor behavior that treats unverifiable postconditions as a distinct result

### "“Let the pendant and Mac work as one continuous conversation when I move between rooms.” If the LTE link drops, the Mac should continue the same voice session over the locally attached wearable, preserve turn order and queued audio, and reconcile the transcript and events exactly once when the link returns—without making me restart or repeat myself."
- **useful because:** A dropped link currently splits a live interaction into separate experiences. Seamless continuity is the single most useful everyday property of a wearable assistant: the owner can leave Wi‑Fi/phone range, return to the Mac, and keep the same task and conversation rather than reconstructing context aloud.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Realtime handles only the active audio conversation. Session reconciliation, duplicate suppression, transcript merge, and queued-event repair should be deterministic or use a cheaper background tier.
- **latency:** Resume within 1 s of detecting the alternate transport; no duplicated spoken turn; queued audio should drain in order with bounded jitter. Reconciliation may finish asynchronously but must expose a clear final session state.
- **cost:** No additional model cost while connected; failover may increase modest relay/WebSocket traffic. Main work is transport/session identity and audio sequence reconciliation.
- **security:** Both transports need the same authenticated session identity but separate replay-safe channel keys. Never replay microphone audio after the owner has ended a call or enabled the local privacy latch. Reconcile by sequence number and server acknowledgement, not timestamps alone.
- **missing:** A transport-agnostic session identity shared by LTE and Mac USB/local links; Relay audio/event journal with exactly-once acknowledgements and ordered merge; Mac local transport endpoint for the physically connected pendant; Pendant and relay handover state machine that preserves call and privacy state; Browser/Mac surfaces that subscribe to the same session rather than creating a second job


## What it asked for

_Nothing._
