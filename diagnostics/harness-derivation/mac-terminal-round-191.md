# Harness derivation — mac-terminal — round 191

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When my pendant is plugged into my Mac, let me use it as a real local voice remote even with no LTE: I press the button, speak, and say 'open the document I was working on' or 'run the test and tell me if it passed.'"
- **useful because:** This is testable today with the physically connected nRF9160 and ESP32, and removes the most damaging failure mode: a wearable that appears present but cannot do anything when the relay is unreachable. The Mac can provide serial transport and local execution while the cloud remains optional for richer reasoning.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal
- **model tier:** Realtime only for turn-taking and short intent extraction; use a cheaper background model for multi-step planning and local verification. If the cloud is unavailable, a local deterministic command vocabulary should still handle open/status/run-and-report requests.
- **latency:** Button-to-recording tone under 150 ms; USB audio round trip under 300 ms; first local action under 2 s. Cloud fallback may take 5-10 s but must not block local commands.
- **cost:** Near-zero incremental API cost for deterministic local commands; roughly $0.01-$0.05 only when a cloud model is needed. Engineering is dominated by serial framing, reconnect tests, and audio buffering.
- **security:** The USB link is physically local but still needs authenticated framing and per-turn IDs. Do not forward the Mac environment or bearer secrets over serial. Spoken commands can trigger unrestricted Mac control under the owner's deliberate policy, so retain an append-only local receipt and clearly announce host-unreachable versus completed.
- **missing:** A USB serial transport adapter for the nRF9160 audio/control frames and ESP32 bridge; A local relay mode that routes pendant turns to localhost without requiring LTE registration; A bounded offline intent vocabulary and local TTS/audio return path; A transport-level receipt that ties button turn ID to the /execute job ID

### "Run this until it is genuinely finished, and only interrupt me if it fails or needs a decision; if the Mac restarts, continue or tell me exactly what was lost."
- **useful because:** Today a 120-second shell can outlive cancellation, jobs remain 'processing' forever after a crash, retries are absent, and the ledger cannot be joined to its job. A supervised task gives the owner reliable outcomes instead of a green-looking request that may have died halfway through.
- **path:** relay-realtime → mac-planner → mac-terminal → dashboard
- **model tier:** Use a cheap background model for retry classification and verification; reserve realtime for the owner's initial request and an exception/decision turn.
- **latency:** Acknowledge dispatch within 1 s. Heartbeat every 5 s. Recovery scan within 10 s of agent boot. Do not add model latency to ordinary command execution.
- **cost:** Usually no model call; $0.01-$0.03 for failure diagnosis or verification. Storage is small per checkpoint, but implementation needs a process supervisor and durable state machine.
- **security:** Keep the owner's unrestricted execution policy; this is not a gate. Run each shell action in its own process group, record a redacted environment fingerprint rather than secrets, and make retries opt-in by idempotency classification. Never claim completion from a vanished child: report interrupted, resumed, or verified.
- **missing:** A durable task supervisor with process-group PID and signal tracking; Boot reconciliation that marks stale processing jobs and resumes only checkpoint-safe steps; A real job-to-ledger foreign key and closed-ledger lifecycle; Exit code, signal, timeout, and bounded stdout/stderr artifact capture; Retry policy with idempotency keys and post-step verification hooks

### "Watch the authenticated pages I already have open, and when something important changes, tell me on the pendant what changed and what I can safely do next; if I say 'handle it,' make the browser change and show me the evidence before any final submission."
- **useful because:** The browser is the only node holding sessions the Mac shell and relay cannot recreate. Combining its session authority with the always-available relay, the wearable's short confirmation, and Mac-side evidence capture turns silent web obligations into an actionable voice inbox without leaking credentials into the model.
- **path:** browser-extension → relay-realtime → pendant → mac-planner → mac-vision
- **model tier:** Use a background model to diff and rank page changes; realtime handles the brief spoken summary and a narrowly scoped decision. Use the vision model only when DOM inspection is insufficient.
- **latency:** Poll only watched pages every 1-5 minutes; deliver a three-sentence alert within 15 s of a meaningful change. After 'handle it,' preview in under 5 s and execute only after the pendant's explicit one-turn confirmation.
- **cost:** $0.001-$0.02 per meaningful page change depending on DOM versus vision; most polls should be zero-model diffs. Browser storage and screenshots dominate local disk, not API spend.
- **security:** Keep cookies and session tokens inside the extension. Send extracted text and cropped evidence, never raw page storage, to the model. Treat submit/send/purchase as a separate final step; return a before/after DOM or screenshot hash and URL so the owner knows exactly what happened.
- **missing:** A durable per-tab watch definition with semantic change filters and deduplication; A relay event type that carries a compact alert plus evidence reference to the pendant; An explicit preview/commit transaction for browser mutations, with final-submit classification; Evidence retention and redaction for screenshots and extracted page text

