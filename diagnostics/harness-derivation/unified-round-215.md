# Harness derivation — unified — round 215

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Do this, but only use the minimum information needed, and forget the working context when you’re done.”"
- **useful because:** This would make the hive safe for real work rather than merely auditable: the relay would create a short-lived task capsule, the Mac and bound browser tab would receive only the fields needed for that task, and completion would return evidence without copying page contents or unrelated memories into durable history. It directly honors the owner's rule that extracted facts must be visible and deletable, while preventing secrets from spreading across surfaces.
- **path:** relay-realtime → mac-planner → browser-extension → mac-terminal → dashboard
- **model tier:** deterministic policy and redaction first; background model only to classify ambiguous fields, never to decide authorization
- **latency:** Under 150 ms for capsule creation and redaction; up to 2 s for a model-assisted ambiguity check, with the action held rather than guessed
- **cost:** Usually <$0.001 in deterministic processing; occasional small-model classification dominates, roughly $0.002–$0.01 per ambiguous task
- **security:** The capsule must be bound to job, target tab/app, expiry, and purpose; sensitive values should be replaced by capability handles where possible. Durable logs keep action receipts and hashes, not the capsule contents. Destructive actions still require the existing physical approval path. A bug could omit needed context and cause a failed action, which is safer than over-sharing.
- **missing:** A typed capsule/redaction contract spanning relay, Mac, and browser; A policy engine that distinguishes durable audit evidence from ephemeral working data; Dashboard controls to show and individually revoke active capsules; A secure handle mechanism for secrets that the executor can use without exposing them to the model

### "“We got cut off—what were we talking about, and continue from there.”"
- **useful because:** A dropped LTE/WebSocket session currently risks both a bad user experience and a false impression that the system remembers. This capability would preserve a bounded, encrypted conversation checkpoint at the relay, explicitly mark its freshness and last-heard turn, and let the pendant resume or discard it on the next deliberate press. It is continuity of the owner's conversation—not action replay—and works even though the pendant is not LTE-registered today by exercising the relay/Mac path in simulation and later on hardware.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** small background model to compress the last few turns into a checkpoint; realtime model only when the owner asks to continue
- **latency:** Checkpoint write under 300 ms after each completed turn; resume answer under 1.5 s after the next press
- **cost:** About $0.001–$0.01 per interrupted conversation, dominated by one short summarization; storage is bounded and expires automatically
- **security:** Never retain raw microphone PCM. The checkpoint must be end-to-end encrypted or tokenized, expire after a short TTL, be tied to the conversation and device counter, and be visible as a pending context item the owner can discard. It must not silently resume an action or browser task; action continuation requires a new plan and approval.
- **missing:** A relay checkpoint record with TTL, device/conversation binding, and explicit discarded/resumed state; A compact pendant event for 'resume context' versus 'start fresh'; A transcript-to-checkpoint redaction pass that excludes secrets and extracted facts unless explicitly requested; Dashboard and spoken disclosure of what checkpoint will be used

### "“Why did you do that, what exactly changed, and what did you rely on?”"
- **useful because:** Status says whether a job finished, but not a trustworthy, spoken explanation of the decision, the exact browser/Mac evidence, or what remains uncertain. This gives the owner a provenance answer assembled across the relay receipt, Mac state, bound browser result, and any pendant delivery receipt—without exposing unrelated tabs or dumping raw logs. It is especially valuable for actions that look successful but may not have taken effect in the outside world.
- **path:** relay-realtime → mac-planner → browser-extension → dashboard → pendant
- **model tier:** deterministic receipt join and evidence ranking; cheap background summarizer for the final one-sentence explanation; realtime only for the spoken answer
- **latency:** Receipt join under 250 ms; evidence fetch up to 2 s; speak a short answer first and offer details afterward
- **cost:** <$0.002 for normal deterministic joins; $0.005–$0.02 when summarization of several evidence candidates is needed
- **security:** Only query explicitly bound tabs/apps and the job's files. Redact secrets, page bodies, and unrelated history. The answer must distinguish observed evidence from inference and say 'unknown' when no receipt proves the external effect. Never turn this into an approval or automatic retry.
- **missing:** A typed provenance graph linking plan step, action receipt, browser command, external evidence, and pendant playback; A redacted evidence normalizer with confidence and freshness fields; An owner-facing dashboard view that expands the spoken summary into the underlying receipts; A policy for which evidence may leave the Mac and which stays local

