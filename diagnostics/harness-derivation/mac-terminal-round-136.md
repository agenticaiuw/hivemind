# Harness derivation — mac-terminal — round 136

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“What am I looking at?” — answer from the screen and the active Safari page, then let me ask a follow-up by voice."
- **useful because:** This is the one capability that makes the pendant feel like a second mind rather than a remote control: the owner can stay hands-free and get grounded help about the exact thing in front of them. The Mac observation layer supplies foreground app and permission truth; Safari supplies authenticated page content; the relay turns the answer into speech. If UI access is unavailable, it says so instead of hallucinating.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension
- **model tier:** Use a cheap text model to fuse the structured observation and page extract; reserve realtime only for the live spoken turn and follow-up. Use vision only when screen recording is actually granted.
- **latency:** 4 seconds for the first spoken answer; 1 second for foreground/browser metadata, up to 2 seconds for a permitted snapshot or DOM extract. Cache the observation for 10 seconds so follow-ups do not resend it.
- **cost:** Usually one small text fusion call plus realtime speech; vision is the dominant cost and should be skipped when DOM/structured observation answers the question.
- **security:** Authenticated page text and screenshots leave the Mac only for this request and must be labeled with URL, timestamp, and permission state. Never infer private content from a stale screenshot; say which source was used. Ask before voice-triggered actions, but answering is read-only.
- **missing:** A single /look-style orchestration route that joins GET /observe with browser snapshot/extract and returns source-cited evidence; Screen Recording and Accessibility granted to the actual AI Pendant Agent binary for screen-grounded answers; A pendant-to-Mac USB trigger/transport while LTE registration is absent

### "“Compare this page with my local notes/project and tell me what conflicts.”"
- **useful because:** The browser has private authenticated facts while the Mac has the owner's local source of truth; today neither surface can reliably reconcile them. A cited contradiction report would catch stale instructions, mismatched dates, and duplicated work without making any changes, and it works hands-free from the pendant.
- **path:** pendant → browser-extension → mac-planner → relay-realtime
- **model tier:** Use a background/cheap text model for extraction, normalization, and diffing; use realtime only to collect the spoken request and read the short result. Escalate to the expensive model only when the two sources are ambiguous or structurally different.
- **latency:** Under 8 seconds for one page and up to three explicitly named local files; stream a one-line progress cue after 2 seconds. Do not scan the whole home directory without an explicit scope.
- **cost:** One or two small extraction/diff calls; dominant cost is tokens from page and local files, capped and chunked. No vision needed for normal DOM pages.
- **security:** Local files and authenticated page contents are sensitive. Keep them on the Mac/relay only for the request, attach path/URL and timestamps to every claim, and redact secrets before sending speech. Read-only by default; never edit either source.
- **missing:** A scoped local-file read/extract action that returns content hashes and line ranges, rather than arbitrary shell output; A /compare orchestration route joining browser extraction and local evidence with citation IDs; A spoken result format that can enumerate conflicts and let the owner request one cited item

### "“If something you’re doing fails while I’m away, diagnose it and tell me the next useful step when I’m back.”"
- **useful because:** A completed/failed job record is not enough: the current live system has a concrete browser failure (“extension does not have access to this frame”) and a concrete Mac failure mode (UI receipts can say success while Accessibility is untrusted). The owner should return to a diagnosis, not a dead end—whether to retry DOM extraction, open the tab, grant a permission, or continue manually.
- **path:** relay → mac-planner → browser-extension → pendant → mac-vision
- **model tier:** Use a cheap background model to classify failures from typed receipts, permission state, and browser status; use realtime only when delivering the short spoken alert. Escalate only novel multi-step failures.
- **latency:** Diagnosis within 10 seconds of a terminal failure; one concise alert on next pendant connection, with no repeated alerts for the same fingerprint. Detailed evidence stays available on Mac.
- **cost:** Near-zero for known error fingerprints; occasional small text call for novel failures. The main savings come from avoiding blind retries and unnecessary vision/model calls.
- **security:** Speak only a redacted explanation and app/site name; keep command text, URLs, local paths, and page content in the authenticated Mac journal. Never auto-retry a mutation based solely on an error classifier.
- **missing:** A durable failure-fingerprint/diagnosis service that consumes /jobs receipts, /observe permission state, and browser heartbeat errors; A next-step taxonomy (retry, activate tab, permission repair, manual handoff) with per-action idempotency; A relay-to-pendant deferred notification queue for the current USB-only, not-LTE-registered pendant

