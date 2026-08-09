# Harness derivation — faculty-perception — round 192

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac and browser readiness** — At 2026-08-08T22:38Z, Mac agent /ops/status reports Accessibility and Screen Recording granted, all required permissions ready, computer-use loop enabled, browser extension online with 2 Safari tabs, and relay reachable with D1-backed service; no pendant appears in live devices inventory.
  - evidence: GET /ops/status HTTP 200 and discover(devices) returned Safari on MacIntel online, home-macbook-bridge online, cloudflare-contract-test offline; no nRF pendant.

## Capabilities it proposed

### "Before you interrupt me, tell me whether now is a good moment—and if I say yes, deliver the answer through the best available surface."
- **useful because:** The system currently knows Mac permissions, foreground computer state, browser tabs, relay reachability, and (when present) pendant health separately, but no one turns them into an interruption decision. This would prevent speaking over a call/video, avoid sending work to a stale browser, and choose pendant/audio versus Mac notification honestly.
- **path:** pendant → relay-realtime → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Cheap background classifier for interruptibility; realtime only for the final spoken question and owner response.
- **latency:** Under 500 ms for a status verdict; under 2 s after owner approval to choose and begin delivery.
- **cost:** Usually <$0.001 per verdict if rule-based; one realtime turn only when asking permission. Dominant cost is optional screen/audio interpretation, not the status reads.
- **security:** Foreground app title, browser URL/title, and permission state are sensitive. Keep raw screenshots local; send only coarse categories (meeting, editor, idle, login wall) to relay. Require explicit approval before interrupting or acting.
- **missing:** A first-class interruptibility endpoint that atomically samples /ops/status, get_mac_status, browser status/inspect, relay liveness, and pendant beacon when registered; A user-configurable policy for protected apps, quiet contexts, and urgency classes; A delivery selector that refuses to claim pendant delivery when no pendant is registered

### "When you change something on my Mac or in my browser, show me a compact proof of exactly what changed, where, and how to undo it—without making me trust the word 'done'."
- **useful because:** Accessibility and Screen Recording are now actually ready, while current completion often means only that the Mac agent ran. A proof receipt would let the owner distinguish intended visible change from a no-op, wrong-tab mutation, or partial failure and undo it safely.
- **path:** mac-planner → mac-vision → browser-extension → relay → dashboard → pendant
- **model tier:** No model for capture or hashing; use deterministic local evidence. Use a cheap text model only to summarize the receipt; realtime speaks the summary when requested.
- **latency:** Capture before/after state within 300 ms for browser text and 1 s for screen-backed actions; summary under 2 s.
- **cost:** Near-zero API cost; local screenshot cropping, DOM/text snapshots, hashes, and ledger writes dominate.
- **security:** Receipts can expose passwords, private pages, or screenshots. Redact secrets before relay/storage, retain only hashes plus a small semantic diff by default, and require confirmation before sharing evidence beyond the Mac.
- **missing:** A mandatory pre/post evidence hook around every mac_run_actions and browser_run_actions mutation; A single receipt schema linking action ledger step, browser command, evidence capsule/content hash, and undo handle; A dashboard/voice formatter that says 'changed / no change / uncertain' rather than equating process completion with success

### "For anything consequential, give me a preview on the Mac, require a deliberate confirmation on the pendant, then execute only if the browser or screen is still the same—and tell me if it drifted."
- **useful because:** A spoken 'yes' can arrive after a page, recipient, amount, or focused app has changed. This creates a real two-key safety boundary: the owner confirms through a different surface, while the Mac/browser proves the preview is still the target immediately before mutation.
- **path:** pendant → relay-realtime → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Cheap deterministic state machine for preview, freshness, and confirmation; realtime handles only natural-language confirmation and final explanation.
- **latency:** Preview in 2 s, confirmation window configurable (default 60 s), drift check under 500 ms immediately before execution.
- **cost:** Near-zero model cost for hashes and state comparison; one realtime turn for the spoken confirmation. Screen capture and browser inspection are the dominant local costs.
- **security:** Never treat an arbitrary browser result or a transcripted 'yes' as authorization. Bind confirmation to an opaque nonce, target hash, action digest, expiry, and device identity; refuse if URL/tab/focused-app/content hash changes. Do not include secrets in the preview sent over relay.
- **missing:** A cross-surface confirmation nonce protocol with expiry and replay protection; Atomic browser/screen drift checks immediately before POST /execute or browser mutation; A pendant confirmation event path (currently no pendant is registered, so this must degrade to an explicit Mac confirmation); A durable audit record that links preview, owner confirmation, drift result, execution receipt, and undo

