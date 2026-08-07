# Harness derivation — browser-extension — round 80

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser availability round 80** — Real Safari is not currently online: GET /browser/status reports only offline home-chrome, tabCount null, and 7 pending commands. However browser session storage retains three prior Safari sessions (default time.is and two form probes), so stale work exists and must not be replayed blindly.
  - evidence: GET /browser/status HTTP 200: online=false, devices=[home-chrome offline], pendingCommands=7; GET /browser/sessions HTTP 200: sessions default/probe-form2/probe-form with prior tab IDs and URLs.

## Capabilities it proposed

### "Explain what I'm looking at in Safari without sending the whole private page to the cloud, and if useful compare it with public information or my Mac files."
- **useful because:** The browser is the only node inside authenticated sessions, but raw page forwarding can expose passwords, health, financial, or work data. This gives the owner an on-demand explanation while keeping sensitive regions local and still allows useful cross-source comparison.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use a cheap local Mac extraction/redaction pass first; send only the selected text or redacted structured facts to the slower background model for comparison; use realtime only for the spoken follow-up.
- **latency:** 2–5 seconds for local extraction/redaction, then under 15 seconds for a sourced explanation; if Safari is offline, report that and retain no page payload.
- **cost:** Usually <$0.01 per request when the local pass suffices; up to $0.03–$0.08 when a redacted excerpt needs background-model comparison. Dominant cost is model tokens for the excerpt and sources.
- **security:** DOM text must be classified locally with password/token/payment/health markers and excluded before any cloud call. Keep raw DOM and screenshots on the Mac with short retention; show the owner exactly which excerpt/facts leave the device. Cross-source comparison must not silently combine identities, and browser mutations remain out of scope unless separately requested.
- **missing:** Local DOM classifier and redaction manifest in the browser bridge; A route for sending a redacted excerpt plus provenance to a background job; Pendant UI/audio response that cites the tab URL and omitted-sensitive-region count

### "When I’m on a logged-in website, check whether a suspicious message, payment request, or login prompt looks legitimate before I act on it."
- **useful because:** The pendant can hear concern, the browser can inspect the exact authenticated page and links, and the Mac/relay can compare domains, certificates, sender patterns, and public advisories. Today those nodes are separate; this prevents a rushed click or payment without requiring the owner to copy private context into chat.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Run deterministic local checks first (origin, redirect chain, domain age/reputation where available, form target, mixed content); use a cheap background model to summarize evidence; reserve realtime for the owner's spoken question and final concise risk explanation.
- **latency:** Local checks in 1–3 seconds; public reputation lookups and synthesis in 5–15 seconds. Never block on a slow source—return a provisional result with confidence and evidence.
- **cost:** <$0.01 for deterministic checks and cached reputation; roughly $0.02–$0.06 when model synthesis and several public lookups are needed. Network reputation APIs dominate variable cost.
- **security:** Do not transmit page text, cookies, or account identifiers. Send only origin, link targets, redacted sender/message features, and hashes of sensitive text. Treat this as advisory, never as proof; display reasons and uncertainty. It must not auto-click, submit, or change account settings.
- **missing:** Local browser inspection of link/form targets and redirect chains (not just rendered text); A small reputation/cache service with timestamped evidence; A pendant response format for risk level, reasons, and a safe next step

### "Before reading a logged-in site, tell me which account, workspace, and browser profile is active; then read only that identity’s relevant items and label every result with its account."
- **useful because:** The owner has asked to read Gmail, GitHub, and Calendar, but a browser can silently be signed into the wrong personal/work account or organization. This prevents cross-account confusion and makes private-page results trustworthy without requiring the owner to inspect Safari manually.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use deterministic browser/profile/account identity extraction locally on the Mac; use a low-cost background model only to normalize workspace names and classify relevance; use realtime for the short spoken identity-and-results response.
- **latency:** Identity check in 1–3 seconds and a concise readout within 10 seconds for an already-open page. If identity cannot be established, return an explicit unknown state rather than guessing.
- **cost:** Typically under $0.01 per request; model cost is limited to small metadata and item summaries, not full page contents. Browser extraction and local caching dominate implementation complexity, not API spend.
- **security:** Never transmit cookies, tokens, full account identifiers, or unrelated page content. Store only a salted account/workspace fingerprint and display-safe label locally with a short TTL. If multiple identities are present, enumerate them and stop before reading until the owner chooses one; this is an identity-selection safeguard, not a destructive-action approval gate.
- **missing:** Browser-bridge extraction of account/profile/workspace identity signals with site-specific adapters; A local identity registry mapping stable fingerprints to owner-chosen labels such as Work Gmail or Personal GitHub; Result envelopes carrying identity provenance through Mac and relay to the pendant

