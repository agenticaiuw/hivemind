# Harness derivation — mac-planner — round 194

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-accessibility-state** — AI Pendant Agent now has Accessibility and Screen Recording; synthesized input is verified posting and UI actions should reach the screen. Foreground app is Claude; 18 apps are running; three durable browser sessions exist.
  - evidence: mac_readonly_inspect(operation=running_apps) invoked GET /observe at 2026-08-08T02:36:03.890Z and returned accessibility.trusted=true, screenRecording=true, eventsPost=true, inputReachability.status=verified.

## Capabilities it proposed

### "When I press the bookmark button and say “save what I’m looking at,” make a durable record of the exact work context I was in, not just the time."
- **useful because:** The existing moment bookmark preserves a timestamp, but later the timestamp alone cannot recover the thought. This joins the worn event to live Mac and browser context so the owner can return to the actual document, app, and page that caused the idea.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Background model for enrichment; realtime only acknowledges the button and confirms capture.
- **latency:** Acknowledge the button immediately; enrich and persist the context within 5 seconds.
- **cost:** About $0.002–$0.01 per bookmark, dominated by optional page/document summarization; raw state capture is negligible.
- **security:** The bundle may contain sensitive URLs, window titles, or selected text. Default to redacted metadata (app, domain, document basename), encrypt in transit, and require an explicit spoken opt-in for selected text or page content. Never capture passwords or secure-input fields.
- **missing:** A resolved mac semantic-inspection operation for document identity/selected text (the current ui_snapshot is available, but semantic selection is not); A deterministic browser-inspect dispatch (browser_tabs currently ties between two live capabilities); A ledger endpoint that stores the joined bookmark/context bundle with retention controls

### "If an alert arrives while I’m in a meeting or handling a sensitive screen, hold it safely and tell me the first moment it is safe to hear it; if I’m free, read it immediately on the pendant."
- **useful because:** This is not just an inbox: it prevents an urgent notification from interrupting a call or exposing private content aloud. The Mac knows foreground apps and secure-input state, Calendar knows meeting windows, and the pendant is the only surface that can deliver without opening another device.
- **path:** relay → mac-planner → pendant → dashboard
- **model tier:** Rules and a small background model for urgency classification; realtime is used only for the spoken acknowledgement.
- **latency:** Evaluate delivery safety within 2 seconds of an alert and re-check at meeting end or foreground-app change.
- **cost:** Under $0.001 per alert for rules; roughly $0.003 when summarization/classification is needed.
- **security:** Alert text must not be sent to the pendant speaker when secure input or a sensitive app is active. Keep full text server-side, send only a short classified payload, expire held alerts, and expose a dashboard audit trail. The owner must configure which apps/domains count as sensitive.
- **missing:** A relay-to-Mac push subscription for foreground/secure-input changes (polling is insufficient); Calendar event-to-interruptibility evaluation tied to the existing pendant alert inbox; Owner-configurable sensitive-app/domain and urgency policy

### "Do this multi-step cleanup overnight, verify the result on the Mac, and wake me on the pendant only if the promised end state is not true."
- **useful because:** Today a server plan can be handed to the Mac, but completion is often inferred from an action response rather than checked against the real desktop. This makes unattended work dependable: stage atomically where possible, execute, inspect the postcondition, retry idempotently, and surface one concise failure alert instead of making the owner babysit the Mac.
- **path:** relay → mac-planner → mac-vision → pendant → dashboard
- **model tier:** Cheap background planner for decomposition and verification; realtime only for the owner's follow-up conversation.
- **latency:** Start within 10 seconds; ordinary jobs finish in minutes. Alert within 30 seconds of a failed postcondition or retry exhaustion.
- **cost:** Approximately $0.01–$0.05 per job, dominated by planning and one verification pass; no model call for deterministic file-only jobs.
- **security:** Unattended actions can mutate or delete data. Owner must define an explicit routine policy and allowed roots/apps; preflight must show touched resources, workbench jobs need idempotency keys, and failure alerts must redact filenames/content where configured. No claim of success without a fresh inspection receipt.
- **missing:** A relay scheduler/lease that survives Mac sleep and reconnects without duplicating a job; A typed postcondition verifier spanning app state, browser state, and file hashes; A pendant alert payload for failure receipts, plus owner-configured unattended-action policy

