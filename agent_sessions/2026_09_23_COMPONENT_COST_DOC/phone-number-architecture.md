# Phone numbers for custom consumer device — 2026-09-23

A carrier or telephony provider assigns the number to a service subscription. A bare modem/eSIM component does not itself provide an active number.

- Nearby-phone companion: calls use phone's existing line via appropriate Bluetooth telephony/audio support; HFP is the established hands-free profile. Text integration is platform dependent. nRF5340 provides BLE/LE Audio, not Classic HFP; validate phone interoperability before BOM commitment.
- Standalone new line: voice/SMS-capable SIM/eSIM plan from carrier/MVNO, compatible modem firmware and accepted finished device. AT&T documents VoLTE-capable device/firmware, suitable SIM/plan and IoT approval. Do not assume data-only IoT subscriptions provide ordinary voice/text service.
- Same number on phone and standalone wearable: AT&T NumberSync requires supported wearable and eligible service. Public consumer documentation does not establish a self-service integration path for arbitrary custom boards. Treat as carrier integration requiring confirmation, not guaranteed availability.
- Transfer existing number: move existing SIM/eSIM service to accepted custom device; this moves service rather than creating a simultaneous second copy.
- Cloud number: voice/SMS provider such as Twilio routes calls/messages to application over internet. This requires connectivity and software. Verified caller ID alone does not move inbound calls or permit SMS sending from an existing mobile number.

Sources:
https://www.att.com/features/numbersync/
https://www.att.com/support/article-modal/wireless/KM1001034/
https://www.business.att.com/content/dam/attbusiness/briefs/3G-faq-messaging.pdf
https://www.bluetooth.com/specifications/specs/hands-free-profile-1-10/
https://www.nordicsemi.com/Products/nRF5340
https://www.twilio.com/docs/phone-numbers
https://help.twilio.com/articles/223180048-How-to-Add-and-Remove-a-Verified-Phone-Number-or-Caller-ID-with-Twilio.

No service purchased, no carrier contacted, no changes to component DOCX.
