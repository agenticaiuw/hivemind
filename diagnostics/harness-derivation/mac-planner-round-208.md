# Harness derivation — mac-planner — round 208

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-bridge-live-state** — The Mac agent, relay, browser bridge, Accessibility, Screen Recording, and automation grants are all live and ready; Safari has 9 tabs with active X.com tab and zero pending browser commands. FULL_CONTROL_MODE and vision loop are enabled, but vision upload consent is false.
  - evidence: GET /ops/snapshot returned 200 at round 208 with ready:true, accessibility trusted:true, screenRecording granted:true, browser online:true, relay reachable:true, and visionUploadConsented:false.

## Capabilities it proposed

### "Take this multi-file task to completion overnight: stage the files atomically on my Mac, open the result if requested, and tell me on the pendant whether it succeeded, was retried, or needs my attention after a restart or link drop."
- **useful because:** A server plan currently has to guess whether a desktop write finished. This gives the owner a durable completion contract rather than a best-effort automation: no half-written deliverable, no duplicate retry, and a spoken receipt even when the Mac or network disappears temporarily.
- **path:** relay-realtime → mac-planner → pendant → dashboard
- **model tier:** Use a cheap deterministic worker for hashing, staging, retry, and receipt reconciliation; use realtime only to explain an exceptional failure to the owner.
- **latency:** Local staging should feel immediate for normal documents (under 5 seconds); recovery can be asynchronous, with a pendant alert as soon as the Mac bridge returns.
- **cost:** Near-zero model cost for normal runs; storage and hashing dominate. Exceptional natural-language explanations may cost under $0.01.
- **security:** Restrict writes to an owner-configured workbench root and preserve per-file hashes. Never silently overwrite a changed destination. Receipts should contain paths and status, not file contents; notification text must redact filenames if the owner enables private mode. Empty unattended-action policy means stage-only and no open-after behavior.
- **missing:** Relay orchestration that retries a mac_workbench_transaction by job_id and deduplicates it across bridge reconnects; Pendant delivery of compact transaction receipts and a durable 'needs attention' alert; A user-facing routine schema for declaring destination, overwrite policy, and open-after policy

### "If a desktop job fails or stalls, inspect the current Mac and browser state, tell me on the pendant what blocked it in one sentence, and offer the smallest concrete recovery action rather than making me start over."
- **useful because:** Automation failures are currently opaque: a relay receipt says a job failed, but only the Mac can see the dialog, login page, or unsaved document that caused it. This joins job telemetry with live perception and turns a failed action into recoverable progress.
- **path:** mac-planner → mac-vision → browser-harness → relay-realtime → pendant
- **model tier:** Use deterministic failure classification and a small background model for UI text normalization; use realtime only when the owner asks a follow-up or the recovery is ambiguous.
- **latency:** Detect and summarize within 3 seconds of a failed receipt; recovery actions should be proposed immediately and executed only under the owner's configured action policy.
- **cost:** Typically under $0.005 per failure; screenshots/UI text and model summarization dominate, while most known dialogs can be classified without a model.
- **security:** Redact passwords, tokens, message bodies, and page content before leaving the Mac. Do not capture continuously: inspect only after a failed/stalled job and retain the evidence for a short TTL. Recovery must be represented as a previewable action list and logged with a receipt; an empty policy should report only, never execute.
- **missing:** A correlation contract linking a job receipt to a one-shot post-failure Mac/browser inspection; A structured failure taxonomy spanning accessibility UI, browser bridge, and app-level errors; A pendant alert payload that carries a short diagnosis and recovery-job identifier

### "When I say 'undo what you just did' through the pendant, find the latest Mac job I can safely reverse, tell me exactly what will be restored, and perform the undo even if the original conversation has ended."
- **useful because:** The owner should not need to remember a job ID or reopen the original session to recover from an automation mistake. The relay can resolve vague intent, the Mac has job receipts and undo handlers, and the pendant provides the fastest interruption path.
- **path:** pendant → relay-realtime → mac-planner → dashboard
- **model tier:** Use deterministic latest-job lookup and undo capability metadata; use realtime only to resolve genuinely ambiguous references such as two jobs completed seconds apart.
- **latency:** Identify and speak the candidate within 1 second; execute the reversible undo and return a receipt within 3 seconds.
- **cost:** Effectively zero model cost for unambiguous cases; under $0.005 when language disambiguation is needed.
- **security:** Only jobs with an explicit reversible undo receipt may qualify; never infer filesystem restoration from a vague request. Show target, affected resources, and reversibility in the spoken preview, log the result, and honor the owner's configured unattended-action policy. If there is no safe candidate, say so and do nothing.
- **missing:** A machine-readable reversibility/undo manifest in every Mac job receipt; A relay intent resolver that maps pendant utterances to the latest eligible job across sessions; A compact pendant confirmation/result protocol for undo preview and completion

