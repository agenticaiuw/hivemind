# Harness derivation — mac-terminal — round 178

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Take the result of the last terminal command, put the relevant value into the form currently open in Safari, and tell me exactly what you filled."
- **useful because:** This is a genuine handoff between two private contexts: the Mac shell has local files/commands, while Safari has authenticated sessions. Today the owner must copy values manually and risk putting the wrong output in the wrong field. The pendant provides a short spoken request and receives a concise, auditable result.
- **path:** relay-realtime → mac-planner → browser-extension → mac-vision → mac-terminal
- **model tier:** background for extracting and normalizing terminal output; realtime only for the spoken request and final confirmation
- **latency:** 2-5 seconds for command/output lookup and form inspection; under 10 seconds for filling and returning a field-by-field report
- **cost:** Usually one cheap extraction call plus one browser inspection/action; roughly $0.01-$0.05, dominated by vision only when the form has no semantic labels
- **security:** Terminal output and authenticated form contents remain on the Mac/browser bridge except the minimal extracted value sent through the relay. Never infer a field when labels are ambiguous; return a preview of field/value pairs and require the owner to say submit for irreversible submission.
- **missing:** A typed handoff object linking a shell job/result to a browser command, with provenance and redaction of secrets; Browser action support for filling from an explicit value map and returning the resulting DOM/displayed values; A relay response that can speak the field-by-field receipt back to the pendant

### "Keep watching this build/test command and interrupt me through the pendant only when its state changes, it fails, or it needs a decision."
- **useful because:** A 120-second shell action is treated as one opaque job today. The owner cannot leave a test/build running, walk away, and get a useful spoken delta; they either poll or miss the failure. This turns the Mac into an unattended worker while preserving the pendant as the attention channel.
- **path:** mac-terminal → mac-planner → relay-realtime → browser-extension
- **model tier:** background model for periodic log summarization and state classification; realtime only to deliver the short alert and collect a decision
- **latency:** Detect process exit immediately; summarize meaningful log changes within 10 seconds while suppressing repeated noise
- **cost:** One cheap incremental summarization call per meaningful log chunk, typically $0.01-$0.10 per hour depending on output volume; local hashing/filtering should dominate normal idle cost
- **security:** Logs may contain source code, paths, or secrets. Keep raw logs on the Mac, send only bounded redacted deltas to the relay, and let the owner choose whether alerts include a line excerpt. The watcher must never silently restart or kill a process.
- **missing:** A detached process/watch action with a durable cursor and process-group identity, rather than execAsync's single 120-second call; Incremental stdout/stderr tailing and exit-code/process-state reporting in the job journal; A relay-to-pendant alert route with deduplication and a 'snooze this watcher' response

### "Find every recurring subscription visible in my authenticated browser and local receipts, reconcile duplicates, and give me one spoken list of what is charging me, with links to cancel each one."
- **useful because:** The browser can see logged-in account pages and the Mac can search downloaded receipts, but neither surface alone can reconcile them. The owner gets a high-value financial inventory without manually searching tabs, email exports, and Downloads; cancellation remains an explicit later request.
- **path:** relay-realtime → browser-extension → mac-planner → mac-terminal → mac-vision
- **model tier:** background model for extraction, deduplication, and date/amount normalization; realtime only for the final spoken summary
- **latency:** 30-90 seconds for a bounded set of open authenticated tabs plus local receipt folders; return progress if a source is slow
- **cost:** $0.05-$0.30 per inventory, mostly browser/page extraction and OCR of receipts; cache document hashes so unchanged receipts cost nothing on later runs
- **security:** This is sensitive financial data. Keep raw pages/receipts local, transmit only normalized merchant/amount/frequency/cancel URL, redact account numbers, and never click cancellation or export data without a separate explicit ask. Require source citations for every line and mark uncertain matches.
- **missing:** A local-only file search action that returns structured receipt candidates without uploading raw documents; Browser extraction across authenticated tabs with per-field provenance and an explicit allowlist of pages; A cross-surface deduplication schema and spoken summary with citations/uncertainty

### "Remember this value for the next form I open, then fill only the matching field when I say 'use the remembered value'."
- **useful because:** The owner frequently transfers one-time identifiers, totals, tracking numbers, and account references between spoken conversation and authenticated forms. A short-lived, provenance-labeled value slot would remove error-prone retyping without creating a permanent memory of sensitive data.
- **path:** relay-realtime → mac-planner → browser-extension → mac-vision
- **model tier:** Realtime for extracting the value from the spoken turn and matching the active field; no background model unless the field label is ambiguous
- **latency:** Under 2 seconds to acknowledge capture; under 3 seconds to fill after the explicit 'use' command
- **cost:** Usually under $0.01 per use; dominated by realtime inference only when speech contains multiple candidate values
- **security:** Store only an encrypted, expiring value plus source turn and intended field class; never persist it in general memory or logs. Refuse to fill a differently typed field, show the masked value on the pendant, and expire after one successful use or 10 minutes.
- **missing:** An ephemeral encrypted value-slot service with one-use semantics; Browser field-type discovery and a value-class compatibility check; A pendant command/result protocol for capture, expiry, and successful consumption

