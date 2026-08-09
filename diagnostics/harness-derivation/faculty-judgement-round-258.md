# Harness derivation — faculty-judgement — round 258

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I delegate something, make sure it either finishes or comes back honestly for recovery—even if the Mac, browser, or relay dies halfway through."
- **useful because:** Today a job can remain permanently 'processing' after a crash, so the owner cannot tell whether to wait, retry, or start over. A leased, resumable delegation would recover orphaned work without duplicate external actions and would surface a precise recovery choice.
- **path:** relay → mac → browser → pendant → dashboard
- **model tier:** background for lease/recovery decisions; realtime only for the owner's spoken status
- **latency:** Normal completion unchanged; crash recovery detected within 1–5 minutes, with an immediate dashboard/pendant status when the owner asks.
- **cost:** Negligible model cost; dominant cost is a few D1 reads/writes per lease sweep and one compact recovery summary when needed.
- **security:** Requeue only idempotent or explicitly reversible steps. Never replay a send, purchase, deletion, or other external side effect without a fresh autonomy-policy verdict and physical approval where required. Store only IDs, step hashes, and receipts in the recovery record.
- **missing:** relay_jobs lease_until and an atomic requeue sweep; a durable relay-job-id to Mac-job-id mapping rather than telemetry-only localJobId; step-level completion/idempotency metadata crossing the relay/Mac boundary; a recovery status route and owner-facing retry/abandon choice

### "Give me a morning brief that knows what I actually heard: continue after an interruption, skip what I acknowledged, and never claim delivery just because audio was generated."
- **useful because:** A generated artifact is not the same as a heard briefing. This would make the pendant a trustworthy conversational surface: playback position and item acknowledgements survive link loss, duplicates collapse, and unfinished items fall back to a reviewable Mac/dashboard queue rather than silently disappearing.
- **path:** relay → pendant → mac → dashboard
- **model tier:** background for compiling/ranking the brief; realtime only for barge-in and the owner's short follow-up
- **latency:** Brief compilation under 10 seconds; item state updates under 1 second when connected and reconciled on reconnect.
- **cost:** Low model cost after compilation; dominant operational cost is artifact metadata and a few authenticated ACK writes, not repeated synthesis.
- **security:** ACKs must be authenticated, monotonic, and deduplicated. The pendant receives opaque item IDs and bounded spoken text only; private content must still pass the existing delivery redaction gate. Never infer that downloaded means heard.
- **missing:** a single durable briefing manifest joining source item, audio artifact, cursor, and owner acknowledgement; relay ingestion of the existing pendant delivery ACK queue with offline replay and duplicate suppression; scheduler wiring that creates item IDs before synthesis and advances only on playback state; a dashboard review state for generated-but-unheard items

### "If a task gets stuck because a website needs me to log in or approve something, pause it safely, tell me exactly what is needed, and finish automatically once I have cleared the block."
- **useful because:** Authenticated browser sessions are physically reachable only through the extension, while planning and follow-up live on the Mac/relay. Today a blocked browser task either fails ambiguously or leaves the owner to remember it. This would turn a login wall into a durable, bounded handoff instead of a lost task or unsafe credential request.
- **path:** browser → mac → relay → pendant → dashboard
- **model tier:** background for classifying the block and preparing the next read-only step; realtime only to explain the block or receive the owner's approval
- **latency:** Detect a block during the current browser poll; notify within one attention-arbitrated cycle. Resume within one poll after the owner clears it.
- **cost:** Low: mostly browser snapshots and state polling; model calls only when the page state is ambiguous. No credential extraction or upload.
- **security:** The browser must return only a typed block reason (login, MFA, owner approval, unavailable page), never passwords, OTPs, cookies, or secret form values. Resume plans expire and are revalidated against current page/session state. Any send, purchase, deletion, or other external side effect remains a separate owner-confirmed action.
- **missing:** production wiring for the existing session-need/browser-job runner modules; a typed browser-block event and durable task handoff tied to the browser session; owner clearance detection that does not read credentials; resume-plan revalidation and a bounded, read-only first step after clearance

### "If I lose, replace, or temporarily lend out the pendant, let me keep my work and conversations without letting the old device impersonate me or receive anything new."
- **useful because:** Today the pendant is treated as the voice endpoint, but there is no owner-visible lifecycle for replacing one. A lost device can leave stale sessions and queued audio ambiguous, while a new device cannot safely inherit only the work it should. This would make hardware failure survivable without turning every replacement into a full reset.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** background for migration and reconciliation; realtime only for a spoken status or explicit confirmation
- **latency:** Immediate local revocation; new-device enrollment under two minutes; queued work reconciliation within one scheduler cycle.
- **cost:** Low model cost; dominant cost is a few signed enrollment, revocation, and queue-reconciliation records.
- **security:** Enrollment must require deliberate physical approval on the new pendant and owner confirmation on an already trusted Mac/browser surface. Revoke the old device epoch before migration, invalidate its sessions and pending delivery keys, and migrate opaque work references—not transcripts, credentials, or cached audio by default. Every migrated item needs an audit receipt and an expiry.
- **missing:** durable device identity and key-epoch registry at the relay; owner-visible lost/replaced-device revoke and enrollment flow; a migration map for unfinished jobs, briefing items, and ACKs with conflict handling; Mac/browser session binding to the active device epoch; firmware support for enrollment challenge, revocation epoch, and safe queue discard


## What it asked for

_Nothing._
## Its own summary

This round produced three owner-facing capabilities: crash-safe delegation recovery with leases and no duplicate side effects; a briefing that advances only on authenticated playback/acknowledgement rather than generation; and safe browser-login/approval handoffs that pause, explain, and resume after revalidation. The second is the strongest daily-use capability: it makes 'I heard it' a real state instead of a guess.

**Biggest unknown:** I still need the owner to decide the morning brief's acceptable fallback semantics (for example, whether generated-but-unheard items should remain queued until explicitly dismissed) and the eventual interruption/content policy. I will not invent those preferences. Engineering-wise, the missing pieces are the durable briefing manifest, relay job leases/requeue, and production wiring for browser blocked-task handoff.

