# Harness derivation — unified — round 28

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **fleet-recovery-gap** — Live Mac status is not ready: browser extension offline with 2 pending commands, Accessibility untrusted, Screen Recording denied, while relay and Mac bridge are online. Browser navigate jobs waited about 45 seconds before failing. Existing receipts record failure but do not repair or resume the originating job.
  - evidence: GET /ops/status and GET /browser/status at 2026-08-07T09:53Z; GET /jobs shows browser_navigate failures of 45334–45373 ms with reason extension offline.

## Capabilities it proposed

### "“Fix whatever is stopping you, then try that again.”"
- **useful because:** Today a request can fail after 45 seconds because the browser extension is offline, while the Mac also reports missing Accessibility/Screen Recording permissions. The owner should not have to understand which surface is broken or manually repair it. The relay can diagnose the fleet, the Mac can perform only safe repair steps, the browser can reattach its session, and the pendant can explain progress and ask for the one permission it cannot grant.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use a cheap background classifier/rule engine for health diagnosis and repair selection; reserve realtime only for the spoken interaction and final concise explanation.
- **latency:** Diagnose in under 2 seconds; safe repairs in under 15 seconds; never spend another 45-second browser timeout. If a human permission is needed, speak it immediately and resume automatically after the permission change.
- **cost:** Usually <$0.01 per invocation; dominated by relay/database writes and optional one realtime turn, not diagnosis.
- **security:** Only allow an explicit allowlist of repairs: wake/launch the bridge, restart its polling process, re-open the selected browser, clear a stale command lease, and open (not manipulate) the relevant macOS permission pane. Never weaken security settings or infer credentials. Require spoken/button confirmation before opening a permission workflow or retrying an irreversible action. Store a short redacted repair receipt, including pre/post health evidence; no page contents leave the device.
- **missing:** Fleet health schema with typed failure causes and freshness; Idempotent browser-bridge reconnect/lease-reset endpoint; Mac repair intents for launching the bridge and opening exact System Settings permission panes; A retry policy that links the repaired request to its original job and refuses duplicate side effects; Pendant-visible progress and final repair receipt API

### "“Keep this completely private: use my Mac and logged-in browser, but do not send the conversation or page contents to the cloud.”"
- **useful because:** The owner should be able to use the hive for sensitive mail, health, finances, and private webpages without choosing between usefulness and cloud exposure. A single spoken privacy mode would make the relay a coordinator, the Mac the local planner/executor, the browser the credential boundary, and the pendant a visible/audible indicator of where data is allowed to travel. If the local path is unavailable, it should hold the request rather than silently downgrade to cloud processing.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use a small local Mac model or deterministic planner for routing and extraction; use no realtime/cloud model for content in private mode. Realtime may handle only a minimal control acknowledgment after redaction, or remain entirely local if the owner chooses strict mode.
- **latency:** Acknowledge the mode change on the pendant in under 500 ms; local planning should begin within 3 seconds. If the Mac/browser is unavailable, explain and queue within 2 seconds rather than timing out.
- **cost:** Near-zero API cost in strict mode; dominated by local Mac compute and encrypted local storage. Optional cloud health metadata should be a few cents per month, never content-bearing.
- **security:** The relay must enforce a cryptographic routing/policy token, not trust model instructions. Browser cookies, DOM text, audio, transcripts, screenshots, and action arguments stay on the Mac/browser path. Dashboard and pendant receipts expose only redacted metadata. Make mode sticky until explicitly ended, show a privacy LED/audio cue, expire queued content, and require confirmation before any operation that would cross the boundary.
- **missing:** End-to-end privacy policy enforcement at relay ingress/egress; Local Mac planner/extractor with an explicit no-upload execution mode; Browser bridge result channel that stays local and supports encrypted local evidence capsules; Pendant privacy-mode state, clear indicator, and offline queue encryption; A policy-aware receipt/audit view proving which surfaces saw each datum


## Changes it proposed to its own stack

