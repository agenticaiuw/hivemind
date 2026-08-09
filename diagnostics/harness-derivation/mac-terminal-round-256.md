# Harness derivation — mac-terminal — round 256

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac USB bench access** — The granted mac_usb_serial_diagnostics schema still has no live implementation; bounded reads of the physically connected nRF9160 and ESP32 ports cannot be performed through the tool inventory.
  - evidence: mac_usb_serial_diagnostics call returned unresolved; live inventory 223 routes/109 actions, nearest action:get_mac_status score 0.225.

## Capabilities it proposed

### "“Put what I’m looking at on my phone so I can finish it there.”"
- **useful because:** The owner can move from a logged-in Safari page to the real iPhone without copying URLs, retyping details, or exposing page contents to a new service. The system extracts only the actionable handoff (URL, title, selected fields, and a draft message), opens the matching iPhone surface through Mirroring, and leaves the final send/submit under the owner's control.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → ios-control
- **model tier:** gpt-5.6-luna for the short structured extraction and action plan; gpt-4.1-mini only if a visual confirmation of the mirrored iPhone is needed; realtime handles the spoken request and confirmation, not extraction.
- **latency:** 2–4 seconds to read the active tab and prepare the iPhone draft; another 1–2 seconds to open the mirrored app. Never wait on a background model for the spoken acknowledgement.
- **cost:** About $0.01–$0.05 per invocation, dominated by one planner call; browser and Mac action calls are local.
- **security:** Only the active tab's selected fields leave the browser harness, with URL and provenance recorded. Default behavior creates a draft and does not send messages, submit forms, or upload attachments without a second explicit request.
- **missing:** A typed browser-to-iOS handoff payload (source tab, destination app, fields, draft text, provenance); An iOS action that opens a draft in the selected app rather than merely focusing the mirrored window; A redaction/selection step so the owner can say 'just the booking details'

### "“Run a real voice-loop rehearsal on the pendant and tell me whether it is safe to wear away from the Mac.”"
- **useful because:** The chips are physically attached now, so this gives the owner an honest go/no-go before relying on the device: button edge, nRF UART, ESP32 audio bridge, frame acknowledgements, dropout timing, and recovery are tested together rather than inferred from a firmware build.
- **path:** pendant → mac-terminal → mac-planner → relay-realtime
- **model tier:** gpt-4.1-mini parses bounded UART logs and computes timing/dropout statistics; gpt-5.6-luna interprets ambiguous failures; realtime is used only to speak the concise result through the pendant.
- **latency:** 15–45 seconds for a bounded rehearsal, with an immediate local 'test started' indication and a hard stop; no microphone capture beyond the supplied test fixture or synthetic tone.
- **cost:** Under $0.02 per run; almost all cost is local serial capture and log parsing, not model tokens.
- **security:** USB is bench-only and must never be reported as LTE wearable continuity. Captured UART logs may contain identifiers, so retain a redacted summary plus hashes rather than raw logs by default; raw logs stay on the Mac unless explicitly requested.
- **missing:** A deterministic dual-UART test runner that drives the existing diagnostics/start_dual_capture.sh and dual_chip_autocapture.sh scripts with bounded duration; A parser for nRF9160/ESP32 frame counters, acknowledgements, timestamps, and reset markers; A synthetic audio fixture and a report that distinguishes USB transport success from LTE readiness

### "“Why did that Mac action fail, and can you repair it without making me repeat the whole request?”"
- **useful because:** Today a failed shell action loses its exit code, signal, environment provenance, and reliable job-to-ledger link, so the owner gets a vague failure and must reconstruct context. A spoken diagnostic turns the existing durable job into an actionable explanation, proposes a minimal repair, and resumes only the failed step rather than replaying earlier side effects.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → dashboard
- **model tier:** gpt-5.6-luna for diagnosis and repair planning; a cheaper local parser first classifies exit code/signal/timeout and searches the captured stderr, reserving the expensive model for ambiguous failures.
- **latency:** Under 1 second for the status acknowledgement; 2–5 seconds for a diagnosis. A repair may run asynchronously, with the pendant reporting queued/running/completed through truthful_action_status_beacon.
- **cost:** $0.005–$0.03 per failure, mostly one planner call; local parsing and receipt creation are negligible.
- **security:** Do not echo inherited secrets or raw environment values into the spoken response. Store a redacted environment fingerprint, argv/cwd, exit status, signal, and bounded stdout/stderr digest. Repairs must be tied to the original job and refuse to replay already-settled side effects.
- **missing:** A shell receipt containing exit code, terminating signal, argv, timeout-vs-process-failure, and redacted environment fingerprint; A durable job-to-ledger join and boot reconciliation for processing jobs; An idempotent per-step resume endpoint that can rerun only failed steps; A diagnostic planner that distinguishes safe retry, corrected command, and irreversible side effect

