# Harness derivation — mac-terminal — round 278

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live-device-status** — The Mac bridge is online and Safari has one online tab; the nRF9160 pendant is currently offline at relay level. This makes Mac/browser workflows and USB bench work actionable now, but any proposal assuming LTE-registered wearable transport is false.
  - evidence: discover(devices) in round 278 returned home-macbook-bridge online, Safari on MacIntel online with 1 tab, nrf9160-pendant offline.

## Capabilities it proposed

### "“Continue the task that was running when the Mac or agent restarted, without doing any already-completed steps, and tell me exactly what resumed and what was skipped.”"
- **useful because:** Today a restart leaves jobs permanently marked processing, cancellation cannot stop an active shell, and the ledger is never closed or joined to its job. This would make long Mac/browser workflows dependable rather than silently abandoned or dangerously repeated. It is the single most useful reliability capability: the owner can launch a real task and trust that a crash is an interruption, not an invisible loss or duplicate side effect.
- **path:** relay → mac-planner → browser → pendant
- **model tier:** background for boot reconciliation and deterministic resume; realtime only to explain the resumed/skipped steps over the pendant
- **latency:** Reconcile within 5 seconds of local-agent boot; resume immediately after the owner asks or the configured policy permits it; spoken status under 2 seconds after querying
- **cost:** Near-zero model cost for ledger reconciliation and idempotency; one short realtime response only when the owner asks. Dominant cost is durable local bookkeeping, not inference.
- **security:** Resume only actions whose ledger replaySafety says safe and whose prior step is durably settled; never infer completion from a missing receipt. Persist a resume report locally and expose only the minimum command/output needed to the pendant. High-impact actions remain explicitly marked non-resumable and are reported as skipped.
- **missing:** Boot-time reconciliation that marks processing jobs interrupted instead of leaving them immortal; orchestrator closeLedger on every terminal path and a real planMeta.jobId join; Pass an abort signal to exec/execFile so cancellation can actually terminate a child; Per-action idempotency enforcement wired to executionContext, plus a typed resume report

### "“Send this exact authenticated webpage to my iPhone so I can continue there, preserving the page, selected text, and the reason I wanted it.”"
- **useful because:** The browser has sessions the relay cannot reach and the iPhone has the owner's mobile context, but today the handoff between them is manual. A pendant request could capture the active Safari tab and selection, create a provenance-backed handoff artifact, then use Mac iPhone Mirroring to open/share it on the real phone. This is only possible by combining browser authority, Mac control, iOS control, and the always-available relay.
- **path:** pendant → relay → browser → mac-planner → ios
- **model tier:** background/cheap model to package title, URL, selection, and provenance; realtime only for the short confirmation and failure explanation
- **latency:** Capture and stage in under 3 seconds; phone handoff in under 10 seconds; if iPhone is unavailable, retain a queued handoff and tell the owner immediately
- **cost:** Usually one small model call for a concise handoff note; dominant work is browser command round-trips and iPhone Mirroring, not tokens
- **security:** Never copy page body by default. Transfer URL, title, explicit selected text, and source/provenance record only; warn if the page is a sensitive authenticated host. Require the owner’s spoken confirmation only when the destination app or share target would expose content outside the device. Queue encrypted local metadata if the phone is offline.
- **missing:** A typed browser export/handoff artifact route that accepts URL, selection, provenance ID, and destination; An iOS action for opening a URL or receiving a local handoff payload through the existing Mirroring harness; A relay command that binds one pendant utterance to the currently focused browser tab without guessing among tabs

### "“That Mac action failed—diagnose the real cause, repair only the failed step, and finish the task without rerunning steps that already changed anything.”"
- **useful because:** The current shell path flattens exit status, drops pid and environment provenance, and has no retry; a failure is often reported as an opaque string and the owner must start over. A failure-aware repair loop would inspect structured stderr/exit code and the durable action receipt, choose a safe correction (for example the missing project cwd or a transient browser host), and continue exactly from the failed step. It makes the Mac feel like an agent that recovers, not a command launcher.
- **path:** pendant → relay → mac-planner → browser
- **model tier:** cheap model for classification and deterministic repair candidates; realtime only for ambiguous or irreversible repairs
- **latency:** Diagnosis under 1 second after failure; one bounded repair attempt within 10 seconds; stop and report rather than loop after a single unsuccessful repair
- **cost:** One small inference only on failures; normal successful tasks cost nothing extra. Dominant cost is collecting bounded stderr and a second action execution.
- **security:** Capture exit code, signal, pid, cwd, argv and a salted environment fingerprint—not secret environment values. Retry only the failed step with an idempotency key and never replay a settled mutation. Keep raw command output local; send a redacted failure capsule to the relay. Do not auto-repair destructive or externally visible actions.
- **missing:** Structured shell receipts containing exit code/signal/pid and original-vs-rewritten action; Failure classifier and one-attempt repair planner wired to executionContext idempotency; A durable step cursor that distinguishes failed, settled, and unknown-after-crash states

