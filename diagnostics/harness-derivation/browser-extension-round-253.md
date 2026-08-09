# Harness derivation — browser-extension — round 253

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Turn the event on this page into a reminder for me.”"
- **useful because:** The browser can see authenticated event/ticket pages that Calendar cannot. From the pendant, the system would read only the active page, extract title/time/location, show the proposed reminder aloud, and—after the owner's ordinary approval—create it on the Mac, preserving the page URL as provenance rather than copying page text. This is a genuinely cross-surface handoff: worn request, private Safari session, Mac calendar mutation, spoken confirmation.
- **path:** pendant → browser → mac-bridge → relay
- **model tier:** background for extraction and field normalization; realtime only for the short spoken confirmation
- **latency:** 3–8 seconds to extract and present the draft; reminder creation under 2 seconds after approval
- **cost:** About $0.01–$0.04 per invocation; browser and calendar operations dominate latency, not model tokens
- **security:** The active tab may contain private details. Send only title, time, timezone, location, and URL to the planner; do not persist page text. Require the owner to approve the normalized reminder before creating it, and retain an undoable job receipt.
- **missing:** A browser action recipe that returns structured event candidates (microdata/ARIA/date-time parsing) rather than only page text; A relay intent that binds an active Safari tab to a Mac create_reminder action; A compact owner approval/rejection interaction from the pendant for the displayed fields

### "“Take the address on this private page and open it in Maps, then tell me how long it will take.”"
- **useful because:** Safari can read an authenticated reservation, invitation, or order page while the Mac agent cannot access that session. The browser extracts only the address; the Mac opens the native Maps route and reads the ETA back through the pendant. It avoids manually copying sensitive addresses and works from pages no public search can reproduce.
- **path:** pendant → browser → mac-bridge → relay
- **model tier:** background model for address extraction and normalization; realtime only for the spoken request and ETA
- **latency:** 5–12 seconds including Maps route calculation
- **cost:** $0.01–$0.03 per request; Maps startup and browser round trip dominate
- **security:** Addresses are sensitive location data: keep the extracted value ephemeral, do not write it to browser findings, and require an explicit spoken confirmation if the destination is not confidently identified. Send only normalized address to the Mac Maps action.
- **missing:** Structured address extraction with confidence and provenance from browser_read_page; A Mac Maps route action that returns duration rather than merely opening a URL; A cross-surface ephemeral secret/location handoff with automatic deletion

### "“Put the boarding pass or access QR code from this page onto my iPhone.”"
- **useful because:** Today the owner must manually scan a code from Safari with the phone or shuttle it through screenshots and messages. The browser session can see the authenticated page, the Mac can inspect the rendered QR, and iPhone Mirroring can open the decoded destination or add the pass to Wallet. The pendant provides the hands-free command and speaks the decoded destination before the phone is changed.
- **path:** pendant → browser → mac-bridge → iOS → relay
- **model tier:** Background vision/QR decoding for the page image; realtime only for the short spoken confirmation. No expensive model is needed when a standards-compliant QR decoder succeeds.
- **latency:** 5–15 seconds to capture and decode; under 10 seconds to open or stage the pass on the iPhone
- **cost:** Usually under $0.01 per invocation; image transfer and iPhone Mirroring latency dominate
- **security:** QR codes can contain bearer tickets, login links, or payment URLs. Keep the decoded payload ephemeral, show its domain/type aloud, never persist the image or raw token, and stop before adding a pass or opening an external destination unless the owner explicitly confirms.
- **missing:** Safari extension action to capture the rendered QR region or page screenshot with form/password redaction; Local QR decoding and payload classification on the Mac; An iOS Mirroring action that stages a decoded pass/link in the appropriate app and returns a receipt; A short-lived browser-to-iPhone secret handoff that excludes raw payloads from normal logs

### "“Use the verification code shown in this private Safari page in the app that is open on my iPhone.”"
- **useful because:** Many sign-ins and device-pairing flows split a one-time code across a browser and phone. Today the owner has to read and retype it while switching attention between devices. The browser can extract the code, the Mac can target the real mirrored iPhone field, and the pendant can confirm the destination without exposing the code in conversation history.
- **path:** pendant → browser → mac-bridge → iOS → relay
- **model tier:** Small background extractor with strict OTP pattern recognition; realtime only for confirmation and completion status
- **latency:** 3–8 seconds
- **cost:** Less than $0.01 per invocation; the dominant cost is the browser/iPhone round trip
- **security:** Treat the value as a one-time secret: never speak or persist it, bind it to the active tab and focused iPhone field, enforce a short TTL, and abort if the page origin or focused app changes. The owner should confirm only the destination app, not repeat the secret.
- **missing:** A browser result mode that extracts an OTP without returning it to model transcript or durable evidence; A focused-field identity/readback action in iPhone Mirroring; A secure Mac-local secret channel from Safari to the mirrored iPhone input; Expiry and failure cleanup for the in-flight code

### "“Start the timers from this recipe and tell me when each one is done.”"
- **useful because:** A recipe in an authenticated browser tab can contain several implicit timers that the Mac or browser cannot reliably keep audible while the owner moves around. Safari would extract named durations, the pendant would run compact offline timers and announce/LED-alert completion, and the relay would reconcile results when the link returns. This makes the wearable useful in the kitchen rather than merely a remote speaker.
- **path:** pendant → browser → relay → mac-bridge
- **model tier:** Background extraction of duration/name pairs; no realtime model after the timers are armed
- **latency:** Under 10 seconds to present the timer list; alerts fire locally at the requested times even with no network
- **cost:** A few cents at most for extraction; timer execution is local and free
- **security:** Persist only timer names, durations, and source URL—not recipe text. Make timers cancellable and show the complete list before arming. A stale page should not silently create a timer; include extraction timestamp and confidence.
- **missing:** A browser structured extraction recipe for named durations; A multi-timer scheduler and completion event on the pendant; Relay reconciliation for offline completion events and duplicate suppression; A pendant interaction for canceling or listing active timers


## Changes it proposed to its own stack

### `integration` — Build a one-shot private datum handoff primitive between Safari and the Mac agent. A browser action may emit exactly one typed value (address, date, account reference, tracking number, or event title), tagged with source URL, confidence, recipient action, and a 60-second expiry; the relay binds it to one pending Mac action, redacts it from generic logs, and destroys it after success or timeout. The pendant can request the handoff and receive only a confirmation/result, never the raw value unless asked.
- **owner gets:** The owner can say “use the address on this page,” “track the package shown here,” or “put that date in my calendar” without copying private text through chat, clipboard, or screenshots. It makes the browser’s unique login reach useful to every other surface while sharply reducing accidental leakage.
- effort: Medium: typed envelope schema, relay binding, Mac action adapters, expiry/cleanup tests, and browser result metadata.  ·  risk: A wrong extraction could send a sensitive value to the wrong Mac action. Bind each envelope to an explicit action type and tab/session, expire quickly, return a preview for ambiguous values, and use existing job undo/receipts for reversible mutations. Recovery is simply expiry and re-read.
- cost: Negligible API cost; implementation work only, with small relay storage for in-flight envelopes.  ·  latency: Adds under 100 ms beyond the existing browser round trip; avoids an extra model pass and clipboard interaction.
- security: Improves security by keeping page text out of durable findings, transcripts, and general logs. URL and typed provenance remain auditable; raw values are encrypted/in-memory and TTL-bound.
- depends on: Structured browser extraction or selector targeting that can name one value; Mac action adapters that accept typed inputs and return receipts; A relay-side per-request binding and cleanup mechanism


## What it asked for

_Nothing._
