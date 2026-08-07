# Harness derivation — mac-planner — round 84

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-planner live state 2026-08-07T12:07Z** — The new read-only observation route works and shows 16 apps running with Claude foreground, 3 durable browser sessions (time.is/UTC plus two test forms), but Chrome extension offline with 5 pending commands. Accessibility and Screen Recording are both false for AI Pendant Agent; UI actions report success while doing nothing. Relay is reachable and mac bridge online.
  - evidence: GET /observe 200 and GET /ops/snapshot 200 at 2026-08-07T12:06:59Z
- **Granted Mac inspection tools** — mac_readonly_inspect and mac_read_sources are present in the tool schema but backend calls currently return 'This tool was granted a schema but has no implementation yet'; use authenticated GET /observe and existing local routes as the current read-only fallback.
  - evidence: Five direct tool calls in round 84 returned the same implementation error; GET /observe returned 200 with live state.

## Capabilities it proposed

### "“If something I asked you to do got stuck, silently verify what really happened, quarantine any stale browser action, and tell me exactly what needs my one decision.”"
- **useful because:** Today the Mac can report a successful UI receipt even when Accessibility rejects the event, and the browser can be offline with five queued commands. This capability turns those contradictory states into a trustworthy recovery answer instead of a false completion or unsafe replay. It is genuinely cross-node: the relay keeps the request alive, the Mac observes execution reality, and the browser extension owns the authenticated tab/queue.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use a cheap background classifier/rule engine for correlation, stale-lease detection, and receipt-vs-observation comparison; use realtime only for the final short spoken explanation or the one decision question.
- **latency:** Initial verification 1–3 seconds from cached job/observe state; browser reattachment or a fresh read may take 5–15 seconds. Pendant response should be under 2 seconds when no decision is needed.
- **cost:** Usually <$0.01 per recovery using rules and existing route reads; occasional 1–3k-token planner call dominates when multiple jobs or tabs must be reconciled. No audio generation unless the owner asks for spoken output.
- **security:** Do not replay a queued browser mutation merely because a lease expired. Compare command idempotency/session affinity, current tab URL/title, and evidence capsules; quarantine ambiguous commands and expose their intended effect. Authenticated page text stays on the Mac/relay path and is redacted in the pendant brief. Any retry that mutates a site must remain stopped for owner choice.
- **missing:** A durable dead-letter/quarantine record for browser commands with reason, age, session binding, and suggested recovery; A verifier that joins Mac action receipts to /observe state and marks UI actions unverified when accessibility.trusted=false; A relay notification contract carrying one recovery card to the pendant without waking a full realtime session; A dashboard view showing stale jobs, quarantined browser commands, and the exact evidence behind the decision

### "“Save this exact moment for later.” Then, days later: “Resume the thing I saved,” and bring back the right page, file, and short explanation of what I was trying to do—without making any change on my behalf."
- **useful because:** A bookmark loses the owner’s intent, selected evidence, and stopping point. This would preserve a genuinely resumable handoff across the pendant, authenticated browser, relay, and Mac: the owner can interrupt a form, research thread, or desktop task and recover it without reconstructing the context from memory.
- **path:** pendant → relay → browser-extension → mac-planner → dashboard
- **model tier:** Use a small background model only to compress the spoken intent and extract a task title; use deterministic capture for URL/tab identity, selection, file path, timestamp, and action state. Use realtime only when the owner asks to resume and wants a spoken explanation.
- **latency:** Capture acknowledgment under 1 second; capsule persistence under 3 seconds. Resume should restore or open the relevant surfaces within 5 seconds, then provide a 10–20 second explanation.
- **cost:** Typically <$0.005 per save and <$0.02 per resume; the only meaningful model cost is compressing a long spoken note or reconciling an expired tab. Storage is small JSON plus optional owner-selected screenshot, retained for 30 days by default.
- **security:** Authenticated URLs, selected text, and form drafts are sensitive. Encrypt capsules at rest, classify fields, redact secrets and passwords, bind browser capsules to a specific session/tab, and never submit or mutate on resume. Require explicit owner choice before reopening a private page on a different browser profile or exposing capsule contents through speech.
- **missing:** A first-class resumable-capsule schema with intent, tab/session binding, file identity, selection/scroll/form checkpoint, sensitivity, expiry, and provenance; A browser-extension capture message that returns the current tab state and selected text without reading unrelated tabs; A Mac-side checkpoint adapter for the active document and safe reopen operations; Relay synchronization and pendant commands for listing, expiring, and resuming capsules, including a compact spoken summary; Dashboard UI showing capsule contents and allowing the owner to revoke or edit them