### "“Do the next step everywhere, but show me one plain-English diff before anything irreversible happens.”"
- **useful because:** The owner gets one coherent preview even when a task crosses an authenticated browser, the Mac, and the real iPhone. Instead of approving opaque clicks, they hear exactly which fields, recipients, files, or settings would change, while reversible navigation and preparation can proceed immediately.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → ios-control → dashboard
- **model tier:** gpt-5.6-luna creates the cross-surface plan and compresses structured before/after state into a spoken diff; gpt-4.1-mini handles screenshots only when a surface has no structured state. Realtime speaks the diff and collects the owner's short approval.
- **latency:** Preparation under 5 seconds; diff under 2 seconds after the last surface is inspected. No model call after approval unless the actual page has changed.
- **cost:** Roughly $0.02–$0.08 per multi-surface task, dominated by structured-state comparison and one planner call.
- **security:** The diff must be generated from captured pre-state and proposed post-state, not the model's prose alone. Bind approval to hashes of the exact plan and page/session versions; invalidate it if any surface changes. Never speak or persist secrets that are not part of the proposed mutation.
- **missing:** A cross-surface action escrow with immutable pre-state, proposed post-state, and approval hash; Structured before/after snapshots for browser forms, Mac files/settings, and mirrored iPhone screens; A pendant approval protocol that names the plan hash and refuses stale approvals; A postcondition verifier that reports partial completion instead of claiming success

### "“I’m leaving the Mac—move this unfinished task to whichever device can continue it, and tell me only if it truly cannot.”"
- **useful because:** A paused browser form, Mac file operation, or iPhone draft becomes a portable continuation rather than a dead screen. The system packages the exact cursor, authenticated session, pending fields, dependencies, and expiry, then resumes on another reachable surface without replaying completed side effects.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → ios-control → dashboard
- **model tier:** gpt-5.6-luna builds the continuation capsule and chooses the next surface; a cheaper deterministic layer validates expiry, session reachability, and completed-step hashes. Realtime is only for the concise handoff and exception.
- **latency:** Under 3 seconds to package and acknowledge the handoff; resume may run asynchronously. The owner should hear a failure only when no reachable surface can continue or the session has expired.
- **cost:** Approximately $0.01–$0.04 per handoff, mostly one planning call; capsule storage and hash checks are local.
- **security:** Continuation capsules must contain references and encrypted sealed fields, not copied passwords or page dumps. Bind them to the owner's authenticated browser/session identity, expire them, and invalidate them after a page revision or conflicting external change.
- **missing:** A portable continuation-capsule schema shared by browser, Mac, iPhone, and relay; Per-surface cursor/state adapters for browser forms, shell workflows, and iPhone drafts; Conflict detection against external changes before resuming; An expiry and ownership protocol so an abandoned capsule cannot be replayed

### "“Don’t tell me you did it—prove that the real-world result happened.”"
- **useful because:** A successful click, shell exit, or iPhone action is not the same as the intended outcome. The system would independently verify the postcondition on the authoritative surface—page state, file contents, device setting, sent-message state—and tell the owner whether it is confirmed, contradicted, or unknowable.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → ios-control → dashboard
- **model tier:** A deterministic verifier checks typed postconditions first; gpt-4.1-mini interprets visual state only when structured verification is unavailable; gpt-5.6-luna handles ambiguous evidence and asks one focused question. Realtime speaks the verdict, never invents certainty.
- **latency:** Immediate action acknowledgement, then a verified verdict within 3 seconds for local/browser state and 10 seconds for delayed external systems. Report 'pending verification' rather than waiting indefinitely.
- **cost:** About $0.005–$0.04 per verification; local structured checks are cheap and visual/model interpretation is the dominant cost.
- **security:** Verification must read the authoritative destination, not trust the action receipt or model-generated screenshot description. Store only a minimal evidence capsule with URL/app, timestamp, state hash, and provenance; redact message bodies and sensitive fields. Distinguish 'not found' from 'not yet observable.'
- **missing:** A typed postcondition language covering browser, Mac, and iPhone state; Independent read-back actions for each mutation, including delayed-service polling with bounded expiry; Evidence capsules that bind the verdict to the exact action and session version; A three-valued result contract: confirmed, contradicted, or unknown


## What it asked for

_Nothing._
