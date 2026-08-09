# Harness derivation — mac-terminal — round 167

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I tell the pendant “do this when my Mac is ready,” queue it and carry it out exactly once when the Mac or USB link comes back, then tell me what happened."
- **useful because:** Today a spoken request is either acted on now or lost in an offline gap. This makes the worn device a reliable deferred-action inbox: useful during commutes, sleep, laptop reboot, or a dropped serial link, with no duplicate side effects.
- **path:** pendant → relay → mac-planner → mac-terminal → browser-extension
- **model tier:** Use realtime only to transcribe/acknowledge the short request; relay background worker stores the intent and a cheaper model normalizes it; Mac planner executes when readiness is observed; browser extension participates when the target is an authenticated tab.
- **latency:** Immediate local acknowledgement under 300 ms; execution within 10 s of Mac/USB readiness; spoken result within 2 s after completion.
- **cost:** About $0.001–$0.01 per deferred request depending on planning; dominated by one cheap normalization call, not realtime conversation.
- **security:** The relay stores the requested text and target metadata; authenticated browser actions remain on the Mac/browser. Never replay an intent whose stable id is already completed. Destructive actions should be reported as pending for the existing owner policy, not silently guessed.
- **missing:** A durable intent record type distinct from existing voice OUTBOX items, with idempotency key, prerequisite predicate (Mac online/USB present/browser session present), and exactly-once completion state; A Mac readiness event for bridge reconnect and process wake, plus a worker that claims queued intents; A typed serial heartbeat/identity route for the two physically connected boards

### "If something I asked the Mac to do fails, fix it yourself if there is a safe alternate path; otherwise tell me exactly what failed and what you need from me, without making me repeat the whole request."
- **useful because:** A failed shell/browser action currently leaves the owner with a vague failure and manual recovery. The pendant should feel like one agent: retain the original intent, inspect the concrete receipt, choose an alternate app/command/session, and report a truthful final state.
- **path:** pendant → relay → mac-planner → mac-terminal → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Cheap model classifies the failure and extracts exit code/stderr; realtime is used only for the final spoken update. Faculty judgement selects a recovery plan; Mac planner or browser executes it.
- **latency:** First failure diagnosis under 1 s after receipt; one automatic recovery attempt within 15 s; ask the owner only after that attempt.
- **cost:** $0.002–$0.02 per failed action; dominated by recovery planning, only paid on failures.
- **security:** A recovery must be constrained to the original intent and same target scope; do not broaden commands or switch authenticated accounts. Persist attempted alternatives and receipts so a crash cannot replay an already successful mutation. Data leaving the Mac is limited to redacted exit metadata and intent.
- **missing:** Exit code, signal, and termination reason in run_shell receipts; A durable job-to-ledger/action join and a preserved pre-rewrite action (the current shell rewrite can make the audit lie); A recovery planner contract with bounded alternate attempts and a final semantic outcome; Process cancellation that actually sends a signal to the child

### "When I say “hold this,” freeze the current Mac/browser work and let me resume it later from the pendant with one sentence, even after the Mac restarts."
- **useful because:** Long computer tasks and browser workflows lose their place when the owner is interrupted or closes the lid. A durable, spoken checkpoint would let the owner leave immediately and resume at the exact unfinished step rather than reconstructing tabs, files, and intent.
- **path:** pendant → relay → mac-planner → mac-terminal → browser-extension → faculty-perception
- **model tier:** Realtime handles the short hold/resume utterance; a cheaper background model summarizes the current action graph and extracts only resumable state; Mac/browser agents restore the session and continue.
- **latency:** A hold acknowledgement under 500 ms and durable checkpoint under 3 s; resume begins within 10 s of Mac/browser readiness.
- **cost:** $0.002–$0.015 per hold/resume, primarily summarization; no model call for a simple hold if action metadata is already structured.
- **security:** Checkpoint may include file paths, window/tab titles, and authenticated-session identifiers; encrypt it at rest and never copy page contents to the relay unless required. Resume must verify the same browser session and reject stale or changed page state instead of acting on a guessed target.
- **missing:** A first-class pause/checkpoint protocol in the executor and browser command queue (not merely a text note); Serialization of the current action cursor, pre/post state, and safe continuation boundary; Mac boot/browser readiness reconciliation that reattaches the checkpoint to a live session; Pendant command routing that distinguishes hold/resume from recording without delaying the active-edge capture

### "Remember the safe, repeatable Mac actions I use and run them instantly when I ask again—“same cleanup as last Friday,” “open my usual work setup,” or “repeat that check”—while showing me exactly which prior recipe you used."
- **useful because:** Repeated requests currently spend a full planning turn and may produce subtly different shell commands. A local recipe cache gives the owner faster, cheaper, more consistent help without sacrificing the unrestricted capability they deliberately chose.
- **path:** pendant → relay → mac-planner → mac-terminal → browser-extension
- **model tier:** Realtime resolves the short reference; a cheap local matcher selects a prior successful recipe. Use a larger model only when the reference is ambiguous or the environment has changed.
- **latency:** Known recipe dispatch under 500 ms after transcription; ambiguity question under 2 s; verify current app/browser preconditions before execution.
- **cost:** Near-zero for exact matches; $0.001–$0.01 only for ambiguous references or recipe extraction.
- **security:** Recipes can contain paths, account names, and browser targets. Keep them on the Mac, redact secrets, bind them to a project/session fingerprint, and refuse reuse if preconditions differ materially. Report recipe id and changed parameters in the spoken receipt.
- **missing:** A local successful-action recipe index with semantic names, preconditions, and stable action fingerprints; A deterministic match/preview route distinct from /plan so exact repeats avoid an LLM call; Recipe invalidation when browser tabs, project, or machine state changes