### "“Who am I talking to right now, and what is this meeting about?”"
- **useful because:** The wearable can answer this without recording the room: correlate the Mac's active call application, current calendar event, and the bound browser tab or document, then speak a short identity/title answer. Today those surfaces are individually reachable but the owner cannot ask the pendant for one privacy-preserving live meeting context.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** deterministic Calendar/app/tab correlation; small model only to resolve conflicting titles or abbreviations
- **latency:** Under 700 ms for the first spoken answer; fall back to “I cannot establish this” rather than guessing
- **cost:** Near-zero when deterministic; <$0.002 only for ambiguous title normalization
- **security:** Read only the frontmost call metadata, calendar event, and explicitly bound tab title/URL—not microphone content, screen pixels, or unrelated contacts. Require confirmation before revealing sensitive attendee names aloud in public mode.
- **missing:** A typed live-meeting-context query across Calendar, active app, and browser tab; A conflict policy when calendar and call metadata disagree; A privacy mode that speaks title only or suppresses names; A short-lived context receipt so the answer is auditable without retaining page contents

### "“What changed on this page since I last looked?”"
- **useful because:** The browser can inspect a page now, but it cannot give the owner a bounded, trustworthy change summary tied to their previous view. This would store a redacted structural fingerprint and selected text anchors—not a full page copy—then speak only the meaningful changes when asked. It is useful for portals, shipment pages, project dashboards, and research pages without background scraping every tab.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → dashboard
- **model tier:** deterministic DOM/URL/anchor diff first; background model summarizes only the changed snippets
- **latency:** Fingerprint lookup under 300 ms; fresh inspection and summary under 2 s
- **cost:** <$0.001 for fingerprinting; $0.003–$0.02 when changed text needs summarization
- **security:** Require explicit tab binding and per-site opt-in. Store hashes and short redacted anchors with TTL, never credentials or full page bodies. Refuse pages whose content is too sensitive or whose identity cannot be established.
- **missing:** Per-tab opt-in change fingerprints and retention rules; A browser-side stable-content extractor; A redaction and sensitivity classifier before relay persistence; A spoken diff contract that reports uncertainty and page identity

### "“Before you send or upload anything, tell me exactly what will leave this Mac and where it will go.”"
- **useful because:** Today approval is tied to action risk, but the owner lacks a plain-language data-egress preview. This capability would enumerate the actual fields, files, URLs, recipients, and destination service for a planned browser/Mac/relay operation, then block until the owner approves when sensitive data is present. It protects against a safe-looking action whose real danger is disclosure rather than mutation.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** deterministic payload and destination inspection; small model only to phrase a human-readable summary
- **latency:** Preview under 500 ms for local actions, under 2 s when browser DOM or file manifests must be inspected
- **cost:** <$0.002 per preview; hashing and file classification dominate, not inference
- **security:** The preview itself must not leak the sensitive values it describes; show categories, sizes, and redacted examples. Bind it to an immutable plan digest and expiry, require the existing physical transaction latch for sensitive/off-machine egress, and record only hashes in audit history.
- **missing:** A pre-dispatch egress manifest for Mac, browser, and relay actions; Field-level sensitivity classification and destination allow/deny policy; Pendant rendering/speech for a compact manifest and a digest-bound approval; Executor enforcement that refuses a plan if its egress manifest changes


## What it asked for

_Nothing._
