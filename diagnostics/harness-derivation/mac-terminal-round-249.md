# Harness derivation — mac-terminal — round 249

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live device reconnaissance** — The newly granted mac_usb_serial_diagnostics and mac_read_diagnostics schemas still do not resolve against the live inventory; no serial or diagnostic implementation is callable. GET /browser/status is live with Safari extension online, five tabs, USPS active.
  - evidence: mac_usb_serial_diagnostics returned resolution=unresolved (best action:get_mac_status 0.226); mac_read_diagnostics unresolved (best GET /health 0.423); describe GET /browser/status returned online:true, tabCount:5.

## Capabilities it proposed

### ""Take care of the next step on the authenticated page I'm looking at. Show me exactly what you found, what will change, and then carry it out; if the page rejects it, recover instead of making me start over.""
- **useful because:** This would turn the browser session the owner already pays for into an agent that can finish real authenticated work, while preserving a spoken and visual evidence trail. The pendant supplies intent and receives the result, the relay coordinates, Safari supplies the private session, and the Mac performs any local consequence. It is more useful than another generic browser reader because it handles the failure/recovery boundary between page state and Mac state.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → mac-vision
- **model tier:** Realtime for the short spoken intent and final readback; a cheaper background model for DOM/evidence comparison and recovery planning.
- **latency:** Read the page in 1-3 seconds, produce the proposed change in under 5 seconds, and finish ordinary actions within 15 seconds; long waits become a durable job with a spoken receipt.
- **cost:** About $0.01-$0.08 per ordinary action, dominated by the evidence comparison and any vision fallback; no model call is needed for straightforward structured fields.
- **security:** The authenticated page contents and evidence capsule leave Safari for the relay/model, so redact secrets and limit transfer to the selected page and affected fields. The owner’s explicit spoken request authorizes the requested mutation; never infer a submit from mere reading. Record before/after evidence and an honest failed state rather than claiming success.
- **missing:** A typed browser transaction primitive that returns before/after DOM evidence plus the mutation result; A cross-surface transaction ID joining browser provenance, Mac job receipts, and the pendant reply; A recovery planner that can re-read the page after a stale-session or validation failure without duplicating a successful submission

### ""Run a 30-second bench health test on the pendant and audio bridge and tell me, in plain English, whether both chips are alive, which link failed if not, and save the evidence.""
- **useful because:** The hardware is physically present now, but there is no owner-facing way to distinguish a dead nRF9160, dead ESP32, bad USB enumeration, or a firmware-level audio fault. A single spoken request would launch the existing dual-UART capture scripts, parse bounded health/counter frames, correlate both chips, and return a useful verdict while the pendant can show the same state locally.
- **path:** pendant → mac-planner → relay-realtime → mac-vision
- **model tier:** Use a deterministic parser and a cheap background model to summarize anomalies; reserve realtime only for the final spoken answer if the request came over voice.
- **latency:** Start capture within 2 seconds, run for 30 seconds, and return a verdict within 5 seconds of capture end. Keep raw logs local and expose only a compact evidence summary.
- **cost:** Under $0.01 when frames parse deterministically; the cost is mostly local disk and one short summary call for anomalous logs.
- **security:** USB logs can contain identifiers and audio transport metadata; keep raw captures on the Mac, hash them in the receipt, and send only counters/errors upstream. The test must be read-only and must not flash or reset either chip unless separately requested.
- **missing:** A real host serial reader/parser for the two known USB ports (the currently granted diagnostic tool still has no live implementation); Stable framed health counters from both firmware images and a shared test correlation ID; A bounded capture action that records port, baud, timestamps, exit status, and SHA-256 of each log

