# Harness derivation — faculty-action — round 254

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Take care of this across my Mac, browser, and phone, and don't stop at ‘done’—keep retrying safe steps, verify each result independently, and tell me exactly where it stopped if anything is uncertain.”"
- **useful because:** This would turn the system from a collection of individual actions into a dependable operator for real multi-step work. It can execute reversible steps, pause for the existing physical approval latch before risky ones, independently verify postconditions, retry only safe failures, and surface an honest unknown instead of claiming success.
- **path:** pendant → relay → mac-bridge → browser → iOS → dashboard
- **model tier:** gpt-5.6-luna for planning and recovery decisions; gpt-4.1-mini for visual state extraction; relay-realtime only for the owner's live interruption and concise status.
- **latency:** First safe action within 3 seconds; each verification within 2 seconds; long workflows continue asynchronously with a pendant haptic outcome and dashboard timeline.
- **cost:** About $0.03–$0.20 per ordinary workflow depending on verification and recovery turns; browser screenshots and repeated planner calls dominate.
- **security:** The relay must receive only opaque step IDs and redacted summaries, never form secrets or page contents. Risk-tiered steps require the existing physical_transaction_approval_latch. A failed or unverifiable step must stop downstream mutations; retries require idempotency keys and expiry.
- **missing:** A workflow executor that owns step dependencies, idempotency keys, bounded safe retries, and compensation/stop rules; Add actionId/attemptId correlation to verify_operation_step so receipts and independent evidence join unambiguously; A durable cross-surface workflow timeline visible to the owner

### "“If I'm moving, driving, or clearly occupied, don't make me answer a risky prompt—quietly hold it, give me a tactile summary, and ask again when I'm still.”"
- **useful because:** The pendant can detect that a confirmation request is unsafe or socially disruptive without opening a microphone. It prevents accidental approvals while walking and prevents a laptop workflow from demanding attention at the worst moment, while preserving the action's expiry and audit trail.
- **path:** pendant → relay → mac-bridge → browser → iOS → dashboard
- **model tier:** Firmware motion classifier for immediate stillness/handling state; relay-realtime only to phrase a live alert; gpt-5.6-luna asynchronously decides whether a deferred action is still valid.
- **latency:** Motion veto under 100 ms locally; relay receives a compact state event within 1 second; no model call for the common safe/unsafe determination.
- **cost:** Near-zero inference cost for local IMU classification; occasional $0.01–$0.05 planner call when an expired action needs replanning.
- **security:** The device must transmit only coarse states (still, moving, vigorous motion, unknown), never raw IMU traces by default. Motion is a safety veto, never approval. Unknown sensor state must conservatively defer risky actions. The owner needs an explicit policy for which risk classes may wait unattended.
- **missing:** motion_context_safety_gate firmware skill using the owned LSM6DSOX (i2c2 enablement, bounded classifier, no raw upload); Relay policy that binds motion state to approval-latch expiry and action risk class; A clear owner-configurable rule table for defer/notify/cancel

