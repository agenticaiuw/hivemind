# Harness derivation — faculty-action — round 262

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **current device reachability** — Live device inventory shows home-macbook-bridge online and Safari online, but nrf9160-pendant offline. Any pendant behavior proposed this round must be firmware work or bench-tested later; it cannot be claimed as live LTE execution now.
  - evidence: discover(devices) in round 262: home-macbook-bridge online, Safari on MacIntel online, nrf9160-pendant offline.

## Capabilities it proposed

### "“Start this job now, and if the Mac or browser drops out, continue from the last step you can prove—then tell me exactly where it stopped.”"
- **useful because:** Today a multi-step action can be handed off or retried, but a link loss in the middle can leave the owner unsure which steps ran. This gives the owner one honest answer: completed checkpoints, the first unknown step, and a safe resume rather than duplicate submissions. The pendant can acknowledge completion or an unresolved stop without exposing page contents.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** background for checkpoint bookkeeping and resume planning; realtime only for the owner's brief spoken request
- **latency:** Acknowledge in under 1 s; checkpoint receipt within 5 s of each step; resume when a surface returns, without blocking the voice conversation
- **cost:** Low per step: one small relay receipt plus one verifier call; model cost is dominated by replanning only after an interruption, not by every checkpoint
- **security:** Never replay a non-idempotent step solely because its receipt is missing. Require postcondition verification or explicit owner approval before retrying. Store hashes and step summaries by default; page contents and secrets remain on Mac/browser. Expire abandoned jobs.
- **missing:** A first-class resumable workflow record with idempotency keys and dependency edges; Executor receipts that carry a stable step/attempt correlation ID; A policy for which action classes may auto-resume versus stage for physical approval

### "“Change this setting on every logged-in site, show me one private before/after summary, and only submit sites whose intended fields all match.”"
- **useful because:** The owner can ask for a broad change once instead of manually repeating it, while avoiding the dangerous failure mode where one site accepts a different value or a stale form. The system reports per-site matched/blocked/unknown and the pendant approves the bounded batch—not a blind global click.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** background for site-by-site planning and normalization; realtime only to explain the batch and collect a deliberate approval
- **latency:** Preview in under 10 s for up to five open sites; each site gets its own verification before the next submission
- **cost:** Moderate: browser snapshots and one verification per site; planning tokens scale with number of distinct forms, while the relay stores only compact hashes
- **security:** Never send credentials, full field values, or page text to the relay. Keep a per-site encrypted local receipt containing field locators, value hashes, URL/origin, and postcondition. Require physical approval for every submit batch, reject cross-origin surprises, and stop on MFA/payment/destructive fields.
- **missing:** A secret-preserving browser batch planner that understands equivalent fields across origins; A browser transaction primitive that can stage multiple sites but commits only the verified subset; A dashboard view for per-origin matched/blocked/unknown results

### "“If I’m walking, driving, or otherwise in motion, don’t make me look at a screen—summarize urgent results aloud and hold anything that needs visual confirmation until I’m still.”"
- **useful because:** A wearable assistant should adapt its action surface to the owner's physical context. This prevents a browser or phone task from silently demanding unsafe visual attention, while still allowing urgent, reversible spoken actions and preserving the pending job for later. The pendant's owned IMU can provide a local low-latency gate even when LTE is unavailable; Mac/browser state supplies the task risk, and the relay coordinates deferral.
- **path:** pendant → relay → mac-planner → browser → ios → dashboard
- **model tier:** Firmware motion classifier and deterministic policy locally; background model only classifies task risk and writes a short spoken summary. No realtime reasoning is needed for every sensor sample.
- **latency:** Local motion state under 200 ms; haptic/voice deferral immediately; resume evaluation within 2 s after stillness is stable
- **cost:** Very low inference cost after firmware integration; occasional background summary generation, with no audio or raw IMU uploaded by default
- **security:** Raw accelerometer/gyro stays on the pendant and is reduced to coarse states (still, walking-like, vehicle-like, unknown). Never claim to detect driving reliably; unknown must defer screen-dependent actions. Emergency and owner-approved reversible actions remain policy-controlled. Do not auto-resume a consequential action merely because motion stops.
- **missing:** Firmware integration of the existing LSM6DSOX on i2c2 and a conservative motion-state classifier; A relay policy field that marks each action as screen-free, screen-needed, or high-risk; A resume gate that requires fresh stillness plus the existing postcondition verifier