### "Before a browser action sends money, publishes, or submits sensitive information, show me a plain-language summary on the pendant and let one deliberate button press authorize exactly that action."
- **useful because:** The Mac and browser can reach authenticated sessions, but the owner has no independent physical checkpoint against a wrong tab, stale page, prompt injection, or accidental click. A small pendant display is unnecessary: the relay can speak the destination, action, and key values, then bind one physical press to one browser command.
- **path:** browser → relay → pendant → mac-planner → dashboard
- **model tier:** Realtime model for concise spoken disclosure summary; deterministic browser/session code for page identity and command binding.
- **latency:** Summary in under 2 seconds; authorization expires after 30 seconds and applies to one exact command only.
- **cost:** <$0.01 per checkpoint; dominated by extracting and summarizing the form/action fields.
- **security:** Never read passwords or full payment numbers aloud; redact secrets and retain only a hash of the approved command. Bind approval to tab ID, origin, DOM action fingerprint, and expiry so replay or navigation cannot reuse it. Default-deny when page identity changes.
- **missing:** A browser command protocol that can pause a pending submit and accept a cryptographically bound pendant approval; A relay primitive tying one physical button edge to one browser command hash; A compact, owner-configurable disclosure policy for financial, publication, and sensitive-data actions

### "Let me leave my desk mid-task, then later say “put me back where I was,” and have the Mac restore the exact app, browser tab, document position, and unsent draft without sending or losing anything."
- **useful because:** A bookmark or job receipt records that something happened, but it does not restore the owner's working state. This would make the pendant a physical continuity key between interruptions, sleep, and changing machines while keeping unsent work local and private.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Background model only for naming the task and resolving ambiguity; deterministic state capture/restoration does the actual work.
- **latency:** Capture on request in under 3 seconds; restore within 10 seconds, with a preview before any destructive navigation.
- **cost:** <$0.005 per checkpoint, mostly storage; no model call for deterministic app/tab/file state.
- **security:** Draft text and document paths can be sensitive. Encrypt state, redact content by default, keep payload on the Mac where possible, and make restoration non-destructive: never overwrite a changed file or submit a form. Expire checkpoints by owner policy.
- **missing:** A durable Mac state checkpoint format covering app windows, document cursor/scroll, browser tab identity, and draft buffers; Browser APIs to restore tab state without relying on fragile mouse coordinates; A pendant-linked checkpoint selector and conflict-aware restore protocol

### "If I say “I lost the pendant” or hold its privacy control, immediately revoke its sessions, stop all audio, invalidate pending browser and Mac commands, and show me a recovery checklist on my Mac."
- **useful because:** A local privacy latch protects the microphone and speaker, but loss of a connected wearable can leave queued commands, browser authority, or relay sessions alive. This is a whole-hive incident response that no single node can perform: the pendant signals locally, the relay revokes centrally, and the Mac/browser quarantine their pending work.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Deterministic policy engine; realtime model only interprets the spoken loss report and confirms state.
- **latency:** Local mute immediately; relay revocation and Mac/browser quarantine within 5 seconds, with repeated retry until receipt.
- **cost:** <$0.002 per incident; dominated by durable revocation writes and delivery retries.
- **security:** Loss mode must be resistant to accidental activation and require a recovery secret or separately authenticated Mac session to clear. Preserve an audit receipt without retaining audio. Never trust a reconnecting device until re-paired; invalidate queued audio and command payloads, not merely the websocket.
- **missing:** A cross-node revocation epoch understood by pendant firmware, relay, browser bridge, and Mac agent; An emergency command path that works when LTE is unavailable but the pendant is USB-attached; Browser/Mac cancellation hooks for already queued commands and a durable recovery UI


## What it asked for

_Nothing._
## Its own summary

This round produced three new cross-node capabilities: (1) bookmark-to-context evidence bundles joining the worn bookmark with live Mac/browser state, (2) interruptibility-aware alert delivery that withholds spoken alerts during meetings or sensitive screens, and (3) unattended overnight Mac jobs with atomic staging, postcondition verification, retry, and pendant-only failure alerts. I also re-checked the live Mac: Accessibility and Screen Recording are now granted and synthesized input is verified, so UI automation is no longer blocked. The browser currently has three durable sessions, and Claude is foreground.

**Biggest unknown:** The missing pieces are still deterministic semantic Mac inspection (document identity/selected text), an unambiguous browser-inspection dispatch, and a live USB-serial exchange tool for the physically connected pendant/bridge. I did not re-request the serial tool because that request is already queued and explicitly must not be repeated.

