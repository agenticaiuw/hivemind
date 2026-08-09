# Harness derivation — browser-extension — round 192

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser bridge availability** — Authenticated Safari bridge currently reports offline with zero devices and zero pending commands, so browser-specific work cannot be exercised this round even though the route inventory and extension protocol exist.
  - evidence: GET /browser/status returned {"online":false,"devices":[],"pendingCommands":0,"spool":{"spooled":0,"lastReason":null,"lastAt":null},"affinity":[]} at round 192.

## Capabilities it proposed

### "I'm looking at a boarding pass, ticket, pickup code, or one-time QR on a logged-in Safari page. Put the useful code and expiry on my pendant and read it back when I press the button, even if I leave the Mac."
- **useful because:** The browser is the only node that can see authenticated passes, while the pendant is the only one available while walking away. This turns a fragile web page into a short-lived, offline-usable travel/access token without persisting the page.
- **path:** browser → mac-harness → relay → pendant
- **model tier:** background for extracting a typed pass record; realtime only for the owner's spoken request
- **latency:** Under 5 seconds to extract and acknowledge; button playback under 1 second once cached.
- **cost:** Low: one extraction call and a tiny relay/pendant payload; dominated by the model only when the page layout is unfamiliar.
- **security:** Never store HTML or screenshots. Detect and label the value as an expiring credential, encrypt in transit and on the pendant, auto-delete at expiry, and require an explicit spoken request or selected-page gesture. Do not expose arbitrary page text.
- **missing:** Safari extension extraction of QR/barcode pixels or accessibility values into a typed expiring-pass record; Pendant playback of a structured code with expiry and automatic deletion; Relay route to issue and revoke a pass capsule

### "Stop whatever the browser is doing right now."
- **useful because:** A browser job can outlive the sentence that started it, and Safari holds sessions nobody else can reach. A physical pendant press or voice command should immediately cancel queued commands, invalidate the active browser lease, and close only the automation-owned tab if requested—without waiting for a 45-second bridge timeout.
- **path:** pendant → relay → mac-harness → browser
- **model tier:** realtime for the spoken/physical stop path; no model needed for cancellation
- **latency:** Hard stop acknowledgement in under 500 ms locally and under 2 seconds at Safari; recovery status within 5 seconds.
- **cost:** Negligible inference cost; small persistent command-ledger and extension protocol change.
- **security:** The stop path must be available offline on the pendant and must not depend on model interpretation. Default action cancels automation only; a separate explicit phrase can close automation-owned tabs. Never close arbitrary owner tabs. Keep an audit receipt without page content.
- **missing:** A pendant-to-relay emergency-stop event that survives a dropped Mac link; An extension command to cancel the current command and mark its tab lease revoked; A cross-surface cancellation route that fan-outs to /jobs/:jobId/cancel and browser command deletion

### "Lock my private browser tabs now, and unlock them when I return."
- **useful because:** The owner can walk away from the Mac with authenticated sessions open. A pendant command provides a physical, immediate privacy boundary: Safari can blank or lock selected origins, while the relay records only that the lock happened—not the page contents.
- **path:** pendant → relay → mac-harness → browser
- **model tier:** realtime only to recognize the explicit command; deterministic extension and relay logic do the locking
- **latency:** Under 1 second to send the lock command and under 2 seconds for Safari to blank matching tabs; unlock on an explicit pendant press plus local presence check.
- **cost:** Near-zero model cost; modest extension UI/state work and encrypted short-lived lease storage.
- **security:** Ship disabled until the owner chooses origins; default to locking all authenticated tabs rather than guessing sensitivity. Unlock must require the pendant's authenticated session, never page text or a spoken secret. Keep recovery if the extension is offline, and do not claim that a browser tab is protected after its heartbeat expires.
- **missing:** Extension support for an origin-scoped lock screen or tab replacement and a reliable restore token; An authenticated pendant presence/lock signal and relay lease; An explicit owner-managed origin configuration (empty by default)

