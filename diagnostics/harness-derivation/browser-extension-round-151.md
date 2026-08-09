# Harness derivation — browser-extension — round 151

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-live-read** — Safari is online with 9 tabs; POST /execute can synchronously list tabs and read an authenticated OpenAI billing page. The read result includes a content hash, redaction counts, evidence capsule ID, and reversible/read-only receipt.
  - evidence: POST /execute actions browser_list_tabs and browser_read_page(tabId 1148327) returned 200 at 2026-08-08T01:38Z.

## Capabilities it proposed

### "When I say “finish this application,” use the page I have open in Safari, fill every reversible field from my local files and calendar, and show me exactly what would be submitted without submitting it."
- **useful because:** This is the highest-value browser capability: the browser has authenticated context, the Mac has the owner's documents and calendar, and the pendant is the fastest way to approve or correct the final draft. Today those surfaces cannot jointly turn an open form into a trustworthy, reviewable completion.
- **path:** browser-extension → mac-planner → mac-vision → relay-realtime → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Background/standard model extracts field schema and matches local evidence; realtime model only handles the owner's spoken corrections and concise final readback.
- **latency:** First draft in 10–20 seconds; each correction under 3 seconds; never wait on a model after the final preview is rendered.
- **cost:** Roughly $0.03–$0.15 per application, dominated by page extraction and document grounding; reuse cached local facts and send only field-level snippets, not whole files.
- **security:** Authenticated page content and selected local documents leave the Mac only to the relay/model. Do not persist raw page text; retain a short-lived field/evidence capsule. Default to typing only reversible fields, visibly mark uncertain values, and stop before submit/send/purchase. Per-origin and per-category rules must be explicit configuration, initially empty.
- **missing:** A browser action that returns structured form controls plus labels and validation errors; A local evidence selector that can cite the exact file/calendar item used for each field; A cross-surface draft object with field-level provenance and a final preview UI/audio contract; A submit boundary that can be intentionally left unexecuted while preserving the draft

### "Remember this exact authenticated page and bring me back to the unfinished step tomorrow; if the page changed or my login expired, tell me what changed instead of silently reopening it."
- **useful because:** A normal bookmark loses the in-progress state and cannot tell whether an authenticated workflow is stale. This makes the browser session a durable handoff between a moment at the desk and a later pendant reminder, while preserving the owner's control over sensitive pages.
- **path:** browser-extension → relay-realtime → mac-planner → relay-realtime → pendant → unified → faculty-perception → faculty-action
- **model tier:** Cheap background model computes a redacted semantic checkpoint and change diff; realtime tier is only used to speak the alert or answer a follow-up.
- **latency:** Capture under 2 seconds; scheduled wake-up under 10 seconds after its due time; change explanation under 5 seconds.
- **cost:** About $0.01–$0.05 per checkpoint/change, mostly page extraction; no model call when the page fingerprint is unchanged.
- **security:** Persist only origin, title, locator, redacted checkpoint, and encrypted short-lived session reference—not page text or cookies. Per-origin retention and may-speak rules are owner-supplied and empty until configured. Never auto-submit or auto-send after reopening; alert if the URL, identity, or form schema differs.
- **missing:** A durable authenticated-session checkpoint primitive with encrypted, expiring references; A semantic page-diff action that compares a checkpoint against a later authenticated read; A routine trigger that can dispatch a targeted alert to offline_alert_inbox; A browser reopen/resume action that returns to the exact tab and locator

### "Build me a private evidence packet for this charge or account problem: inspect the authenticated page, find matching receipts and emails on my Mac, make a dated timeline, and draft (but do not send) the support message."
- **useful because:** When a charge is wrong, the work is split across a logged-in billing page, local mail/files, and a support form. A single node cannot authenticate to the page, search local records, and prepare a cited, reviewable response. The owner gets an answer and a ready next step rather than a vague summary.
- **path:** browser-extension → mac-planner → mac-terminal → relay-realtime → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Background model performs OCR/extraction, deduplication, and timeline assembly; realtime model only answers clarifying questions and reads the short conclusion.
- **latency:** Evidence packet in 30–60 seconds for up to 20 artifacts; incremental additions under 5 seconds.
- **cost:** Approximately $0.05–$0.30 per packet, dominated by document/page extraction; use local hashing and deterministic date/amount matching before invoking a model.
- **security:** Financial/account data is highly sensitive. Keep raw artifacts on the Mac; send only redacted excerpts and hashes for reasoning; never store page text by default. Require explicit per-origin and per-category configuration, with a visible list of artifacts and redactions. Drafting is reversible; sending the support message remains a separate, unperformed action.
- **missing:** A local-only artifact collector that can pass selected Gmail/files evidence as references; Cross-surface entity resolution for merchant, amount, account, and dates; A cited packet format with redaction controls and expiry; A browser form-draft operation that can populate support fields without submitting

