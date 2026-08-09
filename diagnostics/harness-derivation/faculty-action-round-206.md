# Harness derivation — faculty-action — round 206

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### ""That partially failed. Clean up whatever you changed, keep anything I might need, and tell me exactly what remains.""
- **useful because:** Today a multi-step action can leave a half-applied calendar, file, or browser workflow: receipts say what ran, but nothing safely compensates successful reversible steps after a later failure. This gives the owner a truthful, bounded recovery instead of a mysterious partial state.
- **path:** faculty-judgement → relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-action
- **model tier:** background for constructing the compensation plan; realtime only for the owner's short clarification
- **latency:** Plan within 2 s; each compensation step within 5 s; stop immediately on an unverifiable postcondition
- **cost:** Usually 1 cheap planning call plus verifier calls; roughly $0.01-$0.05, dominated by model planning and fresh verification
- **security:** Only explicitly reversible compensations may run automatically. Never undo sends, purchases, deletions, or other irreversible steps. Every compensation is tied to the original operation ID and independently verified; ambiguous recovery is staged for physical approval.
- **missing:** A compensation graph/inverse descriptor on each executable action; An executor primitive that can run verified compensation steps and stop on first unknown; A durable recovery record linking original receipts, compensation receipts, and verifier provenance

### ""Undo the last thing you did for me, but don't touch anything else.""
- **useful because:** An owner can recover from an accidental reversible action without remembering which app or workflow produced it. The system finds the newest still-reversible ledger entry, checks that the current state still matches its expected undo preconditions, performs only that inverse, and reports verified/unknown rather than pretending success.
- **path:** relay-realtime → faculty-judgement → faculty-perception → faculty-action → mac-planner → browser-extension
- **model tier:** realtime for resolving 'last thing' and presenting a one-line summary; background for inverse lookup and verification
- **latency:** Identify candidate in under 1 s; require one deliberate pendant approval for anything beyond low-risk reversible changes; complete and verify within 8 s
- **cost:** Low: ledger lookup plus 1-3 verifier/action calls, about $0.005-$0.03; browser state reads dominate latency
- **security:** Never infer an inverse from natural language alone. Require an action type with a declared inverse, a matching current-state hash, expiry, and scope boundary. If multiple candidates or state drift exist, do nothing and ask. Sensitive messages and destructive operations are never auto-undone.
- **missing:** A canonical inverse registry for mac/browser action types; A 'latest reversible action' query that returns candidate, scope, expiry, and preconditions without secrets; A safe inverse executor that records a new linked ledger entry

### ""Which of these is the file/person/tab I meant?" followed by a wheel turn and one press on the pendant."
- **useful because:** Ambiguous references are a daily failure point: the Mac can find candidates but the owner has no private, low-friction way to choose one while away from the keyboard. The relay presents a numbered, redacted candidate list; the pendant's future rotary input selects one; Mac/browser then acts on the exact opaque ID.
- **path:** relay-realtime → faculty-perception → faculty-judgement → faculty-action → mac-planner → browser-extension
- **model tier:** realtime for candidate ranking and a terse spoken/tactile prompt; background for fetching and redacting candidate metadata
- **latency:** Candidate list in 2 s; each wheel event acknowledged locally under 100 ms; execute only after selection and, for risky actions, physical approval
- **cost:** About $0.01-$0.04 per disambiguation, mostly candidate ranking; local wheel events are negligible
- **security:** Pendant receives only opaque IDs and short labels, never page secrets or file contents. Candidate lists expire quickly and are bound to the originating operation and current app/session. A stale selection must be rejected rather than applied to a changed list.
- **missing:** A rotary encoder and second product button (not yet purchased; explicitly owner direction); Pendant firmware input protocol for bounded candidate-list navigation and selection; A redacted candidate enumeration route across Finder, Calendar, Mail, and browser sessions; Selection token binding and verifier postcondition for the chosen opaque target

### ""What actually changed while I was away? Show me only the differences, across my Mac and browser, and link each difference to the action that caused it.""
- **useful because:** The system can retain receipts and verify individual postconditions, but the owner still cannot get a single trustworthy before/after account across Finder, apps, and browser sessions. A cross-surface change digest would answer the practical question after unattended work without forcing the owner to inspect every app.
- **path:** faculty-perception → faculty-judgement → faculty-action → mac-planner → browser-extension → relay-realtime
- **model tier:** background for collecting and comparing state; realtime only to summarize the already-built digest
- **latency:** Generate within 10 seconds of a job finishing, or on demand within 20 seconds; omit any surface whose baseline is missing rather than guessing
- **cost:** About $0.02-$0.08 per digest, dominated by state collection and diff summarization; hashes and structured diffs keep token use low
- **security:** Private content stays on the Mac/browser; relay receives typed change records, hashes, and owner-approved snippets only. Baselines are scoped to one operation and expire. A missing baseline must produce 'not measured', never 'unchanged'.
- **missing:** A pre-operation state snapshot contract for files, app state, browser fields, and URLs; A cross-surface diff schema linking each changed item to operation and step IDs; A redaction policy and owner-facing digest renderer that can omit secret values while retaining proof of change

