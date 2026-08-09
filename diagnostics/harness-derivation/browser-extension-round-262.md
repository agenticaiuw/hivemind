# Harness derivation — browser-extension — round 262

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-live-state** — Safari extension is online with one real authenticated-capable tab (tabId 85), currently a YouTube watch page; POST /execute browser_read_page succeeds and returns text, evidence capsule, provenance, and receipt.
  - evidence: GET /browser/status HTTP 200 at 2026-08-09T03:53:36Z; POST /execute browser_read_page HTTP 200 at 2026-08-09T03:53:42Z.

## Capabilities it proposed

### "Watch a logged-in page I name and tell me through the pendant only when a meaningful change occurs; summarize the delta, cite the exact on-page evidence, and keep checking until I say stop."
- **useful because:** This turns the browser's unique authenticated reach into a persistent personal sentinel instead of a one-shot scraper. The owner gets high-signal alerts while away from the Mac, including after a dropped link because the pendant's offline alert inbox queues them.
- **path:** browser → relay → pendant → dashboard
- **model tier:** background watcher uses a cheap scheduled model; realtime only speaks the alert or answers a follow-up
- **latency:** Initial setup under 10 seconds; each scheduled check 2–5 seconds; alert delivery within one polling interval, then immediate pendant playback when connected
- **cost:** Low per check; dominated by page extraction and cheap diff summarization, not realtime tokens
- **security:** Must not store page HTML or screenshots. Persist only short claims, host, URL, hash, and 24-hour findings using existing browser retention. Ship an empty per-origin policy and require the owner to fill it; stop before any mutation.
- **missing:** A durable browser page-watch scheduler that can keep an authenticated session alive and compare normalized regions; A relay-to-offline-alert-inbox delivery path for watcher findings; Owner UI/voice commands to stop, inspect, and delete a watch

### "When I say 'send this page to my phone', take the page currently open in Safari, extract the title and the exact link, put it into a draft/share sheet on my iPhone, and tell me on the pendant what is ready—never send it automatically."
- **useful because:** It bridges the browser session only this node can see with the real iPhone, eliminating copy/paste and preserving a reversible handoff. It is useful for authenticated pages, private dashboards, and links that cannot be reconstructed from public search.
- **path:** browser → mac-bridge → iOS → pendant → relay
- **model tier:** cheap planner for extracting title/URL and deterministic handoff; realtime only confirms readiness
- **latency:** 5–12 seconds from voice request to an iPhone draft
- **cost:** Very low; one browser read plus deterministic Mac/iPhone actions, with no background model needed
- **security:** The URL may contain private tokens or sensitive path data: show the exact title and URL on the pendant before opening the draft, redact only in spoken output according to the owner's configured policy, and never press Send. Keep the handoff receipt undoable.
- **missing:** A first-class browser-current-tab read action that returns a stable tab handle to the Mac planner; An iOS share/draft action accepting a URL without simulating an irreversible send; A cross-surface handoff receipt and undo endpoint

### "While I am watching or reading something in Safari, let me ask the pendant 'what does this number mean?' or 'where did that claim come from?' and answer from the current page with a short quote, page location, and confidence—not from memory or a generic web search."
- **useful because:** The owner can interrogate a private or authenticated page hands-free. Grounding every answer to the live tab and exposing evidence prevents the common failure where a general answer sounds confident but is unrelated to what is on screen.
- **path:** browser → relay → pendant → dashboard
- **model tier:** cheap extraction/model for page-local question answering; realtime voices the concise result
- **latency:** 2–6 seconds for an answer; under 1 second if the latest page evidence capsule is fresh
- **cost:** Low; reuse the existing page evidence capsule and invoke a small model only for synthesis
- **security:** Do not persist page text. Return a bounded quote and locator, retain only the existing evidence capsule/hash and short claim, and join browser facts to the prompt only when the question is explicitly page-local.
- **missing:** A reliable current-tab/focus context primitive (the existing browser read grant is ambiguous); Page locators for text spans or timestamps rather than document-level extraction only; A voice-turn contract carrying the active tab/evidence capsule ID