### "“Compare the document open on my Mac with the policy in my logged-in browser, and tell me only the clauses that differ, with the exact source for each difference. Do not edit either one.”"
- **useful because:** The owner can currently read each surface separately, but cannot get a trustworthy, side-by-side semantic comparison spanning a local file and an authenticated page. This is useful for contracts, benefits, travel rules, and project specs where a missed wording change matters more than a general summary.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use deterministic extraction, normalization, and hashing first; invoke a slower text model only for clause alignment and semantic-difference explanations. Realtime is unnecessary except for the final spoken answer.
- **latency:** Extract both sources in 2–5 seconds; a long document comparison may take 15–30 seconds. Return a progress receipt to the pendant rather than holding a live voice turn.
- **cost:** <$0.03 for ordinary documents; long documents are dominated by embedding/alignment or model tokens. Keep excerpts and hashes, not whole documents, in durable state.
- **security:** Both sources may be confidential. Keep raw text on the Mac/relay boundary, redact credentials and unrelated page regions, cite URL/file path and section anchors, and never send either source to an external model without an explicit privacy policy. Read-only by default; no document edits or form submissions.
- **missing:** A source-pair binding that identifies a local document and one authenticated browser tab as the comparison inputs; A common extraction/normalization format preserving page anchors, file headings, and provenance; A clause alignment and semantic-diff worker with bounded excerpts and confidence scores; A cited comparison artifact and pendant-friendly renderer, with deletion and expiration controls


## Changes it proposed to its own stack

### `mac-harness` — Add an automatic observation sandwich around every ui_* action: capture /observe immediately before dispatch and again afterward, then enrich the existing action receipt with accessibilityTrusted, foregroundAppBefore/After, inputReachability, and verificationStatus (verified, unverified, or contradicted). Never block or require approval; if synthesized input is rejected, report the action as unverified instead of successful. For browser actions, attach the active session/tab identity and any evidence capsule ids to the same receipt.
- **owner gets:** The owner will stop hearing “done” when a click or keystroke actually did nothing. They get a truthful, concise result and can choose a retry or another route such as AppleScript, even while using the Mac themselves.
- effort: Medium: wrap computerControl dispatch and actionReceipt creation, persist two small observe snapshots per action, add dashboard/journal rendering and tests for Accessibility false, app focus changes, and browser-offline cases.  ·  risk: Extra observation could slightly increase action latency and may expose foreground-app names in logs; redact sensitive window titles and retain only bounded metadata. A post-action snapshot can still miss a fast transient, so label it verification rather than proof. Recovery is to fall back to the current receipt path if observation fails.
- cost: Negligible API cost; two local probes per UI action. Small JSON growth in the job journal, bounded by retention.  ·  latency: Approximately 50–200 ms per UI action locally; no model call.
- security: Improves auditability without adding authority or gates. It should avoid storing screenshots or keystroke contents in the observation record.
- depends on: GET /observe is already live; Existing action receipts from chg-5fc73ce3; Owner’s accepted FULL_CONTROL_MODE/no-confirmation policy; A small receipt schema extension shared with the relay and dashboard


## What it asked for

_Nothing._
## Its own summary

Round 84 established live truth via GET /observe and /ops/snapshot: relay and Mac bridge are reachable, but the browser extension is offline with 5 pending commands; three durable browser sessions remain; Claude is foreground; Accessibility and Screen Recording are false, so ui_* actions can report success while doing nothing. The newly granted mac_readonly_inspect and mac_read_sources schemas have no implementation yet, so /observe is the usable fallback. I recorded this finding, alerted perception/action/browser peers, proposed a recovery capability for stale/contradictory jobs, and proposed an observation-sandwich receipt change that adds truth without adding gates.

**Biggest unknown:** Whether the browser queue's five commands are safe to quarantine or belong to an active owner task; the extension must reconnect and expose command ids/leases before any recovery decision. Remaining need is implementation of the granted read-only Mac tools (or a supported equivalent) and durable dead-letter/quarantine plus receipt verification wiring—not another permission request.