### "“Make this page safe to share with my colleague, show me exactly what was removed, and put the sanitized copy on my iPhone without sending anything.”"
- **useful because:** The browser can reach authenticated content, while the Mac and iPhone can move it between surfaces, but the owner cannot currently ask the system to perform a privacy-preserving handoff. This would turn a risky copy/paste workflow into a reviewable transformation: identify secrets and personal data, produce a reversible redaction preview, and stage—not transmit—the result on the phone.
- **path:** pendant → relay → browser → mac-planner → ios
- **model tier:** background model for local redaction and classification; realtime only to read the short diff and ask for confirmation if confidence is low
- **latency:** Preview in under 8 seconds for a normal page; no external send until the owner explicitly confirms after seeing the diff
- **cost:** One moderate model call over extracted claims rather than the whole page; browser and phone orchestration dominate latency
- **security:** Process authenticated page contents locally where possible. Never upload the unsanitized page to the relay. Keep original and sanitized artifacts separate, attach source URL and redaction reasons, and require confirmation before any share/send action. Treat credentials, tokens, financial identifiers, and private names as high-sensitivity.
- **missing:** A local structured redaction engine with deterministic detectors and confidence-scored model findings; A reviewable artifact/diff format that the iPhone harness can open without sending; A browser-to-Mac byte handoff for selected content with provenance and content sensitivity labels

### "“At the end of the day, show me every change the hive made on my Mac, browser, and phone, with the before-and-after evidence, and let me undo only the changes I choose.”"
- **useful because:** Today receipts, jobs, browser provenance, and phone actions are separate. The owner cannot get one trustworthy account of what the whole system changed, especially when several nodes acted in sequence. A cross-surface change ledger would make delegation safe to use daily: it would identify each mutation, show evidence of its result, and offer selective reversal rather than an all-or-nothing undo.
- **path:** relay → mac-planner → browser → ios → pendant
- **model tier:** background model to summarize and cluster completed receipts; deterministic code owns the ledger, evidence hashes, and undo routing
- **latency:** Continuously append receipts; daily digest generated in under 5 seconds and read in under 30 seconds; individual undo status under 2 seconds
- **cost:** Small summarization call per digest; storage and evidence capture dominate cost, with no realtime inference required for normal use
- **security:** Keep raw screenshots, page text, and phone content local. Store hashes, timestamps, actor surface, target, and reversible operation metadata in the relay-visible summary. Mark irreversible actions honestly and never fabricate a before-state. Selective undo must refuse when the target has changed since the original mutation.
- **missing:** A shared cross-surface action identity and append-only change ledger; Before/after evidence adapters for Mac, browser, and iOS actions; Conflict-aware selective undo that checks current state before reversing a mutation; A pendant-readable digest and stale/irreversible-state vocabulary

### "“Before you submit this form, verify every field against what I said, flag anything the website changed or inferred, and tell me the exact final payload.”"
- **useful because:** Authenticated browser forms are where a small model mistake can become a real-world commitment. The owner can ask the system to fill fields today, but cannot obtain a semantic contract check between spoken intent, the rendered form, and the final submission payload. This capability would catch stale pages, hidden defaults, altered totals, and mismatched recipients before the irreversible click.
- **path:** pendant → relay → browser → mac-planner
- **model tier:** background model for field-level comparison and anomaly explanation; realtime for the final spoken summary and explicit submit confirmation
- **latency:** Validation in under 3 seconds after the form is filled; final payload summary under 10 seconds for complex forms
- **cost:** One small structured comparison call per submission; browser snapshots and DOM extraction dominate latency
- **security:** Keep secrets and full field values local; send the relay only field labels, sensitivity classes, hashes, and mismatches. Never log passwords, payment numbers, or tokens. Treat submit as a separate action from fill and refuse to claim success until the browser reports the resulting state.
- **missing:** A browser DOM/form serializer that captures visible, hidden, defaulted, and disabled fields with provenance; A spoken-intent-to-field schema with typed values and uncertainty rather than free text; A pre-submit transaction barrier that computes and presents the final payload before dispatch; Post-submit verification tied to the same form transaction


## What it asked for

_Nothing._
