# Harness derivation — browser-extension — round 229

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“I’m looking at a page—read the important part and answer my question.”"
- **useful because:** This would make the pendant a hands-free lens into authenticated Safari: the owner can ask about a bill, dashboard, or account page without dictating a URL or touching the Mac. The browser supplies the live page, the relay answers briefly, and the pendant speaks it; public pages continue to use cheaper web search.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** Realtime for the short spoken answer; browser extraction and claim compression should be deterministic/local first, escalating to the expensive model only when the question needs interpretation.
- **latency:** 4–8 seconds from button/voice request to a one-sentence answer; browser read is usually sub-second and model time dominates.
- **cost:** Roughly one short realtime turn, typically <$0.01–$0.05 depending on model; no page body needs to be resent if the browser emits bounded extracted claims plus a content hash.
- **security:** The active tab may contain secrets. Never send the whole DOM by default: extract the visible/selected region, redact credentials and payment data, and keep the current 24-hour, host-keyed browser-finding retention. The owner already permits browser reads; still stop if the question would cause a mutation.
- **missing:** A reliable browser_read_current_page/focused-region operation (the previously requested grant is still absent); A pendant intent that carries a question plus the current browser session/tab identity; A bounded extractor that turns a page into claims before model context assembly

### "“Finish this web form later.” / “Resume the form I started, show me exactly what is filled, and stop before submission.”"
- **useful because:** Long authenticated forms are where browser automation loses the owner’s work. A resumable draft would preserve field values and their source, reopen the same session, detect changed or invalid fields, and present a spoken/visual diff before any submit. It is materially different from a one-shot fill: interruption, browser restart, and changed-page recovery are first-class.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Background/local planner for field mapping and recovery; realtime only for the owner’s short resume/diff conversation. Use deterministic DOM labels and stored provenance before a model.
- **latency:** Resume in under 5 seconds; diff generation under 2 seconds for ordinary forms.
- **cost:** Usually <$0.01 per resume when deterministic; model fallback adds a small request only for ambiguous fields. Storage is a few KB of field metadata, not page HTML.
- **security:** Drafts can contain personal and financial data. Encrypt locally, bind them to origin and form fingerprint, expire by default, and never put field values into general memory or speech unless requested. Submission remains an explicit owner action, with a final field/value diff and undoable local draft deletion.
- **missing:** An encrypted browser-draft store with per-origin expiry; browser actions to read field values and restore them without submitting; A form fingerprint/change detector and a spoken diff surface

### "“Compare the private page I have open with my local notes and the public sources, then give me a cited answer I can trust.”"
- **useful because:** This is the browser-only superpower in a useful form: reconcile an authenticated source unavailable to the relay with public evidence and the owner’s local context. For example, compare an account’s quoted renewal terms against a note and current public pricing, then speak the disagreement rather than silently choosing one.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Background planner for retrieval, normalization, and citation assembly; realtime is reserved for the final short answer or follow-up. Deterministic source labeling should precede model synthesis.
- **latency:** 10–20 seconds for a three-source comparison; answer playback starts as soon as the first verified conclusion is ready.
- **cost:** About <$0.05–$0.20 for a small synthesis depending on model and source count; public sources can use web_search/read_web_page, while private page text is bounded claims only.
- **security:** Keep private claims isolated from public-search prompts until the final synthesis, redact account identifiers, retain only short-lived host-keyed claims and provenance, and speak private details only in response to an explicit question. The result should enumerate source URLs, observation times, and conflicts so stale authenticated pages cannot masquerade as current facts.
- **missing:** A cross-surface evidence join that accepts browser evidence, local files/notes, and public web results without flattening their trust levels; A citation-aware synthesis schema with freshness/conflict scoring; A pendant playback format for “claim / source / disagreement” in one short response

### "“Move the private page I’m using on Safari to my other device and keep me signed in without showing or copying my password.”"
- **useful because:** The owner could continue an authenticated workflow while leaving the Mac—on a phone, another computer, or a future companion surface—without re-authenticating or exposing credentials. The browser extension would transfer a short-lived, origin-bound session handoff rather than page contents or cookies in general storage.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → iOS
- **model tier:** Background/local deterministic protocol; no large model is needed. Realtime only speaks status and asks for a brief confirmation if the destination is not already trusted.
- **latency:** Under 10 seconds for a handoff; failure must leave the original Safari tab untouched.
- **cost:** Negligible model cost. Engineering cost is in origin-bound handoff tokens and destination integration, not inference.
- **security:** This is effectively delegated authentication. Use one-time, short-lived, origin-bound handoff tokens, device pairing, replay prevention, and immediate expiry after import. Never export raw cookies, passwords, or page text. The owner needs an explicit trusted-device registry; a handoff to an unknown destination must fail closed.
- **missing:** A destination browser surface that can import an origin-bound handoff; Extension support for browser session handoff without exporting cookies; Pendant/device pairing and revocation state shared with the relay; A server-side single-use handoff-token endpoint