### "“Give this website permission to do only this one thing until 5 PM, without giving it my password, and revoke it if the result differs from what I asked.”"
- **useful because:** The owner can delegate a narrowly bounded action to a logged-in browser session without handing credentials to the relay or granting an effectively permanent session. This is different from approving a single click: it is a least-privilege, expiring capability spanning the pendant’s physical consent, relay policy, and browser enforcement, with automatic revocation on an unexpected result.
- **path:** pendant → relay → browser → mac-planner → dashboard
- **model tier:** Background model translates the spoken constraint into a structured capability policy; deterministic relay/browser code enforces it. Realtime is only needed to explain the policy or report a violation.
- **latency:** Policy preview under 3 seconds; browser enforcement adds less than 100 ms per guarded command; violation and revocation haptic within 1 second
- **cost:** Low after setup: one planning call per delegation and compact signed policy checks thereafter
- **security:** The browser must enforce origin, action type, field constraints, expiry, and nonce—not merely trust model text. Never transmit credentials or unrestricted page contents. Default deny on ambiguous selectors, redirects, MFA, payment, or a postcondition mismatch. The pendant signs consent over a digest, not the secret policy payload.
- **missing:** A browser-enforced signed capability-token protocol; A policy compiler from owner language to typed origin/action/field constraints; Revocation propagation from relay to an already-open browser session; A compact dashboard showing active delegations and expiry

### "“Rehearse this across my Mac, browser, and iPhone, show me every intended change and side effect, but do not write anything until I explicitly approve the final diff.”"
- **useful because:** The owner can safely understand a complex action before committing it: which records, files, messages, or settings would change, which steps are blocked, and which assumptions are uncertain. A single final approval covers a concrete diff rather than an opaque plan, while each surface remains able to refuse unsupported or destructive operations.
- **path:** pendant → relay → mac-planner → browser → ios → dashboard
- **model tier:** Background model builds and explains the dry-run; deterministic surface adapters produce change sets. Realtime only summarizes the final diff and receives approval.
- **latency:** Initial rehearsal within 15 seconds for a three-surface task; incremental diffs within 3 seconds; no mutation before approval
- **cost:** Moderate: each adapter needs a read-only preview and the model summarizes potentially large diffs; cost is bounded by changed-item count, with hashes for unchanged data
- **security:** Preview must be side-effect-free, including no implicit drafts, navigation submissions, or clipboard writes. Clearly label inferred versus observed effects. Redact secrets and sensitive values, require fresh verification before commit, and invalidate the approval if any underlying state changes.
- **missing:** A dry-run contract for Mac, browser, and iOS adapters; A normalized change-set format with observed/inferred/unknown provenance; A state-version or snapshot mechanism that makes the final approval bind to the preview; A dashboard diff viewer usable from the pendant’s short spoken interaction


## Changes it proposed to its own stack

### `hardware` — Add a low-power secure element (for example, an I2C device with hardware-backed key generation, monotonic counters, and anti-rollback storage) to the pendant revision, and bind its attestation key to the relay during provisioning. Keep the private key non-exportable; use the existing button path only to authorize signing digests.
- **owner gets:** The owner gets a physical pendant that can prove “I approved this exact action” even if the Mac, relay, or browser is compromised. That makes bounded website delegation, high-risk approvals, and later audit receipts meaningfully trustworthy instead of relying on firmware-held secrets.
- effort: Hardware respin, secure-element driver and provisioning ceremony, relay/browser signature verification, key rotation and recovery UX; several engineering weeks plus a board revision.  ·  risk: A lost or bricked pendant requires recovery without silently weakening the trust boundary. Bad provisioning could permanently strand the device. Roll out in audit-only mode first, retain a clearly disclosed recovery path, and reject unsigned legacy approvals rather than silently accepting them.
- cost: Roughly $1–4 in component cost at prototype quantities, negligible power while idle and a few mA during signing; engineering and provisioning dominate.  ·  latency: Typically tens of milliseconds per signature, acceptable for approval and delegation setup, not for every audio packet.
- security: Substantially improves resistance to extracted firmware keys and forged approvals; introduces key custody, replacement, revocation, and supply-chain responsibilities.
- depends on: A typed signed capability-token protocol; A relay key registry and revocation path; A physical approval UX that hashes the exact human-readable action summary; The owner choosing a recovery policy for a lost pendant


## What it asked for

_Nothing._