### "Let me teach you a Mac/browser workflow once by doing it while I say 'learn this'; turn the observed sequence into a parameterized routine, show me the steps and assumptions, and let me invoke it later from the pendant with new values."
- **useful because:** The owner currently has to restate multi-step computer procedures every time. Learning by demonstration would make the system improve from the owner's real workflows instead of forcing them to design an automation language. The pendant provides the start/stop boundary and naming; the Mac and browser provide the observable actions and state.
- **path:** pendant → mac-vision → mac-planner → browser-harness → relay-realtime → dashboard
- **model tier:** Use a local deterministic event recorder for UI/browser actions and a background reasoning model to infer parameters, preconditions, and stable checkpoints. Use realtime only for naming the routine or answering a clarification while teaching.
- **latency:** Recording must add effectively no interaction latency. Produce a reviewable draft within 30 seconds after teaching; routine invocation should begin within 2 seconds.
- **cost:** Roughly $0.02–$0.15 per learned workflow, dominated by action trace summarization and checkpoint inference; later invocations are mostly deterministic and cheap.
- **security:** Never record passwords, typed secrets, clipboard contents, or page bodies by default. Keep raw traces local, send only redacted accessibility/browser events, and make every inferred variable visible before saving. A learned routine must run in a sandbox/dry-run first and stop when a precondition or target identity changes; owner policy controls whether later mutations run unattended.
- **missing:** A pendant command and durable session boundary for starting, pausing, and ending demonstration capture; A unified Mac/browser event trace with semantic targets rather than coordinates; A routine compiler that extracts parameters, preconditions, checkpoints, and failure branches; A review/edit UI and versioned routine store with dry-run playback

### "When I ask the pendant 'what am I looking at?' while a Mac window is in front of me, describe the relevant error, controls, or next step using a privacy-preserving local screen interpretation, without uploading the screenshot or reading unrelated windows."
- **useful because:** The owner can get help with a visual state without narrating it or exposing an entire desktop to a remote model. This is especially valuable for dialogs, charts, and browser pages that the current text-only bridge cannot understand reliably.
- **path:** pendant → mac-vision → mac-planner → relay-realtime
- **model tier:** Run a vision-capable model locally on the Mac for pixel interpretation and emit only a short structured description; use realtime for the owner's spoken question and response, never for raw screenshot analysis.
- **latency:** Capture-to-answer under 4 seconds for a single window; no continuous capture and no screenshot retention after the answer.
- **cost:** Local inference cost is compute/power rather than API spend; optional remote fallback should be disabled by default and, if explicitly enabled, cost under $0.02 per query.
- **security:** Window-scoped capture only, with sensitive-app and secure-input exclusion. Raw pixels remain on-device and are discarded immediately; the relay receives redacted semantic text. The owner must explicitly enable this capability and remote fallback must require a separate setting.
- **missing:** A local vision inference service callable by the Mac agent; Window-bounded capture and sensitive-app exclusion before inference; A pendant intent and response format for concise visual questions; A policy setting distinguishing local-only interpretation from optional remote fallback

### "Whenever you bring a file from my browser or an external app onto my Mac, attach a private provenance record so I can later ask where it came from, when it was fetched, and whether the source has changed."
- **useful because:** Files lose their origin as soon as they are downloaded, copied, or renamed. Provenance would let the owner trust, refresh, or delete a document without remembering which tab or account produced it, while joining browser session identity with Mac filesystem state.
- **path:** browser-harness → mac-planner → relay-realtime → dashboard → pendant
- **model tier:** Use deterministic URL/account/session capture, file hashing, and timestamps; use a cheap background model only to normalize titles and classify document type. Realtime is only for spoken provenance queries.
- **latency:** Attach provenance during the transfer with no perceptible delay beyond hashing; answer a later query in under 2 seconds for indexed files.
- **cost:** Near-zero API cost; local hashing and a small encrypted metadata index dominate.
- **security:** Do not store credentials, cookies, page bodies, or full URLs containing secrets. Normalize and redact query parameters, encrypt the index, scope records to owner-approved folders, and provide a reliable purge that removes both sidecars and index entries. Provenance must never be asserted if capture failed.
- **missing:** A browser-to-Mac transfer hook that emits source metadata with the resulting file; A durable encrypted provenance index keyed by content hash and filesystem identity; A relay query that resolves natural-language file references to provenance records; Dashboard controls for redaction, retention, and purge


## What it asked for

_Nothing._
