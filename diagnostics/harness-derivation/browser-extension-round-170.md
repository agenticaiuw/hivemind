# Harness derivation — browser-extension — round 170

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-live-state** — Safari extension is online with 9 tabs, including authenticated Gmail inbox and X home; POST /execute browser_list_tabs succeeds. Active tab is X (tabId 1163292); Gmail tab is tabId 901464.
  - evidence: POST /execute {actions:[{type:"browser_list_tabs"}]} returned success at 2026-08-08T02:42:45Z.

## Capabilities it proposed

### "“Compare the confirmation I’m looking at with my calendar and inbox, and tell me if anything conflicts or changed.”"
- **useful because:** The browser can see authenticated confirmations and portals while the Mac can see local Calendar/Mail. A cross-source discrepancy check catches changed times, cancellation notices, wrong addresses, and duplicate bookings that no single node can establish. The pendant gets only a short actionable result, not page text.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Background/cheap model for extraction and field comparison; realtime only to answer the spoken follow-up.
- **latency:** 10–20 seconds for a one-off check; under 2 minutes for a scheduled watch.
- **cost:** Usually $0.01–$0.05 per check; browser/Mac reads dominate latency, model cost is small structured extraction.
- **security:** Authenticated page and local mail/calendar fields leave the device to the relay. Ship empty per-origin and per-category rules; default to ephemeral redacted fields, no raw page persistence, and require the owner to configure which origins/categories may be compared or spoken. Never send or cancel anything.
- **missing:** A cross-source comparison job that accepts browser tab/URL plus selected Calendar/Mail fields; Per-origin extraction and per-category speak/store policy UI; A durable discrepancy record with expiry and a pendant alert adapter

### "“Keep my private browser work resumable. If Safari crashes or a login expires, restore the relevant tabs and tell me what I was in the middle of without saving the page contents.”"
- **useful because:** Authenticated work is uniquely stranded in Safari today. A continuity layer would remember only origin, tab title, task label, expiry, and a short owner-approved checkpoint—not page text or cookies—then reopen tabs on the Mac, detect login expiry, and speak a concise recovery prompt through the pendant. It turns the browser from a one-session tool into a dependable everyday surface.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Cheap background model classifies tab titles and checkpoint text; realtime handles the owner’s spoken ‘continue’ or ‘forget it’.
- **latency:** Restore in 5–15 seconds; login-expiry diagnosis under 30 seconds.
- **cost:** Under $0.01 per restore; browser command round trips dominate, with occasional model extraction.
- **security:** Never persist cookies, DOM, screenshots, or raw page text by default. Persist encrypted origin/title/task metadata locally with TTL; make checkpoint capture explicit and configurable per origin. A restored tab can expose sensitive content on screen, so the pendant should announce only the site and task until asked.
- **missing:** Crash/session recovery state machine tied to browser tab IDs; Encrypted short-lived continuity store and owner-visible delete-all control; Login-expiry detection and a browser re-authentication handoff; Pendant spoken recovery/forget commands

### "“Find the forms or drafts I started in my logged-in browser, read me the exact fields that would be sent, and let me correct or stage them from the pendant—but never submit until I explicitly say submit.”"
- **useful because:** This makes the browser useful for tedious, high-consequence work without silently sending anything. Safari supplies sessions and form state, the Mac/relay turns it into a compact spoken card, and the pendant provides an accessible review/edit loop while the browser remains staged. The exact pre-submit payload and a hash of the page state prevent a stale form from being sent after the site changes.
- **path:** browser-extension → mac-vision → mac-planner → relay-realtime → pendant
- **model tier:** Cheap structured extraction for form fields and diffing; realtime only for spoken review, corrections, and the final explicit command.
- **latency:** 5–15 seconds to inspect a form; 1–2 seconds per correction; final submit path must show the payload before action.
- **cost:** $0.01–$0.04 per form review; DOM extraction is the main latency, with vision only for canvas/custom controls.
- **security:** Forms may contain financial, health, or identity data. Ship empty per-origin and per-category speak/store policy; redact sensitive values on the relay by default and keep the full staged payload only in the local browser agent. Never auto-submit, and invalidate the staged payload when URL, form fields, or page hash changes.
- **missing:** DOM/form-schema extraction that handles custom controls and file inputs; Local encrypted staging vault with page-state hash and expiry; Pendant vocabulary for field-by-field review and correction; A final explicit-submit command path with a fresh browser revalidation

