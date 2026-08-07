# Harness derivation — browser-extension — round 69

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“When I get back to my Mac, tell me which browser tasks actually ran while Safari was disconnected, which were safely held, and continue only the ones still pointed at the same page.”"
- **useful because:** Today a pending command can be claimed repeatedly by an offline device (the live poll already shows a home-chrome command with five attempts), leaving the owner unable to know whether a private-page action happened. This gives a concise spoken reconciliation and safe continuation across the pendant, relay, Mac, and authenticated Safari session.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** Background reconciliation uses a cheaper model; realtime is used only to speak the short result and accept “resume/rebind” commands.
- **latency:** Under 10 seconds after the browser heartbeat returns; no polling or model spend while all devices are offline.
- **cost:** Usually <$0.01 per reconnect, dominated by one small reconciliation summary; browser and status calls are local.
- **security:** Only command metadata, tab/session fingerprints, and receipts are spoken or sent to the model; page contents remain in the browser tier unless needed. Never silently rebind a command to a different account or tab; the owner can explicitly say resume/rebind, and the system should show the target URL and action first.
- **missing:** Lease/epoch-fenced browser delivery and quarantine described in the companion browser-harness change; A reconnect-triggered reconciliation routine that joins browser status, command receipts, durable sessions, and Mac jobs; A compact pendant notification/voice intent for stale-held versus completed browser work

### "“Before you use a logged-in website for me, tell me which account, workspace, and permission state the page is actually in—and warn me if it has silently switched accounts, expired, or landed on an MFA/consent screen.”"
- **useful because:** A browser session can remain open while its identity changes: a shared profile may switch accounts, a workspace may change, or an expired login may show a convincing sign-in page. The owner currently has no cross-surface identity-attestation report, so an otherwise correct-looking browser action can target the wrong account.
- **path:** browser-extension → mac-planner → relay → pendant
- **model tier:** Use a cheap background classifier for known login/account/session markers; use realtime only when the owner asks a question or needs the short spoken warning.
- **latency:** 2–5 seconds before a browser task begins, with no extra delay for pages already attested under the same tab/session fingerprint.
- **cost:** Typically <$0.005 per attestation, dominated by a small extraction/classification call; cached attestations avoid repeated model calls.
- **security:** The attestation must minimize exposure: return account/workspace labels, authentication state, and evidence snippets or DOM hashes—not passwords, cookies, or full page content. It should warn and annotate rather than impose a new approval gate; the owner’s maximum-access policy remains intact.
- **missing:** A browser identity-attestation schema with account/workspace/auth-state, evidence locator, timestamp, and expiry; Extension extraction of identity and MFA/consent markers from the active authenticated page; A task-start integration that attaches the attestation to browser receipts and spoken relay summaries; Cross-tab conflict handling when tabs in one session attest to different accounts


## Changes it proposed to its own stack

### `browser-harness` — Add lease- and epoch-fenced browser command delivery. On every extension heartbeat, issue a device session epoch and capability lease; browser/poll may claim only commands whose target device/session matches the current epoch. A claim expires after a short TTL, and if the device goes offline or its tab/session fingerprint changes, move the command to a durable quarantine record (preserving attempts, payload hash, tabId, URL, and timestamps) rather than returning it again. On reconnect, automatically requeue only commands whose lease and tab/session fingerprint still match; otherwise mark them stale and expose a typed resume/rebind operation. Make POST /browser/result reject late results from an old lease without deleting the command, and include queue age/stale count in browser status and receipts.
- **owner gets:** A disconnected or replaced browser cannot later execute an old click, form fill, or navigation against the wrong logged-in tab. When Safari returns, safe work resumes automatically where it is still the same page, while genuinely stale work is visible instead of silently replaying or disappearing.
- effort: Medium: schema fields and state transitions in browserBridge/browserSessions, heartbeat epoch issuance, poll/result fencing, status/receipt fields, plus crash/reconnect tests for duplicate claims and late results.  ·  risk: A legitimate long-running command may be quarantined on a transient network drop; recovery is automatic on matching re-heartbeat or an explicit rebind/resume operation. No action is refused based on content; only stale delivery is prevented. Existing processing rows need a one-time migration to expired/quarantined states.
- cost: Negligible storage and CPU; no additional model/API calls.  ·  latency: One heartbeat/status lookup and lease check per poll/result, sub-millisecond locally; reconnect may add one poll cycle.
- security: Reduces cross-device/session command replay and prevents late results from being associated with a new tab. Store hashes and metadata, not page contents, in quarantine records.
- depends on: GET /browser/status; POST /browser/heartbeat; GET /browser/poll; POST /browser/result/:commandId; GET /browser/sessions; chg-14accc01 request IDs/tab-session affinity

### `browser-harness` — Add an extension-side private-page egress filter with typed sensitivity labels. Before extracted page text, screenshots, or form previews leave Safari, classify and redact credentials, payment numbers, recovery codes, hidden input values, and other secret-like regions locally; transmit only the minimum selected DOM spans plus stable locators and a redaction manifest. Permit an owner-specified per-site policy such as 'never send message bodies' or 'send only table rows', and make receipts record what was withheld.
- **owner gets:** The owner can ask the pendant about a private page or prepare work from it without having to choose between no help and sending an entire authenticated page—including secrets or unrelated personal content—to the model. They get useful answers with an explicit account of what the browser kept private.
- effort: High: extension-side DOM/visual sensitivity detection, policy storage keyed to site/session, extraction API changes, redaction tests against dynamic web apps, and receipt/UI support.  ·  risk: A classifier can over-redact useful context or miss an unusual secret format. Recovery is a per-site policy override and a visible redaction report; the raw page remains available locally for a later explicitly requested operation. Never claim a page is safe solely because no marker was detected.
- cost: Small local CPU/memory cost in Safari; reduced model and bandwidth cost because less content leaves the device. No new external API spend.  ·  latency: Approximately 50–300 ms for DOM extraction and local redaction; visual pages may add up to 1–2 seconds.
- security: Substantially reduces accidental exfiltration of credentials and unrelated private content. Policies and manifests must be encrypted locally and must not include the redacted values themselves.
- depends on: browser_read_page/browser_snapshot extraction in the extension; A typed sensitivity/redaction policy store; Receipt support for redaction manifests; Relay and Mac summaries that preserve the browser’s redaction boundary


## What it asked for

_Nothing._
