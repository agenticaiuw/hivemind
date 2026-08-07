# Harness derivation — mac-terminal — round 29

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“I’m leaving my Mac—save what I’m looking at and what I was trying to do, keep working on it, and give me the result on my pendant when it’s ready.”"
- **useful because:** Today work is split between a live browser tab, Mac state, and relay jobs; walking away loses the exact page, evidence, and intent. A physical pendant handoff makes an interrupted task resumable and returns a concise result without reopening the computer.
- **path:** pendant button/voice: capture a handoff request and later announce a result → Mac agent: snapshot focused app, open tabs, selected text, downloads, and current job context into a checkpoint → browser extension: capture authenticated tab/session IDs plus page URL/title and a redacted evidence excerpt; resume the same tab later → relay: persist the checkpoint, run background research or Mac/browser steps while offline/asleep, and route completion to the pendant → dashboard: show checkpoint, evidence, progress, and a one-tap resume/stop control
- **model tier:** Use a cheap background model to normalize the checkpoint and poll/reconcile progress; use realtime only for the spoken handoff and completion summary. Escalate to the expensive tier only when the owner asks an ambiguous follow-up.
- **latency:** Acknowledge the button/voice handoff in under 2 seconds; checkpoint in under 10 seconds; background work may take minutes. Completion notification should be under 5 seconds after the relay records success.
- **cost:** Roughly $0.01–$0.05 per handoff, dominated by extracting/summarizing page context; polling and typed state transitions are negligible. Avoid resending page text by storing a content hash plus short excerpt and fetching only on resume.
- **security:** Authenticated page URLs, tab IDs, and excerpts leave the Mac for the relay; redact secrets/form values and store only the minimum evidence with a short TTL. Never submit/send browser mutations as part of automatic resume; require the existing owner confirmation at the final irreversible step. A lost pendant should not expose page contents through notifications.
- **missing:** A Mac/browser checkpoint API that atomically captures focused UI plus authenticated tab/session binding; A durable relay handoff job with lease, retry, expiry, and pendant push notification; A browser resume protocol that validates the original tab/session and reports when it has changed; A pendant-side offline queue/notification state (single button, LED/audio); Dashboard UI for evidence, progress, and final approval

### "“What am I looking at right now—and what’s the one thing I should notice?”"
- **useful because:** The owner can ask while away from the keyboard and get a grounded answer about the exact private page or Mac window in front of them, without explaining which tab, copying text, or uploading the whole screen. The system should identify the active context, extract only the relevant region, and speak a concise answer with a way to inspect its evidence.
- **path:** pendant: capture the spoken question and play the answer; a double-press can request the source snippet → Mac agent: identify the focused window and coordinate a one-shot capture, OCR/accessibility extraction, or focused-app metadata → browser extension: attest the active authenticated tab, extract only the visible/relevant DOM region, and return URL/title plus a short evidence hash → relay: route the request to the correct local surface, enforce an ephemeral context token, and discard the payload after answer delivery → dashboard: show the exact source region and confidence after the answer, without retaining the full screen
- **model tier:** Realtime handles the short spoken answer and ambiguity resolution; a cheaper vision/text model performs OCR and relevance extraction locally or in the relay. Use the expensive tier only for genuinely ambiguous visual interpretation.
- **latency:** Identify and answer in 3–6 seconds, with a spoken progress cue by 1 second. Evidence view may arrive within 10 seconds.
- **cost:** About $0.005–$0.03 per question, dominated by one small image or DOM-region inference; local accessibility extraction should avoid sending pixels whenever possible.
- **security:** The active window may contain passwords, messages, or other people’s data. Require an ephemeral per-question token, region minimization, local redaction of password fields and secrets, no raw screenshot retention, and an explicit indicator when capture is active. If the active context cannot be attested, say so rather than inspect an arbitrary tab.
- **missing:** A focused-window/context-attestation API shared by the Mac agent and browser extension; A one-shot, region-limited extraction endpoint with local secret redaction and evidence hashes; Relay support for ephemeral context tokens and guaranteed payload expiry; Pendant UX for capture-active indication and source/evidence replay


## Changes it proposed to its own stack