### "“I’m signing into the desktop app. Use the verification code already in my logged-in browser to finish the sign-in, but never tell me or the model the code.”"
- **useful because:** The browser is the only node holding the owner’s authenticated web session, while the Mac is the node that can complete a local app flow. Today the owner must manually read and transfer one-time codes between them. A secret-preserving bridge could locate the current challenge in the browser, inject the code directly into the waiting Mac app, and return only success/failure to the pendant.
- **path:** browser-extension → mac-vision → mac-planner → relay-realtime → pendant
- **model tier:** Small background extractor constrained to a one-time-code schema; realtime only reports progress. The code must bypass model text generation entirely.
- **latency:** Under 10 seconds from spoken request to completion; abort after one code or 60 seconds.
- **cost:** Less than $0.01 per attempt; browser and local-app round trips dominate.
- **security:** This handles authentication secrets. The code must be transferred through an encrypted, short-lived local channel, never logged, persisted, spoken, or placed in model context. Require an explicit owner request naming the waiting app and reject ambiguous pages or multiple competing codes. Expire and erase all buffers immediately.
- **missing:** A browser extractor that returns a one-time secret only to a designated local consumer, not to the model; A Mac app-targeted secure text injection primitive with focus verification; A local ephemeral secret channel and zero-retention audit receipt; Pendant command handling for target-app selection and abort

### "“From the browser session I already have, export the exact account settings or booking details into the local Mac app I name, preserving links and dates but leaving passwords and payment data behind.”"
- **useful because:** Authenticated web systems and local Mac applications cannot currently exchange structured records without copy-paste. This would let the owner turn a private web confirmation, address, subscription, or appointment into a local task or record while preserving provenance and deliberately excluding secrets. It is more reliable than asking a model to paraphrase a page.
- **path:** browser-extension → mac-planner → mac-terminal → relay-realtime → pendant
- **model tier:** Cheap schema-constrained extraction and validation; realtime is only for conversational field selection.
- **latency:** 10–30 seconds per transfer, with a spoken field preview before local insertion.
- **cost:** $0.01–$0.03 per transfer; browser extraction and app integration dominate.
- **security:** Raw authenticated content may be sensitive. Extraction rules must be per-origin and user-configured, with deny-by-default fields for credentials, payment numbers, health data, and private message bodies. Store only the selected structured record locally, attach source URL and timestamp, and never submit or send it onward automatically.
- **missing:** A user-defined browser-to-app schema/field mapping registry; Local structured insertion adapters for Calendar, Reminders, Notes, and arbitrary Mac apps; A redaction/validation step that runs before any data leaves the browser process; Pendant field-by-field confirmation and cancellation

### "“I think someone may be using my browser. From the pendant, freeze my private browser session, close only the sensitive tabs, lock the Mac, and tell me exactly what was contained without reading page contents aloud.”"
- **useful because:** A wearable is the one surface available when the owner is away from the Mac and cannot safely inspect the screen. Today browser and Mac controls are separate. A coordinated emergency response can stop exposure quickly while preserving a minimal, non-content receipt of which origins were closed, then allow the owner to resume later from a deliberate unlock.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** Deterministic policy/action orchestration; no expensive model needed except optional spoken explanation.
- **latency:** Initiate in under 2 seconds; close/lock confirmation in under 8 seconds.
- **cost:** Negligible API cost; the dominant cost is extension/Mac command round trips.
- **security:** This is a high-impact local action and must be unmistakably triggered by a dedicated pendant phrase/button sequence, with a hardware-visible acknowledgement and an undo/reopen path. Do not capture screenshots or page text. Keep only origin, tab count, timestamp, and action receipt locally; relay should not retain it beyond a short TTL.
- **missing:** A pendant emergency intent and offline-safe local trigger; Browser tab sensitivity configuration and selective close/freeze operation; Mac lock command plus coordinated transaction/rollback record; A short-lived, content-free security receipt delivered back to the pendant


## What it asked for

_Nothing._
## Its own summary

Safari is genuinely usable now: the extension is online with 9 tabs, including authenticated Gmail, and POST /execute browser_list_tabs completed successfully. I recorded three new cross-surface capabilities: (1) authenticated confirmation/calendar/mail discrepancy detection—the strongest candidate for the system’s most useful daily feature; (2) privacy-preserving browser-work continuity and recovery; and (3) staged authenticated form review with exact payload/hash validation before explicit submission. All three were accepted, though the recorder flagged proximity to existing confirmation and form-review concepts, so future proposals should move further away rather than rephrase these. I still need owner-supplied per-origin and per-category read/speak/store policy, and eventually the first real sites/workflows to configure; I will not invent those. The generic browser enqueue grant remains ambiguous, but direct POST /execute browser actions work today.

**Biggest unknown:** Which authenticated sites and browser tasks the owner actually wants automated, and which data categories may be spoken versus never persisted. Without that explicit configuration, the browser can inspect tabs but should not infer sensitivity or build site-specific automation.

