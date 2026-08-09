# Harness derivation — mac-planner — round 295

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-accessibility-and-screen-recording** — Both Accessibility and Screen Recording are now granted to AI Pendant Agent; ops status reports trusted/granted and requiredMissing=[]; browser and relay are online. This supersedes the older denied context.
  - evidence: GET /ops/status returned permissions.accessibility.trusted=true, screenRecording.granted=true, ready=true; GET /browser/status returned online=true with one Safari tab.

## Capabilities it proposed

### "When I press the bookmark button, later show me exactly what I was looking at and doing at that moment, turn it into a short titled note with source links, and suggest one follow-up — without recording ambient audio unless I enabled it."
- **useful because:** A physical bookmark currently marks time but leaves the owner to reconstruct context. Joining the pendant event to Mac/browser evidence makes a fleeting idea recoverable in one pass, especially when the owner is away from the keyboard when inspiration strikes.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use the realtime model only to acknowledge the button event; use a background model for event correlation, title/summary, and follow-up extraction. Let the Mac agent do deterministic context collection and note creation.
- **latency:** A local LED acknowledgement immediately; upload when connected. Context reconstruction within 30 seconds of link return, with a one-sentence spoken notification and an editable note shortly after.
- **cost:** Low: one background summarization call per bookmark, dominated by context payload length; deterministic Mac/browser reads and one note write are negligible.
- **security:** Context can include private page titles, selected text, and window names. Default to metadata and URLs, redact page bodies/password fields, and retain only the resulting note plus provenance. Never include ambient audio unless the existing bookmark setting explicitly enabled it. Creating a note is owner-authorized; external sending remains confirmation-required.
- **missing:** A durable bookmark-to-context correlation route carrying the pendant event timestamp and device id; A semantic Mac context read for window/document identity and selected text (the pending request is not granted); A browser effect/context preview that can return the active page metadata at a historical timestamp rather than only the current tab

### "Take care of this end to end: understand what I am referring to from my current Mac and browser context, prepare the needed files or web form, and stop only at the exact irreversible step so I can approve or change it by voice."
- **useful because:** The owner should not have to translate a spoken intention into app names, URLs, file paths, and intermediate steps. The pendant supplies intent and approval, the relay supplies judgment, and the Mac/browser supply reach; together they can complete the reversible 90% while making the final consequence legible.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Realtime for the short clarification/approval exchange; a cheaper background model for context grounding and plan generation; deterministic preflight and action execution on the Mac; browser extension for authenticated pages.
- **latency:** Context snapshot and a concrete plan in under 8 seconds; reversible preparation in under 30 seconds; approval prompt must name the exact recipient, file, amount, or submission before execution.
- **cost:** One small planning call plus one short approval turn per task; browser and Mac operations dominate wall time, not token cost. Reuse the same context snapshot through the plan to avoid resending it each turn.
- **security:** The current FULL_CONTROL path has no live approval gate, so this must not silently execute the final mutation. The action ledger needs an explicit irreversible boundary, redacted previews, idempotency key, and a durable expiry. Reads and reversible drafts may follow owner policy; sending mail, deleting, purchasing, or submitting must require an affirmative pendant response.
- **missing:** A server-to-Mac plan schema that marks the irreversible boundary and idempotency key; Semantic context read for the active document, selection, and browser form rather than a screenshot alone; A browser effect preview that reports the exact mutation before submit; A pendant approval/decline event path with timeout and replay protection

### "Run an end-to-end pendant health check when I ask, then tell me whether the audio path, radio link, and Mac bridge are healthy; if something fails, collect a redacted evidence bundle and draft the exact bug report with the next bench command."
- **useful because:** Today a failure can be anywhere across the worn device, USB bench link, relay, or Mac, and the owner must be the integration engineer. One command should turn opaque symptoms into a bounded diagnosis and an actionable report, rather than another vague 'try again.'
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** Use the device's deterministic audio_path_diagnostic_fixture and duplex counters for measurements; use a background model only to classify the evidence and write the human report. Realtime should speak only the result and one next action.
- **latency:** Local fixture starts immediately; a compact result within 20 seconds over USB or link, and a complete report within one minute. It must be cancellable by the pendant button.
- **cost:** Near-zero model cost for healthy checks; one short background call only on anomaly. Storage is a small compressed receipt, not microphone audio.
- **security:** The fixture must never capture or retain microphone content. Redact bearer tokens, URLs, account identifiers, and raw serial payloads from the report. Running a bench command can mutate firmware or hardware state, so report it as a proposed command and require the owner's explicit approval before execution.
- **missing:** A reliable trigger and result contract that can invoke the accepted fixture over today's USB-connected bench without pretending LTE registration; A cross-node health schema joining pendant counters, relay websocket state, Mac bridge status, and browser status; A redacting evidence-bundle writer and a bug-report draft destination in ~/AI-Pendant-Workspace; A bounded command runner that returns exit code and output receipt for the suggested bench command