### "When a website reaches a human-only checkpoint—CAPTCHA, passkey prompt, biometric approval, or an ambiguous consent screen—tell me exactly what is waiting, let me complete only that step in Safari, then resume the rest of the task without losing its place."
- **useful because:** Many valuable authenticated workflows fail today at the point where automation must yield to the real person. This would let the owner safely combine their browser identity and human judgement with automation, rather than abandoning the task or handing credentials to a service.
- **path:** browser → mac-bridge → relay → pendant → dashboard
- **model tier:** cheap task-state model for checkpoint detection and resume; realtime only announces the checkpoint and captures the owner's short response
- **latency:** Checkpoint notification within 2 seconds; resume within 5 seconds after Safari reports completion
- **cost:** Low; mostly deterministic extension events, with a small model call only to explain the checkpoint
- **security:** Never solve or bypass CAPTCHA, never read passkey secrets or biometric data, and never infer consent. Pause with the exact page origin, visible action, and pending task; require the owner to perform the human step in Safari. Store only a task checkpoint, not page contents.
- **missing:** Extension events for navigation/focus/blocked-challenge detection and a stable tab lease; A resumable browser task state machine with checkpoint tokens and crash recovery; Pendant interaction for 'waiting / done / cancel' and a dashboard showing the paused action

### "Give me a private browser errand that can survive interruptions: open the authenticated site, collect the required facts across its pages, show me a compact checklist of what was found and what is still missing, and resume tomorrow exactly at the unfinished step."
- **useful because:** Long authenticated tasks such as insurance claims, returns, applications, and travel changes are currently too fragile for a voice request. The owner gets a durable, inspectable work state without having to keep Safari open or remember where they stopped.
- **path:** browser → mac-bridge → relay → pendant → dashboard
- **model tier:** background model extracts fields and plans page transitions; realtime is reserved for owner questions and spoken checkpoints
- **latency:** First plan under 15 seconds; each resumed step under 8 seconds; no need for a live voice connection while collecting
- **cost:** Moderate for multi-page tasks, dominated by page extraction; use small models for field normalization and reserve the expensive tier for ambiguity
- **security:** Persist a structured checklist and provenance, never raw page text or screenshots. Keep credentials and session cookies inside Safari. Any submission, payment, or message remains a separately displayed final action; the owner can inspect and cancel.
- **missing:** A durable browser task record with field-level provenance and resumable page checkpoints; A scheduler that can wake a task while preserving Safari session affinity; A dashboard/pendant checklist view and explicit final-action preview

### "When I am on a private web page, let me say 'make this understandable for my doctor/lawyer/partner' and have the system produce a short, audience-specific brief with links and quoted evidence, open it as a local draft, and let me edit it on the Mac before I decide whether to share it."
- **useful because:** The browser can reach information no other node can, but today it cannot safely turn that information into a useful handoff without copying it manually. This creates a reviewable bridge from authenticated pages to a human recipient while keeping sending under the owner's control.
- **path:** browser → mac-bridge → relay → pendant → dashboard
- **model tier:** background summarization model for the draft; realtime only gathers the audience and constraints and reads back the key points
- **latency:** 30 seconds for a multi-page brief; immediate spoken confirmation that a local draft is ready
- **cost:** Moderate, proportional to selected page evidence; no cost for transport or local editing
- **security:** Only explicitly selected pages or claims may enter the brief. Show source URLs and quoted evidence beside every material claim, keep the draft local until approved, redact configured categories, and never send automatically.
- **missing:** A user-selected multi-page evidence bundle rather than implicit whole-tab capture; Local draft creation with source-linked claims and an edit-before-share UI; A provenance-aware export format that prevents unsupported claims from appearing source-backed


## Changes it proposed to its own stack

### `browser-harness` — Add a browser extension command browser_capture_selection that returns the user's current selection, focused element label/value (with password fields hard-redacted), nearest semantic heading, URL, and a stable DOM locator; include a short-lived evidence capsule ID and reject capture when there is no explicit selection/focus. Let the pendant voice turn bind to that capsule for one question, then expire it.
- **owner gets:** The owner can highlight one confusing sentence, invoice line, or form field and ask the pendant about exactly that fragment instead of receiving a vague summary of an entire private page. It makes authenticated Safari useful in the moment and sharply reduces wrong-context answers.
- effort: Medium: Safari extension content-script/accessibility extraction, POST /execute action schema, and a one-turn relay context binding.  ·  risk: Some sites expose misleading accessibility labels or sensitive focused values; password/token inputs must be redacted locally. If extraction fails, fall back to page-level read and say so. Capsule expiry prevents stale context.
- cost: Negligible API cost; a few hundred bytes per capture and one small synthesis call. No hardware cost.  ·  latency: Adds roughly 100–300 ms over normal browser read; answer remains a 2–5 second voice turn.
- security: Improves minimization because only selected/focused content is sent. Still requires explicit empty per-origin policy and existing 24-hour browser-fact limits; never persist selection text.
- depends on: POST /execute browser action dispatch; A resolved browser current-selection/focus command (current browser-read grant is ambiguous); Relay support for one-turn evidence-capsule binding


## What it asked for

_Nothing._