### "“Read me the things waiting for my attention, one at a time, and let me scroll to the one I want before you open or act on anything.”"
- **useful because:** A pendant with a wheel can become an attention inbox rather than a stream of interruptions. The owner can triage reminders, failed workflows, browser drafts, and verified outcomes by touch while the phone stays in a pocket. Selection only chooses an opaque item; opening sensitive content or approving an action remains a separate deliberate step.
- **path:** pendant → relay → mac-bridge → browser → iOS → dashboard
- **model tier:** No model for queue navigation; gpt-5.6-luna only summarizes or groups items when the inbox changes. Relay-realtime reads the selected short summary if the owner requests it.
- **latency:** Wheel-to-haptic response below 80 ms locally; queue refresh under 1 second when connected; offline navigation uses the cached compact inbox.
- **cost:** Usually <$0.01 per refresh; model cost only when generating a new short summary, roughly $0.005–$0.03.
- **security:** The pendant stores opaque IDs, risk class, expiry, and short owner-approved labels—not page bodies, credentials, or private message text. Sensitive entries expose only a generic haptic category until the owner explicitly asks through the live link. Selection never executes or approves.
- **missing:** A rotary encoder and second button in the product enclosure (owner's stated hardware direction); A compact INBOX projection protocol with deterministic ordering, expiry, and haptic vocabulary; Firmware wheel navigation and a safe read-out request gesture

### "“Bookmark exactly what I’m doing, and later put me back into that same work—not just a note saying I was there.”"
- **useful because:** A spoken or tactile bookmark would become a resumable workspace: the owner could leave a meeting, switch devices, and return to the same browser tabs, foreground Mac document, phone context, draft state, and conversation position. It preserves intent and working state rather than merely recording a timestamp.
- **path:** pendant → relay → mac-bridge → browser → iOS → dashboard
- **model tier:** gpt-5.6-luna for extracting a compact task label and deciding which state is safe to snapshot; deterministic Mac/browser/iOS adapters for capture and restoration; relay-realtime only for immediate confirmation.
- **latency:** Capture under 2 seconds; restoration preview under 3 seconds; restoration may continue asynchronously and must report each item that could not be restored.
- **cost:** $0.02–$0.10 per snapshot/restore, dominated by state summarization and verification; storage is small for metadata but may grow for local screenshots or drafts.
- **security:** Never copy passwords, payment data, private page bodies, or microphone audio into the snapshot by default. Store opaque references plus hashes and sensitivity labels. Restoration must reopen or draft, never submit, and require the existing physical approval for external side effects.
- **missing:** A cross-surface scene schema with sensitivity labels, expiries, opaque references, and content hashes; Read-only capture and verified restore adapters for Mac, browser, and iPhone Mirroring; A user-visible conflict policy when tabs, documents, or drafts have changed since capture

### "“For the next hour, handle routine follow-ups from this person in the way I just showed you, but stop and ask me before anything sensitive or irreversible.”"
- **useful because:** The owner could grant a narrowly scoped, expiring delegation instead of approving every repetitive action individually. The system would learn one demonstrated pattern, operate across Mail, Messages, browser, and calendar, and automatically revoke the authority at the deadline or on a context change.
- **path:** pendant → relay → mac-bridge → browser → iOS → dashboard
- **model tier:** gpt-5.6-luna for extracting the demonstrated policy and classifying each candidate action; deterministic policy enforcement and AppleScript/browser adapters for execution; realtime only for exceptions.
- **latency:** Routine actions under 5 seconds; sensitive exceptions surfaced immediately with a tactile alert; delegation state must remain valid offline only as a local pending policy, never as permission to send.
- **cost:** $0.05–$0.30 per delegation window, mostly policy extraction and exception classification; routine deterministic actions are inexpensive.
- **security:** This is bounded capability delegation, not blanket consent: sender, destination, action types, data fields, rate limit, expiry, and maximum risk must be explicit. Secrets never enter the pendant. Every external mutation needs an idempotency key, receipt, and independent verification; the owner can revoke with one physical gesture.
- **missing:** A first-class expiring delegation-token/policy model distinct from one-shot physical approval; A policy simulator showing examples that would and would not be sent before activation; Revocation propagation across relay, Mac, browser, and iOS with fail-closed behavior

### "“When I say ‘send that file to them,’ identify the file and recipient from what I’m looking at, show me exactly what will leave my devices, and only send after I physically confirm.”"
- **useful because:** This would solve a common gap between conversation and action: the owner need not name a path, account, or upload control. The Mac, browser session, and phone can jointly resolve the intended artifact and destination, while the pendant gives a compact, deliberate confirmation and the system verifies the resulting upload or message.
- **path:** pendant → relay → mac-bridge → browser → iOS → dashboard
- **model tier:** gpt-4.1-mini for visual/local UI grounding; gpt-5.6-luna for ambiguity resolution and risk classification; deterministic adapters for attachment and upload; realtime only to ask a concise clarification.
- **latency:** Resolve candidate file and recipient in 3 seconds; confirmation preview in 5 seconds; send only after physical approval; verification within 3 seconds after submission.
- **cost:** $0.03–$0.20 per send, dominated by UI grounding and post-send verification; no document contents need leave the Mac unless the destination requires it.
- **security:** The relay receives only hashes, filenames, recipient labels, and redacted previews unless the owner explicitly permits more. Never infer a recipient from a weak visual match. The physical confirmation digest must bind file hash, byte size, recipient, service, and expiry. If any postcondition is unknown, report unknown and do not retry blindly.
- **missing:** A privacy-preserving artifact/recipient resolver spanning Finder, browser sessions, and iPhone Mirroring; A confirmation envelope that binds a file digest and destination identity to the physical approval latch; Service-specific verified postconditions for message attachments and uploads


## What it asked for

_Nothing._