### ""If any part of this request touches a private page or file, let me approve the exact fields before you send or save anything.""
- **useful because:** The owner needs a usable middle ground between refusing all private workflows and handing an agent unrestricted page/file contents. The system should identify sensitive fields locally, show redacted labels and values on the Mac, and let the pendant approve only a field-level digest; unrelated fields remain inaccessible and untouched.
- **path:** faculty-perception → faculty-judgement → faculty-action → mac-planner → browser-extension → relay-realtime
- **model tier:** realtime for the short approval conversation; local/background models for field classification and redaction
- **latency:** Detect and present the field manifest within 3 seconds; apply an approval or refusal within 5 seconds; no field write before the signed approval arrives
- **cost:** About $0.01-$0.05 per sensitive workflow; local classification and hashes dominate, not audio
- **security:** The pendant receives labels, sensitivity classes, and digests, never secrets. Approval is bound to field locator, destination, normalized value hash, expiry, and operation ID. Any DOM/file change invalidates it. Clipboard and screenshots are prohibited in the approval path.
- **missing:** Field-level sensitivity classification for browser forms and file operations; A redacted approval manifest renderer on the Mac; An executor that accepts only approved field digests and rejects any changed value; A verifier postcondition for the exact destination field/file mutation


## Changes it proposed to its own stack

### `hardware` — Add a dedicated secure element (for example, an ATECC608-class device) to the pendant and provision a non-exportable device key used to sign physical approval, cancellation, and outcome acknowledgements. Bind signatures to transaction nonce, operation digest, monotonic counter, expiry, and device boot identity; keep page contents and form secrets out of the pendant. Add firmware anti-replay checks and a factory recovery path that invalidates a lost pendant key.
- **owner gets:** A deliberate press on the pendant would remain trustworthy even if the relay, Mac agent, or firmware update path were compromised. Today the owner has a physical approval concept, but not a hardware root that makes a forged approval distinguishable from their real gesture.
- effort: Moderate hardware spin and firmware/relay protocol work: I2C wiring, secure provisioning, signed-envelope verification, key rotation and manufacturing recovery. Bench prototype first, then enclosure revision.  ·  risk: Provisioning mistakes could permanently lock out the pendant; losing the device would require recovery. Mitigate with per-device keys, a documented revocation path, test keys never used in production, and fail-closed verification. Do not silently migrate existing approvals without a protocol version.
- cost: Roughly $1-$3 per unit plus PCB/enclosure revision; negligible steady-state power, with brief I2C current during signing.  ·  latency: Approximately tens of milliseconds per signature, acceptable within the existing approval window; no impact on audio streaming.
- security: Substantially improves authenticity and replay resistance. It does not make a compromised owner Mac trustworthy, so server-side postcondition verification remains required.
- depends on: A production pendant PCB/enclosure rather than the current DK bench wiring; A versioned signed approval envelope and device-key registry; A secure provisioning and revocation procedure


## What it asked for

### `s12-1eum` (skill) — motion_context_safety_gate
- does: Samples the owned LSM6DSOX IMU while an action approval is pending, classifies only coarse motion states (stationary, walking-like motion, vigorous motion, sensor unavailable), and emits a compact signed context event. It never infers location, records raw motion, or approves an action. For high-risk transactions it gives a distinct local haptic/audio cue and refuses to return an approval token while vigorous motion is present; the relay may re-present the pending transaction when stationary.
- must be on-device because: The pendant is the only surface physically worn by the owner and can observe movement while the Mac/browser are remote or asleep. Sending raw accelerometer data to the server would be invasive and would add latency; the safety classification must survive a link interruption and run locally.
- trigger: A pending physical transaction approval envelope arrives, or the IMU detects transition into/out of vigorous motion during the bounded approval window.
- storage: Persist only the last coarse state, transition timestamp/monotonic counter, and pending transaction association in the existing small inbox/approval record; under 128 bytes plus one queued event per pending transaction. Never persist raw samples.
- RAM budget: A fixed 1-second ring of decimated 6-axis int16 samples (at 25 Hz, about 900 B), classifier state under 1 KB, and one event record under 256 B; target under 3 KB, well below the 211,608 B application RAM budget. Enable i2c2 and integrate the already-owned IMU; no new hardware.

## Its own summary

Round 206 produced three actionable cross-surface capabilities: (1) verified compensation after a partially failed multi-step operation, (2) a narrowly scoped 'undo last reversible action' flow, and (3) rotary-encoder disambiguation of files/people/tabs using opaque candidate IDs. I also queued motion_context_safety_gate (s12-1eum): the owned IMU locally blocks high-risk approval while vigorous motion is detected, without storing raw motion. The recorder warned that compensation is close to an existing partial-failure idea and undo is close to that new compensation proposal, so these should be merged or differentiated rather than independently implemented.

**Biggest unknown:** The owner still needs to decide whether automatic compensation is acceptable for any action class; absent that policy, default must remain stage-for-approval. The rotary candidate picker additionally needs the planned encoder/second button. For motion gating, the unresolved engineering question is whether the LSM6DSOX is electrically wired and what stationary/vigorous thresholds are safe; firmware must validate those on the bench before enabling it.

