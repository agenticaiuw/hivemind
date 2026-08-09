# Harness derivation — browser-extension — round 249

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live browser access** — Safari extension is online with two tabs: an authenticated-looking DoorDash order URL in an inactive tab and a YouTube video active. browser_read_page through POST /execute works and returns evidence capsules/receipts; active page is Max Hodak: Average Is Not Good Enough.
  - evidence: POST /execute browser_read_page at 2026-08-09T02:09:18Z returned tabId 7975357, plus prior browser_list_tabs result showed tabId 6516355 DoorDash order and tabId 7975357 YouTube.

## Capabilities it proposed

### "“I’m looking at this page—answer my question about it through the pendant, using the page I already have open.”"
- **useful because:** This is the browser's unique value in its simplest high-frequency form: the owner need not copy a URL, switch apps, or expose a logged-in page to a public search engine. A voice question is correlated with the active Safari tab, the extension reads only that tab, and the relay answers from a fresh evidence capsule. It works for private dashboards, receipts, support portals, and long articles alike.
- **path:** pendant → relay → browser → mac-planner
- **model tier:** Use realtime for the short conversational turn only; use a cheaper background extraction model when the page is long, then let realtime answer from the compact evidence capsule. Deterministic page reading and redaction stay on the Mac.
- **latency:** Target 3–6 seconds from the spoken question to the answer; long pages may take a background extraction pass and return a brief progress acknowledgement first.
- **cost:** Usually one short realtime turn plus a small extraction prompt, roughly cents per question. Cost is dominated by page text sent for extraction; cap to main content, relevant forms/landmarks, and the question's matched section.
- **security:** Read-only browser action by default, with no clicks or typing. Send the URL and only the relevant extracted passage to the model; apply existing redaction and retain only a short claim/provenance capsule under the browser's 24-hour TTL. The response must say when the page did not contain enough evidence rather than guessing. Do not speak secrets or persist page text.
- **missing:** A reliable active-tab/read-context correlation from a pendant conversation to one browser command; Question-focused extraction that chooses relevant page regions without retaining the full page; A compact evidence handoff from browser result to relay-realtime, including URL/title and freshness; A user-visible indicator when the answer came from the open private page

### "“Turn the important fields on this private web page into a draft task on my Mac, and show me exactly what you would create before doing it.”"
- **useful because:** This closes the gap between seeing an authenticated page and acting on it without making the browser agent perform a high-impact mutation. For example, a logged-in invoice, appointment, or renewal page can produce a structured draft with title, due date, amount, source URL, and suggested reminder time. The owner gets a usable local artifact while retaining control over what is created.
- **path:** browser → mac-planner → relay → pendant
- **model tier:** Use a background/cheap model for schema extraction and field normalization; use mac-planner only for the short, deterministic draft action. Realtime speaks the proposed fields and answers corrections, not the whole page.
- **latency:** Extract and present the draft in under 8 seconds; create the local reminder/note in under 3 seconds after the owner asks. Never wait on a long page when a focused form read suffices.
- **cost:** A few cents per extraction, dominated by the page-to-structured-fields prompt; Mac action and pendant confirmation are effectively free.
- **security:** Read the current page only and stop before any browser submission. Preserve source URL, timestamp, and evidence capsule with existing browser retention rules; do not store page body. Display the exact local mutation (field-by-field) and provide an undo receipt. Redact account numbers and payment details unless the owner explicitly asks to include them. This is an inspectable preview, not an invented site allowlist.
- **missing:** A schema-mapping step from browser forms/main text to reminder/note fields with confidence and missing-field reporting; A preview payload rendered both in the pendant's concise speech and Mac dashboard; A handoff that lets mac-planner create_reminder or a note only after the owner approves the exact draft; A provenance link from the created local item back to the browser evidence capsule

### "“Take the ticket or QR code I have open in my logged-in browser and put a usable copy on my real iPhone, without uploading it anywhere.”"
- **useful because:** A private ticket, boarding pass, event code, or pickup QR is trapped in Safari and is awkward to use at the physical gate. The browser extension can read the authenticated page, mac-vision can capture only the code region, and ios-control can place it in a local note or photo on the owner's real iPhone. The relay can tell the pendant that the copy is ready, while no cloud service receives the ticket image.
- **path:** browser → mac-vision → ios-control → mac-planner → relay → pendant
- **model tier:** Use deterministic browser extraction and local OCR/QR decoding first; use a cheap vision model only if the code region is not structurally exposed. Realtime is limited to the spoken request and completion message.
- **latency:** Aim for 10–20 seconds, including iPhone Mirroring. If decoding confidence is low, report that instead of guessing or writing a corrupt code.
- **cost:** Near-zero inference when the page exposes the QR payload; at most a few cents for local-region vision. No upload or storage service is needed.
- **security:** This is a sensitive artifact. Keep image/payload on the Mac/iPhone only, avoid browser evidence persistence and relay logs, and show the destination app/path before writing. Do not send, redeem, purchase, or alter the ticket. Require an explicit final spoken instruction for the local iPhone write because it creates a durable copy; provide deletion afterward.
- **missing:** A browser action that returns a QR/barcode region or payload without storing page text; A local-only handoff from browser result to mac-vision/ios-control, bypassing relay persistence; An iPhone Mirroring action to create a photo/note and verify it visually; A one-shot cleanup action to delete the temporary Mac artifact and any local capture