### "If a travel booking, delivery, or appointment changes, find the best replacement in the authenticated pages I already use, update my local calendar draft, and tell me the tradeoff through the pendant."
- **useful because:** Time-sensitive changes require combining authenticated browser portals, local calendar/files, and a low-attention spoken interface. The owner should not have to notice an email, compare alternatives, copy details, and repair their calendar manually while traveling or working.
- **path:** browser-extension → mac-planner → mac-vision → relay-realtime → mac-terminal
- **model tier:** Background model for monitoring and comparing alternatives; realtime only for urgent spoken interruption and the owner's choice
- **latency:** Detect a watched change within 2 minutes; produce a bounded comparison within 30 seconds; never silently finalize a booking or payment
- **cost:** $0.05-$0.50 per change, dominated by authenticated page inspection and alternative comparison; unchanged pages should cost almost nothing via hashes
- **security:** Travel, delivery, and appointment pages reveal sensitive location and schedule data. Keep raw pages local, send only normalized options, and require explicit owner selection before any purchase, cancellation, or external message. Every calendar edit needs an undoable receipt.
- **missing:** A generalized authenticated page-watch rule with semantic change detection; A local calendar-draft action that can reconcile time zones and conflicts; A structured alternative-comparison and owner-selection protocol spanning browser, Mac, and pendant

### "When the web app breaks, collect the exact browser state and the relevant local logs, reproduce it once, and give me a ready-to-send bug report with evidence and a minimal next step."
- **useful because:** The browser holds the authenticated failure state while the Mac holds the project and server logs; either node alone loses half the diagnosis. The owner gets a useful report instead of repeatedly explaining a failure or sending screenshots without context.
- **path:** browser-extension → mac-vision → mac-terminal → mac-planner → relay-realtime
- **model tier:** Background model for log correlation, reproduction, and report drafting; realtime only for the spoken diagnosis and a short follow-up question
- **latency:** Collect evidence in 5 seconds, attempt one bounded reproduction in 30 seconds, and return a report draft within 60 seconds
- **cost:** $0.05-$0.40 per incident, mostly vision/log-context processing; local hashing and filtering should avoid resending unchanged logs
- **security:** Authenticated page contents, cookies, source code, and logs are highly sensitive. Keep raw evidence on the Mac, redact tokens/cookies/customer data before model calls, attach only selected snippets and screenshots, and never send the report externally without explicit owner action.
- **missing:** A browser diagnostic snapshot including console/network errors and DOM state without exporting session secrets; A local log correlation/search action keyed by timestamp, project, and request ID; An evidence bundle format with redaction, reproducibility metadata, and a draft-only external-share action


## Changes it proposed to its own stack

### `integration` — Add a USB-tethered local pendant session: auto-discover /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA, bind the nRF9160 button/audio stream to the Mac relay as a first-class device even when LTE registration is absent, and route spoken replies/status back over the ESP32 bridge. Persist a session UUID and reconnect cursor so unplug/replug does not duplicate a turn.
- **owner gets:** They can wear and use the real pendant on the Mac today instead of waiting for LTE registration; the same button request can inspect Safari, run a local command, and speak the result with honest offline/link status.
- effort: Medium: serial framing/baud discovery, bridge lifecycle, turn-id replay tests, and one local device registration path.  ·  risk: Malformed serial frames or reconnect races could duplicate audio or commands. Gate only by exact turn ID/cursor and keep the existing truthful link beacon authoritative; on ambiguity drop the frame and report disconnected rather than guessing.
- cost: Negligible API cost for local turns; roughly 1-3% Mac CPU while active and small bridge development cost. No new hardware.  ·  latency: USB local round trips should reduce request/reply latency by roughly 100-500 ms versus waiting for an unregistered LTE path.
- security: USB is a local trust boundary: bind only the two enumerated serial identities, do not expose the serial protocol on LAN, and keep bearer credentials out of firmware. Local commands still follow the owner's deliberate full-control policy.
- depends on: A serial protocol adapter for the nRF9160 and ESP32 firmware; A local relay device-registration/session route; Turn-idempotent audio and event forwarding; The already accepted audio_link_truth_and_recovery and truthful_action_status_beacon behavior


## What it asked for

_Nothing._