### "“I think I left something sensitive open—lock down my browser now.”"
- **useful because:** A worn device is the only surface likely to remain with the owner when the Mac is unattended. One deliberate pendant action could immediately close or blur sensitive Safari tabs, revoke the browser extension’s live command lease, and report what happened, without needing the owner to find the Mac.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** Deterministic emergency control; no model call should be required. Realtime is only a fallback for a spoken status report.
- **latency:** Best effort within 2 seconds while the Mac is reachable; queue a revocation for the next reconnect if it is offline.
- **cost:** Near-zero inference cost; small engineering cost for a signed emergency command and extension handling.
- **security:** The gesture must be unambiguous and locally acknowledged. It should revoke browser commands and close only tabs in a configured sensitive set by default, with an owner-selectable “close all” mode. Do not claim that remote website sessions were logged out unless the site confirms it; distinguish local tab closure from server-side logout.
- **missing:** A firmware emergency-control gesture distinct from ordinary playback/button actions; A signed, replay-resistant browser lockdown command from relay to extension; Extension handling for tab closure, command-lease revocation, and optional screen blur; A durable receipt that the pendant can replay after reconnect

### "“Let me operate this authenticated website hands-free: next field, choose the second option, and tell me where I am.”"
- **useful because:** Today the browser tier can issue discrete actions, but the owner cannot reliably drive a complex private site while walking or while the Mac screen is out of reach. A semantic interaction mode would expose a numbered, spoken control map for the current page, track focus and form state, and let the pendant advance through safe controls without CSS selectors or visual debugging.
- **path:** pendant → browser-extension → relay-realtime → mac-vision
- **model tier:** Local accessibility-tree/DOM parser first; realtime only interprets short commands and speaks the current focus. Vision is a fallback for canvas-heavy pages.
- **latency:** Under 1 second for focus movement and under 3 seconds for a spoken page-state update.
- **cost:** Very low for ordinary pages; occasional vision/model fallback costs a small realtime turn.
- **security:** Semantic labels can include private account data. Send only the focused control and nearby context, redact values marked password/payment, and never activate a submit/purchase/send control from a vague command. Preserve the owner’s existing maximum-access policy while making the interaction observable and reversible where possible.
- **missing:** An extension command for accessibility-tree extraction and semantic focus movement; A browser-side focus/session state machine that survives page rerenders; A pendant interaction vocabulary for next/previous/select/back; A reliable distinction between navigation controls and irreversible submit controls


## Changes it proposed to its own stack

### `integration` — Wire a first-class “page evidence packet” through the existing browser execution path: after browser_read_page/browser_snapshot, produce bounded claims (title, URL, observed time, selected facts, content hash, redaction counts), attach the evidence capsule to the owner’s voice request, and let the relay answer or hand it to Mac/local notes without resending raw page text. Add a single spoken/button entry point and a visible browser receipt so the owner can see exactly what was read.
- **owner gets:** The owner gets a dependable answer about the private page already open in Safari instead of a generic assistant that cannot see it. It turns today’s working browser read into the system’s signature capability, with clear evidence and less accidental leakage.
- effort: Medium: adapter between /execute browser receipts, evidence capsules, pipeline events/audio, and voice intent routing; no new browser extension protocol required for the first version.  ·  risk: A bad extractor could omit the important clause or expose a secret. Recover by retaining the source URL/hash and letting the owner request the raw page interactively; keep raw HTML out of memory and log only the bounded packet. If the browser disappears, report stale/unavailable rather than guessing.
- cost: Low incremental API cost; mostly deterministic extraction. A model is called only for question answering over the packet.  ·  latency: Adds roughly 0.5–2 seconds for extraction and routing; total answer remains within a short spoken interaction.
- security: Improves security versus sending DOM text: explicit origin/URL, redaction counts, evidence capsule, and 24-hour browser-fact TTL. Still needs the owner’s empty-to-explicit per-origin policy when he is ready.
- depends on: The existing POST /execute browser_read_page/browser_snapshot actions; Existing browser evidence capsules and provenance; A voice intent carrying the current browser session; Existing /pipeline/events and /pipeline/audio routes


## What it asked for

_Nothing._
