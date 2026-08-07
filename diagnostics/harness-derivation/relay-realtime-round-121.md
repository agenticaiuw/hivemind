# Harness derivation — relay-realtime — round 121

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If I say “check that thing you sent to my Mac,” tell me the status right away, even if my Mac is asleep."
- **useful because:** This is a common pendant scenario: the owner is away and wants a quick update. It avoids waking the Mac or re-running work, and it prevents hallucinated success/failure by relying on recorded receipts.
- **path:** relay → mac-bridge
- **model tier:** realtime for the spoken request, then a cheap status lookup; no planner unless the status says new action is needed
- **latency:** Under 1 second for a cache hit; a couple seconds if it needs to fetch job receipts.
- **cost:** Low. One status lookup and possibly a receipt read; dominated by storage read cost.
- **security:** Must not reveal details from other users’ jobs (single-owner assumption helps but still validate ownership). Don’t fabricate status; speak the stored status verbatim.
- **missing:** A working relay_job_status implementation or equivalent relay-side job/receipt lookup route exposed to the relay surface

### "When I press the pendant and say “pin this,” save the last few seconds of our conversation as a project bookmark; when my Mac is next available, identify the document or browser page I was working in and append the bookmark there with a timestamp and link back to the audio/transcript."
- **useful because:** The owner can capture an idea or decision while away from the desk without stopping to open an app, then find it where work actually resumes. It combines the pendant’s physical presence, the relay’s live audio/session context, and Mac/browser awareness; neither the pendant nor Mac alone can provide this continuity.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Realtime only for the short spoken command and acknowledgment; a cheaper background model should trim/transcribe the buffered utterance, classify the destination, and format the bookmark after reconnect.
- **latency:** Acknowledge the pin locally/in the live turn within 500 ms; append it on reconnect within 10 seconds. If destination resolution is uncertain, put it in an inbox rather than blocking the voice interaction.
- **cost:** About $0.001–$0.01 per bookmark depending on audio transcription and summarization; storage and Mac sync dominate engineering cost, not inference.
- **security:** The audio/transcript and destination metadata leave the pendant for relay processing and may be written into private documents. Bind each bookmark to the owner’s authenticated session, encrypt it in transit and at rest, expose an audit trail, and never publish it to a page or document outside the owner’s active account.
- **missing:** A durable relay bookmark record with a monotonic cursor and replay after reconnect; A pendant command that retains a bounded recent-audio window and marks it without losing the live stream; A Mac/browser destination resolver that reports the active document or tab and an append-at-location operation; Idempotent delivery and a visible unfiled-bookmarks inbox for disconnected or ambiguous cases

### "Know when I’m busy before speaking: if my Mac or browser shows a meeting, presentation, call, or focused work session, keep non-urgent pendant replies silent and queue them; still surface urgent results immediately, and let me say “read my queued updates” later."
- **useful because:** A worn assistant should not embarrass or distract the owner during a meeting or concentration. This is not a permission gate on actions: it is cross-surface attention etiquette, using the Mac/browser’s actual state while the pendant remains the only device that can reach the owner away from the desk.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use deterministic signals first (active call app, presentation mode, browser meeting tab, focus mode). Use the cheaper background model only to classify ambiguous app titles and rank queued updates; reserve realtime for the owner’s spoken override.
- **latency:** Evaluate attention state in under 1 second when an event arrives; suppress or speak within 300 ms. Queue retrieval should begin speaking within 1 second.
- **cost:** Near-zero inference for explicit OS/browser signals; roughly $0.001 per ambiguous classification. The main cost is a reliable event stream and state reconciliation across reconnects.
- **security:** Active app, tab titles, and meeting indicators are sensitive. Send only coarse classifications to the relay by default, retain raw titles locally, encrypt queued content, and provide a dashboard purge/history control. The owner’s explicit “speak now” must override suppression.
- **missing:** A Mac/browser attention-state event feed rather than one-shot status reads; A relay attention policy and durable per-owner notification queue with urgency and expiry; A pendant-visible queued-state indicator and an offline-safe spoken override; A common event identity/cursor so a queued update cannot be spoken twice after reconnect

