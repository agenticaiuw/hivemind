# Harness derivation — browser-extension — round 133

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser live state** — Safari extension is online with three tabs: authenticated Gmail inbox (tab 901464) and two failed example.com tabs; Gmail is the pinned session tab but not active.
  - evidence: POST /execute browser_list_tabs returned tabCount=3, Gmail title/URL, and two example.com 'Failed to open page' tabs at 2026-08-07T18:16:09Z.

## Capabilities it proposed

### "“I’m looking at this page—save the important parts so I can ask about it later.”"
- **useful because:** The owner can turn a private, authenticated Safari page into a durable, sourced personal dossier with one voice request. The browser captures the exact evidence, the Mac stores a local searchable artifact, the relay keeps a compact pointer, and the pendant can later retrieve and read it even when Safari is no longer open.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use the cheap background model to extract and compress page evidence; use realtime only for the spoken command and later question answering.
- **latency:** Capture and save in 5–10 seconds; later pendant answers should begin in under 2 seconds from the compact index, fetching full evidence only when needed.
- **cost:** Typically one short background extraction plus embedding/indexing call, roughly $0.01–$0.05; storage and Mac execution dominate rather than realtime inference.
- **security:** Private page text leaves Safari and is stored on the owner’s Mac; relay should receive only a dossier id, title, URL, and redacted summary by default. Never capture passwords, payment fields, or hidden form values. Saving is reversible via delete.
- **missing:** A browser action to capture the active tab with bounded, user-visible evidence rather than truncated page text; A local encrypted dossier/index store and retrieval route shared by Mac and relay; Pendant command/event plumbing for ‘save this’ and later offline lookup; A redaction pass for secrets and personally sensitive fields before persistence

### "“This security or CI alert just arrived—tell me whether it is real, correlate it with my local project, and prepare the safest fix without publishing anything.”"
- **useful because:** A browser-only summary cannot tell whether a private GitHub alert is stale or already fixed locally. Safari can inspect the authenticated alert and run details, Mac-terminal can compare the checked-out repository and tests, and the relay can give the owner a concise pendant interruption with a ready-to-review patch or command plan. It turns an alarming inbox event into an evidence-backed decision while stopping short of push, merge, or disclosure.
- **path:** browser-extension → mac-terminal → mac-planner → relay-realtime → pendant
- **model tier:** Background/cheap model performs extraction, diff and test-result synthesis; realtime is reserved for the owner’s immediate spoken question and alert delivery.
- **latency:** Initial triage in 30–90 seconds, depending on local tests; pendant alert within 3 seconds of a high-confidence finding.
- **cost:** $0.02–$0.15 per incident, dominated by background reasoning over logs/diffs; browser and shell execution are local.
- **security:** Authenticated GitHub/email content and source code remain on the Mac whenever possible. Do not paste secrets into the relay or automatically open PRs, push commits, rotate credentials, or send incident mail. Show commands, diffs, test output, and destinations before any irreversible step.
- **missing:** An event trigger that classifies incoming authenticated mail/page alerts as security or CI incidents; A cross-surface correlation job joining browser evidence to the exact local repository/branch/commit; A sandboxed local test-and-diff runner with artifact redaction and a spoken alert channel; A durable incident record with status, owner decision, and expiry

### "“If the site needs me to unlock it, guide me through the one-time code or approval and then continue the task.”"
- **useful because:** Authenticated browser work currently fails at exactly the moment a site asks for a passkey, one-time code, device approval, or CAPTCHA. The browser can pause on the real challenge, the relay can notify the pendant without exposing page contents, and the owner can approve or type locally; afterward the browser resumes the original read-only or draft workflow instead of losing context.
- **path:** browser-extension → relay-realtime → pendant → mac-planner
- **model tier:** Realtime handles the short interruption and precise spoken guidance; a cheaper background model resumes extraction or drafting after authentication succeeds.
- **latency:** Challenge detection under 2 seconds; owner interaction naturally takes 10–60 seconds; resume within 3 seconds after completion.
- **cost:** Usually <$0.01 per challenge; cost is negligible compared with the owner’s lost time and failed sessions.
- **security:** Never send OTPs, passkeys, recovery codes, or CAPTCHA answers to the relay/model. The pendant should signal ‘approve’ or ‘I’m ready’; sensitive typing happens in Safari or a local secure prompt. Display the origin and challenge type, expire the paused job, and never auto-approve an unfamiliar domain or push notification.
- **missing:** Browser challenge detection for passkey/OTP/CAPTCHA/approval UI with origin and challenge metadata; A pause/resume state machine that preserves tab affinity and the original task safely; A pendant-local approve/ready interaction and relay notification path that carries no secret; A way to direct secret entry to Safari without the model receiving keystrokes

### "“Give you temporary access to only this one logged-in site for this one task, then revoke it and show me exactly what access remains.”"
- **useful because:** Today, browser access is effectively an all-or-nothing live Safari session: the assistant can act in whatever tabs the extension exposes, but the owner cannot create a narrowly scoped, time-limited delegation for a contractor-like task. A compartmented delegation would let the owner safely ask for work on a sensitive portal without granting broad ongoing access, and would produce a concrete post-task proof that the delegation expired.
- **path:** browser-extension → relay-realtime → mac-planner → pendant
- **model tier:** Realtime handles the owner’s short delegation command and status questions; a cheaper background model executes and audits the bounded task.
- **latency:** Delegation setup under 5 seconds; task latency depends on the site; revocation and an access report within 3 seconds of completion or timeout.
- **cost:** Less than $0.03 per task for policy evaluation and audit summarization; local browser execution and encrypted state are the main costs.
- **security:** The browser must enforce origin, tab, action, time, and data scopes rather than trusting model instructions. Never export cookies, tokens, passwords, or OTPs. Show the owner the exact domain, allowed operations, expiry, and captured fields before activation; revoke on timeout, tab close, device disconnect, or explicit pendant command. Preserve an append-only audit of attempted and completed actions.
- **missing:** An extension-enforced capability token bound to origin, tab/session, action class, field allowlist, and expiry; A revocation endpoint that invalidates queued and in-flight browser commands, not merely the model job; A preflight UI/pendant confirmation displaying the delegation scope and a postflight access report; Cookie/session compartmenting or a browser-side mediator so the server never receives raw credentials or unrestricted tab access


## What it asked for

_Nothing._
## Its own summary

Confirmed live Safari access: authenticated Gmail is open alongside two failed example.com tabs. Filed three non-duplicate capabilities: private page evidence dossiers for later pendant recall, cross-surface CI/security incident correlation with local repo tests, and secure pause/resume for OTP/passkey/CAPTCHA challenges without exposing secrets. Each names the missing connective pieces and existing routes.

**Biggest unknown:** Whether the owner wants any of these workflows prioritized, especially the security-alert correlation or authentication challenge handoff.