### "“Explain the thing I just copied.”"
- **useful because:** The owner can move information from any Mac app into a hands-free conversation without naming the app, switching windows, or pasting into chat. The system would capture the clipboard event locally, attach the active app/document and (when applicable) Safari tab as provenance, then let the pendant answer questions about that exact snippet and remember which source it came from.
- **path:** mac-planner → browser-extension → relay-realtime → pendant
- **model tier:** Use a small text model for summarization, translation, and straightforward explanation; use the realtime tier only for the spoken exchange. Escalate to a stronger model for technical or multi-document follow-ups.
- **latency:** Detect a clipboard change in under 300 ms; first spoken explanation in under 3 seconds. Keep the snippet local until the owner explicitly asks for an explanation, then send only the selected content and provenance.
- **cost:** One short text call per explicit explanation; negligible background cost for local clipboard hashing and event detection. Large copied documents should be truncated with an offer to continue.
- **security:** Clipboard contents can contain passwords, tokens, or private work. Never upload on change alone: store only a salted hash and metadata until a button/voice request arrives; redact common secrets and show the source app before speaking. Do not persist the raw snippet beyond a short TTL unless asked.
- **missing:** A local clipboard watcher that emits a bounded, consented event with content type, size, hash, and source application; A relay event and Mac route that can fetch the current clipboard only after an explicit pendant request; A provenance-aware explanation context joining clipboard text to the active Safari tab or local document; A USB pendant command path for this currently attached but LTE-unregistered device


## Changes it proposed to its own stack

### `mac-harness` — Make every UI action run through an input-reachability handshake and a capability ladder: before ui_click/type_text/press_keys, verify the actual AI Pendant Agent bundle is Accessibility-trusted; if false, do not claim success, automatically fall back to DOM/browser actions or typed AppleScript where possible, and return a structured blocked reason plus the exact System Settings target. Record the attempted method, fallback, and evidence in the job receipt.
- **owner gets:** The Mac currently reports UI steps as successful while doing nothing: /observe proves Accessibility is false and eventsPost is rejected because permission was granted to a different binary. The owner gets truthful answers and useful progress instead of believing an email was typed or a button clicked when it was not.
- effort: Medium: central preflight in computerControl/executor, typed fallback dispatch, and receipt schema changes; add tests for the wrong-binary permission case and browser DOM fallback.  ·  risk: A preflight could incorrectly classify a temporarily unavailable UI; recover by retrying once and preserving the original action for manual replay. Some apps have no DOM or AppleScript fallback and must remain explicitly blocked.
- cost: No meaningful API cost; one local permission probe per batch, with cached result and short TTL.  ·  latency: Adds about 50–150 ms to the first UI batch; avoids wasting 400 ms-plus per false-success step and expensive vision retries.
- security: Improves auditability without reducing owner-authorized access. No new data leaves the Mac; permission diagnostics may identify the host app and bundle path.
- depends on: Grant Accessibility to /Users/evanliu/Applications/AI Pendant Agent.app, or preserve the explicit untrusted state and make fallback truthful; Extend action receipts with attempted transport and evidence fields


## What it asked for

_Nothing._
## Its own summary

Round 136 produced four owner-facing advances. The highest-value proposal is hands-free “What am I looking at?”: fuse Mac foreground observation, authenticated Safari extraction, and optional vision, then speak a cited answer through the pendant. I also proposed (1) truthful UI execution with an Accessibility preflight and typed fallbacks so false-success clicks/types cannot be reported, (2) cross-source contradiction checking between a logged-in page and scoped local files, and (3) durable failure diagnosis that turns browser/Mac receipts into one actionable spoken recovery step. Live checks show relay, Mac agent, and Safari extension are online; browser snapshot currently fails on frame access; Accessibility and Screen Recording are still false for the actual AI Pendant Agent binary; the pendant remains USB-attached/prototype rather than LTE-registered.

**Biggest unknown:** Whether the orchestrator will wire a unified /look, /compare, and failure-diagnosis orchestration layer (including scoped local-file evidence and deferred pendant notifications), and whether Accessibility/Screen Recording can be granted to the actual AI Pendant Agent bundle. I still need those implementation capabilities—not another permission gate—to make the proposals executable.

