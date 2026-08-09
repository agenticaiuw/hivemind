# Harness derivation — faculty-perception — round 222

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-permissions** — Live continuity snapshot at 2026-08-09T00:39Z reports AI Pendant Agent accessibility and screenRecording both trusted, requiredMissing/optionalMissing empty, ready=true; browser extension online in Safari with 2 tabs and zero pending commands; relay reachable with D1 and mac bridge online. This supersedes prior denied-permission context.
  - evidence: read_continuity_snapshot include relay,pipeline returned GET /ops/snapshot HTTP 200; body.status.permissions and body.status.browser/relay fields.

## Capabilities it proposed

### "“Send this message, but ask me one last time before it actually goes out—and show me exactly what you’re about to send.”"
- **useful because:** The system can act across a logged-in browser today, but the owner currently has no wearable-grade, target-specific consent boundary. This makes consequential actions both safer and less annoying: the pendant speaks the exact recipient/content, the owner confirms, and execution is cryptographically tied to the preview rather than to a vague prior instruction.
- **path:** relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Realtime model only for the short spoken confirmation; a cheaper background model can draft and classify the action. Mac vision/perception should extract the final target and postcondition, not the realtime model.
- **latency:** Preview in 2–4 seconds; spoken confirmation under 500 ms after preview; execute immediately after confirmation; postcondition screenshot within 3 seconds.
- **cost:** About $0.01–$0.04 per invocation depending on screenshot/vision tokens; browser and local Mac work dominate latency, not model generation.
- **security:** Never read a generic “yes” as consent. Bind a single-use, 30-second approval token to action type, destination identity, normalized text/value, and a screenshot/content hash; invalidate it if the page changes. Require a second confirmation for irreversible financial, deletion, or public-post actions. Only redacted target fields leave the Mac; page bodies stay local.
- **missing:** A Mac-side approval envelope that hashes the final browser target and expires; A relay route that carries the envelope to the pendant and returns a device-originated confirmation; A browser executor preflight/postcondition contract; existing browser actions currently report execution, not semantic target identity; A visible spoken/UI distinction between preview, approved, and verified states

### "“What is the browser showing right now? Tell me only what you can point to, and say when you’re unsure.”"
- **useful because:** A voice answer about a logged-in page is valuable only if perception can distinguish visible fact from inference. With Accessibility and Screen Recording now live, the Mac can capture the actual tab/window, the browser bridge can identify the active page, and the relay can give a concise answer without pretending that stale DOM text or a guessed URL is current.
- **path:** relay-realtime → mac-vision → browser-extension → faculty-perception → faculty-judgement
- **model tier:** Use the local vision model for screenshot grounding and a low-cost text model to compress grounded observations. Reserve realtime for the owner’s question and uncertainty phrasing.
- **latency:** Active-tab snapshot in under 1 second, grounded answer in 2–3 seconds; if capture is stale or permission changes, say so rather than retrying invisibly.
- **cost:** Roughly $0.005–$0.02 per question; local screenshot capture is free, with vision tokens dominating.
- **security:** Logged-in page pixels and text remain on the Mac unless the owner explicitly asks for cloud reasoning. Redact passwords, payment fields, and private message bodies before any relay upload. Every claim should carry capture time, tab identity, and confidence; never use the browser URL alone as evidence.
- **missing:** A local screen-grounding result format with element/region coordinates, capture timestamp, and uncertainty; A policy-controlled redaction pass before any relay/model upload; A browser-to-screen join that rejects answers when the active tab changed between capture and speech; A compact spoken citation format such as “Safari tab 2, captured 1.4 seconds ago”

### "“Did that actually happen? Give me a receipt I can trust, and undo it if it didn’t.”"
- **useful because:** The current stack can queue Mac/browser actions and can often report completion, but completion is not the same as a changed page or sent message. A cross-surface semantic receipt would let the owner ask once and get a bounded before/after proof: which tab/app changed, what field or state changed, when it was observed, and whether undo is genuinely available.
- **path:** relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-action → unified
- **model tier:** Cheap background model extracts a structured diff from local before/after captures; realtime only summarizes the receipt aloud. No expensive model is needed when the action already has a typed postcondition.
- **latency:** Capture-before under 500 ms, action as usual, capture-after within 2 seconds; spoken receipt under 1 second after the verified diff. If verification cannot run, report “executed but unverified,” never success.
- **cost:** Usually under $0.01, dominated by local capture and optional vision; cloud tokens are avoidable for typed actions.
- **security:** Receipts must not store raw private page content. Keep hashes, redacted field labels, app/tab pseudonym, timestamps, and a tiny reversible diff. Treat an undo as a new action requiring its own verification; never infer reversibility from a generic success status.
- **missing:** A typed postcondition schema for browser and Mac actions; A local before/after capture coordinator that waits for page stabilization; A receipt record linking action-ledger step, browser command, evidence capsule, and undo token; A user-facing distinction among verified, executed-unverified, failed, and undo-expired

