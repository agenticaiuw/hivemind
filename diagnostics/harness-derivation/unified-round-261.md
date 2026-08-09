# Harness derivation — unified — round 261

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “do it,” stage the risky browser/Mac work, read me exactly what will happen, let me approve it with the pendant button, then finish it and tell me what physically completed—even if the Mac or relay went offline in between."
- **useful because:** This is the core trustworthy action loop: today a blocked plan can be spoken about and discarded, while the approval machinery cannot complete because relay persistence and delivery are missing. The owner gets one continuous, auditable outcome instead of a promise that silently stops.
- **path:** relay → pendant → mac-bridge → browser → dashboard
- **model tier:** planner for decomposition and risk explanation; realtime only for the spoken summary; deterministic executor and receipt verifier for the actual steps
- **latency:** Stage summary in under 3 s; button approval acknowledged locally in under 250 ms; execution may take minutes but survives reconnect and reports progress at the next turn.
- **cost:** ~$0.01–$0.05 per staged action depending on planner use; browser/Mac execution and receipt polling dominate latency, not tokens.
- **security:** Never send page secrets to the pendant. Bind approval to the existing plan digest, world fingerprint, nonce, expiry, and replay counter; require physical_transaction_approval_latch. A changed page, expired lease, or unrepeatable step becomes blocked rather than guessed. The owner must confirm destructive/off-machine steps.
- **missing:** Implement the relay half of APPROVAL_STORE_CONTRACT and speak the staged readback on the next conversation (unprompted pendant push is unavailable).; Wire prepareAction into the live orchestrator and close ordinary ledgers.; Add relay_jobs lease_until/requeue sweep and a continuation worker.; Connect the physical approval nonce to /approve, then dispatch only the bound plan.

### "After any action, answer “did it really happen?” with one compact evidence card: what the Mac changed, what the browser submitted, whether the relay accepted the job, and whether the pendant actually started and finished playback."
- **useful because:** A successful API response is not the same as a changed account, and relay acceptance is not the same as hearing. This gives the owner a single trustworthy answer across the surfaces that each know a different part of reality.
- **path:** relay → mac-bridge → browser → pendant → dashboard
- **model tier:** deterministic evidence join first; background model only to summarize conflicts or missing evidence
- **latency:** Return known receipts in under 1 s; wait up to 5 s for late browser/audio acknowledgements, then label the card pending rather than claiming success.
- **cost:** <$0.005 for a normal join; storage and polling dominate, with model cost near zero unless evidence conflicts.
- **security:** Use opaque job/artifact IDs and redact page text, form values, and audio. Query only the bound browser sessions/apps. Distinguish observed, reported, and inferred fields; never upgrade a receipt into physical completion.
- **missing:** A typed cross-surface join route with source enums and correlation IDs for job, browser command, pipeline artifact, and audio-delivery events.; Persist the pendant-side audio_delivery_ack_queue events at the relay and expose playback-start/finish/interruption to the join.; Add Mac receipt correlation for run_shell results, which currently lack exit code/argv/env.

### "When a conversation drops, let me press once and continue from the last confirmed turn: tell me what was heard, what was not delivered, and ask only for the missing part instead of making me repeat myself."
- **useful because:** The owner currently cannot tell whether silence means LTE loss, relay failure, or playback failure. A confirmed-turn handoff turns a dropped call into a recoverable interaction and prevents duplicate commands or repeated sensitive speech.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** deterministic sequence/ack reconciliation; background model to compress the missing-turn summary; realtime only when the owner resumes speaking
- **latency:** Local press feedback under 250 ms; resume summary under 2 s after reconnect; no automatic replay of owner audio without a new press.
- **cost:** <$0.01 per recovery; event storage and retransmission dominate, and summarization is optional.
- **security:** Use monotonic turn IDs, artifact hashes, and separate captured/accepted/played states. Never persist successful-path raw audio; only failure-path OUTBOX data is retained. Require a fresh deliberate press before recapturing speech, and discard ambiguous duplicate turns.
- **missing:** A relay turn-reconciliation record that joins capture, relay acceptance, model response, and playback acknowledgements.; Pendant/bridge firmware emission of compact turn-boundary and playback state events over the registered LTE path.; A resume endpoint that returns only the first unconfirmed turn and marks it claimed, with expiry and idempotency.