### `mac-harness` — Add a shell execution flight recorder and failure-recovery loop without changing FULL_CONTROL_MODE: record command hash, exact argv/string, cwd, selected environment names (not values), start/end timestamps, exit/signal, stdout/stderr byte counts plus capped tails, and host resource snapshot; on timeout/nonzero exit, automatically run a small fixed diagnostic bundle (cwd, disk, network, process, permissions), classify the failure, and retry only when the planner marks the command idempotent. Store a content-addressed compressed transcript linked to the existing receipt and expose a single job timeline in /jobs/:id and the dashboard.
- **owner gets:** When a task fails, the agent can explain whether it was a bad path, missing permission, timeout, or unavailable network and recover instead of asking the owner to repeat it. The owner gets a trustworthy answer about what ran, while retaining the deliberately unrestricted capability.
- effort: Medium: executor instrumentation, bounded transcript storage/redaction, typed failure schema, retry metadata, and dashboard timeline; no shell-policy change.  ·  risk: Command output can contain secrets and large logs; redact common credential patterns, cap output, encrypt or short-retain transcripts, and allow deletion. Automatic retries could duplicate side effects, so retries are opt-in per command and disabled after ambiguous termination. Recovery is to fall back to the current one-shot executor.
- cost: Small storage and CPU overhead per job; roughly cents per GB-month for retained compressed logs. Diagnostic commands add negligible local cost and avoid repeated expensive model turns.  ·  latency: Successful commands gain only milliseconds; failed commands take a few seconds for diagnostics and optional retry, while the owner receives an immediate queued/running status.
- security: Improves accountability without gates. Do not persist full environment values, stdin, or unrestricted page contents; hash/redact sensitive fields and make transcript access follow existing Mac-agent auth.
- depends on: Existing job receipts and /jobs/:jobId lifecycle; A bounded local transcript store and authenticated observability endpoint; Planner support for explicit idempotent=true retry intent

### `integration` — Create an ephemeral 'active-context capsule' protocol shared by Mac agent and browser extension. On request, the Mac issues a single-use token bound to the focused window and browser tab; the extension or accessibility adapter returns only a selected visible/semantic region, source metadata, redacted text or low-resolution crop, and a content hash. The relay expires the capsule after one answer or 60 seconds and links the evidence hash to the job receipt without storing raw pixels.
- **owner gets:** They can ask about exactly what is in front of them and trust that the answer came from the current page, not an old tab or an invented context, while reducing the chance that private screen contents leak or linger.
- effort: Medium-high: cross-process focus attestation, browser/Mac adapters, secret-field redaction, token expiry, typed evidence schema, and a small dashboard evidence viewer.  ·  risk: Focus can change during capture or accessibility APIs can fail; return an explicit stale/unknown result and never silently substitute another tab. Redaction can miss novel secrets, so default to minimal regions and short-lived transport. Recovery is a fresh capsule request.
- cost: Low recurring cost; mostly local metadata/OCR, with a small model call only when visual interpretation is needed. Short-lived capsule storage is bounded and automatically deleted.  ·  latency: Adds under a second for token negotiation and extraction; avoids sending full screenshots and usually reduces model latency and token cost.
- security: Strengthens least-retention and provenance without adding an approval gate. It needs authenticated local IPC, per-request nonce binding, encrypted relay transport, and deletion verification.
- depends on: Mac focused-window API; Browser extension active-tab attestation; Relay ephemeral payload store and expiry sweeper; Pendant capture indicator and evidence replay control


## What it asked for

_Nothing._
## Its own summary

Discovered the live Mac surface still exposes broad shell execution plus job receipts/observability, while the production tools remain split into short Mac actions, delegated workflows, browser actions, and relay status. I recorded two new proposals: a cross-surface physical handoff that snapshots the focused Mac/browser task and resumes it after the owner walks away, and a non-gating shell flight recorder with bounded failure diagnostics and opt-in idempotent retries. I also asked unified whether any checkpoint or pendant-push primitive already exists.

**Biggest unknown:** Whether the current browser bridge can atomically snapshot and later reattach an authenticated tab/session, and whether the pendant/relay already has a durable push-notification or offline queue. To implement the handoff, I still need those interface contracts, plus a bounded/redacted transcript store and a planner-visible idempotent retry flag; I do not need broader Mac permissions or a new shell authorization grant.

