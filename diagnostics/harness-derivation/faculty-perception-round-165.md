# Harness derivation — faculty-perception — round 165

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac observability** — At 2026-08-08T02:56:08Z, /observe reports inputReachability.status=verified, Accessibility trusted, Screen Recording true, secureInput=false, and uiActionsWillReachTheScreen=true for com.aipendant.agent. /ops/snapshot reports permissions.ready=true with no required or optional missing permissions.
  - evidence: Authenticated GET /observe and GET /ops/snapshot both returned HTTP 200; /observe included checkedAt 2026-08-08T02:54:26Z and verified input probe.
- **live browser and relay** — At 2026-08-08T02:56:08Z, the Mac bridge, Safari browser extension, and relay are reachable/online; Safari exposes 9 tabs and the active tab is X at https://x.com (tabId 1163292). Browser pending commands and spool are both zero.
  - evidence: Authenticated GET /ops/snapshot and GET /browser/status returned online=true, relay reachable=true, browser online=true, pendingCommands=0, spooled=0.
- **continuity snapshot grant** — The granted read_continuity_snapshot tool is not executable in the current runtime: its resolver returned unresolved, with nearest matches GET /ops/snapshot and GET /pipeline. Cross-surface continuity must therefore be read from those routes directly, with their individual freshness and retention limitations.
  - evidence: Direct call to read_continuity_snapshot returned error unresolved, resolution nearestRealCapabilities /ops/snapshot and /pipeline.

## Capabilities it proposed

### ""Before you interrupt me, tell whether I’m busy; if I am, hold it and deliver it when I’m free.""
- **useful because:** The system can now observe the real foreground app, secure-input state, browser tab, and relay/browser liveness. It should turn those facts into a cross-surface interruption decision instead of speaking over a meeting, sensitive form, or active call.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Cheap background classifier/rules for state; realtime only for the owner's explicit override or ambiguous voice request.
- **latency:** Observe state in under 300 ms; decision under 500 ms; queued delivery at the next safe transition. No model call for ordinary rule matches.
- **cost:** Near-zero for rule matches; occasional small text-model call under $0.001 when app context is ambiguous. Dominant cost is none, not audio.
- **security:** Foreground app and tab titles can reveal sensitive activity. Keep raw URLs and titles local; relay receives only a coarse sensitivity class (meeting, sensitive-form, idle, unknown). Speaking or sending an urgent item still requires the owner's existing policy/confirmation.
- **missing:** A local focus/interruption policy with owner-configurable safe states and urgency classes; A relay queue item that records defer reason and re-evaluates on state change; A browser signal for active media/call state rather than only tab metadata

### ""Give me a one-sentence readiness check before you do anything risky: what app is active, whether the browser is trustworthy, and whether you can undo it.""
- **useful because:** The live Mac is now Accessibility- and Screen-Recording-ready, but that power is easy to misuse. A compact pre-action reality fence would let the owner hear the exact current context and reversibility before an action crosses from planning into execution.
- **path:** pendant → mac-planner → mac-vision → browser-extension → relay → dashboard
- **model tier:** Rules and hashes for normal checks; cheap text model only to summarize the check in natural language. Realtime is reserved for a spoken confirmation.
- **latency:** Under 400 ms for observation and risk classification; spoken summary within 1.5 s. Action remains blocked until explicit confirmation for irreversible or sensitive operations.
- **cost:** Usually no model cost; under $0.001 for fallback wording. Screen capture and hashing are local and dominate CPU, not API spend.
- **security:** Never send screenshots, raw tab URLs, or form contents to the relay. Hash the active UI locally and expose only app class, tab host classification, sensitivity, and undo availability. A stale observation must fail closed rather than authorize.
- **missing:** A shared sensitivity-labeled context record with timestamp, app identity, browser tab pseudonym, state hash, and expiry; Action executor support for binding a planned step to that record and rejecting stale/mismatched state; Owner-visible spoken and dashboard representation of the risk class

### ""If the connection or permissions break while you’re working, explain exactly what failed, keep the request safe, and resume only when the missing surface is back.""
- **useful because:** The system now has verified input reachability, complete automation permissions, online relay, and an online browser extension. A cross-surface degradation mode would make failures legible and prevent the dangerous state where the Mac reports success while the browser, relay, or future pendant cannot finish the job.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Rules/state machine for health transitions and recovery; cheap model for a concise owner-facing explanation. Realtime only when the owner asks what happened.
- **latency:** Health transition detected within 2 s; status explanation under 1 s; automatic retry only for idempotent steps after the required surface is healthy for a configurable debounce (for example 5 s).
- **cost:** No recurring API cost for health checks; under $0.001 for rare explanation generation. Storage is a bounded event ring.
- **security:** Do not replay writes after uncertain completion. Persist idempotency key, pre-state, and receipt locally; redact URLs, secrets, and form values from cross-surface health events. Recovery of an irreversible action must require confirmation.
- **missing:** A typed cross-surface health state machine and bounded transition log; A job runner distinction between definitely-not-started, in-flight-unknown, and completed-without-delivery; A relay push or polling contract for browser and Mac health changes