### "Let me say “try this safely” and have the Mac run a shell or file operation in a disposable shadow workspace, then tell me the exact predicted changes before anything touches my real files."
- **useful because:** The current unrestricted shell is powerful but makes experimentation costly: the owner cannot ask what a command would do without risking permanent changes. A shadow execution mode would make unfamiliar maintenance, migrations, and cleanup approachable from the pendant.
- **path:** pendant → relay → mac-planner → mac-terminal
- **model tier:** Realtime handles the short request; a cheap planner selects a shadow strategy; Mac-terminal performs the operation against an APFS clone or disposable directory and computes a semantic diff. Use the expensive tier only when the command cannot be isolated or the diff is ambiguous.
- **latency:** Preview for ordinary file operations under 10 s; command timeout bounded by the requested operation; spoken diff within 2 s after completion.
- **cost:** $0.001–$0.02 per preview, dominated by diff summarization; local APFS clone uses disk space rather than API spend.
- **security:** Some commands affect network services, keychains, hardware, or external accounts and cannot be shadowed honestly. Detect those effects, label the result 'not simulated,' and never imply safety. Keep clones local; do not upload file contents. Applying the predicted diff must be a separate explicit action.
- **missing:** A shadow executor that can create and destroy APFS snapshots or disposable workspaces and restrict external side effects; A command capability classifier that identifies operations which cannot be virtualized; A typed semantic-diff receipt that distinguishes observed changes from predicted changes

### "If the relay is unavailable but my pendant is plugged into my Mac, let me keep asking for private Mac help locally; sync the transcript and receipts to the relay only when the link returns."
- **useful because:** The owner is already physically wearing a device that can be attached to the Mac today, yet cloud or LTE loss currently turns it into a dead end. Local-only operation would preserve core command, status, and browser assistance during outages and keep sensitive requests off the network by default.
- **path:** pendant → mac-terminal → mac-planner → browser-extension → relay → faculty-perception → faculty-action
- **model tier:** A small local model handles intent extraction and routine Mac actions; use realtime only when a live relay conversation is available. Queue compact event and receipt records locally, then reconcile to the relay with idempotent sequence numbers.
- **latency:** Button-to-local acknowledgement under 500 ms; routine command start under 3 s; reconciliation within 30 s after relay recovery.
- **cost:** Zero network/API cost while offline for local model and typed actions; occasional cheap reconciliation call after reconnect.
- **security:** Local mode must clearly announce that cloud reasoning and remote browser coordination are unavailable. Keep sensitive transcripts and authenticated page data on the Mac; upload only records the owner has allowed. Prevent duplicate execution during reconciliation using stable intent IDs and monotonic cursors.
- **missing:** A USB serial audio/control protocol between the nRF9160, ESP32 bridge, and Mac local agent; An offline local planner/model with an explicit capability subset and local speech-to-text/text-to-speech path; A bidirectional outbox reconciliation protocol for intents, receipts, and conversation cursors; A browser extension mode that can accept commands without relay mediation

### "Make this a focus block: silence distracting Mac notifications, hide unrelated browser tabs, keep only the files and site I name, and restore my exact workspace automatically when the block ends."
- **useful because:** The owner currently has to coordinate macOS settings, windows, and browser tabs manually, and often forgets how to restore them. A spoken focus block would turn the pendant into a reversible boundary around attention, not just another command launcher.
- **path:** pendant → relay → mac-planner → mac-terminal → browser-extension → faculty-action
- **model tier:** Realtime parses the short focus request; a cheaper planner snapshots workspace state and emits typed Mac/browser operations; realtime is used only to announce start/end and exceptions.
- **latency:** Enter focus within 3 s; restore within 5 s of timer expiry or button request; no cloud round trip required once the plan is prepared.
- **cost:** $0.001–$0.01 per block for plan/diff generation; local state snapshot and restoration dominate no API cost.
- **security:** Snapshot may contain private window titles, URLs, and file paths; retain it encrypted on the Mac and expire it after restoration. Do not close unsaved documents or tabs; quarantine them and report exceptions. Restoration must be idempotent after a crash.
- **missing:** A reversible workspace transaction spanning macOS notification/focus state, windows/apps, and Safari tabs; Browser commands for hide/restore tab groups with stable tab identity, not just URL navigation; A timer/recovery daemon that restores state after sleep or agent restart and reports what could not be restored


## What it asked for

_Nothing._
## Its own summary

This round produced four non-identical owner-facing capabilities: deferred intent execution when Mac/USB/browser readiness returns; bounded automatic recovery with truthful failure reporting; spoken hold/resume of a Mac/browser action across interruption and restart; and a local recipe cache for instant, consistent repeats. I also proposed a USB-queryable execution trace, but the recorder correctly rejected it as overlapping the existing shell-ledger work. Live discovery confirms Safari is online with 9 tabs, the Mac bridge is online, and the cloudflare test device is offline. The newly granted mac_read_diagnostics schema still does not resolve in this runtime, even for basic checks.

**Biggest unknown:** The concrete USB serial protocol and typed diagnostic surface for the physically connected nRF9160 and ESP32 remain missing: identity, link state, heartbeat, counters, and compact receipt exchange. The prior mac_usb_serial_diagnostics request is still pending/denied, so I cannot verify or operate those ports through a safe typed interface. The four capabilities above all depend on that missing bridge event/receipt contract for reliable offline behavior.