### ""When I come back to my Mac, give me one concise voice briefing of everything that changed while I was away—browser pages, finished or failed Mac jobs, and anything waiting for me—and let me ask for the exact evidence.""
- **useful because:** The owner currently has to remember what they asked before walking away and manually inspect several surfaces. This creates a return-to-work handoff: the Mac detects a foreground transition, the relay compresses only changes since the last departure, Safari contributes authenticated-tab deltas, and the pendant reads the result without opening a microphone continuously.
- **path:** mac-planner → mac-vision → browser-extension → relay-realtime → pendant
- **model tier:** Cheap background summarization over structured event deltas; realtime only for the short spoken briefing and follow-up questions.
- **latency:** Detect return within 2 seconds, produce a three-item maximum briefing within 4 seconds, and fetch exact evidence on demand within 3 seconds.
- **cost:** Usually under $0.01 because the input is event metadata and hashes rather than screenshots or full pages; vision is only invoked for an explicit evidence request.
- **security:** Do not transmit all browser content or keystrokes. Keep a per-session change ledger of URLs, titles, job IDs, statuses, and redacted field-level claims; require the owner to ask for page evidence before sending authenticated text to the model. Treat an app switch as presence, not consent to mutate anything.
- **missing:** A durable departure/return detector tied to the Mac foreground app and browser heartbeat; A change cursor that joins Mac job completion, browser command results, and pendant-dispatched requests without replaying old events; A compact evidence query that can retrieve the exact receipt or browser provenance record named in the spoken summary

### ""Fill this authenticated form with my saved details, but keep the actual values out of the AI and show me a proof of which fields were filled and which site received them.""
- **useful because:** The owner could finally use the wearable as a safe form-filling agent without sending passwords, addresses, payment details, or other durable personal data through the model. The model interprets the page and chooses semantic fields; a local Mac broker injects values only after verifying the exact origin, and the pendant reports a redacted proof. This is materially different from ordinary browser automation: the AI can act without ever possessing the secrets.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → mac-vision
- **model tier:** Realtime only for the spoken request and concise result; a cheap model handles field-label interpretation. Secret lookup, origin matching, injection, and proof generation must be deterministic local code.
- **latency:** Inspect and classify the form in 2 seconds, inject ordinary fields within 5 seconds, and return a redacted receipt within 2 seconds. Never wait on the model while a secret is in memory.
- **cost:** Usually below $0.01 per form; local encrypted-store access and browser messaging dominate, with no token cost for the secret values.
- **security:** Values must never enter relay prompts, logs, screenshots, browser provenance, or job receipts. The local broker must bind each field to the top-level origin, frame origin, label hash, and one-time request nonce; reject unexpected origins and cross-origin iframes. The owner explicitly requests filling, but submission remains a separate verb. Store only field names, origin, value-class, and success/failure—not values.
- **missing:** A local encrypted personal-data vault with OS-keychain-backed, per-origin and per-field retrieval; A browser-extension command that accepts opaque local value handles and injects them without returning values to the relay; A redacted form receipt proving origin, field labels, value classes, and DOM acceptance while excluding secret text; A shared nonce and expiry protocol between the pendant request, relay job, Mac broker, and browser tab

### ""Search across the authenticated tabs I already have open and tell me which tab contains the answer, without opening a new session or leaking the other tabs' contents.""
- **useful because:** The browser currently exposes one active page well, but the owner's useful context is often distributed across several already-authenticated tabs. This would let the pendant answer 'which tab has my order/status/document?' while preserving session locality: inspect only titles, headings, and narrowly matched snippets, then read the winning tab aloud or hand it to the Mac for action.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** A cheap background model ranks structured tab summaries; realtime only speaks the selected result. Use vision only when a tab has no structured accessibility tree.
- **latency:** Index five to ten open tabs in under 4 seconds and return the best match in under 6 seconds; fetch full evidence only after the owner asks.
- **cost:** Around $0.01 per search, dominated by summarizing snippets; no cost for tabs eliminated by title/URL matching.
- **security:** Authenticated tab contents must remain scoped to this request and be discarded after a short TTL. Do not send unrelated tabs wholesale; return tab IDs, origin, title, and the minimal matching evidence. Never mutate a tab during search.
- **missing:** A browser command to enumerate multiple tabs and return bounded, relevance-targeted accessibility summaries; A relay-side ephemeral tab index with strict host and TTL scoping; A spoken handoff that identifies the winning tab and can safely target it for a later, separately requested action


## Changes it proposed to its own stack