### "Before I leave the house, tell me what I am likely to forget today, using my open work tabs, local files, calendar, and unfinished Mac jobs; give me the three highest-cost omissions and let me fix each one from the pendant."
- **useful because:** No single node can answer this: the browser has authenticated obligations, the Mac has local drafts and failed work, the relay has time and delivery, and the pendant is the only interface available while moving. It converts scattered unfinished state into a short, prioritized intervention rather than another generic briefing.
- **path:** browser-extension → mac-planner → mac-terminal → relay-realtime → pendant → dashboard
- **model tier:** A cheap background model builds and ranks the omission graph; realtime only speaks the three-item result and handles the owner's chosen fix. Use vision only for tabs whose semantic state cannot be extracted from DOM.
- **latency:** Build the snapshot in under 20 s and speak in under 5 s after the button press. Fix previews should arrive within 3 s; long actions continue asynchronously with the existing status beacon.
- **cost:** $0.01-$0.06 per on-demand scan, dominated by model context and occasional browser vision; cached hashes should make repeated scans nearly free.
- **security:** Raw authenticated page content stays in the extension unless explicitly selected as evidence. Local file names and calendar details need sensitivity labels. Never infer an omission as fact: every item must cite its source tab/file/job and offer dismiss, defer, or fix.
- **missing:** A cross-surface unfinished-obligation graph linking browser changes, local files, calendar, and Mac jobs; Source citations and sensitivity labels that survive into a spoken alert; A pendant-friendly three-choice fix protocol (fix, defer, dismiss); A scheduler/trigger for departure or a user-defined time window

### "When I say 'continue where I left off,' restore the exact work state from my last interruption: the right Mac app and window, browser tab and scroll position, file and selection, and the pending job or draft—then tell me what changed since I stopped."
- **useful because:** Today context is fragmented across app focus, browser sessions, project state, and relay conversations. A durable semantic cursor would let the owner move from desk to walking to desk without re-explaining the task or accidentally resuming the wrong tab or draft.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use a small background model to resolve references and summarize deltas; realtime only confirms the restored state. Vision is a fallback for window/selection state that accessibility APIs cannot expose.
- **latency:** Identify the last cursor in under 2 s and restore app/tab focus in under 4 s. If any component is unreachable, report the exact missing part rather than blocking restoration of the rest.
- **cost:** Usually $0.002-$0.02 per resume; local state capture and a compact delta index dominate, not inference.
- **security:** Persist opaque references and hashes for sensitive documents, not their contents. Browser cookies never leave the extension. Require an explicit spoken confirmation before typing into or submitting a restored draft, and make every restoration idempotent.
- **missing:** A signed, cross-surface semantic-cursor record containing app/window/tab/file/job anchors; Mac APIs to capture and restore selection, scroll, and focused window state; Browser commands for restoring tab, frame, scroll, and draft anchors; A durable relay-to-pendant cursor query and delta-summary event

### "Use my Mac and authenticated browser to do the work, but do not send their private contents to the cloud; ask the cloud only for a plan over redacted facts, execute locally, and tell me on the pendant exactly what data was kept local."
- **useful because:** The most capable nodes are also the ones holding the owner's secrets. Today the useful planner and relay can be fed context without a durable, inspectable boundary. A privacy-preserving split lets the owner use browser and shell reach without choosing between capability and confidentiality.
- **path:** mac-terminal → mac-planner → browser-extension → relay-realtime → pendant → dashboard
- **model tier:** Run extraction, redaction, retrieval, and action planning locally with a small model or deterministic rules. Use the expensive realtime model only on schemas, labels, and redacted summaries; never include raw page text, file contents, cookies, or environment variables by default.
- **latency:** Redaction and local retrieval under 1 s for a normal request; cloud plan under 3 s; pendant explanation under 5 s. If a field cannot be safely classified, keep it local and continue with a partial plan.
- **cost:** $0.001-$0.02 per request, often zero for local routing; the cost is a local index/redaction model and dashboard work rather than tokens.
- **security:** The boundary must be technically enforceable, not a prompt instruction: separate local and cloud payload types, deny raw-content serialization, redact secrets and personal identifiers, log hashes and field categories, and expose a pendant-readable disclosure receipt. The owner can explicitly promote a field for one turn.
- **missing:** A local privacy broker that produces typed redacted facts instead of arbitrary context strings; Browser and shell data-classification/redaction adapters, including environment-secret stripping; A cloud planner schema that rejects raw content and returns an executable intent graph; A disclosure receipt visible in the dashboard and speakable on the pendant


## What it asked for

_Nothing._
## Its own summary

This round produced three distinct owner-facing capabilities. The highest-value one is USB-local pendant voice: the physically connected nRF9160/ESP32 should work as a low-latency local voice remote even with no LTE, using the existing pipeline and execute/job routes. I also proposed supervised, crash-recovering long-running Mac tasks with truthful completion, and authenticated-browser watch/voice handoff with evidence before final submission. The recorder accepted all three as new, while warning that most named routes already exist and the missing work is the connective layer.

**Biggest unknown:** The exact USB serial framing and current firmware/bridge behavior remain unobserved. I still need the pending mac_usb_serial_diagnostics capability (already requested; I did not re-ask) to verify ports, framing, and whether audio/control can be exercised today. The browser proposal also needs an authoritative inventory of /watches semantics and the relay's pendant event delivery contract.

