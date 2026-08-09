# Harness derivation — faculty-perception — round 150

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live-observability** — At 2026-08-08T02:06Z the Mac agent is fully ready: Accessibility and Screen Recording are granted, all required permissions ready, relay reachable on D1, browser extension online with Safari 9 tabs and zero pending commands. Computer-use loop is enabled but visionUploadConsented remains false. No pendant appears in the live ops snapshot/registry.
  - evidence: GET /ops/snapshot and GET /browser/status returned 200; ops.status.permissions.ready=true, accessibility.trusted=true, screenRecording.granted=true, browser.online=true, tabCount=9, pendingCommands=0, computerUse.loopEnabled=true, visionUploadConsented=false; established registry says no pendant.

## Capabilities it proposed

### "When I press the pendant, tell me what I am looking at and what just happened around it."
- **useful because:** It gives the owner one trustworthy, time-aligned answer from their speech, current Safari tab, and Mac state instead of making them describe the screen. It explicitly reports missing/uncertain senses rather than hallucinating a view.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** Realtime for the short spoken answer; a cheaper background model can compress the captured context after the turn.
- **latency:** 2–4 seconds after the press; capture and provenance must be bounded before inference.
- **cost:** Roughly one realtime turn plus a small vision/text input; image upload and realtime tokens dominate, approximately $0.01–$0.05 per invocation depending on screenshot size.
- **security:** The live ops snapshot shows Screen Recording granted but visionUploadConsented=false. Require an explicit owner opt-in before any screenshot leaves the Mac, redact password/payment fields in the browser extension, keep the context pin ephemeral, and speak uncertainty when only tab metadata is available.
- **missing:** Owner consent flag and UI for uploading a screenshot to the relay; A synchronized context-pin envelope containing audio sequence, active app/tab, screenshot or DOM excerpt, and capture times; A pendant connection (none is registered today)

### "After you do something for me, say whether it is verified, only attempted, or still unknown—and show me the one observation that proves it."
- **useful because:** Today a Mac receipt or relay completion can mean only that bytes or an action were emitted. A state-change witness would stop the owner from trusting false success, especially for calendar, messages, purchases, and browser forms.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Cheaper background model compares structured before/after observations; realtime only speaks the compact verdict when the owner asks.
- **latency:** Under 5 seconds for reversible actions; up to 30 seconds for a browser or multi-app verification pass.
- **cost:** Usually <$0.01 per verification; the dominant cost is extra Mac/browser reads, not model tokens.
- **security:** Never expose secret field values in the witness. Store hashes, field names, app/site origin, timestamps, and redacted before/after classifications. Require confirmation for irreversible actions when no independent observation exists.
- **missing:** A common witness envelope joining actionLedger stepKey, browser command/DOM observation, AppleScript result, and an independent post-state read; Per-operation verification adapters (calendar event lookup, sent-message lookup, browser confirmation-state checks); Relay and dashboard readers that distinguish attempted from externally verified

### "Warn me on the pendant if the page or app I am acting in changes unexpectedly, loses my session, or reaches a risky confirmation screen."
- **useful because:** The owner can leave a browser task running without silently submitting to the wrong page, an expired login, or a changed price. This is a perception capability that protects action rather than taking action itself.
- **path:** browser-extension → mac-planner → relay → pendant → dashboard
- **model tier:** A deterministic local DOM/title/URL/state classifier handles ordinary changes; a cheap model is invoked only for ambiguous screenshots or semantic transitions. Realtime is used only for the urgent spoken warning.
- **latency:** Detect ordinary URL/title/session changes within 1 second; ambiguous classification within 3 seconds.
- **cost:** Near-zero for local classifiers; occasional screenshot analysis <$0.01 per ambiguous transition.
- **security:** Keep page bodies local by default; transmit only redacted transition metadata and hashes. Never infer that a payment or send is safe. Require an owner confirmation before any downstream action after a risk transition.
- **missing:** A persistent browser watch with baseline DOM/URL/title hashes and semantic checkpoints; A relay event type for browser-risk transitions with deduplication and expiry; A pendant notification policy that can interrupt only high-confidence, high-risk changes

### "Only act on words meant for me: if someone else is talking near me, or a podcast/video is playing, tell me you heard speech but do not turn it into a command."
- **useful because:** A wearable microphone is always present in messy real life. This prevents accidental messages, purchases, and destructive actions caused by overheard speech while still letting the owner say a short wake phrase and proceed naturally.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** A small on-device classifier handles voice activity, speaker/near-field cues, and wake-phrase confidence; realtime is used only after the local gate accepts an utterance.
- **latency:** Local accept/reject within 150 ms of utterance end; no cloud audio upload for rejected speech.
- **cost:** Near-zero for rejected ambient audio; realtime tokens only for accepted utterances, roughly the existing turn cost.
- **security:** Ambient speech must remain on-device and be discarded immediately. Require an explicit wake phrase or pendant button for commands; never infer identity from voice alone for high-impact actions.
- **missing:** A pendant-local ambient-speech/near-field command gate; A signed gate verdict carried with each uplink utterance; Relay and Mac planners that refuse action when the verdict is ambient or uncertain; A user calibration flow for noisy rooms and headphones