### "After you successfully do something for me, let me say “remember this as ‘weekly status’.” Next time I say that name, replay the same Mac/browser workflow with today’s values, showing me a short spoken preview of what it will touch before running it."
- **useful because:** The owner can turn a one-off voice delegation into a personal command without learning an automation language. The pendant supplies the name and intent, the Mac/browser provide the real authenticated workflow, and the relay preserves a reusable, inspectable recipe rather than forcing the owner to repeat details.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Realtime handles naming, disambiguation, and the brief preview. A cheaper background model extracts stable parameters from the completed action receipt and proposes a parameterized recipe; the Mac planner executes it when invoked.
- **latency:** Confirm recipe capture within 1 second. Resolve a named command and speak its preview within 2 seconds; execution may take normal Mac/browser job time with progress available.
- **cost:** Usually $0.002–$0.02 per new recipe for extraction and validation; invocation cost is the normal planner/browser action cost. Most effort is safe parameterization and testing against changed UI.
- **security:** Recipes may contain private URLs, document names, or authenticated actions. Encrypt them per owner, redact secrets and session tokens, display the concrete targets in the preview, and allow immediate disable/deletion. Do not silently broaden a recipe when the target changes.
- **missing:** A recipe store linked to action receipts, with versioning and parameter schemas; A planner step that distinguishes stable intent from accidental coordinates/text and can test a recipe read-only; A spoken preview/result contract and dashboard editor for named commands; A fallback path that reports drift and asks the owner to reteach instead of guessing

### "When I say “tell Alex I’ll be ten minutes late,” turn it into a message in the communication app I’m already signed into, use the right Alex and current conversation when unambiguous, and tell me whether it was drafted, sent, or failed when delivery is confirmed."
- **useful because:** While away from the Mac, the owner can handle time-sensitive human coordination naturally by voice. The pendant captures intent, the relay keeps the conversation responsive, and the authenticated browser/Mac session supplies the recipient and channel that the pendant cannot reach.
- **path:** pendant → relay → mac-planner → browser-extension → mac-vision → dashboard
- **model tier:** Realtime extracts recipient, message, urgency, and channel constraints and gives an immediate status. The cheaper planner/browser tier resolves the open conversation, performs the send, and returns a typed delivery receipt.
- **latency:** Acknowledge and start lookup within 1 second; return draft/send status within 5 seconds, with late delivery receipts queued for the next voice turn.
- **cost:** About $0.005–$0.03 per message depending on planning and browser use; authenticated session lookup and delivery verification dominate.
- **security:** Messages leave the pendant and are sent under the owner’s authenticated identity. Restrict destination selection to an exact open conversation or an explicitly resolved contact, redact message content from general logs, and retain a tamper-evident sent/draft receipt. Never claim sent until the app confirms it.
- **missing:** A typed cross-surface message intent and delivery-state protocol; A browser/Mac resolver for current conversation plus explicit ambiguity reporting; A durable delivery receipt that can be spoken later after LTE or Mac disconnects; An owner-controlled retention/redaction policy for message transcripts and receipts


## Changes it proposed to its own stack

### `model-routing` — Add a voice-session context contract that carries a small, persistent conversation state token (e.g., last job reference, last target surface, last known device status) across turns without resending full context, and make it available to all surfaces via a shared state lookup route.
- **owner gets:** The pendant can understand follow-ups like “that one” or “the last thing” without misrouting, and it reduces cost and latency by not re-sending large context every turn.
- effort: Medium to high. Needs a shared state store, state versioning, and clear privacy boundaries.  ·  risk: State drift or stale references could cause wrong actions. Mitigate with expirations, explicit invalidation, and showing a quick summary before acting on ambiguous references.
- cost: Medium upfront. Ongoing cost is small read/write operations per turn.  ·  latency: Improves latency for follow-ups by avoiding extra discovery and re-parsing.
- security: Medium. Conversation state may contain sensitive references; encrypt and restrict access per owner.
- depends on: A shared, low-latency state store accessible by relay and mac surfaces; A small schema for state keys and lifetimes


## What it asked for

_Nothing._
## Its own summary

Recorded four owner-facing proposals: voice project bookmarks that land in the active Mac/browser work, attention-aware silent queuing during meetings/focus, reusable named voice recipes, and authenticated voice messaging with typed delivery receipts. The common missing layer is durable, idempotent cross-surface event/receipt handling plus destination resolution—not another realtime model.

**Biggest unknown:** Whether any of these connective layers already exist privately on the relay but are absent from its published route inventory; I was instructed not to probe further this round.