### "“I saw it somewhere yesterday—find the exact page, message, or document I was looking at and tell me where it is.”"
- **useful because:** Today a browser read, a Mac screen, and a spoken interaction die in separate transient paths. The owner cannot search their own recent visual experience across Safari, desktop apps, and wearable voice without manually remembering words or reopening tabs. A private episodic index would turn “I saw it” into a recoverable fact while retaining only what is needed to locate it.
- **path:** pendant → relay-realtime → mac-vision → browser-extension → mac-planner → faculty-perception → unified
- **model tier:** Use a background local model to derive OCR/text and compact visual embeddings from explicitly allowed captures; use a small text model for retrieval/reranking. Realtime is only for the owner’s spoken query and concise result.
- **latency:** Capture/index incrementally without affecting interaction; query top matches in 2–5 seconds. If no high-confidence match exists, say that plainly and return the search boundary.
- **cost:** Near-zero recurring cloud cost if embeddings/OCR stay on the Mac; occasional local CPU/storage use. Cloud cost only when the owner explicitly asks to search a redacted excerpt.
- **security:** This is highly sensitive surveillance-adjacent data. It must be opt-in by app/window/domain, visibly indicate capture, exclude passwords, payment fields, private messages, and screen-off periods, encrypt the index locally, and support immediate deletion plus per-item expiry. The relay receives only query/result metadata unless the owner explicitly requests content.
- **missing:** An owner-controlled capture policy and visible recording indicator spanning browser and Mac windows; A local encrypted episodic index keyed by time, app/tab pseudonym, URL/document locator, OCR snippets, and visual embedding; A Mac-to-relay query endpoint that returns provenance and confidence without uploading the raw index; A pendant interaction for narrowing results by time, app, or spoken remembered phrase; Deletion and expiry controls that can prove a result was removed rather than merely hidden

### "“What has this system retained about me, where is it stored, and delete every copy you are allowed to delete?”"
- **useful because:** The owner currently cannot obtain one truthful inventory across the Mac, browser bridge, relay, audio stores, announcements, evidence capsules, and job history. A privacy ledger would expose the actual copies and retention state—not just policy text—and let the owner revoke or delete them with a receipt, including an explicit list of copies that require manual action or cannot be removed.
- **path:** relay-realtime → faculty-perception → faculty-judgement → faculty-action → mac-planner → browser-extension
- **model tier:** A cheap background model groups and explains records; deterministic code enumerates stores and performs deletion. Realtime only answers the owner and requests confirmation for destructive deletion.
- **latency:** Inventory in under 10 seconds with bounded records; deletion begins only after a clear confirmation and returns a per-store receipt within 30 seconds.
- **cost:** Usually under $0.02; the dominant cost is bounded local/relay enumeration, not inference.
- **security:** The inventory itself is sensitive and must be local-first, redacted by default, and scoped to the authenticated owner. Destructive deletion needs an explicit preview and confirmation, immutable tombstone receipts without content, and honest reporting of backups, browser-provider copies, or stores that cannot be reached.
- **missing:** A common retention/deletion manifest emitted by each Mac, browser, relay, audio, and evidence store; Authenticated read and delete adapters for relay announcements/audio, Mac ledgers/jobs/capsules, and browser spool/provenance; A cross-store correlation key so the same capture or page excerpt is not reported as unrelated copies; A deletion receipt format that distinguishes deleted, expired, withheld, unreachable, and provider-retained

### "“Freeze this moment so I can continue it later from the pendant, the Mac, or the browser—reopen the exact work state, not just a reminder.”"
- **useful because:** A reminder preserves an intention but loses the working set: the authenticated tab, selected text, desktop document, unsent draft, and the owner’s spoken reason for stopping. A portable, owner-invoked work capsule would let the owner leave the Mac and resume the same bounded task later, while explicitly refusing to snapshot secrets or claim that an external site state is restorable.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-action
- **model tier:** Cheap local extraction creates a structured work capsule; realtime only handles the spoken save/resume interaction. Use deterministic reopen/verify steps, with a slower model only for summarizing the owner’s reason and unresolved questions.
- **latency:** Save in 2 seconds; resume preview in 3 seconds and restore in under 10 seconds, with a spoken progress update if a tab, app, or session is unavailable.
- **cost:** Under $0.02 per save/resume; local capture and reopening dominate. No page body needs to leave the Mac.
- **security:** Never serialize passwords, cookies, tokens, private form values, or raw page bodies. Store app/tab pseudonyms, safe URLs, document IDs, selected non-secret text hashes, window geometry, and an owner-spoken note. Reopen must re-authenticate normally and require confirmation before restoring unsent or externally visible drafts.
- **missing:** A cross-surface work-capsule schema with secret classification and explicit restorable/non-restorable fields; Mac and browser snapshot adapters that can restore state without copying credentials; A relay-held handoff record with expiry, revocation, and device-independent ownership; A resume verifier that reports exactly which parts reopened and which did not


## What it asked for

_Nothing._
## Its own summary

Established fresh live truth: the exact AI Pendant Agent now has Accessibility and Screen Recording, all required permissions are present, browser bridge is online with two Safari tabs and zero pending commands, and the D1 relay/Mac bridge are reachable. I recorded this and informed judgement. I proposed three new owner-facing capabilities: single-use, target-bound spoken consent before consequential browser actions; uncertainty-aware “what is visible now?” screen perception; and semantic before/after receipts that distinguish verified from merely executed and support honest undo. The first is the strongest candidate for the system’s most useful cross-surface behavior.

**Biggest unknown:** The pendant itself is still absent from the relay and cannot validate any wearable delivery claim. For implementation, we still need the exact live screen-capture/vision result contract, a target-bound approval envelope, and a semantic postcondition/receipt bridge joining Mac action ledger, browser command, evidence capsule, and undo. I asked mac-vision to confirm what already exists so future proposals do not duplicate it.