### `mac-harness` — Add a PTY-backed execution session for long-running Mac actions, without reducing FULL_CONTROL_MODE: POST /execute should optionally return a session handle immediately, stream stdout/stderr chunks with sequence numbers, capture the child PID/process group and exit code, and make cancel terminate that process group rather than merely setting an AbortController. On restart, reconcile the durable session record to exited/unknown and attach its final output to the existing job and ledger IDs.
- **owner gets:** When the owner asks the pendant to do something that takes a minute, they can hear real progress, stop a genuinely stuck command, and know whether it exited successfully instead of waiting 120 seconds for a vague failure. This is the difference between an agent that acts and one that appears frozen.
- effort: Medium-high: replace exec with spawn/execFile-compatible process supervision, add a bounded event stream and durable session metadata, thread one job ID into ledger creation, and add restart reconciliation. Preserve the existing arbitrary command surface and unattended policy.  ·  risk: PTY behavior can change programs that expect pipes; retain the current pipe mode as default and opt in per action. A hard kill may leave external side effects incomplete, so report interrupted rather than failed/succeeded. Recover by retaining final buffered output and marking process state unknown when the host dies.
- cost: Negligible API cost; modest local CPU and disk for bounded output chunks. No new hardware.  ·  latency: Immediate acknowledgement and first output chunk, rather than waiting for completion. Streaming adds negligible overhead; completion remains command-bound.
- security: No new authority beyond the owner-approved unrestricted shell. Do not persist environment values; persist only an allowlisted environment fingerprint and redact token-like output before relay streaming.
- depends on: The existing POST /execute run_shell action; The existing GET /jobs/:jobId and GET /jobs/:jobId/receipts routes; The existing action ledger, after orchestrator closes it and supplies planMeta.jobId; A new authenticated GET /jobs/:jobId/stream or equivalent event endpoint

### `integration` — Introduce a local browser privacy gateway between Safari and the relay: the extension sends the Mac agent a structured accessibility tree, and the gateway performs origin-aware redaction, secret-field removal, and bounded snippet selection before any page evidence is forwarded upstream. Keep raw DOM and screenshots local, issue short-lived evidence handles, and let the relay request only a handle's redacted view. Apply the same gateway to browser results, provenance, and any later Mac action receipt.
- **owner gets:** The owner can use authenticated browser help without choosing between useful automation and shipping an entire private webpage to a cloud model. They get precise answers and actions while unrelated account data stays on the Mac.
- effort: High: extension protocol changes, a local redaction/selection service, evidence-handle storage and expiry, and tests across forms, cross-origin frames, PDFs, and canvas pages.  ·  risk: Bad classification could omit the field needed to answer or accidentally expose a sensitive value. Fail closed for unknown field types, retain a local diagnostic mode, and let the owner explicitly request a one-page screenshot when structured evidence is insufficient. Handles expire and are invalidated when the tab navigates.
- cost: Small local CPU/memory and negligible API cost; no new model call is required for deterministic redaction.  ·  latency: Adds roughly 50-200 ms for structured pages; screenshot/canvas fallback may add 1-3 seconds.
- security: Improves privacy substantially, but the gateway becomes a high-value local component. Protect it with the existing bearer/session boundary, origin binding, encrypted temporary storage, and never log raw DOM or secret values.
- depends on: The live Safari extension and browser result route; A new local evidence-redaction service and typed browser evidence schema; Short-lived evidence handles understood by relay-realtime and mac-planner; Origin/navigation invalidation hooks in the extension


## What it asked for

_Nothing._
## Its own summary

Round produced four owner-facing proposals: authenticated browser transaction with evidence/recovery, a dual-chip bench smoke test, PTY-backed live Mac execution with real cancellation and crash reconciliation, and return-to-Mac change briefing. The recorder flagged all as near existing backlog, so the important conclusion is that these are connective gaps, not missing primitive routes. Fresh reconnaissance confirms Safari/browser is online with five tabs and USPS active, while both newly granted diagnostic schemas remain unresolved: there is still no callable serial reader or general Mac diagnostics implementation. I still need an actual bounded USB/UART capture/parser implementation (or a typed capability that resolves to it), plus the cross-surface transaction/change cursors that join pendant intent, browser provenance, and Mac job receipts.

**Biggest unknown:** Whether the existing bench scripts can be safely invoked through run_shell in this live environment and what exact UART framing/health counters the current nRF9160 and ESP32 firmware emit; the granted serial tool cannot answer because the live inventory has no implementation.