### "If a browser task gets stuck behind a login, CAPTCHA, expired session, or 2FA prompt, tell me exactly what I must do and resume from the same safe point after I fix it."
- **useful because:** The owner would no longer lose a half-finished task or wonder whether the system submitted anything. The browser can pause at a protected boundary, the pendant can explain the block, and the Mac can continue without repeating earlier steps.
- **path:** browser-extension → mac-planner → relay → pendant → dashboard
- **model tier:** Deterministic browser classifiers detect login/CAPTCHA/2FA walls; a cheaper planner reconstructs the next safe step. Realtime speaks only the concise intervention request.
- **latency:** Detect a blocked boundary within 1 second; resume within 3 seconds after the extension reports recovery.
- **cost:** Usually <$0.01 per blocked task; browser inspection and state checkpointing dominate, not model inference.
- **security:** Never ask the model to read or relay passwords, TOTP seeds, or CAPTCHA answers. Pause before protected fields, store only a redacted checkpoint and DOM/state hash, and require owner confirmation before retrying a submission.
- **missing:** A browser checkpoint protocol that captures resumable step state without secrets; Explicit blocked-boundary events from the extension; A durable relay-to-Mac resume lease with expiry and idempotency; A pendant dialogue for requesting and confirming owner intervention

### "When I am away from my Mac, let me leave a task that can continue safely, but stop automatically when its assumptions change and ask me from the pendant before crossing the next boundary."
- **useful because:** This turns the hive into a genuinely dependable delegate: the relay can keep work alive, the browser can hold authenticated state, the Mac can act, and the wearable remains the owner’s veto channel instead of requiring the owner to babysit a screen.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** A background planning model handles long-running task decomposition and checkpoint comparison; realtime is reserved for boundary questions and owner replies.
- **latency:** Background steps may take minutes; a boundary alert must reach the pendant within 2 seconds of detection, with a 10-minute lease before safe cancellation.
- **cost:** Roughly $0.01–$0.10 per multi-step task depending on checkpoints and retries; browser/Mac execution time dominates.
- **security:** Each task needs a declared scope, expiry, allowed applications/domains, and irreversible-action policy. The relay must not retain page secrets or silently widen scope. Require explicit pendant confirmation for payments, sends, deletions, or changed assumptions.
- **missing:** A cross-surface task lease with scope, expiry, checkpoints, and owner-veto semantics; A relay scheduler that survives Mac/browser disconnection and resumes only on matching state; A pendant command/reply channel and offline veto queue; A common assumption-diff format for Mac, browser, and relay observations


## Changes it proposed to its own stack

### `model-routing` — Make the relay and Mac planner treat visionUploadConsented as a hard input-policy gate: when false, route context requests to DOM/title/app metadata only, label screenshots unavailable, and never silently fall back to uploading a screen. When true, attach a short-lived, redacted context-pin ID and expiry to the turn.
- **owner gets:** The system will stop making the owner guess whether a spoken answer saw their screen, while preserving privacy until they explicitly opt in.
- effort: Moderate: propagate one consent bit from /ops/snapshot into planner/tool context and add a tested no-image branch.  ·  risk: A stale consent bit could suppress useful vision or, worse, permit it unexpectedly; fail closed, expire consent, and expose the reason in the spoken answer and dashboard.
- cost: Negligible model cost change; avoids accidental screenshot upload costs.  ·  latency: No-image branch is faster; consent and redaction checks add under 100 ms.
- security: Strongly reduces accidental screen exfiltration; requires an auditable consent timestamp and scope.
- depends on: Owner-facing consent control; Context-pin envelope from Mac/browser to relay


## What it asked for

_Nothing._
## Its own summary

Round 150 established a materially changed reality: the exact AI Pendant Agent now has Accessibility and Screen Recording, all required automation permissions, relay reachability, and an online Safari extension with 9 tabs and no pending commands. Computer use is enabled, but visionUploadConsented is false; no pendant is registered. I recorded this and proposed four new owner-facing capabilities/changes: a synchronized context pin, state-change witnesses, browser-risk divergence warnings, and a fail-closed vision-consent router. The most useful is the state-change witness: it prevents 'Mac completed' from being mistaken for 'the world changed.'

**Biggest unknown:** The granted read_continuity_snapshot tool still fails resolution (nearest live routes are GET /ops/snapshot and GET /pipeline), so I still need a reliably resolved single cross-surface continuity read—not another permission. Product gaps remain the missing context-pin envelope, independent post-state verification adapters, browser semantic watches, and an owner consent control for screenshot upload. A physical pendant is also still absent, so wearable delivery cannot yet be verified.