### "When I make a commitment in any message or webpage, ask me once whether it is real, then keep a private promise ledger and remind me only when the promise is actually at risk of being missed."
- **useful because:** Today the Mac, browser, relay, and wearable have no shared concept of a commitment lifecycle. This would turn vague 'I'll send that tomorrow' language into owner-approved promises, distinguish promises from casual text, watch for completion evidence, and escalate at the right moment instead of producing repetitive reminders.
- **path:** browser-extension → mac-planner → mac-vision → relay → pendant → dashboard
- **model tier:** Background text model extracts candidate commitments; deterministic rules track due windows and completion evidence; realtime is used only for the one approval or a concise escalation.
- **latency:** Candidate extraction within 3 seconds of a message/page read; no continuous model calls. Escalation should reach the owner within 10 seconds of a verified risk.
- **cost:** Low background cost, roughly <$0.01 per 100 inspected messages/pages; storage and browser observation dominate, not realtime inference.
- **security:** Messages, recipients, and private page text must remain on-device by default. Never send a commitment or message automatically. Require explicit approval to create a promise and again before any outbound reminder or reply.
- **missing:** A commitment object and state machine (candidate, accepted, due, evidence-found, fulfilled, cancelled, overdue) shared by Mac and relay; Browser and Mail/Messages observation hooks that emit only redacted candidate text and source pointers; A completion-evidence matcher spanning sent messages, files, calendar events, and browser confirmations; A wearable escalation route with honest acknowledgement and quiet-hour policy

### "Before anything leaves my Mac for the relay or a cloud model, show me what will leave, remove secrets and identifying details, and let me set a rule that keeps certain apps, sites, and conversations local forever."
- **useful because:** The current system can read private browser tabs, Mail, Messages, and screens, but transport and model choice are not presented as a single owner-controlled boundary. A live privacy gate would make cloud assistance usable without silently exporting credentials, medical content, or work data.
- **path:** mac-planner → mac-vision → browser-extension → relay → dashboard → pendant
- **model tier:** Deterministic local classifier and redactor first; a cheap local model may label ambiguous text. Realtime is never used to decide privacy policy and receives only approved material.
- **latency:** Under 150 ms for known app/site rules; under 1 s for local classification and redaction before a cloud request.
- **cost:** Near-zero API cost for rules and local redaction; occasional local inference cost only. The main cost is maintaining a reviewable redaction preview.
- **security:** The gate itself must fail closed, prevent prompt injection from changing policy, preserve URLs as hashed handles when needed for provenance, and require explicit confirmation to override a blocked transfer. Policy must survive relay failure and be auditable offline.
- **missing:** A single preflight interception point before relay, web search, browser evidence, and realtime tool payloads; A local sensitivity taxonomy and reversible redaction preview with owner-editable rules; A signed policy snapshot shared by Mac, browser extension, relay, and pendant; A dashboard showing what was withheld, transformed, or allowed

### "When two of my sources disagree about something important—like a calendar time, price, address, or account status—show me the conflict with both sources and ask which one should win instead of silently choosing."
- **useful because:** The system currently collapses machine context, browser readings, memory, and routines into answers even when provenance or freshness differs. A disagreement witness would prevent stale machine facts or a changed webpage from becoming confident action, while preserving the owner's chosen authority for future decisions.
- **path:** browser-extension → mac-planner → mac-vision → relay → pendant → dashboard
- **model tier:** Deterministic field extraction, timestamps, hashes, and source ranking; a cheap model only normalizes equivalent values. Realtime asks the owner to resolve the conflict.
- **latency:** Detect conflicts during a task in under 1 second; present a two-source card in under 3 seconds; persist the resolution immediately.
- **cost:** Low: local parsing and hashing dominate; no cloud model needed for straightforward dates, amounts, URLs, or names.
- **security:** Keep source bodies local and send only conflicting fields and provenance. Never overwrite an owner preference automatically; resolutions need scope and expiry (for example, this trip only versus always).
- **missing:** A normalized fact-comparison layer joining memory, browser evidence, calendar/mail, and relay results; Freshness- and provenance-aware conflict scoring rather than confidence-only sorting; An owner resolution record with scope, expiry, and source authority; A cross-surface UI/voice card that exposes the exact disagreement and blocks consequential action until resolved


## What it asked for

_Nothing._
## Its own summary

Discovered and recorded a materially changed live state: the exact AI Pendant Agent now has Accessibility and Screen Recording, all required automation permissions are ready, computer-use is enabled, Safari bridge is online with two tabs, and the D1 relay is reachable. There is still no registered nRF pendant. I proposed three owner-visible capabilities: interruptibility-aware delivery, proof-carrying Mac/browser changes, and a two-key preview/confirmation flow that rejects stale screen or browser state.

**Biggest unknown:** Whether the physical pendant can be registered and emit authenticated confirmation/playback events. Until then, any pendant-dependent delivery or confirmation must honestly degrade to Mac/browser surfaces; the missing work is protocol/firmware wiring, not another diagnostic read.