### ""Save my entire working moment. If anything crashes or I switch devices, put me back exactly where I was — app, browser tabs, drafts, and the conversation — without sending or submitting anything.""
- **useful because:** Today the system can undo individual Mac jobs, but it cannot restore the owner's actual working context across the Mac UI, browser session, relay conversation, and pendant state. A bounded, encrypted working-moment checkpoint would make crashes, sleep, and handoffs recoverable without replaying side effects.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Deterministic checkpoint/restore engine; cheap model only to explain conflicts. Realtime is unnecessary except for a spoken restore request.
- **latency:** Checkpoint in under 2 seconds on explicit request or before a risky multi-step task; restore preview in under 3 seconds; restoration requires confirmation whenever a target document or form has changed.
- **cost:** No recurring model cost; local serialization and screenshot thumbnails dominate. Encrypted checkpoint storage should be capped (for example 20 moments or 250 MB).
- **security:** Never persist passwords, tokens, secure-input contents, or raw sensitive screenshots. Browser extension must redact secret fields before export; relay should hold only an opaque checkpoint ID and encrypted blob metadata. Restore must default to preview-only and never submit forms or send messages.
- **missing:** A cross-surface checkpoint schema joining active app/window, browser session/tab and locator, draft-safe document state, relay conversation cursor, and pendant interaction state; Browser and Mac restore adapters that can distinguish draft restoration from side-effecting submission; Encrypted local storage with explicit owner deletion and conflict detection

### ""Put me in privacy lock when I press the pendant button: no listening, screenshots, browser reads, relay speech, or background actions until I unlock it, and show me proof that every surface is locked.""
- **useful because:** Privacy is currently a collection of independent permissions and heuristics. The owner needs one physical, unmistakable control that propagates from the worn device to the relay, Mac agent, and browser extension, with a verifiable fail-closed state rather than trusting a UI indicator.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Firmware and server state machine only; no language model needed. Realtime is bypassed while locked.
- **latency:** Local microphone/screenshot suppression immediately; relay and browser lock acknowledgement within 1 second; if any surface does not acknowledge, the pendant remains visibly/ audibly in 'lock pending' and refuses new capture.
- **cost:** Negligible API cost. A bounded signed lock-state record and heartbeat add tiny bandwidth/storage overhead.
- **security:** The lock command must be authenticated, monotonic, replay-resistant, and fail closed across reconnects. Local suppression must happen before audio leaves the pendant; Mac and browser must reject queued commands while locked. Unlock should require a deliberate long press plus owner confirmation, not a remote model decision.
- **missing:** A pendant-originated privacy-lock firmware state with nonvolatile monotonic epoch; Relay-wide lock gate covering realtime audio, announcements, jobs, and browser proxy calls; Mac/browser enforcement hooks that cancel or quarantine pending work and return signed lock acknowledgements; A compact cross-surface attestation view in the dashboard

### ""When I say 'take over this project', keep a living map of the files, tabs, reminders, and next decisions, and let me continue it from the pendant without rebuilding the context every time.""
- **useful because:** The current context graph, sessions, jobs, browser tabs, and reminders are separate stores. The owner cannot promote a real-world project into one durable, portable workspace that the pendant, Mac, browser, and relay all understand and update safely.
- **path:** pendant → relay → mac-planner → mac-terminal → browser-extension → dashboard
- **model tier:** Cheap background model maintains summaries and proposes links; realtime handles only the owner's spoken edits and questions. Deterministic connectors own file/tab/reminder facts.
- **latency:** Open an existing project context in under 2 seconds; background updates within 10 seconds of a change; spoken lookup under 1.5 seconds.
- **cost:** Small background summarization cost, roughly $0.01–$0.05 per active project per day depending on event volume; storage and connector polling dominate.
- **security:** Project membership must be explicit; sensitive files, browser secrets, and message contents stay local unless the owner opts in. Every inferred relation needs provenance and an easy remove action. Never let a summary become an instruction without confirmation.
- **missing:** A first-class project/workspace object spanning context graph, Mac files, browser sessions, reminders, and relay conversations; Event connectors that report changes with provenance and sensitivity labels; Pendant query/update protocol for compact project state and offline edits; Conflict resolution when Mac, browser, and pendant make concurrent changes


## What it asked for

_Nothing._
## Its own summary

Fresh live checks changed the reality fence: the exact AI Pendant Agent binary is now Accessibility- and Screen-Recording-trusted, input reachability is verified, automation permissions are complete, the Mac bridge/relay/browser extension are online, and Safari has 9 tabs (active X tab). I recorded these facts and proposed three cross-surface owner capabilities: focus-aware interruption deferral, context-bound pre-action readiness fencing, and safe degradation/recovery for broken surfaces. The granted continuity tool itself is unresolved at runtime; I used /ops/snapshot, /pipeline, /observe, and /browser/status instead and recorded that limitation. I still need a real unified continuity endpoint implementation, a live registered pendant/firmware heartbeat, and typed state contracts connecting observations to action binding and recovery; without those, pendant-heard status and complete away-time coverage remain unknowable.

**Biggest unknown:** There is still no live nRF9160 pendant in the relay registry, so no current evidence can establish that audio reached or was heard by the owner. The pipeline also still reports completed Mac/relay work without a device playback event.

