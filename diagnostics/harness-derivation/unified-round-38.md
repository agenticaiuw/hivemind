# Harness derivation — unified — round 38

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **cross-surface readiness** — Relay and Mac bridge are reachable and macBridgeOnline=true, but browser extension is offline with 3 pending commands; Mac computer-use loop is disabled, Accessibility is untrusted, and Screen Recording is missing. Apple automation grants are present. The owner’s timezone is America/Chicago and reminder creation is allowed without confirmation.
  - evidence: GET /ops/status returned relay.reachable=true, macBridgeOnline=true, browser.online=false/pendingCommands=3, computerUse.loopEnabled=false, accessibility.trusted=false, screenRecording.granted=false, automation grants present; owner projection states timezone and reminder policy.

## Capabilities it proposed

### "When I say “I promised them I’d do this,” make sure it doesn’t disappear: find the relevant person/thread and deadline across my open browser tabs, Mail, Calendar, and notes, then ask one concise clarification and create a private follow-up with a link back to the evidence."
- **useful because:** The pendant catches commitments at the moment they are spoken, while the Mac and authenticated browser supply context that neither the wearable nor relay can access alone. It prevents vague promises from becoming forgotten tasks without sending anything or silently inventing a deadline.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use gpt-realtime-2.1 only to detect the explicit commitment utterance and ask the one clarification. Use a cheaper background model for entity/deadline extraction and reconciliation. Mac planner performs local Mail/Calendar/Notes lookup; browser extension searches already-open authenticated tabs; dashboard presents the evidence and resulting reminder.
- **latency:** Acknowledge on the pendant within 500 ms; gather local/browser evidence in under 10 s. If browser is offline, speak that limitation and create only a clearly marked uncited draft after confirmation.
- **cost:** About $0.01–$0.04 per commitment, dominated by realtime audio and background reconciliation; local AppleScript/browser extraction should add no model cost.
- **security:** Search only explicitly named or confidently inferred sources, never arbitrary private pages. Keep transcripts and evidence local/Mac by default; relay receives the short utterance and typed result, not page contents. Creating a reminder is allowed by owner policy, but any email/message or form submission requires confirmation. Redact secrets and offer a “private/no transcript” gesture.
- **missing:** Commitment extraction and evidence schema shared by relay, Mac, and browser; A browser command that searches only currently open authenticated tabs and returns stable citations; A deduplicating reminder/follow-up writer with source links and uncertainty fields; Pendant trigger/UX for marking an utterance private and for resolving one clarification; Cross-surface correlation IDs and an expiry policy for sensitive evidence

### "When I say “I’m busy now,” make the whole hive enter an attention firewall: pause non-urgent relay work, suppress Mac and browser notifications, defer low-priority spoken output, and let only a genuinely time-sensitive event break through. When I say “I’m free,” restore everything and give me one short digest of what was deferred."
- **useful because:** Today the owner must separately manage the pendant conversation, Mac notifications, browser alerts, and background jobs. This gives them one reliable spoken boundary that follows them across surfaces, without losing work or forcing them to remember which device is interrupting them.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use the realtime model only to recognize the explicit mode command and confirm the transition. Use deterministic relay policy for queueing and urgency; use a cheaper background model to summarize deferred items when the owner becomes free. Mac and browser agents apply reversible notification/surface policies locally.
- **latency:** Mode change acknowledgement within 300 ms on the pendant; Mac/browser policy convergence within 2 seconds; deferred digest available within 15 seconds after leaving the mode.
- **cost:** Usually under $0.01 per transition; model cost is limited to the short spoken command and the final digest. Most enforcement is deterministic local policy.
- **security:** The firewall must never suppress safety-critical or explicitly allowlisted alerts. Store only mode state and job IDs in the relay, not notification contents. Browser and Mac notification controls must be reversible, visible in the dashboard, and logged. “I’m free” must not trigger any outbound action.
- **missing:** A shared interruption policy with urgency classes and owner-configurable allowlists; Mac and browser adapters that can pause/suppress notifications without stealing focus; Relay job pausing and resumable queue semantics, including audio-output cancellation; A durable deferred-item digest and restore receipt shared by pendant and dashboard; A physical override path that can silence output even if the relay or Mac is unreachable


## Changes it proposed to its own stack

### `integration` — Add a cross-surface Commitment Evidence Ledger. The relay assigns a correlation ID at the pendant utterance, then Mac Mail/Calendar/Notes and the browser bridge append typed evidence records (source surface, account/app, URL or local object identifier, quote hash, timestamp, confidence, sensitivity, expiry). A reconciler emits either a ready reminder or one clarification question; dashboard and spoken receipts render the same ledger, and all records support tombstoning when the source disappears.
- **owner gets:** A promise captured on the pendant will remain traceable instead of becoming an ungrounded reminder. The owner can see exactly why a follow-up exists and return to the original thread, while private content stays on the machine that accessed it.
- effort: Medium: shared schema and D1/local persistence, adapters in Mac planner and browser bridge, relay correlation propagation, dashboard receipt UI, and end-to-end tests for browser offline and stale/deleted sources.  ·  risk: A stale or wrong person match could create an embarrassing reminder. Require confidence thresholds, show the evidence before auto-creating anything ambiguous, expire inaccessible citations, and make reminder creation idempotent with undo.
- cost: Negligible storage; roughly 1–3 KB metadata per commitment. Background extraction uses a cheap model; no additional realtime call beyond the utterance.  ·  latency: Immediate pendant acknowledgement remains local/realtime; evidence reconciliation adds approximately 2–10 seconds depending on Mac and browser availability.
- security: Evidence quotes and URLs are sensitive. Encrypt at rest, keep page text on the Mac, send only hashes/typed summaries to relay, scope browser access to explicitly open tabs, and enforce per-source TTL/deletion propagation.
- depends on: A durable correlation/request ID propagated through pendant → relay → Mac/browser; Typed citation/result contracts for Mail/Calendar/Notes and authenticated browser tabs; A local reminder writer that accepts evidence links and supports idempotency/undo


## What it asked for

_Nothing._