### `integration` — Add a fleet-wide self-healing transaction coordinator. Before dispatch, each job obtains short-lived health leases from relay, Mac bridge, and browser bridge. A typed failure (offline, stale poller, missing permission, expired session) triggers at most one idempotent repair intent, then revalidates the lease and resumes the same job step with its original idempotency key. Hard timeouts become immediate actionable failures; every repair and resume is appended to one owner-readable receipt and pushed to the pendant.
- **owner gets:** A spoken request either completes or quickly tells the owner exactly what they need to do; it no longer silently burns a minute and leaves them wondering whether to repeat the request. If the problem is repairable, work continues without re-explaining the task, and retries cannot double-submit.
- effort: Medium-high: shared health/failure taxonomy, relay coordinator, Mac bridge repair intents, browser polling handshake, receipt linkage, and pendant event rendering.  ·  risk: A repair could restart a bridge during another job or cause an unsafe retry. Use per-surface leases, one repair per incident, idempotency keys, and stop on unknown postcondition. Recover by leaving the original job paused with the exact last verified step and a manual resume action.
- cost: Small relay D1 writes and a few health probes; <$0.01 typical run. Engineering cost is mostly coordinator and bridge protocol work.  ·  latency: Adds <2 seconds for healthy preflight; materially reduces failed browser waits from ~45 seconds to a fast (<2 second) diagnosis.
- security: Improves security by never changing permissions automatically; permission panes are opened only with confirmation. Health receipts must redact URLs, tab titles, tokens, and page text.
- depends on: Typed fleet health schema; Idempotent operation manifest/step IDs and independent postcondition verification; Mac bridge safe repair intents; Browser bridge reconnect handshake; Pendant progress/receipt delivery

### `relay` — Introduce a cryptographically enforced data-boundary token carried with every request, artifact, and action step. The token declares allowed surfaces (pendant, relay metadata, Mac, browser), retention, and whether content may leave the local path. Relay ingress rejects disallowed payloads before model invocation; Mac/browser agents attach signed, redacted evidence receipts; the pendant displays the active boundary and refuses to upload queued private audio until policy permits. Include a local append-only audit ledger and a one-command purge for all artifacts tied to the token.
- **owner gets:** The owner can ask for help with genuinely sensitive material and receive useful results without having to trust that every component will remember a conversational promise not to upload it. They get a clear answer about where their data went and can erase the complete local trail afterward.
- effort: High: policy-token format and key management, relay enforcement at every route, local planner and browser evidence signing, encrypted pendant queue, audit UI, and negative tests proving forbidden routing is blocked.  ·  risk: A policy bug could leak private content or make work silently unavailable. Default-deny unknown tokens, fail closed when enforcement cannot be proven, bind tokens to job/step IDs, rotate keys, and test with synthetic secrets before enabling real accounts. Recovery is to discard the job and purge all artifacts rather than retrying on a broader route.
- cost: Minimal per-request compute and storage overhead; modest encrypted local ledger growth. No cloud model spend in strict local mode; engineering cost is substantial.  ·  latency: Adds tens of milliseconds for token checks and signing; local-only planning may be slower than realtime cloud responses but avoids network waits and retries.
- security: Strongly improves confidentiality and auditability, but introduces key-management and policy-configuration risk. The boundary must be enforced below the model prompt layer and audited independently.
- depends on: Local Mac planner/extractor that can operate without cloud content; Browser bridge local evidence/result transport; Pendant encrypted offline storage and privacy-state indicator; Relay route middleware covering audio, transcription, jobs, browser results, and logs


## What it asked for

### `t7-wwdv` (tool) — fleet_health_and_repair
- why: The current system exposes raw /ops/status but no typed, callable health diagnosis or safe repair operation. This capability is needed to turn offline-browser and missing-permission failures into fast, resumable owner-facing recovery instead of repeated timeouts.

```json
{
  "type": "object",
  "required": [
    "operation"
  ],
  "properties": {
    "operation": {
      "type": "string",
      "enum": [
        "diagnose",
        "repair",
        "revalidate"
      ]
    },
    "jobId": {
      "type": "string"
    },
    "surfaces": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": [
          "relay",
          "mac-bridge",
          "browser",
          "pendant"
        ]
      }
    },
    "repairKind": {
      "type": "string",
      "enum": [
        "wake_browser_bridge",
        "restart_browser_polling",
        "clear_stale_command_lease",
        "open_accessibility_settings",
        "open_screen_recording_settings"
      ]
    },
    "idempotencyKey": {
      "type": "string"
    },
    "confirmationToken": {
      "type": "string"
    }
  }
}
```

## Its own summary

Discovered a live, actionable fleet gap: relay and Mac bridge are online, but browser is offline with two queued commands; Accessibility and Screen Recording are also missing. Browser jobs currently wait ~45 seconds before failing. I proposed a new cross-surface capability, “Fix whatever is stopping you, then try that again,” plus a fleet self-healing transaction coordinator that diagnoses typed failures, performs one safe idempotent repair, revalidates, and resumes the original step without duplicate side effects. I also recorded the live evidence and queued a fleet_health_and_repair tool request.

**Biggest unknown:** Whether the browser bridge can expose a safe reconnect/polling handshake and whether the Mac host can launch it/open exact permission panes through currently available automation; the orchestrator still needs to implement the typed health schema, repair intents, and original-job resume linkage.