### "If I say “lock down the browser,” immediately stop all browser work, cancel anything queued, close or freeze the AI-controlled tabs, and tell me what data was retained or discarded."
- **useful because:** The owner wears the pendant continuously but may not be near the Mac. A physical/voice emergency control gives them a fast way to cut off AI access to logged-in sessions, especially when Safari is offline with commands waiting to reconnect.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** No generative model is needed for the security action; use a deterministic relay command and a concise realtime acknowledgement. A slower background job may produce the retention report afterward.
- **latency:** Relay acknowledgment under 1 second; Mac/extension cancellation and tab freeze within 5 seconds when reachable. If a node is offline, record the revocation durably and enforce it before any reconnect dispatch.
- **cost:** Near-zero model cost; small durable-state and audit-log storage cost per revocation.
- **security:** This must be an unconditional emergency stop, separate from ordinary action approval. Revoke browser command leases, invalidate session bindings, clear raw page caches and screenshots according to retention policy, and emit an auditable receipt. It must not delete the owner’s normal Safari data or sign them out of unrelated sites without explicit separate configuration.
- **missing:** A relay-wide browser revocation token checked by every dispatcher and extension poll; Pendant trigger mapping for a spoken phrase and/or dedicated button gesture; Mac-side purge/freeze operation for browser artifacts and an owner-readable retention receipt


## Changes it proposed to its own stack

### `browser-harness` — Add browser-command freshness leases and a reconnect quarantine. Every queued browser command gets createdAt, expiresAt, tab/session fingerprint, and an owner-visible intent summary. If Safari is offline past the lease, mark it stale instead of dispatching it when the extension reconnects; retain the result as cancelled and provide one explicit resume action that revalidates the current tab before enqueueing a new command. Surface and safely drain the seven currently pending commands rather than replaying them blindly.
- **owner gets:** If the owner closes Safari or walks away, an old click/type/navigate must not happen unexpectedly hours later. On return they can resume exactly the still-relevant task, with the current page checked first.
- effort: Medium: queue schema and worker changes, reconnect tests, dashboard/pedant status copy, and a migration for existing pending commands.  ·  risk: A legitimate long-running job could expire and require resume; recovery is explicit resume with a new lease. Existing commands need a one-time migration to conservative short leases and cancellation receipts.
- cost: Negligible API cost; small D1/storage increase for lease metadata and cancellation receipts.  ·  latency: No added latency for online commands; reconnect adds a quick session/tab validation before resume.
- security: Improves safety by preventing stale authenticated actions from replaying after session/page changes. Does not add an approval gate or reduce owner access.
- depends on: A working Safari heartbeat/reconnect path (currently /browser/status reports offline); Durable browser job runner chg-16bc5dee; Typed browser receipts and request IDs chg-14accc01 / chg-5fc73ce3

### `integration` — Add a browser-availability watchdog spanning the Mac bridge and relay: when a browser request arrives and /browser/status is offline or has no live tab, classify the failure, ask the Mac bridge to bring Safari/its extension to the foreground (or open a neutral Start Page), then re-check the heartbeat once. If still unavailable, return a one-sentence spoken diagnosis with the exact recovery instruction instead of queuing more commands. Keep authenticated URLs and page content out of diagnostics.
- **owner gets:** The owner repeatedly asked to read Gmail, GitHub, Calendar, and browser pages but received generic failures. This turns a silent offline extension into either a self-recovered browser session or an actionable answer, without replaying stale private actions.
- effort: Small-to-medium: status preflight in browser dispatch, Mac bridge foreground/open-Safari action, one retry state machine, and concise error mapping.  ·  risk: Safari may be intentionally closed or the owner may be presenting another app; recovery only opens a neutral page and never navigates to an account automatically. If bridge is unavailable, fail fast and preserve the pending request for explicit retry.
- cost: No model cost; one extra heartbeat and at most one Mac action per failed browser request.  ·  latency: Adds up to ~2 seconds only when status is unhealthy; healthy requests are unchanged.
- security: Safer than blind queueing: no page navigation or credential interaction during recovery, and diagnostics reveal only availability, not URLs or content.
- depends on: A reliable real Safari extension heartbeat (currently live status is offline); Mac bridge open_app/open_url action; Browser command queue with stale-command handling


## What it asked for

_Nothing._
