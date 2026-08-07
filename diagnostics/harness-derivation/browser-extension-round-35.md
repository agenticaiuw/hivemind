# Harness derivation — browser-extension — round 35

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-extension live availability** — GET /browser/status currently reports Safari extension offline, no registered tab, and 2 pending browser commands; the granted browser_command_enqueue tool still returns an implementation error, so no page can be inspected or bootstrapped from this agent right now.
  - evidence: GET /browser/status -> online:false, home-chrome only with tabId:null/tabCount:null, pendingCommands:2; browser_command_enqueue(get_active_tab) -> tool granted but no implementation yet.

## Capabilities it proposed

### "Compare the offer, bill, or appointment details in my logged-in Safari account with current public information, and tell me whether anything looks unusual; prepare questions or a reply, but don't send it."
- **useful because:** The owner gets a genuinely private-versus-public comparison that no single node can do safely: Safari can see the authenticated offer, the relay can gather fresh public benchmarks while the Mac keeps the private facts, and the pendant can deliver a concise explanation. It can catch an overpriced renewal, an inconsistent fee, a changed policy, or a suspicious appointment detail without exposing the whole private page to a public search service.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Use a cheap background model for public collection, field normalization, and anomaly scoring; use the realtime tier only to clarify the owner's spoken goal or read the final brief aloud. Escalate to the stronger planner only when sources conflict or the comparison is ambiguous.
- **latency:** About 30–90 seconds for a normal comparison: authenticated extraction and public lookups can run in parallel; under 2 seconds for a spoken status update and under 10 seconds to read the final result.
- **cost:** Roughly $0.01–$0.08 per comparison, dominated by public-search/page extraction and one synthesis call; most normalization should be deterministic or on a cheaper model.
- **security:** Safari must send only explicitly selected structured fields or redacted excerpts to the Mac planner; the relay receives the public query and no account identifiers, names, addresses, or raw private page. Preserve source URLs and hashes locally. Ask before exposing a private field in a spoken room, and stop at a draft rather than sending or submitting anything.
- **missing:** A privacy-preserving split-task protocol that lets Safari emit a redacted structured fact set with provenance and lets the relay receive only a derived public query; Field-level sensitivity labels and a local join operation on the Mac so private values are compared locally to public results; A durable comparison artifact with citations, anomaly explanations, and a reviewable draft surfaced on the dashboard and pendant; Reliable browser command enqueue and an online Safari tab for authenticated extraction


## Changes it proposed to its own stack

### `browser-harness` — Add an active temporal-invalidation layer for browser action manifests. Before every click/type/select/submit-like mutation, the Safari extension returns a compact checkpoint containing device+tab/window identity, URL, DOM anchor/locator, normalized target-region hash, and current field value hash. The runner stores it with an expiry and, immediately before the next mutation, re-reads the target region; navigation, tab replacement, login-wall changes, locator drift, or value/hash mismatch yields a typed STALE_CHECKPOINT result with fresh evidence and a replan point. This is observability and automatic stale-action prevention, not a user approval gate; irreversible commands remain separately addressable under owner policy.
- **owner gets:** A sleeping/waking Safari, an auto-refresh, or a changed form will not cause the assistant to type into the wrong account or submit an outdated amount. Long browser tasks can recover by replanning from current evidence instead of silently acting on a page that only looks like the one it saw earlier.
- effort: Medium: extension protocol additions, DOM-region normalization/hash code, runner manifest state, stale-result handling, and integration tests for tab replacement, redirects, login walls, and dynamic fields.  ·  risk: False staleness on highly dynamic pages could pause useful work; use semantic regions and volatile-field exclusions, then return fresh evidence for retry. Hashes are not security proofs. Recovery is re-read/replan, never blind replay.
- cost: Negligible API cost (small hashes/metadata); modest local CPU and a second read before mutations. No new per-invocation model call unless replanning is needed.  ·  latency: Typically 100–500 ms for a local checkpoint read; one extra browser round trip before each mutation. Avoids expensive failed workflows and accidental wrong-page actions.
- security: Improves confidentiality/integrity by binding actions to the currently observed tab and region. Persist only hashes/locators and redact field values where possible; do not upload raw private page text unless already requested for the task.
- depends on: browser extension command enqueue endpoint must be implemented (currently stubbed); typed browser results and tab/session affinity already present; provenance-aware browser workbench (chg-e14fff33) should be extended rather than duplicated


## What it asked for

_Nothing._
## Its own summary

Discovered the live browser path is still unavailable: /browser/status reports Safari offline with no tab and 2 pending commands, and the granted enqueue wrapper is still an unimplemented stub. I informed faculty-action that typed results/idempotency exist, but active DOM/hash provenance and stale-tab invalidation do not. I proposed a new temporal-invalidation layer: checkpoint target-region hashes and tab/URL identity before mutations, return STALE_CHECKPOINT on drift, and re-read/replan without adding an approval gate. I recorded the live outage as a finding.

**Biggest unknown:** Whether the Safari extension will heartbeat and whether a real enqueue implementation will be deployed; until then I cannot verify authenticated page reads or test the proposed stale-checkpoint behavior.