### "While I’m on any logged-in site, tell me what personal information and permissions this site can currently see, compare it with my privacy preferences and local account records, and prepare a precise list of settings I could revoke without changing anything yet."
- **useful because:** The owner cannot get a trustworthy, account-specific privacy audit from a generic web search: only the browser can see the live logged-in identity, enabled integrations, consent state, and account settings. The Mac can compare those disclosures against the owner's own records and preferences, while the pendant can explain the risks in plain language at the moment they matter.
- **path:** browser-extension → mac-planner → mac-terminal → relay-realtime → pendant → unified → faculty-perception → faculty-judgement
- **model tier:** Use a cheaper background model for page extraction, permission taxonomy, and deterministic comparison; reserve realtime only for the owner's spoken questions and a short spoken risk summary.
- **latency:** Initial audit in 20–40 seconds for one origin; follow-up setting explanations under 5 seconds. No background polling unless the owner explicitly schedules it.
- **cost:** About $0.03–$0.20 per audit, dominated by authenticated page extraction and model classification; hashes and local rules avoid resending unchanged pages.
- **security:** This reveals highly sensitive identity, payment, health, and connected-account details. Raw page content should remain on the Mac whenever possible; the model receives only extracted permission rows and redacted evidence. Persist the audit as an expiring, encrypted report with origin and timestamp. Never revoke access automatically; show each proposed change and stop before any save/confirm action. The owner's per-origin and per-category speak/store rules must be explicit configuration, initially empty.
- **missing:** A browser snapshot that exposes semantic settings rows, consent controls, and linked integrations rather than only page text; A local privacy-preference and account-inventory projection that can be compared without exporting raw records; A normalized permission vocabulary with evidence citations and confidence; A reversible settings-plan preview that can identify the exact controls to change but intentionally does not apply them

### "For the account I’m looking at, make an offline recovery kit: list the exact recovery methods and backup codes I already have, identify what is missing, and guide me through fixing the gaps without exposing secrets or changing settings for me."
- **useful because:** Account recovery is usually discovered only after the owner is locked out. The browser can inspect the authenticated provider’s actual recovery state, while the Mac can verify local access to the owner’s authenticator, recovery files, and trusted devices. The pendant can guide a safe checklist even when the browser is no longer available.
- **path:** browser-extension → mac-planner → mac-terminal → relay-realtime → pendant → unified → faculty-perception → faculty-action
- **model tier:** Background model normalizes recovery controls and matches non-secret device/file metadata; realtime is limited to interactive spoken checklist guidance.
- **latency:** Audit in 15–30 seconds; each checklist step explained in under 3 seconds.
- **cost:** About $0.02–$0.12 per account audit, mostly authenticated page extraction; secrets and backup-code contents stay local and are never sent to the model.
- **security:** Recovery data is exceptionally sensitive. Never extract, speak, or persist passwords, tokens, or backup codes; only record presence, count, age, and storage location. Require an explicit owner-selected origin and local confirmation before inspecting authenticator/file metadata. Never alter recovery settings or send codes automatically.
- **missing:** Semantic extraction of security/recovery controls and trusted-device state; A local-only secret-presence checker that proves availability without reading secret values; An encrypted, offline pendant checklist payload with expiry and emergency wipe; A recovery-gap planner that can point to controls without clicking save

### "Compare the same fact across the private pages I have open and my local records—for example a plan price, renewal date, delivery status, or account name—and tell me exactly where they disagree, with the newest source and a suggested next step."
- **useful because:** Today each page can be read, but nobody reconciles contradictory authenticated views. This would catch silent renewals, stale account details, and support mistakes before the owner acts, using browser sessions that public search cannot access and local records that the browser cannot see.
- **path:** browser-extension → mac-planner → mac-terminal → relay-realtime → pendant → unified → faculty-perception → faculty-judgement
- **model tier:** Deterministic extraction and date/amount comparison first; a cheap background model explains conflicts and ranks source reliability. Realtime only speaks the concise discrepancy report.
- **latency:** Up to four tabs plus selected local records reconciled in 15–30 seconds; a single additional source under 5 seconds.
- **cost:** Approximately $0.03–$0.18 per reconciliation, dominated by extracting multiple pages; unchanged sources can be content-hash cached.
- **security:** Cross-origin correlation can expose more than any one page. Require an explicit set of tabs/records for each run, keep raw artifacts local and expiring, and send only redacted facts with citations. Never infer or announce sensitive categories the owner has not enabled; never edit a source automatically.
- **missing:** A user-selectable multi-tab capture with stable citations and timestamps; A local-record query that returns typed facts rather than raw mail/files; Source reliability and conflict-resolution rules that are inspectable; A spoken discrepancy card that links each claim to its originating tab or local artifact


## What it asked for

_Nothing._
## Its own summary

The browser tier is now genuinely usable: Safari is online with 9 tabs, and I verified authenticated page extraction through POST /execute. I recorded three new cross-surface capabilities: (1) “finish this application” — browser form schema + Mac evidence/calendar + field-level provenance + pendant review, stopping before submit (my single most useful proposal); (2) authenticated workflow checkpoints that detect stale pages/login expiry and resume later; (3) private charge/account evidence packets assembled from the authenticated page plus local mail/files, with a cited draft support message but no send. What I still need is not another enqueue wrapper: I need structured form-control/validation extraction, a field-level evidence/provenance object, an encrypted expiring session checkpoint, a semantic page-diff, local artifact selection, and an explicit submit boundary. The owner must eventually provide per-origin and per-category read/speak/persist rules; those should ship empty rather than be guessed.

**Biggest unknown:** Which authenticated origins and data categories the owner actually wants enabled. The live browser proves reachability, but inventing a site list or sensitivity policy would be unsafe.

