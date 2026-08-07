# Harness derivation — relay-realtime — round 65

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Remember this exactly, and when my Mac and browser are next available, carry it out across whichever app or logged-in tab is needed; tell me on the pendant when it is actually done, and if anything is ambiguous, ask me then.”"
- **useful because:** The pendant is the one surface the owner can use while away, while the Mac and authenticated browser are the only surfaces that can perform many real tasks. Today a spoken request cannot become a durable, context-preserving handoff that survives both surfaces being offline and distinguishes accepted, waiting, completed, and failed. This gives the owner a reliable ‘tell it once while walking, get a truthful completion later’ workflow rather than a lost utterance or a falsely optimistic reply.
- **path:** pendant → relay → mac-planner → browser-extension → mac-vision → dashboard
- **model tier:** Realtime relay only captures and clarifies the request; a cheaper background worker normalizes it and watches availability; mac-planner plans when the Mac returns; browser-extension executes against the owner’s already-authenticated tabs; mac-vision is used only when structured browser/Mac actions cannot complete; relay speaks the final status on the next pendant contact and dashboard shows the audit trail.
- **latency:** Acknowledge capture in under 1 second. Queueing is immediate. Start within 30 seconds of both required surfaces becoming available; completion can take minutes, but every spoken update must identify waiting versus completed rather than implying success.
- **cost:** Roughly $0.01–$0.08 per handoff depending on planner retries and vision fallback; the dominant cost is background planning/vision, not the short realtime acknowledgment. Durable state and availability polling add negligible per-request API cost but some Worker/storage usage.
- **security:** The request and execution receipts leave the pendant for relay storage and may include private app/tab context. Encrypt task payloads at rest, minimize projected secrets, bind each task to the owner’s device/session, and record the exact target surface and result. Reversible actions can proceed under owner policy; irreversible or externally communicative actions should be represented as pending and require an explicit spoken confirmation at execution time, not at capture time.
- **missing:** A durable handoff record with immutable lifecycle states (captured, clarified, waiting-for-Mac, waiting-for-browser, executing, completed, failed, expired) and resumable action cursor.; A Worker queue plus availability-triggered wake-up mechanism that survives process restarts and does not rely on a nonexistent scheduler.; A single correlation ID propagated from pendant audio through planner, browser/Mac commands, receipts, and spoken completion.; A reconnect notification path from relay to the pendant, including concise LED/audio semantics for queued, needs-input, and completed.; Conflict detection when the owner or another task changes the target app/tab/file between capture and execution, with a safe re-plan rather than stale actions.; A dashboard view and pendant commands for listing, editing, cancelling, retrying, or asking ‘what is waiting?’ without losing the original utterance.

### "“What is on my Mac right now?” or “Read the page I left open and tell me the important parts.”"
- **useful because:** The owner wears the pendant away from the desk and cannot see the Mac display. Today the relay can converse, but it cannot give a grounded, current visual state of the unattended Mac and authenticated browser as an audio answer. A one-shot, cited visual snapshot would let the owner check work state, a dialog, or a page without asking another person or falsely relying on stale text.
- **path:** pendant → relay → mac-vision → mac-planner → browser-extension → dashboard
- **model tier:** Mac-vision captures a single current screen or selected open-tab snapshot and extracts only visible text/structure; browser-extension supplies tab URL/title and DOM text where available; a background compact model produces a short evidence-linked brief; realtime relay handles the spoken question and reads the result. Do not use realtime vision unless the owner is actively waiting for a difficult visual interpretation.
- **latency:** Acknowledge immediately; return a basic tab/screen inventory in 2 seconds when the Mac is online, and a spoken summary in 5–10 seconds. If the Mac is offline or capture permissions are absent, say so explicitly and provide no inferred answer.
- **cost:** About $0.005–$0.04 per request for metadata/text extraction; $0.03–$0.15 when an image must be interpreted. The image/vision call dominates cost, so crop to the requested window and discard captures after the response unless the owner asks to retain one.
- **security:** Screens may expose passwords, private messages, health data, or work secrets. Require device-bound authentication, redact password fields and known secret-like regions before model submission, send only the requested window/tab, retain no image by default, and speak a warning when the result contains potentially sensitive content. This is read-only and should not control the Mac.
- **missing:** A read-only Mac snapshot endpoint with explicit window/tab targeting, freshness timestamp, permission-state reporting, and automatic secret-region redaction.; A browser bridge operation that returns current tab provenance plus bounded visible text, not arbitrary session cookies or hidden page data.; A mac-vision mode that can classify/describe a single snapshot without entering the disabled computer-use control loop.; A relay response schema carrying evidence references and freshness so spoken answers cannot be mistaken for current state when capture failed.; A pendant-friendly ‘repeat last snapshot’ and dashboard thumbnail/provenance view with automatic expiry.


## Changes it proposed to its own stack

### `model-routing` — Add a relay-first intent router that uses relay_route_intent to label the request, picks a target (mac-planner, browser-harness, or server_browser_actions), and records a job receipt. If a job is queued, use relay_job_status to report progress verbatim. Route to server-side browser for public pages when the Mac/browser extension is offline.
- **owner gets:** From the pendant, the owner can ask anything and the system chooses the right place to do it. They get fast acknowledgment, fewer failures, and consistent status updates.
- effort: Medium. Needs intent labels, target selection rules, and receipt persistence; no new permissions required if using existing tools.  ·  risk: Misrouting could cause the wrong surface to act. Mitigate with conservative fallbacks: status-only queries stay local, public browsing uses server browser, private sessions stay on the Mac browser harness.
- cost: Moderate. Most cost is downstream planning/execution; routing itself is cheap.  ·  latency: Improves perceived latency by avoiding unnecessary Mac round trips and by giving immediate status via relay_job_status.
- security: Keeps private pages on the owner’s devices; reduces data exfiltration risk. Requires careful classification to avoid sending sensitive URLs/content to server-side browsing.
- depends on: Reliable job receipts and durable status storage; Browser harness capability that can distinguish public vs authenticated/private contexts


## What it asked for

_Nothing._
