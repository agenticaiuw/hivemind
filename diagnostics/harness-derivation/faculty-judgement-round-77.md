# Harness derivation — faculty-judgement — round 77

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **owner-facing reliability gap** — The owner has repeatedly asked for Gmail, GitHub, calendar, browser page access, and status checks; the owner projection records multiple 'failed' outcomes without a cause or preserved retry context. A normalized cross-surface failure receipt is therefore a new, directly evidenced need rather than a speculative feature.
  - evidence: discover:owner lists repeated failed requests and no-command failures; existing established routes/tools expose separate health, browser status, Mac status, jobs, and receipts but no shared diagnosis/retry contract.

## Capabilities it proposed

### "When something I ask fails, tell me what actually blocked it, test the safe alternatives you can reach, and give me the smallest next step to fix it—without making me repeat the request."
- **useful because:** The owner's recent Gmail, GitHub, calendar, and browser requests repeatedly failed with little actionable explanation. This would turn silent failures into a useful diagnosis: distinguish missing login/session, bridge offline, Mac route unavailable, permission gate, malformed intent, or transient outage; try only reversible probes; and preserve the original goal for one-tap retry after repair. It uses the pendant's immediate conversational context, the relay's durable job/error records, authenticated browser status, and Mac's granted AppleScript surface together—none alone can explain the whole failure.
- **path:** pendant → relay → browser → mac-planner → dashboard
- **model tier:** background for classification and repair-plan generation; realtime only to speak the concise diagnosis and ask for any required confirmation
- **latency:** Under 2 seconds for a first spoken diagnosis from structured receipts; up to 10 seconds for parallel health probes. Never block the owner on a long investigation.
- **cost:** Usually <$0.01 per failure using structured rules and a small background model; realtime cost only for the spoken response. Dominant cost is retained error/context payload, capped to the failed intent and recent receipt.
- **security:** Never expose bearer tokens, cookies, page contents, or secret memory in diagnostics. Browser probes must be read-only and limited to session/status metadata; Mac probes use allowlisted AppleScript/status routes. Ask before changing account settings, reauthorizing, sending, deleting, or typing credentials. Clearly label inferred versus observed causes.
- **missing:** A normalized cross-surface failure receipt schema with cause class, observed evidence, safe probes attempted, and retry token.; A durable repair/retry record that keeps the original intent without retaining sensitive arguments.; A small health-probe orchestrator and owner-facing diagnosis card/audio item.; A route to invalidate a stale browser session or request owner-led reauthorization without handling credentials.

### "Before you call a scheduled brief or background task complete, check what sources it actually reached, tell me what was missing or stale, and offer to rerun only the missing parts."
- **useful because:** A green 'completed' status is not the same as a trustworthy brief: browser sessions can be disconnected, Mac permissions can block one source, or a job can finish with partial results. The owner needs to know whether 'calendar, mail, files' really covered all three, especially when they are not watching the run.
- **path:** relay → mac-planner → browser → pendant → dashboard
- **model tier:** background model for coverage reconciliation and concise explanation; realtime only when the owner asks for the result or a missing source needs a decision
- **latency:** Attach a provisional coverage result within 1 second of job completion; reconcile slow sources within 15 seconds and update the queue. No repeated full run unless explicitly requested.
- **cost:** <$0.01 per routine using structured source receipts; background model cost dominates only when reconciling conflicting or unstructured outputs. Storage is a small redacted manifest per run.
- **security:** Store source names, timestamps, and result hashes rather than private contents. Do not infer that an account was checked from a successful login alone. Never rerun mutations or access a new account without approval; identify stale/unauthorized sources explicitly.
- **missing:** A routine coverage manifest declaring required sources and freshness SLA.; Per-source start/end/permission/error receipts and a completion predicate (not just job status).; Partial-rerun support keyed to missing source, preserving the original routine snapshot.; A pendant/dashboard presentation that says complete, partial, stale, or blocked in plain language.

### "When I ask “did that actually happen?”, give me a plain-language answer separating attempted, accepted by the local app, completed by the remote service, and independently observed afterward—then tell me what remains uncertain and whether a safe retry exists."
- **useful because:** Today a successful local job receipt can be mistaken for a real-world result, while a failed command can leave the owner unsure whether anything changed. This gives the owner an honest postcondition, especially after link loss or partial browser/Mac execution, without making them inspect logs or repeat an action blindly.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** A cheap background model or deterministic reducer should classify structured lifecycle evidence; use the expensive realtime tier only to answer the owner immediately or resolve genuinely ambiguous evidence.
- **latency:** Return the first spoken state from existing receipts in under 2 seconds; perform independent observation asynchronously and update the owner within 15 seconds. Never delay a safe acknowledgement waiting for a slow remote check.
- **cost:** Usually under $0.01 per query; the dominant cost is a small amount of retained, redacted lifecycle metadata and occasional background reconciliation, not model inference.
- **security:** Persist hashes, timestamps, surface names, and redacted evidence references—not page contents, credentials, cookies, or secret memory. Independent observation must be read-only unless the owner explicitly approves a mutation. If evidence conflicts, say so rather than selecting the more convenient claim.
- **missing:** A typed lifecycle/postcondition schema shared by Mac actions, browser commands, and relay jobs.; An independent-observation adapter for each action class (for example, re-read the target page or app state without replaying the mutation).; A durable, redacted evidence bundle with expiry and a user-visible uncertainty explanation.; A safe retry evaluator that refuses non-idempotent retries unless the owner confirms.


