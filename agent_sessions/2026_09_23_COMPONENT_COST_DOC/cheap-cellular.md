# Cheaper standalone LTE voice candidate — 2026-09-23

The best manufacturer-confirmed lower-cost option found is **SIMCom A7672G**, a 24 × 24 × 2.4 mm LTE Cat 1 module. [SIMCom explicitly advertises VoLTE](https://en.simcom.com/product/A7672G.html) for the family, shows analog audio for A7672G, and lists US-relevant LTE bands B2/B4/B5/B12/B13/B25/B26/B66. This establishes module capability, **not** that a particular firmware, SIM, carrier and plan will complete a US voice call. B71 is not listed for A7672G.

[DigiKey currently lists A7672G](https://www.digikey.com/en/products/detail/simcom-wireless-solutions-limited/A7672G/28868527) at **$22.22 for one** and **$18.3832 each at 25+**, or **$551.50 for 30** before freight, tax or tariff. Its stock is **zero**, with an 18-week manufacturer lead time. Thus the quote corrects the claim that standalone voice hardware necessarily costs ~$40 per unit, but is *not* a currently shippable 30-unit purchase. The [matching A7672G-LABE evaluation kit](https://www.digikey.com/en/products/detail/simcom-wireless-solutions-limited/A7672G-LABE-TEKIT/28716794) is **$52.81** and likewise out of stock.

I found two apparently cheaper parts that should **not** be presented as proven voice replacements:

| Module | Listed price | Availability | Voice finding |
|---|---:|---|---|
| [A7670G-LABE at LCSC](https://www.lcsc.com/product-detail/C18548275.html) | $11.5717 one; $11.2775 at 10+ | Only 1 in stock | The [SIMCom sheet](https://datasheet.lcsc.com/lcsc/2410301810_SIMCom-Wireless-Solutions-A7670G-LABE_C18548275.pdf) lists suitable US LTE bands but does not explicitly establish VoLTE for this exact part. GSM fallback cannot establish US call suitability. |
| [SIM7670G-LNGV at LCSC](https://www.lcsc.com/product-detail/2g-3g-4g-5g-modules_simcom-wireless-solutions-sim7670g-lngv_C45935408.html) | $14.4991 one; $14.1592 at 10+ | Only 4 in stock | **Reject for direct voice:** [SIMCom lists VoLTE = NA](https://cn.simcom.com/product/SIM7670X.html) for SIM7670G. |

The 30-unit total for the A7670G-LABE would be $338.33, and for the SIM7670G-LNGV $424.78, at their 10+ listed tiers, but neither is a qualified 30-unit voice option. The A7672G still needs antenna, SIM, power circuitry, audio integration, carrier/IMS provisioning, and a live voice and SMS test. Phone-mediated calls over Bluetooth are a separate architecture with no extra pendant cellular module.