### "Before I do anything irreversible in Safari, tell me exactly what the page is about to send, charge, publish, or delete, in one short spoken sentence."
- **useful because:** The owner gets a last-moment, authenticated-page reality check from the only node that can inspect the live form and the only interface available while their hands are occupied. It is not a permission gate: after the explanation, the owner can proceed normally. This would be the system's most valuable browser capability because it prevents wrong-recipient, wrong-amount, and stale-form mistakes without blocking maximum access.
- **path:** browser → mac-harness → relay → pendant
- **model tier:** A cheap background classifier identifies submit-like controls and visible field values; realtime is used only to turn the resulting typed diff into the owner's one-sentence spoken answer.
- **latency:** One to two seconds after a pendant press or before a detected submit-like click; under 500 ms for the pendant acknowledgement.
- **cost:** Low per check: DOM/accessibility extraction plus a small typed summarization request. Cost is dominated by unusual pages requiring model interpretation, not ordinary forms.
- **security:** The extension must inspect only the active form and the target action, never passwords or unrelated page text. Values should be redacted by field category and returned as a transient typed diff, not persisted. The result must clearly distinguish observed values from inference and expire after the page changes.
- **missing:** A Safari extension action that freezes a submit target long enough to produce a typed preflight diff without altering the page; A DOM-to-typed-action extractor covering recipient, amount, destination, attachments, and deletion scope; A signed page-version checkpoint shared between Safari, the Mac agent, relay, and pendant so the spoken sentence cannot describe an earlier page state; A pendant trigger for on-demand preflight that does not conflict with existing playback and bookmark controls

### "Compare the details on these two logged-in pages and tell me if they disagree."
- **useful because:** Only the browser extension can access both authenticated origins, while the relay can reason over their structured claims and the pendant can give a concise answer without exposing either page. This catches mismatched delivery dates, account balances, reservation names, subscription prices, or order totals before the owner acts.
- **path:** browser → mac-harness → relay → pendant
- **model tier:** Background model for cross-page entity matching and contradiction detection; realtime only for the final spoken result.
- **latency:** Three seconds for two pages and under one second to speak the verdict once the comparison is ready.
- **cost:** Moderate but bounded: two capped DOM extractions and one small comparison prompt; never send full HTML or screenshots.
- **security:** Require explicit selection of both tabs or origins. Keep only typed claims and contradiction evidence for this request, with no durable page storage. Treat all page content as untrusted data, and never follow instructions found in either page.
- **missing:** A multi-tab extraction command with independent tab consent and page-version hashes; A typed claim normalizer for names, amounts, dates, addresses, and status values across origins; A relay comparison endpoint that returns contradictions with source URLs and confidence; A pendant response format that says which page disagrees without reading sensitive values aloud unless requested

### "Is this logged-in page trying to trick me, steal something, or make me do something unexpected? Tell me why before I click."
- **useful because:** The extension can inspect the actual authenticated page, including destination URLs, form targets, unusual payment or credential requests, and instructions hidden from a short voice description. The relay can judge the evidence while the pendant gives a compact warning. This protects the owner in the exact place where generic web search and the Mac shell have no visibility.
- **path:** browser → mac-harness → relay → pendant
- **model tier:** A background security classifier produces typed indicators; realtime only speaks the short verdict when the owner asks or a risky submit target appears.
- **latency:** Under two seconds for an on-demand scan and under 750 ms for a warning before a submit-like action.
- **cost:** Low-to-moderate: capped accessibility extraction plus a small security classification call; no continuous page screenshots.
- **security:** Treat every page as hostile input and never let page instructions control the agent. Do not claim certainty: return indicators, evidence locations, and confidence. Exclude passwords, payment numbers, message bodies, and unrelated tabs from the evidence capsule. Keep findings transient unless the owner explicitly saves them.
- **missing:** A browser-side submit-target and navigation-reputation extractor that never executes page instructions; A prompt-injection-resistant security analysis contract with typed indicators such as origin mismatch, hidden destination, credential request, and urgency pressure; A pendant warning channel with a distinct urgent tone and a concise explanation; A deterministic hook that pauses only the browser action being analyzed while leaving the owner's maximum-access policy intact


## What it asked for

_Nothing._