## Changes it proposed to its own stack

### `integration` — Add a cross-surface Failure Receipt and Recovery Ladder. Every failed plan, execute, browser command, and relay job emits a normalized record: intent fingerprint (sensitive arguments redacted), stage, observed error, evidence references, confidence-ranked cause, safe probes attempted, and a short-lived retry token. A coordinator runs only read-only health probes in parallel (relay/job state, browser bridge/session status, Mac status/route health), deduplicates transient failures, maps the result to one owner-facing diagnosis, and preserves the original intent for explicit retry after repair. Expire raw evidence quickly and retain only the redacted diagnosis and receipt link.
- **owner gets:** Instead of hearing 'failed' and starting over, the owner gets 'Safari bridge is disconnected; nothing was changed; open the extension and say retry' or 'Calendar access succeeded but the requested event was ambiguous; choose between two items.' Their goal survives the interruption, while destructive work never auto-retries.
- effort: Medium: shared schema, receipt persistence, probe adapters, redaction tests, dashboard/audio rendering, and retry-token plumbing across existing routes.  ·  risk: A wrong cause could send the owner down an unnecessary repair path; show evidence and confidence and provide 'try again' rather than claiming certainty. Never auto-retry non-idempotent actions. If the relay dies, the original intent remains pending with an expiry and can be discarded.
- cost: Negligible API cost for structured classification; <$0.01 for uncommon background explanation. Small D1/R2 cost for redacted receipts; raw page/error evidence should be TTL-deleted.  ·  latency: Parallel probes add roughly 0.5–2 seconds; return an immediate provisional diagnosis and update later for slow jobs.
- security: Improves security by preventing blind repeated attempts and credential leakage. Redact cookies, tokens, email bodies, URLs with sensitive query strings, and secret-memory values before persistence; owner confirmation required for reauthorization or any mutation.
- depends on: The existing jobs/receipts and browser command IDs must expose machine-readable error codes and idempotency state.; A redaction utility shared by relay, Mac, and browser surfaces.; An owner-visible retry route that accepts only the short-lived token and re-plans from the original goal, not arbitrary stored credentials.


## What it asked for

### `t20-n326` (tool) — cross_surface_failure_diagnose
- why: The owner-facing agent needs one safe, read-only call that explains a failed intent across relay, Mac, and browser and returns a short-lived retry token. Existing status tools expose each surface separately and cannot correlate causes or preserve the original goal.

```json
{
  "type": "object",
  "required": [
    "intent_or_job_id"
  ],
  "properties": {
    "intent_or_job_id": {
      "type": "string",
      "description": "Original intent fingerprint, job ID, or command ID."
    },
    "include_probes": {
      "type": "boolean",
      "default": true,
      "description": "Run only read-only health/session probes."
    },
    "max_wait_ms": {
      "type": "integer",
      "minimum": 0,
      "maximum": 10000,
      "default": 2000
    },
    "retain_retry": {
      "type": "boolean",
      "default": true,
      "description": "Issue a short-lived retry token without retaining sensitive arguments."
    }
  }
}
```

## Its own summary

This round produced two new, evidenced gaps: (1) a cross-surface Failure Receipt and Recovery Ladder that explains why Gmail/browser/Mac requests failed, runs bounded read-only probes, preserves a redacted retry token, and prevents blind repetition; and (2) routine coverage integrity, so a scheduled brief is labeled complete/partial/stale/blocked based on the sources actually reached rather than a green job status. I recorded the owner's repeated unexplained failures as evidence, proposed both the owner capabilities and the integration change, and queued the precise cross_surface_failure_diagnose tool schema. What I still need is implementation of the shared redacted failure/coverage receipt contract, machine-readable per-source error and freshness receipts, and partial-rerun support. No new grant appeared in discover:granted this round; I am not re-requesting the already-denied Accessibility/TCC permissions.

**Biggest unknown:** Whether the existing job and pipeline records already contain enough per-source evidence to compute coverage, or whether adapters must be added at each routine's planner/executor boundary.