### "Use my saved information to fill a form or checkout, but never reveal the underlying secrets to the model or relay; show me only the fields and final effect, then let the browser submit it."
- **useful because:** The system can reach authenticated browser sessions, but today any automation that needs a password, payment detail, address, or private identifier must either expose it to an agent or stop being useful. This would make high-value private automation possible without turning the language model into a secret holder.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use a background model to map the user's intent to form fields. Secret lookup and insertion must be deterministic, local to the Mac/browser vault boundary, and unavailable to both relay and model. Realtime only handles the short spoken confirmation.
- **latency:** Field mapping and a redacted preview within 10 seconds; local secret insertion should be near-instant; submission only after the owner hears the exact destination and consequence.
- **cost:** One small planning call per form; vault lookup, browser fill, and redacted preview are local. Cost is dominated by browser-page context if unusually complex.
- **security:** This is explicitly not ordinary autofill. Secrets must be released only to an allowlisted browser origin and field signature, never placed in logs, model context, screenshots, receipts, or relay payloads. Payment, account creation, and final submission require a fresh pendant-bound approval. Site changes, replay, clipboard leakage, and malicious form labels require origin pinning and human-readable field previews.
- **missing:** A browser-side secret broker with origin and field binding; A redaction-preserving form semantic model and effect preview; A Mac-local vault integration that returns write-only handles rather than values; A pendant-bound approval token that authorizes one exact origin/form/action

### "Let one deliberate press of my pendant authorize exactly this one risky action on my Mac or in my authenticated browser, and automatically revoke it if the plan, destination, or form changes."
- **useful because:** Voice approval is easy to mishear and a server-side approval can be replayed after the owner has forgotten it. A physical, one-shot authorization bound to the exact planned effect gives the owner a reliable 'yes, this and nothing else' control while away from the keyboard.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** The relay creates a canonical action digest; the pendant signs or MACs that digest using device-held key material; the Mac/browser verifies it locally. No model is needed for authorization, and realtime only explains the preview.
- **latency:** Digest and spoken preview in under 5 seconds; button authorization applied in under 2 seconds. Any changed URL, recipient, amount, file hash, or action order invalidates the token immediately.
- **cost:** Negligible model cost after the original plan; cryptographic verification is local. Hardware work is limited to secure key storage or a protected device identity, depending on the pendant's available security primitives.
- **security:** The private key must never leave the pendant. Tokens need nonce, expiry, action digest, origin, and monotonic counter to prevent replay. Lost-device recovery and key rotation are mandatory. This complements—not replaces—owner policy, and destructive actions should remain auditable.
- **missing:** Pendant firmware support for a non-exportable device key and signed one-shot approval event; A canonical cross-node action digest covering browser effects and Mac mutations; Mac/browser verification middleware that rejects stale or changed plans; A durable revocation and key-rotation path through the relay

### "For anything you create or change on my Mac, let me ask 'why is this here?' from the pendant and hear a short provenance trail: what I said, which sources you used, what actions ran, and what changed from the original."
- **useful because:** Automation becomes trustworthy when the owner can inspect the origin of a file, draft, or browser change after the moment of action. Current receipts describe jobs, but they do not give the owner a human-scale, cross-node explanation attached to the resulting artifact.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Collect hashes, timestamps, URLs, action types, and before/after metadata deterministically. Use a background model only to compress that evidence into a short spoken explanation; never let the model invent missing provenance.
- **latency:** Provenance should be written atomically with each mutation. A spoken answer should arrive within 5 seconds for a local artifact and clearly say when evidence is unavailable.
- **cost:** Small background summarization call only when queried; receipts and hashes are local storage. Browser source metadata may dominate payload size, so retain references rather than page bodies.
- **security:** Provenance can itself reveal private URLs, mail subjects, or document names. Apply the existing redaction layer, enforce per-artifact access scope, and never expose secret form values. If an action lacks evidence, say 'unknown' instead of fabricating a trail.
- **missing:** An artifact-attached provenance manifest with before/after hashes and source references; A common event identifier joining relay intent, browser command, Mac job, and workbench transaction; A pendant query path that retrieves a redacted provenance summary without replaying private source content; Atomic persistence so a file cannot appear committed without its provenance receipt

### "When I correct you by voice, apply that correction to the right future tasks across my pendant, Mac, and browser, tell me exactly what behavior it changes, and let me undo it later without erasing the original evidence."
- **useful because:** A correction made during a live interaction currently disappears into a single conversation or becomes an opaque memory. The owner should be able to teach the whole hive once—such as a naming convention, a preferred source, or a recurring exception—without accidentally changing unrelated automation.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use realtime only to acknowledge and disambiguate scope. A background model can propose the rule and examples, but deterministic scope matching, versioning, and rollback must be handled by the relay and local agents.
- **latency:** A proposed correction rule within 5 seconds; no future behavior changes until the owner confirms scope. Propagation to online nodes within seconds and replay to an offline pendant on reconnect.
- **cost:** One short background call per correction and negligible storage for versioned rules; future tasks become cheaper because the correction is not resent as conversational context every turn.
- **security:** Corrections may contain sensitive facts or overbroad instructions. Store scope, provenance, confidence, and expiry separately; never let a rule silently authorize destructive actions or leak private data. Redact the spoken evidence according to the existing memory policy and provide a one-command rollback.
- **missing:** A versioned, scoped correction/rule store with provenance and rollback; A relay fan-out protocol for syncing rule versions to pendant, Mac, and browser; A confirmation UX that previews affected task classes and example consequences; Rule-evaluation hooks in planning, browser automation, and Mac routines


## What it asked for

_Nothing._