### "While I am on a phone or video call, let me quietly ask the pendant for help—“what did they just ask?”, “give me a concise answer”, or “remind me what I promised”—and hear the suggestion privately without the other person hearing it. Do not record the call unless I explicitly start a note."
- **useful because:** This gives the wearable a capability no Mac, browser, or phone control surface can provide alone: private, in-the-moment cognitive assistance while the owner is occupied in a live conversation. It can reduce missed commitments and let the owner stay present instead of looking at a screen.
- **path:** pendant → relay → mac-bridge → ios-control → browser
- **model tier:** realtime model for low-latency whisper responses; background model for optional post-call commitment extraction only after explicit opt-in
- **latency:** Button-to-whisper acknowledgement under 300 ms; short answer under 2 s. If transcription is incomplete, say so rather than inventing context.
- **cost:** Approximately $0.02–$0.15 per assisted exchange depending on audio duration and realtime transcription; the live audio stream dominates cost.
- **security:** The default must not continuously retain or upload call audio. Use a deliberate pendant gesture to open a short, visibly bounded assistance window, show an active LED state, and automatically close it after the answer. Separate the owner's microphone from call audio where technically possible; if call audio cannot be isolated, require explicit consent before capture. Redact phone numbers, contact names, and sensitive transcript content from durable logs. Do not send suggestions into the call or control the phone without a separate confirmation.
- **missing:** A phone-call audio tap or OS-supported live transcription source that can provide the remote speaker's audio without relying on prohibited screen/accessibility scraping.; A pendant interaction mode for short private queries while another audio session is active, with hard capture duration and privacy-latch precedence.; A low-latency audio mixer that routes the assistant response only to the owner's earpiece and never to the call uplink.; An explicit owner setting for which calls/apps may be assisted and whether call audio may leave the phone.

### "Before a website or app sends anything sensitive, tell me exactly which data will leave the device, which account and recipient it is going to, and let me approve only that disclosure from the pendant. Block hidden or newly added fields instead of submitting them silently."
- **useful because:** The owner can currently approve an action without seeing the full data boundary. This protects against autofill mistakes, wrong-account browser sessions, malicious page changes, and accidental disclosure while still allowing ordinary low-risk forms to proceed quickly.
- **path:** browser → mac-bridge → pendant → relay → dashboard
- **model tier:** deterministic field and destination diff first; planner model only for explaining unfamiliar fields in plain language
- **latency:** Inspect and summarize a normal form in under 500 ms; approval remains valid only while the form and destination fingerprint are unchanged.
- **cost:** Usually below $0.005 per submission; DOM inspection and hashing dominate, with model use only for ambiguous labels.
- **security:** Never upload field values merely to classify them. Hash or locally classify values, redact secrets, bind approval to origin, account/session identity, destination, field names, and a page fingerprint. A page mutation invalidates approval. Require explicit confirmation for credentials, financial data, health data, messages, and off-machine uploads.
- **missing:** A browser-side pre-submit interception hook that exposes the final request payload and destination before network transmission.; A typed sensitive-field classifier that runs locally and returns reasons without exporting values.; A browser identity/session attestation so the owner can distinguish accounts with the same origin.; A pendant approval frame carrying the disclosure digest and expiry.

### "When I am about to act in the wrong account, recipient, or context, stop me before the action: say “this is your work account, not personal” or “this goes to Alex Smith, not Alex Lee,” and require a deliberate pendant confirmation only when the context differs from my normal pattern."
- **useful because:** A browser can be logged into several accounts and a Mac can address similarly named contacts. Preventing a wrong-recipient or wrong-account mistake before submission is more valuable than undoing it afterward, especially for messages, purchases, permissions, and shared documents.
- **path:** browser → mac-bridge → ios-control → pendant → relay
- **model tier:** deterministic identity and destination matching for known entities; background model only to resolve ambiguous names; realtime for the short spoken warning
- **latency:** Context check under 300 ms for known accounts/contacts; ambiguous matches produce a clear hold rather than delaying indefinitely.
- **cost:** <$0.005 for known entities; occasional disambiguation costs a small planner call.
- **security:** Identity metadata must be minimized and locally hashed where possible. Never infer identity from page appearance alone when an account/session attestation is unavailable. Do not auto-send or auto-select among ambiguous recipients. The owner can configure trusted account labels and must be able to disable pattern-based shortcuts.
- **missing:** A cross-surface account and recipient identity registry with owner-editable labels.; Browser session attestation and iOS contact/account metadata access.; A pre-action context gate integrated with form submission, message send, and permission changes.; A compact spoken warning protocol and pendant confirmation nonce.


## What it asked for

_Nothing._
## Its own summary

Recorded three new owner-facing capabilities: private pendant coaching during phone/video calls without default recording; pre-submit data-boundary inspection and disclosure approval; and wrong-account/wrong-recipient context protection across browser, Mac, and iOS. Each requires new cross-surface hooks rather than merely exposing existing routes.

**Biggest unknown:** Whether the phone and call surfaces can provide an OS-supported remote-audio/transcription feed without recording or accessibility scraping; this determines whether private live-call coaching can ship with the intended privacy boundary.