### "“If a private website needs me to complete a CAPTCHA, passkey, or two-factor step, tell me on the pendant, leave the task paused, and continue automatically once I finish it in Safari.”"
- **useful because:** Authenticated browser work often fails at the exact point where the owner must prove presence. Today the browser agent times out or leaves an ambiguous half-completed task. A cross-node challenge handoff would let the owner walk away from the Mac, receive a concise pendant alert, complete the challenge in the real Safari session, and have the paused workflow resume from a verified checkpoint. It must never attempt to defeat a CAPTCHA or infer a one-time code.
- **path:** browser → relay → pendant → mac-planner → dashboard
- **model tier:** Use deterministic browser state detection and a cheap background classifier for challenge types. Realtime is only needed for the pendant notification and any spoken clarification; no expensive reasoning is needed while paused.
- **latency:** Detect and alert within 2 seconds of the challenge appearing. Resume within 5 seconds after Safari reports completion, with a bounded timeout and a clear expired-task message.
- **cost:** A few cents or less per interrupted workflow; most cost is extension polling and state snapshots. No page contents need to be sent to a model while paused.
- **security:** Never read, store, repeat, or transmit one-time passwords, passkeys, or CAPTCHA answers. Pause before the protected step and identify only the challenge category and page origin. The owner completes it directly in Safari. Store a short-lived task checkpoint, not page text or screenshots; invalidate it if the origin, tab, or form state changes unexpectedly. Any later external submission remains subject to the existing owner-approved execution policy.
- **missing:** A browser challenge detector that recognizes login/CAPTCHA/2FA/passkey interstitials without collecting secret fields; A durable paused-task checkpoint tied to tab identity, origin, and form state; Relay-to-pendant urgent notification and acknowledgment for browser tasks; A browser result event that signals challenge completion and safely revalidates the checkpoint before resuming; Dashboard controls to cancel, expire, or inspect the paused workflow

### "“Forget everything you learned from this private website, everywhere, and tell me what could not be erased.”"
- **useful because:** A browser session can touch several storage layers—short-lived findings, evidence capsules, job records, local drafts, and pendant alerts—but the owner cannot currently issue one origin-scoped erasure and receive a complete answer. This gives the owner a practical privacy control after handling a sensitive account, while distinguishing successfully erased material from immutable operational receipts or data retained by the site itself.
- **path:** browser → relay → mac-planner → pendant → dashboard
- **model tier:** Use deterministic indexed deletion and receipt traversal; a cheap model is unnecessary except for explaining the resulting inventory in plain language. Realtime can read a short deletion report over the pendant.
- **latency:** Return an initial inventory in under 3 seconds and complete local deletion within 10 seconds. If a remote or immutable record cannot be erased, say so immediately rather than implying success.
- **cost:** Minimal API cost; this is primarily indexed local deletion and audit traversal.
- **security:** Require the owner to specify an origin or current browser task, not an ambiguous global “forget everything.” Delete page-derived claims, evidence capsules, cached extracts, pending browser jobs, local drafts, and pendant alert copies where technically possible; preserve only a minimal tamper-resistant deletion receipt with no page content. Never claim to erase data from the website, Safari history, model-provider logs, or backups unless those systems confirm deletion. The dashboard must show exactly what remains.
- **missing:** A cross-store origin index linking browser evidence, findings, jobs, drafts, and pendant alert IDs; An origin-scoped deletion transaction with retries and idempotency; A retention inventory endpoint that reports stores not under this system's control; A pendant-friendly deletion summary and dashboard audit view

### "“Watch me do this once in Safari, then let me ask the pendant to repeat the same private-browser routine later, with the values and final result shown before it runs.”"
- **useful because:** Many authenticated tasks are repetitive but site-specific: downloading a statement, checking a claim, copying a status, or opening a recurring report. The owner can demonstrate the workflow once instead of describing selectors or URLs. Later, the browser extension replays semantic steps against the current page, adapts to harmless layout changes, and the pendant reports what it found. This is materially different from a fixed macro because it captures intent, checkpoints, and failure points rather than brittle coordinates.
- **path:** browser → pendant → relay → mac-planner → dashboard
- **model tier:** Use a background model to turn the demonstration into a compact semantic recipe; use deterministic browser actions for replay and realtime only for the owner's request/result. Escalate to the Mac planner when the site changes and the recipe cannot be safely matched.
- **latency:** Recording is immediate; replay should finish in 5–15 seconds for a short workflow. On mismatch, pause within one action and notify rather than guessing through the rest of the sequence.
- **cost:** A few cents to compile a new recipe; replays are mostly extension calls and should be nearly free. The main cost is model use only when page structure changes.
- **security:** Do not record passwords, passkeys, OTPs, payment fields, or raw page text. Store action intent, allowed origins, selectors/landmarks, and redacted expected outcomes. Recipes ship disabled until the owner names them and can be deleted with their run history. Preserve the existing policy that genuinely irreversible browser submissions stop and show the exact payload first.
- **missing:** A browser demonstration recorder that emits semantic action traces while excluding secret fields; A recipe compiler and matcher based on landmarks/forms rather than coordinates; A replay checkpoint/resume engine with mismatch detection and clear failure receipts; A dashboard/pendant interface for naming, disabling, and previewing private-browser routines


## What it asked for

_Nothing._
